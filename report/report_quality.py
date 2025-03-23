#! /usr/bin/env python
import argparse
import os
import numpy as np
from collections import defaultdict 
from py_report_html import Py_report_html
import py_exp_calc.exp_calc as pxc
import umap
import copy 
import pandas as pd

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
    quality_tests.insert(0, ["Method 1", "Method 2", "variable","p-value", "adjusted p-value"])
    return quality_tests

def get_umap_with_labels(embedding_npy, embedding_node_names, node2external_group, node2HLCcommunity, node2Loucommunity, ext_groups_description, random_seed=123):
    print("Starting UMAP transformation...")
    print(f"Embedding shape: {embedding_npy.shape}")
    print(f"Number of gene names: {len(embedding_node_names)}")
    # Dimensionality reduction
    umap_coords = pxc.data2umap(embedding_npy, n_neighbors = 30, min_dist = 0.1, n_components = 2, 
        metric = 'euclidean', random_seed = random_seed)
    print("UMAP transformation successful. Coordinates obtained:")

    table = []
    for i, node in enumerate(embedding_node_names):
        external_groups = node2external_group.get(str(node), ["background"])
        community_HLC = node2HLCcommunity.get(str(node), ["background"])[0]
        community_Lou = node2Loucommunity.get(str(node), ["background"])[0]
        pos1, pos2 = umap_coords[i]
        for external_group in external_groups:
            ext_group_description = ext_groups_description.get(external_group, "background")
            table.append([external_group, "cluster-"+community_HLC, "cluster-"+community_Lou, str(node), str(pos1), str(pos2), ext_group_description])
    return table

def open_groups(path2groups, top=11, group_col= 0, node_col = 1, sep = "\t", filter_by=None):
    node2group = {}
    group2nodes = {}

    with open(path2groups) as f:
        for line in f:
            line = line.strip().split(sep)
            group = line[group_col]
            node = line[node_col]
            if filter_by and not group in filter_by:
                continue
            nodes = group2nodes.get(group)
            if not nodes:
                group2nodes[group] = [node]
            else:
                nodes.append(node)

    group2size = {group: len(nodes) for group, nodes in group2nodes.items()}
    groups = list(group2nodes.keys())
    groups.sort(key=lambda x: -group2size[x])
    all_nodes = []
    for nodes in group2nodes.values():
        all_nodes.extend(nodes)

    all_nodes = list(set(all_nodes))

    if top:
        groups = groups[0:top]
    for group in groups:
        for node in group2nodes[group]:
            if node2group.get(node):
                node2group[node].append(group)
            else:
                node2group[node] = [group]
    return node2group, [[group, size] for group, size in group2size.items()], groups

def parse_methods(table, method_parser, col_i = 0):
    for row in table:
        row[col_i] = method_parser[row[col_i]]

def read_file_to_dict(file_path):
    result_dict = {}
    with open(file_path) as f:
        for line in f:
            line = line.strip().split("\t")
            result_dict[line[1]] = line[0]
    return result_dict

##############################################################################################
## OPTPARSE
##############################################################################################

parser = argparse.ArgumentParser(description="")
parser.add_argument("-i", "--quality_metrics", dest="quality_metrics", default=None,
    help="Path to quality_metrics")
parser.add_argument("-r", "--relative_pos", dest="relative_pos", default=None,
    help="Path to relative position")
parser.add_argument("--prioritization", dest="prioritization", default=None,
    help="Path to ranking prioritization")
parser.add_argument("--gene_names_ens", dest="gene_names_ens", default=None,
    help="Path to node id to ens identifier")
parser.add_argument("--gene_names_symbol", dest="gene_names_symbol", default=None,
    help="Path to node id to ens identifier")
