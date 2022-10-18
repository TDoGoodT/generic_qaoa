[![PyPI version](https://badge.fury.io/py/generic_qaoa.svg)](https://badge.fury.io/py/generic_qaoa)[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)


# Generic QAOA

Generic QAOA is used for solving any given combinatorial optimization problem by generating a parameterized quantum-circuit and optimizing the parameters  to get the correct solution to the problem.
The quantum-circuit is generated by a set of given clauses, which resemble the problem.


## Getting Started



## Installation

Install generic_qaoa with pip

```bash
  pip install generic_qaoa
```
    
## Usage

We will demonstrate the same problem solved in the qiskit textbook using our generic-qaoa tool 
```python
from generic_qaoa import GenericQaoa
from generic_qaoa.clause import CombinatoricsClause
clauses = [
            CombinatoricsClause([0], [1]),
            CombinatoricsClause([1], [0]),
            CombinatoricsClause([2], [1]),
            CombinatoricsClause([1], [2]),
            CombinatoricsClause([2], [3]),
            CombinatoricsClause([3], [2]),
            CombinatoricsClause([3], [0]),
            CombinatoricsClause([0], [3])
           ]

qaoa = GenericQaoa(_p=2,
                   _clauses=clauses,
                   _qbits=range(4),
                   simulate=True)
circ = qaoa.qaoa_circuit
print(circ)
```

Easy, right? this will result in the circuit, to run it just do
```python
qaoa.run()
```
to see the results run
```python
from generic_qaoa.utils import plot_histogram
plot_histogram(qaoa.last_result.counts_histogram)
print(qaoa.last_result.selected)
```
Another example will be using the mathmatical_clause to factor semiprime numbers:
```python
from generic_qaoa.vqf_helper import create_clauses
from generic_qaoa.clause import MathematicalClause
from generic_qaoa.utils import get_pq_from_selected, plot_histogram
from generic_qaoa import GenericQaoa
m = 69169
p_dict, q_dict, z_dict, clauses = create_clauses(m,true_p_int=263, true_q_int=263)
free_symbols = set().union(*[clause.free_symbols for clause in clauses])
qubit_index_to_symbol = {i: sym for i, sym in enumerate(free_symbols)}
symbol_to_qubit_index = {sym: i for i, sym in qubit_index_to_symbol.items()}
final_clauses = [MathematicalClause((clause * clause).expand(), symbol_to_qubit_index)
for clause in clauses if clause != 0]
```
This will create clauses after the preprocessing steps described in the vqf article and calculate the amout of qubits needed for the circuit
now we can create the circuit and run it as we did before
```python
vqf = GenericQaoa(_p=3,
                  _clauses=final_clauses,
                  _qbits=range(len(free_symbols)),
                  _grid_size=8,
                  simulate=True)

vqf.run()
```
after the run, you can see the results 

```python
plot_histogram(vqf.last_result.counts_histogram)
p, p_dict, q, q_dict = get_pq_from_selected(p_dict, q_dict, vqf.last_result.selected, symbol_to_qubit_index)
print("p,q=", p, q)
```
We found that many times the results are incorrect but are only 1 bitflip in p,q or both away from the right solution. so, we add some "postprocessing" which doesn't significant overhead O(log(m)) 
```python
if p * q != m:
    print("Trying to fix with bit-flip.")
    for i in range(len(p_dict)):
        for j in range(len(q_dict)):
            new_p: int
            if p_dict[i] == 1:
                new_p = p - 2 ** i
            else:
                new_p = p + 2 ** i
            new_q: int
            if q_dict[j] == 1:
                new_q = q - 2 ** j
            else:
                new_q = q + 2 ** j
            if new_q == m or new_p == m:
                break
            if new_p * q == m:
                p = new_p
            elif p * new_q == m:
                q = new_q
            if new_p * new_q == m:
                p = new_p
                q = new_q
            if p * q == m:
                break
        if p * q == m:
            break
```
We were able to run on a simulator and get nice results with small numbers, the numbers from the article and 69169 as shown in the example. 
