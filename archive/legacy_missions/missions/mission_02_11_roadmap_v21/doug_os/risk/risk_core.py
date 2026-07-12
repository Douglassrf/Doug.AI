class RiskCore:
    def __init__(
        self,
        max_risk=80,
        max_manipulation=70,
        min_reality=40,
        max_entropy_hold=85,
        max_drawdown=0.03,
        max_daily_loss=0.05,
        max_weekly_loss=0.10,
    ):
        self.max_risk = max_risk
        self.max_manipulation = max_manipulation
        self.min_reality = min_reality
        self.max_entropy_hold = max_entropy_hold
        self.max_drawdown = max_drawdown
        self.max_daily_loss = max_daily_loss
        self.max_weekly_loss = max_weekly_loss

    def evaluate(self, market_event: dict) -> dict:
        risk = float(market_event.get("risk", 0))
        manipulation = float(market_event.get("manipulation_risk", 0))
        reality = float(market_event.get("reality_score", 100))
        entropy = float(market_event.get("entropy", 0))
        drawdown = float(market_event.get("drawdown", 0))
        daily_loss = float(market_event.get("daily_loss", 0))
        weekly_loss = float(market_event.get("weekly_loss", 0))

        if risk >= self.max_risk:
            return {"decision": "BLOCK", "reason": "risk_above_limit", "bunker_mode": True}
        if manipulation >= self.max_manipulation:
            return {"decision": "BLOCK", "reason": "manipulation_above_limit", "bunker_mode": True}
        if reality <= self.min_reality:
            return {"decision": "BLOCK", "reason": "reality_score_too_low", "bunker_mode": True}
        if drawdown >= self.max_drawdown:
            return {"decision": "BLOCK", "reason": "drawdown_above_limit", "bunker_mode": True}
        if daily_loss >= self.max_daily_loss:
            return {"decision": "BLOCK", "reason": "daily_limit_reached", "bunker_mode": True}
        if weekly_loss >= self.max_weekly_loss:
            return {"decision": "BLOCK", "reason": "weekly_limit_reached", "bunker_mode": True}
        if entropy >= self.max_entropy_hold:
            return {"decision": "HOLD", "reason": "entropy_extreme_hold", "bunker_mode": False}

        return {"decision": "ALLOW", "reason": "risk_core_approved", "bunker_mode": False}
