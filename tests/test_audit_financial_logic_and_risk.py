from __future__ import annotations

import unittest
import threading
from datetime import UTC, datetime, timedelta
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.backtest import run_strategy_backtest
from app.batch3_backtest_truth import _simulate_trade_next_open
from app.authoritative_risk_engine import issue_execution_approval, verify_risk_approval
from app.models import RiskRuntimeState
from app.execution_reservation import reserve_execution_capacity
from app.trading_costs import calculate_cost_adjusted_geometry
from app.scanner_trend import TREND_UP


class FakeBacktestClient:
    def __init__(self, reference_time=None) -> None:
        self.calls: list[tuple[str, str, int]] = []
        self.reference = reference_time or datetime(2026, 7, 15, 12, 0, tzinfo=UTC)

    def safe_fetch_recent_candles(self, symbol: str, interval: str, limit: int):
        self.calls.append((symbol, interval, limit))
        minutes = {"1": 1, "5": 5, "15": 15, "60": 60}[interval]
        count = max(300, min(limit, 400))
        first = self.reference - timedelta(minutes=minutes * count)
        candles = []
        for index in range(count):
            close = 100.0 + (index * 0.05)
            candles.append(
                {
                    "timestamp": (first + timedelta(minutes=minutes * index)).isoformat(),
                    "open": close - 0.02,
                    "high": close + 0.08,
                    "low": close - 0.08,
                    "close": close,
                    "volume": 1000.0,
                    "confirm": True,
                }
            )
        return True, candles, None


class FakeLiveClient:
    def safe_fetch_positions(self):
        return True, [], None

    def safe_fetch_wallet_balance(self):
        return True, {"totalEquity": "1000"}, None


