class RiskEmpire:
    def __init__(
        self,
        max_risk=80,
        max_manipulation=70,
        min_reality=40,
        max_entropy_hold=85,
        max_drawdown=0.03,
        max_daily_loss=0.05,
        max_position_risk=0.01,
    ):
        self.max_risk = max_risk
        self.max_manipulation = max_manipulation
        self.min_reality = min_reality
        self.max_entropy_hold = max_entropy_hold
        self.max_drawdown = max_drawdown
        self.max_daily_loss = max_daily_loss
        self.max_position_risk = max_position_risk

    def evaluate_market(self, market_event: dict) -> dict:
        risk = float(market_event.get("risk", 0))
        manipulation = float(market_event.get("manipulation_risk", 0))
        reality = float(market_event.get("reality_score", 100))
        entropy = float(market_event.get("entropy", 0))
        drawdown = float(market_event.get("drawdown", 0))
        daily_loss = float(market_event.get("daily_loss", 0))
        position_risk = float(market_event.get("position_risk", 0))

        if risk >= self.max_risk:
            return self._block("risk_above_limit")
        if manipulation >= self.max_manipulation:
            return self._block("manipulation_above_limit")
        if reality <= self.min_reality:
            return self._block("reality_score_too_low")
        if drawdown >= self.max_drawdown:
            return self._block("drawdown_above_limit")
        if daily_loss >= self.max_daily_loss:
            return self._block("daily_loss_limit_reached")
        if position_risk > self.max_position_risk:
            return self._block("position_risk_above_limit")
        if entropy >= self.max_entropy_hold:
            return {"decision":"HOLD","reason":"entropy_extreme_hold","bunker_mode":False}

        return {"decision":"ALLOW","reason":"risk_empire_approved","bunker_mode":False}

    def _block(self, reason):
        return {"decision":"BLOCK","reason":reason,"bunker_mode":True}
