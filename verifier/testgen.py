# verifier/testgen.py
from __future__ import annotations
import ast, random
from typing import List, Tuple

DEFAULT_EDGE = [ -1, 0, 1, 2, 5, 10, 20, 50 ]
RAND_RANGE = (-100, 100)

def infer_param_count(py_code: str, func_name: str) -> int:
    """Parse Python code and count positional parameters of func_name."""
    t = ast.parse(py_code)
    for n in t.body:
        if isinstance(n, ast.FunctionDef) and n.name == func_name:
            return len([a for a in n.args.args])
    raise ValueError(f"Function {func_name} not found")

def gen_examples(param_count: int, max_random: int = 10) -> List[List[int]]:
    """Produce a mix of edge cases and random integer tuples."""
    cases: List[List[int]] = []
    # Single-param edge cases
    if param_count == 0:
        cases.append([])
    elif param_count == 1:
        for v in DEFAULT_EDGE:
            cases.append([v])
    else:
        # multi-arg: combine a few interesting pairs/triples
        seeds = DEFAULT_EDGE[:6]
        if param_count == 2:
            for a in seeds:
                for b in (0, 1, 2, 5, -1):
                    cases.append([a, b])
        elif param_count == 3:
            for a in (0, 1, 2):
                for b in (0, 1, 2):
                    for c in (0, 1, 2):
                        cases.append([a,b,c])

    # randoms
    lo, hi = RAND_RANGE
    for _ in range(max_random):
        tup = [ random.randint(lo, hi) for _ in range(param_count) ]
        cases.append(tup)
    # Deduplicate
    dedup = []
    seen = set()
    for c in cases:
        t = tuple(c)
        if t not in seen:
            seen.add(t); dedup.append(c)
    return dedup
