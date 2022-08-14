from sympy import Symbol

from .clause_interface import Clause


def _parse_mathmatical_caluse_into_hamiltonian(clauses, symbol_to_qubit: dict):
    new_clauses = clauses.expand()
    for sym in new_clauses.free_symbols:
        new_clauses = new_clauses.subs(sym, f"z{symbol_to_qubit[sym]}").expand()
    for sym in new_clauses.free_symbols:
        new_sym = (1 / 2) * (1 - sym)
        new_clauses = new_clauses.subs(sym, new_sym).expand()
    for sym in new_clauses.free_symbols:
        new_clauses = new_clauses.subs(sym ** 2, 1).expand()

    return new_clauses.expand()


class MathematicalClause(Clause):
    def __init__(self, clause: Symbol, symbol_to_qubit: dict):
        """
        In the Clause constructor we must translate the clauses to Hamiltonian
        """
        self._hamiltonian: Symbol = _parse_mathmatical_caluse_into_hamiltonian(clause, symbol_to_qubit)

    @property
    def only_z_clause(self) -> Symbol:
        return self._hamiltonian
