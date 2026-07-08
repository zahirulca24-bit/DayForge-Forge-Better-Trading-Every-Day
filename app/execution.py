from __future__ import annotations

from datetime import UTC, datetime
from math import isfinite
from threading import Lock
from typing import Any

from app.bot_controls import can_execute, get_execution_mode
from app.exchange import BybitClient, ExchangeError
from app.journal import create_trade_entry, update_trade_entry
from app.risk import register_active_trade, start_loss_cooldown, validate_trade


SL_REASON_UNKNOWN = "unknown"
SL_REASON_EXCHANGE_CLOSE = "exchange_close"
SL_REASON_FORCED_RISK_CLOSE = "forced_risk_close"

_execution_lock = Lock()
_active_trades: list[dict[str, Any]] = []
_closed_trades: list[dict[str, Any]] = []
_active_order_ids: list[str] = []


def execute_signal(client: BybitClient, signal: dict[str, Any], auto_triggered: bool = False) -> dict[str, Any]:
    allowed, reason = can_execute()
    if not allowed:
        return {"ok": False, "error": reason}

    validation = validate_trade(signal)
    if not validation.get("allowed"):
        return {"ok": False, "error": validation.get("reason", "Risk validation failed")}

    normalized_signal = _normalize_signal(signal)
    if normalized_signal is None:
        return {"ok": False, "error": "Invalid execution signal payload"}

    ok_symbol, symbol_infos, symbol_error = client.safe_fetch_symbol_info(symbol=normalized_signal["symbol"])
    if not ok_symbol or not symbol_infos:
        return {"ok": False, "error": symbol_error or "Symbol info unavailable"}

    ok_wallet, wallet, wallet_error = client.safe_fetch_wallet_balance()
    if not ok_wallet or wallet is None:
        return {"ok": False, "error": wallet_error or "Wallet balance unavailable"}

    symbol_info = symbol_infos[0]
    quantity = _calculate_position_size(
        wallet=wallet,
        entry=normalized_signal["entry"],
        stop_loss=normalized_signal["stop_loss"],
        qty_step=symbol_info.get("qtyStep"),
        min_order_qty=symbol_info.get("minOrderQty"),
        risk_per_trade=float(validation.get("risk_per_trade", 0.01)),
        client=client,
    )
    if quantity is None:
        return {"ok": False, "error": "Unable to calculate valid position size"}

    take_profit = client.normalize_price(normalized_signal["take_profit"], symbol_info["tickSize"])
    stop_loss = client.normalize_price(normalized_signal["stop_loss"], symbol_info["tickSize"])
    side = "Buy" if normalized_signal["direction"] == "long" else "Sell"
    execution_mode = get_execution_mode()

    try:
        order_result = client.place_market_order(
            symbol=normalized_signal["symbol"],
            side=side,
            qty=quantity,
        )
    except ExchangeError as exc:
        return {"ok": False, "error": str(exc)}

    order_id = str(order_result.get("orderId") or order_result.get("orderLinkId") or "")
    trade = {
        "symbol": normalized_signal["symbol"],
        "direction": normalized_signal["direction"],
        "entry": normalized_signal["entry"],
        "stop_loss": float(stop_loss),
        "take_profit": float(take_profit),
        "quantity": quantity,
        "order_id": order_id,
        "status": "active",
        "detected_at": normalized_signal.get("detected_at"),
        "opened_at": _utc_now_iso(),
        "execution_mode": execution_mode,
        "result": None,
        "sl_hit_reason": None,
        "auto_triggered": auto_triggered,
        "exchange_metadata": {
            "mode": execution_mode,
            "order_response": order_result,
        },
    }

    protection_error: str | None = None
    try:
        client.set_trading_stop(
            symbol=normalized_signal["symbol"],
            take_profit=take_profit,
            stop_loss=stop_loss,
        )
    except ExchangeError as exc:
        protection_error = str(exc)
        trade["status"] = "protection_pending"

    journal = create_trade_entry(trade)
    trade["journal_id"] = journal["journal_id"]

    with _execution_lock:
        _active_trades.append(trade)
        if order_id:
            _active_order_ids.append(order_id)

    register_active_trade(normalized_signal["symbol"])

    return {
        "ok": True,
        "trade": trade,
        "warning": protection_error,
    }


