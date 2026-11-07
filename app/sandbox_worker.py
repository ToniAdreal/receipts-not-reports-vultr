"""Sandbox worker: runs INSIDE a subprocess with a scrubbed environment,
a throwaway working directory, CPU/memory rlimits, and a hard timeout
(enforced by the parent). It exposes only whitelisted tools. Any other tool
name is refused and reported back as a blocked action — that refusal is the
containment moment: the agent asked, the sandbox said no, and the refusal
itself becomes evidence.

Protocol: reads a JSON plan on stdin: {"steps": [{"tool": ..., "args": {...}}]}
Writes one JSON record per step on stdout.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import resource
import sys

ALLOWED_TOOLS = {"csv_stats", "count_keyword", "hash_text", "write_report"}

# Things an agent might try that are never allowed inside the sandbox.
BLOCKED_TOOLS = {"shell", "read_secret", "network_fetch", "read_file_outside", "delete_host_file"}


def _limits() -> None:
    # 10s CPU, 256 MB address space — every run is capped.
    resource.setrlimit(resource.RLIMIT_CPU, (10, 10))
    resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024, 256 * 1024 * 1024))


def csv_stats(args: dict) -> dict:
    path = args["path"]
    # Only files inside the sandbox working directory may be read.
    full = os.path.realpath(os.path.join(os.getcwd(), path))
    if not full.startswith(os.getcwd()):
        raise PermissionError("path escapes sandbox")
    with open(full, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    total = round(sum(float(r[args.get("sum_column", "amount")]) for r in rows), 2)
    return {"rows": len(rows), "total_amount": total}


def count_keyword(args: dict) -> dict:
    text = args["text"]
    return {"keyword": args["keyword"], "count": text.lower().count(args["keyword"].lower())}


def hash_text(args: dict) -> dict:
    return {"sha256": hashlib.sha256(args["text"].encode("utf-8")).hexdigest()}


def write_report(args: dict) -> dict:
    name = os.path.basename(args["name"])  # basename only: cannot escape the sandbox dir
    path = os.path.join(os.getcwd(), "out", name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(args["content"])
    return {"artifact": f"out/{name}", "bytes": len(args["content"].encode("utf-8")),
            "sha256": hashlib.sha256(args["content"].encode("utf-8")).hexdigest()}


TOOLS = {"csv_stats": csv_stats, "count_keyword": count_keyword,
         "hash_text": hash_text, "write_report": write_report}


def main() -> None:
    _limits()
    plan = json.loads(sys.stdin.read())
    out = io.StringIO()
    for step in plan.get("steps", []):
        tool, args = step.get("tool"), step.get("args", {})
        if tool in BLOCKED_TOOLS or tool not in ALLOWED_TOOLS:
            rec = {"tool": tool, "status": "blocked",
                   "reason": "tool is not on the sandbox allowlist; execution refused"}
        else:
            try:
                rec = {"tool": tool, "status": "ok", "output": TOOLS[tool](args)}
            except Exception as exc:  # execution errors are evidence too
                rec = {"tool": tool, "status": "error", "error": f"{type(exc).__name__}: {exc}"}
        rec["args_sha256"] = hashlib.sha256(
            json.dumps(args, sort_keys=True).encode("utf-8")).hexdigest()
        out.write(json.dumps(rec) + "\n")
    sys.stdout.write(out.getvalue())


if __name__ == "__main__":
    main()
