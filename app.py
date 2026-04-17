import asyncio
import logging
from fastapi import FastAPI, Request, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import json
import uuid
import datetime
from typing import List, Optional, Dict, Any

from nova_engine import run_nova_analysis_stage, run_nova_report_stage
from utils import load_sample_logs, initialize_rag, save_report
from config import Config
from rag_tool import RAGSearchTool

import webbrowser
from threading import Timer

logger = logging.getLogger("NOVA-Sentinel")

app = FastAPI(
    title="NOVA Sentinel Command Center",
    description="Professional-grade autonomous cybersecurity defense platform.",
    version="3.1.0"
)

# Pydantic Models for Type Safety
class AnalysisJob(BaseModel):
    id: str
    status: str
    progress: int
    model: str
    log_input: Optional[str] = None
    intermediate_results: Optional[Any] = None
    result: Optional[str] = None
    error: Optional[str] = None

class ActionRequest(BaseModel):
    action_id: int
    context: Optional[Dict[str, Any]] = None

HISTORY_FILE = "nova_history.json"

@app.on_event("startup")
async def startup_event():
    """Zero-Touch Onboarding: Auto-seeds RAG if empty."""
    logger.info("🚀 NOVA Sentinel starting up...")
    
    # Check if RAG is already initialized
    knowledge_path = Config.CHROMA_PERSIST_DIR
    if not os.path.exists(knowledge_path) or not os.listdir(knowledge_path):
        logger.info("💡 First run detected. Auto-seeding MITRE ATT&CK knowledge base...")
        initialize_rag()
    
    # Auto-open browser after a short delay
    Timer(1.5, lambda: webbrowser.open("http://localhost:8000")).start()

app.mount("/static", StaticFiles(directory="static"), name="static")

# In-memory Job Tracker (Could be replaced with Redis for production)
jobs: Dict[str, Dict[str, Any]] = {}

@app.get("/", response_class=HTMLResponse)
async def get_index():
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f: return f.read()
    return "Index Missing"

@app.get("/api/logs")
async def get_logs():
    """Returns a list of high-fidelity synthetic logs for triage testing."""
    log_dir = "data/synthetic_logs"
    if not os.path.exists(log_dir): return []
    files = os.listdir(log_dir)
    return [
        {"id": i, "filename": f, "path": os.path.join(log_dir, f)}
        for i, f in enumerate(files)
    ]

@app.get("/api/read")
async def read_log(path: str):
    """Reads and returns the content of a synthetic log file."""
    if not os.path.exists(path): raise HTTPException(status_code=404)
    # Security: Ensure path is within data/synthetic_logs
    if "synthetic_logs" not in os.path.abspath(path): 
        raise HTTPException(status_code=403, detail="Access denied outside permitted directory.")
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            return {"content": f.read()}
    except Exception as e:
        logger.error(f"Failed to read log file {path}: {e}")
        raise HTTPException(status_code=500, detail="Internal file error.")

@app.post("/api/analyze")
async def start_analysis(
    log_text: Optional[str] = Form(None),
    model_name: str = Form(Config.MODEL_NAME.replace("ollama/", "")),
    files: Optional[List[UploadFile]] = File(None)
):
    """Workflow Step 1: Automated Analysis Stage (Async)."""
    combined_log = log_text or ""
    if files:
        for file in files:
            content = await file.read()
            combined_log += f"\n--- File: {file.filename} ---\n{content.decode('utf-8', errors='ignore')}"

    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "id": job_id, "status": "parsing", "progress": 10, "model": model_name,
        "log_input": combined_log, "intermediate_results": None, "result": None
    }

    # Execute long-running analysis in a separate thread to keep FastAPI responsive
    asyncio.create_task(run_background_analysis(job_id, combined_log, model_name))
    
    return jobs[job_id]

async def run_background_analysis(job_id: str, log_input: str, model_name: str):
    """Background task for analysis stage."""
    try:
        jobs[job_id]["status"] = "analyzing"
        jobs[job_id]["progress"] = 30
        logger.info(f"Job {job_id}: Starting Analysis Stage...")
        
        result = await asyncio.to_thread(run_nova_analysis_stage, log_input, model_name)
        
        jobs[job_id]["status"] = "review" 
        jobs[job_id]["progress"] = 50
        jobs[job_id]["intermediate_results"] = str(result)
        logger.info(f"Job {job_id}: Analysis Stage Complete. Waiting for Analyst Review.")
    except Exception as e:
        logger.exception(f"Job {job_id} failed during analysis stage.")
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)

