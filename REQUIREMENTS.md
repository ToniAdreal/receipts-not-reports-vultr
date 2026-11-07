# Vultr: Agent Rush Hackathon — Requirements (researched 2026-11-07 ~03:30 PST)

Primary source (fetched directly, no login):
- LabLab event page: https://lablab.ai/ai-hackathons/vultr-hackathon
- Same page mirrored at: https://lablab.build/ai-hackathons/vultr-hackathon
- Vultr Community event page: https://community.vultr.com/e/vultr-agent-rush-hackathon

## Verified from the official LabLab event page

- **Event**: Vultr: Agent Rush Hackathon (LabLab × Vultr). Online build Nov 3–8, 2026, plus an optional onsite phase in Salt Lake City, UT (Pierpont Place) on Nov 8 for approved teams. Online participation is a supported path.
- **Deadline**: End of submissions **Nov 8, 3:00 PM Pacific Standard Time** (event schedule on the official page: "Nov 8 3:00 PM Pacific Standard Time End of Submissions!"). Page event window listed as 2026-11-03T16:00Z to 2026-11-08T23:00Z, which is consistent with Nov 8 15:00 PST.
- **Team size**: 1–6 people. Our team of 2 fits.
- **Registration**: register on lablab.ai AND join the LabLab Discord — both required. (Already done per team status; not re-done in this build step.)
- **Prizes**: $9,000 cash + $5,000 Vultr credits total (1st $5,000 + $3,000 credits; 2nd $3,000 + $1,000 credits; 3rd $1,000 + $1,000 credits), plus an onsite-only raffle. Prize distribution may take up to 90 days. Submissions must be original and MIT-compliant.
- **Per-participant credit**: every participant gets $200 in free Vultr credits (requires a Vultr account with an email not previously associated with a Vultr account). NOT claimed in this build step, per instructions.

## The two challenges (pick one)

### Challenge 1 — Blast Radius Zero (our track)
Build a web-based agent that performs real work (writing/running code, or operating a real browser) with every action contained inside a sandbox running on Vultr. "Containment-first is required. An agent that only chats is a demo; an agent that executes safely is a product."
- Best-for list explicitly includes **verification and safety**, and the example directions literally include **"Research with Receipts"** — our "Receipts, Not Reports" direction is a named example direction for this challenge.
- Execution patterns: (A) sandboxed code execution, (B) sandboxed browser use.
- Containment focus: process isolation, secret hygiene (no API keys inside the sandbox), resource limits (time/memory caps on every run), lifecycle discipline (reset/destroy environment after each task).
- **Submission expectations**: GitHub repo with setup + docs; **Vultr VM backend deployment**; public demo URL; recorded demo video; clear architecture and use-case explanation; **at least one containment moment shown in the demo video**.
- **Technology requirements (Challenge 1)**: Vultr VM backend + web app deployed on Vultr; **Vultr Serverless Inference required for agent LLM calls** (OpenAI-compatible endpoint `https://api.vultrinference.com/v1`); isolated sandbox execution required (Docker strongly recommended; OpenSandbox, gVisor, E2B, Microsandbox listed as examples). Vultr GPUs are NOT available for this event.

### Challenge 2 — Powering the Future of Work
Enterprise multi-step workflow product (sales ops, finance, HR, support, procurement). Requires Vultr VM backend + web deployment; Serverless Inference optional. Submission expectations are the same minus the containment moment. Our project fits Challenge 1 better (verification/safety is a named best-for area there), so we build for Challenge 1.

## What to submit (LabLab submission form, per official page)

- Basic information: project title, short description, long description, technology & category tags
- Cover image
- Video presentation
- Slide presentation
- Public GitHub repository
- Demo application platform + application URL
- README must explain: Vultr services/infrastructure used, backend/deployment architecture, the agent's use case and how it executes real tasks. (No separate Vultr architecture report needed.)
- Official submission must be completed **on LabLab** to be judged.

## Judging criteria (official)

1. **Application of Technology** — how effectively the chosen model(s) are integrated into the solution.
2. **Presentation** — clarity and effectiveness of the project presentation.
3. **Business Value** — impact and practical value, fit into business areas.
4. **Originality** — uniqueness and creativity, ability to demonstrate behaviors.

## Fit notes / risks for "Receipts, Not Reports"

- FIT: "Research with Receipts" is an official example direction for Challenge 1; verification/safety is a named best-for area. Our design extends it: the agent does real work inside a contained runner, every tool call is captured as evidence, and the receipt chain verifies the agent's self-report against that evidence.
- RISK 1 (must fix before submission): the backend must actually be deployed on a **Vultr VM** and the agent's LLM calls must go through **Vultr Serverless Inference**. This build implements an OpenAI-compatible inference adapter pointed at `https://api.vultrinference.com/v1` (env-configured, with a deterministic local fallback for offline dev), but the actual Vultr VM deployment depends on the separately handled Vultr account/credit step. Without a Vultr deployment, a Challenge 1 submission is incomplete.
- RISK 2: the demo video must show a **containment moment**. The MVP builds this in: the demo agent attempts a disallowed action (reading a secret / running a shell command) and the sandbox blocks it; the block itself is recorded as a receipt in the chain.
- RISK 3: "real executed results rather than described ones" — the MVP executes a real (seeded, clearly labeled demo) CSV analysis task inside the contained runner instead of only auditing pasted logs. Log/transcript ingestion is also supported via the API.

## Unverified

- Exact LabLab submission-form field names/limits beyond the sections listed above (the form itself sits behind login; not accessed in this step).
- Whether judges accept a non-Vultr hosted fallback demo URL if the Vultr VM is down (assume no; plan is Vultr VM as primary).
- Slide presentation format requirements (page says a slide presentation is part of the submission package but gives no format/length spec).
