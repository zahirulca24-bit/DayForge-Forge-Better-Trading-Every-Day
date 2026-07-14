# Task Register

Only one task may be active at a time. A task is active when its state is `CLAIMED`, `IN PROGRESS`, `CODE PASS`, `CI PASS` or `RUNTIME PENDING`.

## Current active task

| Task ID | Title | Owner | State | Branch / PR | Completion evidence |
|---|---|---|---|---|---|
| GOV-001 | Create chat-independent Project Control System | ChatGPT session 14 Jul 2026 | CODE PASS / REVIEW PENDING | `docs/compact-readme-pending-2026-07-14` / PR #52 | Control files created; main not merged |

## Engineering queue

| Priority | Task ID | Title | State | Dependency |
|---:|---|---|---|---|
| P0-1 | DAILY-LOSS-AUTHORITY-001 | Authoritative Bybit 5% BDT-day loss circuit | AVAILABLE | GOV-001 review/closure |
| P0-2 | JOURNAL-IDENTITY-001 | Persist/backfill `orderId`, `orderLinkId`, `execId` and fills | AVAILABLE | GOV-001 review/closure |
| P0-3 | PNL-MATCH-001 | Exact overlapping-trade PnL attribution | CODE PASS / PR #48 NOT MERGED | Product Owner merge decision |
| P0-4 | STATE-CLASS-001 | Active/pending/stale/closed separation | CODE PASS / PR #49 NOT MERGED | Product Owner merge decision |
| P0-5 | AUTH-SECURITY-001 | Token expiry, logout/revoke, rate limiting | CODE PASS / PR #50 NOT MERGED | Product Owner merge decision |
| P1-1 | WS-READINESS-001 | Private WS degradation/readiness truth | AVAILABLE | Issue #54 |
| P1-2 | CONFIG-AUTHORITY-001 | One effective risk/settings/trade-count source | AVAILABLE | Issue #55 |
| P1-3 | RUNTIME-STORAGE-001 | Durable Render primary database | AVAILABLE | Issue #56 |
| P1-4 | PERFORMANCE-TRUTH-001 | Reconciled-only performance metrics | AVAILABLE | Issue #57 and Journal identity |
| P2-1 | INCIDENT-DEDUPE-001 | Expected execution-skip deduplication | AVAILABLE | Issue #58 |
| VERIFY-001 | FULL-LIFECYCLE-001 | TP, partial, close, refresh, restart and cleanup verification | BLOCKED | Issues #51 and #53 |

## Claim procedure

Before implementation, update one row with:

- owner/session;
- `CLAIMED` state;
- exact branch name;
- scope boundary;
- dependency check.

No other task may be started until the active task becomes `VERIFIED COMPLETE`, `BLOCKED`, `PAUSED` or `SUPERSEDED` by explicit Product Owner direction.

## Completion rule

A task may be marked `VERIFIED COMPLETE` only when its required evidence exists. A PR, code diff or passing unit test alone is not sufficient when runtime verification is required.