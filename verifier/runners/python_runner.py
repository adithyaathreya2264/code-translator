# verifier/runners/python_runner.py
from __future__ import annotations
from pathlib import Path
from verifier.sandbox import mkworkdir, write_file, run_cmd, cleanup, RunResult

TEMPLATE = """\
# GENERATED
{user_code}

def __ct_call(args):
    return {func_name}(*args)

if __name__ == "__main__":
    import sys
    # argv[1:] are integers
    args = [int(x) for x in sys.argv[1:]]
    out = __ct_call(args)
    print(out)
"""

def run_python_func(code: str, func_name: str, args: list[int]) -> RunResult:
    work = mkworkdir("ct_py_")
    try:
        src = TEMPLATE.format(user_code=code, func_name=func_name)
        script = work / "prog.py"
        write_file(script, src)
        return run_cmd(["python", str(script), *map(str, args)], cwd=work)
    finally:
        cleanup(work)
