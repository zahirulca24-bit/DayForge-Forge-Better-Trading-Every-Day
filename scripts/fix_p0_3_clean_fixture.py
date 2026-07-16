from pathlib import Path

path = Path("tests/test_exchange_journal_backfill.py")
text = path.read_text(encoding="utf-8")
old = '''        existing = {
            "journal_id": "existing",
            "execution_key": "ledger-existing",
            "symbol": "ONDOUSDT",
            "direction": "long",
            "quantity": 10.0,
            "status": "closed",
            "exchange_metadata": {
'''
new = '''        existing = {
            "journal_id": "existing",
            "execution_key": "ledger-existing",
            "symbol": "ONDOUSDT",
            "direction": "long",
            "quantity": 10.0,
            "status": "closed",
            "strategy_name": "exchange_backfill",
            "exchange_metadata": {
'''
if old not in text:
    raise RuntimeError("clean idempotency fixture anchor not found")
path.write_text(text.replace(old, new, 1), encoding="utf-8")
