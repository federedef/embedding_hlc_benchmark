#!/usr/bin/env python
#get_quality_by_external_group.py -m !launch_RARE_*!/embedding_matrix.npy -l !launch_RARE_*!/embedding_matrix.lst --external_groups $external_path
import argparse
import numpy as np
import py_exp_calc.exp_calc as pxc 
import networkx as nx
import itertools
from cdlib import NodeClustering, evaluation

# methods

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
	submatrix = distance_matrix[indexes,:][:,indexes]
	distances = np.triu(submatrix).flatten()
	distances = distances[distances != 0]
	#print(external_group)
	#print(distances)
	return np.mean(distances),np.median(distances),len(indexes)

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
# print(ext_groups)
G = read_graph(opts.input, " ")

# print("HEYYYYYYYYYYYYYYY")
# c = [len(c) for c in sorted(nx.connected_components(G), key=len, reverse=True)]
# print(c)
# print(nx.is_connected(G))
# print("==================")

group2metric = {name: get_cluster_metrics(nodes, G) for name, nodes in ext_groups.items()}
# get distance
distance_matrix = pxc.coords2dis(matrix)
# Nomalization is necessary for comparison
norm_distance_matrix = pxc.z_normalization_matrix(distance_matrix)
np.fill_diagonal(norm_distance_matrix,0)
with open("quality_metrics","w") as f:
	for group_name,nodes in ext_groups.items():
		mean, median, size=get_average_distance(norm_distance_matrix, lst2position, nodes)
		# print(size)
		# print(str(size))
		# print("\t".join([str(group_name),str(mean),str(median),str(size)]))
		if size == 1 or size == 0 : continue
		# print("\t".join([str(group_name),str(mean),str(median),str(size)]) +"\t"++ "\t".join([str(x) for x in group2metric[group_name]]) + "\n")
		f.write("\t".join([str(group_name),str(mean),str(median),str(size)])+"\t"+ "\t".join([str(x) for x in group2metric[group_name]]) + "\n")


distance_matrix = np.argsort(np.argsort(distance_matrix, axis=1), axis=1) + 1
norm_distance_matrix = pxc.z_normalization_matrix(distance_matrix)
with open("relative_quality_metrics","w") as f:
	for group_name,nodes in ext_groups.items():
		mean, median, size = get_average_distance(norm_distance_matrix, lst2position, nodes)
		if size == 1 or size == 0 : continue
		f.write("\t".join([str(group_name),str(mean),str(median),str(size)]) +"\t"+ "\t".join([str(x) for x in group2metric[group_name]]) + "\n")


# --------------------------- #
# def get_pos(group, lst2position, position2lst, distance_matrix):
# 	scores = []
# 	for node in group:
# 		# lst2position(node)
# 		node_poscore = pxc.get_rank_metrics(-distance_matrix[lst2position[node],:], position2lst)
# 		node_poscore = {row[0]: row[1:-1] for row in node_poscore}
# 		for positive in group - {node}:
# 			scores.append(node_poscore[positive][1])
# 	return scores

# from itertools import combinations

# all_scores = []
# for node_group in ext_groups.values():
# 	# positives = list(itertools.combinations(list(node_group),2))
# 	# negatives = random.choices(list(universe-positive), k=len(positives))
# 	# negatives = zip(node_group,negatives)
# 	scores= get_pos(node_group, lst2position, position2lst, distance_matrix)
# 	all_scores.extend(scores)

# with open("relative_pos", "w") as f:
# 	for score in all_scores:
# 		f.write(str(score)+"\n")



