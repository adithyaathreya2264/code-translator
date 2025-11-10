import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from verifier.runners.java_runner import run_java
r = run_java("public static double square(double x){ return x*x; }", "square", inputs=[[2],[3]])
print(r)