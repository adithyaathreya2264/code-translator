"""
Comprehensive integration test for the Code Translator Verification System.
Covers:
- Language runners (Python, C, C++, Java)
- Verification pipeline (testgen + compare + services)
- FastAPI endpoints (/verify, /runs, /runs/{id})
- MongoDB persistence
"""

import json
import pytest
from fastapi.testclient import TestClient
from api.app import app
from api.services import verify_equivalence
from verifier.runners.python_runner import run_python
from verifier.runners.c_runner import run_c
from verifier.runners.cpp_runner import run_cpp
from verifier.runners.java_runner import run_java
from db.client import get_collection

client = TestClient(app)


# ─────────────────────────────────────────────
# 1️⃣ BASIC RUNNER TESTS
# ─────────────────────────────────────────────
def test_python_runner():
    code = "def square(x): return x*x"
    r = run_python(code, "square", [[2], [3]])
    assert r["ok"]
    assert r["results"] == [4, 9]


def test_c_runner():
    code = "double square(double a){ return a*a; }"
    r = run_c(code, "square", [[2], [3]])
    assert r["ok"]
    assert r["results"] == [4, 9]


def test_cpp_runner():
    code = "double square(double a){ return a*a; }"
    r = run_cpp(code, "square", [[2], [3]])
    assert r["ok"]
    assert r["results"] == [4, 9]


def test_java_runner():
    code = "public static double square(double x){ return x*x; }"
    r = run_java(code, "square", [[2], [3]])
    assert r["ok"]
    assert r["results"] == [4, 9]


# ─────────────────────────────────────────────
# 2️⃣ FULL PIPELINE (verify_equivalence)
# ─────────────────────────────────────────────
def test_verify_equivalence_c():
    py_ref = "def square(x): return x*x"
    target = "double square(double a){ return a*a; }"
    report = verify_equivalence(py_ref, "square", "c", target)
    assert report["ok"]
    assert len(report["inputs"]) > 0
    assert report["reference_results"] == report["target_results"]


def test_verify_equivalence_java():
    py_ref = "def square(x): return x*x"
    target = "public static double square(double x){ return x*x; }"
    report = verify_equivalence(py_ref, "square", "java", target)
    assert report["ok"]


# ─────────────────────────────────────────────
# 3️⃣ API ENDPOINTS TESTS
# ─────────────────────────────────────────────
def test_api_post_verify():
    payload = {
        "py_ref_code": "def square(x): return x*x",
        "func_name": "square",
        "target_lang": "c",
        "target_code": "double square(double a){ return a*a; }",
        "inputs_hint": 3,
        "tol": 1e-9
    }
    res = client.post("/verify", json=payload)
    assert res.status_code in (200, 400)
    data = res.json()
    assert "created_at" in data
    assert "request" in data
    assert "result" in data


def test_api_get_runs_and_id():
    # Fetch runs
    res = client.get("/runs?limit=5")
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    if data["items"]:
        _id = data["items"][0]["_id"]
        res2 = client.get(f"/runs/{_id}")
        assert res2.status_code == 200
        assert "_id" in res2.json()


# ─────────────────────────────────────────────
# 4️⃣ MONGO DB CHECK
# ─────────────────────────────────────────────
def test_mongo_persistence():
    col = get_collection()
    doc = col.find_one(sort=[("created_at", -1)])
    assert doc is not None
    assert "created_at" in doc
    assert "request" in doc
    assert "result" in doc


# ─────────────────────────────────────────────
# 5️⃣ UI SERVING CHECK
# ─────────────────────────────────────────────
def test_ui_static_serving():
    res = client.get("/ui/")
    assert res.status_code == 200 or res.status_code == 304
