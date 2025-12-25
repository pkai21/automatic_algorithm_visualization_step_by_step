import itertools
from core.src.bianchini_algo.algorithm_5 import labelStates

V0 = []
V1_Undivided = []

colorV0 = []
colorV1 = []

doubtsV0 = []
doubtsV1 = []

graphH = None

state = [[], [], 0]  # States of the program including nodes traversed in G, H, order of the state, colorV0, colorV1, graphH

class Graph:
    def __init__(self, V0, V1):
        self.V0 = V0 #cạnh của V_0
        self.V1 = V1 #cạnh của V_1
        self.Node_V0 = [] #đỉnh của V_0 đã đc thêm
        self.Node_V1 = [] #đỉnh của V_1 đã đc thêm

    def add_edge(self, a, b):
        if type(a[0]) is int:
            if not self.V0[a[0]][a[1]]:
                self.V0[a[0]][a[1]] = []
                self.Node_V0.append(a)
            self.V0[a[0]][a[1]].append(b)
        else:
            if not self.V1[a[0][0]][a[0][1]][a[0][2]][a[1]]:
                self.V1[a[0][0]][a[0][1]][a[0][2]][a[1]] = []
                self.Node_V1.append(a)
            self.V1[a[0][0]][a[0][1]][a[0][2]][a[1]].append(b)

    def adj(self, v):
        adj_v = self.V0[v[0]][v[1]] if type(v[0]) is int else self.V1[v[0][0]][v[0][1]][v[0][2]][v[1]]
        return adj_v if adj_v else []
    
    def get_NodeV0(self):
        return self.Node_V0

    def empty(self):
        for i in self.Node_V0:
            self.V0[i[0]][i[1]] = None
        for i in self.Node_V1:
            self.V1[i[0][0]][i[0][1]][i[0][2]][i[1]] = None
        self.Node_V0 = []
        self.Node_V1 = []
        
def MINIMIZENFA(ver, Q, sigma, F, delta):
    global colorV0, colorV1, doubtsV0, doubtsV1, graphH, V0
    
    colorV0 = [[None for _ in range(len(Q))] for _ in range(len(Q))]
    V0 = list(itertools.product(Q, Q))
    V1_Undivided = list(itertools.product(Q, Q, sigma))
    colorV1 = [[[[None for _ in range(2)] for _ in range(len(sigma))] for _ in range(len(Q))] for _ in range(len(Q))]
    graphH = Graph([[None for _ in range(len(Q))] for _ in range(len(Q))],
                   [[[[None for _ in range(2)] for _ in range(len(sigma))] for _ in range(len(Q))] for _ in range(len(Q))])
    
    for u in V0:
        if (F[u[0]] == 1 and F[u[1]] == 0) or (F[u[0]] == 0 and F[u[1]] == 1):
            colorV0[u[0]][u[1]] = 'BLACK'
        elif u[0] == u[1]:
            colorV0[u[0]][u[1]] = 'WHITE'

    for v in V1_Undivided:
        colorV1[v[0]][v[1]][v[2]][0] = None  
        colorV1[v[0]][v[1]][v[2]][1] = None  

    doubtsV0 = [[None for _ in range(len(Q))] for _ in range(len(Q))]
    for u in V0:
        doubtsV0[u[0]][u[1]] = 0

    doubtsV1 = [[[[None for _ in range(2)] for _ in range(len(sigma))] for _ in range(len(Q))] for _ in range(len(Q))]
    for v in V1_Undivided:
        doubtsV1[v[0]][v[1]][v[2]][0] = 0
        doubtsV1[v[0]][v[1]][v[2]][1] = 0
    
    state.append(colorV0)
    state.append(colorV1)
    state.append(graphH)
    
    if ver == 0:  
        for u in V0:
            graphH.empty()
            EQUIVLEFT(u, sigma, delta)

            for v in V0:
                if v in graphH.get_NodeV0():
                    if colorV0[v[0]][v[1]] != 'BLACK':
                        colorV0[v[0]][v[1]] = 'WHITE'
    else:
        print("Use algorithm 5")
        V0_considered = getV0_considered(Q, sigma, F, delta)
        for u in V0_considered:
            graphH.empty()
            EQUIVLEFT(u, sigma, delta)
            for v in V0:
                if v in graphH.get_NodeV0():
                    if colorV0[v[0]][v[1]] != 'BLACK':
                        colorV0[v[0]][v[1]] = 'WHITE'
            
    return GRAPHW()


def RELAX_V0(u):
    state[1].insert(0, u)
    state[2] += 1
    for v in graphH.adj(u):
        state[1].insert(0, v)
        doubtsV1[v[0][0]][v[0][1]][v[0][2]][v[1]] -= 1
        state[2] += 1
        if doubtsV1[v[0][0]][v[0][1]][v[0][2]][v[1]] == 0:
            colorV1[v[0][0]][v[0][1]][v[0][2]][v[1]] = 'BLACK'
            state[2] += 1
            RELAX_V1(v)
    state[1].pop(0)
    state[2] += 1

def RELAX_V1(v):
    state[1].insert(0, v)
    state[2] += 1
    for u in graphH.adj(v):
        state[1].insert(0, v)
        doubtsV0[u[0]][u[1]] -= 1
        state[2] += 1
        if doubtsV0[u[0]][u[1]] == 0:
            colorV0[u[0]][u[1]] = 'BLACK'
            state[2] += 1
            RELAX_V0(u)
    state[1].pop(0)
    state[2] += 1

