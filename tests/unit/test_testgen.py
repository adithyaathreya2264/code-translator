from verifier.testgen import generate_inputs_from_reference

def test_generate_inputs_arity1():
    code = "def square(x):\n    return x*x\n"
    ins = generate_inputs_from_reference(code, "square", 3)
    assert ins[:3] == [[-2], [-1], [0]]