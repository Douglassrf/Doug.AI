class DarwinEngine:
    def __init__(self):
        self.candidates = []

    def add_strategy(self, name: str, score: float = 0.0):
        self.candidates.append({"name": name, "score": score, "status": "paper_only"})

    def evolve(self):
        self.candidates.sort(key=lambda x: x["score"], reverse=True)
        survivors = self.candidates[:3]
        discarded = self.candidates[3:]
        return {"survivors": survivors, "discarded": discarded, "production_changed": False}