def EQUIVLEFT(u, sigma, delta):
    state[0].insert(0, u)
    state[2] += 1
    if colorV0[u[0]][u[1]] is not None:
        state[0].pop(0)
        state[2] += 1
        return colorV0[u[0]][u[1]]
    
    colorV0[u[0]][u[1]] = 'GREY'
    doubtsV0[u[0]][u[1]] = 0
    state[2] += 1
    for v in A0(u, sigma, delta):
        if colorV0[u[0]][u[1]] != 'BLACK':  
            col_v = EQUIVRIGHT(v, sigma, delta)
            
            if col_v == 'BLACK':
                colorV0[u[0]][u[1]] = 'BLACK'
                doubtsV0[u[0]][u[1]] = 0
                state[2] += 1
            elif col_v == 'GREY':
                graphH.add_edge(v, u)
                doubtsV0[u[0]][u[1]] = 1
                state[2] += 1

    if colorV0[u[0]][u[1]] == 'GREY':
        if doubtsV0[u[0]][u[1]] == 0:
            colorV0[u[0]][u[1]] = 'WHITE'
            state[2] += 1

    if colorV0[u[0]][u[1]] == 'BLACK': 
        RELAX_V0(u)

    state[0].pop(0)
    state[2] += 1
    return colorV0[u[0]][u[1]]


def EQUIVRIGHT(v,sigma, delta):
    state[0].insert(0, v)
    state[2] += 1
    if colorV1[v[0][0]][v[0][1]][v[0][2]][v[1]] is not None:
        state[0].pop(0)
        state[2] += 1
        return colorV1[v[0][0]][v[0][1]][v[0][2]][v[1]]
    
    colorV1[v[0][0]][v[0][1]][v[0][2]][v[1]] = 'GREY'
    doubtsV1[v[0][0]][v[0][1]][v[0][2]][v[1]] = 0
    state[2] += 1
    
    for u in A1(v, delta):
        if colorV1[v[0][0]][v[0][1]][v[0][2]][v[1]] != 'WHITE':  
            col_u = EQUIVLEFT(u, sigma, delta)
            
            if col_u == 'WHITE':
                colorV1[v[0][0]][v[0][1]][v[0][2]][v[1]] = 'WHITE'
                doubtsV1[v[0][0]][v[0][1]][v[0][2]][v[1]] = 0
                state[2] += 1

            elif col_u == 'GREY':
                graphH.add_edge(u, v)
                doubtsV1[v[0][0]][v[0][1]][v[0][2]][v[1]] += 1
                state[2] += 1

    if colorV1[v[0][0]][v[0][1]][v[0][2]][v[1]] == 'GREY':
        if doubtsV1[v[0][0]][v[0][1]][v[0][2]][v[1]] == 0:
            colorV1[v[0][0]][v[0][1]][v[0][2]][v[1]] = 'BLACK'
            state[2] += 1

    if colorV1[v[0][0]][v[0][1]][v[0][2]][v[1]] == 'BLACK':
        RELAX_V1(v)

    state[0].pop(0)
    state[2] += 1
    return colorV1[v[0][0]][v[0][1]][v[0][2]][v[1]]


# Danh sách V1 được nối từ u  
def A0(u, sigma, delta):
    listV = []
    for x in sigma:
        for p_ in delta[u[0]][x]:
            listV.append(((p_, u[1], x), 1))
        for q_ in delta[u[1]][x]:
            listV.append(((u[0], q_, x), 0))
    return listV


# Danh sách V0 được nối từ v
def A1(v, delta):
    listU = []
    if (v[1] == 0):
        for p_ in delta[v[0][0]][v[0][2]]:
            listU.append((p_, v[0][1]))
    else:
        for q_ in delta[v[0][1]][v[0][2]]:
            listU.append((v[0][0], q_))
    return listU


# Thêm vào đồ thị H: Gốc v đỉnh u
def ADDARC(v, u):
    graphH[v].append(u)
    return graphH


# Lấy danh sách các đỉnh trong đồ thị H
def VERTICESH():
    listVer = []
    for u in graphH:
        if u not in listVer:  # Kiểm tra nếu đỉnh u chưa có trong all_vertices
            listVer.append(u)
        # Thêm các đỉnh cuối vào list
        for v in graphH[u]:
            if v not in listVer:  # Kiểm tra nếu đỉnh v chưa có trong all_vertices
                listVer.append(v)
    return listVer


# Lấy các đỉnh được nối từ đỉnh gốc u
def ADJ(u):
    return graphH[u]


# Gom nhóm các trạng thái: Đưa ra danh sách đỉnh cuối cùng
def GRAPHW():
    graphW = {}
    for u in V0:
        if colorV0[u[0]][u[1]] == 'WHITE':
            if u[0] not in graphW:
                graphW[u[0]] = []
            graphW[u[0]].append(u[1])
    
    graphWe = []
    for group in graphW.values():
        if (group not in graphWe):
            graphWe.append(group)

    return graphWe


# Lấy V0 cần xét khi sử dụng thuật toán 5
def getV0_considered(Q, sigma, F, delta):
    group = labelStates(Q, sigma, F, delta)
    V0_considered = []
    for values in group:
        if len(values) > 1:
            for i in range(len(values)):
                for j in range(len(values)):
                    if i != j:
                        V0_considered.append((values[i], values[j]))
    return V0_considered