parser.add_argument("--group_distance",dest="group_distance", default=None, help="distance inside nodes of the same external group")
parser.add_argument("--emb_pos", dest="emb_pos", default=None, type = lambda x: {i.split(";")[0]:i.split(";")[1] for i in x.split(",")}, help="path to embedding position")
parser.add_argument("--embedding_distances", dest="embedding_distances", 
    default=None, type = lambda x: {i.split(";")[0]:i.split(";")[1] for i in x.split(",")}, 
    help="path to embedding distances")
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
group_distance = open_metrics(opts.group_distance)
rankings = open_metrics(opts.prioritization)
top_subset = 5

ranking_dic = {}
for rank in rankings:
    if rank[0] != "netcom": continue
    if rank[6] in ranking_dic:
        ranking_dic[rank[6]].append(rank)
    else:
        ranking_dic[rank[6]] = [rank]

subset_ranking_dic = {}
for key, value in ranking_dic.items():
    subset_ranking_dic[key] = value[0:top_subset]
#
#print(ranking_dic)
top_subset_ranking = []
for key, value in subset_ranking_dic.items():
    top_subset_ranking.extend(value)

print(top_subset_ranking)

#print(rankings)
candidates2seed = {}
for row in top_subset_ranking:
    if row[0] == "netcom":
        if candidates2seed.get(row[1]):
            candidates2seed[row[1]].append(row[6])
        else:
            candidates2seed[row[1]] = [row[6]]

#candidates2seed = {row[1]: row[6] for row in rankings if row[0] == "netcom"}

idnode2ens = {}
if opts.gene_names_ens:
    idnode2ens = read_file_to_dict(opts.gene_names_ens)
idnode2symbol = {}
if opts.gene_names_symbol:
    idnode2symbol = read_file_to_dict(opts.gene_names_symbol)

all_quality_metrics = [row for row in quality_metrics if float(row[4])>0 and row[0] in ["baseline","justnet","justcom","netcom","justcom_lou","netcom_lou"]]
all_quality_metrics = copy.deepcopy(all_quality_metrics)
quality_metrics = [row for row in quality_metrics if float(row[4])>0 and float(row[5])<=1 and row[0] in ["baseline","justnet","justcom","netcom","justcom_lou","netcom_lou"]]

flitered_groups = list(set([row[1] for row in quality_metrics]))
node2external_group, all_group_size, selected_external_groups = open_groups(opts.external_groups, top=10, filter_by= None)#flitered_groups)#None)#flitered_groups)

parse_names = { "baseline": "baseline",
                "justnet":"neigh",
                "justcom":"HLC_comm",
                "netcom":"neigh-HLC_comm",
                "justcom_lou":"Louvain_comm",
                "netcom_lou":"neigh-Louvain_comm"}
all_groups = []
for groups in node2external_group.values():
    for group in groups:
        all_groups.append(group)
all_groups = sorted(list(set(all_groups)))
if not opts.external_group_description:
    ext_groups_description = {group: group for group in all_groups}
ext_groups_description = {group: description for group, description in open_metrics(opts.external_group_description)}

for row in rankings: # 'netcom', '2946', '0.997615269917237', '0.0002471424158171146', '4', '4', 'CBL-related disorder'
    row[0] = parse_names[row[0]]
    row.append(idnode2ens[row[1]])
    row.append(idnode2symbol.get(row[1],"NA"))
rankings.insert(0, ["embedding_method","candidate","score","relative_pos","rank","rank_uniq","syndrome", "gene_ens","gene_symbol"])

group_distance = [[parse_names[row[0]],ext_groups_description[row[1]],*row[2:]] for row in group_distance if row[1] in selected_external_groups]
i = 0
new_group_distance = []
implemetation = ""
reaction = ""
for row in group_distance:
    if row[0] != implemetation:
        implemetation = row[0]
        i = 0
    if reaction != row[1]:
        i = 0
        reaction = row[1]
    new_group_distance.append([row[0],row[1]+f"_{i}", row[2]])
    i = i + 1

