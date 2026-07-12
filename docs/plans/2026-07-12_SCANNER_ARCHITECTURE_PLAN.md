# DrayFrogd — Scanner Architecture Update Plan

**Date:** 2026-07-12  
**Day:** Sunday  
**Status:** PLANNED / LOCKED FOR IMPLEMENTATION  
**Repository:** `zahirulca24-bit/DrayFrogd`  
**Base branch:** `main`  
**Planning branch:** `docs/2026-07-12-scanner-plan`

---

## 1. Objective

Separate Scanner, Strategy Engine and Signal Engine responsibilities so that the bot first ranks suitable trending markets, then searches for approved strategy setups, then monitors only useful signal symbols for execution.

---

## 2. Locked End-to-End Flow

```text
Bybit USDT Perpetual Market
→ Liquidity / Turnover / Spread Filter
→ Trend Classification
→ Reject Sideways and Insufficient-Data Markets
→ Rank Uptrend and Downtrend Symbols
→ Select Top 30 Ranked Symbols
→ Strategy Engine Evaluates Approved Strategies
→ Near Setup / Active Signal
→ Signal Engine Stores and Ranks Useful Signals
→ Bot Monitors Signal Symbols Only
→ Active Signal + Risk Gate Passed
→ Trade Execution
```

---

## 3. Step 1 — Scanner Market Ranking, Trend Classification and Sideways Rejection

### Scanner responsibilities

The Scanner will only:

- collect Bybit USDT perpetual market candidates;
- validate liquidity, 24-hour turnover, price movement and spread;
- fetch sufficient closed 5-minute candles;
- classify each market as:
  - `UPTREND`
  - `DOWNTREND`
  - `SIDEWAYS`
  - `INSUFFICIENT_DATA`
- reject `SIDEWAYS` and `INSUFFICIENT_DATA` symbols;
- calculate trend-strength and market-quality scores;
- rank eligible uptrend/downtrend symbols;
- return the Top 30 ranked symbols.

### Direction enforcement

- `UPTREND` → Strategy Engine may search only Long setups.
- `DOWNTREND` → Strategy Engine may search only Short setups.
- `SIDEWAYS` → Must not enter Strategy Engine.
- `INSUFFICIENT_DATA` or stale candles → Must be rejected.

### Scanner exclusions

The Scanner must not:

- match trading strategies;
- produce entry, stop-loss or take-profit levels;
- create executable signals;
- place or manage orders.

### Step 1 acceptance criteria

- Exactly one deterministic trend status is returned per checked symbol.
- Sideways symbols never reach Strategy Engine evaluation.
- Ranked output contains no more than 30 symbols.
- Every ranked symbol contains market rank, direction, trend strength and quality score.
- Tests cover uptrend, downtrend, sideways, insufficient data, ranking and Top-30 limits.
- Existing execution behaviour remains unchanged.

---

## 4. Step 2 — Strategy and Signal Pipeline

This step starts only after Step 1 passes tests and review.

### Strategy Engine input

The Strategy Engine receives only the Scanner's Top 30 ranked symbols, including approved direction.

### Approved strategies

- EMA Pullback
- Breakout
- Pure SMC

### Strategy result states

- `NO_SETUP`
- `NEAR_SETUP`
- `ACTIVE`
- `INVALID`
- `EXPIRED`

### Candle contract

- 5-minute candles: minimum 250 closed candles.
- 1-minute candles: minimum 250 closed candles.
- Open/incomplete candles must not be used for confirmed entries.
- Breakout must have sufficient EMA200 data.

### Signal Engine responsibilities

Signal Engine will keep only useful strategy results:

- `NEAR_SETUP`
- `ACTIVE`

Behaviour:

- Near Setup → monitor the symbol; do not trade.
- Active Signal → send to Risk and Execution gates.
- Expired/Invalid → remove from executable monitoring.
- Multiple setups for one symbol → select one primary best-quality signal; retain other matches only as confirmation metadata.

### Ranking layers

1. **Market Ranking** — Scanner selects the most suitable markets.
2. **Signal Ranking** — Signal Engine ranks matched setups by quality, confidence, freshness and valid risk geometry.

---

## 5. Step 3 — Scanner and Signal UI Truthfulness

This step starts after backend contracts are stable.

### Scanner UI must show

- Symbols checked
- Uptrend count
- Downtrend count
- Sideways rejected count
- Insufficient-data count
- Ranked symbols: maximum 30
- Strategy checks: maximum 90 for three strategies
- Near setups
- Active signals

### Required label correction

`TOTAL 90` must not be presented as 90 symbols.

Correct presentation:

- `Symbols Ranked: 30`
- `Strategy Checks: 90`

### Signal card must show

- Market rank
- Trend direction
- Strategy
- Trade type
- Direction
- Entry
- Stop Loss
- TP1
- TP2
- Final TP
- Signal age
- Near / Active / Expired state
- Account-executable state separately from strategy-valid state

---

## 6. Locked Trade-Profile Rules

These rules are not implemented inside the Scanner task, but Scanner/Signal metadata must preserve the selected trade type.

| Rule | Scalping | Intraday |
|---|---:|---:|
| Maximum leverage | 20x | 10x |
| TP1 | 1.5R | 2R |
| TP2 | 2R | 2.5R |
| Final target | 2.5R | 3R |
| Trailing stop | Disabled | Enabled only after approved trigger |
| Maximum duration | 59 minutes | 6 hours |

Unknown trade type must not silently inherit a default management profile.

---

## 7. Deferred Critical Tasks

The following are confirmed problems but remain outside this bounded Scanner task:

- Journal restart reconciliation and actual exchange timestamps
- Entry fees, realized PnL and net daily PnL synchronization
- Strategy and trade-type persistence after restart
- Bot/manual/external trade classification
- Scalping 20x and Intraday 10x enforcement
- Scalping and Intraday TP ladder enforcement
- Failed or uncertain reservation cleanup
- Authentication expiry and server-side logout
- Frontend stale-data truthfulness
- Settings page completion

These items must be implemented as separate bounded tasks after Scanner, Strategy and Signal pipeline stabilization.

---

## 8. Responsibility Split

### Product Owner — User

- Approves business rules and bounded scope.
- Sends approved task prompt to Codex.
- Checks preview and screenshots.
- Approves commit, push and merge.

### Planner / Auditor / Reviewer — ChatGPT

- Maintains architecture and scope.
- Writes exact credit-efficient Codex prompts.
- Audits changed files, diff and tests.
- Returns `SAFE TO PUSH` or `CHANGES REQUIRED`.
- Does not merge to `main` without Product Owner approval.

### Implementer — Codex

- Creates an implementation branch.
- Changes code only within approved scope.
- Adds and runs tests.
- Reports changed files, diff summary and test evidence.
- Does not merge to `main` without explicit Product Owner approval.

---

## 9. Execution Order for 2026-07-12

1. Prepare Step 1 Codex implementation prompt.
2. Codex implements Scanner Market Ranking, Trend Classification and Sideways Rejection on a separate branch.
3. Run targeted and full available tests.
4. Review changed files and exact diff.
5. Correct any gaps before proceeding.
6. Start Step 2 only after Step 1 is accepted.
7. Start Step 3 only after backend contracts are stable.
8. Do not merge to `main` without explicit Product Owner approval.

---

## 10. Current Active Task

**SCANNER-ARCH-001 — Scanner Market Ranking, Trend Classification and Sideways Rejection**

No Journal, accounting, authentication, execution-profile or unrelated frontend implementation is included in this task.
