#!/usr/bin/env python

import argparse
import numpy as np
import py_exp_calc.exp_calc as pxc 
import networkx as nx
import itertools
from cdlib import NodeClustering, evaluation


def read_graph(graph_path, split_character="\t"):
    G = nx.Graph()
    with open(graph_path) as f:
        for line in f:
            pair = line.rstrip().split(split_character)
            node1 = pair[0]
            node2 = pair[1]
            G.add_node(node1)
            G.add_node(node2)
            if len(pair) == 3:
                G.add_edge(node1, node2, weight=float(pair[2]))
            else:
                G.add_edge(node1, node2, weight=1)
    return G

def open_lst(path):
	nodes = []
	with open(path) as f:
		for line in f:
			node = line.strip().split("\t")[0]
			nodes.append(node)
	return nodes

def get_external_groups(path):
	external_groups = {}
	with open(path) as f:
		for line in f:
			line = line.strip().split("\t")
			external_group = line[0]
			node = line[1]
			if external_groups.get(external_group):
				external_groups[external_group].add(node)
			else:
				external_groups[external_group] = {node}
	return external_groups

def get_average_distance(distance_matrix, lst2position, external_group):
	indexes = [lst2position[node] for node in external_group]
	indexes = list(set(indexes))
	distances = get_distance(distance_matrix, lst2position, external_group)
	return np.mean(distances),np.median(distances),len(indexes)

def get_distance(distance_matrix, lst2position, external_group):
	indexes = [lst2position[node] for node in external_group]
	indexes = list(set(indexes))
	submatrix = distance_matrix[indexes,:][:,indexes]
	distances = np.triu(submatrix).flatten()
	distances = distances[distances != 0]
	return distances

def get_diam(G, nodes):
	max_d = 0
	for pair in itertools.combinations(nodes, 2):
		try:
			d=len(nx.shortest_path(G,pair[0],pair[1]))
			if d > max_d:
				max_d = d
		except nx.exception.NetworkXNoPath:
			continue
	return max_d

def get_cluster_metrics(cluster,G):
	#print(cluster)
	c = NodeClustering([list(cluster)],G)
	ied = evaluation.internal_edge_density(G,c)[0]
	tpr = evaluation.triangle_participation_ratio(G,c)[0]
	cr = evaluation.cut_ratio(G,c)[0]
	diam = get_diam(G, cluster)
	return ied, tpr, cr, diam

# argparse
parser = argparse.ArgumentParser(description="")
parser.add_argument("--input",
                    nargs="?",
                    default=r"../data/Edgelist",
                    help="Input graph path -- edge list edges.")
parser.add_argument("-m", "--matrix", dest="matrix", help="matrix input")
parser.add_argument("-l","--list",dest="lst",help="lst path")
parser.add_argument("--external_groups",dest="external_groups", help="The external groups")
opts = parser.parse_args()
# Main
matrix = np.load(opts.matrix)
lst = open_lst(opts.lst)
lst2position = {n: p for p, n in enumerate(lst)}
position2lst ={p: n for p, n in enumerate(lst)}
ext_groups = get_external_groups(opts.external_groups)
G = read_graph(opts.input, "\t")

group2metric = {name: get_cluster_metrics(nodes, G) for name, nodes in ext_groups.items()}
# get distance
distance_matrix = pxc.coords2dis(matrix)
# Nomalization is necessary for comparison
norm_distance_matrix = pxc.z_normalization_matrix(distance_matrix)
np.fill_diagonal(norm_distance_matrix,0)

np.save("distance_matrix", norm_distance_matrix)
with open("distance_matrix.lst","w") as f:
	for node in lst:
		f.write(node+"\n")

with open("quality_metrics","w") as f:
	for group_name, nodes in ext_groups.items():
		mean, median, size =get_average_distance(norm_distance_matrix, lst2position, nodes)
		if size == 1 or size == 0 : continue
		f.write("\t".join([str(group_name),str(mean),str(median),str(size)])+"\t"+ "\t".join([str(x) for x in group2metric[group_name]]) + "\n")

with open("group_distance","w") as f:
	for group_name, nodes in ext_groups.items():
		distances = get_distance(norm_distance_matrix, lst2position, nodes)
		for distance in distances:
			f.write("\t".join([str(group_name),str(distance)]) + "\n")

distance_matrix = np.argsort(np.argsort(distance_matrix, axis=1), axis=1) + 1
norm_distance_matrix = pxc.z_normalization_matrix(distance_matrix)
with open("relative_quality_metrics","w") as f:
	for group_name,nodes in ext_groups.items():
		mean, median, size = get_average_distance(norm_distance_matrix, lst2position, nodes)
		if size == 1 or size == 0 : continue
		f.write("\t".join([str(group_name),str(mean),str(median),str(size)]) +"\t"+ "\t".join([str(x) for x in group2metric[group_name]]) + "\n")



