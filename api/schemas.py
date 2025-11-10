# api/schemas.py
from __future__ import annotations
from typing import Literal, List, Optional
from pydantic import BaseModel

Language = Literal["python", "java", "c", "cpp"]

class TranslateRequest(BaseModel):
    source_lang: Language
    target_lang: Language
    code: str
    function_name: Optional[str] = None
    inputs: Optional[List[List[int]]] = None  # e.g., [[12,18],[0,5],[-4,6]]
    param_count: Optional[int] = None