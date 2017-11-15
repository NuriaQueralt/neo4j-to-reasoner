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
match path=(source:Disorders)-[r1]-(i1)-[r2]-(i2)-[r3]-(target:Disorders) where source.cui="C0024530" AND target.cui in ["C1846722","C1836307","C0270726","C1836315","C0024748","C1855217","C1855188","C0268225","C2931840","C0268263","C1720864","C0342849","C2931893","C0206307","C3542499","C1857762","C1856974","C1264039","C0010690","C1969084","C1282968","C0268255","C2936785","C0016788","C1264040","C0017921","C1282974","C0017922","C2936915","C1282971","C0017924","C2936916","C1282975","C0017923","C1563715","C1264041","C0017926","C1861481","C0017925","C0024790","C0346104","C0406355","C0029455","C1833699","C0024137","C0023521","C2973527","C0399378","C0026709","C2745953","C0018036","C0020725","C2931894","C1858032","C0023806","C0268226","C1850510","C0238286","C0037052","C0033788","C0473579","C0012602","C0032371","C0393720","C0036161","C0011644","C0852007","C0079588","C2717836","C2720163","C0393725","C0751791","C0085132","C0278193","C0041408","C0242526","C0016719","C0005283","C0002312","C1456873","C0010674","C0917713","C3542021","C1299598","C0410189","C0162671","C0238288","C0022541","C2678065","C0338430","C0162672","C0751951","C0206157","C0338430","C1836727","C1868617","C0221055","C0030246","C2931688","C2677903","C1274788","C0027127","C2936781","C0266599","C0002986","C1845102","C0035372","C0162635","C0270853","C2930918","C0019562","C1858496","C0085548","C0265354","C0024796","C0002736","C0004135","C0032580","C0020179","C0751783","C0344061","C0013080","C0023522","C2713319","C1851536","C1832112","C0012236","C0220704","C0795907","C2936346","C3266101","C0431406","C0002895","C1840364","C0028860","C1864902","C0035335","C0025267","C0016667","C0751156","C0035436","C0032897","C0221026","C0026705","C2718304","C0023786","C2713321","C0019202","C0271091","C1844678","C0024140","C0004623","C0271093","C1855465","C0043194","C0175702","C1956097","C0001080","C1848533","C0751781","C0035934","C0013338","C0271561","C1865134","C2931540","C2673649","C0393547","C0752353","C1839259","C0268542","C1866719","C1866727","C1833603","C0751202","C1849053","C0265344","C0026946","C0020630","C0042769","C0042740","C0410529","C0030499","C0747256","C1704375","C3536983","C2363065","C0917796","C0024454","C0265216","C0027831","C0266526","C1842531","C1864887","C0018203","C0339537","C2931753","C1328349","C0206657","C0027832","C0027859","C1136041","C0751779","C0162359","C1848030","C0016037","C0553586","C0004779","C0812437","C0028326","C0010314","C2931860","C0268296","C0010691","C0268646","C0023374","C0085390","C0342773","C0342784","C0393814","C0221757","C3501835","C2700265","C0599973","C0079661","C0265246","C1847800","C0238357","C2930895","C0036391","C0220726","C0024530","C0238358","C0238357","C0220663","C0265234","C0039445","C0175699","C2931888","C0220658","C0265303","C0031269","C0206115","C2931803","C0043459","C0175713","C3179239","C0000744","C0085280","C0007965","C0265493","C0010324","C0018553","C0265252","C0549463","C0272324","C0272322","C0242292","C0022716","C0265275","C0272199","C0796016","C0265215","C0013903","C1263858","C0036323","C0004775","C1507149","C2931163","C0004903","C0001193","C1510455","C0342544","C1720416","C0398764","C1845069","C1856899","C0546125","C0078918","C0546123","C1836050","C2677897","C0432253","C1836602","C1850168","C2936880","C2676732","C1970009","C0242387","C0265241","C0751785","C0008924","C0270972","C0345210","C0079541","C3711749","C0859976","C0014848","C0345218","C1845068","C2675369","C2931811","C0152096","C2931705","C2675185","C2936830","C0152095","C0398692","C0221027","C0265428","C1837065","C0206680","C0268297","C3669122","C0346109","C0398562","C1860808","C0022595","C1857829","C0265338","C0236791","C0545080","C1266191","C0280028","C0002894","C0043379","C3266843","C1540912","C3472621","C0432443","C2931249","C0432442","C0346421","C1850184","C2936907","C1318558","C1842036","C0034960","C0265497","C2937419","C1837028","C0268147","C2931845","C1837028","C0272238","C1864923","C0016952","C0410203","C0432218","C1834674","C0410204","C3645536","C2930820","C0021171","C0022283","C0795868","C3267076","C0796072","C1834558","C0282525","C0002066","C2931645","C0001206","C0346072","C1838120","C0268631","C0342731","C1959626","C0265245","C0268130","C0220987","C0796147","C2931760","C0175701","C0027341","C0268575","C0018809","C0795864","C1849401","C0265496","C1863081","C0265475","C2931809","C0008928","C2930803","C0265223","C1865070","C0524528","C1859591","C1853919","C1858051","C0006845","C1837206","C1859317","C1837371","C1291245","C0268416","C0268314","C0268621","C1853258","C1850865","C1865695","C1843706","C1834523","C1862472","C1836862","C1260899","C2931850","C2751325","C1864840","C0020497","C1850625","C0005859","C0268548","C1866728","C0431401","C1866507","C1863878","C1864872","C0220662","C1852085","C1859721","C0027877","C1864670","C0022340","C1834523","C0796172","C0265257","C1856272","C0265965","C0013364","C0175691","C0265286","C0342436","C0271889","C0011436","C0034345","C2936911","C0263390","C1856061","C0574108","C0268418","C0026755","C0751753","C0268547","C2931781","C0268123","C0268465","C2936906","C0010964","C0345419","C0795950","C1832615","C2931685","C0152101","C0268059","C0235833","C0020256","C0342418","C0018609","C2931042","C0878544","C0268233","C0265240","C0432130","C0546264","C0265224","C0431289","C2931167","C0013481","C1851920","C0015923","C0814154","C2985290","C3146244","C0013581","C1851286","C2746069","C0345335","C3714581","C0795690","C0027819","C2931189","C3854181","C0265329","C0265281","C0039743","C0752354","C2931689","C0271829","C0268414","C0265449","C1849435","C1846496","C0432219","C1849678","C0342871","C0033770","C0265363","C0085261","C0221759","C1510479","C0031900"] return count(path)
