# Demo Video Script — Receipts, Not Reports

- **Target length:** ~2:45 (hard limit 3:00)
- **Format:** screen recording of the live demo UI at 1080p, voiceover (VO)
  recorded over it. Record against the deployed demo:
  `<!-- PLACEHOLDER: live demo URL after Vultr VM deployment -->`
  (a local run at http://localhost:8000 is visually identical for rehearsal).
- **Setup before recording:** open the demo page, browser zoom 100%, run the
  demo once off-camera to confirm the run completes, then reload the page so
  the recording starts clean. Demo data is fictional and labelled DEMO on
  screen — say so once, on camera.
- **Required beats (Challenge 1):** the containment moment (0:55) and the
  tamper-and-reverify catch (2:00). Do not cut these.

---

## 0:00–0:20 — Hook

- **On screen:** demo UI, idle. Title "Receipts, Not Reports" visible.
  Slow zoom toward the tagline.
- **VO:** "This agent just finished a job, and it wrote a nice summary of
  what it did. There's only one problem: parts of that summary aren't true.
  Receipts, Not Reports doesn't trust the summary. It verifies it — against
  a tamper-evident receipt chain of what actually executed inside the
  sandbox."

## 0:20–0:55 — Run the demo agent

- **On screen:** click **"Run demo agent"**. The run summary line appears,
  then the **Claims vs evidence** table populates. Pause on the summary:
  5 tool steps, total_amount=1520.48, verdict counts
  {verified: 2, mismatch: 1, no_evidence: 1}.
- **VO:** "The agent analysed a small orders file — clearly labelled demo
  data — inside a contained sandbox: no secrets in its environment, CPU and
  memory limits, a timeout, and a working directory that is destroyed when
  the run ends. Every step it took was written into a hash-chained receipt
  log. Now let's grade its report against that log."

## 0:55–1:30 — THE CONTAINMENT MOMENT (required)

- **On screen:** scroll to the **Receipt chain** table. Highlight rows #2
  and #4: `blocked_action — read_secret · blocked — CONTAINMENT: execution
  refused` and `blocked_action — shell · blocked — CONTAINMENT: execution
  refused`. Hold on each row for ~3 seconds.
- **VO:** "Halfway through the job, the agent tried two things it should
  never do: read an API secret, and run an arbitrary shell command. The
  sandbox refused both — nothing executed, nothing leaked. Any tool outside
  the allowlist gets the same answer: network fetches included. And notice:
  the refusals are receipts too, sitting in the chain. So 'the agent was
  contained' isn't something we assert. It's something anyone can verify."

## 1:30–2:00 — The false claims get caught

- **On screen:** scroll back up to **Claims vs evidence**. Highlight the
  `mismatch` row ("Total order amount was 2520.48" → evidence says
  1520.48), then the `no_evidence` row ("I emailed the summary report to
  the team" → no email tool call in the chain), then the two `verified`
  rows.
- **VO:** "Here's why this matters. The agent's report claims a total of
  2520.48. The receipts say 1520.48 — mismatch. It also claims it emailed
  the report to the team. There is no email anywhere in the evidence chain
  — no evidence. The claims that are true verify cleanly. Two lies, both
  caught, claim by claim."

## 2:00–2:35 — TAMPER AND RE-VERIFY (required)

- **On screen:** scroll to the chain status line: "Chain integrity: VALID
  (7 events checked)". Click **"Tamper with one receipt"**, then click
  **"Re-verify chain"**. Hold on the result: the chain now reports BROKEN,
  naming the first modified event.
- **VO:** "But what if someone edits the log afterwards to hide all this?
  Watch. I'll tamper with one receipt — change a single value in the
  history — and re-verify. The chain breaks, and it points at the exact
  event that was touched. Every receipt is hash-linked to the one before
  it, so rewriting history is detectable, at the first modified link."

## 2:35–2:50 — Close

- **On screen:** scroll back to the top: title, tagline, and the claims
  table in one frame. End card (title slide from the deck) if available.
- **VO:** "Agents are going to do real work, inside real infrastructure
  like this Vultr VM, with narration from Vultr Serverless Inference. The
  question is whether anyone can check what they did. Don't accept the
  report. Demand the receipts."

---

## Recording notes

- If a live run surprises (it shouldn't — the demo is deterministic), re-run
  off-camera and re-record the segment; the seeded outcome is always
  verified 2 / mismatch 1 / no_evidence 1, chain of 7 events.
- The same verify flow works on external logs via `POST /api/ingest` —
  mention only if a segment runs short; do not add a terminal segment
  unless the total stays under 3:00.
- Upload as the "Video presentation" field of the LabLab submission.
