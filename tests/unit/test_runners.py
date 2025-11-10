import pytest
from verifier.runners.python_runner import run_python
from verifier.runners.java_runner import run_java
from verifier.runners.c_runner import run_c
from verifier.runners.cpp_runner import run_cpp

def _assert_ok(res):
    # If a test fails, this prints the full dict (stderr/raw/generated_main) to help you immediately
    assert res.get("ok"), f"\nRunner failed:\n{res}"

def test_python_runner_arity1():
    src = "def square(x):\n    return x*x\n"
    r = run_python(src, "square", inputs=[[2],[3]])
    _assert_ok(r)
    assert r["results"] == [4, 9]

def test_java_runner_arity1():
    # One-arg method; arity-aware runner should generate only the 1-arg call
    src = "public static double square(double x){ return x*x; }"
    r = run_java(src, "square", inputs=[[2],[3]])
    _assert_ok(r)
    assert r["results"] == [4, 9]

def test_c_runner_arity1():
    src = "double square(double a){ return a*a; }"
    r = run_c(src, "square", inputs=[[2],[3]])
    _assert_ok(r)
    assert r["results"] == [4, 9]

def test_cpp_runner_arity1():
    src = "double square(double a){ return a*a; }"
    r = run_cpp(src, "square", inputs=[[2],[3]])
    _assert_ok(r)
    assert r["results"] == [4, 9]