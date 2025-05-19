#!/usr/bin/env python

import argparse
import networkx as nx
import numpy as np
from karateclub import Role2Vec, HOPE, NetMF, NMFADMM, NodeSketch

# Functions
def load_graph(input_file, delimiter="\t"):
    G = nx.Graph()

    with open(input_file, "r") as f:
        for line in f:
            parts = line.strip().split(delimiter)
            if len(parts) == 2:
                src, dst = parts
                G.add_edge(src, dst)
            elif len(parts) == 3:
                src, dst, weight = parts
                G.add_edge(src, dst, weight=float(weight))
    print(G.nodes())
    return G

def relabel_graph_to_consecutive_ids(G):
    mapping = {node: i for i, node in enumerate(G.nodes())}
    G_relabelled = nx.relabel_nodes(G, mapping)
    reverse_mapping = {i: node for node, i in mapping.items()}
    return G_relabelled, reverse_mapping

def train_model(method, G, dimensions, epochs):
    if method == "role2vec":
        model = Role2Vec(dimensions=dimensions, epochs=epochs)
    elif method == "hope":
        model = HOPE(dimensions=dimensions)
    elif method == "netmf":
        model = NetMF(dimensions=dimensions)
    elif method == "nmfadmm":
        model = NMFADMM(dimensions=dimensions)
    elif method == "nodesketch":
        model = NodeSketch(dimensions=dimensions)
    else:
        raise ValueError(f"Unsupported method: {method}")

    print(f"[INFO] Relabeling nodes to consecutive integers...")
    G_relabelled, reverse_mapping = relabel_graph_to_consecutive_ids(G)

    print(f"[INFO] Training {method}...")
    model.fit(G_relabelled)

    # Embedding vector por nodo
    embedding_dict = model.get_embedding_dictionary() if hasattr(model, 'get_embedding_dictionary') else None

    if embedding_dict is not None:
        node_names = [reverse_mapping[i] for i in range(len(embedding_dict))]
        embeddings = np.array([embedding_dict[i] for i in range(len(embedding_dict))])
    else:
        embeddings_matrix = model.get_embedding()
        node_names = [reverse_mapping[i] for i in range(len(embeddings_matrix))]
        embeddings = embeddings_matrix

    return embeddings, node_names

def save_embeddings_with_nodes(embeddings, node_names, output_file):
    np.save(output_file + ".npy", embeddings)
    with open(output_file + ".lst", "w") as f:
        for node in node_names:
            f.write(f"{node}\n")
    print(f"[INFO] Embeddings saved to {output_file}.npy")
    print(f"[INFO] Node names saved to {output_file}_nodes.txt")

# parser
parser = argparse.ArgumentParser(description="Graph Embedding CLI Tool")
parser.add_argument("--method", choices=["role2vec", "hope", "netmf", "nmfadmm", "nodesketch"],
                        required=True, help="Embedding method to use")
parser.add_argument("--edgelist",help="Edge list of the graph")
parser.add_argument("--dimensions", type=int, default=128, help="Embedding dimension size")
parser.add_argument("--epochs", type=int, default=50, help="Number of training epochs (if applicable)")
args = parser.parse_args()
# Main

G = load_graph(args.edgelist)
embeddings, node_names = train_model(args.method, G, args.dimensions, args.epochs)
save_embeddings_with_nodes(embeddings, node_names, "embedding_matrix")

