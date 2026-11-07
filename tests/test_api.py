from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200 and r.json()["ok"] is True


def test_demo_run_end_to_end():
    r = client.post("/api/demo/run")
    assert r.status_code == 200
    data = r.json()
    assert data["demo_data"] is True
    assert data["chain"]["valid"] is True
    kinds = [e["kind"] for e in data["events"]]
    assert "blocked_action" in kinds  # containment moment present
    counts = data["verification"]["counts"]
    # Seeded demo agent: 2 honest claims verified, 1 wrong value, 1 invented action.
    assert counts["verified"] == 2
    assert counts["mismatch"] == 1
    assert counts["no_evidence"] == 1


def test_verify_endpoint_detects_tamper():
    data = client.post("/api/demo/run").json()
    data["events"][1]["payload"]["status"] = "forged"
    r = client.post("/api/verify", json={"events": data["events"], "claims": []})
    assert r.json()["chain"]["valid"] is False


def test_ingest_builds_chain_from_external_log():
    r = client.post("/api/ingest", json={
        "records": [{"tool": "csv_stats", "status": "ok", "output": {"rows": 3}}],
        "claims": [{"type": "tool_executed", "tool": "csv_stats"},
                   {"type": "tool_executed", "tool": "email_send"}],
    })
    data = r.json()
    assert data["chain"]["valid"] is True
    assert data["verification"]["counts"]["verified"] == 1
    assert data["verification"]["counts"]["no_evidence"] == 1
