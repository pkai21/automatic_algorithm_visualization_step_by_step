from collections import defaultdict
import csv
import ast

# Global variables to store the current NFA configuration
Q = []
F = []
sigma = []
delta = []

def set_nfa_config(states, final_states, alphabet, transitions):
    """
    Set the global NFA configuration.
    """
    global Q, F, sigma, delta
    
    Q = states
    sigma = alphabet
    F = convert_F(final_states, Q)
    delta = convert_to_2d_array(transitions, Q, sigma)

def convert_to_2d_array(delta_tuple, Q, sigma):
    result = [[[] for _ in range(len(sigma))] for _ in range(len(Q))]

    for curr, next, sym in delta_tuple:
        result[curr][sym].append(next)

    return result

def normalize_delta(delta):
    return [[sorted(cell) for cell in row] for row in delta]

def convert_F(F_val, Q):
    F = [0] * len(Q)
    for i in F_val:
        F[i] = 1
    return F