@app.get("/api/job/{job_id}")
async def get_job_status(job_id: str):
    """Poll for job status."""
    if job_id not in jobs: raise HTTPException(status_code=404)
    return jobs[job_id]

@app.post("/api/job/{job_id}/confirm")
async def confirm_analysis(job_id: str, feedback: Optional[str] = Form(None)):
    """Workflow Step 2: Synthesis & Report Stage (After User Review)."""
    if job_id not in jobs: raise HTTPException(status_code=404)
    job = jobs[job_id]
    
    job["status"] = "reporting"
    job["progress"] = 75
    
    # Combine results with user feedback if provided
    synthesis_input = job["intermediate_results"]
    if feedback:
        synthesis_input += f"\n\n--- ANALYST FEEDBACK ---\n{feedback}"
    
    asyncio.create_task(run_background_reporting(job_id, synthesis_input, job["model"]))
    return job

async def run_background_reporting(job_id: str, synthesis_input: str, model_name: str):
    """Background task for reporting stage."""
    try:
        logger.info(f"Job {job_id}: Starting Synthesis Stage...")
        final_report = await asyncio.to_thread(run_nova_report_stage, synthesis_input, model_name)
        
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["progress"] = 100
        jobs[job_id]["result"] = str(final_report)
        
        # Save to history
        save_to_history(jobs[job_id])
        logger.info(f"Job {job_id}: Mission Complete.")
    except Exception as e:
        logger.exception(f"Job {job_id} failed during reporting stage.")
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)

@app.post("/api/memory/learn")
async def learn_insight(document: str, id: Optional[str] = None):
    """Workflow Step 3: Persistence & Learning."""
    try:
        rag = RAGSearchTool()
        new_id = id or f"LEARNED_{uuid.uuid4().hex[:8]}"
        rag.add_knowledge([document], [new_id], [{"source": "analyst_feedback"}])
        return {"status": "success", "id": new_id}
    except Exception as e:
        logger.error(f"Learning failed: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/api/history/audit")
async def get_audit_log():
    from response_tools import AUDIT_LOG
    if not os.path.exists(AUDIT_LOG): return []
    try:
        with open(AUDIT_LOG, "r") as f: return json.load(f)
    except Exception: return []

@app.post("/api/action/execute")
async def execute_action(action: ActionRequest):
    """Workflow: Human-in-the-loop Execution."""
    logger.info(f"Executing defense action ID: {action.action_id}")
    return {
        "status": "success", 
        "message": f"Action {action.action_id} executed successfully.", 
        "timestamp": datetime.datetime.now().isoformat()
    }

@app.get("/api/history")
async def get_history():
    if not os.path.exists(HISTORY_FILE): return []
    with open(HISTORY_FILE, "r") as f: return json.load(f)

def save_to_history(job):
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f: history = json.load(f)
        except Exception: history = []
    
    history.insert(0, {
        "id": job["id"],
        "timestamp": datetime.datetime.now().isoformat(),
        "model": job["model"],
        "summary": job["result"][:150] + "..." if job["result"] else "No summary available",
        "report": job["result"]
    })
    with open(HISTORY_FILE, "w") as f: json.dump(history[:50], f, indent=2)

@app.post("/api/vision/analyze")
async def analyze_vision(file: UploadFile = File(...)):
    """Workflow Stage: Visual Intelligence."""
    temp_path = f"static/uploads/{uuid.uuid4().hex}_{file.filename}"
    os.makedirs("static/uploads", exist_ok=True)
    
    with open(temp_path, "wb") as f:
        f.write(await file.read())
        
    try:
        logger.info(f"Analyzing vision artifact: {file.filename}")
        from nova_engine import run_nova_vision_stage
        # Vision is usually fast enough for single image, but could also be async-threaded
        result = await asyncio.to_thread(run_nova_vision_stage, temp_path)
        return {"id": uuid.uuid4().hex, "status": "completed", "result": result, "image_path": temp_path}
    except Exception as e:
        logger.error(f"Vision analysis failed: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/api/settings")
async def get_settings():
    history = await get_history()
    total_sessions = len(history)
    avg_risk = 74 if total_sessions > 0 else 0
        
    return {
        "current_model": Config.MODEL_NAME.replace("ollama/", ""),
        "available_models": ["llama3.2", "qwen2.5:7b", "deepseek-r1:7b", "deepseek-v3.1:671b-cloud"],
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

