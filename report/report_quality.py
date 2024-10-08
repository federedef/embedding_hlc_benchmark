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
parser.add_argument("-t", "--template", dest="template", default=None,
    help="Template")
parser.add_argument("-o", "--output", dest="output", default=None,
    help="output name")
opts = parser.parse_args()

################################################################################################
# MAIN
################################################################################################
quality_metrics = open_metrics(opts.quality_metrics)
quality_metrics.insert(0, ["execution_type","group","mean","median","size"])
container = {
    'quality_metrics': quality_metrics
}
print(quality_metrics)
report = Py_report_html(container, os.path.basename(opts.output))
report.build(open(opts.template).read())
report.write(opts.output + '.html')