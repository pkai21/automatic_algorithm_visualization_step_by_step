def max_in_F (final_states):
    if not final_states:
        return -1
    return max(final_states)

def generate_counter_example_delta(delta_tuple ,curr, next, sym):
    delta_tuple.append((curr, next, sym))
    return delta_tuple 

