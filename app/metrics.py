from __future__ import annotations

from typing import Any

from app.execution import get_active_trades, get_closed_trades
from app.journal import get_closed_trade_history


def get_metrics() -> dict[str, Any]:
    active_trades = get_active_trades()
    closed_trades = get_closed_trades() or get_closed_trade_history()
    total_trades = len(active_trades) + len(closed_trades)
    win_trades = sum(1 for trade in closed_trades if str(trade.get("result", "")).lower() == "tp")
    loss_trades = sum(1 for trade in closed_trades if str(trade.get("result", "")).lower() == "sl")
    win_rate = (win_trades / total_trades) if total_trades else 0.0
    pnl_r = (win_trades * 2.0) - loss_trades

    return {
        "total_trades": total_trades,
        "active_trades_count": len(active_trades),
        "closed_trades_count": len(closed_trades),
        "win_trades": win_trades,
        "loss_trades": loss_trades,
        "win_rate": round(win_rate, 4),
        "pnl_r": round(pnl_r, 4),
    }


def get_portfolio_summary() -> dict[str, Any]:
    metrics = get_metrics()
    return {
        "active_trades": metrics["active_trades_count"],
        "closed_trades": metrics["closed_trades_count"],
        "total_trades": metrics["total_trades"],
        "win_rate": metrics["win_rate"],
        "pnl_r": metrics["pnl_r"],
        "execution_mode": next((trade.get("execution_mode") for trade in get_active_trades() if trade.get("execution_mode")), "demo"),
    }
