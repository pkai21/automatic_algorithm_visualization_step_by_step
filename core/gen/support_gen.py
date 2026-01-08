# ------------------------------------------------------------------------------
# Copyright (c) 2026 Phan_Van_Khai
# All rights reserved.
#
# This source code is the proprietary and confidential property of Phan_Van_Khai.
# Unauthorized copying, distribution, or modification of this file, 
# via any medium, is strictly prohibited.
# ------------------------------------------------------------------------------

import sys
def max_in_F (final_states):
    if not final_states:
        return -1
    return max(final_states)

def generate_counter_example_delta(delta_tuple ,curr, next, sym):
    delta_tuple.append((curr, next, sym))
    return delta_tuple 

