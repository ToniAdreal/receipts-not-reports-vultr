# Build Log — Receipts, Not Reports (Vultr Agent Rush)

## 2026-11-07 ~03:30–04:10 PST — Round 1: research, scaffold, core, tests

Decision confirmed GO by user. Deadline: **Sun 2026-11-08 15:00 PST**.
Track chosen: **Challenge 1 — Blast Radius Zero** (official page lists
"Research with Receipts" as an example direction and verification/safety as a
best-for area). Requirements research saved in `REQUIREMENTS.md`.

### Built

- `app/receipts.py` — SHA-256 hash-chained receipt log (canonical JSON,
  genesis-linked), plus `verify_chain` that detects content edits, deletions,
  and reordering and reports the first bad sequence number.
- `app/sandbox_worker.py` + `app/sandbox.py` — contained execution: worker
  subprocess with scrubbed environment (no secrets/API keys), fresh temp
  working dir seeded with demo data, CPU (10s) and memory (256MB) rlimits,
  15s wall-clock timeout, 64KB output cap, directory destroyed after the run.
  Tool allowlist: `csv_stats`, `count_keyword`, `hash_text`, `write_report`.
  `shell`, `read_secret`, `network_fetch`, etc. are refused and returned as
  blocked records (the containment moment).
- `app/verifier.py` — claim-vs-evidence grading: `tool_executed`, `value`,
  and `blocked` claim types → `verified` / `mismatch` / `no_evidence`.
- `app/agent.py` — demo agent: runs a 5-step plan (CSV analysis, two blocked
  attempts, keyword count, report write), then issues a self-report with two
  seeded false claims (wrong total, invented email) for the verifier to catch.
  Narration goes through Vultr Serverless Inference when
  `VULTR_INFERENCE_API_KEY` + `VULTR_INFERENCE_MODEL` are set, with a
  deterministic local fallback.
- `app/main.py` — FastAPI: `/`, `/api/health`, `/api/demo/run`,
  `/api/verify`, `/api/ingest` (chain an external agent log, then verify it).
- `app/static/index.html` — demo UI: run button, claims-vs-evidence table,
  receipt chain table with blocked actions highlighted as containment,
  one-click "tamper with a receipt" + re-verify to show the chain breaking.
- `app/demo_data/demo_orders.csv` — 8 fictional DEMO orders, labelled demo.

### Test results (real, this machine)

- `.venv/bin/python -m pytest -q` → **19 passed** (chain 6, verifier 5,
  sandbox 4, API 4) in 1.16s. Only warning: Starlette TestClient deprecation.
- Live smoke test: uvicorn on :8791, `/api/health` ok; `POST /api/demo/run`
  returned chain valid = true, 7 events, verdict counts
  {verified: 2, mismatch: 1, no_evidence: 1} — exactly the seeded outcome;
  UI HTML served. Server stopped after the check.
- Demo CSV total verified by hand: amounts sum to 1520.48, matching tests.

### How to run

```bash
cd ~/workspace/vultr-agent-rush
.venv/bin/uvicorn app.main:app --port 8000   # then open http://localhost:8000
```

### Remaining TODO toward submission

1. **Vultr deployment (hard requirement, Challenge 1)** — deploy this app to
   a Vultr VM and set `VULTR_INFERENCE_API_KEY` / `VULTR_INFERENCE_MODEL` so
   agent narration uses Vultr Serverless Inference. Depends on the Vultr
   account + $200 credit step, which is handled separately (not touched here).
   Fallback if VM is not ready in time: any public URL for the demo link, but
   the official expectations say the web app must be deployed on Vultr —
   treat fallback as incomplete.
2. Optional hardening if time allows: swap sandbox transport to Docker
   (`--network none --memory 256m --cpus 1`, one container per run).
3. **Public GitHub repo** — push this directory (exclude `.venv`), README is
   already written to LabLab's spec (Vultr usage, architecture, use case).
4. **Demo video** (must show the containment moment): script — run demo →
   show read_secret + shell blocked → show the two false claims caught →
   tamper a receipt → re-verify shows the chain broken. Target 2–3 minutes.
5. **Cover image + slide presentation** for the LabLab form (no format spec
   found on the official page).
6. **LabLab submission form** fields (per official page): project title,
   short description, long description, technology & category tags, cover
   image, video presentation, slide presentation, public GitHub repo, demo
   application platform + application URL. Submit on LabLab before
   2026-11-08 15:00 PST. Submission itself is a separate step (not done here).
7. Team on the LabLab project: user + Ma Xudong (Jeremiah Ma), team size 2 of
   max 6 — confirm both members are attached to the project in LabLab during
   the submission step.

### Blockers / notes

- No blocker for the build itself. The only external dependency is the
  Vultr account/credit/deployment step (item 1), intentionally untouched in
  this round.
- Exact LabLab form field limits are unverified (form is behind login).
