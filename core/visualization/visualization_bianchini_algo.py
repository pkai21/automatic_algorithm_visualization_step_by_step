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

def visualize(Q, F, delta, sigma, sigma_labels, title_text, max_states, state_labels={}, return_fig=False):
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
    #  ELIP
    # ===============================================
    radius_x = 9.0  
    radius_y = 5.5  
    
    start_angle = np.pi
    angles = start_angle + np.linspace(0, 2 * np.pi, max_states, endpoint=False)
    
    fixed_pos = {}
    for i in range(max_states):
        x = radius_x * np.cos(angles[i])
        y = radius_y * np.sin(angles[i])
        fixed_pos[i] = (x, y)
    
    pos = {node: fixed_pos[node] for node in states}
    
    # ===============================================
    # 3. GRAPH
    # ===============================================
    fig = plt.figure(figsize=(20, 12)) 
    for i in range(max_states):
        center = fixed_pos[i]
        circle_radius = 1.8 
        circle = plt.Circle(center, circle_radius, color='gray', fill=False, alpha=0.15, lw=2)
        plt.gca().add_patch(circle)

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
                                 font_size=26,
                                 label_pos=0.5,
                                 bbox=dict(facecolor='white', edgecolor='none', alpha=0.9),
                                 connectionstyle="arc3,rad=0.25")

    # DYNAMIC SCALING)
    max_y_reached = radius_y 

    for u, v in self_loops:
        x, y = pos[u]
        
        current_size = node_sizes_map[u]
        scale = np.sqrt(current_size / base_size)
        
        arm_len = 70 * scale
        
        theta = np.pi / 2 
        deg = 90
        angleA = deg + 25 
        angleB = deg - 25
        
        loop_style = f"arc,angleA={angleA},angleB={angleB},armA={arm_len},armB={arm_len},rad=30"
        
        nx.draw_networkx_edges(G, pos,
                               edgelist=[(u, v)],
                               node_size=node_sizes_map[u],
                               edge_color='blue',
                               arrowsize=35,
                               connectionstyle=loop_style,
                               arrowstyle='->')
        
        lbl = edge_labels.get((u, v))
        if lbl:
            base_offset = 2
            current_offset = base_offset * scale
            
            label_x = x 
            label_y = y + current_offset 
            
            plt.text(label_x, label_y, lbl,
                     size=26, color='darkgreen',
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

    required_top_margin = max_y_reached + 2.0
    
    default_margin_y = radius_y + 5.0
    
    final_max_y = max(default_margin_y, required_top_margin)
    final_max_x = radius_x + 5.0
    
    plt.xlim(-final_max_x, final_max_x)
    plt.ylim(-(radius_y + 2.0), final_max_y)
    
    plt.margins(0)
    plt.tight_layout()

    if return_fig:
        canvas = FigureCanvasAgg(fig)
        buf = io.BytesIO()
        canvas.print_figure(buf, format='png', bbox_inches='tight', pad_inches=0.05)
        buf.seek(0)
        pil_image = Image.open(buf)
        plt.close(fig)
        return pil_image.copy() 
    else:
        plt.close(fig)
        return None