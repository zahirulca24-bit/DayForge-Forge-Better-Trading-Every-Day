from __future__ import annotations

from math import isfinite
from typing import Any

GRADE_A_PLUS = "A+"
GRADE_A = "A"
GRADE_B_PLUS = "B+"
GRADE_REJECT = "REJECT"

ACTION_EXECUTE = "EXECUTE"
ACTION_WATCHLIST = "WATCHLIST_ONLY"
ACTION_REJECT = "REJECT"

A_PLUS_SCORE = 95.0
A_SCORE = 85.0
B_PLUS_SCORE = 75.0

PROFILE_RULES: dict[str, dict[str, float]] = {
    "scalping": {
        "minimum_rr": 1.5,
        "preferred_rr": 2.5,
    },
    "intraday": {
        "minimum_rr": 2.0,
        "preferred_rr": 3.0,
    },
}

COMPONENT_WEIGHTS: dict[str, float] = {
    "trend": 20.0,
    "setup": 20.0,
    "confirmation": 20.0,
    "strategy_confidence": 15.0,
    "market_quality": 10.0,
    "volume_quality": 5.0,
    "risk_reward": 10.0,
}


def grade_signal(signal: dict[str, Any]) -> dict[str, Any]:
    status = str(signal.get("status") or "").lower().strip()
    direction = str(signal.get("direction") or "").lower().strip()
    trade_type = _normalize_trade_type(signal.get("trade_type"))
    profile = PROFILE_RULES[trade_type]
    trend_aligned = bool(signal.get("trend_aligned"))

    geometry = _authoritative_geometry(
        direction=direction,
        entry=signal.get("entry"),
        stop_loss=signal.get("stop_loss"),
        take_profit=signal.get("take_profit"),
    )
    authoritative_rr = geometry["risk_reward"] if geometry else None

    trend_quality = _bounded(signal.get("trend_strength"))
    strategy_confidence = _bounded(signal.get("confidence_score"))
    setup_quality = _setup_quality(signal, strategy_confidence)
    confirmation_quality = _confirmation_quality(signal, strategy_confidence, status)
    market_quality = _bounded(signal.get("market_score"))
    volume_quality = _volume_quality(signal)
    rr_quality = _risk_reward_quality(authoritative_rr, profile)

    component_quality = {
        "trend": trend_quality,
        "setup": setup_quality,
        "confirmation": confirmation_quality,
        "strategy_confidence": strategy_confidence,
        "market_quality": market_quality,
        "volume_quality": volume_quality,
        "risk_reward": rr_quality,
    }
    component_points = {
        name: round((component_quality[name] / 100.0) * weight, 2)
        for name, weight in COMPONENT_WEIGHTS.items()
    }
    total_score = round(min(100.0, sum(component_points.values())), 2)

    base = {
        "grade": GRADE_REJECT,
        "grade_action": ACTION_REJECT,
        "grade_score": total_score,
        "grade_components": component_points,
        "grade_component_quality": {name: round(value, 2) for name, value in component_quality.items()},
        "grade_reasons": [],
        "executable": False,
        "watchlist_only": False,
        "authoritative_risk_reward": round(authoritative_rr, 4) if authoritative_rr is not None else None,
        "grade_minimum_rr": profile["minimum_rr"],
        "grade_preferred_rr": profile["preferred_rr"],
        "grade_trade_type": trade_type,
    }

    hard_failure = _hard_failure(
        status=status,
        direction=direction,
        trend_aligned=trend_aligned,
        geometry=geometry,
        authoritative_rr=authoritative_rr,
        minimum_rr=profile["minimum_rr"],
    )
    if hard_failure:
        base["grade_reasons"] = [hard_failure]
        return base

    if status == "active" and _qualifies_a_plus(
        total_score=total_score,
        authoritative_rr=float(authoritative_rr),
        preferred_rr=profile["preferred_rr"],
        trend_quality=trend_quality,
        setup_quality=setup_quality,
        confirmation_quality=confirmation_quality,
        strategy_confidence=strategy_confidence,
        market_quality=market_quality,
        volume_quality=volume_quality,
    ):
        return {
            **base,
            "grade": GRADE_A_PLUS,
            "grade_action": ACTION_EXECUTE,
            "grade_reasons": [
                "strong_trend",
                "strong_setup",
                "strong_confirmation",
                "strong_volume_and_market_quality",
                "preferred_risk_reward_met",
                "high_confidence",
            ],
            "executable": True,
        }

    if status == "active" and _qualifies_a(
        total_score=total_score,
        authoritative_rr=float(authoritative_rr),
        minimum_rr=profile["minimum_rr"],
        trend_quality=trend_quality,
        setup_quality=setup_quality,
        confirmation_quality=confirmation_quality,
        strategy_confidence=strategy_confidence,
        market_quality=market_quality,
    ):
        return {
            **base,
            "grade": GRADE_A,
            "grade_action": ACTION_EXECUTE,
            "grade_reasons": [
                "valid_trend",
                "valid_setup",
                "valid_confirmation",
                "profile_minimum_risk_reward_met",
                "acceptable_confidence",
            ],
            "executable": True,
        }

    if status == "near_setup" and _qualifies_b_plus(
        total_score=total_score,
        trend_quality=trend_quality,
        setup_quality=setup_quality,
        strategy_confidence=strategy_confidence,
    ):
        return {
            **base,
            "grade": GRADE_B_PLUS,
            "grade_action": ACTION_WATCHLIST,
            "grade_reasons": [
                "near_setup_only",
                "trend_and_setup_quality_valid",
                "entry_confirmation_pending",
            ],
            "watchlist_only": True,
        }

    if status == "active":
        base["grade_reasons"] = ["active_signal_quality_below_A_threshold"]
    elif status == "near_setup":
        base["grade_reasons"] = ["near_setup_quality_below_B_plus_threshold"]
    else:
        base["grade_reasons"] = ["signal_status_not_gradable"]
    return base


