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
MATCH (a)<-->() RETURN id(a),a.name,labels(a),count(*) as degree ORDER BY degree DESC LIMIT 20
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

# imatinib-asthma, with the ids enumerated
time cypher-shell -a bolt://localhost:7690 'PROFILE MATCH path=(source)-[*..3]-(target) where id(source) in [20391,33498,37483,37996,108238] AND id(target) in [58305,81336,116957,120975,126685,126831,128515,139148,145350,148806,153169,153693,154436,159046,160389,161676,237245,244566,245913,249204,255830] return path' > t3
real    241m13.127s
user    65m15.588s


# find imatinib-asthma path?
MATCH path=((source)-[r1]-(i1)-[r2]-(i2)-[r3]-(target)) where lower(source.name)=~"imatinib.*" AND lower(target.name)=~"asthma.*" AND lower(i1.name)=~".*kit.*" AND lower(i2.name)=~".*mast.*" return path

# filter based on PMID count
MATCH path=((source)-[r1]-(i1)-[r2]-(i2)-[r3]-(target)) where lower(source.name)=~"imatinib.*" AND lower(target.name)=~"asthma.*" AND lower(i1.name)=~".*kit.*" AND lower(i2.name)=~".*mast.*" and toInt(r2.n_pmids)>4 return path

MATCH path=((source)-[r1]-(i1)-[r2]-(i2)-[r3]-(target)) where lower(source.name)=~"imatinib.*" AND lower(target.name)=~"asthma.*" AND lower(i1.name)=~".*kit.*" AND lower(i2.name)=~".*mast.*" and toInt(r3.n_pmids)+toInt(r2.n_pmids)>4 return path

MATCH path=((source)-[rels*..3]-(target)) with path, reduce(t=0, r IN rels | t + toint(r.n_pmids)) AS total where lower(source.name)=~"imatinib.*" AND lower(target.name)=~"asthma.*" AND total>2 return path limit 10;


### Changes to input files from mike
# copied edges_condensed_filtered_neo4j.csv and nodes_condensed_filtered_neo4j.csv from ~mmayers/projects/semmed/data/

# lowercase node labels
cat input/nodes_condensed_filtered_neo4j.csv | gawks '{$2=tolower($2);print $0}' > input/nodes_2017-11-03.csv
cat input/edges_condensed_filtered_neo4j.csv | gawks '$4>1' > input/edges_2017-11-05.csv

# to load new data
sudo ./reset_database.sh
sudo ./import-command.sh
sudo /home/mmayers/software/neo4j-community-3.1.3/bin//neo4j start

# delete nodes of type Living Beings, Anatomy, Procedures
match (n:`Living Beings`) detach delete n
match (n:Procedures) detach delete n
match (n:Anatomy) detach delete n

#create indexes
CREATE INDEX ON :Disorders(name)
CREATE INDEX ON :`Chemicals & Drugs`(name)
CREATE INDEX ON :Disorders(cui)
CREATE INDEX ON :`Chemicals & Drugs`(cui)

# find true imatinib-asthma path
MATCH path=((source:`Chemicals & Drugs`)-[r1]-(i1)-[r2]-(i2)-[r3]-(target:Disorders)) 
where source.name starts with "imatinib" AND target.name starts with "asthma" AND i1.name=~".*kit.*" AND i2.name=~".*mast.*" 
return path

# finishes almost instantly
explain MATCH path=((source:`Chemicals & Drugs`)-[rels*..2]-(target:Disorders)) 
where source.name starts with "imatinib" AND target.name starts with "asthma" 
return path,reduce(t=0, r IN rels | t + r.n_pmids) AS total limit 10

# very long to finish
explain MATCH path=((source:`Chemicals & Drugs`)-[rels*..2]-(target:Disorders)) 
with path, reduce(t=0, r IN rels | t + r.n_pmids) AS total  
where source.name starts with "imatinib" AND target.name starts with "asthma" 
return path, total limit 10

