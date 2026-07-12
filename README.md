# DrayFrogd V2

Bybit-first automated trading terminal built with **FastAPI, React, PostgreSQL and Bybit V5 APIs**.

The project is currently in **Demo Beta / Engineering Verification**. Live-capital trading is not approved.

> **Last documentation update:** 12 July 2026, 11:30 PM BDT (`Asia/Dhaka`)  
> **Runtime evidence captured:** 12 July 2026, approximately 9:15 PM–9:21 PM BDT  
> **Current phase:** Runtime Verification and Trade Management Hardening  
> **Latest `main` commit:** `234c4733321974ecb898abb5bfa3aa64ca6ea2a9` — PR #30  
> **Latest verified CI:** run #227 — backend compile passed, backend tests **180/180**, frontend TypeScript passed, frontend production build passed  
> **Documentation PR:** PR #31 — branch `docs/readme-runtime-audit-2026-07-12`  
> **Live trading:** blocked by default

---

## 1. Progress Measurement Rules

Progress percentages in this README are **gate-based**, not subjective estimates.

- A code roadmap task reaches **100%** only when its approved scope is implemented, tested, merged and supported by recorded CI evidence.
- A runtime task reaches **100%** only when the deployed application and Bybit Demo evidence confirm the full lifecycle.
- A documentation task reaches **100%** only after content update, branch commit, PR, CI and approved merge are complete.
- A green CI run proves only tested code/build paths. It does not prove exchange fills, protection amendments, journal synchronization or real runtime safety.

---

## 2. Current Work Progress Ledger

### Completed engineering roadmap

| Work item | Completed gates | Progress | Evidence |
|---|---:|---:|---|
| Scanner Architecture and Profile Separation | 4/4 | **100%** | PR #27 merged; backend compile; **171/171** backend tests; frontend checks passed |
| Strategy and Signal Pipeline | 4/4 | **100%** | PR #28 merged; backend compile; **180/180** backend tests; frontend checks passed |
| Scanner and Signal UI Truthfulness | 4/4 | **100% implementation scope** | PR #30 merged; CI run #227; backend **180/180**; frontend checks passed |
| README Runtime Audit Update | 3/5 | **60% closure** | Content updated, branch committed and PR #31 opened; CI and merge remain pending |

### Runtime verification and repair program

| Work item | Verified gates | Progress | Current state |
|---|---:|---:|---|
| Scalping deployed lifecycle verification | 4/10 | **40%** | Entry, initial protection, TP1 partial close and TP2 partial close verified; remaining lifecycle failed/pending |
| TP2 → TP1-price SL profit-lock repair | 0/5 | **0%** | Critical defect confirmed; implementation not started |
| Partial-close journal, fees and realized-PnL synchronization | 0/6 | **0%** | Defect confirmed; implementation not started |
| Strategy/trade-profile metadata recovery | 0/5 | **0%** | `unknown`/missing metadata confirmed; implementation not started |
| TP-stage and risk-value frontend consistency | 0/5 | **0%** | UI mismatch confirmed; implementation not started |
| Blank-page reproduction and stability repair | 0/4 | **0%** | Symptom observed; root cause not confirmed |
| Complete Intraday lifecycle verification | 0/8 | **0%** | Not started |
| Restart, close-path and orphan-order verification | 0/6 | **0%** | Not started |

### Scalping lifecycle gate details

The current **4/10 = 40%** verification score is based on these explicit gates:

- [x] Exchange position opened.
- [x] Initial SL and final TP visible.
- [x] TP1 closed approximately 50%.
- [x] TP2 closed approximately 25%.
- [ ] TP2 moved remaining SL to TP1 price — **failed**.
- [ ] Remaining 25% remained correctly protected — **failed**.
- [ ] Partial-close journal lifecycle synchronized — **failed**.
- [ ] Fees and realized PnL synchronized — **failed**.
- [ ] Strategy/profile metadata remained authoritative — **failed**.
- [ ] Final close and order cleanup verified — **pending**.

---

## 3. Runtime Verification Checklist — 12 July 2026

