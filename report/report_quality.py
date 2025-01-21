#! /usr/bin/env python
import argparse
import os
import numpy as np
from collections import defaultdict 
from py_report_html import Py_report_html
import py_exp_calc.exp_calc as pxc
import umap
import copy 

##############################################################################################
## METHODS
##############################################################################################

def open_metrics(path):
    metrics = []
    with open(path) as f:
        for line in f:
            line = line.strip().split("\t")
            metrics.append(line)
    return metrics

def quality_test(quality_metrics, alternative, method_parser=None):
    # alternative: greater, less, both
    idx_factor = [0]   
    adj_pval = "fdr_bh"  
    assumptions = {"continuos": True, "paired": False}
    quality_tests = pxc.get_test([[row[0],float(row[2])] for row in quality_metrics ], 
                                    idx_factor, alternative, adj_pval, assumptions, 
                                    header=False, parametric = True)

    quality_tests = [[row[0].replace("F1_", "").split(":")[0],row[0].replace("F1_", "").split(":")[1],*row[1:]] for row in quality_tests]
    if method_parser:
        quality_tests = [[method_parser[row[0]],method_parser[row[1]],*row[2:]] for row in quality_tests]
    #quality_tests = [row for row in quality_tests if row[0] == "netcom_lou" or row[1] == "netcom_lou"]
    quality_tests.insert(0, ["Method 1", "Method 2", "variable","p-value", "adjusted p-value"])
    return quality_tests

def get_umap_with_labels(embedding_npy, embedding_node_names, node2external_group, node2HLCcommunity, node2Loucommunity, ext_groups_description, random_seed=123):
    print("Starting UMAP transformation...")
    print(f"Embedding shape: {embedding_npy.shape}")
    print(f"Number of gene names: {len(embedding_node_names)}")
    # Dimensionality reduction
    umap_coords = pxc.data2umap(embedding_npy, n_neighbors = 15, min_dist = 0.1, n_components = 2, metric = 'euclidean', random_seed = random_seed)
    print("UMAP transformation successful. Coordinates obtained:")
    print(umap_coords)

    table = []
    for i, node in enumerate(embedding_node_names):
        external_group = node2external_group.get(str(node), "background")
        community_HLC = node2HLCcommunity.get(str(node), "background")
        community_Lou = node2Loucommunity.get(str(node), "background")
        pos1, pos2 = umap_coords[i]
        ext_group_description = ext_groups_description.get(external_group, "background")
        table.append([external_group, "cluster-"+community_HLC, "cluster-"+community_Lou, str(node), str(pos1), str(pos2), ext_group_description])
    
    return table

def open_groups(path2groups, top=11, group_col= 0, node_col = 1, sep = "\t"):
    node2group = {}
    group2nodes = {}

    with open(path2groups) as f:
        for line in f:
            line = line.strip().split(sep)
            group = line[group_col]
            node = line[node_col]
            nodes = group2nodes.get(group)
            if not nodes:
                group2nodes[group] = [node]
            else:
                nodes.append(node)

    group2size = {group: len(nodes) for group, nodes in group2nodes.items()}
    groups = list(group2nodes.keys())
    groups.sort(key=lambda x: -group2size[x])

    if top:
        groups = groups[0:(top-1)]
    for group in groups:
        for node in group2nodes[group]:
            node2group[node] = group
    return node2group, [[group, size] for group, size in group2size.items()]

def parse_methods(table, method_parser, col_i = 0):
    for row in table:
        row[col_i] = method_parser[row[col_i]]

##############################################################################################
## OPTPARSE
##############################################################################################

parser = argparse.ArgumentParser(description="")
parser.add_argument("-i", "--quality_metrics", dest="quality_metrics", default=None,
    help="Path to quality_metrics")
parser.add_argument("-r", "--relative_pos", dest="relative_pos", default=None,
    help="Path to relative position")