# quick to finish
explain MATCH path=((source:`Chemicals & Drugs`)-[rels*..2]-(target:Disorders)) 
where source.name starts with "imatinib" AND target.name starts with "asthma" 
with path, reduce(t=0, r IN rels | t + r.n_pmids) AS total  
return path, total limit 10

# get imatinib -> asthma with edge n_pmids > 1 (took 162 minutes, 822087 paths)
time cypher-shell -a bolt://localhost:7690 'MATCH path=((source:`Chemicals & Drugs`)-[rels*..3]-(target:Disorders)) where source.name starts with "imatinib" AND target.name = "asthma" return path' > output/imatinib_asthma_path3

# explicitly use name of imatinib (took 39 minutes, 616221 paths)
time cypher-shell -a bolt://localhost:7690 'MATCH path=((source:`Chemicals & Drugs`)-[rels*..3]-(target:Disorders)) where source.name = "imatinib" AND target.name = "asthma" return path' > output/imatinib_asthma_path3.2

# use CUIs instead of names (43 minutes, 616221 paths)
time cypher-shell -a bolt://localhost:7690 'MATCH path=(source:`Chemicals & Drugs`)-[*..3]-(target:Disorders) where source.cui = "C0935989" AND target.cui = "C0004096" return path' > output/imatinib_asthma_path3.3

# use explicit path length instead of variable length 
#   path 3: (1.3 mins, 615826 paths)
#   path 2: (<1s, 396 paths)
#   total: 616222 paths
time cypher-shell -a bolt://localhost:7690 'match path=(source:`Chemicals & Drugs`)-[r1]-(i1)-[r2]-(i2)-[r3]-(target:Disorders) where source.cui="C0935989" AND target.cui="C0004096" return path' > output/imatinib_asthma_path3.4
time cypher-shell -a bolt://localhost:7690 'match path=(source:`Chemicals & Drugs`)-[r1]-(i1)-[r2]-(target:Disorders) where source.cui="C0935989" AND target.cui="C0004096" return path' > output/imatinib_asthma_path3.4b

# constrain the paths by intermediate node types (1 s, 2843 paths)
time cypher-shell -a bolt://localhost:7690 'match path=(source:`Chemicals & Drugs`)-[r1]-(i1:`Genes & Molecular Sequences`)-[r2]-(i2:Physiology)-[r3]-(target:Disorders) where source.cui="C0935989" AND target.cui="C0004096" return path' > output/imatinib_asthma_path3_semtypes.1

# constrain the paths by intermediate node types (73 mins, 45008 paths)
time cypher-shell -a bolt://localhost:7690 'match path=(source:`Chemicals & Drugs`)-[*..3]-(target:Disorders) where source.cui="C0935989" AND target.cui="C0004096" and all (n IN nodes(path)[1..-1] WHERE "Genes & Molecular Sequences" IN labels(n) OR "Physiology" IN labels(n) ) return path' > output/imatinib_asthma_path3_semtypes.2

# constrain the paths by intermediate node types (6 s, 44909 paths)
time cypher-shell -a bolt://localhost:7690 'match path=(source:`Chemicals & Drugs`)-[r1]-(i1)-[r2]-(i2)-[r3]-(target:Disorders) where source.cui="C0935989" AND target.cui="C0004096" and ( "Genes & Molecular Sequences" IN labels(i1) OR "Physiology" IN labels(i1) ) AND ( "Genes & Molecular Sequences" IN labels(i2) OR "Physiology" IN labels(i2) ) return path' > output/imatinib_asthma_path3_semtypes.3

# use neo4j-to-reasoner.py
time python3 neo4j-to-reasoner.py -s C0935989 -e C0004096 -t cui -f json_text -p 2 > t4


### automate path finding

head data/q2-drugandcondition-list > data/q2-drugandcondition-list.head
python3 search_umls.py -S settings_private.yaml -H -i data/q2-drugandcondition-list.head -o tt1

python3 driver_q2.py