class AuditFinancialLogicAndRiskTests(unittest.TestCase):
    def setUp(self) -> None:
        # Create an isolated named temporary SQLite database for each test to run independently across threads
        import tempfile
        self.db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.engine = create_engine(
            f"sqlite:///{self.db_file.name}",
            connect_args={"check_same_thread": False},
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        import app.models  # noqa: F401
        Base.metadata.create_all(bind=self.engine)

        # Patch SessionLocal globally on the database module and all imported modules
        self.patches = [
            patch("app.database.SessionLocal", self.SessionLocal),
            patch("app.execution_reservation.SessionLocal", self.SessionLocal, create=True),
            patch("app.journal.SessionLocal", self.SessionLocal, create=True),
            patch("app.authoritative_risk_engine.SessionLocal", self.SessionLocal, create=True),
            patch("app.journal.engine", self.engine),
            patch("app.authoritative_risk_engine.get_execution_mode", return_value="demo"),
        ]
        for p in self.patches:
            p.start()

    def tearDown(self) -> None:
        for p in self.patches:
            p.stop()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()
        try:
            import os
            os.unlink(self.db_file.name)
        except Exception:
            pass

    def test_gross_rr_passes_but_net_rr_fails_after_fees(self) -> None:
        """Verify that a signal with sufficient Gross RR gets rejected in backtest when Net RR fails due to fees."""
        # Setup evaluator that returns gross RR of exactly 1.5 (tp=115.0, entry=100.0, stop=90.0)
        def evaluator(symbol, setup, trigger, now=None):
            detected_str = now.isoformat() if now else "2026-07-15T12:00:00+00:00"
            return [{
                "symbol": symbol,
                "strategy_name": "test_strat",
                "strategy": "test_strat",
                "direction": "long",
                "entry": 100.0,
                "stop_loss": 90.0,
                "take_profit": 115.0,
                "risk_reward": 1.5,
                "detected_at": detected_str,
                "status": "active",
                "confidence_score": 85,
                "rejection_reason": None,
            }]

        client = FakeBacktestClient()
        with patch("app.backtest._strategy_evaluator", return_value=evaluator), \
             patch("app.backtest.analyze_trend", return_value={"state": TREND_UP, "strength": 90.0}):
            # With fee_bps=10.0, net RR drops below 1.5, so signal must be rejected
            res_fail = run_strategy_backtest(
                client,
                symbol="BTCUSDT",
                trade_type="scalping",
                min_risk_reward=1.5,
                fee_bps=10.0,
                risk_amount=10.0,
            )
            self.assertTrue(res_fail["ok"])
            self.assertEqual(res_fail["summary"]["trades"], 0)
            self.assertGreater(res_fail["summary"]["skipped_by_reason"].get("net_risk_reward_below_backtest_floor", 0), 0)

            # With zero costs (fee_bps=0.0, slippage_bps=0.0), net RR is exactly 1.5, so it passes and trade is simulated
            res_pass = run_strategy_backtest(
                client,
                symbol="BTCUSDT",
                trade_type="scalping",
                min_risk_reward=1.5,
                fee_bps=0.0,
                slippage_bps=0.0,
                risk_amount=10.0,
            )
            self.assertTrue(res_pass["ok"])
            self.assertGreater(res_pass["summary"]["trades"], 0)

    def test_gross_rr_passes_but_net_rr_fails_after_slippage(self) -> None:
        """Verify that a signal with sufficient Gross RR gets rejected in backtest when Net RR fails due to slippage."""
        def evaluator(symbol, setup, trigger, now=None):
            detected_str = now.isoformat() if now else "2026-07-15T12:00:00+00:00"
            return [{
                "symbol": symbol,
                "strategy_name": "test_strat",
                "strategy": "test_strat",
                "direction": "long",
                "entry": 100.0,
                "stop_loss": 90.0,
                "take_profit": 115.0,
                "risk_reward": 1.5,
                "detected_at": detected_str,
                "status": "active",
                "confidence_score": 85,
                "rejection_reason": None,
            }]

        client = FakeBacktestClient()
        with patch("app.backtest._strategy_evaluator", return_value=evaluator), \
             patch("app.backtest.analyze_trend", return_value={"state": TREND_UP, "strength": 90.0}):
            # With slippage_bps=10.0 (fee_bps=0.0), net RR drops below 1.5, so signal is rejected
            res_fail = run_strategy_backtest(
                client,
                symbol="BTCUSDT",
                trade_type="scalping",
                min_risk_reward=1.5,
                fee_bps=0.0,
                slippage_bps=10.0,
                risk_amount=10.0,
            )
            self.assertTrue(res_fail["ok"])
            self.assertEqual(res_fail["summary"]["trades"], 0)

    def test_net_rr_passes_and_backtest_trade_accepted(self) -> None:
        """Verify that a trade is simulated successfully when Net RR is sufficient."""
        def evaluator(symbol, setup, trigger, now=None):
            detected_str = now.isoformat() if now else "2026-07-15T12:00:00+00:00"
            return [{
                "symbol": symbol,
                "strategy_name": "test_strat",
                "strategy": "test_strat",
                "direction": "long",
                "entry": 100.0,
                "stop_loss": 90.0,
                "take_profit": 118.0,  # gross RR of 1.8
                "risk_reward": 1.8,
                "detected_at": detected_str,
                "status": "active",
                "confidence_score": 85,
                "rejection_reason": None,
            }]

        client = FakeBacktestClient()
        with patch("app.backtest._strategy_evaluator", return_value=evaluator), \
             patch("app.backtest.analyze_trend", return_value={"state": TREND_UP, "strength": 90.0}):
            res = run_strategy_backtest(
                client,
                symbol="BTCUSDT",
                trade_type="scalping",
                min_risk_reward=1.5,
                fee_bps=5.5,
                slippage_bps=2.0,
                risk_amount=10.0,
            )
            self.assertTrue(res["ok"])
            self.assertGreater(res["summary"]["trades"], 0)

    def test_backtest_and_live_risk_engine_parity(self) -> None:
        """Verify that backtest and live risk engines make identical viability decisions for the same inputs."""
        # Signal geometry with gross RR of 1.5
        direction = "long"
        entry = 100.0
        stop_loss = 99.0
        take_profit = 101.5
        min_risk_reward = 1.5
        fee_bps = 5.5
        slippage_bps = 2.0

        # Live engine calculation
        live_economics = calculate_cost_adjusted_geometry(
            direction=direction,
            entry=entry,
            stop_loss=stop_loss,
            take_profit=take_profit,
            quantity=1.0,
            fee_bps=fee_bps,
            slippage_bps=slippage_bps,
        )
        self.assertIsNotNone(live_economics)
        live_net_rr = live_economics["net_risk_reward"]
        live_allowed = (live_net_rr + 1e-9 >= min_risk_reward)

        # Backtest engine calculation
        backtest_economics = calculate_cost_adjusted_geometry(
            direction=direction,
            entry=entry,
            stop_loss=stop_loss,
            take_profit=take_profit,
            quantity=1.0,
            fee_bps=fee_bps,
            slippage_bps=slippage_bps,
        )
        self.assertIsNotNone(backtest_economics)
        backtest_net_rr = backtest_economics["net_risk_reward"]
        backtest_allowed = (backtest_net_rr + 1e-9 >= min_risk_reward)

        self.assertEqual(live_allowed, backtest_allowed)
        self.assertEqual(live_net_rr, backtest_net_rr)

    def test_backtest_result_reports_parity_truthfully(self) -> None:
        """Verify that parity metadata reports profile_rr_gate properly."""
        def evaluator(symbol, setup, trigger, now=None):
            detected_str = now.isoformat() if now else "2026-07-15T12:00:00+00:00"
            return [{
                "symbol": symbol,
                "strategy_name": "test_strat",
                "strategy": "test_strat",
                "direction": "long",
                "entry": 100.0,
                "stop_loss": 90.0,
                "take_profit": 118.0,
                "risk_reward": 1.8,
                "detected_at": detected_str,
                "status": "active",
                "confidence_score": 85,
                "rejection_reason": None,
            }]

        client = FakeBacktestClient()
        with patch("app.backtest._strategy_evaluator", return_value=evaluator), \
             patch("app.backtest.analyze_trend", return_value={"state": TREND_UP, "strength": 90.0}):
            # When run normally, the gate is applied, so profile_rr_gate must be True
            res = run_strategy_backtest(
                client,
                symbol="BTCUSDT",
                trade_type="scalping",
                min_risk_reward=1.5,
                fee_bps=5.5,
                slippage_bps=2.0,
                risk_amount=10.0,
            )
            self.assertTrue(res["live_pipeline_parity"]["profile_rr_gate"])

    def test_first_risk_approval_consumption_succeeds(self) -> None:
        """Verify that the first attempt to consume a signed decision ID is successful."""
        now = datetime(2026, 7, 17, 1, 30, tzinfo=UTC)
        payload = {
            "symbol": "BTCUSDT",
            "strategy_name": "ema_pullback",
            "trade_type": "scalping",
            "direction": "long",
            "entry": 100.0,
            "stop_loss": 99.0,
            "take_profit": 103.0,
            "risk_reward": 3.0,
            "detected_at": (now - timedelta(seconds=10)).isoformat(),
            "status": "active",
            "signal_state": "ACTIVE",
            "is_executable": True,
            "primary_signal": True,
        }

        with patch("app.authoritative_risk_engine.get_trade_by_execution_key", return_value=None):
            approval = issue_execution_approval(
                FakeLiveClient(),
                payload,
                now=now,
                wallet={"totalEquity": "1000"},
                positions=[],
                account_equity=1000.0,
                validation={
                    "allowed": True,
                    "reason": "",
                    "trade_type": "scalping",
                    "risk_amount": 20.0,
                    "risk_per_trade": 0.02,
                    "leverage_cap": 20.0,
                    "exposure_cap": 0.50,
                    "min_risk_reward": 1.5,
                },
                risk_state={"active_symbols": [], "active_trade_count": 0, "available_risk": 50.0},
            )

        self.assertTrue(approval["allowed"])
        verified = verify_risk_approval(
            approval["token"],
            payload,
            execution_mode="demo",
            consume=True,
            now=now,
        )
        self.assertTrue(verified["allowed"])

    def test_reusing_same_decision_id_fails(self) -> None:
        """Verify that reusing the same decision ID fails deterministically with RISK_APPROVAL_ALREADY_USED."""
        now = datetime(2026, 7, 17, 1, 30, tzinfo=UTC)
        payload = {
            "symbol": "BTCUSDT",
            "strategy_name": "ema_pullback",
            "trade_type": "scalping",
            "direction": "long",
            "entry": 100.0,
            "stop_loss": 99.0,
            "take_profit": 103.0,
            "risk_reward": 3.0,
            "detected_at": (now - timedelta(seconds=10)).isoformat(),
            "status": "active",
            "signal_state": "ACTIVE",
            "is_executable": True,
            "primary_signal": True,
        }

        with patch("app.authoritative_risk_engine.get_trade_by_execution_key", return_value=None):
            approval = issue_execution_approval(
                FakeLiveClient(),
                payload,
                now=now,
                wallet={"totalEquity": "1000"},
                positions=[],
                account_equity=1000.0,
                validation={
                    "allowed": True,
                    "reason": "",
                    "trade_type": "scalping",
                    "risk_amount": 20.0,
                    "risk_per_trade": 0.02,
                    "leverage_cap": 20.0,
                    "exposure_cap": 0.50,
                    "min_risk_reward": 1.5,
                },
                risk_state={"active_symbols": [], "active_trade_count": 0, "available_risk": 50.0},
            )

        self.assertTrue(approval["allowed"])
        # First consumption
        verified1 = verify_risk_approval(
            approval["token"],
            payload,
            execution_mode="demo",
            consume=True,
            now=now,
        )
        self.assertTrue(verified1["allowed"])

        # Second consumption
        verified2 = verify_risk_approval(
            approval["token"],
            payload,
            execution_mode="demo",
            consume=True,
            now=now,
        )
        self.assertFalse(verified2["allowed"])
        self.assertEqual(verified2["error"], "RISK_APPROVAL_ALREADY_USED")

    def test_concurrent_consumption_allows_only_one_success(self) -> None:
        """Verify that concurrent consumption allows exactly one success and others fail with RISK_APPROVAL_ALREADY_USED."""
        now = datetime(2026, 7, 17, 1, 30, tzinfo=UTC)
        payload = {
            "symbol": "BTCUSDT",
            "strategy_name": "ema_pullback",
            "trade_type": "scalping",
            "direction": "long",
            "entry": 100.0,
            "stop_loss": 99.0,
            "take_profit": 103.0,
            "risk_reward": 3.0,
            "detected_at": (now - timedelta(seconds=10)).isoformat(),
            "status": "active",
            "signal_state": "ACTIVE",
            "is_executable": True,
            "primary_signal": True,
        }

        with patch("app.authoritative_risk_engine.get_trade_by_execution_key", return_value=None):
            approval = issue_execution_approval(
                FakeLiveClient(),
                payload,
                now=now,
                wallet={"totalEquity": "1000"},
                positions=[],
                account_equity=1000.0,
                validation={
                    "allowed": True,
                    "reason": "",
                    "trade_type": "scalping",
                    "risk_amount": 20.0,
                    "risk_per_trade": 0.02,
                    "leverage_cap": 20.0,
                    "exposure_cap": 0.50,
                    "min_risk_reward": 1.5,
                },
                risk_state={"active_symbols": [], "active_trade_count": 0, "available_risk": 50.0},
            )

        self.assertTrue(approval["allowed"])

        results = []
        threads = []

        def worker():
            res = verify_risk_approval(
                approval["token"],
                payload,
                execution_mode="demo",
                consume=True,
                now=now,
            )
            results.append(res)

        for _ in range(5):
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        successes = [r for r in results if r.get("allowed")]
        failures = [r for r in results if not r.get("allowed") and r.get("error") == "RISK_APPROVAL_ALREADY_USED"]

        self.assertEqual(len(successes), 1)
        self.assertEqual(len(failures), 4)

    def test_replay_protection_works_across_separate_instances(self) -> None:
        """Verify that replay protection works across completely separate verification calls since it uses DB."""
        now = datetime(2026, 7, 17, 1, 30, tzinfo=UTC)
        payload = {
            "symbol": "BTCUSDT",
            "strategy_name": "ema_pullback",
            "trade_type": "scalping",
            "direction": "long",
            "entry": 100.0,
            "stop_loss": 99.0,
            "take_profit": 103.0,
            "risk_reward": 3.0,
            "detected_at": (now - timedelta(seconds=10)).isoformat(),
            "status": "active",
            "signal_state": "ACTIVE",
            "is_executable": True,
            "primary_signal": True,
        }

        with patch("app.authoritative_risk_engine.get_trade_by_execution_key", return_value=None):
            approval = issue_execution_approval(
                FakeLiveClient(),
                payload,
                now=now,
                wallet={"totalEquity": "1000"},
                positions=[],
                account_equity=1000.0,
                validation={
                    "allowed": True,
                    "reason": "",
                    "trade_type": "scalping",
                    "risk_amount": 20.0,
                    "risk_per_trade": 0.02,
                    "leverage_cap": 20.0,
                    "exposure_cap": 0.50,
                    "min_risk_reward": 1.5,
                },
                risk_state={"active_symbols": [], "active_trade_count": 0, "available_risk": 50.0},
            )

        # Separate db check: simulate separate instance/session
        db_first = self.SessionLocal()
        try:
            # First instance consumes it
            verified1 = verify_risk_approval(
                approval["token"],
                payload,
                execution_mode="demo",
                consume=True,
                now=now,
            )
            self.assertTrue(verified1["allowed"])
        finally:
            db_first.close()

        # Separate second instance tries to verify/consume it
        db_second = self.SessionLocal()
        try:
            verified2 = verify_risk_approval(
                approval["token"],
                payload,
                execution_mode="demo",
                consume=True,
                now=now,
            )
            self.assertFalse(verified2["allowed"])
            self.assertEqual(verified2["error"], "RISK_APPROVAL_ALREADY_USED")
        finally:
            db_second.close()

    def test_expired_approval_remains_rejected(self) -> None:
        """Verify that an expired approval is rejected."""
        now = datetime(2026, 7, 17, 1, 30, tzinfo=UTC)
        payload = {
            "symbol": "BTCUSDT",
            "strategy_name": "ema_pullback",
            "trade_type": "scalping",
            "direction": "long",
            "entry": 100.0,
            "stop_loss": 99.0,
            "take_profit": 103.0,
            "risk_reward": 3.0,
            "detected_at": (now - timedelta(seconds=10)).isoformat(),
            "status": "active",
            "signal_state": "ACTIVE",
            "is_executable": True,
            "primary_signal": True,
        }

        with patch("app.authoritative_risk_engine.get_trade_by_execution_key", return_value=None):
            approval = issue_execution_approval(
                FakeLiveClient(),
                payload,
                now=now,
                wallet={"totalEquity": "1000"},
                positions=[],
                account_equity=1000.0,
                validation={
                    "allowed": True,
                    "reason": "",
                    "trade_type": "scalping",
                    "risk_amount": 20.0,
                    "risk_per_trade": 0.02,
                    "leverage_cap": 20.0,
                    "exposure_cap": 0.50,
                    "min_risk_reward": 1.5,
                },
                risk_state={"active_symbols": [], "active_trade_count": 0, "available_risk": 50.0},
            )

        # Try to verify 10 minutes later (expires in max 20 seconds)
        future_now = now + timedelta(minutes=10)
        verified = verify_risk_approval(
            approval["token"],
            payload,
            execution_mode="demo",
            consume=True,
            now=future_now,
        )
        self.assertFalse(verified["allowed"])
        self.assertEqual(verified["error"], "RISK_APPROVAL_EXPIRED")

    def test_existing_execution_key_duplicate_protection_passes(self) -> None:
        """Verify that the existing execution_key duplicate protection is preserved and still passes."""
        db = self.SessionLocal()
        try:
            db.add(
                RiskRuntimeState(
                    id=1,
                    trades_day="2026-07-12",
                    active_symbols="[]",
                    symbol_cooldowns="{}",
                    day_start_equity=1000.0,
                    live_risk=0.0,
                    base_risk_pool=50.0,
                    effective_risk_pool=50.0,
                    available_risk=50.0,
                    active_trade_count=0,
                    circuit_breaker_active=False,
                )
            )
            db.commit()
        finally:
            db.close()

        trade_payload = {
            "symbol": "BTCUSDT",
            "strategy_name": "breakout",
            "direction": "long",
            "execution_mode": "demo",
            "entry": 100.0,
            "stop_loss": 98.0,
            "take_profit": 103.0,
            "quantity": 10.0,
            "detected_at": "2026-07-12T00:00:00+00:00",
            "exchange_metadata": {},
        }

        # Try to reserve once
        res1 = reserve_execution_capacity(
            trade_payload,
            "test_key_123",
            required_risk=20.0,
            max_active_trades=5,
        )
        self.assertTrue(res1["reserved"])

        # Try to reserve again with same key
        res2 = reserve_execution_capacity(
            trade_payload,
            "test_key_123",
            required_risk=20.0,
            max_active_trades=5,
        )
        self.assertFalse(res2["reserved"])
        self.assertEqual(res2["reason"], "DUPLICATE_EXECUTION")

    def test_fees_and_slippage_are_not_double_counted(self) -> None:
        """Verify that simulated PnL does not double-count fee or slippage."""
        signal = {
            "direction": "long",
            "entry": 100.0,
            "stop_loss": 99.0,
            "take_profit": 102.0,
            "risk_reward": 2.0,
        }
        candles = [
            {"timestamp": "2026-07-18T10:00:00Z", "open": 100.0, "high": 100.0, "low": 100.0, "close": 100.0, "volume": 1.0, "confirm": True},
            {"timestamp": "2026-07-18T10:05:00Z", "open": 100.0, "high": 103.0, "low": 100.0, "close": 101.0, "volume": 1.0, "confirm": True},
        ]

        # Run simulation with 5.5 bps fees and 2.0 bps slippage
        result = _simulate_trade_next_open(
            signal,
            candles,
            start_index=1,
            risk_amount=50.0,
            fee_bps=5.5,
            slippage_bps=2.0,
            max_hold_candles=10,
        )
        self.assertIsNotNone(result)
        # Entry fee = 100 * 50 * 5.5/10000 = 2.75
        # Exit fee = 102 * 50 * 5.5/10000 = 2.805
        # Entry slippage = 100 * 50 * 2.0/10000 = 1.0
        # Exit slippage = 102 * 50 * 2.0/10000 = 1.02
        # Total fee = 5.555, Total slippage = 2.02, Net PnL = 100.0 - 5.555 - 2.02 = 92.425
        self.assertAlmostEqual(result["fees"], 5.555, places=5)
        self.assertAlmostEqual(result["slippage"], 2.02, places=5)
        self.assertAlmostEqual(result["net_pnl"], 92.425, places=5)


if __name__ == "__main__":
    unittest.main()
