def newNFA(miniNFA,Q, F, sigma, delta):
    new_Q = []
    state_labels= {} 
    for qs in miniNFA:
        new_Q.append(qs[0])
        state_labels[qs[0]] = qs  
    
    lookup_map = {val: key for key, lst in state_labels.items() for val in lst}

    new_delta = [[[] for _ in range(len(sigma))] for _ in range(len(Q))]

    for i in range (len(delta)):
        for j in range (len(sigma)):
            for yi in delta[i][j]:
                x = lookup_map[i]
                y = lookup_map[yi]
                if y not in new_delta[x][j]:
                        new_delta[x][j].append(y)

    print (state_labels)
    return new_Q, F, new_delta, state_labels
