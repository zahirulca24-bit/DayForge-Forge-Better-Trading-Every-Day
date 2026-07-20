# DayForge Open Issues Checklist

**Updated:** 18 July 2026  
**Rule:** Code/CI is not live proof. Any issue without a complete merge is Pending. Any merged issue without runtime evidence remains Live Test Pending.

| Priority | Issue | Topic | Build | Merge | Live Test | Overall |
|---:|---|---|---|---|---|---|
| 1 | #51 | Journal and Bybit identity | Partial | Partial: PR #99 and #100 merged | Pending | Pending |
| 2 | #53 | Authoritative daily-loss control | Pending | Pending | Pending | Pending |
| 3 | #55 | Configuration authority | Pending | Pending | Pending | Pending |
| 4 | #56 | Persistent runtime storage | Pending | Pending | Pending | Pending |
| 5 | #37 | Complete Bybit Demo lifecycle proof | Partial | Pending | Pending | Pending |
| 6 | #63 | Intraday 2.0R profile target | Done: code and CI passed | Pending: PR #64 closed without merge | Pending | Pending |
| 7 | #59 | Backtest and strategy truth | Pending | Pending | Pending | Pending |
| 8 | #54 | Private WebSocket readiness | Pending | Pending | Pending | Pending |
| 9 | #57 | Performance truth | Partial | Pending | Pending | Pending |
| 10 | #65 | Trade-churn rule lock and safety gates | Done | Done: PR #93, #97 and #98 merged | Pending | Pending |
| 11 | #58 | Incident deduplication | Pending | Pending | Pending | Pending |

## Next actions

- **#51:** P0-1C partial-close fee and realized PnL evidence.
- **#53:** Start after #51 identity authority is sufficiently complete.
- **#55:** Audit all runtime configuration reads and UI/execution agreement.
- **#56:** Prove production database persistence across restart.
- **#37:** Run controlled Demo lifecycle test after dependencies are ready.
- **#63:** Reconcile current main and recreate a clean PR if still required.
- **#59:** Start after execution and financial data are trustworthy.
- **#54:** Define and test REST fallback readiness policy.
- **#57:** Complete after exact close and financial reconciliation.
- **#65:** Verify retained safety gates in deployed runtime.
- **#58:** Implement after higher-priority safety work.

## Execution order

`#51 -> #53 -> #55 -> #56 -> #37 -> #63 -> #59 -> #54 -> #57 -> #65 -> #58`

## Summary

- Overall complete: **0 / 11**
- Live-tested complete: **0 / 11**
- Fully merged, live test pending: **#65**
- Partially merged: **#51**
- Code complete but not merged: **#63**
