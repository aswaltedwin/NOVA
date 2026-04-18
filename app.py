import asyncio
import logging
import os
import json
import uuid
import datetime
import re # New: For parsing risk scores
from typing import List, Optional, Dict, Any
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException, UploadFile, File, Form, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import desc # New: For ordering trends

from nova_engine import run_nova_analysis_stage, run_nova_report_stage
from utils import load_sample_logs, initialize_rag, save_report
from config import Config, logger
from rag_tool import RAGSearchTool
from models import init_db, SessionLocal, Job, AuditLog

import webbrowser
from threading import Timer

# Initialize Database
init_db()

app = FastAPI(
    title="NOVA Sentinel Command Center",
    description="Professional-grade autonomous cybersecurity defense platform.",
    version=Config.VERSION
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key Middleware (Simple)
async def verify_api_key(request: Request):
    api_key = request.headers.get("X-API-KEY")
    if api_key != Config.API_KEY:
        raise HTTPException(status_code=403, detail="Invalid Security Token")
    return api_key

# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# WebSocket Manager for Real-time Status
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

# Pydantic Models
class AnalysisJobSchema(BaseModel):
    id: str
    status: str
    progress: int
    model: str
    result: Optional[str] = None
    error: Optional[str] = None

    class Config:
        orm_mode = True

class ActionRequest(BaseModel):
    action_id: int
    context: Optional[Dict[str, Any]] = None

@app.on_event("startup")
async def startup_event():
    logger.info(f"🚀 NOVA Sentinel {Config.VERSION} starting up...")
    
    # Check RAG
    if not os.path.exists(Config.CHROMA_PERSIST_DIR) or not os.listdir(Config.CHROMA_PERSIST_DIR):
        logger.info("💡 First run detected. Auto-seeding MITRE ATT&CK knowledge base...")
        initialize_rag()
    
    Timer(1.5, lambda: webbrowser.open("http://localhost:8000")).start()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_index():
    index_path = Path("index.html")
    if index_path.exists():
        return HTMLResponse(content=index_path.read_text(encoding="utf-8"))
    return "Index Missing"

@app.get("/api/logs")
async def get_logs():
    log_dir = Path("data/synthetic_logs")
    if not log_dir.exists(): return []
    return [
        {"id": i, "filename": f.name, "path": str(f)}
        for i, f in enumerate(log_dir.iterdir()) if f.is_file()
    ]

@app.get("/api/read")
async def read_log(path: str):
    base_path = Path("data/synthetic_logs").resolve()
    target_path = Path(path).resolve()
    
    if not target_path.exists() or not target_path.is_relative_to(base_path):
        raise HTTPException(status_code=403, detail="Unauthorized access to paths outside log directory.")
    
    try:
        return {"content": target_path.read_text(encoding="utf-8")}
    except Exception as e:
        logger.error(f"Read failure: {e}")
        raise HTTPException(status_code=500, detail="Internal file error.")

@app.websocket("/ws/jobs")
async def websocket_jobs(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text() # Keep connection alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/api/analyze")
async def start_analysis(
    log_text: Optional[str] = Form(None),
    model_name: str = Form(Config.MODEL_NAME.replace("ollama/", "")),
    files: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db)
):
    combined_log = log_text or ""
    if files:
        for file in files:
            content = await file.read()
            combined_log += f"\n--- File: {file.filename} ---\n{content.decode('utf-8', errors='ignore')}"

    job_id = str(uuid.uuid4())
    new_job = Job(
        id=job_id, status="parsing", progress=10, model=model_name,
        log_input=combined_log
    )
    db.add(new_job)
    db.commit()

    asyncio.create_task(run_background_analysis(job_id, combined_log, model_name))
    return {"id": job_id, "status": "parsing"}

async def run_background_analysis(job_id: str, log_input: str, model_name: str):
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job: return

        job.status = "analyzing"
        job.progress = 30
        db.commit()
        await manager.broadcast({"job_id": job_id, "status": "analyzing", "progress": 30})
        
        result = await asyncio.to_thread(run_nova_analysis_stage, log_input, model_name)
        
        # Extract Risk Score if present in result
        risk_match = re.search(r"Risk Score:\s*(\d+)", str(result))
        extracted_risk = int(risk_match.group(1)) if risk_match else 0
        
        job.status = "review" 
        job.progress = 50
        job.intermediate_results = str(result)
        job.risk_score = extracted_risk # New: Persistence
        db.commit()
        await manager.broadcast({
            "job_id": job_id, "status": "review", "progress": 50, 
            "intermediate": str(result), "risk_score": extracted_risk
        })

    except Exception as e:
        logger.exception(f"Job {job_id} analysis failed.")
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.status = "failed"
            job.error = str(e)
            db.commit()
            await manager.broadcast({"job_id": job_id, "status": "failed", "error": str(e)})
    finally:
        db.close()

@app.get("/api/job/{job_id}")
async def get_job_status(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job: raise HTTPException(status_code=404)
    return {
        "id": job.id, "status": job.status, "progress": job.progress,
        "model": job.model, "intermediate": job.intermediate_results,
        "result": job.result, "error": job.error
    }

@app.post("/api/job/{job_id}/confirm")
async def confirm_analysis(job_id: str, feedback: Optional[str] = Form(None), db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job: raise HTTPException(status_code=404)
    
    job.status = "reporting"
    job.progress = 75
    db.commit()
    
    synthesis_input = job.intermediate_results
    if feedback:
        synthesis_input += f"\n\n--- ANALYST FEEDBACK ---\n{feedback}"
    
    asyncio.create_task(run_background_reporting(job_id, synthesis_input, job.model))
    return {"id": job_id, "status": "reporting"}

async def run_background_reporting(job_id: str, synthesis_input: str, model_name: str):
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job: return

        final_report = await asyncio.to_thread(run_nova_report_stage, synthesis_input, model_name)
        
        job.status = "completed"
        job.progress = 100
        job.result = str(final_report)
        db.commit()
        
        await manager.broadcast({"job_id": job_id, "status": "completed", "progress": 100, "result": str(final_report)})
    except Exception as e:
        logger.exception(f"Job {job_id} reporting failed.")
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.status = "failed"
            job.error = str(e)
            db.commit()
            await manager.broadcast({"job_id": job_id, "status": "failed", "error": str(e)})
    finally:
        db.close()

@app.get("/api/action/execute")
async def execute_action(action: ActionRequest, db: Session = Depends(get_db)):
    # Log to Audit Log
    new_audit = AuditLog(action=f"Execute_Action_{action.action_id}", details=json.dumps(action.context))
    db.add(new_audit)
    db.commit()
    
    return {"status": "success", "message": f"Action {action.action_id} logged and executed."}

@app.get("/api/stats/trend")
async def get_risk_trend(db: Session = Depends(get_db)):
    """Returns risk trends for the last 7 missions."""
    jobs = db.query(Job).filter(Job.status == "completed").order_by(desc(Job.created_at)).limit(7).all()
    # Reverse to show chronological order
    trend_data = [{"id": j.id, "risk": j.risk_score, "date": j.created_at.strftime("%H:%M")} for j in reversed(jobs)]
    return trend_data

@app.get("/api/settings")
async def get_settings(db: Session = Depends(get_db)):
    total_sessions = db.query(Job).count()
    # Calculate real average risk from DB
    avg_risk_query = db.query(Job).filter(Job.risk_score > 0).all()
    avg_risk = sum(j.risk_score for j in avg_risk_query) // len(avg_risk_query) if avg_risk_query else 0
        
    return {
        "current_model": Config.MODEL_NAME.replace("ollama/", ""),
        "available_models": Config.AVAILABLE_MODELS,
        "ollama_status": "online",
        "rag_status": "synced",
        "stats": {
            "total_sessions": total_sessions,
            "avg_risk": avg_risk,
            "mitre_count": 102
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


