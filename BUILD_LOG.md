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

## 2026-11-07 ~03:31–03:40 PST — Round 2: public repo + submission assets

- **Public GitHub repo: https://github.com/ToniAdreal/receipts-not-reports-vultr**
  The first-choice name `receipts-not-reports` was already taken by the
  user's own earlier Apart Research repo, so the `-vultr` suffix was used.
  Repo created public under ToniAdreal, git identity set to
  `ToniAdreal <184365500+ToniAdreal@users.noreply.github.com>`, project code
  committed (`.venv`/`__pycache__` excluded via existing `.gitignore`) and
  pushed to `main`. README gained a "Live demo" section with clearly marked
  placeholders (demo URL, VM details) — no URL or deployment fact invented;
  fill in after the Vultr VM deployment lands and is verified.
- **Cover image** — `submission/cover.png` (1920×1080): programmatic title
  band (no AI imagery) over a real screenshot of the running app's demo UI
  (`submission/ui_run.png`, captured locally via headless Chromium after an
  actual demo run: claims table with verified 2 / mismatch 1 / no_evidence 1
  and both blocked containment rows visible).
- **Slide deck** — `submission/slides.pptx` (7 slides, 16:9) + rendered
  `submission/slides.pdf`: problem, solution, how it works, containment
  moment, Vultr usage (VM + Serverless Inference adapter, live URL marked
  as placeholder), demo results from the tested build (19 tests passing,
  verdict counts verified 2 / mismatch 1 / no_evidence 1), team
  (Toni Adreal + Jeremiah Ma). Slides were rendered and visually checked;
  slide 7 layout fixed so no text is clipped or hidden behind the UI shot.
- **Video script** — `submission/video_script.md`: timed ~2:45 script
  mapped to on-screen UI actions, with the required containment moment
  (sandbox refusing `read_secret` and `shell`; `network_fetch` called out
  as refused by the same allowlist) at 0:55 and the tamper-and-reverify
  catch at 2:00.
- Submission assets were committed and pushed to the repo in this round
  (under `submission/`).

### Remaining TODO (unchanged from round 1, minus repo/assets)

1. **Vultr VM deployment + Serverless Inference key** — handled separately
   (account/$200 credit authorized by user). After it lands: replace the
   README/slides/script demo-URL placeholders with the verified live URL.
2. **Record the demo video** from `submission/video_script.md` (show the
   containment moment and the tamper catch).
3. **LabLab submission form** — handled separately; attach cover.png,
   slides, video, repo URL, and the live demo URL; confirm both team
   members (user + Ma Xudong) are on the project. Deadline
   2026-11-08 15:00 PST.

## 2026-11-07 ~07:55–08:10 PST — Round 3: demo video recorded

- **Demo video: `submission/demo_video.mp4` — 113.5s, 1920×1080, H.264 + AAC, 4.7MB** (ffprobe-verified; under the 3:00 limit). Six segments following `submission/video_script.md` (condensed VO to fit the pace): hook, run demo, containment moment (blocked `read_secret` + `shell` rows), false claims caught (mismatch 2520.48 vs 1520.48, no-evidence email claim), tamper + re-verify (chain flips to BROKEN: event hash mismatch), close on the cover end card.
- **All visuals are the real running app**: headless Chromium (Playwright) drove the local FastAPI app at :8000 — idle UI, run, tamper, re-verify — and captured screenshots; no AI imagery, no mock UI. Narration is platform TTS (default voice) with burned-in subtitles (28 cues, timed to the audio).
- **Verification**: 19 tests re-passed before recording; live smoke green; frames extracted at 0:08/0:30/0:55/1:25/1:40/1:50 and visually checked (containment rows highlighted, BROKEN status line legible, subtitles one line at the bottom).
- **Notes / deviations**: edge-tts (Microsoft) failed — the egress proxy blocks its TLS endpoint (SSL WRONG_VERSION_NUMBER) — so narration used the platform `/opt/hatch/bin/tts` CLI instead. The tamper VO is worded to what the UI actually shows ("status flips to broken: event hash mismatch") rather than claiming the UI names the exact event number, which it does not. The local server was stopped after capture. `.venv` gained `edge-tts` + `pillow` (build tooling only, not app deps).
- **Still open (not this round)**: Vultr VM deployment (blocked on the $200 coupon pool), replacing the demo-URL placeholder in README/slides, LabLab form submission. Deadline 2026-11-08 15:00 PST.

## 2026-11-07 ~08:24–08:30 PST — Round 4: fallback deployment (user decision)

- **User decision (08:24 PST):** if the $200 Vultr coupon pool stays empty, submit anyway with the demo hosted elsewhere, rather than abandoning the line. Coupon rechecks (every 30 min) continue; if credit lands before the deadline, Vultr VM deployment still proceeds and the demo URL gets swapped.
- **Fallback deploy:** new Render Web Service "receipts-not-reports" in the user's workspace, created via the Public Git repository method (Render's GitHub app had no access to this repo; no GitHub permission change was made). Python 3, build `pip install -r requirements.txt`, start `uvicorn app.main:app --host 0.0.0.0 --port $PORT`, Free tier, Oregon. First deploy of commit fbbacf8 went Live at 08:27:04 PST.
- **Live URL:** https://receipts-not-reports.onrender.com — verified end to end in the browser: homepage title and Run demo agent button present; a full demo run rendered (5 tool steps, verdicts verified 2 / mismatch 1 / no_evidence 1, chain integrity VALID across 7 events including the blocked read_secret and shell receipts); `/api/health` returned ok. Free tier cold-starts (~50s) after idle.
- **README** Live demo section now carries the real URL plus an honest hosting note (Vultr is the target; the credit pool was exhausted before our claim; fallback host until credit lands). No claim of a Vultr deployment that has not happened.
- **Still open:** LabLab submission form (attach cover.png, slides.pdf, demo_video.mp4, repo URL, demo URL above). Deadline 2026-11-08 15:00 PST.

## 2026-11-07 ~08:29–08:39 PST — Round 5: LabLab submission complete

- **Submitted** to the Vultr: Agent Rush Hackathon on LabLab (Challenge 1, C1-Blast Radius Zero, Online). Confirmation page: "Congratulations! You have successfully submitted your project for the Vultr: Agent Rush Hackathon event!" A cover-crop fix was then re-submitted ("Submission Updated!").
- **Project page:** https://lablab.build/ai-hackathons/vultr-hackathon/receipts-not-reports/receipts-not-reports — independently re-read by the main agent after submission: title, track, full long description (with the honest fallback-hosting note), GitHub / presentation / demo links, and the hosted video file all present.
- **Form adaptations:** long description trimmed to 1,962 of the 2,000-char limit (facts unchanged); demo platform recorded as "Other" (no Render option exists) with hosting explained in the Additional Information note; Technologies list on the form is a fixed AI-product list, so Vultr + OpenAI were selected and Python/FastAPI stay named in the description; Categories: Security, Developer Tools.
- **Team:** LabLab team "Receipts Not Reports" created (the form rejects commas in team names). Jeremiah Ma could not be added as a member: LabLab invite search found no account for him. He is credited as co-author in the submission's Additional Information note, the slides, and this repo.
- **Open tail:** coupon rechecks continue every 30 min. If Vultr credit lands before the 2026-11-08 15:00 PST deadline, deploy to a Vultr VM and update the submission's demo URL (the platform accepts updates, as the cover fix showed).
