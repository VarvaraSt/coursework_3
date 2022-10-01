#import plotly.graph_objects as go
import networkx as nx
#import plotly
import matplotlib.pyplot as plt

def save_as_png(V, E, path = "filename.png"):
    G = nx.Graph()
    G.add_nodes_from(V)
    G.add_edges_from(E)
    plt.clf()
    nx.draw(G, pos=nx.circular_layout(G), with_labels = True, node_color = "#fdd03b", 
            edge_color = "#00202e", font_color = "#00202e", node_size = 400, width = 2, font_size = 14)
    plt.savefig(path)
    
def save_as_png_flows(V, E, dict_of_flows, path = "result.png"):
    G = nx.Graph()
    G.add_nodes_from(V)
    G.add_edges_from(E)
    plt.clf()
    nx.draw(G, pos=nx.circular_layout(G), with_labels = True, node_color = "#fdd03b", edge_color = "#00202e", 
            font_color = "#00202e", node_size = 400, width = 2, font_size = 14, style = 'dashed')
    G = nx.DiGraph()
    G.add_nodes_from(V)
    G.add_edges_from(dict_of_flows)
    nx.draw(G, pos=nx.circular_layout(G), with_labels = True, node_color = "#fdd03b", edge_color = "#00202e", 
            font_color = "#00202e", node_size = 400, width = 2, font_size = 14, arrowsize = 20)
    labels = dict(dict_of_flows)
    for key in labels:
        labels[key] = round(labels[key], 3)
    nx.draw_networkx_edge_labels(G, pos=nx.circular_layout(G), edge_labels = labels, 
            font_color = "#00202e", font_size = 14)    
    plt.savefig(path)