import random

def modify_delta(Q, delta, F, a, b):
    
    n = max(Q) + 1  
    new_states = list(range(n, n + b))  
    modified_delta = set(delta)  
    Q_new = Q[:]
    F_new = F[:]
    
    for new_state in new_states:
        for trans in delta:
            q1, q2, sym = trans
            if q1 == a and q2 == a:
                modified_delta.add((new_state, new_state, sym))
            elif q1 == a:
                modified_delta.add((new_state, q2, sym))
            elif q2 == a:
                modified_delta.add((q1, new_state, sym))
    
    Q_new.extend(new_states)
    
    if a in F:
        F_new.extend(new_states)
    
    return Q_new, modified_delta, F_new

def gene_NFA(Q, delta, F):
    Q_result = Q[:]
    delta_result = delta[:]
    F_result = F[:]
    num_state_repeat = random.randint(1, len(Q))
    for _ in range(num_state_repeat):
        a =  random.choice(Q)
        b = random.randint(1, 3)
        Q_result,delta_result,F_result = modify_delta(Q_result,delta_result,F_result,a,b)
    return Q_result, delta_result, F_result

