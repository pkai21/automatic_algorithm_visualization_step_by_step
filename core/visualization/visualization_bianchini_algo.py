import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

def visualize(F, delta, sigma, filename):
    G = nx.DiGraph()
    edge_weights = {}  # Lưu trữ trọng số của các cạnh
    
    # Gộp các trọng số của các cạnh trùng nhau
    for p in range(len(delta)):
        for x in sigma:  # x là ký hiệu (0 hoặc 1)
            for q in delta[p][x]:  # q là trạng thái kế tiếp
                if (p, q) in edge_weights:
                    edge_weights[(p, q)].append(str(x))
                else:
                    edge_weights[(p, q)] = [str(x)]
    
    # Thêm các cạnh vào đồ thị
    for (src, dest), weights in edge_weights.items():
        G.add_edge(src, dest, label=", ".join(weights))
    
    edge_labels = {(src, dest): G[src][dest]['label'] for src, dest in G.edges()}
    node_colors = ['red' if F[node] == 1 else 'lightblue' for node in G.nodes()]
    
    # Sử dụng spring_layout với khoảng cách tối ưu
    k_value = 3.0 / np.sqrt(len(G.nodes())) if len(G.nodes()) > 1 else 1.0
    pos = nx.spring_layout(G, k=k_value, seed=42)
    pos = nx.rescale_layout_dict(pos, scale=2.0)  # Đảm bảo các đỉnh không quá gần hoặc quá xa
    
    # Điều chỉnh vị trí vòng lặp
    for node in G.nodes():
        if G.has_edge(node, node):
            pos[node] += np.array([0.05, 0.05])
    
    # Điều chỉnh kích thước khung hình theo mật độ đỉnh
    num_nodes = len(G.nodes())
    fig_width = max(10, min(30, num_nodes * 1.5))
    fig_height = max(8, min(25, num_nodes * 1.2))
    plt.figure(figsize=(fig_width, fig_height))
    
    nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=1200, 
            font_size=14, font_weight='bold', edge_color='blue', 
            arrowsize=25, connectionstyle='arc3,rad=0.3')
    
    # Hiển thị đường truyền
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels,
                                 font_color='black', font_size=12,
                                 connectionstyle='arc3,rad=0.3', label_pos=0.5,
                                 bbox=dict(facecolor='white', edgecolor='none', alpha=0.7))
    
    plt.title(filename)
    plt.savefig(filename) 
    plt.close()
