from threading import Lock
from typing import Any

from app.exchange import BybitDemoClient


_symbol_lock = Lock()
_symbol_metadata: dict[str, dict[str, dict[str, Any]]] = {}


def refresh_symbol_metadata(
    client: BybitDemoClient,
    category: str = "linear",
    symbol: str | None = None,
) -> dict[str, Any]:
    ok, symbols, error = client.safe_fetch_symbol_info(category=category, symbol=symbol)
    if not ok:
        return {"ok": False, "symbols": get_symbol_metadata(category=category, symbol=symbol), "error": error}

    with _symbol_lock:
        category_store = _symbol_metadata.setdefault(category, {})
        for item in symbols:
            name = item.get("symbol")
            if name:
                category_store[name] = item

    return {"ok": True, "symbols": get_symbol_metadata(category=category, symbol=symbol), "error": None}


def get_symbol_metadata(category: str = "linear", symbol: str | None = None) -> list[dict[str, Any]]:
    with _symbol_lock:
        category_store = _symbol_metadata.get(category, {})
        if symbol:
            item = category_store.get(symbol)
            return [item] if item else []
        return list(category_store.values())
