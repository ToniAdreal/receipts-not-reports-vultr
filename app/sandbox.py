"""Parent-side contained runner.

Each run gets a fresh temporary directory (seeded with demo data copies),
spawns the worker as a subprocess with a scrubbed environment (no API keys,
no host secrets), enforces a wall-clock timeout, caps captured output, and
destroys the directory when the run ends — lifecycle discipline per the
Blast Radius Zero containment brief.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

WORKER = Path(__file__).with_name("sandbox_worker.py")
DATA_DIR = Path(__file__).with_name("demo_data")
RUN_TIMEOUT_S = 15
MAX_OUTPUT_BYTES = 64 * 1024


def run_plan(steps: list[dict], timeout_s: int = RUN_TIMEOUT_S) -> list[dict]:
    """Execute a plan of tool steps in the sandbox. Returns one record per step."""
    workdir = Path(tempfile.mkdtemp(prefix="receipts-sandbox-"))
    try:
        if DATA_DIR.exists():
            for f in DATA_DIR.iterdir():
                if f.is_file():
                    shutil.copy2(f, workdir / f.name)
        env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"),
               "PYTHONHASHSEED": "0", "LANG": "C.UTF-8"}  # no secrets, no API keys
        started = time.time()
        try:
            proc = subprocess.run(
                [sys.executable, str(WORKER)],
                input=json.dumps({"steps": steps}),
                capture_output=True, text=True,
                cwd=workdir, env=env, timeout=timeout_s,
            )
            stdout = proc.stdout[:MAX_OUTPUT_BYTES]
            records = [json.loads(line) for line in stdout.splitlines() if line.strip()]
        except subprocess.TimeoutExpired:
            records = [{"tool": s.get("tool"), "status": "timeout",
                        "reason": f"run exceeded {timeout_s}s cap and was killed"}
                       for s in steps]
        duration_ms = int((time.time() - started) * 1000)
        for r in records:
            r["duration_ms"] = duration_ms
        # Any step with no record (worker died) becomes an error record.
        if len(records) < len(steps):
            for s in steps[len(records):]:
                records.append({"tool": s.get("tool"), "status": "error",
                                "error": "worker exited without a record"})
        return records
    finally:
        shutil.rmtree(workdir, ignore_errors=True)  # environment destroyed after the task
