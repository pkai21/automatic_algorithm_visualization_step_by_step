import math

succ = []
dist = []
B = []
Buckets = [[]]
Q5 = []
signature = []

def labelStates(Q, sigma, F, delta):
    tau = reverse(Q, sigma, delta)
    BFS(Q, tau, F)
    global succ
    succ = compute_succesor(Q, sigma, F, delta)
    return compute_buckets(Q, F, delta)

def SIG_sort(a):
    return signature[a]


def dist_sort(a):
    return dist[a]


def compute_buckets(Q, F, delta):
    global B, signature, Buckets, Q5
    B = [0] * len(Q)
    signature = [0] * len(Q)
    i = 0
    Buckets = [[]]
    for j in range(len(F)):
        if F[j]:
            B[j] = 1
            i += 1
            Buckets[0].append(j)
    Next, d = 2, 1
    Q5 = sorted(Q, key=dist_sort)
    
    while i < len(Q5) and dist[Q5[i]] < math.inf:
        j = i
        while j + 1 < len(Q5) and dist[Q5[j + 1]] == d:
            j += 1
            SIG(Q5[j], delta)
        Q5[i:j + 1] = sorted(Q5[i:j + 1], key=SIG_sort)
        Next = split_interval(Next, i, j)
        i, d = j + 1, d + 1
    if i < len(Q5) - 1:
        Buckets.append([Q5[j] for j in range(i, len(Q5))])
    return Buckets


def split_interval(Next, i, j):
    global B, Buckets, Q5
    b = []
    sig = signature[Q5[i]]
    for k in range(i, j + 1):
        curr = signature[Q5[k]]
        if curr == sig:
            b.append(Q5[k])
        else:
            sig = curr
            Buckets.append(b)
            b = [Q5[k]]
            Next += 1
        B[Q5[k]] = Next
    Buckets.append(b)
    return Next + 1


def reverse(Q, sigma, delta):
    tau = [[] for i in Q]  
    for p in Q:
        for x in sigma:
            for q in delta[p][x]:
                tau[q].append(p)
    return tau


def BFS(Q, tau, F):
    queue = [i for i in range(len(F)) if F[i]]
    sz = len(Q)
    colored = [0] * sz
    global dist
    dist = [math.inf] * sz

    for i in queue:
        dist[i] = 0
        colored[i] = 1

    while queue:
        a = queue.pop(0)
        for i in tau[a]:
            if colored[i] == 0:
                queue.append(i)
                colored[i] = 1
                dist[i] = dist[a] + 1


def compute_succesor(Q, sigma, F, delta):
    succ = [0] * len(Q)
    for i in F:
        succ[i] = (0, i)
    Q_temp = [i for i in Q if dist[i] < math.inf]
    for p in Q_temp:
        d = dist[p]
        found = False
        for x in sigma:
            if not found:
                for p_temp in delta[p][x]:
                    if dist[p_temp] + 1 == d:
                        succ[p] = x
                        found = True
    return succ
    

def SIG(p, delta):
    return (succ[p], B[min(delta[p][succ[p]], key=dist_sort)])

