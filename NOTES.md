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
MATCH (source { name:"chlorcyclizine"}), (target { name: "Asthma"}), path=(source)-[*..3]-(target) WITH source, target, path, [r IN relationships(path) | type(r)] AS types RETURN path AS Path;
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


## FA-related queries

### get all nodes related to FANC (genes, protein, disease)
match (a) where lower(a.name) =~ "fanc.*" return a;

### add label nodeLabel on fanc related nodes and mitomycin nodes
match (a) where lower(a.name) =~ "fanc.*" OR lower(a.name) =~ "mitomycin.*" set a :nodeLabel return a;

### create index on names of all nodes
create index on:nodeLabel(name)

### sort nodes by degree
'
MATCH (a)-->() RETURN id(a),count(*) as degree ORDER BY degree DESC LIMIT 10
'

### find paths between fanc nodes and mitomycin nodes with ONE intermediate node
### 47381 = DNA, 47586 = RNA, 253653 = excision, 49000 = Amino acids, 860 = Cell membrane
### 121340 = Fanconi Syndrome, 1030 - Cell surface

match (a)-[r1]-(i1)-[r2]-(b) 
where lower(a.name)=~"fanc.*" and 
      lower(b.name)=~"mitomycin.*" 
return a,b,r1,r2,i1 limit 500;

match (a)-[r1]-(i1)-[r2]-(b) 
where lower(a.name)=~"fanc.*" and 
      lower(b.name)=~"mitomycin.*" and 
      NOT id(i1) in [47381,47586,253653,49000,860,121340] 
return a,b,r1,r2,i1 limit 500;

match (a)-[r1]-(i1)-[r2]-(b) 
      where lower(a.name)=~"fanc.*" and 
      lower(b.name)=~"mitomycin.*" and 
      NOT id(i1) in [47381,47586,253653,49000,860,121340] AND 
      toInteger(r1.n_pmids) > 2 AND 
      toInteger(r2.n_pmids) > 2 
return a,b,r1,r2,i1 limit 500;

### find paths between fanc nodes and mitomycin nodes with TWO intermediate node
match (a)-[r1]-(i1)-[r2]-(i2)-[r3]-(b) 
where lower(a.name)=~"fanc.*" AND
      lower(b.name)=~"mitomycin.*" AND 
      NOT id(i1) in [47381,47586,253653,49000,860,121340] AND
      NOT id(i2) in [47381,47586,253653,49000,860,121340] AND
      toInteger(r1.n_pmids) > 2 AND 
      toInteger(r2.n_pmids) > 2 AND
      toInteger(r3.n_pmids) > 2 
return a,b,r1,r2,r3,i1,i2 limit 500;


### maureen notes

double click -> show node details --> show all edges in inspector
ask kevin to explode translator network


### convert terms to UMLS
python search_umls.py -S settings_private.yaml -H -i data/q1-disease-list -d -o results/q1-disease-list-cui.txt
python search_umls.py -S settings_private.yaml -H -i data/q2-drugandcondition-list -d -o results/q2-drugandcondition-list-cui.txt


# imatinib example
time python3 neo4j-to-reasoner.py -s imatinib -e Asthma -f json_text -p 2 > output/imatinib_asthma_full2.txt
