# DayForge V2

> **DayForge — Forge Better Trading Every Day**

Bybit-first automated trading terminal built with FastAPI, React, PostgreSQL and Bybit V5 REST/WebSocket APIs.

## Current project status

| Field | Status |
|---|---|
| Product phase | **Demo Beta / Engineering Verification** |
| Default exchange mode | **Bybit Demo** |
| Live-capital approval | **BLOCKED / NOT APPROVED** |
| Current `main` head | `52604c387d54b948b46ff7f1b45856c6be57cb27` |
| Main automated verification | Backend **213/213 PASS** after PR #47 |
| Current operator evidence | Private WS connected, Public WS connected, REST/ledger data visible |
| Runtime verdict | **PARTIAL PASS / JOURNAL IDENTITY AND FULL LIFECYCLE PENDING** |
| Product Owner merge rule | No PR merge without explicit approval |
| Last status update | 14 July 2026, BDT |

Historical milestones and the former long daily log are kept in [`docs/STATUS_HISTORY.md`](docs/STATUS_HISTORY.md). The previous full README remains available through Git history.

---

## Product objective

DayForge must:

1. Scan liquid Bybit USDT perpetual markets.
2. Build separate Scalping and Intraday contexts.
3. Reject sideways, stale, insufficient-data and high-spread markets.
4. Produce deterministic canonical signals.
5. Allow only `ACTIVE` signals into Risk and Execution.
6. Size positions from fixed USDT risk and Stop Loss distance.
7. Confirm actual exchange fills and native protection.
8. Reconcile positions, orders, executions, fees and realized PnL from Bybit evidence.
9. Preserve one authoritative operator view across Dashboard, Active Trades, Journal and Performance.
10. Retain an auditable lifecycle across refresh and backend restart.

## Core architecture

```text
React + TypeScript Frontend
        |
        | Authenticated REST API
        v
FastAPI Backend
        |
        +-- Scanner / Strategy / Signal
        +-- Risk / Position Sizing / Execution
        +-- Trade Management
        +-- Journal and Authoritative Reconciliation
        +-- Bybit Private/Public WebSocket
        +-- Periodic Bybit REST truth refresh
        +-- Watchdog and Bot Controls
        |
        +-- PostgreSQL on Render
        +-- SQLite for local development
        v
Bybit V5 Demo APIs
```

---

## Locked trading and safety rules

### Signal rules

- Ranked universe: Top 30.
- Scalping: 5m context/setup + 1m trigger.
- Intraday: 1h trend + 15m setup + 5m trigger.
- Open/current candles are excluded from confirmed analysis.
- `SIDEWAYS`, `STALE` and `INSUFFICIENT_DATA` are blocked.
- `NEAR_SETUP` is monitor-only.
- Only `ACTIVE` may proceed to Risk and Execution.
- Same-symbol duplicate positions are blocked.

### Risk controls

| Rule | Locked value |
|---|---:|
| Maximum active trades | 5 |
| Maximum total margin exposure | 50% of account/day equity |
| Losing-symbol cooldown | 30 minutes |
| Daily reset timezone | Asia/Dhaka |
| Daily hard stop | 5% net realized loss for the BDT day |

When the daily hard stop is active, new execution must stop. Existing positions must continue to be protected and reconciled.

### Release controls

- Demo is the default and only approved runtime mode.
- Code/CI PASS is not runtime PASS.
- Runtime PASS is not live-capital approval.
- Feature branches and pull requests are mandatory.
- Do not merge to `main` without explicit Product Owner approval.

---

## Current deployed evidence

### Confirmed working

- Bybit Private WebSocket badge displays `CONNECTED`.
- Bybit Public WebSocket badge displays `CONNECTED`.
- Periodic REST reconciliation is merged and runs during WebSocket idle periods.
- Bybit Ledger Audit reads account transaction-log evidence.
- Deployed screenshots showed 29 ledger records and symbol-level wallet changes.
- Bybit reported zero open positions and the application also displayed zero active positions.
- Unknown financial values remain `N/A` instead of being fabricated as zero.

### Important limitation

The deployed Journal showed rows with:

- `Order ID: Unavailable`
- `PnL Sync Source: Unavailable`
- `Protection: Not recorded`
- `Close Reason: ORDER NOT ACCEPTED`
- realized PnL and fees as `N/A`

At the same time, Bybit transaction logs proved that real trades occurred. Therefore, exchange connectivity is working, but order/execution identity persistence and lifecycle reconciliation are not yet complete.

---

## Active P0 work

