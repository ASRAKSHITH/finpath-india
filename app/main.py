from fastapi import FastAPI
from app.config import GOOGLE_API_KEY
from app.schemas import FinPathRequest
from app.orchestrator import run_finpath_india

app = FastAPI(title="FinPath India")


@app.get("/")
def health():
    return {"status": "ok", "app": "FinPath India"}


@app.post("/analyze")
async def analyze(payload: FinPathRequest):
    return await run_finpath_india(payload.query)