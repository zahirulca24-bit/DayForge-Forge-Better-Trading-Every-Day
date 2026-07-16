from __future__ import annotations

from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    target = Path(path)
    text = target.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"Expected integration anchor not found in {path}: {old[:120]!r}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> None:
    replace_once(
        "app/background_worker.py",
        "from app.exchange import get_exchange_client\n",
        "from app.exchange import get_exchange_client\nfrom app.exchange_journal_backfill import backfill_exchange_journal_lifecycle\n",
    )
    replace_once(
        "app/background_worker.py",
        """                ledger_repair_result = await asyncio.to_thread(repair_incomplete_journal_closes, client)\n                if not ledger_repair_result.get(\"ok\") and ledger_repair_result.get(\"pending\"):\n                    logger.debug(\"Ledger close repair pending: %s\", ledger_repair_result.get(\"pending\"))\n\n                await asyncio.to_thread(sync_loss_cooldowns)\n""",
        """                ledger_repair_result = await asyncio.to_thread(repair_incomplete_journal_closes, client)\n                if not ledger_repair_result.get(\"ok\") and ledger_repair_result.get(\"pending\"):\n                    logger.debug(\"Ledger close repair pending: %s\", ledger_repair_result.get(\"pending\"))\n\n                lifecycle_result = await asyncio.to_thread(backfill_exchange_journal_lifecycle, client)\n                if not lifecycle_result.get(\"ok\"):\n                    _safe_log_bot_event(\n                        \"exchange_journal_backfill_failed\",\n                        lifecycle_result.get(\"error\") or \"Exchange lifecycle backfill failed\",\n                        level=\"warning\",\n                        metadata={\n                            \"endpoint\": \"background:exchange_journal_backfill\",\n                            \"affected_module\": \"journal\",\n                            \"error_code\": \"EXCHANGE_JOURNAL_BACKFILL_FAILED\",\n                            \"result\": lifecycle_result,\n                        },\n                    )\n                elif lifecycle_result.get(\"pending\"):\n                    logger.debug(\"Exchange journal lifecycle backfill pending: %s\", lifecycle_result.get(\"pending\"))\n\n                await asyncio.to_thread(sync_loss_cooldowns)\n""",
    )

    replace_once(
        "app/journal.py",
        """def _send_supabase(table: str, payload: dict[str, Any], upsert: bool) -> None:\n    if not settings.supabase_url or not settings.supabase_service_role_key:\n        return\n""",
        """def _send_supabase(table: str, payload: dict[str, Any], upsert: bool) -> None:\n    database_url = str(settings.database_url or \"\").strip().lower()\n    if database_url.startswith((\"postgres://\", \"postgresql://\", \"postgresql+psycopg://\")):\n        # PostgreSQL is already the durable primary. Mirroring the same payload\n        # through Supabase REST would create duplicate bot events and redundant\n        # journal writes against the same database.\n        return\n    if not settings.supabase_url or not settings.supabase_service_role_key:\n        return\n""",
    )

    replace_once(
        "app/reconciliation_persistence.py",
        "from app.journal import append_trade_event, update_trade_entry\n",
        "from app.journal import append_trade_event, update_trade_entry\n",
    )
    replace_once(
        "app/reconciliation_persistence.py",
        """def _persist_reconciliation_event(\n    journal_id: str,\n    event_type: str,\n    message: str,\n    payload: dict[str, Any],\n) -> None:\n""",
        """def _persist_exact_close(\n    journal_id: str,\n    trade: dict[str, Any],\n    exact_close: dict[str, Any],\n) -> dict[str, Any] | None:\n    if not journal_id:\n        return None\n    trade_metadata = trade.get(\"exchange_metadata\") if isinstance(trade.get(\"exchange_metadata\"), dict) else {}\n    close_metadata = exact_close.get(\"exchange_metadata\") if isinstance(exact_close.get(\"exchange_metadata\"), dict) else {}\n    metadata = {**trade_metadata, **close_metadata}\n    persisted = update_trade_entry(\n        journal_id,\n        {\n            \"status\": \"closed\",\n            \"result\": exact_close.get(\"result\"),\n            \"sl_hit_reason\": exact_close.get(\"sl_hit_reason\"),\n            \"close_reason\": exact_close.get(\"close_reason\"),\n            \"exit_price\": exact_close.get(\"exit_price\"),\n            \"realized_pnl\": exact_close.get(\"realized_pnl\"),\n            \"fees\": exact_close.get(\"fees\"),\n            \"closed_at\": exact_close.get(\"closed_at\"),\n            \"exchange_metadata\": metadata,\n        },\n    )\n    if persisted is not None:\n        append_trade_event(\n            journal_id,\n            \"RECONCILED_CLOSED_EXACT\",\n            \"Exchange position is absent and exact Bybit close fill/PnL/fees were persisted after restart.\",\n            {\n                \"symbol\": trade.get(\"symbol\"),\n                \"source\": ((metadata.get(\"close_sync\") or {}).get(\"source\") if isinstance(metadata.get(\"close_sync\"), dict) else None),\n                \"realized_pnl\": exact_close.get(\"realized_pnl\"),\n                \"fees\": exact_close.get(\"fees\"),\n            },\n        )\n    return persisted\n\n\ndef _persist_reconciliation_event(\n    journal_id: str,\n    event_type: str,\n    message: str,\n    payload: dict[str, Any],\n) -> None:\n""",
    )

    replace_once(
        "app/authoritative_reconciliation.py",
        """from app.reconciliation_persistence import (\n    _mark_journal_stale, _persist_active_trade, _persist_pending_close_sync,\n    _persist_reconciliation_event, _persist_reconciliation_state,\n)\n""",
        """from app.reconciliation_persistence import (\n    _mark_journal_stale, _persist_active_trade, _persist_exact_close,\n    _persist_pending_close_sync, _persist_reconciliation_event,\n    _persist_reconciliation_state,\n)\n""",
    )
    replace_once(
        "app/authoritative_reconciliation.py",
        """        if exact_close is not None:\n            closed_trade = close_trade(journal_id, exact_close) if journal_id else None\n            if closed_trade is None:\n                closed_trade = {**trade, **exact_close, \"status\": \"closed\"}\n            closed_symbols.append(symbol)\n            closed_trades.append(closed_trade)\n            updates.append(\n                {\n                    \"symbol\": symbol,\n                    \"status\": \"closed\",\n                    \"reason\": \"Exact Bybit closed PnL synchronized\",\n                }\n            )\n            _persist_reconciliation_event(\n                journal_id,\n                \"RECONCILED_CLOSED_EXACT\",\n                \"Exchange position is absent and exact Bybit close fill/PnL/fees were synchronized.\",\n                exact_close,\n            )\n            continue\n""",
        """        if exact_close is not None:\n            closed_trade = close_trade(journal_id, exact_close) if journal_id else None\n            persisted_after_restart = False\n            if closed_trade is None and journal_id:\n                closed_trade = _persist_exact_close(journal_id, trade, exact_close)\n                persisted_after_restart = closed_trade is not None\n            if closed_trade is None:\n                closed_trade = {**trade, **exact_close, \"status\": \"closed\"}\n            closed_symbols.append(symbol)\n            closed_trades.append(closed_trade)\n            updates.append(\n                {\n                    \"symbol\": symbol,\n                    \"status\": \"closed\",\n                    \"reason\": \"Exact Bybit closed PnL synchronized\",\n                }\n            )\n            if not persisted_after_restart:\n                _persist_reconciliation_event(\n                    journal_id,\n                    \"RECONCILED_CLOSED_EXACT\",\n                    \"Exchange position is absent and exact Bybit close fill/PnL/fees were synchronized.\",\n                    exact_close,\n                )\n            continue\n""",
    )


if __name__ == "__main__":
    main()
