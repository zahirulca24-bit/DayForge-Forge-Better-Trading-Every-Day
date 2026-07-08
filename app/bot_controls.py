from typing import Any

from app.config import settings
from app.database import SessionLocal
from app.models import BotRuntimeConfig


def ensure_runtime_config() -> None:
    db = SessionLocal()
    try:
        row = db.query(BotRuntimeConfig).filter(BotRuntimeConfig.id == 1).first()
        if row is None:
            db.add(
                BotRuntimeConfig(
                    id=1,
                    bot_status="idle",
                    emergency_stop=False,
                    execution_mode="demo",
                    auto_trading_enabled=True,
                )
            )
            db.commit()
    finally:
        db.close()


def start_bot() -> dict[str, Any]:
    return _update_runtime(bot_status="running")


def stop_bot() -> dict[str, Any]:
    return _update_runtime(bot_status="stopped")


def activate_emergency_stop() -> dict[str, Any]:
    return _update_runtime(bot_status="stopped", emergency_stop=True)


def resume_bot() -> dict[str, Any]:
    return _update_runtime(emergency_stop=False)


def update_bot_config(
    execution_mode: str | None = None,
    auto_trading_enabled: bool | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    if execution_mode is not None:
        normalized_mode = execution_mode.lower()
        if normalized_mode not in {"demo", "live"}:
            raise ValueError("Execution mode must be demo or live")
        if normalized_mode == "live" and not is_live_mode_available():
            raise ValueError("Live mode cannot be enabled until real Bybit API keys are configured")
        payload["execution_mode"] = normalized_mode

    if auto_trading_enabled is not None:
        payload["auto_trading_enabled"] = bool(auto_trading_enabled)

    return _update_runtime(**payload)


def get_bot_status() -> dict[str, Any]:
    row = _get_runtime_row()
    return _serialize_runtime(row)


def can_execute() -> tuple[bool, str]:
    row = _get_runtime_row()
    if row.emergency_stop:
        return False, "Emergency stop is active"
    if row.bot_status != "running":
        return False, "Bot is not running"
    if not row.auto_trading_enabled:
        return False, "Auto trading is disabled"
    if row.execution_mode == "live" and not is_live_mode_available():
        return False, "Live mode is not unlocked"
    return True, ""


def get_execution_mode() -> str:
    return _get_runtime_row().execution_mode


def is_live_mode_available() -> bool:
    return bool(settings.bybit_live_api_key and settings.bybit_live_api_secret)


def _update_runtime(**updates: Any) -> dict[str, Any]:
    db = SessionLocal()
    try:
        row = db.query(BotRuntimeConfig).filter(BotRuntimeConfig.id == 1).first()
        if row is None:
            row = BotRuntimeConfig(id=1)
            db.add(row)
            db.flush()

        for key, value in updates.items():
            setattr(row, key, value)
        db.commit()
        db.refresh(row)
        return _serialize_runtime(row)
    finally:
        db.close()


def _get_runtime_row() -> BotRuntimeConfig:
    ensure_runtime_config()
    db = SessionLocal()
    try:
        row = db.query(BotRuntimeConfig).filter(BotRuntimeConfig.id == 1).first()
        if row is None:
            raise RuntimeError("Bot runtime config is unavailable")
        db.expunge(row)
        return row
    finally:
        db.close()


def _serialize_runtime(row: BotRuntimeConfig) -> dict[str, Any]:
    return {
        "status": row.bot_status,
        "emergency_stop": row.emergency_stop,
        "execution_mode": row.execution_mode,
        "auto_trading_enabled": row.auto_trading_enabled,
        "live_mode_available": is_live_mode_available(),
    }
