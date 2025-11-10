# api/main.py
from __future__ import annotations
from pathlib import Path
import os
from dotenv import load_dotenv
from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# --- Load environment early ---
ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
    print("✅ Loaded environment variables from .env")
else:
    print("⚠️  .env file not found — relying on system environment vars")

from api.schemas import TranslateRequest
from api.services import translate_only, translate_and_verify
from storage.mongo import list_recent_jobs
from storage.files import job_dir

# --- FastAPI setup ---
app = FastAPI(title="AI Code Translator & Verifier")
UI = ROOT / "ui"
ART = ROOT / "artifacts"
ART.mkdir(exist_ok=True)

# Serve UI and local artifacts
app.mount("/ui", StaticFiles(directory=str(UI), html=True), name="ui")
app.mount("/artifacts", StaticFiles(directory=str(ART), html=False), name="artifacts")

@app.get("/")
def root_page():
    """Serve the main UI page."""
    return FileResponse(UI / "index.html")

@app.get("/health")
def health():
    """Simple system status check."""
    return {
        "ok": True,
        "openai": bool(os.getenv("OPENAI_API_KEY")),
        "mongo": bool(os.getenv("MONGODB_URI")),
    }

router = APIRouter(prefix="/api")

# --- Translation ---
@router.post("/translate")
def translate_ep(req: TranslateRequest):
    out = translate_only(
        req.source_lang,
        req.target_lang,
        req.code,
        req.function_name or "func",
        param_count=req.param_count,
    )
    return {"translated_code": out}

# --- Translation + Verification ---
@router.post("/translate_and_verify")
def translate_and_verify_ep(req: TranslateRequest):
    res = translate_and_verify(
        req.source_lang,
        req.target_lang,
        req.code,
        req.function_name or "func",
        max_random=8,
        custom_inputs=req.inputs,
        param_count=req.param_count,
    )
    return res

# --- Job History from MongoDB Atlas ---
@router.get("/history")
def history(limit: int = 25):
    """Retrieve full translation history (latest N jobs) from MongoDB Atlas."""
    try:
        items = list_recent_jobs(limit)
        return {"items": items}
    except Exception as e:
        return {"items": [], "error": str(e)}

# --- Local artifact download (optional) ---
@router.get("/job/{job_id}/{kind}")
def job_file(job_id: str, kind: str):
    """
    Download artifact files for a specific job:
    kind ∈ { 'source', 'translated', 'report' }
    """
    p = job_dir(job_id)
    if not p.exists():
        raise HTTPException(404, "Job not found")

    if kind == "report":
        f = p / "report.json"
        if not f.exists():
            raise HTTPException(404, "Report not found")
        return FileResponse(f)

    if kind == "source":
        for s in ("source_python.txt", "source_java.txt", "source_c.txt", "source_cpp.txt"):
            f = p / s
            if f.exists():
                return FileResponse(f)
        raise HTTPException(404, "Source not found")

    if kind == "translated":
        for s in ("translated_python.txt", "translated_java.txt", "translated_c.txt", "translated_cpp.txt"):
            f = p / s
            if f.exists():
                return FileResponse(f)
        raise HTTPException(404, "Translated not found")

    raise HTTPException(400, "Invalid kind")

app.include_router(router)
