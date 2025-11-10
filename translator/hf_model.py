# translator/hf_model.py
from __future__ import annotations
import threading
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Small, CPU-friendly baseline. You can switch later (e.g., codet5-base).
_MODEL_NAME = "Salesforce/codet5-small"
_lock = threading.Lock()
_tokenizer = None
_model = None

def _lazy_load():
    global _tokenizer, _model
    if _tokenizer is None or _model is None:
        with _lock:
            if _tokenizer is None or _model is None:
                _tokenizer = AutoTokenizer.from_pretrained(_MODEL_NAME)
                _model = AutoModelForSeq2SeqLM.from_pretrained(_MODEL_NAME)

def translate_raw(prompt: str, max_new_tokens: int = 256) -> str:
    _lazy_load()
    inputs = _tokenizer(prompt, return_tensors="pt")
    out_ids = _model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        num_beams=4,
        early_stopping=True,
        no_repeat_ngram_size=3,
    )
    return _tokenizer.decode(out_ids[0], skip_special_tokens=True)

