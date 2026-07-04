class RiskEmpire:
    """Evaluate high‑level risk conditions and block trading if limits are exceeded.

    When instantiated without explicit parameters, defaults are taken from
    :mod:`doug_os.config.RISK_EMPIRE_DEFAULTS`.  This allows centralised
    tuning of risk tolerances.  Pass any argument explicitly to override
    the corresponding default.
    """

    def __init__(
        self,
        max_risk: float | None = None,
        max_manipulation: float | None = None,
        min_reality: float | None = None,
        max_entropy_hold: float | None = None,
        max_drawdown: float | None = None,
        max_daily_loss: float | None = None,
        max_position_risk: float | None = None,
    ):
        # Import defaults lazily to avoid circular dependency at import time
        from doug_os.config import RISK_EMPIRE_DEFAULTS

        defaults = RISK_EMPIRE_DEFAULTS
        self.max_risk = max_risk if max_risk is not None else defaults["max_risk"]
        self.max_manipulation = (
            max_manipulation if max_manipulation is not None else defaults["max_manipulation"]
        )
        self.min_reality = min_reality if min_reality is not None else defaults["min_reality"]
        self.max_entropy_hold = (
            max_entropy_hold if max_entropy_hold is not None else defaults["max_entropy_hold"]
        )
        self.max_drawdown = max_drawdown if max_drawdown is not None else defaults["max_drawdown"]
        self.max_daily_loss = (
            max_daily_loss if max_daily_loss is not None else defaults["max_daily_loss"]
        )
        self.max_position_risk = (
            max_position_risk if max_position_risk is not None else defaults["max_position_risk"]
        )

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
