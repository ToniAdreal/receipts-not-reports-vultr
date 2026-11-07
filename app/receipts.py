"""Tamper-evident receipt chain.

Every piece of evidence (a tool call, a blocked action, a produced artifact)
is appended as an event whose SHA-256 hash covers the previous event's hash
plus the canonical encoding of the event itself. Editing, deleting, or
reordering any historical event breaks every hash after it, so a verifier can
detect tampering without trusting the agent or the log producer.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, asdict
from typing import Any

GENESIS = "0" * 64


def canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def event_hash(prev_hash: str, body: dict) -> str:
    return hashlib.sha256((prev_hash + canonical(body)).encode("utf-8")).hexdigest()


@dataclass
class Receipt:
    seq: int
    ts: str
    kind: str  # e.g. "tool_call", "blocked_action", "artifact", "run_start", "run_end"
    payload: dict
    prev_hash: str
    hash: str

    def body(self) -> dict:
        return {"seq": self.seq, "ts": self.ts, "kind": self.kind, "payload": self.payload}

    def to_dict(self) -> dict:
        return asdict(self)


class ReceiptChain:
    def __init__(self) -> None:
        self.events: list[Receipt] = []

    def append(self, ts: str, kind: str, payload: dict) -> Receipt:
        prev = self.events[-1].hash if self.events else GENESIS
        body = {"seq": len(self.events), "ts": ts, "kind": kind, "payload": payload}
        r = Receipt(seq=body["seq"], ts=ts, kind=kind, payload=payload,
                    prev_hash=prev, hash=event_hash(prev, body))
        self.events.append(r)
        return r

    @property
    def head(self) -> str:
        return self.events[-1].hash if self.events else GENESIS

    def to_list(self) -> list[dict]:
        return [e.to_dict() for e in self.events]

    @staticmethod
    def from_list(events: list[dict]) -> "ReceiptChain":
        c = ReceiptChain()
        for e in events:
            c.events.append(Receipt(**e))
        return c


def verify_chain(events: list[dict]) -> dict:
    """Recompute the chain from scratch. Returns integrity verdict."""
    prev = GENESIS
    for i, e in enumerate(events):
        try:
            body = {"seq": e["seq"], "ts": e["ts"], "kind": e["kind"], "payload": e["payload"]}
        except (KeyError, TypeError):
            return {"valid": False, "checked": i, "first_bad_seq": i,
                    "reason": "malformed event"}
        if e.get("seq") != i:
            return {"valid": False, "checked": i, "first_bad_seq": i,
                    "reason": f"sequence gap or reorder at position {i}"}
        if e.get("prev_hash") != prev:
            return {"valid": False, "checked": i, "first_bad_seq": i,
                    "reason": "prev_hash does not match previous event hash"}
        if event_hash(prev, body) != e.get("hash"):
            return {"valid": False, "checked": i, "first_bad_seq": i,
                    "reason": "event hash mismatch (content was modified)"}
        prev = e["hash"]
    return {"valid": True, "checked": len(events), "first_bad_seq": None,
            "reason": "chain intact", "head": prev}