| Priority | Work item | Current status |
|---:|---|---|
| 1 | `JOURNAL-IDENTITY-001` — persist/backfill `orderId`, `orderLinkId`, `execId` and fill evidence | **Issue #51 OPEN / NOT FIXED** |
| 2 | Exact PnL attribution for overlapping same-symbol trades | **PR #48 READY / NOT MERGED** |
| 3 | Separate active, pending, stale and closed operator states | **PR #49 READY / NOT MERGED** |
| 4 | Expiring sessions, logout revocation and login throttling | **PR #50 READY / NOT MERGED** |
| 5 | Full TP/partial-close/Journal/restart lifecycle verification | **Issue #37 OPEN** |

### Issue #51 acceptance criteria

- Accepted order stores matching `orderId` and `orderLinkId`.
- Fill stores matching `execId`, quantity, price, fee, side, timestamp and position index.
- Missing identity is backfilled only from exact exchange evidence.
- `ORDER NOT ACCEPTED` is written only after an explicit Bybit rejection.
- Missing-identity rows remain `RECONCILIATION_PENDING` or `SYNC_INCOMPLETE`.
- Incomplete/rejected rows are excluded from closed-trade count, win/loss and strategy PnL.
- Identity and financial evidence survive refresh and restart.

---

## Required live verification

Use one fresh controlled Bybit Demo trade. Capture Bybit, Dashboard, Active Trades and Journal evidence at the same timestamps.

### Gate 1 — Order and fill identity

- Journal reservation is created.
- Bybit accepts the order.
- Journal stores the same `orderId` / `orderLinkId`.
- Fill stores the same `execId`, quantity, entry price and fee.

**Fail immediately if an accepted trade still shows `Order ID: Unavailable`.**

### Gate 2 — Native protection

- Stop Loss exists on Bybit.
- TP1, TP2 and final target exist with the correct quantities.
- Journal protection evidence is recorded.

### Gate 3 — TP1 partial close

- Approximately 50% closes.
- Remaining quantity is correct.
- Partial exit price, exact fee and realized PnL are persisted.
- Required break-even protection is visible on Bybit.
- Dashboard, Active Trades and Journal agree.

### Gate 4 — TP2 and final close

- Approximately 25% closes at TP2.
- Intraday trailing protection activates after TP2.
- Final 25% closes correctly.
- Exact exit, fees, realized PnL, close reason and close source persist.
- Performance and win/loss classification use only known outcomes.

### Gate 5 — Refresh and restart

- Repeated browser refresh does not duplicate or erase the trade.
- Render backend restart recovers the lifecycle exactly once.
- Closed rows do not reopen.
- Identity, fees, PnL and protection state remain intact.
- No orphan native orders remain.

### Gate 6 — Rejected execution

A controlled rejected order must:

- use `ORDER_REJECTED` or `EXECUTION_FAILED`;
- persist the exact Bybit rejection reason;
- remain outside completed-trade count, win/loss and realized PnL.

### Gate 7 — Loss controls

- A realized loss blocks the same symbol for 30 minutes.
- At 5% BDT-day net realized loss, new executions stop.
- The engine/UI exposes the exact hard-stop or cooldown reason.

---

## Next screenshot-based investigation

The supplied Bybit transaction logs show a loss cluster after an earlier profitable period. Do **not** tune strategy rules from Journal statistics until Issue #51 and the full close lifecycle are verified.

After data integrity is proven, investigate:

1. trade-by-trade net PnL sequence;
2. strategy and trade-type attribution;
3. whether symbol cooldown activated after each loss;
4. whether the 5% daily loss stop activated;
5. duplicate/re-entry timing;
6. fees versus gross trading outcome;
7. market regime and signal-quality changes around the loss cluster.

---

## Lower-priority engineering backlog

- Readiness endpoint must fail with HTTP 503 when critical dependencies are unavailable.
- Bybit history pagination and date-range guards.
- Decimal-based financial persistence instead of binary Float.
- Versioned Alembic migrations.
- Multi-worker protection against duplicate bot loops.
- Durable audit/outbox retry for external persistence.
- Dependency pinning and cleanup of unused frontend packages.
- Replace silent broad exception handling with auditable errors.
- ACTIVE-signal Risk/Execution decision visibility (`EXEC-QUEUE-001`).
- Historical backtesting only after runtime closure.

---

## Current verdict

```text
DEMO BETA
MAIN STABLE AT LAST MERGED FIX
P0 PRs READY BUT NOT MERGED
JOURNAL IDENTITY PERSISTENCE OPEN
FULL BYBIT DEMO LIFECYCLE VERIFICATION PENDING
LIVE-CAPITAL TRADING NOT APPROVED
```
