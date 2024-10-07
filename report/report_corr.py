#! /usr/bin/env python
import argparse
import os
import numpy as np
from collections import defaultdict 
from py_report_html import Py_report_html
from py_exp_calc.exp_calc import get_corr

##############################################################################################
## METHODS
##############################################################################################


##############################################################################################
## OPTPARSE
##############################################################################################

parser = argparse.ArgumentParser(description="")
parser.add_argument("-R", "--reference_matrix", dest="ref_matrix", default=None,
    help="Path to reference matrix")
parser.add_argument("-G", "--compare_matrix", dest="comp_matrix", default=None,
    help="Path to reference matrix")
parser.add_argument("-o", "--output", dest="output", default=None,
    help="Output")
parser.add_argument("-t", "--template", dest="template", default=None,
    help="Template")
opts = parser.parse_args()


################################################################################################
# MAIN
##############################################################################################
matrix1 = np.load(opts.ref_matrix)
matrix2 = np.load(opts.comp_matrix)

nnodes1 = matrix1.shape[0]
nnodes2 = matrix2.shape[0]
if nnodes1 != nnodes2:
    print("different nodes number for a graph")
    print(nnodes2-nnodes1)
else:
    print("The are the same", nnodes1)

matrix1 = np.dot(matrix1, matrix1.T)
matrix2 = np.dot(matrix2, matrix2.T)

corrs = []
for i in range(nnodes1):
    corr, _ = get_corr(x=matrix1[i,:],y=matrix2[i,:],corr_type= "spearman")
    corrs.append([1,corr])
print(corrs)
container = {
        'corr': corrs,
        'median': np.mean([corr[1] for corr in corrs]),
        'max': np.min([corr[1] for corr in corrs]),
        'min': np.max([corr[1] for corr in corrs]),
}
report = Py_report_html(container, os.path.basename(opts.output))
report.build(open(opts.template).read())
report.write(opts.output + '.html')

