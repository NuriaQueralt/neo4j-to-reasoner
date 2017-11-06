####
# trying official python client

from neo4j.v1 import GraphDatabase, basic_auth
import yaml
import json
import re
import argparse
import sys

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
        #e["n_pmids"] = list(map(int, edge.properties['n_pmids']))[0]
        e["n_pmids"] = edge.properties['n_pmids']
        s_pmids = edge.properties['pmids']
        a_pmids = re.sub(".*pubmed/","",s_pmids).split(",")
        e["pmids"] = list(map(int, a_pmids))
        e["type"] = edge.type
        out['Edges'].append(e)
    return out

parser = argparse.ArgumentParser(description='process user given parameters')
parser.add_argument("-f", "--format", required = False, dest = "format", help = "yaml/json", default="yaml")
parser.add_argument("-s", "--start", required = True, dest = "start", help = "starting node")
parser.add_argument("-e", "--end", required = True, dest = "end", help = "ending node")
parser.add_argument("-t", "--nodetype", required = False, dest = "nodetype", help = "node type (name/cui)", default="name")
parser.add_argument("-l", "--limit", required = False, dest = "limit", help = "limit on number of records", default=None)
parser.add_argument("-p", "--pathlength", required = False, dest = "pathlength", help = "max path length", default=2)

args = parser.parse_args()

if(args.format not in ["json","yaml","json_text"]):
   sys.stderr.write("Invalid format. Exiting.\n")
   exit()


driver = GraphDatabase.driver("bolt://localhost:7690")
session = driver.session()

if( args.nodetype == "name" ):
    query = 'MATCH path=(source:`Chemicals & Drugs`)-[*..'+args.pathlength+']-(target:Disorders) where source.name starts with "'+args.start.lower()+'" AND target.name starts with "'+args.end.lower()+'" return path'
elif( args.nodetype == "cui" ):
    query = 'MATCH path=(source:`Chemicals & Drugs`)-[*..'+args.pathlength+']-(target:Disorders) where source.cui = "'+args.start+'" AND target.cui = "'+args.end+'" return path'
else :
    sys.stderr.write("Error with nodetype.\n")
    exit()

if args.limit is not None:
    query = query + ' limit ' + args.limit

sys.stderr.write("QUERY: "+query+"\n")

result = session.run(query)

output = []
for record in result:
    z = parsePath(record)
    output.append(z)

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
