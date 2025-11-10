# verifier/runners/cpp_runner.py
from __future__ import annotations
from pathlib import Path
from verifier.sandbox import mkworkdir, write_file, run_cmd, cleanup, RunResult

CPP_TEMPLATE = r"""// GENERATED
#include <bits/stdc++.h>
using namespace std;

{user_code}

int __ct_dispatch(int argc, char** argv){
    switch(argc-1){
        case 0: return {func_name}();
        case 1: return {func_name}(stoi(argv[1]));
        case 2: return {func_name}(stoi(argv[1]), stoi(argv[2]));
        case 3: return {func_name}(stoi(argv[1]), stoi(argv[2]), stoi(argv[3]));
        case 4: return {func_name}(stoi(argv[1]), stoi(argv[2]), stoi(argv[3]), stoi(argv[4]));
        default: return 0;
    }
}

int main(int argc, char** argv){
    int out = __ct_dispatch(argc, argv);
    cout << out << "\n";
    return 0;
}
"""

def run_cpp_func(code: str, func_name: str, args: list[int]) -> RunResult:
    work = mkworkdir("ct_cpp_")
    try:
        src = CPP_TEMPLATE.format(user_code=code, func_name=func_name)
        cppfile = work / "prog.cpp"
        exe = work / "prog.exe"
        write_file(cppfile, src)

        cc = run_cmd(["g++", str(cppfile), "-O2", "-std=c++17", "-o", str(exe)], cwd=work)
        if not cc.ok:
            return cc
        rr = run_cmd([str(exe), *map(str, args)], cwd=work)
        return rr
    finally:
        cleanup(work)
