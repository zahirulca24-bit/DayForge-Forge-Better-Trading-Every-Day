# Current Handoff

> Keep this file short. Update it before ending or changing chat.

## Session

- Date: 14 July 2026 BDT
- Repository: `zahirulca24-bit/DayForge-Forge-Better-Trading-Every-Day`
- Main head inspected: `52604c387d54b948b46ff7f1b45856c6be57cb27`
- Working branch: `docs/compact-readme-pending-2026-07-14`
- Open documentation PR: #52
- Main merge: **NOT PERFORMED**

## Active task

`GOV-001 — Create chat-independent Project Control System`

State: **CODE/DOCUMENTATION PASS — PRODUCT OWNER REVIEW PENDING**

## Work completed in this branch

- Replaced oversized README daily log with a compact current-status README.
- Added `docs/STATUS_HISTORY.md`.
- Added root `PROJECT_CONTROL.md`.
- Added Decision, Task, Evidence and Handoff registers.
- Added exact session-start prompt.
- Created/updated runtime issues #37, #51 and #53–#58.
- Recorded current screenshot evidence without claiming unsupported strategy root causes.

## Open code PRs — not merged

- PR #48 — exact PnL matching
- PR #49 — active/pending/stale classification
- PR #50 — authentication hardening

## Critical open issues

1. Issue #53 — authoritative Bybit daily-loss hard stop
2. Issue #51 — Journal order/execution identity persistence
3. Issue #54 — Private WS degradation/readiness
4. Issue #55 — configuration source drift
5. Issue #56 — Render storage durability
6. Issue #57 — performance metric truth
7. Issue #58 — incident deduplication
8. Issue #37 — full lifecycle verification

## Safety status

Demo auto execution should remain stopped until Issue #53 is fixed and runtime-verified. Live-capital trading is not approved.

## Next allowed action

After Product Owner reviews/closes `GOV-001`, claim exactly one task. Current priority is Issue #53 unless the Product Owner explicitly chooses another task.

## Do not assume

- Do not treat Bybit ledger loss as safely matched to individual Journal rows without identity.
- Do not claim the strategy is the root cause of the loss cluster before data integrity is repaired.
- Do not claim Private WS runtime pass from an older connected screenshot when later screenshots show connecting.
- Do not merge any PR without explicit Product Owner approval.