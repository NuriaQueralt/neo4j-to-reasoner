####
# trying official python client

from neo4j.v1 import GraphDatabase, basic_auth
import yaml
import json
import re
import argparse
import sys

### TODO: Need to restrict this list to *genetic* diseases by parsing http://www.orphadata.org/data/xml/en_product6.xml
# temporary fix via shell programming hack...
rareDiseaseCUIList = '["C0000744","C0001080","C0001193","C0001206","C0002066","C0002736","C0002895","C0002986","C0004135","C0004779","C0005859","C0006845","C0007965","C0008928","C0010314","C0010674","C0012236","C0013364","C0013481","C0013581","C0013903","C0014848","C0016037","C0016667","C0016719","C0016788","C0017922","C0017924","C0017925","C0017926","C0018203","C0018553","C0018609","C0019202","C0019562","C0020179","C0020497","C0020725","C0021171","C0022283","C0022541","C0022595","C0022716","C0023374","C0023806","C0024454","C0024790","C0025267","C0027127","C0027341","C0027819","C0027832","C0027859","C0028326","C0028860","C0029455","C0030246","C0031269","C0031900","C0033770","C0034960","C0035372","C0036391","C0037052","C0039445","C0043194","C0043459","C0079588","C0079661","C0085132","C0085261","C0085390","C0085548","C0152101","C0162359","C0162671","C0162672","C0175691","C0175699","C0175701","C0175702","C0206115","C0206657","C0220662","C0220704","C0220726","C0220987","C0221026","C0221055","C0221757","C0221759","C0235833","C0238286","C0238288","C0238357","C0238358","C0242292","C0242387","C0265215","C0265216","C0265223","C0265224","C0265234","C0265241","C0265245","C0265246","C0265252","C0265257","C0265275","C0265281","C0265286","C0265329","C0265338","C0265344","C0265354","C0265363","C0265965","C0266526","C0268123","C0268130","C0268225","C0268226","C0268233","C0268255","C0268263","C0268296","C0268297","C0268414","C0268416","C0268465","C0268542","C0268547","C0268548","C0268575","C0268621","C0268631","C0270853","C0270972","C0271091","C0271093","C0271829","C0272199","C0272322","C0272324","C0282525","C0339537","C0342544","C0342731","C0342849","C0342871","C0346072","C0346421","C0393547","C0393814","C0398562","C0398764","C0399378","C0410203","C0410204","C0410529","C0431401","C0431406","C0432219","C0432253","C0473579","C0546125","C0546264","C0549463","C0599973","C0751156","C0751202","C0751753","C0751779","C0751781","C0751783","C0751785","C0751951","C0752353","C0752354","C0795864","C0795907","C0795950","C0796016","C0796147","C0812437","C0859976","C0917796","C1136041","C1260899","C1263858","C1264039","C1264041","C1282968","C1282971","C1282974","C1282975","C1291245","C1318558","C1328349","C1507149","C1510455","C1510479","C1720416","C1720864","C1832615","C1833699","C1834523","C1834558","C1834674","C1836050","C1836602","C1836727","C1837028","C1837065","C1837206","C1837371","C1839259","C1840364","C1842036","C1844678","C1845102","C1846496","C1846722","C1847800","C1848030","C1848533","C1849435","C1849678","C1850168","C1850510","C1850625","C1851286","C1851536","C1852085","C1853258","C1855465","C1856061","C1856974","C1857762","C1857829","C1858051","C1858496","C1859317","C1860808","C1861481","C1862472","C1863081","C1864840","C1864872","C1864887","C1864902","C1864923","C1865070","C1868617","C1956097","C1959626","C1969084","C1970009","C2675369","C2676732","C2677897","C2677903","C2700265","C2717836","C2720163","C2746069","C2751325","C2930820","C2930895","C2930918","C2931042","C2931163","C2931189","C2931540","C2931645","C2931688","C2931689","C2931753","C2931760","C2931781","C2931803","C2931840","C2931850","C2931860","C2931893","C2931894","C2936346","C2936781","C2936785","C2936880","C2936906","C2936907","C2936915","C2936916","C2973527","C3179239","C3266101","C3472621","C3501835","C3645536","C3669122","C3854181"]'

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
parser.add_argument("-s", "--start", required = True, dest = "start", help = "starting node")
parser.add_argument("-t", "--nodetype", required = False, dest = "nodetype", help = "node type (name/cui)", default="name")
parser.add_argument("-l", "--limit", required = False, dest = "limit", help = "limit on number of records", default=1000000)
parser.add_argument("-p", "--pathlength", required = False, dest = "pathlength", help = "max path length", default=2)

args = parser.parse_args()

if(args.format not in ["json","yaml","json_text"]):
   sys.stderr.write("Invalid format. Exiting.\n")
   exit()

# initialize neo4j
driver = GraphDatabase.driver("bolt://localhost:7690")
session = driver.session()
output = []

# top level loop over path lengths
for pathLength in range(1,int(args.pathlength)):
    path = "[]-()-" * pathLength
    if( args.nodetype == "name" ):
        query = 'MATCH path=(source:Disorders)-'+path+'[]-(target:Disorders) where source.name starts with "'+args.start.lower()+'" AND target.cui in ' + rareDiseaseCUIList + ' return path'
    elif( args.nodetype == "cui" ):
        query = 'MATCH path=(source:Disorders)-'+path+'[]-(target:Disorders) where source.cui = "'+args.start+'" AND target.cui in '+rareDiseaseCUIList+' return path'
    else :
        sys.stderr.write("Error with nodetype.\n")
        exit()
    
    if args.limit is not None:
        query = query + ' limit ' + str(args.limit)
    
    sys.stderr.write("QUERY: "+query+"\n")
    result = session.run(query)
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
