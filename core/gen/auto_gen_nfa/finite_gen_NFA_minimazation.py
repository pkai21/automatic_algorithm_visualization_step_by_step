import random

def finite_generate_delta(num_states, num_transitions, sigma):
    delta = []
    used = [[[] for _ in range(num_states)] for _ in range(num_states)]

    def add_edge(edge):
        if edge[1] not in used[edge[0]][edge[2]]:
            delta.append(edge)
            used[edge[0]][edge[2]].append(edge[1])
            return True
        return False

    # Bước 1: Chuỗi q0 → q1 → ... → q(n-1)
    for i in range(num_states - 1):
        sym = random.choice(sigma)
        add_edge((i, i + 1, sym))

    # Bước 2: Thêm phân nhánh NFA (tránh a = n-2)
    candidates = [edge for edge in delta if edge[0] < num_states - 2]
    a, b, x = random.choice(candidates)
    possibles = [c for c in range(a + 1, num_states) if c != b]
    c = random.choice(possibles)
    add_edge((a, c, x))

    # Bước 3: Thêm random đến đủ số cạnh
    remaining = num_transitions - len(delta)
    while remaining > 0:
        s = random.randint(0, num_states - 2)  # s < num_states - 1
        ns = random.randint(s + 1, num_states - 1)  # ns > s
        sym = random.choice(sigma)
        if add_edge((s, ns, sym)):
            remaining -= 1

    return delta


