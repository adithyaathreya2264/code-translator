from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from db.models import VerifyRequest, VerifyRecord, VerifyResult
from db.client import get_collection
from api.services import verify_equivalence
from bson import ObjectId

router = APIRouter()
datetime.now(timezone.utc)
@router.post("/verify")
def post_verify(req: VerifyRequest):
    report = verify_equivalence(
        py_ref_code=req.py_ref_code,
        func_name=req.func_name,
        target_lang=req.target_lang,
        target_code=req.target_code,
        inputs_hint=req.inputs_hint,
        tol=req.tol,
    )
    if not report.get("ok"):
        # Still store failure for traceability
        doc = {
            "created_at": datetime.now(timezone.utc),
            "request": req.model_dump(),
            "result": report,
        }
        col = get_collection()
        ins = col.insert_one(doc)
        raise HTTPException(status_code=400, detail={"id": str(ins.inserted_id), "report": report})

    # success path
    record = {
        "created_at": datetime.now(timezone.utc),
        "request": req.model_dump(),
        "result": report,
    }
    col = get_collection()
    ins = col.insert_one(record)
    record["_id"] = str(ins.inserted_id)
    return record

# ✅ 1. List verification runs
@router.get("/runs")
def list_runs(limit: int = 10):
    col = get_collection()
    docs = list(col.find().sort("created_at", -1).limit(limit))
    for d in docs:
        d["_id"] = str(d["_id"])
    return {"items": docs}

# ✅ 2. Get single verification by ID
@router.get("/runs/{run_id}")
def get_run(run_id: str):
    col = get_collection()
    doc = col.find_one({"_id": ObjectId(run_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Run not found")
    doc["_id"] = str(doc["_id"])
    return doc