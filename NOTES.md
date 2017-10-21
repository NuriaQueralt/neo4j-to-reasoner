# TODO
* limit by pmid count

# Queries
## links between chlorcyclizine and asthma with ONE intermediate node (59 paths)

on t1.medium, first query is 930ms, second query is 19ms

on avalanche, first query is 910ms, second query is 206ms

```
MATCH (source { name:"chlorcyclizine"}), (target { name: "Asthma"}), path=(source)-[*..2]-(target) WITH source, target, path, [r IN relationships(path) | type(r)] AS types RETURN path AS Path;
```

returns same number results as

```
match (a:`Chemicals & Drugs` {name: "chlorcyclizine"})-[r]-(x)-[s]-(b:Disorders {name: "Asthma"}) return a.name, type(r), r.n_pmids, x.name, type(s), s.n_pmids, b.name;
```

## links between chlorcyclizine and asthma with TWO intermediate node  (177k paths)

on t1.medium, first query is ???, second query is 3885ms
on avalanche, first query is ???, second query is 43753ms

```
MATCH (source { name:"chlorcyclizine"}), (target { name: "Asthma"}), path=(source)-[*..2]-(target) WITH source, target, path, [r IN relationships(path) | type(r)] AS types RETURN path AS Path;
```

```
match (a:`Chemicals & Drugs` {name: "chlorcyclizine"})-[r]-(x)-[s]-(y)-[t]-(b:Disorders {name: "Asthma"}) return a.name, type(r), r.n_pmids, x.name, type(s), s.n_pmids, y.name, type(t), t.n_pmids, b.name;
```


## From the command line

on t1.medium (port 7687) 
on avalanche (port 7690) 43s

```
time cypher-shell -a bolt://localhost:7690  'match (a:`Chemicals & Drugs` {name: "chlorcyclizine"})-[r]-(x)-[s]-(y)-[t]-(b:Disorders {name: "Asthma"}) return a.name, type(r), r.n_pmids, x.name, type(s), s.n_pmids, y.name, type(t), t.n_pmids, b.name;' > temp/t1
```


### use this command to build neo4j-to-reasoner.py
```
time cypher-shell -a bolt://localhost:7690  'MATCH (source { name:"chlorcyclizine"}), (target { name: "Asthma"}), path=(source)-[*..3]-(target) RETURN path AS Path;' > output/neo4j_output_full.txt
time cypher-shell -a bolt://localhost:7690  'MATCH (source { name:"chlorcyclizine"}), (target { name: "Asthma"}), path=(source)-[*..3]-(target) RETURN path AS Path LIMIT 10000;' > output/neo4j_output_snippet.txt
```
