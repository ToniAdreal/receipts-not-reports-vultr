"""Claim-vs-evidence verification.

An agent's self-report is a list of claims. Each claim is checked against the
receipt chain's evidence events — never against the agent's own words.

Claim shapes:
  {"type": "tool_executed", "tool": "csv_stats"}
      Verified if a tool_call event for that tool has status "ok".
  {"type": "value", "tool": "csv_stats", "field": "total_amount", "value": 123.45}
      Verified if the tool's recorded output field equals the claimed value.
  {"type": "blocked", "tool": "read_secret"}
      Verified if a blocked_action event exists for that tool (containment proof).

Verdicts: "verified", "mismatch" (evidence exists but disagrees),
"no_evidence" (nothing in the chain backs the claim).
"""
from __future__ import annotations


def _tool_events(events: list[dict], kind: str, tool: str) -> list[dict]:
    return [e for e in events
            if e.get("kind") == kind and e.get("payload", {}).get("tool") == tool]


def check_claim(claim: dict, events: list[dict]) -> dict:
    ctype, tool = claim.get("type"), claim.get("tool")
    result = {"claim": claim, "verdict": "no_evidence", "evidence_seq": None, "detail": ""}

    if ctype == "blocked":
        hits = _tool_events(events, "blocked_action", tool)
        if hits:
            result.update(verdict="verified", evidence_seq=hits[0]["seq"],
                          detail="sandbox refusal is recorded in the chain")
        else:
            result["detail"] = "no blocked_action event for this tool"
        return result

    hits = [e for e in _tool_events(events, "tool_call", tool)
            if e["payload"].get("status") == "ok"]
    if not hits:
        result["detail"] = f"no successful {tool} tool_call in the evidence chain"
        return result

    ev = hits[-1]
    result["evidence_seq"] = ev["seq"]
    if ctype == "tool_executed":
        result.update(verdict="verified", detail="successful tool_call found in chain")
    elif ctype == "value":
        actual = ev["payload"].get("output", {}).get(claim.get("field"))
        if actual == claim.get("value"):
            result.update(verdict="verified", detail=f"evidence value {actual!r} matches claim")
        else:
            result.update(verdict="mismatch",
                          detail=f"claimed {claim.get('value')!r} but evidence says {actual!r}")
    else:
        result["detail"] = f"unknown claim type {ctype!r}"
    return result


def verify_report(events: list[dict], claims: list[dict]) -> dict:
    results = [check_claim(c, events) for c in claims]
    counts = {"verified": 0, "mismatch": 0, "no_evidence": 0}
    for r in results:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    return {"results": results, "counts": counts,
            "all_verified": counts["mismatch"] == 0 and counts["no_evidence"] == 0}
