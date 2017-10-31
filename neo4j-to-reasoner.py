####
# trying official python client

from neo4j.v1 import GraphDatabase, basic_auth
from yaml import dump
import re

def parsePath( path ):
    out = {}
    out['Nodes'] = []
    for node in path["Path"].nodes:
        n = {}
        n["name"] = node.properties['name']
        n["umlscui"] = node.properties['umlscui']
        n["label"] = list(node.labels)[0]
        out['Nodes'].append(n)
    out['Edges'] = []
    for edge in path["Path"].relationships:
        e = {}
        e["n_pmids"] = list(map(int, edge.properties['n_pmids']))[0]
        s_pmids = edge.properties['pmids']
        a_pmids = re.sub(".*pubmed/","",s_pmids).split(",")
        e["pmids"] = list(map(int, a_pmids))
        e["type"] = edge.type
        out['Edges'].append(e)
    return out


driver = GraphDatabase.driver("bolt://localhost:7690")
session = driver.session()

query = 'MATCH (source { name:"chlorcyclizine"}), (target { name: "Asthma"}), path=(source)-[*..3]-(target) WITH source, target, path, [r IN relationships(path) | type(r)] AS types RETURN path AS Path LIMIT 10000;'

result = session.run(query)

output = []
for record in result:
    z = parsePath(record)
    output.append(z)


#f = open('out.yaml','w')
#f.write(dump(output, default_flow_style=False))
#f.close()
print(dump(output, default_flow_style=False))

