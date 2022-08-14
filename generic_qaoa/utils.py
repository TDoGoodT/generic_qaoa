from sympy import Symbol
from qiskit.visualization import plot_histogram

def get_pq_from_selected(p_dict, q_dict, selected ,symbol_to_qubit_index):
    for index, value in p_dict.items():
        if isinstance(value, int):
            continue
        for term in value.free_symbols:
            p_dict[index] = p_dict[index].subs(term, selected[symbol_to_qubit_index[term]])
    for index, value in q_dict.items():
        if isinstance(value, int):
            continue
        for term in value.free_symbols:
            q_dict[index] = q_dict[index].subs(term, selected[symbol_to_qubit_index[term]])
    q_str = [str(v) for v in q_dict.values()]
    q_str.reverse()
    q = int(''.join(q_str), 2)
    p_str = [str(v) for v in p_dict.values()]
    p_str.reverse()
    p = int(''.join(p_str), 2)
    return p, p_dict, q, q_dict

def z_to_qubit_index(z_sym: Symbol):
    z_str = str(z_sym)
    return int(z_str[1:])
