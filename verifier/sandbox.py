# verifier/sandbox.py
from __future__ import annotations
import shutil, subprocess, tempfile, textwrap, os
from pathlib import Path
from typing import List, Optional, Tuple

DEFAULT_TIMEOUT = 5  # seconds (can be tweaked per language)

class RunResult:
    def __init__(self, ok: bool, exit_code: int, stdout: str, stderr: str, workdir: Path):
        self.ok = ok
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr
        self.workdir = workdir  # leave dir for debugging if needed

def mkworkdir(prefix: str = "ct_run_") -> Path:
    return Path(tempfile.mkdtemp(prefix=prefix))

def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def run_cmd(cmd: List[str], cwd: Path, timeout: int = DEFAULT_TIMEOUT) -> RunResult:
    try:
        proc = subprocess.run(
            cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout
        )
        ok = proc.returncode == 0
        return RunResult(ok, proc.returncode, proc.stdout, proc.stderr, cwd)
    except subprocess.TimeoutExpired as e:
        return RunResult(False, -1, e.stdout or "", f"TIMEOUT after {timeout}s", cwd)

def cleanup(path: Path):
    if path.exists():
        shutil.rmtree(path, ignore_errors=True)