This section records evidence observed from the deployed Render application and the connected Bybit Demo account. Checked items are evidence-confirmed. Unchecked items remain defects or pending verification.

### Evidence confirmed

- [x] Deployed frontend loaded and authenticated successfully.
- [x] Backend, admin authentication, exchange API keys, exchange connection and wallet synchronization showed ready.
- [x] One ZECUSDT demo position was visible in both DrayFrogd and Bybit.
- [x] ZECUSDT entry was approximately `530.04` with initial SL `527.54`.
- [x] The approved Scalping ladder was created:
  - TP1 approximately `533.79` — close about 50%.
  - TP2 approximately `535.04` — close about 25%.
  - Final TP `536.29` — close the remaining 25%.
- [x] Bybit transaction evidence showed an initial quantity of about `7.97`, a TP1 close of about `3.98`, a TP2 close of about `1.99`, and about `2.00` remaining.
- [x] Partial TP execution worked at the exchange.
- [x] Active position quantity, entry, mark price, exposure and floating PnL were broadly synchronized with the exchange snapshot.

### Confirmed runtime defects

- [ ] **CRITICAL — Scalping TP2 profit lock failed.** After TP2, the remaining position SL still showed the original loss stop `527.54`. The locked rule requires the remaining 25% SL to move to the TP1 price, approximately `533.79`.
- [ ] **TP-stage UI is incorrect.** The Active Trades page displayed final TP `536.29` as `TP1`; the actual TP1 and TP2 stages were not presented correctly.
- [ ] **Partial-close journal synchronization is incomplete.** The exchange showed partial closes and fees, while the journal still showed one open trade with no partial-close lifecycle evidence.
- [ ] **Realized PnL synchronization is incorrect.** The Dashboard showed `Today's Realized = 0.00` even though Bybit showed realized cash flow from the ZECUSDT partial closes.
- [ ] **Fees are missing from the journal.** The exchange recorded fees, but the trade record showed `N/A`.
- [ ] **Trade metadata was not authoritative after recovery/adoption.** Strategy was `unknown`; trade type, management profile and signal timestamp were missing or unavailable.
- [ ] **Risk settings are inconsistent across pages.** Dashboard showed `1.00%` risk per trade while Control Center showed `1.90%`.
- [ ] **Daily trade limit/status presentation is inconsistent.** Dashboard showed `8`, while Control Center showed `1/0` and a configured maximum of `0`.
- [ ] **Intermittent blank page was observed.** Root cause is not yet confirmed; routing, loading and runtime error handling require evidence-based reproduction.
- [ ] **Final close and native-order cleanup remain unverified.** Remaining TP, SL close, manual close, orphan-order cleanup and journal finalization require proof.
- [ ] **Intraday profile lifecycle remains unverified.** TP1 break-even, TP2 trailing activation, runner management and six-hour maximum duration need complete Bybit Demo evidence.

### Runtime verdict

The deployed system proved that Scanner/Signal output can reach exchange execution and that native partial TP orders can fill. It did **not** prove a safe complete lifecycle.

**Current safety classification:** Demo Beta — runtime defects confirmed — live trading not approved.

No live-capital approval may be given until the TP2 protection defect, authoritative journal/PnL reconciliation and both profile lifecycles are fixed and re-verified.

---

## 4. Sequential Repair Plan and Ownership

Work must remain sequential and evidence-driven. One bounded repair task must be completed before the next begins.

| Step | Task | Primary worker | Product Owner role | Start state |
|---|---|---|---|---|
| 0 | Close README PR #31 | Repository worker | Review and approve merge | In progress |
| 1 | Fix Scalping TP2 → TP1-price SL profit lock | Repository worker | Approve scope and review evidence | Not started |
| 2 | Fix partial-fill reconciliation, fees and realized PnL | Repository worker | Review deployed evidence | Not started |
| 3 | Recover authoritative strategy/profile metadata | Repository worker | Review recovery result | Not started |
| 4 | Correct TP labels and risk/daily-trade UI values | Repository worker | Screenshot review | Not started |
| 5 | Reproduce and fix blank-page failure | Repository worker | Confirm reproduction is resolved | Not started |
| 6 | Run complete Scalping Demo re-verification | Render + Bybit Demo + repository worker | Provide/approve runtime evidence | Not started |
| 7 | Run complete Intraday Demo verification | Render + Bybit Demo + repository worker | Provide/approve runtime evidence | Not started |
| 8 | Verify restart, close cleanup and orphan orders | Repository worker + Bybit Demo | Review final evidence | Not started |

