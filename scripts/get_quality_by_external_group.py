#!/usr/bin/env python
#get_quality_by_external_group.py -m !launch_RARE_*!/embedding_matrix.npy -l !launch_RARE_*!/embedding_matrix.lst --external_groups $external_path
import argparse
import numpy as np
import py_exp_calc.exp_calc as pxc 

# methods

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
	print(distances)
	return np.mean(distances),np.median(distances),len(indexes)

# argparse
parser = argparse.ArgumentParser(description="")
parser.add_argument("-m", "--matrix", dest="matrix", help="matrix input")
parser.add_argument("-l","--list",dest="lst",help="lst path")
parser.add_argument("--external_groups",dest="external_groups", help="The external groups")
opts = parser.parse_args()
# Main
matrix = np.load(opts.matrix)
lst = open_lst(opts.lst)
lst2position = {n: p for p, n in enumerate(lst)}
ext_groups = get_external_groups(opts.external_groups)
# get distance
distance_matrix = pxc.coords2dis(matrix)
# Nomalization is necessary for comparison
distance_matrix = pxc.min_max_normalization_matrix(distance_matrix)
with open("quality_metrics","w") as f:
	for group_name,nodes in ext_groups.items():
		mean, median, size=get_average_distance(distance_matrix, lst2position, nodes)
		f.write("\t".join([str(group_name),str(mean),str(median),str(size)]) + "\n")
