# verifier/runners/c_runner.py
from __future__ import annotations
from pathlib import Path
from verifier.sandbox import mkworkdir, write_file, run_cmd, cleanup, RunResult

C_TEMPLATE = r"""/* GENERATED */
#include <stdio.h>
#include <stdlib.h>
{user_code}

/* Up to 4 args for now; extend as needed */
int __ct_dispatch(int argc, char** argv){
    switch(argc-1){
        case 0: return {func_name}();
        case 1: return {func_name}(atoi(argv[1]));
        case 2: return {func_name}(atoi(argv[1]), atoi(argv[2]));
        case 3: return {func_name}(atoi(argv[1]), atoi(argv[2]), atoi(argv[3]));
        case 4: return {func_name}(atoi(argv[1]), atoi(argv[2]), atoi(argv[3]), atoi(argv[4]));
        default: return 0;
    }
}

int main(int argc, char** argv){
    int out = __ct_dispatch(argc, argv);
    printf("%d\n", out);
    return 0;
}
"""

def run_c_func(code: str, func_name: str, args: list[int]) -> RunResult:
    work = mkworkdir("ct_c_")
    try:
        src = C_TEMPLATE.format(user_code=code, func_name=func_name)
        cfile = work / "prog.c"
        exe = work / "prog.exe"
        write_file(cfile, src)

        cc = run_cmd(["gcc", str(cfile), "-O2", "-std=c11", "-o", str(exe)], cwd=work)
        if not cc.ok:
            return cc
        rr = run_cmd([str(exe), *map(str, args)], cwd=work)
        return rr
    finally:
        cleanup(work)
