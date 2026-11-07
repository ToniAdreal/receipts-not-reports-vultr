from app.receipts import ReceiptChain, verify_chain, GENESIS

TS = "2026-11-07T00:00:00+00:00"


def build():
    c = ReceiptChain()
    c.append(TS, "run_start", {"agent": "demo"})
    c.append(TS, "tool_call", {"tool": "csv_stats", "status": "ok", "output": {"rows": 8}})
    c.append(TS, "blocked_action", {"tool": "read_secret", "status": "blocked"})
    return c


def test_chain_links_and_head():
    c = build()
    ev = c.to_list()
    assert ev[0]["prev_hash"] == GENESIS
    assert ev[1]["prev_hash"] == ev[0]["hash"]
    assert ev[2]["prev_hash"] == ev[1]["hash"]
    assert c.head == ev[-1]["hash"]


def test_verify_intact_chain():
    res = verify_chain(build().to_list())
    assert res["valid"] is True and res["checked"] == 3


def test_verify_detects_content_tamper():
    ev = build().to_list()
    ev[1]["payload"]["output"]["rows"] = 9999  # doctor the evidence
    res = verify_chain(ev)
    assert res["valid"] is False and res["first_bad_seq"] == 1


def test_verify_detects_deletion():
    ev = build().to_list()
    del ev[1]
    res = verify_chain(ev)
    assert res["valid"] is False


def test_verify_detects_reorder():
    ev = build().to_list()
    ev[1], ev[2] = ev[2], ev[1]
    res = verify_chain(ev)
    assert res["valid"] is False


def test_deterministic_hashes():
    a, b = build().to_list(), build().to_list()
    assert [e["hash"] for e in a] == [e["hash"] for e in b]
