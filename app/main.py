"""Receipts, Not Reports — FastAPI app.

Endpoints:
  GET  /                demo UI
  GET  /api/health
  POST /api/demo/run    run the contained demo agent, return chain + verification
  POST /api/verify      {events, claims} -> chain integrity + claim verdicts
  POST /api/ingest      {records: [raw tool records], claims: [...]}
                        build a receipt chain from an external agent log, then verify
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .agent import run_demo_agent
from .receipts import ReceiptChain, verify_chain
from .verifier import verify_report

app = FastAPI(title="Receipts, Not Reports")
STATIC = Path(__file__).with_name("static")


class VerifyRequest(BaseModel):
    events: list[dict]
    claims: list[dict] = []


class IngestRequest(BaseModel):
    records: list[dict]
    claims: list[dict] = []


@app.get("/api/health")
def health():
    return {"ok": True, "service": "receipts-not-reports"}


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


@app.post("/api/demo/run")
def demo_run():
    result = run_demo_agent()
    result["chain"] = verify_chain(result["events"])
    return result


@app.post("/api/verify")
def verify(req: VerifyRequest):
    return {"chain": verify_chain(req.events),
            "verification": verify_report(req.events, req.claims)}


@app.post("/api/ingest")
def ingest(req: IngestRequest):
    chain = ReceiptChain()
    now = datetime.now(timezone.utc).isoformat()
    for rec in req.records:
        kind = "blocked_action" if rec.get("status") == "blocked" else "tool_call"
        chain.append(now, kind, rec)
    events = chain.to_list()
    return {"events": events, "chain": verify_chain(events),
            "verification": verify_report(events, req.claims),
            "chain_head": chain.head}
