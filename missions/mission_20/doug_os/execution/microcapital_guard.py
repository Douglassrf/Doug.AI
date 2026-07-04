class MicrocapitalGuard:
    def __init__(self, max_trade_risk=0.005, max_daily_loss=0.01, leverage_allowed=False):
        self.max_trade_risk = max_trade_risk
        self.max_daily_loss = max_daily_loss
        self.leverage_allowed = leverage_allowed

    def validate(self, trade: dict) -> dict:
        if trade.get("leverage", 1) > 1 and not self.leverage_allowed:
            return {"approved": False, "reason": "leverage_not_allowed"}
        if float(trade.get("risk", 1)) > self.max_trade_risk:
            return {"approved": False, "reason": "trade_risk_above_microcapital_limit"}
        if float(trade.get("daily_loss", 0)) > self.max_daily_loss:
            return {"approved": False, "reason": "daily_loss_limit"}
        return {"approved": True, "reason": "microcapital_guard_approved"}
