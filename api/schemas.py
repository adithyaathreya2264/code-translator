from pydantic import BaseModel
from typing import Literal, List, Optional

Language = Literal["python","java","c","cpp"]

class TranslateRequest(BaseModel):
    source_lang: Language
    target_lang: Language
    code: str
    function_name: Optional[str] = None
    inputs: Optional[List[dict]] = None  # optional known input sets
