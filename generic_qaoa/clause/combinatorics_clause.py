from sympy import symbols, Symbol

from .clause_interface import Clause
from typing import List


def _parse_literals_into_hamiltonian(one_literals, zero_literals) -> Symbol:
    for l in one_literals:
        assert l not in zero_literals
    one_symbols = [(1 - symbols('z' + str(l))) for l in one_literals]
    zero_symbols = [(1 + symbols('z' + str(l))) for l in zero_literals]
    new_clause = 1
    for sym in one_symbols:
        new_clause *= sym
    for sym in zero_symbols:
        new_clause *= sym
    return new_clause.expand()


class CombinatoricsClause(Clause):
    def __init__(self, one_literals: List[int], zero_literals: List[int]):
        self._hamiltonian = _parse_literals_into_hamiltonian(one_literals, zero_literals)

    @property
    def only_z_clause(self):
        return self._hamiltonian

