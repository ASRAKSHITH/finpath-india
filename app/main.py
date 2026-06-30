from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from app.config import GOOGLE_API_KEY
from app.schemas import FinPathRequest
from app.orchestrator import run_finpath_india
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
import json

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="FinPath India")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Financial-Disclaimer"] = "AI generated advice. Not registered with SEBI."
    return response

@app.get("/health")
def health():
    return {"status": "ok", "app": "FinPath India"}

from app.schemas import FinPathRequest, FinPathFeedback

@app.post("/analyze")
@limiter.limit("10/minute")
async def analyze(request: Request, payload: FinPathRequest):
    return await run_finpath_india(payload.query, payload.history)

@app.post("/feedback")
async def feedback(payload: FinPathFeedback):
    # Log feedback directly so observability tools can pick it up
    from app.observability import logger
    logger.logger.info(json.dumps({
        "event_type": "USER_FEEDBACK",
        "trace_id": payload.trace_id,
        "feedback": payload.feedback
    }))
    return {"status": "recorded"}

# Serve React Frontend if built
ui_path = os.path.join(os.path.dirname(__file__), "..", "finpath-ui", "dist")
if os.path.exists(ui_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(ui_path, "assets")), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        file_path = os.path.join(ui_path, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(ui_path, "index.html"))