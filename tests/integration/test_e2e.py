from api.services import verify_equivalence

def test_e2e_python_to_c_square():
    py_ref = "def square(x):\n    return x*x\n"
    c_code = "double square(double a){ return a*a; }"
    rep = verify_equivalence(py_ref, "square", "c", c_code, inputs_hint=3)
    assert rep["ok"], rep

def test_e2e_python_to_java_add():
    py_ref = "def add(a,b):\n    return a+b\n"
    java_code = "public static double add(double a,double b){ return a+b; }"
    rep = verify_equivalence(py_ref, "add", "java", java_code, inputs_hint=3)
    assert rep["ok"], rep