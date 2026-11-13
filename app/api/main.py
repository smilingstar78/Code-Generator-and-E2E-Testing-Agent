import os
from dotenv import load_dotenv

# Load .env file BEFORE importing agent graph to provide GROQ_API_KEY
load_dotenv()

import io
import zipfile
from typing import Dict, Any
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.agent.graph import agent_graph
from app.sandbox.docker_executor import DockerExecutor
from app.api.terminal import router as terminal_router

app = FastAPI(title="Autonomous Code Generation & E2E Testing Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(terminal_router)

class SpecificationRequest(BaseModel):
    specification: str

class TestExecutionRequest(BaseModel):
    files: Dict[str, str]

class ZipDownloadRequest(BaseModel):
    files: Dict[str, str]

executor = DockerExecutor()

@app.get("/")
def read_root():
    return {"status": "online", "message": "Autonomous Agent API operational"}

@app.post("/generate")
def generate_codebase(request: SpecificationRequest):
    initial_state = {
        "specification": request.specification,
        "files": {},
        "test_logs": "",
        "execution_exit_code": -1,
        "fix_attempts": 0
    }
    final_state = agent_graph.invoke(initial_state)
    return final_state

@app.post("/run-tests")
def run_tests_endpoint(request: TestExecutionRequest):
    exit_code, logs = executor.run_tests(request.files)
    return {
        "execution_exit_code": exit_code,
        "test_logs": logs
    }

@app.post("/download-zip")
def download_zip_endpoint(request: ZipDownloadRequest):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for filename, content in request.files.items():
            clean_filename = filename.strip().lstrip("/")
            zip_file.writestr(clean_filename, content)

    zip_buffer.seek(0)
    return Response(
        content=zip_buffer.getvalue(),
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=generated_agent_code.zip"}
    )