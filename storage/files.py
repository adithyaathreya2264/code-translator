# storage/files.py
from __future__ import annotations
from pathlib import Path
from datetime import datetime
import json, shutil, uuid

ART = Path(__file__).resolve().parents[1] / "artifacts"
ART.mkdir(exist_ok=True)

def new_job_id() -> str:
    ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    uid = uuid.uuid4().hex[:8]
    return f"{ts}-{uid}"

def job_dir(job_id: str) -> Path:
    p = ART / job_id
    p.mkdir(parents=True, exist_ok=True)
    return p

def save_text(path: Path, text: str):
    path.write_text(text, encoding="utf-8")

def save_json(path: Path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

def list_jobs(limit: int = 50):
    items = []
    for p in sorted(ART.glob("*"), reverse=True):
        if not p.is_dir(): continue
        rep = p / "report.json"
        meta = p / "meta.json"
        row = {"job_id": p.name}
        if meta.exists():
            try: row.update(json.loads(meta.read_text(encoding="utf-8")))
            except: pass
        if rep.exists():
            try:
                r = json.loads(rep.read_text(encoding="utf-8"))
                row["pass_rate"] = r.get("pass_rate")
            except: pass
        items.append(row)
        if len(items) >= limit: break
    return items
