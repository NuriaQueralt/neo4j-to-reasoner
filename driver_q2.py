#
# driver_q2.py
#
# read in input files from data/q2-drugandcondition-list, run neo4j-to-reasoner.py

import pandas as pd
import math
import sys
import subprocess
from pathlib import Path

df = pd.read_csv( 'results/q2-drugandcondition-list-cui.txt', header=0, sep="\t", keep_default_na=False)
for index, row in df.iterrows():
    if( row.ConditionCUI == "" or row.DrugCUI == "" ):
        sys.stderr.write("Skipping " + str(index)+"\n")
        continue
    print(str(row))
    a = row
    output_filename = "output/"+str(index)+"_"+row.Drug.replace(" ","")+"_"+row.Condition.replace(" ","")+"_path3.csv"
    cmd = "python3 neo4j-to-reasoner.py -s "+row.DrugCUI+"  -e "+row.ConditionCUI+"  -t cui -f json_text -p 3 > "+output_filename

    if( Path(output_filename).exists() ):
        sys.stderr.write("Skipping " + output_filename +"\n")
        continue

    print(cmd)
    subprocess.call(cmd, shell=True)