group_distance = new_group_distance
df = pd.DataFrame(group_distance, columns=["Implementation","group","distance"])
wide_df = df.pivot(index='Implementation', columns='group', values='distance')
wide_df.reset_index(inplace=True)
list_of_lists = wide_df.values.tolist()
head = wide_df.columns.tolist()
list_of_lists.insert(0, head)
list_of_lists = [list(i) for i in zip(*list_of_lists)]
list_of_lists = [ ["_".join(row[0].split("_")[0:-1]), *row[1:]] for row in list_of_lists ] 
list_of_lists[0][0] = "pathway"

node2HLCcommunity, hlcgroup2size, _ = open_groups(opts.communities["HLC"],top=21)
node2Loucommunity, louvaingroup2size, _ = open_groups(opts.communities["Louvain"],top=21)
print("new")
alg_type2table = {}
for alg_type, emb_pos_data in opts.emb_pos.items():
    embedding_npy = np.load(emb_pos_data+".npy")
    embedding_pos = [row[0] for row in open_metrics(emb_pos_data+".lst")]
    embedding_table = get_umap_with_labels(embedding_npy, embedding_pos, 
                                        node2external_group, node2HLCcommunity, 
                                        node2Loucommunity, ext_groups_description,
                                         random_seed = 123)
    ext_table = []
    for row in embedding_table:
        row.append(idnode2ens[row[3]])
        row.append(idnode2symbol.get(row[3], "NA"))
        ext_table.append(row + ["original"])
        #if candidates2seed.get(row[3]):
        #    for seed in candidates2seed[row[3]]:
        #        ext_table.append([seed] + row[1:6] + [seed] + [row[7]] + [row[8]] + ["prioritized"])

    embedding_table = ext_table
    print(embedding_table[0])
    print(embedding_table[1])

    embedding_table.insert(0, ["Reactome Pathway","HLC cluster","Louvain cluster","node","dim1","dim2", "Reactome Pathway Description","gene_ens","gene_symbol","type"])
    alg_type2table[parse_names[alg_type]] = embedding_table

relative_pos = [row for row in relative_pos if float(row[4])>4 and float(row[5])>0.75]

greater_quality_tests = quality_test(quality_metrics, "greater", parse_names)
less_quality_tests = quality_test(quality_metrics,"less", parse_names)

parse_methods(all_quality_metrics, parse_names)
parse_methods(quality_metrics, parse_names)
parse_methods(relative_pos, parse_names)

all_quality_metrics.insert(0, ["Implementation","group","mean","median","size","ied", "tpr", "cr", "diam"])
quality_metrics = [[row[0],row[1],*row[2:]] for row in quality_metrics]
quality_metrics.insert(0, ["Implementation","group","mean","median","size","ied", "tpr", "cr", "diam"])
relative_pos.insert(0, ["Implementation","group","mean","median","size","ied", "tpr", "cr", "diam"])
group_distance = [[row[0],row[1],row[2]] for row in group_distance]

ext_table = [] 
for row in group_distance:
    ext_table.append([row[0],row[1],row[2]])
    ext_table.append([row[1],row[0],row[2]])

group_distance = ext_table
group_distance.insert(0, ["Implementation","Group", "distance"])
group_distance = [[row[1],row[0],row[2]] for row in group_distance]


container = {
    'all_quality_metrics': all_quality_metrics,
    'quality_metrics': quality_metrics,
    'relative_metrics': relative_pos,
    'greater_quality_tests': greater_quality_tests,
    'less_quality_tests': less_quality_tests,
    'alg_type2embtable': alg_type2table,
    'hlcgroup2size': hlcgroup2size,
    'louvaingroup2size': louvaingroup2size,
    'group_distance': list_of_lists, #group_distance,
    'all_group_size': all_group_size,
    'rankings': rankings
}

report = Py_report_html(container, os.path.basename(opts.output))
report.compress = True
report.build(open(opts.template).read())
report.write(opts.output + '.html')

