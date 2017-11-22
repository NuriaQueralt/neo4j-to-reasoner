#
# driver_q1.py
#
# read in input files from data/q1-disease-list run neo4j-to-reasoner.py

import pandas as pd
import math
import sys
import subprocess
from pathlib import Path

df = pd.read_csv( 'results/q1-disease-list-cui.txt', header=0, sep="\t", keep_default_na=False)
for index, row in df.iterrows():
    if( row.DiseaseCUI == "" ):
        sys.stderr.write("Skipping " + str(index)+"\n")
        continue
    print(str(row))
    a = row
    output_filename = "output/q1_"+str(index)+"_"+row.Disease.replace(" ","")+"_path3b.txt"
    cmd = "python3 q1-neo4j-to-reasoner.py -s "+row.DiseaseCUI+"  -t cui -f json_text -p 3 > "+output_filename

    if( Path(output_filename).exists() ):
        sys.stderr.write("Skipping " + output_filename +"\n")
        continue

    print(cmd)
    subprocess.call(cmd, shell=True)