def _qualifies_a_plus(
    *,
    total_score: float,
    authoritative_rr: float,
    preferred_rr: float,
    trend_quality: float,
    setup_quality: float,
    confirmation_quality: float,
    strategy_confidence: float,
    market_quality: float,
    volume_quality: float,
) -> bool:
    return (
        total_score >= A_PLUS_SCORE
        and authoritative_rr + 1e-9 >= preferred_rr
        and trend_quality >= 75.0
        and setup_quality >= 85.0
        and confirmation_quality >= 85.0
        and strategy_confidence >= 85.0
        and market_quality >= 70.0
        and volume_quality >= 70.0
    )


def _qualifies_a(
    *,
    total_score: float,
    authoritative_rr: float,
    minimum_rr: float,
    trend_quality: float,
    setup_quality: float,
    confirmation_quality: float,
    strategy_confidence: float,
    market_quality: float,
) -> bool:
    return (
        total_score >= A_SCORE
        and authoritative_rr + 1e-9 >= minimum_rr
        and trend_quality >= 55.0
        and setup_quality >= 70.0
        and confirmation_quality >= 70.0
        and strategy_confidence >= 70.0
        and market_quality >= 55.0
    )


def _qualifies_b_plus(
    *,
    total_score: float,
    trend_quality: float,
    setup_quality: float,
    strategy_confidence: float,
) -> bool:
    return (
        total_score >= B_PLUS_SCORE
        and trend_quality >= 50.0
        and setup_quality >= 70.0
        and strategy_confidence >= 65.0
    )


def _hard_failure(
    *,
    status: str,
    direction: str,
    trend_aligned: bool,
    geometry: dict[str, float] | None,
    authoritative_rr: float | None,
    minimum_rr: float,
) -> str | None:
    if status not in {"active", "near_setup"}:
        return "signal_not_active_or_near_setup"
    if direction not in {"long", "short"}:
        return "invalid_signal_direction"
    if not trend_aligned:
        return "signal_not_aligned_with_1h_trend"
    if geometry is None:
        return "invalid_trade_geometry"
    if authoritative_rr is None or authoritative_rr + 1e-9 < minimum_rr:
        return "risk_reward_below_profile_minimum"
    return None


def _setup_quality(signal: dict[str, Any], fallback: float) -> float:
    setup = signal.get("setup_15m")
    if isinstance(setup, dict) and setup.get("score") is not None:
        return _bounded(setup.get("score"))
    return fallback


def _confirmation_quality(signal: dict[str, Any], fallback: float, status: str) -> float:
    confirmation = signal.get("confirmation_5m")
    if isinstance(confirmation, dict) and confirmation.get("score") is not None:
        return _bounded(confirmation.get("score"))
    return fallback if status == "active" else min(fallback, 70.0)


def _volume_quality(signal: dict[str, Any]) -> float:
    components = signal.get("market_score_components")
    if not isinstance(components, dict):
        return _bounded(signal.get("market_score"))
    volume_points = _positive(components.get("volume"))
    if volume_points is None:
        return _bounded(signal.get("market_score"))
    return min(100.0, (volume_points / 15.0) * 100.0)


def _risk_reward_quality(authoritative_rr: float | None, profile: dict[str, float]) -> float:
    if authoritative_rr is None or authoritative_rr <= 0:
        return 0.0
    minimum = profile["minimum_rr"]
    preferred = profile["preferred_rr"]
    if authoritative_rr + 1e-9 < minimum:
        return 0.0
    if authoritative_rr + 1e-9 >= preferred:
        return 100.0
    span = max(preferred - minimum, 1e-9)
    return min(100.0, 60.0 + (((authoritative_rr - minimum) / span) * 40.0))


def _authoritative_geometry(
    *,
    direction: str,
    entry: Any,
    stop_loss: Any,
    take_profit: Any,
) -> dict[str, float] | None:
    entry_value = _positive(entry)
    stop_value = _positive(stop_loss)
    target_value = _positive(take_profit)
    if entry_value is None or stop_value is None or target_value is None:
        return None

    if direction == "long":
        if not stop_value < entry_value < target_value:
            return None
        risk = entry_value - stop_value
        reward = target_value - entry_value
    elif direction == "short":
        if not target_value < entry_value < stop_value:
            return None
        risk = stop_value - entry_value
        reward = entry_value - target_value
    else:
        return None
    if risk <= 0 or reward <= 0:
        return None
    return {
        "risk_distance": risk,
        "reward_distance": reward,
        "risk_reward": reward / risk,
    }


def _normalize_trade_type(value: Any) -> str:
    normalized = str(value or "scalping").lower().strip()
    return normalized if normalized in PROFILE_RULES else "scalping"


def _bounded(value: Any) -> float:
    number = _positive(value)
    if number is None:
        return 0.0
    return min(100.0, number)


def _positive(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not isfinite(number) or number < 0:
        return None
    return number
