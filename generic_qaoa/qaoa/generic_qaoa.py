from copy import copy

from scipy.optimize import minimize

import dataclasses
from typing import List, Callable
from qiskit.providers import Backend
import numpy as np
from qiskit import Aer, IBMQ, execute

from .qaoa_circuit import QaoaCircuitFactory

SIMULATOR_ENGINE = 'aer_simulator'
REAL_ENGINE = ''
TOKEN = '8e3dad95805407e1f5eaa12f1e35089a95e65638fcd0ed837f4e4f64ccced5471c2a85c124b05552e3804dc6080b8aa70a0b3636723fb047bb30031a4af28776'
IBMQ.save_account(TOKEN, overwrite=True)


class GenericQaoa(object):
    def __init__(self, **qaoa_kwargs):
        self.qaoa_circuit_component = QaoaCircuitComponent(**qaoa_kwargs)

    @property
    def last_result(self):
        return self.qaoa_circuit_component.results[-1]

    @property
    def qaoa_circuit(self):
        return self.qaoa_circuit_component.qaoa_circuit

    def run(self):
        execute_circ = self.qaoa_circuit_component.get_execution_function(self.qaoa_circuit_component.simulate)
        x0 = self.qaoa_circuit_component.get_best_angles()
        result = minimize(fun=execute_circ,
                          x0=x0,
                          method=self.qaoa_circuit_component.minimize_method)
        return result


@dataclasses.dataclass
class QaoaResults:
    selected: str
    counts_histogram: dict


@dataclasses.dataclass
class QaoaCircuitComponent(object):
    _p: int
    _clauses: List
    _qbits: List
    _grid_size: int = 5
    _minimize_method: str = 'COBYLA'
    simulate: bool = True
    _shots: int = 512
    _backend: Backend = None
    _best_angles: List = None
    _circuit: QaoaCircuitFactory.QaoaCircuit = None
    results: List[QaoaResults] = dataclasses.field(default_factory=lambda: [])


    def __post_init__(self):
        if self.simulate:
            self._backend = Aer.get_backend(SIMULATOR_ENGINE)
        else:
            IBMQ.load_account()
            provider = IBMQ.get_provider(group='open')
            from qiskit.providers.ibmq import least_busy

            small_devices = provider.backends(filters=lambda x: x.configuration().n_qubits == len(self._qbits)
                                                                and not x.configuration().simulator)

            self._backend = least_busy(small_devices)
            print(f"chosen backend={self._backend}")
        self._backend.shots = self._shots

    @property
    def backend(self):
        return self._backend

    @property
    def minimize_method(self):
        return self._minimize_method

    def get_best_angles(self):
        if self._best_angles is None:
            self._best_angles = self._find_best_angles()
        return self._best_angles

    @property
    def qaoa_circuit(self):
        self._circuit = QaoaCircuitFactory.create_parameterized_circuit(self._clauses, self._p, len(self._qbits))
        return self._circuit

    def get_execution_function(self, return_also_counts_histogram=False, simulate=False) -> Callable[[List], float]:
        def execution_function(angles: List):
            circuit = QaoaCircuitFactory.create_circuit(self._clauses,
                                                        angles[:len(angles) // 2],
                                                        angles[len(angles) // 2:],
                                                        self._p, len(self._qbits))
            job = self._backend.run(circuit)
            print(f"running circuit on {self._backend}")
            if not simulate:
                job.wait_for_final_state()
            print(f"done")
            counts_histogram = job.result().get_counts()
            selected = max(counts_histogram, key=lambda bitstring: counts_histogram[bitstring])
            energy: float = sum([clause.objective_func(selected) for clause in self._clauses])
            self.results.append(QaoaResults(selected, counts_histogram))
            if return_also_counts_histogram:
                return energy, counts_histogram
            return energy

        return execution_function

    def _find_best_angles(self):
        """
           Grid search on QAOA angles. similar to the grid search from the VQF article.

           Returns:
               best_beta, best_gamma (floats): best values of the beta and gamma found.
       """
        max_step = self._p
        best_betas = np.array([])
        best_gammas = np.array([])
        for step in range(1, max_step + 1):
            self._p = step
            beta, gamma = self._one_step_grid_search(best_betas, best_gammas)
            best_betas = np.append(best_betas, beta)
            best_gammas = np.append(best_gammas, gamma)
        self._p = max_step
        return best_betas, best_gammas

    def _one_step_grid_search(self, _betas, _gammas):
        circuits_and_angles = []
        best_beta = None
        best_gamma = None
        best_counts = 0
        best_energy = np.inf
        beta_range = np.linspace(0, np.pi, self._grid_size)
        gamma_range = np.linspace(0, 2 * np.pi, self._grid_size)
        for beta in beta_range:
            for gamma in gamma_range:
                circuit = copy(self.qaoa_circuit)
                circuit = circuit.bind_parameters({circuit.betas: np.hstack([_betas, beta])})
                circuit = circuit.bind_parameters({circuit.gammas: np.hstack([_gammas, gamma])})
                circuits_and_angles.append((circuit, (beta, gamma)))
        job = execute([circuits for circuits, angles in circuits_and_angles], backend=self.backend)
        print(f"running circuit on {self._backend}")
        job.wait_for_final_state()
        print("done")
        job_result = job.result()
        for idx, (circuit, (beta, gamma)) in enumerate(circuits_and_angles):
            counts_histogram = job_result.get_counts(idx)
            selected = max(counts_histogram, key=lambda bitstring: counts_histogram[bitstring])
            energy: float = sum([clause.objective_func(selected) for clause in self._clauses])
            if energy == best_energy:
                selected_bitstring = max(counts_histogram, key=lambda bitstring: counts_histogram[bitstring])
                if best_counts < counts_histogram[selected_bitstring]:
                    best_counts = counts_histogram[selected_bitstring]
                    best_beta = beta
                    best_gamma = gamma
            if energy < best_energy:
                best_counts = 0
                best_energy = energy
                best_beta = beta
                best_gamma = gamma

        return best_beta, best_gamma
