from collections import defaultdict
import csv
import ast

def set_nfa_config(states, final_states, alphabet, transitions):
    Q = states
    sigma, sigma_labels = convert_sigma(alphabet)
    F = convert_F(final_states, Q)
    
    delta_raw = convert_to_2d_array(transitions, Q, sigma)
    delta = normalize_delta(delta_raw)

    return Q, sigma, sigma_labels, F, delta

def convert_to_2d_array(delta_tuple, Q, sigma):
    print ("Delta tuple:", delta_tuple)
    result = [[[] for _ in range(len(sigma))] for _ in range(len(Q))]
    for curr, next, sym in delta_tuple:
        result[curr][sym].append(next)
    return result

def normalize_delta(delta):
    return [[sorted(cell) for cell in row] for row in delta]

def convert_F(F_val, Q):
    F_res = [0] * len(Q)
    for i in F_val:
        F_res[i] = 1
    return F_res

def convert_sigma(alphabet):
    sigma = list(range(len(alphabet)))
    sigma_labels = dict(enumerate(alphabet))
    return sigma, sigma_labels
 