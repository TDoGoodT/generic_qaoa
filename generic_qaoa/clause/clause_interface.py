from abc import abstractmethod

class Clause:
    @property
    @abstractmethod
    def clause(self):
        pass

    def objective(self, selected_bitstring) -> float:
        subs_map = {f"z{idx}": 1 if value == '1' else -1 for idx, value in enumerate(reversed(selected_bitstring))}
        obj = float(self.clause.subs(subs_map))
        return obj
