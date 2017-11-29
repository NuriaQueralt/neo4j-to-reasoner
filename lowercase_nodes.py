#
# lowercase_nodes.py
# 
# change all node names to lower case in the neo4j nodes file prior to loading

import sys
import pandas as pd

d = pd.read_csv(sys.argv[1])
d['name:STRING'] = d['name:STRING'].str.lower()
print(d.to_csv(None,sep=",",index=False))
