####
# trying official python client

from neo4j.v1 import GraphDatabase, basic_auth
from yaml import dump

driver = GraphDatabase.driver("bolt://localhost:7690")
session = driver.session()

query = 'MATCH (source { name:"chlorcyclizine"}), (target { name: "Asthma"}), path=(source)-[*..3]-(target) WITH source, target, path, [r IN relationships(path) | type(r)] AS types RETURN path AS Path LIMIT 10;'

result = session.run(query)
for record in result:
    print(record["Path"])
    a = record["Path"]

