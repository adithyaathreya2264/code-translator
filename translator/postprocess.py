# translator/postprocess.py
from __future__ import annotations
import re

def _strip_md(code: str) -> str:
    code = code.strip()
    code = re.sub(r"^```[a-zA-Z]*\s*", "", code)
    code = re.sub(r"\s*```$", "", code)
    return code.strip()

def ensure_python_signature(code: str, func_name: str, param_count: int) -> str:
    code = _strip_md(code)
    args = ", ".join([f"a{i}: int" for i in range(param_count)])
    desired = f"def {func_name}({args})"
    # If first non-empty line doesn't start with desired def, replace it
    lines = [l for l in code.splitlines() if l.strip()]
    if not lines:
        return f"{desired}:\n    return 0"
    if not lines[0].lstrip().startswith("def "):
        lines.insert(0, f"{desired} -> int:")
    else:
        # normalize the def line
        lines[0] = re.sub(r"^def\s+\w+\s*\(.*\)\s*:?(\s*->\s*int)?\s*:?$",
                          f"{desired} -> int:", lines[0].strip())
        if not lines[0].endswith(":"):
            lines[0] += ":"
    # ensure at least one return
    if not any(re.match(r"\s*return\b", ln) for ln in lines[1:]):
        lines.append("    return 0")
    return "\n".join(lines)

def ensure_java_signature(code: str, func_name: str, param_count: int) -> str:
    code = _strip_md(code)
    params = ", ".join([f"int a{i}" for i in range(param_count)])
    sig = f"public static int {func_name}({params})"
    lines = [l for l in code.splitlines() if l.strip()]
    if not lines:
        return sig + " { return 0; }"
    # put correct signature on first line
    lines[0] = sig + " {"
    if not lines[-1].strip().endswith("}"):
        lines.append("}")
    return "\n".join(lines)

def ensure_c_like_signature(code: str, func_name: str, param_count: int, lang: str) -> str:
    code = _strip_md(code)
    params = ", ".join([f"int a{i}" for i in range(param_count)])
    sig = f"int {func_name}({params})"
    lines = [l for l in code.splitlines() if l.strip()]
    if not lines:
        return sig + " { return 0; }"
    lines[0] = sig + " {"
    if not lines[-1].strip().endswith("}"):
        lines.append("}")
    return "\n".join(lines)

def ensure_c_signature(code: str, func_name: str, param_count: int) -> str:
    return ensure_c_like_signature(code, func_name, param_count, "c")

def ensure_cpp_signature(code: str, func_name: str, param_count: int) -> str:
    return ensure_c_like_signature(code, func_name, param_count, "cpp")

def postprocess_for(lang: str, func_name: str, param_count: int, code: str) -> str:
    if lang == "python":
        return ensure_python_signature(code, func_name, param_count)
    if lang == "java":
        return ensure_java_signature(code, func_name, param_count)
    if lang == "c":
        return ensure_c_signature(code, func_name, param_count)
    if lang == "cpp":
        return ensure_cpp_signature(code, func_name, param_count)
    return _strip_md(code)
