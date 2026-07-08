from threading import Lock
from typing import Any

from app.exchange import BybitDemoClient
from app.strategy import evaluate_ema_pullback_strategy


SCANNER_SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "XRPUSDT",
    "BNBUSDT",
    "DOGEUSDT",
    "ADAUSDT",
    "LINKUSDT",
]
BIAS_CANDLE_LIMIT = 250
TRIGGER_CANDLE_LIMIT = 50

_signals_lock = Lock()
_latest_signals: list[dict[str, Any]] = []
_latest_scan_results: list[dict[str, Any]] = []


def run_scan(client: BybitDemoClient) -> dict[str, Any]:
    signals: list[dict[str, Any]] = []
    scan_results: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []

    for symbol in SCANNER_SYMBOLS:
        ok_5m, candles_5m, error_5m = client.safe_fetch_recent_candles(symbol=symbol, interval="5", limit=BIAS_CANDLE_LIMIT)
        if not ok_5m:
            skipped.append({"symbol": symbol, "reason": error_5m or "Failed to fetch 5m candles"})
            continue

        ok_1m, candles_1m, error_1m = client.safe_fetch_recent_candles(symbol=symbol, interval="1", limit=TRIGGER_CANDLE_LIMIT)
        if not ok_1m:
            skipped.append({"symbol": symbol, "reason": error_1m or "Failed to fetch 1m candles"})
            continue

        signal = evaluate_ema_pullback_strategy(symbol=symbol, candles_5m=candles_5m, candles_1m=candles_1m)
        normalized = {
            "symbol": symbol,
            "direction": signal.get("direction"),
            "entry": signal.get("entry"),
            "stop_loss": signal.get("stop_loss"),
            "take_profit": signal.get("take_profit"),
            "risk_reward": signal.get("risk_reward"),
            "detected_at": signal.get("detected_at"),
            "status": signal.get("status"),
            "confidence_score": signal.get("confidence_score"),
            "rejection_reason": signal.get("rejection_reason"),
        }
        scan_results.append(normalized)
        if normalized.get("direction") and normalized.get("status") == "active":
            signals.append(normalized)

    with _signals_lock:
        _latest_signals.clear()
        _latest_signals.extend(signals)
        _latest_scan_results.clear()
        _latest_scan_results.extend(scan_results)

    return {
        "ok": True,
        "symbols_scanned": len(SCANNER_SYMBOLS),
        "signals_found": len(signals),
        "signals": list(signals),
        "results": list(scan_results),
        "skipped": skipped,
    }


def get_latest_signals() -> list[dict[str, Any]]:
    with _signals_lock:
        return list(_latest_scan_results or _latest_signals)


def get_active_signals() -> list[dict[str, Any]]:
    with _signals_lock:
        return [signal for signal in _latest_signals if signal.get("status") == "active"]