Every implementation step requires:

1. Exact changed files and diff review.
2. Focused tests for the bounded defect.
3. Full available backend test suite.
4. Frontend TypeScript and production build when frontend is affected.
5. CI success.
6. Product Owner approval before merge.
7. Deployed Bybit Demo evidence when runtime behavior is affected.

---

## 5. Completed Scanner and Signal Roadmap

### [x] Step 1 — Scanner Architecture and Profile Separation

**Merged evidence:** PR #27, merge commit `1e2d31690616553cf1c93d669d132188d783a9c8`.

Implemented:

- Dynamic Bybit USDT perpetual candidate collection.
- Liquidity, turnover, movement and spread validation.
- Dynamic ranked universe capped at **Top 30**.
- Separate profile pipelines:
  - **Scalping:** 5-minute trend/setup + 1-minute trigger.
  - **Intraday:** 1-hour trend + 15-minute setup + 5-minute trigger.
- Open/current candles excluded from confirmed analysis.
- `SIDEWAYS`, `INSUFFICIENT_DATA` and stale profile data blocked before strategy evaluation.
- Explicit `market_rank` 1–30.
- Explicit `trade_type`; missing or unknown profile is blocked and never defaults to Scalping.
- Manual `/scanner/run` remains scan-only.

### [x] Step 2 — Strategy and Signal Pipeline

**Merged evidence:** PR #28, merge commit `c216a9af96e87a3d466ca0f1a70e3c4825650444`.

Implemented:

- Canonical result states: `NO_SETUP`, `NEAR_SETUP`, `ACTIVE`, `INVALID`, `EXPIRED`.
- `NEAR_SETUP` remains monitor-only.
- Only `ACTIVE` can continue to Risk and Execution gates.
- Trade geometry is validated before a result becomes useful.
- Opposite-trend and missing-trade-type results are rejected.
- One deterministic primary useful signal per symbol.
- Same-direction matches remain confirmation metadata.
- Signal ranking uses state, quality score, market rank and freshness.

### [x] Step 3 — Scanner and Signal UI Truthfulness

**Merged evidence:** PR #30, merge commit `234c4733321974ecb898abb5bfa3aa64ca6ea2a9`.

Implemented scope:

- Canonical signal states replace fabricated Ready/Executable/Blocked presentation.
- One ranked market row per symbol.
- Market rank and signal rank remain separate.
- Market score and signal score remain separate.
- Strategy, Risk and Execution states remain separate.
- Entry, SL, TP, RR, trend, profile, timeframes and signal age come from the canonical contract.
- Per-signal Auto Trade and Demo Execute controls were removed.
- Manual Run Scan remains scan-only.
- Dashboard Latest Signals shows canonical primary `ACTIVE` signals only.

Runtime defects discovered after this implementation are tracked separately in Sections 2–4 and do not erase the completed bounded PR #30 scope.

---

## 6. Locked End-to-End Flow

```text
Bybit USDT Perpetual Market
→ Liquidity / Turnover / Movement / Spread Filter
→ Closed-Candle Profile-Specific Analysis
→ Trend Classification
→ Reject Sideways / Stale / Insufficient Markets
→ Rank Eligible Markets (Top 30)
→ Strategy Engine Evaluates Approved Strategies
→ Canonical Signal State
→ Signal Engine Deduplicates and Ranks Useful Signals
→ Bot Monitors Useful Signal Symbols
→ ACTIVE Signal + Risk Gate Passed
→ Trade Execution
→ Trade-Type-Specific Management Profile
→ Exchange and Journal Reconciliation
→ Exact Fees and Realized PnL
```

