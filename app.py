from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import json
from nova_engine import run_nova_sentinel
from utils import load_sample_logs, initialize_rag, save_report
from config import Config

app = FastAPI(title="NOVA Sentinel Hub")

# Data Models
class TriageRequest(BaseModel):
    log_input: str
    model_name: str

@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/logs")
async def get_logs():
    return load_sample_logs()

@app.get("/api/init-rag")
async def init_rag():
    try:
        msg = initialize_rag()
        return {"status": "success", "message": msg}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/triage")
async def execute_triage(request: TriageRequest):
    try:
        # Run the crew
        result = run_nova_sentinel(request.log_input, request.model_name)
        
        # Format result
        raw_result = str(result)
        
        # Save locally as well
        save_report({"model": request.model_name, "report": raw_result}, "nova_last_report.json")
        
        return {
            "status": "success", 
            "result": raw_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
