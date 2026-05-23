from fastapi import FastAPI
from app.config import GOOGLE_API_KEY
from app.schemas import FinPathRequest
from app.orchestrator import run_finpath_india
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="FinPath India")

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


@app.get("/")
def health():
    return {"status": "ok", "app": "FinPath India"}


@app.post("/analyze")
async def analyze(payload: FinPathRequest):
    return await run_finpath_india(payload.query)