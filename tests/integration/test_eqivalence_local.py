from verifier.runners.python_runner import run_python_func
from verifier.runners.java_runner import run_java_func
from verifier.runners.c_runner import run_c_func
from verifier.runners.cpp_runner import run_cpp_func
from verifier.testgen import infer_param_count, gen_examples
from verifier.compare import build_report

PY_GCD = """\
def gcd(a:int, b:int)->int:
    a = abs(a); b = abs(b)
    while b != 0:
        a, b = b, a % b
    return a
"""

JAVA_GCD = """\
public static int gcd(int a, int b){
    a = Math.abs(a); b = Math.abs(b);
    while(b != 0){
        int t = b;
        b = a % b;
        a = t;
    }
    return a;
}
"""

C_GCD = """\
int gcd(int a, int b){
    if(a<0) a=-a; if(b<0) b=-b;
    while(b != 0){ int t = b; b = a % b; a = t; }
    return a;
}
"""

CPP_GCD = """\
int gcd(int a, int b){
    a = abs(a); b = abs(b);
    while(b != 0){ int t=b; b=a%b; a=t; }
    return a;
}
"""

def test_equivalence_gcd():
    n = infer_param_count(PY_GCD, "gcd")
    cases = gen_examples(n, max_random=8)

    ref_out = []
    for args in cases:
        r = run_python_func(PY_GCD, "gcd", args)
        assert r.ok, r.stderr
        ref_out.append(r.stdout)

    tgt_out = []
    for args in cases:
        rj = run_java_func(JAVA_GCD, "gcd", args)
        assert rj.ok, rj.stderr
        tgt_out.append(rj.stdout)

    rep = build_report(cases, ref_out, tgt_out)
    assert rep["pass_rate"] >= 0.95, rep
