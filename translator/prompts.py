# translator/prompts.py
from __future__ import annotations

HEADER = (
    "You are a precise code translator. "
    "Output ONLY one function with the exact required signature. "
    "No comments, no extra text, no I/O, no main, no classes (unless the signature requires)."
)

def sig_python(func_name: str, param_count: int) -> str:
    args = ", ".join([f"a{i}: int" for i in range(param_count)])
    return f"def {func_name}({args}) -> int"

def sig_java(func_name: str, param_count: int) -> str:
    args = ", ".join([f"int a{i}" for i in range(param_count)])
    return f"public static int {func_name}({args})"

def sig_c(func_name: str, param_count: int) -> str:
    args = ", ".join([f"int a{i}" for i in range(param_count)])
    return f"int {func_name}({args})"

def sig_cpp(func_name: str, param_count: int) -> str:
    args = ", ".join([f"int a{i}" for i in range(param_count)])
    return f"int {func_name}({args})"

def make_prompt(source_lang: str, target_lang: str, func_name: str, param_count: int, code: str) -> str:
    # Signature block per target
    if target_lang == "python":
        sig = sig_python(func_name, param_count)
        rules = "- Python 3.11, integers only, pure function."
    elif target_lang == "java":
        sig = sig_java(func_name, param_count)
        rules = "- Emit ONLY a static method (no class header; wrapper is added externally)."
    elif target_lang == "c":
        sig = sig_c(func_name, param_count)
        rules = "- C11, integers only, no stdio, no globals."
    elif target_lang == "cpp":
        sig = sig_cpp(func_name, param_count)
        rules = "- C++17, integers only, no I/O, no globals."
    else:
        raise ValueError(f"Unsupported target {target_lang}")

    return f"""{HEADER}

Translate this {source_lang.upper()} function into {target_lang.upper()}.
Emit exactly one function with this signature:
{sig}

Source ({source_lang}):
{code}

Rules:
{rules}
Return int. Output only the function code block, nothing else.
Output:
"""

# Convenience wrappers (optional)
def py_to_java(func_name, n, code): return make_prompt("python","java",func_name,n,code)
def py_to_c(func_name, n, code):    return make_prompt("python","c",func_name,n,code)
def py_to_cpp(func_name, n, code):  return make_prompt("python","cpp",func_name,n,code)

def java_to_py(func_name, n, code): return make_prompt("java","python",func_name,n,code)
def c_to_py(func_name, n, code):    return make_prompt("c","python",func_name,n,code)
def cpp_to_py(func_name, n, code):  return make_prompt("cpp","python",func_name,n,code)

def java_to_c(func_name, n, code):  return make_prompt("java","c",func_name,n,code)
def java_to_cpp(func_name, n, code):return make_prompt("java","cpp",func_name,n,code)
def c_to_java(func_name, n, code):  return make_prompt("c","java",func_name,n,code)
def cpp_to_java(func_name, n, code):return make_prompt("cpp","java",func_name,n,code)
def c_to_cpp(func_name, n, code):   return make_prompt("c","cpp",func_name,n,code)
def cpp_to_c(func_name, n, code):   return make_prompt("cpp","c",func_name,n,code)
