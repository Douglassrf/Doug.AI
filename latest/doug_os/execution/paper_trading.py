class PaperTradingEngine:
    def __init__(self, balance=10000.0):
        self.balance = balance
        self.positions = []
        self.history = []

    def apply_decision(self, decision: dict, price: float):
        if decision.get("decision") not in ("BUY","SELL"):
            record = {"action":"HOLD","price":price,"balance":self.balance}
        else:
            record = {"action":decision["decision"],"price":price,"size":0.01,"balance":self.balance}
            self.positions.append(record)
        self.history.append(record)
        return record

    def daily_report(self):
        return {"balance": self.balance, "positions": len(self.positions), "events": len(self.history)}
