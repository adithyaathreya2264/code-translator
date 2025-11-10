# verifier/compare.py
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class CaseResult:
    args: List[int]
    expected: str
    got: str
    ok: bool
    err: str = ""

def norm_int(s: str) -> str:
    return s.strip().splitlines()[-1].strip()

def build_report(cases: List[List[int]], ref_out: List[str], tgt_out: List[str]) -> Dict[str, Any]:
    rows: List[CaseResult] = []
    passed = 0
    for args, e, g in zip(cases, ref_out, tgt_out):
        e1 = norm_int(e)
        g1 = norm_int(g)
        ok = (e1 == g1)
        if ok: passed += 1
        rows.append(CaseResult(args=args, expected=e1, got=g1, ok=ok))
    return {
        "total": len(cases),
        "passed": passed,
        "pass_rate": (passed / len(cases)) if cases else 0.0,
        "cases": [r.__dict__ for r in rows],
    }
