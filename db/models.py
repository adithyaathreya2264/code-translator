from typing import List, Literal, Optional, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime

Lang = Literal["python", "java", "c", "cpp"]

class VerifyRequest(BaseModel):
    py_ref_code: str = Field(..., description="Reference Python code")
    func_name: str
    target_lang: Lang
    target_code: str
    inputs_hint: int = 4
    tol: float = 1e-9

class VerifyResult(BaseModel):
    ok: bool
    inputs: List[List[float]]
    reference_results: List[Any]
    target_results: List[Any]
    mismatches: List[int]
    stdout: Dict[str, str]

class VerifyRecord(BaseModel):
    _id: Optional[str] = None  # filled by Mongo driver at insert time
    created_at: datetime
    request: VerifyRequest
    result: VerifyResult