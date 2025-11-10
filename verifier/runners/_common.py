import json, os, shutil, subprocess, sys, tempfile, time
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

Result = Dict[str, Any]

def make_workdir(prefix: str = "run-") -> Path:
    p = Path(tempfile.mkdtemp(prefix=prefix))
    return p

def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def run_cmd(cmd, cwd: Path, timeout: int = 10) -> Tuple[int, str, str]:
    """Run a command with timeout; returns (exit_code, stdout, stderr)."""
    try:
        cp = subprocess.run(
            cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout
        )
        return cp.returncode, cp.stdout, cp.stderr
    except subprocess.TimeoutExpired as e:
        return 124, e.stdout or "", (e.stderr or "") + "\n[timeout]"

def cleanup(path: Optional[Path]):
    if path and path.exists():
        shutil.rmtree(path, ignore_errors=True)

def ok(data: Dict[str, Any]) -> Result:
    return {"ok": True, **data}

def err(msg: str, **extra) -> Result:
    e = {"ok": False, "error": msg}
    e.update(extra)
    return e

def to_json_stdin(stdin_payload: Any) -> str:
    return json.dumps(stdin_payload, ensure_ascii=False)