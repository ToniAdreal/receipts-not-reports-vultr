# Receipts, Not Reports

**Don't trust what an agent says it did. Verify it.**

An AI agent's self-report is a claim, not evidence. Receipts, Not Reports runs
an agent's real work inside a contained sandbox, captures every tool call —
including the actions the sandbox *refused* — into a tamper-evident,
hash-chained receipt log, and then checks the agent's own summary against
that chain. Wrong numbers and invented actions are flagged claim by claim.

Built for the **Vultr: Agent Rush Hackathon — Challenge 1: Blast Radius Zero**,
whose example directions include "Research with Receipts" and whose best-for
list includes verification and safety.

## Live demo

- **Demo URL:** https://receipts-not-reports.onrender.com
  (verified live 2026-11-07: homepage, full demo run, and `/api/health`
  all checked end to end.)
- **Hosting note:** the deployment target is a Vultr Cloud Compute VM
  (see below). The event's $200 Vultr credit pool was exhausted before
  our claim could be redeemed, so the live demo above currently runs on
  a fallback host (Render free tier; it may cold-start for ~50 seconds
  after idle). The app is a standard uvicorn service with no
  Vultr-specific code paths, and the Vultr VM deployment proceeds
  unchanged if credit lands before the submission deadline.

## How it works

1. **Contained execution.** The agent's plan runs in a subprocess sandbox:
   fresh throwaway working directory, scrubbed environment (no API keys or
   host secrets), CPU/memory rlimits, wall-clock timeout, output cap, and the
   directory is destroyed after the run. Only allowlisted tools can execute.
2. **Containment moment.** In the demo run the agent attempts to read a secret
   and to run a shell command. The sandbox refuses both — and the refusals are
   recorded as first-class receipts, so "the agent was contained" is itself
   verifiable, not just asserted.
3. **Receipt chain.** Every event (run start, tool call, blocked action,
   artifact, run end) is appended with a SHA-256 hash covering the previous
   event's hash and the event's canonical content. Editing, deleting, or
   reordering history breaks the chain at the first modified event.
4. **Claim verification.** The agent's self-report is parsed into claims
   (tool executed / value equals / action blocked). Each claim is graded
   against the chain: `verified`, `mismatch` (evidence disagrees), or
   `no_evidence` (nothing backs it). The seeded demo agent makes two false
   claims on purpose — one wrong total, one invented "I emailed the report" —
   and the UI shows both being caught.

The demo dataset (`app/demo_data/demo_orders.csv`) is fictional and labelled
DEMO everywhere it surfaces. No real metrics, users, or results are claimed.

## Vultr architecture (Challenge 1)

- **Vultr Cloud Compute VM** hosts this FastAPI backend and web UI as the
  central control layer: it plans the task, dispatches it to the sandbox,
  and serves verification. (Deployment target; the app is a standard
  uvicorn service behind any reverse proxy.)
- **Vultr Serverless Inference** (`https://api.vultrinference.com/v1`,
  OpenAI-compatible) provides the agent's LLM narration when
  `VULTR_INFERENCE_API_KEY` and `VULTR_INFERENCE_MODEL` are set. Without
  them, a deterministic local narrator keeps the demo runnable offline —
  the receipt and verification logic never depends on the model.
- **Sandboxing**: subprocess isolation in this MVP (scrubbed env, rlimits,
  timeout, throwaway cwd). The deployment path swaps the worker transport
  for a Docker container per run (`docker run --rm --network none
  --memory 256m --cpus 1`) — the tool allowlist and receipt format are
  unchanged. Vultr GPUs are not used (not available for this event).

## Run it

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --port 8000
# open http://localhost:8000 and click "Run demo agent"
```

API:

- `POST /api/demo/run` — run the contained demo agent; returns the receipt
  chain, the agent's claims, and per-claim verdicts.
- `POST /api/verify` — `{events, claims}`: re-check chain integrity and claims
  (this is what catches a tampered log).
- `POST /api/ingest` — `{records, claims}`: build a receipt chain from any
  external agent's tool-call log and verify its claims against it.
- `GET /api/health`

## Tests

```bash
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q   # 19 tests: chain, verifier, sandbox, API
```

## License

MIT (hackathon submissions must be original and MIT-compliant).
