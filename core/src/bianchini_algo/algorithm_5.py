import math
import core.helper.bianchini_algo.input_config_bianchini as input_config_bianchini

succ = []
dist = []
B = []
Buckets = [[]]
Q5 = []
signature = []

def labelStates():
    tau = reverse(input_config_bianchini.delta)
    BFS(input_config_bianchini.Q, tau, input_config_bianchini.F)
    global succ
    succ = compute_succesor()
    return compute_buckets()


def SIG_sort(a):
    return signature[a]


def dist_sort(a):
    return dist[a]


def compute_buckets():
    global B, signature, Buckets, Q5
    B = [0] * len(input_config_bianchini.Q)
    signature = [0] * len(input_config_bianchini.Q)
    i = 0
    Buckets = [[]]
    for j in range(len(input_config_bianchini.F)):
        if input_config_bianchini.F[j]:
            B[j] = 1
            i += 1
            Buckets[0].append(j)
    Next, d = 2, 1
    Q5 = sorted(input_config_bianchini.Q, key=dist_sort)
    
    while i < len(Q5) and dist[Q5[i]] < math.inf:
        j = i
        while j + 1 < len(Q5) and dist[Q5[j + 1]] == d:
            j += 1
            SIG(Q5[j])
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


def reverse(delta):
    tau = [[] for i in input_config_bianchini.Q]  # adjacent list
    for p in input_config_bianchini.Q:
        for x in input_config_bianchini.sigma:
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


def compute_succesor():
    succ = [0] * len(input_config_bianchini.Q)
    for i in input_config_bianchini.F:
        succ[i] = (0, i)
    Q_temp = [i for i in input_config_bianchini.Q if dist[i] < math.inf]
    for p in Q_temp:
        d = dist[p]
        found = False
        for x in input_config_bianchini.sigma:
            if not found:
                for p_temp in input_config_bianchini.delta[p][x]:
                    if dist[p_temp] + 1 == d:
                        succ[p] = x
                        found = True
    return succ
    

def SIG(p):
    return (succ[p], B[min(input_config_bianchini.delta[p][succ[p]], key=dist_sort)])

