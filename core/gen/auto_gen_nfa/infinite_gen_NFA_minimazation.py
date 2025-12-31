import random

def infinite_generate_delta(num_states, num_transitions, sigma):
    delta = []
    used = [[[] for _ in range(num_states)] for _ in range(num_states)]

    def add_edge(edge):
        if edge[1] not in used[edge[0]][edge[2]]:
            delta.append(edge)
            used[edge[0]][edge[2]].append(edge[1])
            return True
        return False

    # Buoc 1: Chuoi q0 -> q1 -> ... -> q(n-1)
    for i in range(num_states - 1):
        sym = random.choice(sigma)
        add_edge((i, i + 1, sym))
    
    # Buoc 2: Them nhanh nguoc de dat NFA (tranh a = 0)
    candidates = [edge for edge in delta if edge[0] > 0]
    edge = random.choice(candidates)
    possibles = [c for c in range(0, edge[0])]
    c = random.choice(possibles)
    add_edge((edge[0], c, edge[2]))

    # Buoc 3: Them random de du canh
    remaining = num_transitions - len(delta)
    while remaining > 0:
        s = random.randint(1, num_states)  # s > 0
        ns = random.randint(0, s-1) # ns < s
        sym = random.choice(sigma)
        if add_edge((s, ns, sym)):
            remaining -= 1

    return delta
