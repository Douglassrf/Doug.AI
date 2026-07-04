class TestnetExecutor:
    def __init__(self):
        self.orders = {}
        self.next_id = 1

    def place_order(self, side: str, symbol: str, qty: float):
        oid = str(self.next_id)
        self.next_id += 1
        self.orders[oid] = {"id":oid,"side":side,"symbol":symbol,"qty":qty,"status":"OPEN","real_money":False}
        return self.orders[oid]

    def cancel_order(self, order_id: str):
        if order_id in self.orders:
            self.orders[order_id]["status"] = "CANCELED"
            return self.orders[order_id]
        return {"error":"order_not_found"}
