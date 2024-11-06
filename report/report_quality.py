#! /usr/bin/env python
import argparse
import os
import numpy as np
from collections import defaultdict 
from py_report_html import Py_report_html
import py_exp_calc.exp_calc as pxc

#report_quality.py -i quality_metrics -t $template/quality.txt
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

##############################################################################################
## OPTPARSE
##############################################################################################

parser = argparse.ArgumentParser(description="")
parser.add_argument("-i", "--quality_metrics", dest="quality_metrics", default=None,
    help="Path to quality_metrics")
parser.add_argument("-r", "--relative_pos", dest="relative_pos", default=None,
    help="Path to relative position")
parser.add_argument("-t", "--template", dest="template", default=None,
    help="Template")
parser.add_argument("-o", "--output", dest="output", default=None,
    help="output name")
opts = parser.parse_args()

################################################################################################
# MAIN
################################################################################################
quality_metrics = open_metrics(opts.quality_metrics)
relative_pos = open_metrics(opts.relative_pos)

n=20
quality_metrics = [row for row in quality_metrics if float(row[4])>4 and float(row[5])>0 and row[0] in ["baseline","justnet","justcom","netcom"]]
relative_pos = [row for row in relative_pos if float(row[4])>4 and float(row[5])>0]
#quality_metrics = [row for row in quality_metrics]
#relative_pos = [row for row in relative_pos]
# new_quality_metrics = []
# for row in quality_metrics:
#     for i in range(int(row[4])):
#         idx=f"{row[1]}_{i}"
#         new_quality_metrics.append([row[0],idx,row[2],row[3],row[4],row[5]])
# quality_metrics = new_quality_metrics
quality_metrics.insert(0, ["execution_type","group","mean","median","size","ied", "tpr", "cr", "diam"])
relative_pos.insert(0, ["execution_type","group","mean","median","size","ied", "tpr", "cr", "diam"])

print(relative_pos)
container = {
    'quality_metrics': quality_metrics,
    'relative_metrics': relative_pos
}

report = Py_report_html(container, os.path.basename(opts.output))
report.build(open(opts.template).read())
report.write(opts.output + '.html')