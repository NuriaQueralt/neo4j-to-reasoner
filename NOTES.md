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

### sort nodes by degree (takes ~2 seconds via web interface)
'
MATCH (a)<-->() with a,count(*) as degree where degree > 5000 RETURN id(a),a.name,labels(a),degree ORDER BY degree DESC
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

# delete high degree nodes
MATCH (a)<-->() with a,count(*) as degree where degree > 5000 RETURN a, degree
MATCH (a)<-->() with a,count(*) as degree where degree > 5000 detach delete a
MATCH (a)<-->() with a,count(*) as degree where degree > 2500 AND not labels(a) in ["Disorders"] RETURN a, degree
MATCH (a)<-->() with a,count(*) as degree where degree > 2500 AND not labels(a) in ["Disorders"] detach delete a


#create indexes
CREATE INDEX ON :Disorders(name)
CREATE INDEX ON :`Chemicals & Drugs`(name)
CREATE INDEX ON :Disorders(cui)
CREATE INDEX ON :`Chemicals & Drugs`(cui)

# find true imatinib-asthma path
MATCH path=((source:`Chemicals & Drugs`)-[r1]-(i1)-[r2]-(i2)-[r3]-(target:Disorders)) 
where source.name = "imatinib" AND target.name = "asthma" AND i1.name=~".*kit.*" AND i2.name="mast cell activation" 
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


### Q1 ###

match (n) where n.name starts with "sickle cell" return n;
match (n) where n.name starts with "malaria" return n;

# sickle cell trait is C0037054
# malaria is C0024530

# find true positive
match path=(source:Disorders)-[r1]-(i1)-[r2]-(i2)-[r3]-(target:Disorders) where source.cui="C0024530" AND target.cui="C0037054" AND (i1.name starts with "heme" OR i2.name starts with "heme") return path


# find paths from a specific disease to any disease
match path=(source:Disorders)-[r1]-(i1)-[r2]-(target:Disorders) where source.cui="C0037054" return count(path)
match path=(source:Disorders)-[r1]-(i1)-[r2]-(i2)-[r3]-(target:Disorders) where source.cui="C0037054" return count(path)

# get UMLS CUIs from Orphanet
python3 orphadata2cui.py > results/orphadata2cui.txt

# to get comma-separated string
gawkt '{print $2}' results/orphadata2cui.txt | paste -d, -s | sed 's/,/","/g'

# query from malaria to genetic diseases
match path=(source:Disorders)-[r1]-(i1)-[r2]-(i2)-[r3]-(target:Disorders) where source.cui="C0024530" AND target.cui in ["C0000744","C0001080","C0001193","C0001206","C0002066","C0002736","C0002895","C0002986","C0004135","C0004779","C0005859","C0006845","C0007965","C0008928","C0010314","C0010674","C0012236","C0013364","C0013481","C0013581","C0013903","C0014848","C0016037","C0016667","C0016719","C0016788","C0017922","C0017924","C0017925","C0017926","C0018203","C0018553","C0018609","C0019202","C0019562","C0020179","C0020497","C0020725","C0021171","C0022283","C0022541","C0022595","C0022716","C0023374","C0023806","C0024454","C0024790","C0025267","C0027127","C0027341","C0027819","C0027832","C0027859","C0028326","C0028860","C0029455","C0030246","C0031269","C0031900","C0033770","C0034960","C0035372","C0036391","C0037052","C0039445","C0043194","C0043459","C0079588","C0079661","C0085132","C0085261","C0085390","C0085548","C0152101","C0162359","C0162671","C0162672","C0175691","C0175699","C0175701","C0175702","C0206115","C0206657","C0220662","C0220704","C0220726","C0220987","C0221026","C0221055","C0221757","C0221759","C0235833","C0238286","C0238288","C0238357","C0238358","C0242292","C0242387","C0265215","C0265216","C0265223","C0265224","C0265234","C0265241","C0265245","C0265246","C0265252","C0265257","C0265275","C0265281","C0265286","C0265329","C0265338","C0265344","C0265354","C0265363","C0265965","C0266526","C0268123","C0268130","C0268225","C0268226","C0268233","C0268255","C0268263","C0268296","C0268297","C0268414","C0268416","C0268465","C0268542","C0268547","C0268548","C0268575","C0268621","C0268631","C0270853","C0270972","C0271091","C0271093","C0271829","C0272199","C0272322","C0272324","C0282525","C0339537","C0342544","C0342731","C0342849","C0342871","C0346072","C0346421","C0393547","C0393814","C0398562","C0398764","C0399378","C0410203","C0410204","C0410529","C0431401","C0431406","C0432219","C0432253","C0473579","C0546125","C0546264","C0549463","C0599973","C0751156","C0751202","C0751753","C0751779","C0751781","C0751783","C0751785","C0751951","C0752353","C0752354","C0795864","C0795907","C0795950","C0796016","C0796147","C0812437","C0859976","C0917796","C1136041","C1260899","C1263858","C1264039","C1264041","C1282968","C1282971","C1282974","C1282975","C1291245","C1318558","C1328349","C1507149","C1510455","C1510479","C1720416","C1720864","C1832615","C1833699","C1834523","C1834558","C1834674","C1836050","C1836602","C1836727","C1837028","C1837065","C1837206","C1837371","C1839259","C1840364","C1842036","C1844678","C1845102","C1846496","C1846722","C1847800","C1848030","C1848533","C1849435","C1849678","C1850168","C1850510","C1850625","C1851286","C1851536","C1852085","C1853258","C1855465","C1856061","C1856974","C1857762","C1857829","C1858051","C1858496","C1859317","C1860808","C1861481","C1862472","C1863081","C1864840","C1864872","C1864887","C1864902","C1864923","C1865070","C1868617","C1956097","C1959626","C1969084","C1970009","C2675369","C2676732","C2677897","C2677903","C2700265","C2717836","C2720163","C2746069","C2751325","C2930820","C2930895","C2930918","C2931042","C2931163","C2931189","C2931540","C2931645","C2931688","C2931689","C2931753","C2931760","C2931781","C2931803","C2931840","C2931850","C2931860","C2931893","C2931894","C2936346","C2936781","C2936785","C2936880","C2936906","C2936907","C2936915","C2936916","C2973527","C3179239","C3266101","C3472621","C3501835","C3645536","C3669122","C3854181"] return count(path)