Responsibility boundaries:

- **Scanner:** market filtering, profile eligibility, trend classification and market ranking.
- **Strategy Engine:** setup detection and trade geometry proposals.
- **Signal Engine:** canonical states, useful-result retention, deduplication and signal ranking.
- **Risk Engine:** final risk authority.
- **Position Sizing:** fixed-risk quantity and exchange-constraint authority.
- **Execution Engine:** final exchange-order authority.
- **Trade Management:** profile-specific protection, TP stages, break-even, trailing and close lifecycle.
- **Journal/Reconciliation:** authoritative lifecycle, fees, PnL and restart recovery evidence.

---

## 7. Locked Risk and Trade Profiles

Scalping and Intraday must never share one generic management profile.

| Rule | Scalping | Intraday |
|---|---:|---:|
| Fixed risk per trade | 20 USDT | 50 USDT |
| Maximum leverage | 20x | 10x |
| Minimum Risk:Reward | 1:1.5 | 1:2.0 |
| TP1 | 1.5R — close 50% | 2R — close 50% |
| TP2 | 2R — close 25% | 2.5R — close 25% |
| Final target / Runner | 2.5R — final 25% | 3R — final 25% runner |
| Early protection | At 1R move SL to break-even plus observed fee buffer | At TP1 move SL to break-even |
| After TP2 | Move remaining SL to TP1 price | Activate trailing protection |
| Trailing stop | Disabled | Enabled only after TP2 |
| Maximum duration | 59 minutes | 6 hours |

Mandatory authoritative fields:

- `trade_type`
- `strategy_name`
- `management_profile`
- selected leverage
- TP1, TP2 and final/runner targets
- TP allocation percentages
- break-even/profit-lock rule
- trailing state
- maximum holding time

An unknown or missing `trade_type` must not silently inherit a management profile.

Portfolio controls:

- Maximum **5 active trades**.
- Same-symbol duplicate positions are blocked.
- Total combined margin exposure cannot exceed **50% of account/day equity**.
- A realized losing close creates a **30-minute symbol cooldown**.
- Daily reset timezone is **Asia/Dhaka**.
- At **5% net realized daily loss**, new execution stops for that BDT day.
- Existing positions continue to be protected and reconciled.

---

## 8. Project Milestone Status

| # | Milestone | Status | Current evidence / remaining gap |
|---|---|---|---|
| 1 | Repository foundation and CI | ✅ Complete | FastAPI, React, backend compile/tests, TypeScript and frontend build |
| 2 | Authentication and bot controls | 🟡 Partial | Login and controls exist; session expiry, logout and public operational endpoint hardening remain |
| 3 | Database persistence and restart safety | 🟡 Partial | PostgreSQL/SQLite persistence exists; recovered trade metadata is not authoritative |
| 4 | Bybit exchange integration | ✅ Complete in code | Wallet, positions, market data, orders, leverage, protection and close APIs |
| 5 | Market Scanner | ✅ Complete | Top-30 ranking and separate profile pipelines merged through PR #27 |
| 6 | Strategy and Signal Engine | ✅ Complete | Canonical pipeline and primary signal ranking merged through PR #28 |
| 7 | Risk Engine Authority | 🟡 Partial | Core gates exist; frontend values need one authoritative contract |
| 8 | Position sizing and exposure | ✅ Complete in code | SL-distance sizing, exchange constraints and portfolio exposure controls |
| 9 | Trade Execution Engine | ✅ Complete in code | Reservation, idempotency, fill confirmation and protection verification |
| 10 | Trade Management Engine | 🔴 Runtime defect | Partial TP fills worked; Scalping TP2 profit-lock failed |
| 11 | Journal and exact PnL sync | 🔴 Runtime defect | Partial closes, fees and realized PnL did not reconcile |
| 12 | Frontend operations terminal | 🟡 Partial | UI roadmap merged; TP labels, settings consistency and blank-page stability remain |
| 13 | Deployment and observability | 🟡 Partial | Render and Watchdog exist; lifecycle verification remains incomplete |
| 14 | Full Bybit Demo E2E and soak testing | ⬜ Pending | Complete Scalping and Intraday evidence required |
| 15 | Live-release hardening | ⬜ Pending | Security, backups, monitoring and approved demo evidence required |

