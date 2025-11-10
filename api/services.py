# api/services.py
from __future__ import annotations
from typing import Literal, Dict, Any, List, Optional
import os, re
from datetime import datetime

# --- OpenAI Translation ---
if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("❌ OPENAI_API_KEY not found in environment or .env file")

from translator.openai_model import translate_with_openai as _llm_call
from translator.prompts import make_prompt
from translator.postprocess import postprocess_for

from verifier.testgen import infer_param_count as infer_param_count_py, gen_examples
from verifier.compare import build_report

from verifier.runners.python_runner import run_python_func
from verifier.runners.java_runner import run_java_func
from verifier.runners.c_runner import run_c_func
from verifier.runners.cpp_runner import run_cpp_func

from storage.mongo import save_full_job
from storage.files import new_job_id, job_dir, save_text, save_json

Language = Literal["python", "java", "c", "cpp"]

# ---------- Helper: Infer parameter count ----------
_SIG_RE = re.compile(r"\b(?:int|public\s+static\s+int)\s+([A-Za-z_]\w*)\s*\(([^)]*)\)")

def infer_param_count_generic(source_lang: Language, code: str, func_name: str, fallback: int = 1) -> int:
    """Infer function arity (param count) for Python and others."""
    if source_lang == "python":
        return infer_param_count_py(code, func_name)
    for line in code.splitlines():
        m = _SIG_RE.search(line)
        if not m:
            continue
        if m.group(1) != func_name:
            continue
        args = m.group(2).strip()
        if args == "" or args.lower() == "void":
            return 0
        return len([x for x in args.split(",") if x.strip()])
    return fallback

# ---------- Runner dispatcher ----------
def run_in_lang(lang: Language, code: str, func_name: str, args: List[int]):
    if lang == "python":
        return run_python_func(code, func_name, args)
    if lang == "java":
        return run_java_func(code, func_name, args)
    if lang == "c":
        return run_c_func(code, func_name, args)
    if lang == "cpp":
        return run_cpp_func(code, func_name, args)
    raise ValueError(f"Unsupported language: {lang}")

# ---------- Translate Only ----------
def translate_only(
    source_lang: Language,
    target_lang: Language,
    code: str,
    func_name: str,
    param_count: Optional[int] = None,
) -> str:
    """
    Translate a function using OpenAI.
    Also stores the translation job in MongoDB (without verification).
    """
    if source_lang not in ("python", "java", "c", "cpp") or target_lang not in ("python", "java", "c", "cpp"):
        raise ValueError("Unsupported language")

    n = param_count or infer_param_count_generic(source_lang, code, func_name)

    # Skip translation if same language (normalize only)
    if source_lang == target_lang:
        translated = postprocess_for(target_lang, func_name, n, code)
    else:
        prompt = make_prompt(source_lang, target_lang, func_name, n, code)
        raw = _llm_call(prompt)
        translated = postprocess_for(target_lang, func_name, n, raw)

    # --- Save immediately to MongoDB ---
    try:
        job_id = new_job_id()
        record = {
            "job_id": job_id,
            "timestamp": datetime.utcnow(),
            "source_lang": source_lang,
            "target_lang": target_lang,
            "function_name": func_name,
            "param_count": n,
            "source_code": code,
            "translated_code": translated,
            "verified": False,
            "pass_rate": None,
        }
        save_full_job(record)
        print(f"🟢 Stored translation-only job {job_id} in MongoDB.")
    except Exception as e:
        print(f"⚠️ Could not store translation-only job: {e}")

    return translated

# ---------- Translate + Verify ----------
def translate_and_verify(
    source_lang: Language,
    target_lang: Language,
    code: str,
    func_name: str,
    max_random: int = 8,
    custom_inputs: Optional[List[List[int]]] = None,
    param_count: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Translate with OpenAI, execute both source & target on same test cases,
    compare outputs, and store full results in MongoDB Atlas.
    """
    n = param_count or infer_param_count_generic(source_lang, code, func_name)
    cases: List[List[int]] = gen_examples(n, max_random=max_random)
    if custom_inputs:
        for tup in custom_inputs:
            if isinstance(tup, list) and len(tup) == n and all(isinstance(x, int) for x in tup):
                cases.append(tup)

    translated = translate_only(source_lang, target_lang, code, func_name, param_count=n)

    # Run reference (source)
    ref_out: List[str] = []
    for args in cases:
        r = run_in_lang(source_lang, code, func_name, args)
        if not r.ok:
            return {"error": f"{source_lang} reference failed: {r.stderr}"}
        ref_out.append(r.stdout)

    # Run translated (target)
    tgt_out: List[str] = []
    for args in cases:
        rr = run_in_lang(target_lang, translated, func_name, args)
        if not rr.ok:
            return {
                "translated_code": translated,
                "error": f"{target_lang} run failed: {rr.stderr}"
            }
        tgt_out.append(rr.stdout)

    # Compare
    report = build_report(cases, ref_out, tgt_out)

    # Save locally (optional)
    job_id = new_job_id()
    d = job_dir(job_id)
    save_text(d / f"source_{source_lang}.txt", code)
    save_text(d / f"translated_{target_lang}.txt", translated)
    save_json(d / "report.json", report)

    # --- Store full job (verified) in MongoDB ---
    try:
        job_record = {
            "job_id": job_id,
            "timestamp": datetime.utcnow(),
            "source_lang": source_lang,
            "target_lang": target_lang,
            "function_name": func_name,
            "param_count": n,
            "cases": cases,
            "pass_rate": float(report.get("pass_rate", 0.0)),
            "source_code": code,
            "translated_code": translated,
            "report": report,
            "verified": True,
        }
        save_full_job(job_record)
        print(f"🟢 Stored verified job {job_id} in MongoDB.")
    except Exception as e:
        print(f"⚠️ Failed to store verified job in MongoDB: {e}")

    return {"job_id": job_id, "translated_code": translated, "report": report}