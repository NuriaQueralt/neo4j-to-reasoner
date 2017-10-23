####
# trying official python client

from neo4j.v1 import GraphDatabase, basic_auth
from yaml import dump

driver = GraphDatabase.driver("bolt://localhost:7690")
session = driver.session()

query = 'MATCH (source { name:"chlorcyclizine"}), (target { name: "Asthma"}), path=(source)-[*..3]-(target) WITH source, target, path, [r IN relationships(path) | type(r)] AS types RETURN path AS Path LIMIT 1;'

result = session.run(query)
for record in result:
    print(record["Path"])
    a = record["Path"]

a.nodes
a.relationships

# convert this structure
'''
>>> a.nodes
(<Node id=59729 labels={'Chemicals & Drugs'} properties={'name': 'chlorcyclizine'}>, <Node id=47907 labels={'Chemicals & Drugs'} properties={'name': 'Atropine'}>, <Node id=49094 labels={'Chemicals & Drugs'} properties={'name': 'Potassium'}>, <Node id=153169 labels={'Disorders'} properties={'name': 'Asthma'}>)
>>> a.relationships
(<Relationship id=133156 start=47907 end=59729 type='ASSOCIATED_WITH_CDawCD' properties={'n_pmids': '1', 'pmids': '{35784}'}>, <Relationship id=2760 start=49094 end=47907 type='ASSOCIATED_WITH_CDawCD' properties={'n_pmids': '2', 'pmids': '{2804636, 7508351}'}>, <Relationship id=4507438 start=49094 end=153169 type='ASSOCIATED_WITH_CDawDO' properties={'n_pmids': '8', 'pmids': '{11882918, 8777958, 4008616, 6364906, 10639760, 13208020, 9602294, 2772863}'}>)
'''

# into this YAML
'''
--- 
- 
  Nodes: 
    - 
      label: "Chemicals & Drugs"
      name: chlorcyclizine
    - 
      label: "Chemicals & Drugs"
      name: Atropine
    - 
      label: "Chemicals & Drugs"
      name: Potassium
    - 
      label: Disorders
      name: Asthma
  Edges: 
    - 
      n_pmids: 1
      pmids: 
        - 35784
      type: ASSOCIATED_WITH_CDawCD
    - 
      n_pmids: 2
      pmids: 
        - 2804636
        - 7508351
      type: ASSOCIATED_WITH_CDawCD
    - 
      n_pmids: 8
      pmids: 
        - 11882918
        - 8777958
        - 4008616
        - 6364906
        - 10639760
        - 13208020
        - 9602294
        - 2772863
      type: ASSOCIATED_WITH_CDawDO
--- 
'''
