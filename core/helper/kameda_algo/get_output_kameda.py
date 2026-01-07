def build_shift_dict(n, x):
    return {i: (i + x) % n for i in range(n)}
    
def get_key(d,val):
    key = next(k for k, v in d.items() if v == val)
    return key

def get_kameda_out(min_nfa):
    k = len(min_nfa.states)
    x = min_nfa.start_states.pop()
    anphabet = min_nfa.alphabet
    dict_states = build_shift_dict(k, x)
    sigma_labels = {i: int(v) for i, v in enumerate(sorted(anphabet, key=int))}
    Q = [i for i in range(k)]
    sigma = [i for i in range(len(anphabet))]
    F = [0]* k
    while len(min_nfa.accept_states) > 0:
        val = min_nfa.accept_states.pop()
        state = get_key(dict_states, val)
        F[state] = 1
    print(dict_states)
    print (sigma_labels)
    delta = [[[] for _ in range(len(sigma))] for _ in range(len(Q))]
    for src, trans in min_nfa.transitions.items():
        for char, dests in trans.items():
            while len(dests) > 0:
                delta[get_key(dict_states, src)][get_key(sigma_labels, int(char))].append(get_key(dict_states,dests.pop()))
    
    return Q, sigma, sigma_labels, F, delta