---

## 9. Architecture

```text
React + TypeScript Frontend
        |
        | Authenticated REST API
        v
FastAPI Backend
        |
        +-- Scanner
        +-- Strategy Engine
        +-- Signal Engine
        +-- Risk Engine
        +-- Position Sizing
        +-- Execution Service
        +-- Trade Management
        +-- Journal and Reconciliation
        +-- Watchdog and Bot Controls
        |
        +-- PostgreSQL (deployment)
        +-- SQLite (local development)
        |
        v
Bybit V5 Demo / Live APIs
```

| Layer | Technology |
|---|---|
| Backend | Python 3.12, FastAPI, SQLAlchemy |
| Frontend | React, TypeScript, Vite |
| Exchange | Bybit V5 REST APIs |
| Production database | PostgreSQL |
| Local database | SQLite |
| Hosting | Render |
| CI | GitHub Actions |

---

## 10. Enabled Strategies

Current registered strategies:

1. **EMA Pullback**
2. **Breakout**
3. **Pure SMC**

Completed controls:

- Canonical five-state result contract.
- Direction enforcement.
- Useful-signal retention and deduplication.
- One primary useful signal per symbol.
- Deterministic signal ranking.

Still required:

- Strategy version and enable/disable control.
- Historical backtesting and walk-forward validation.
- Failure analysis and controlled tuning workflow.
- Deployed evidence linking each executed trade to an authoritative strategy/profile.

---

## 11. Testing and Release Evidence

Automated checks:

- Backend compile.
- Backend unit/integration suite.
- Frontend TypeScript check.
- Frontend production build.

Required runtime evidence:

- Deployed health/readiness.
- Bybit Demo order and position evidence.
- TP1/TP2/final protection transitions.
- Journal, fees and realized-PnL evidence.
- Restart and recovery evidence.
- Close-path and order-cleanup evidence.
- Complete Scalping and Intraday lifecycles.

---

## 12. Local Development

Backend:

```powershell
py -3 -m pip install -r requirements.txt
py -3 -m app.database_bootstrap
py -3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Frontend:

```powershell
cd frontend
npm install
npm run dev
```

Local database:

```text
sqlite:///./app.db
```

Keep `APP_ENV=development` when using SQLite.

---

## 13. Required Environment Variables

Backend:

- `APP_ENV`
- `DATABASE_URL`
- `FRONTEND_URL`
- `ADMIN_USERNAME`
- `ADMIN_PASSWORD_HASH`
- `SESSION_SECRET`
- `BYBIT_DEMO_API_KEY`
- `BYBIT_DEMO_API_SECRET`
- `BYBIT_LIVE_API_KEY`
- `BYBIT_LIVE_API_SECRET`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

Frontend:

- `VITE_API_BASE_URL`

Never commit API keys, passwords, session secrets, service-role credentials or `.env` files.

---

## 14. Safety and Release Rules

- Default mode is `demo`.
- Live mode is not production-approved.
- Scalping and Intraday management rules must remain separate.
- Unknown trade type must not receive a silent default management profile.
- Code completion is not runtime verification.
- Runtime verification is not live-capital approval.
- Do not describe a test as passed without evidence.
- Do not claim a deployment without deployment evidence.
- Use feature branches and pull requests for production changes.
- Do not merge to `main` without explicit Product Owner approval.
- Do not enable live trading before demo E2E, soak testing, operations review and release approval.

---

## 15. Current Verdict

DrayFrogd has a substantial demo-trading application, a completed Scanner/Signal roadmap and core safety architecture.

The 12 July 2026 deployed verification proved exchange entry and native partial TP fills, but it also confirmed a critical Scalping TP2 protection failure and incomplete journal/PnL reconciliation.

**Current classification:** Demo Beta — runtime repair required — live trading not approved.
