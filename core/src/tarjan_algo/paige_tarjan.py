import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

sys.path.append(os.path.abspath(os.path.join(current_dir, '..')))

sys.path.append(os.path.abspath(os.path.join(current_dir, '..', '..')))

import networkx as nx
import matplotlib.pyplot as plt
from bispy import compute_maximum_bisimulation, Algorithms
import sys

def create_E(Q,sigma,delta):
    E = [[] for i in sigma] 
    for p in Q:
        for x in sigma:
            for q in delta[p][x]:
                E[x].append((p, q))
    return E

def create_G (Q,sigma, delta):
    E = create_E(Q,sigma,delta)
    graph = [nx.DiGraph(E[i]) for i in sigma] 
    for i in range(len(graph)):
        graph[i].add_nodes_from(Q)

    return graph

def TARJANNFA(Q, sigma, F, delta):
    graph = create_G (Q,sigma, delta)
    initial_partition = [[], []]
    for i in range(len(F)):
        initial_partition[F[i]].append(i)

    for i in sigma:
        initial_partition = compute_maximum_bisimulation(graph[i],
                                                        initial_partition=initial_partition,
                                                        algorithm=Algorithms.PaigeTarjan)

    return sorted([list(item) for item in initial_partition])


