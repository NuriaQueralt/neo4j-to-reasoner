#
# sum_pmids.py
#
# INPUT: text file with JSON format on each line corresponding to a path; same
#        type as exported by json_text in *=neo4j-to-reasoner.py
#
import gzip
import json
import numpy as np
import argparse

def geo_mean_overflow(iterable):
    a = np.log(iterable)
    return np.exp(a.sum()/len(a))


parser = argparse.ArgumentParser(description='process user given parameters')
parser.add_argument("-i", "--inputfile", required = True, dest = "inputfile", help = "input file to parse")
args = parser.parse_args()

count=0
with gzip.open(args.inputfile,'rt') as f:
    for line in f:
        data = json.loads(line)
        pmidCounts = []
        for edge in data['Edges']:
            pmidCounts.append(edge['n_pmids'])
        print(line.rstrip()+"\t"+str(np.sum(pmidCounts))+"\t"+str(np.mean(pmidCounts))+"\t"+str(geo_mean_overflow(pmidCounts)))
