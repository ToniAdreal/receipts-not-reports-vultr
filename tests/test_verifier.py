from app.receipts import ReceiptChain
from app.verifier import check_claim, verify_report

TS = "2026-11-07T00:00:00+00:00"


def events():
    c = ReceiptChain()
    c.append(TS, "tool_call", {"tool": "csv_stats", "status": "ok",
                               "output": {"rows": 8, "total_amount": 1520.48}})
    c.append(TS, "blocked_action", {"tool": "read_secret", "status": "blocked"})
    return c.to_list()


def test_tool_executed_verified():
    r = check_claim({"type": "tool_executed", "tool": "csv_stats"}, events())
    assert r["verdict"] == "verified"


def test_value_match_and_mismatch():
    ev = events()
    ok = check_claim({"type": "value", "tool": "csv_stats", "field": "total_amount",
                      "value": 1520.48}, ev)
    bad = check_claim({"type": "value", "tool": "csv_stats", "field": "total_amount",
                       "value": 2520.48}, ev)
    assert ok["verdict"] == "verified"
    assert bad["verdict"] == "mismatch" and "1520.48" in bad["detail"]


def test_no_evidence_for_invented_action():
    r = check_claim({"type": "tool_executed", "tool": "email_send"}, events())
    assert r["verdict"] == "no_evidence"


def test_blocked_claim_verified_by_refusal_receipt():
    r = check_claim({"type": "blocked", "tool": "read_secret"}, events())
    assert r["verdict"] == "verified"


def test_report_counts():
    rep = verify_report(events(), [
        {"type": "tool_executed", "tool": "csv_stats"},
        {"type": "tool_executed", "tool": "email_send"},
    ])
    assert rep["counts"] == {"verified": 1, "mismatch": 0, "no_evidence": 1}
    assert rep["all_verified"] is False