parser.add_argument("--emb_pos", dest="emb_pos", default=None, type = lambda x: {i.split(";")[0]:i.split(";")[1] for i in x.split(",")}, help="path to embedding position")
parser.add_argument("--communities", dest="communities", default=None, type = lambda x: {i.split(";")[0]:i.split(";")[1] for i in x.split(",")}, help="path to embedding position")
parser.add_argument("--external_groups", dest="external_groups", default=None, help="")
parser.add_argument("-t", "--template", dest="template", default=None,
    help="Template")
parser.add_argument("--external_group_description", default= None, dest="external_group_description", help="a table with the first column the name of the external group and second column its description")
parser.add_argument("-o", "--output", dest="output", default=None,
    help="output name")
opts = parser.parse_args()

################################################################################################
# MAIN
################################################################################################
quality_metrics = open_metrics(opts.quality_metrics)
relative_pos = open_metrics(opts.relative_pos)
node2external_group, _ = open_groups(opts.external_groups)
parse_names = { "baseline": "baseline",
                "justnet":"neigh",
                "justcom":"HLCcomm",
                "netcom":"neigh-HLCcomm",
                "justcom_lou":"Louvaincomm",
                "netcom_lou":"neigh-Louvaincomm"}

all_groups = []
for groups in node2external_group.values():
    for group in groups:
        all_groups.append(group)
all_groups = sorted(list(set(all_groups)))
if not opts.external_group_description:
    ext_groups_description = {group: group for group in all_groups}
ext_groups_description = {group: description for group, description in open_metrics(opts.external_group_description)}

node2HLCcommunity, hlcgroup2size = open_groups(opts.communities["HLC"],top=20)
node2Loucommunity, louvaingroup2size = open_groups(opts.communities["Louvain"],top=20)

alg_type2table = {}
for alg_type, emb_pos_data in opts.emb_pos.items():
    embedding_npy = np.load(emb_pos_data+".npy")
    embedding_pos = [row[0] for row in open_metrics(emb_pos_data+".lst")]
    embedding_table = get_umap_with_labels(embedding_npy, embedding_pos, node2external_group, node2HLCcommunity, node2Loucommunity, ext_groups_description, random_seed = 123)
    embedding_table.insert(0, ["Reactome Pathway","HLC cluster","Louvain cluster","node","dim1","dim2", "Reactome Pathway Description"])
    alg_type2table[alg_type] = embedding_table

all_quality_metrics = [row for row in quality_metrics if float(row[4])>4]
all_quality_metrics = copy.deepcopy(all_quality_metrics)
quality_metrics = [row for row in quality_metrics if float(row[4])>4 and float(row[5])>0.75 and row[0] in ["baseline","justnet","justcom","netcom","justcom_lou","netcom_lou"]]
relative_pos = [row for row in relative_pos if float(row[4])>4 and float(row[5])>0.75]

greater_quality_tests = quality_test(quality_metrics, "greater", parse_names)
less_quality_tests = quality_test(quality_metrics,"less", parse_names)

parse_methods(all_quality_metrics, parse_names)
parse_methods(quality_metrics, parse_names)
parse_methods(relative_pos, parse_names)

all_quality_metrics.insert(0, ["Implementation","group","mean","median","size","ied", "tpr", "cr", "diam"])
quality_metrics.insert(0, ["Implementation","group","mean","median","size","ied", "tpr", "cr", "diam"])
relative_pos.insert(0, ["Implementation","group","mean","median","size","ied", "tpr", "cr", "diam"])

container = {
    'all_quality_metrics': all_quality_metrics,
    'quality_metrics': quality_metrics,
    'relative_metrics': relative_pos,
    'greater_quality_tests': greater_quality_tests,
    'less_quality_tests': less_quality_tests,
    'alg_type2embtable': alg_type2table,
    'hlcgroup2size': hlcgroup2size,
    'louvaingroup2size': louvaingroup2size
}

report = Py_report_html(container, os.path.basename(opts.output))
report.compress = True
report.build(open(opts.template).read())
report.write(opts.output + '.html')