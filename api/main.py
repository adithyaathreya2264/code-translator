from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI()
ROOT = Path(__file__).resolve().parents[1]
UI = ROOT / "ui"
ART = ROOT / "artifacts"
ART.mkdir(exist_ok=True)

# serve static ui
app.mount("/ui", StaticFiles(directory=str(UI), html=True), name="ui")

@app.get("/")
def root():
    return FileResponse(UI / "index.html")

@app.get("/health")
def health():
    return {"ok": True}

from api.schemas import TranslateRequest
from api.services import translate_stub
from fastapi import APIRouter

router = APIRouter(prefix="/api")

@router.post("/translate")
def translate(req: TranslateRequest):
    out = translate_stub(req.source_lang, req.target_lang, req.code)
    return {"translated_code": out}

app.include_router(router)
