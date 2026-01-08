# ------------------------------------------------------------------------------
# Copyright (c) 2026 Phan_Van_Khai
# All rights reserved.
#
# This source code is the proprietary and confidential property of Phan_Van_Khai.
# Unauthorized copying, distribution, or modification of this file, 
# via any medium, is strictly prohibited.
# ------------------------------------------------------------------------------

import sys
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import io
from PIL import Image

def visualize_couterexample(Q, F, delta, sigma, sigma_labels, state_labels={}, return_fig=False):
    all_states = set(Q)
    if not all_states:
        return None
    
    states = sorted(all_states)
    existing_set = set(states)
    
    G = nx.DiGraph()
    G.add_nodes_from(states)

    edge_weights = {}
    for p in range(len(delta)):
        for x in sigma:
            for q in delta[p][x]:
                key = (p, q)
                if key in edge_weights:
                    edge_weights[key].append(str(sigma_labels[x]))
                else:
                    edge_weights[key] = [str(sigma_labels[x])]
    
    for (src, dest), weights in edge_weights.items():
        if src in existing_set and dest in existing_set:
            G.add_edge(src, dest, label=", ".join(weights))
    
    node_colors = [
                    'red' if F[node] == 1 
                    else 'green' if node == 0 
                    else 'lightblue' 
                    for node in G.nodes()
                ]
    
    if state_labels:
        custom_labels = {}
        for node in states:
            orig_states = state_labels.get(node, [node])
            custom_labels[node] = ", ".join(map(str, sorted(orig_states)))
    else:
        custom_labels = {node: str(node) for node in states}

    base_size = 2200          
    size_per_char = 900       
    
    node_sizes_list = []
    node_sizes_map = {} 
    
    for node in states:
        label_len = len(custom_labels[node])
        size = base_size + (label_len - 1) * size_per_char
        node_sizes_list.append(size)
        node_sizes_map[node] = size
    
    # ===============================================
    #  ARRAY
    # ===============================================
    pos = {}
    dx = 6.0  
    dy = 5.0  

    row1_nodes = []
    remaining_nodes = []
    
    cutoff_index = len(states) 
    
    for i, node in enumerate(states):
        is_final = False
        try:
             if isinstance(F, dict): is_final = (F.get(node) == 1)
             else: is_final = (F[node] == 1)
        except: pass
        
        if is_final:
            cutoff_index = i + 1
            break
            
    row1_nodes = states[:cutoff_index]
    remaining_nodes = states[cutoff_index:]

    len_row1 = len(row1_nodes)
    len_sub_row = max(1, len_row1 - 2) 

    for i, node in enumerate(row1_nodes):
        pos[node] = (i * dx, 0)

    current_idx = 0
    row_count = 1 
    
    while current_idx < len(remaining_nodes):
        chunk = remaining_nodes[current_idx : current_idx + len_sub_row]
        
        for k, node in enumerate(chunk):
            x_pos = (1 + k) * dx
            y_pos = -row_count * dy
            pos[node] = (x_pos, y_pos)
            
        current_idx += len_sub_row
        row_count += 1

    total_rows = row_count

    # ===============================================
    # GRAPH
    # ===============================================
    fig = plt.figure(figsize=(20, 12)) 

    self_loops = [(u, v) for u, v in G.edges() if u == v]
    regular_edges = [(u, v) for u, v in G.edges() if u != v]
    
    edge_labels = {(u, v): d['label'] for u, v, d in G.edges(data=True)}
    regular_edge_labels = {k: v for k, v in edge_labels.items() if k[0] != k[1]}

    nx.draw_networkx_edges(G, pos,
                           edgelist=regular_edges,
                           node_size=node_sizes_list, 
                           edge_color='blue',
                           arrowsize=35,
                           connectionstyle="arc3,rad=0.25", 
                           arrowstyle='->')
    
    nx.draw_networkx_edge_labels(G, pos,
                                 edge_labels=regular_edge_labels,
                                 font_color='darkgreen',
                                 font_size=24,
                                 label_pos=0.5,
                                 bbox=dict(facecolor='white', edgecolor='none', alpha=0.9),
                                 connectionstyle="arc3,rad=0.25")

    max_y_reached = 0
    
    for u, v in self_loops:
        if u not in pos: continue 
        x, y = pos[u]
        
        current_size = node_sizes_map[u]
        scale = np.sqrt(current_size / base_size)
        arm_len = 70 * scale

        loop_style = f"arc,angleA=115,angleB=65,armA={arm_len},armB={arm_len},rad=30"
        
        nx.draw_networkx_edges(G, pos,
                               edgelist=[(u, v)],
                               node_size=node_sizes_map[u],
                               edge_color='blue',
                               arrowsize=35,
                               connectionstyle=loop_style,
                               arrowstyle='->')
        
        lbl = edge_labels.get((u, v))
        if lbl:
            base_offset = 1.5
            current_offset = base_offset * scale
            
            label_x = x 
            label_y = y + current_offset 
            
            plt.text(label_x, label_y, lbl,
                     size=24, color='darkgreen',
                     ha='center', va='center',
                     bbox=dict(facecolor='white', edgecolor='none', alpha=0.9),
                     zorder=10)

            if label_y > max_y_reached:
                max_y_reached = label_y

    nx.draw_networkx_nodes(G, pos,
                           node_color=node_colors,
                           node_size=node_sizes_list)

    nx.draw_networkx_labels(G, pos,
                            labels=custom_labels,
                            font_size=26, 
                            font_weight='bold')
    
    plt.axis('off')

    all_x = [p[0] for p in pos.values()]
    all_y = [p[1] for p in pos.values()]
    
    if all_x:
        margin_x = 3.0
        margin_y = 3.0
        plt.xlim(min(all_x) - margin_x, max(all_x) + margin_x)
        plt.ylim(min(all_y) - margin_y, max(max_y_reached, max(all_y)) + margin_y)
    
    plt.tight_layout()

    if return_fig:
        canvas = FigureCanvasAgg(fig)
        buf = io.BytesIO()
        canvas.print_figure(buf, format='png', bbox_inches='tight', pad_inches=0.1)
        buf.seek(0)
        pil_image = Image.open(buf)
        plt.close(fig)
        return pil_image.copy() 
    else:
        plt.close(fig)
        return None