def get_active_trades() -> list[dict[str, Any]]:
    with _execution_lock:
        return [dict(trade) for trade in _active_trades]


def get_closed_trades() -> list[dict[str, Any]]:
    with _execution_lock:
        return [dict(trade) for trade in _closed_trades]


def replace_active_trades(trades: list[dict[str, Any]]) -> None:
    with _execution_lock:
        _active_trades.clear()
        _active_trades.extend(dict(trade) for trade in trades)
        _active_order_ids.clear()
        _active_order_ids.extend(str(trade.get("order_id")) for trade in trades if trade.get("order_id"))


def close_trade(
    journal_id: str,
    close_fields: dict[str, Any],
) -> dict[str, Any] | None:
    with _execution_lock:
        trade = next((item for item in _active_trades if item.get("journal_id") == journal_id), None)
        if trade is None:
            return None

        closed_trade = dict(trade)
        closed_trade.update(close_fields)
        closed_trade["status"] = "closed"
        closed_trade["closed_at"] = close_fields.get("closed_at") or _utc_now_iso()
        _active_trades[:] = [item for item in _active_trades if item.get("journal_id") != journal_id]
        _closed_trades.append(closed_trade)
        if closed_trade.get("order_id"):
            _active_order_ids[:] = [item for item in _active_order_ids if item != closed_trade.get("order_id")]

    update_trade_entry(
        journal_id,
        {
            "status": "closed",
            "result": closed_trade.get("result"),
            "sl_hit_reason": closed_trade.get("sl_hit_reason"),
            "closed_at": closed_trade.get("closed_at"),
            "exchange_metadata": closed_trade.get("exchange_metadata"),
        },
    )

    if closed_trade.get("result") == "sl":
        start_loss_cooldown()
    return closed_trade


def add_closed_trades(trades: list[dict[str, Any]]) -> None:
    if not trades:
        return

    with _execution_lock:
        for trade in trades:
            _closed_trades.append(dict(trade))


def _calculate_position_size(
    wallet: dict[str, Any],
    entry: float,
    stop_loss: float,
    qty_step: str | None,
    min_order_qty: str | None,
    risk_per_trade: float,
    client: BybitClient,
) -> str | None:
    if qty_step is None:
        return None

    account_balance = _extract_balance(wallet)
    sl_distance = abs(entry - stop_loss)
    if not _is_positive_number(account_balance, sl_distance, risk_per_trade):
        return None

    risk_amount = account_balance * risk_per_trade
    raw_quantity = risk_amount / sl_distance
    normalized = client.normalize_quantity(raw_quantity, qty_step)

    try:
        quantity_value = float(normalized)
    except ValueError:
        return None

    if min_order_qty is not None and quantity_value < float(min_order_qty):
        min_normalized = client.normalize_quantity(float(min_order_qty), qty_step)
        if float(min_normalized) <= 0:
            return None
        return min_normalized

    return normalized if quantity_value > 0 else None


def _extract_balance(wallet: dict[str, Any]) -> float | None:
    for key in ["totalAvailableBalance", "totalWalletBalance", "totalEquity"]:
        value = wallet.get(key)
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            continue
        if isfinite(numeric) and numeric > 0:
            return numeric
    return None


def _normalize_signal(signal: dict[str, Any]) -> dict[str, Any] | None:
    try:
        direction = str(signal.get("direction", "")).lower()
        if direction not in {"long", "short"}:
            return None
        return {
            "symbol": str(signal.get("symbol", "")).upper(),
            "direction": direction,
            "entry": float(signal.get("entry")),
            "stop_loss": float(signal.get("stop_loss")),
            "take_profit": float(signal.get("take_profit")),
            "detected_at": signal.get("detected_at"),
        }
    except (TypeError, ValueError):
        return None


def _is_positive_number(*values: float | None) -> bool:
    return all(value is not None and isfinite(value) and value > 0 for value in values)


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()
