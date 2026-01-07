
from core.src.kameda_algo.algorithm_kameda import NFA

def set_kameda_in(sigma,sigma_labels,F,delta):
    nfa = NFA()
    for i in range (len(delta)):
        for j in range(len(sigma)):
            if len(delta[i][j]) > 0:
                for val in delta[i][j]:
                    nfa.add_transition(str(i),str(sigma_labels[j]), str(val))
        
    nfa.start_states = {"0"}
    F_val = []
    for i, val in enumerate(F):
        if val == 1:
            F_val.append(i)

    nfa.accept_states = {str(x) for x in F_val}

    return nfa