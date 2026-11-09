import os
import io
import json
import zipfile
import traceback
from dotenv import load_dotenv

# Load environment variables from .env file before anything else
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Optional, List

from app.agent.graph import build_graph
from app.agent.state import AgentState
from app.sandbox.docker_executor import DockerExecutor

app = FastAPI(
    title="Autonomous Code Generation & E2E Testing Agent API",
    version="1.2.0"
)

# Enable CORS for React frontend (port 5173 / localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize compiled LangGraph app and Docker execution engine
graph_app = build_graph()
executor = DockerExecutor()

class GenerationRequest(BaseModel):
    specification: str

class TestExecutionRequest(BaseModel):
    files: Dict[str, str]

class GenerationResponse(BaseModel):
    execution_exit_code: int
    iterations: int
    files: Dict[str, str]
    test_logs: Optional[str]
    syntax_errors: Optional[List[str]]

@app.get("/health")
def health_check():
    return {
        "status": "online",
        "sandbox": "docker-ready",
        "version": app.version
    }

@app.post("/generate", response_model=GenerationResponse)
def generate_code(request: GenerationRequest):
    """Standard synchronous execution endpoint."""
    initial_state: AgentState = {
        "specification": request.specification,
        "file_manifest": [],
        "files": {},
        "test_logs": None,
        "execution_exit_code": 1,
        "iterations": 0,
        "is_complete": False,
        "syntax_errors": []
    }

    try:
        final_state = graph_app.invoke(initial_state)
        return GenerationResponse(
            execution_exit_code=final_state.get("execution_exit_code", 1),
            iterations=final_state.get("iterations", 0),
            files=final_state.get("files", {}),
            test_logs=final_state.get("test_logs", ""),
            syntax_errors=final_state.get("syntax_errors", [])
        )
    except Exception as e:
        print("\n--- ERROR DURING AGENT INVOCATION ---")
        traceback.print_exc()
        print("-------------------------------------\n")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stream-generate")
async def stream_generate(request: GenerationRequest):
    """Server-Sent Events (SSE) streaming endpoint for real-time node state updates."""
    initial_state: AgentState = {
        "specification": request.specification,
        "file_manifest": [],
        "files": {},
        "test_logs": None,
        "execution_exit_code": 1,
        "iterations": 0,
        "is_complete": False,
        "syntax_errors": []
    }

    async def event_generator():
        try:
            for event in graph_app.stream(initial_state):
                for node_name, state_update in event.items():
                    payload = json.dumps({
                        "node": node_name,
                        "iterations": state_update.get("iterations", 0),
                        "execution_exit_code": state_update.get("execution_exit_code"),
                        "files": state_update.get("files", {}),
                        "test_logs": state_update.get("test_logs", "")
                    })
                    yield f"data: {payload}\n\n"
        except Exception as e:
            error_payload = json.dumps({"error": str(e)})
            yield f"data: {error_payload}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/run-tests")
def run_tests_only(request: TestExecutionRequest):
    """Executes the provided workspace code directly inside Docker without calling LLMs."""
    try:
        exit_code, logs = executor.run_pytest(request.files)
        return {
            "execution_exit_code": exit_code,
            "test_logs": logs
        }
    except Exception as e:
        print("\n--- ERROR DURING DIRECT DOCKER TEST EXECUTION ---")
        traceback.print_exc()
        print("-------------------------------------------------\n")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/download-zip")
def download_zip(request: TestExecutionRequest):
    """Compresses workspace code files into an in-memory ZIP archive for download."""
    try:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for filename, content in request.files.items():
                zip_file.writestr(filename, content)
        
        zip_buffer.seek(0)
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=generated_code.zip"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))