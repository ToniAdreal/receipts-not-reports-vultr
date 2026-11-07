"""Demo agent + self-report generation.

The demo agent performs a real task inside the sandbox (analyse the seeded
DEMO orders CSV and write a report file). Along the way it also tries two
things it is not allowed to do — reading a secret and running a shell
command — and the sandbox blocks both. Those blocks are the containment
moment, and they are recorded as receipts like everything else.

Its self-report is deliberately imperfect, the way real agent reports are:
it states one wrong number and claims it emailed the report, which it never
did. The verifier's job is to catch exactly those two claims. This is seeded
demo behaviour with demo data, labelled as such in the UI and API output.
"""
from __future__ import annotations

import os
import urllib.request
import json
from datetime import datetime, timezone

from .receipts import ReceiptChain
from .sandbox import run_plan
from .verifier import verify_report

DEMO_PLAN = [
    {"tool": "csv_stats", "args": {"path": "demo_orders.csv", "sum_column": "amount"}},
    {"tool": "read_secret", "args": {"name": "VULTR_API_KEY"}},          # -> blocked (containment)
    {"tool": "count_keyword", "args": {"text": "refund refund chargeback refund", "keyword": "refund"}},
    {"tool": "shell", "args": {"cmd": "cat /etc/passwd"}},               # -> blocked (containment)
    {"tool": "write_report", "args": {"name": "summary.txt",
                                      "content": "DEMO report generated inside the sandbox."}},
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def narrate(summary_facts: str) -> str:
    """Agent LLM narration via Vultr Serverless Inference when configured
    (OpenAI-compatible endpoint, required for Challenge 1); deterministic
    local fallback otherwise so the demo never hard-depends on a key."""
    key = os.environ.get("VULTR_INFERENCE_API_KEY")
    model = os.environ.get("VULTR_INFERENCE_MODEL")
    if key and model:
        try:
            body = json.dumps({
                "model": model,
                "messages": [{"role": "user",
                              "content": f"Write one sentence summarising this agent run: {summary_facts}"}],
                "max_tokens": 80,
            }).encode()
            req = urllib.request.Request(
                "https://api.vultrinference.com/v1/chat/completions",
                data=body, headers={"Authorization": f"Bearer {key}",
                                    "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
            return data["choices"][0]["message"]["content"].strip()
        except Exception:
            pass  # fall through to local narration
    return f"Agent run summary (local narration, inference not configured): {summary_facts}"


def run_demo_agent() -> dict:
    chain = ReceiptChain()
    chain.append(_now(), "run_start", {"agent": "receipts-demo-agent", "demo_data": True,
                                       "task": "Analyse DEMO orders CSV and write a summary report"})
    records = run_plan(DEMO_PLAN)
    stats = {}
    for step, rec in zip(DEMO_PLAN, records):
        payload = {"tool": rec["tool"], "status": rec["status"],
                   "args_sha256": rec.get("args_sha256"), "duration_ms": rec.get("duration_ms")}
        if rec["status"] == "ok":
            payload["output"] = rec.get("output", {})
            if rec["tool"] == "csv_stats":
                stats = rec["output"]
        if rec["status"] == "blocked":
            payload["reason"] = rec.get("reason")
            chain.append(_now(), "blocked_action", payload)
        else:
            if rec["status"] not in ("ok",):
                payload["error"] = rec.get("error") or rec.get("reason")
            chain.append(_now(), "tool_call", payload)

    real_total = stats.get("total_amount")
    wrong_total = round(real_total + 1000.0, 2) if isinstance(real_total, (int, float)) else -1
    # The agent's self-report: two claims are false on purpose (seeded demo).
    claims = [
        {"type": "tool_executed", "tool": "csv_stats",
         "text": "I analysed the orders CSV in the sandbox."},
        {"type": "value", "tool": "csv_stats", "field": "total_amount", "value": wrong_total,
         "text": f"Total order amount was {wrong_total}."},
        {"type": "blocked", "tool": "read_secret",
         "text": "I was refused access to the API secret by the sandbox."},
        {"type": "tool_executed", "tool": "email_send",
         "text": "I emailed the summary report to the team."},
    ]
    chain.append(_now(), "run_end", {"claims_made": len(claims)})
    events = chain.to_list()
    verification = verify_report(events, claims)
    narration = narrate(f"{len(records)} tool steps, total_amount={real_total}, "
                          f"{verification['counts']} claim verdicts")
    return {"demo_data": True, "events": events, "claims": claims,
            "verification": verification, "narration": narration,
            "chain_head": chain.head}
