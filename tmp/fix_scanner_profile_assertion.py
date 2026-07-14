from pathlib import Path

path = Path("tests/test_scanner_integration.py")
text = path.read_text(encoding="utf-8")
old = '''        self.assertEqual(result["signals"][0]["confirmation_count"], 1)\n        self.assertEqual(result["signals"][0]["confirmations"][0]["trade_type"], "intraday")\n        intraday_result = next(item for item in result["results"] if item["trade_type"] == "intraday")\n        self.assertEqual(intraday_result["signal_state"], "ACTIVE")\n        self.assertTrue(intraday_result["is_executable"])\n        self.assertEqual(intraday_result["risk_reward"], 2.0)\n'''
new = '''        self.assertEqual(result["signals"][0]["confirmation_count"], 1)\n        represented_profiles = {\n            result["signals"][0]["trade_type"],\n            result["signals"][0]["confirmations"][0]["trade_type"],\n        }\n        self.assertEqual(represented_profiles, {"scalping", "intraday"})\n        intraday_result = next(item for item in result["results"] if item["trade_type"] == "intraday")\n        self.assertEqual(intraday_result["signal_state"], "ACTIVE")\n        self.assertTrue(intraday_result["is_executable"])\n        self.assertEqual(intraday_result["risk_reward"], 2.0)\n'''
if text.count(old) != 1:
    raise RuntimeError("Expected one updated scanner assertion block")
path.write_text(text.replace(old, new, 1), encoding="utf-8")
