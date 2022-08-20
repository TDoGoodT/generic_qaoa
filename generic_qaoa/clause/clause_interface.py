from abc import abstractmethod
from sympy import Symbol


class Clause:
    @property
    @abstractmethod
    def only_z_clause(self) -> Symbol:
        pass

    def objective_func(self, selected_bitstring) -> float:
        subs_map = {f"z{idx}": 1 if value == '1' else -1 for idx, value in enumerate(reversed(selected_bitstring))}
        obj = float(self.only_z_clause.subs(subs_map))
        return obj
