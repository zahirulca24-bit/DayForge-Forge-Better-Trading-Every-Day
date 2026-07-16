from pathlib import Path


path = Path("app/authoritative_risk_engine.py")
text = path.read_text(encoding="utf-8")
old = '''    if detected_at is not None:\n        max_age = max(int(settings.risk_signal_max_age_seconds), 1)\n        age_seconds = (current - detected_at).total_seconds()\n        if age_seconds < -5:\n            return _reject("SIGNAL_TIMESTAMP_INVALID", "Signal detected_at timestamp is in the future")\n        if age_seconds > max_age:\n            return _reject(\n                "SIGNAL_STALE",\n                f"Signal age {age_seconds:.0f}s exceeds the {max_age}s execution limit",\n            )\n'''
new = '''    if detected_at is not None and normalized.get("auto_triggered"):\n        max_age = max(int(settings.risk_signal_max_age_seconds), 1)\n        age_seconds = (current - detected_at).total_seconds()\n        if age_seconds < -5:\n            return _reject("SIGNAL_TIMESTAMP_INVALID", "Signal detected_at timestamp is in the future")\n        if age_seconds > max_age:\n            return _reject(\n                "SIGNAL_STALE",\n                f"Signal age {age_seconds:.0f}s exceeds the {max_age}s execution limit",\n            )\n'''
if old not in text:
    raise RuntimeError("P0-5 stale-signal compatibility anchor not found")
path.write_text(text.replace(old, new, 1), encoding="utf-8")
