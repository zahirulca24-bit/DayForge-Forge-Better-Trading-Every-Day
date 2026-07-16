from __future__ import annotations

from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    target = Path(path)
    text = target.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"Expected anchor not found in {path}: {old[:140]!r}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> None:
    replace_once(
        "app/config.py",
        '    execution_risk_headroom_ratio: float = float(os.getenv("EXECUTION_RISK_HEADROOM_RATIO", "0.90"))\n',
        '    execution_risk_headroom_ratio: float = float(os.getenv("EXECUTION_RISK_HEADROOM_RATIO", "0.90"))\n'
        '    risk_approval_ttl_seconds: int = int(os.getenv("RISK_APPROVAL_TTL_SECONDS", "20"))\n'
        '    risk_signal_max_age_seconds: int = int(os.getenv("RISK_SIGNAL_MAX_AGE_SECONDS", "120"))\n',
    )

    replace_once(
        "app/authoritative_risk_engine.py",
        '''def issue_execution_approval(\n    client: Any,\n    signal: dict[str, Any],\n    *,\n    auto_triggered: bool = False,\n    now: datetime | None = None,\n) -> dict[str, Any]:\n''',
        '''def issue_execution_approval(\n    client: Any,\n    signal: dict[str, Any],\n    *,\n    auto_triggered: bool = False,\n    now: datetime | None = None,\n    wallet: dict[str, Any] | None = None,\n    positions: list[dict[str, Any]] | None = None,\n    account_equity: float | None = None,\n    identity_signal: dict[str, Any] | None = None,\n    validation: dict[str, Any] | None = None,\n    risk_state: dict[str, Any] | None = None,\n) -> dict[str, Any]:\n''',
    )
    replace_once(
        "app/authoritative_risk_engine.py",
        '''    mode = get_execution_mode()\n    execution_key = _build_execution_key(normalized, mode)\n    existing = get_trade_by_execution_key(execution_key)\n''',
        '''    mode = get_execution_mode()\n    identity = _normalize_signal(identity_signal or signal)\n    if identity is None:\n        return _reject("INVALID_SIGNAL_IDENTITY", "Execution signal identity is invalid")\n    execution_key = _build_execution_key(identity, mode)\n    existing = get_trade_by_execution_key(execution_key)\n''',
    )
    replace_once(
        "app/authoritative_risk_engine.py",
        '''    ok_positions, positions, positions_error = client.safe_fetch_positions()\n    if not ok_positions:\n        return _reject("POSITION_STATE_UNAVAILABLE", positions_error or "Position data unavailable")\n    if _has_open_symbol(positions, normalized["symbol"]):\n        return _reject("SYMBOL_ALREADY_ACTIVE", f"{normalized['symbol']} already has an exchange position")\n\n    ok_wallet, wallet, wallet_error = client.safe_fetch_wallet_balance()\n    if not ok_wallet or wallet is None:\n        return _reject("WALLET_STATE_UNAVAILABLE", wallet_error or "Wallet balance unavailable")\n    account_equity = extract_account_equity(wallet)\n    if account_equity is None:\n        return _reject("EQUITY_UNAVAILABLE", "Fresh account equity is unavailable")\n\n    risk_state = refresh_risk_state(account_equity=account_equity, now=current)\n    validation = validate_trade(normalized, account_equity=account_equity)\n    if not validation.get("allowed"):\n''',
        '''    resolved_positions = positions\n    if resolved_positions is None:\n        ok_positions, resolved_positions, positions_error = client.safe_fetch_positions()\n        if not ok_positions:\n            return _reject("POSITION_STATE_UNAVAILABLE", positions_error or "Position data unavailable")\n    if _has_open_symbol(resolved_positions, normalized["symbol"]):\n        return _reject("SYMBOL_ALREADY_ACTIVE", f"{normalized['symbol']} already has an exchange position")\n\n    resolved_wallet = wallet\n    if resolved_wallet is None:\n        ok_wallet, resolved_wallet, wallet_error = client.safe_fetch_wallet_balance()\n        if not ok_wallet or resolved_wallet is None:\n            return _reject("WALLET_STATE_UNAVAILABLE", wallet_error or "Wallet balance unavailable")\n    resolved_equity = account_equity if account_equity is not None else extract_account_equity(resolved_wallet)\n    if resolved_equity is None:\n        return _reject("EQUITY_UNAVAILABLE", "Fresh account equity is unavailable")\n\n    resolved_risk_state = risk_state or refresh_risk_state(account_equity=resolved_equity, now=current)\n    resolved_validation = validation or validate_trade(normalized, account_equity=resolved_equity)\n    if not resolved_validation.get("allowed"):\n''',
    )
    replace_once(
        "app/authoritative_risk_engine.py",
        '''            str(validation.get("reason") or "Risk validation failed"),\n            risk_state=risk_state,\n        )\n\n    economics = calculate_cost_adjusted_geometry(\n''',
        '''            str(resolved_validation.get("reason") or "Risk validation failed"),\n            risk_state=resolved_risk_state,\n        )\n\n    economics = calculate_cost_adjusted_geometry(\n''',
    )
    replace_once(
        "app/authoritative_risk_engine.py",
        '''    minimum_net_rr = float(validation.get("min_risk_reward") or 0.0)\n''',
        '''    minimum_net_rr = float(resolved_validation.get("min_risk_reward") or 0.0)\n''',
    )
    replace_once(
        "app/authoritative_risk_engine.py",
        '''        "risk_amount": float(validation.get("risk_amount") or 0.0),\n        "risk_per_trade": float(validation.get("risk_per_trade") or 0.0),\n        "leverage_cap": float(validation.get("leverage_cap") or 0.0),\n        "exposure_cap": float(validation.get("exposure_cap") or 0.0),\n''',
        '''        "risk_amount": float(resolved_validation.get("risk_amount") or 0.0),\n        "risk_per_trade": float(resolved_validation.get("risk_per_trade") or 0.0),\n        "leverage_cap": float(resolved_validation.get("leverage_cap") or 0.0),\n        "exposure_cap": float(resolved_validation.get("exposure_cap") or 0.0),\n''',
    )
    replace_once(
        "app/authoritative_risk_engine.py",
        '''        "account_equity": account_equity,\n''',
        '''        "account_equity": resolved_equity,\n''',
    )
    replace_once(
        "app/authoritative_risk_engine.py",
        '''        "decision": decision,\n    }\n''',
        '''        "decision": decision,\n        "validation": resolved_validation,\n        "risk_state": resolved_risk_state,\n        "economics": economics,\n    }\n''',
    )
    replace_once(
        "app/authoritative_risk_engine.py",
        '''    detected_at = _parse_time(normalized.get("detected_at"))\n''',
        '''    if normalized.get("auto_triggered") and not normalized.get("detected_at"):\n        return _reject("SIGNAL_TIMESTAMP_REQUIRED", "Automatic execution requires a detected_at timestamp")\n    detected_at = _parse_time(normalized.get("detected_at"))\n''',
    )
    replace_once(
        "app/authoritative_risk_engine.py",
        '''        "primary_signal": signal.get("primary_signal") if "primary_signal" in signal else None,\n    }\n''',
        '''        "primary_signal": signal.get("primary_signal") if "primary_signal" in signal else None,\n        "auto_triggered": bool(signal.get("auto_triggered")),\n    }\n''',
    )
    replace_once(
        "app/authoritative_risk_engine.py",
        '''def _approval_secret() -> bytes | None:\n    value = str(settings.session_secret or "").strip()\n    if not value:\n        return None\n''',
        '''def _approval_secret() -> bytes | None:\n    value = str(settings.session_secret or "").strip()\n    if not value:\n        if str(settings.app_env or "").lower() == "production":\n            return None\n        value = "dayfrogd-development-risk-approval"\n''',
    )

    replace_once(
        "app/execution_service.py",
        'from app.bot_controls import can_execute, get_execution_mode\n',
        'from app.authoritative_risk_engine import issue_execution_approval, verify_risk_approval\n'
        'from app.bot_controls import can_execute, get_execution_mode\n',
    )
    replace_once(
        "app/execution_service.py",
        '''    execution_signal["risk_reward"] = quote_geometry["risk_reward"]\n    refresh_risk_state(account_equity=account_equity)\n    validation = validate_trade(execution_signal, account_equity=account_equity)\n    if not validation.get("allowed"):\n        return {\n            "ok": False,\n            "error": validation.get("reason", "Risk validation failed"),\n            "pre_order_quote": quote,\n        }\n\n    sizing = calculate_position_size(\n''',
        '''    execution_signal["risk_reward"] = quote_geometry["risk_reward"]\n    risk_state = refresh_risk_state(account_equity=account_equity)\n    validation = validate_trade(execution_signal, account_equity=account_equity)\n    if not validation.get("allowed"):\n        return {\n            "ok": False,\n            "error": validation.get("reason", "Risk validation failed"),\n            "pre_order_quote": quote,\n        }\n\n    approval = issue_execution_approval(\n        client,\n        {**execution_signal, "auto_triggered": auto_triggered},\n        auto_triggered=auto_triggered,\n        wallet=wallet,\n        positions=positions,\n        account_equity=account_equity,\n        identity_signal=original_signal,\n        validation=validation,\n        risk_state=risk_state,\n    )\n    if not approval.get("allowed"):\n        return {\n            "ok": False,\n            "error": approval.get("error") or "RISK_APPROVAL_REJECTED",\n            "detail": approval.get("reason"),\n            "risk_approval": approval,\n            "pre_order_quote": quote,\n        }\n\n    sizing = calculate_position_size(\n''',
    )
    replace_once(
        "app/execution_service.py",
        '''    execution_mode = get_execution_mode()\n    execution_key = _build_execution_key(original_signal, execution_mode)\n''',
        '''    execution_mode = get_execution_mode()\n    approval_decision = dict(approval.get("decision") or {})\n    execution_key = str(approval_decision.get("execution_key") or _build_execution_key(original_signal, execution_mode))\n''',
    )
    replace_once(
        "app/execution_service.py",
        '''            "selected_leverage": selected_leverage,\n        },\n    }\n\n    try:\n        reservation = reserve_execution_capacity(\n''',
        '''            "selected_leverage": selected_leverage,\n            "risk_approval": approval_decision,\n        },\n    }\n\n    consumed = verify_risk_approval(\n        str(approval.get("token") or ""),\n        {**execution_signal, "auto_triggered": auto_triggered},\n        execution_mode=execution_mode,\n        consume=True,\n    )\n    if not consumed.get("allowed"):\n        return {\n            "ok": False,\n            "error": consumed.get("error") or "RISK_APPROVAL_REJECTED",\n            "detail": consumed.get("reason"),\n            "risk_approval": consumed,\n            "sizing": sizing,\n        }\n\n    try:\n        reservation = reserve_execution_capacity(\n''',
    )
    replace_once(
        "app/execution_service.py",
        '''            "status": "closed",\n            "result": "execution_failed",\n            "close_reason": error,\n            "closed_at": closed_at,\n            "exchange_metadata": {**metadata, "execution_error": detail},\n''',
        '''            "status": "execution_failed",\n            "result": "execution_failed",\n            "close_reason": error,\n            "closed_at": None,\n            "exchange_metadata": {**metadata, "execution_error": detail, "failed_at": closed_at},\n''',
    )

    replace_once(
        "app/risk.py",
        'from app.trade_state import CAPACITY_BLOCKING_STATUSES\n',
        'from app.trade_state import CAPACITY_BLOCKING_STATUSES, is_capacity_blocking_status\n',
    )
    replace_once(
        "app/risk.py",
        '''            active_rows = [item for item in journal_rows if str(item.status or "").lower() != "closed"]\n''',
        '''            active_rows = [item for item in journal_rows if is_capacity_blocking_status(item.status)]\n''',
    )
    replace_once(
        "app/risk.py",
        '''                "risk_model": "dynamic_fixed_usdt",\n''',
        '''                "risk_model": "dynamic_fixed_usdt",\n                "risk_policy_authority": "authoritative_risk_engine_v1",\n''',
    )
    replace_once(
        "app/risk.py",
        '''def get_risk_state() -> dict[str, Any]:\n    return refresh_risk_state()\n''',
        '''def get_risk_state(account_equity: float | None = None) -> dict[str, Any]:\n    return refresh_risk_state(account_equity=account_equity)\n''',
    )

    replace_once(
        "app/main.py",
        'from app.risk import get_risk_state, validate_trade\n',
        'from app.risk import extract_account_equity, get_risk_state, validate_trade\n',
    )
    replace_once(
        "app/main.py",
        '''@app.post("/risk/validate")\ndef risk_validate(payload: RiskSignalRequest, _: dict = Depends(require_authenticated)) -> dict:\n    return validate_trade(payload.model_dump())\n\n\n@app.get("/risk/state")\ndef risk_state(_: dict = Depends(require_authenticated)) -> dict:\n    return get_risk_state()\n''',
        '''@app.post("/risk/validate")\ndef risk_validate(payload: RiskSignalRequest, _: dict = Depends(require_authenticated)) -> dict:\n    client = get_exchange_client(get_execution_mode())\n    wallet_ok, wallet, wallet_error = client.safe_fetch_wallet_balance()\n    if not wallet_ok or wallet is None:\n        return {"allowed": False, "reason": wallet_error or "Wallet balance unavailable"}\n    return validate_trade(payload.model_dump(), account_equity=extract_account_equity(wallet))\n\n\n@app.get("/risk/state")\ndef risk_state(_: dict = Depends(require_authenticated)) -> dict:\n    client = get_exchange_client(get_execution_mode())\n    wallet_ok, wallet, _ = client.safe_fetch_wallet_balance()\n    equity = extract_account_equity(wallet) if wallet_ok else None\n    return get_risk_state(account_equity=equity)\n''',
    )

    replace_once(
        "app/metrics.py",
        '''    total_trades = len(active_trades) + len(closed_trades)\n''',
        '''    active_trade_count = _exchange_active_count(client)\n    if active_trade_count is None:\n        active_trade_count = len(active_trades)\n    total_trades = active_trade_count + len(closed_trades)\n''',
    )
    replace_once(
        "app/metrics.py",
        '''        "active_trades_count": len(active_trades),\n''',
        '''        "active_trades_count": active_trade_count,\n''',
    )
    replace_once(
        "app/metrics.py",
        '''def _daily_financial_truth(\n''',
        '''def _exchange_active_count(client: Any | None) -> int | None:\n    if client is None:\n        return None\n    try:\n        ok, positions, _ = client.safe_fetch_positions()\n    except Exception:\n        return None\n    if not ok:\n        return None\n    count = 0\n    for position in positions or []:\n        try:\n            size = float(position.get("size") or 0.0)\n        except (TypeError, ValueError):\n            continue\n        if isfinite(size) and size > 0:\n            count += 1\n    return count\n\n\ndef _daily_financial_truth(\n''',
    )

    replace_once(
        "frontend/src/types.ts",
        '''export interface RiskStateResponse {\n  risk_per_trade: number;\n''',
        '''export interface RiskStateResponse {\n  risk_policy_authority?: string;\n  risk_profiles?: Record<"scalping" | "intraday", {\n    risk_amount: number;\n    leverage_cap: number;\n    min_risk_reward: number;\n  }>;\n  risk_per_trade: number;\n''',
    )

    replace_once(
        "frontend/src/App.tsx",
        '''const emptyRiskState: RiskStateResponse = {\n  risk_per_trade: 0.01,\n''',
        '''const emptyRiskState: RiskStateResponse = {\n  risk_policy_authority: "authoritative_risk_engine_v1",\n  risk_profiles: {\n    scalping: { risk_amount: 20, leverage_cap: 20, min_risk_reward: 1.5 },\n    intraday: { risk_amount: 50, leverage_cap: 10, min_risk_reward: 2 },\n  },\n  risk_per_trade: 0.01,\n''',
    )
    replace_once(
        "frontend/src/App.tsx",
        '''            metrics={metrics}\n            activeTrades={activeTrades}\n''',
        '''            metrics={metrics}\n            riskState={riskState}\n            activeTrades={activeTrades}\n''',
    )
    replace_once(
        "frontend/src/App.tsx",
        '''            onRiskSettingsChange={(settings) => authToken ? runAction("bot-config-risk", () => api.updateBotConfig(authToken, settings)) : Promise.resolve()}\n''',
        '''''',
    )

    replace_once(
        "frontend/src/components/DashboardView.tsx",
        '''  MetricsResponse,\n  SystemReadiness,\n''',
        '''  MetricsResponse,\n  RiskStateResponse,\n  SystemReadiness,\n''',
    )
    replace_once(
        "frontend/src/components/DashboardView.tsx",
        '''  metrics: MetricsResponse;\n  activeTrades: Trade[];\n''',
        '''  metrics: MetricsResponse;\n  riskState: RiskStateResponse;\n  activeTrades: Trade[];\n''',
    )
    replace_once(
        "frontend/src/components/DashboardView.tsx",
        '''  metrics,\n  activeTrades,\n''',
        '''  metrics,\n  riskState,\n  activeTrades,\n''',
    )
    replace_once(
        "frontend/src/components/DashboardView.tsx",
        '''              <LimitCard label="Risk / trade" value={`${(numberValue(botStatus.risk_per_trade || 0.01) * 100).toFixed(2)}%`} />\n              <LimitCard label="Leverage cap" value={`${numberValue(botStatus.leverage_cap || 5).toFixed(0)}x`} />\n              <LimitCard label="Max open" value={String(botStatus.max_open_trades || 3)} />\n              <LimitCard label="Daily trades" value={String(botStatus.max_daily_trades || 8)} />\n''',
        '''              <LimitCard label="Risk budgets" value={`$${riskState.risk_profiles?.scalping.risk_amount ?? 20} / $${riskState.risk_profiles?.intraday.risk_amount ?? 50}`} />\n              <LimitCard label="Leverage caps" value={`${riskState.risk_profiles?.scalping.leverage_cap ?? 20}x / ${riskState.risk_profiles?.intraday.leverage_cap ?? 10}x`} />\n              <LimitCard label="Max open" value={String(riskState.max_open_trades)} />\n              <LimitCard label="Daily trades" value={`${riskState.trades_today} / ${riskState.max_trades_per_day}`} />\n''',
    )

    replace_once(
        "frontend/src/components/ControlPanel.tsx",
        'import { useEffect, useMemo, useState, type ReactNode } from "react";\n',
        'import { useMemo, type ReactNode } from "react";\n',
    )
    replace_once(
        "frontend/src/components/ControlPanel.tsx",
        '''  onRiskSettingsChange: (settings: {\n    risk_per_trade?: number;\n    leverage_cap?: number;\n    exposure_cap?: number;\n    max_open_trades?: number;\n    max_daily_trades?: number;\n  }) => Promise<void>;\n''',
        '''''',
    )
    replace_once(
        "frontend/src/components/ControlPanel.tsx",
        '''  onRefresh,\n  onRiskSettingsChange,\n}: ControlPanelProps) {\n  const [riskForm, setRiskForm] = useState({\n    riskPercent: String((riskState.risk_per_trade * 100).toFixed(2)),\n    leverageCap: String(riskState.leverage_cap),\n    exposureCap: String((riskState.exposure_cap * 100).toFixed(0)),\n    maxOpenTrades: String(riskState.max_open_trades),\n    maxDailyTrades: String(riskState.max_trades_per_day),\n  });\n  const [riskFormError, setRiskFormError] = useState<string | null>(null);\n\n  useEffect(() => {\n    setRiskForm({\n      riskPercent: String((riskState.risk_per_trade * 100).toFixed(2)),\n      leverageCap: String(riskState.leverage_cap),\n      exposureCap: String((riskState.exposure_cap * 100).toFixed(0)),\n      maxOpenTrades: String(riskState.max_open_trades),\n      maxDailyTrades: String(riskState.max_trades_per_day),\n    });\n  }, [riskState]);\n''',
        '''  onRefresh,\n}: ControlPanelProps) {\n''',
    )
    replace_once(
        "frontend/src/components/ControlPanel.tsx",
        '''  const saveRiskSettings = async () => {\n    const parsed = {\n      riskPercent: Number(riskForm.riskPercent),\n      leverageCap: Number(riskForm.leverageCap),\n      exposureCap: Number(riskForm.exposureCap),\n      maxOpenTrades: Number(riskForm.maxOpenTrades),\n      maxDailyTrades: Number(riskForm.maxDailyTrades),\n    };\n\n    if (\n      !Number.isFinite(parsed.riskPercent) ||\n      parsed.riskPercent <= 0 ||\n      !Number.isFinite(parsed.leverageCap) ||\n      parsed.leverageCap <= 0 ||\n      !Number.isFinite(parsed.exposureCap) ||\n      parsed.exposureCap <= 0 ||\n      !Number.isFinite(parsed.maxOpenTrades) ||\n      parsed.maxOpenTrades <= 0 ||\n      !Number.isFinite(parsed.maxDailyTrades) ||\n      parsed.maxDailyTrades < 0\n    ) {\n      setRiskFormError("Risk values must be positive; max daily trades can be 0 for unlimited.");\n      return;\n    }\n\n    setRiskFormError(null);\n    await onRiskSettingsChange({\n      risk_per_trade: parsed.riskPercent / 100,\n      leverage_cap: parsed.leverageCap,\n      exposure_cap: parsed.exposureCap / 100,\n      max_open_trades: Math.floor(parsed.maxOpenTrades),\n      max_daily_trades: Math.floor(parsed.maxDailyTrades),\n    });\n  };\n\n''',
        '''''',
    )
    replace_once(
        "frontend/src/components/ControlPanel.tsx",
        '''            <Metric label="Risk / Trade" value={formatPercent(riskState.risk_per_trade)} />\n            <Metric label="Leverage Cap" value={`${riskState.leverage_cap}x`} />\n            <Metric label="Exposure Cap" value={formatPercent(riskState.exposure_cap)} />\n            <Metric label="Minimum RR" value={`${riskState.min_risk_reward.toFixed(1)}R`} />\n''',
        '''            <Metric label="Scalping Risk" value={`${formatMoney(riskState.risk_profiles?.scalping.risk_amount)} · ${riskState.risk_profiles?.scalping.leverage_cap ?? 20}x`} />\n            <Metric label="Intraday Risk" value={`${formatMoney(riskState.risk_profiles?.intraday.risk_amount)} · ${riskState.risk_profiles?.intraday.leverage_cap ?? 10}x`} />\n            <Metric label="Exposure Cap" value={formatPercent(riskState.exposure_cap)} />\n            <Metric label="Authority" value={readable(riskState.risk_policy_authority, "Authoritative Risk Engine")} />\n''',
    )
    replace_once(
        "frontend/src/components/ControlPanel.tsx",
        '''          <div className="my-5 border-t border-slate-800" />\n\n          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3">\n            <RiskInput label="Risk %" value={riskForm.riskPercent} onChange={(value) => setRiskForm((current) => ({ ...current, riskPercent: value }))} />\n            <RiskInput label="Leverage Cap" value={riskForm.leverageCap} onChange={(value) => setRiskForm((current) => ({ ...current, leverageCap: value }))} />\n            <RiskInput label="Exposure %" value={riskForm.exposureCap} onChange={(value) => setRiskForm((current) => ({ ...current, exposureCap: value }))} />\n            <RiskInput label="Max Open Trades" value={riskForm.maxOpenTrades} onChange={(value) => setRiskForm((current) => ({ ...current, maxOpenTrades: value }))} />\n            <RiskInput label="Max Daily Trades" value={riskForm.maxDailyTrades} onChange={(value) => setRiskForm((current) => ({ ...current, maxDailyTrades: value }))} />\n            <button\n              type="button"\n              onClick={() => void saveRiskSettings()}\n              disabled={actionLoading === "bot-config-risk"}\n              className="mt-auto inline-flex h-[42px] items-center justify-center rounded-xl border border-emerald-500/20 bg-emerald-500/10 px-4 text-xs font-semibold text-emerald-300 transition-colors hover:bg-emerald-500/20 disabled:opacity-50"\n            >\n              {actionLoading === "bot-config-risk" ? "SAVING..." : "SAVE RISK SETTINGS"}\n            </button>\n          </div>\n          {riskFormError && <div className="mt-3 text-xs text-rose-300">{riskFormError}</div>}\n''',
        '''          <div className="mt-5 rounded-xl border border-sky-500/20 bg-sky-500/10 p-3 text-xs text-sky-200">\n            Risk budgets, leverage caps, daily limits and fee-aware execution gates are locked by the Authoritative Risk Engine. UI fields cannot override execution policy.\n          </div>\n''',
    )
    replace_once(
        "frontend/src/components/ControlPanel.tsx",
        '''function RiskInput({ label, value, onChange }: { label: string; value: string; onChange: (value: string) => void }) {\n  return <label className="block space-y-2"><span className="text-[10px] font-mono uppercase tracking-wider text-slate-500">{label}</span><input type="number" min="0" step="any" value={value} onChange={(event) => onChange(event.target.value)} className="dashboard-input" /></label>;\n}\n\n''',
        '''''',
    )

    replace_once(
        "frontend/src/components/TradeHistory.tsx",
        '''  needsAttention: boolean;\n  isClosed: boolean;\n''',
        '''  needsAttention: boolean;\n  countsAsTrade: boolean;\n  isClosed: boolean;\n''',
    )
    replace_once(
        "frontend/src/components/TradeHistory.tsx",
        '''  const adoptedPosition = metadata.source === "exchange_position_only";\n\n  const missingClosedEvidence = isClosed && (exitValue === null || pnlValue === null || feesValue === null);\n''',
        '''  const adoptedPosition = metadata.source === "exchange_position_only";\n  const executionFailedBeforeOrder =\n    String(item.result || "").toLowerCase() === "execution_failed" &&\n    !item.order_id &&\n    !openedAt;\n\n  const missingClosedEvidence = isClosed && (exitValue === null || pnlValue === null || feesValue === null);\n''',
    )
    replace_once(
        "frontend/src/components/TradeHistory.tsx",
        '''  const needsAttention =\n    ["FAILED", "UNCERTAIN", "UNKNOWN"].includes(status) ||\n''',
        '''  const needsAttention =\n    !executionFailedBeforeOrder && (\n    ["FAILED", "UNCERTAIN", "UNKNOWN"].includes(status) ||\n''',
    )
    replace_once(
        "frontend/src/components/TradeHistory.tsx",
        '''    (!item.order_id && !adoptedPosition && !exactExchangeCloseComplete);\n''',
        '''    (!item.order_id && !adoptedPosition && !exactExchangeCloseComplete));\n''',
    )
    replace_once(
        "frontend/src/components/TradeHistory.tsx",
        '''    needsAttention,\n    isClosed,\n''',
        '''    needsAttention,\n    countsAsTrade: !executionFailedBeforeOrder,\n    isClosed,\n''',
    )
    replace_once(
        "frontend/src/components/TradeHistory.tsx",
        '''    needsAttention,\n    isClosed,\n    metadata: {},\n''',
        '''    needsAttention,\n    countsAsTrade: true,\n    isClosed,\n    metadata: {},\n''',
    )
    replace_once(
        "frontend/src/components/TradeHistory.tsx",
        '''  const summary = useMemo(() => ({\n    total: rows.length,\n    open: rows.filter((row) => !row.isClosed && !isPendingSyncStatus(row.auditStatus)).length,\n    pending: rows.filter((row) => isPendingSyncStatus(row.auditStatus)).length,\n    closedToday: rows.filter((row) => row.isClosed && bdtDate(row.closedAt) === todayBdtDate()).length,\n''',
        '''  const summary = useMemo(() => ({\n    total: rows.filter((row) => row.countsAsTrade).length,\n    open: rows.filter((row) => row.countsAsTrade && row.auditStatus === "OPEN").length,\n    pending: rows.filter((row) => row.countsAsTrade && isPendingSyncStatus(row.auditStatus)).length,\n    closedToday: rows.filter((row) => row.countsAsTrade && row.isClosed && bdtDate(row.closedAt) === todayBdtDate()).length,\n''',
    )


if __name__ == "__main__":
    main()
