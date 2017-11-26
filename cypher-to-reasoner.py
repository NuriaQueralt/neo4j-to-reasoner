####
# trying official python client

from neo4j.v1 import GraphDatabase, basic_auth
import yaml
import json
import re
import argparse
import sys

# Core function to parse neo4j results
def parsePath( path ):
    out = {}
    out['Nodes'] = []
    for node in path["path"].nodes:
        n = {}
        n["name"] = node.properties['name']
        n["umlscui"] = node.properties['cui']
        n["label"] = list(node.labels)[0]
        out['Nodes'].append(n)
    out['Edges'] = []
    for edge in path["path"].relationships:
        e = {}
        e["n_pmids"] = edge.properties['n_pmids']
        s_pmids = edge.properties['pmids']
        a_pmids = re.sub(".*pubmed/","",s_pmids).split(",")
        e["pmids"] = list(map(int, a_pmids))
        e["type"] = edge.type
        out['Edges'].append(e)
    return out

# Parse and validate command line arguments
parser = argparse.ArgumentParser(description='process user given parameters')
parser.add_argument("-f", "--format", required = False, dest = "format", help = "yaml/json", default="yaml")
parser.add_argument("-q", "--query", required = True, dest = "query", help = "cypher query")

args = parser.parse_args()

if(args.format not in ["json","yaml","json_text"]):
   sys.stderr.write("Invalid format. Exiting.\n")
   exit()

# initialize neo4j
driver = GraphDatabase.driver("bolt://localhost:7690")
session = driver.session()
output = []

sys.stderr.write("QUERY: "+args.query+"\n")
result = session.run(args.query)
sys.stderr.write("QUERY complete.\n")

counter = 0
for record in result:
    z = parsePath(record)
    output.append(z)
    counter = counter + 1
    if(counter%100000==0):
        sys.stderr.write("Processed "+str(counter)+"\n")

### print output 
if(args.format == "yaml"): 
    print(yaml.dump(output, default_flow_style=False))
elif(args.format == "json"):
    print(json.dumps(output))
elif(args.format == "json_text"):
    for record in output:
        print(json.dumps(record))
else:
    sys.stderr.write("Error.\n")
