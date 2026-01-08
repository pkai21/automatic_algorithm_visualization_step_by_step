# ------------------------------------------------------------------------------
# Copyright (c) 2026 Phan_Van_Khai
# All rights reserved.
#
# This source code is the proprietary and confidential property of Phan_Van_Khai.
# Unauthorized copying, distribution, or modification of this file, 
# via any medium, is strictly prohibited.
# ------------------------------------------------------------------------------

import sys
def get_nfa_config(Q, sigma, sigma_labels, F, delta):
    delta_raw = re_normalize_delta(delta)
    transitions = re_convert_to_2d_array(delta_raw)
    final_states = re_convert_F(F)  
    alphabet = re_convert_sigma(sigma, sigma_labels)  
    states = Q

    return states, final_states, alphabet, transitions


def re_convert_to_2d_array(result):
    delta_tuple = []
    for curr, row in enumerate(result):
        for sym, next_states in enumerate(row):
            for next_state in next_states:
                delta_tuple.append((curr, next_state, sym))
    return delta_tuple

def re_normalize_delta(delta):
    return delta

def re_convert_F(F_res):
    F_val = []
    for i, val in enumerate(F_res):
        if val == 1:
            F_val.append(i)
    return F_val

def re_convert_sigma(sigma, sigma_labels):
    alphabet = []
    sorted_sigma = sorted(sigma)
    
    for idx in sorted_sigma:
        if idx in sigma_labels:
            alphabet.append(sigma_labels[idx])
            
    return alphabet