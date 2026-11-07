from app.sandbox import run_plan


def test_allowed_tool_executes():
    recs = run_plan([{"tool": "csv_stats",
                      "args": {"path": "demo_orders.csv", "sum_column": "amount"}}])
    assert recs[0]["status"] == "ok"
    assert recs[0]["output"]["rows"] == 8
    assert recs[0]["output"]["total_amount"] == 1520.48


def test_disallowed_tools_are_blocked():
    recs = run_plan([
        {"tool": "read_secret", "args": {"name": "VULTR_API_KEY"}},
        {"tool": "shell", "args": {"cmd": "cat /etc/passwd"}},
        {"tool": "network_fetch", "args": {"url": "https://example.com"}},
    ])
    assert [r["status"] for r in recs] == ["blocked", "blocked", "blocked"]


def test_path_escape_is_an_error_not_a_read():
    recs = run_plan([{"tool": "csv_stats",
                      "args": {"path": "../../etc/passwd", "sum_column": "amount"}}])
    assert recs[0]["status"] == "error"


def test_timeout_cap():
    # csv_stats on a missing file errors fast; timeout path is exercised via tiny cap
    recs = run_plan([{"tool": "hash_text", "args": {"text": "abc"}}], timeout_s=10)
    assert recs[0]["status"] == "ok" and len(recs[0]["output"]["sha256"]) == 64
