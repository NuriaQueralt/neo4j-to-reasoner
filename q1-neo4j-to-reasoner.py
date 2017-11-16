####
# trying official python client

from neo4j.v1 import GraphDatabase, basic_auth
import yaml
import json
import re
import argparse
import sys

### TODO: Need to restrict this list to *genetic* diseases by parsing http://www.orphadata.org/data/xml/en_product6.xml
rareDiseaseCUIList = '["C1846722","C1836307","C0270726","C1836315","C0024748","C1855217","C1855188","C0268225","C2931840","C0268263","C1720864","C0342849","C2931893","C0206307","C3542499","C1857762","C1856974","C1264039","C0010690","C1969084","C1282968","C0268255","C2936785","C0016788","C1264040","C0017921","C1282974","C0017922","C2936915","C1282971","C0017924","C2936916","C1282975","C0017923","C1563715","C1264041","C0017926","C1861481","C0017925","C0024790","C0346104","C0406355","C0029455","C1833699","C0024137","C0023521","C2973527","C0399378","C0026709","C2745953","C0018036","C0020725","C2931894","C1858032","C0023806","C0268226","C1850510","C0238286","C0037052","C0033788","C0473579","C0012602","C0032371","C0393720","C0036161","C0011644","C0852007","C0079588","C2717836","C2720163","C0393725","C0751791","C0085132","C0278193","C0041408","C0242526","C0016719","C0005283","C0002312","C1456873","C0010674","C0917713","C3542021","C1299598","C0410189","C0162671","C0238288","C0022541","C2678065","C0338430","C0162672","C0751951","C0206157","C0338430","C1836727","C1868617","C0221055","C0030246","C2931688","C2677903","C1274788","C0027127","C2936781","C0266599","C0002986","C1845102","C0035372","C0162635","C0270853","C2930918","C0019562","C1858496","C0085548","C0265354","C0024796","C0002736","C0004135","C0032580","C0020179","C0751783","C0344061","C0013080","C0023522","C2713319","C1851536","C1832112","C0012236","C0220704","C0795907","C2936346","C3266101","C0431406","C0002895","C1840364","C0028860","C1864902","C0035335","C0025267","C0016667","C0751156","C0035436","C0032897","C0221026","C0026705","C2718304","C0023786","C2713321","C0019202","C0271091","C1844678","C0024140","C0004623","C0271093","C1855465","C0043194","C0175702","C1956097","C0001080","C1848533","C0751781","C0035934","C0013338","C0271561","C1865134","C2931540","C2673649","C0393547","C0752353","C1839259","C0268542","C1866719","C1866727","C1833603","C0751202","C1849053","C0265344","C0026946","C0020630","C0042769","C0042740","C0410529","C0030499","C0747256","C1704375","C3536983","C2363065","C0917796","C0024454","C0265216","C0027831","C0266526","C1842531","C1864887","C0018203","C0339537","C2931753","C1328349","C0206657","C0027832","C0027859","C1136041","C0751779","C0162359","C1848030","C0016037","C0553586","C0004779","C0812437","C0028326","C0010314","C2931860","C0268296","C0010691","C0268646","C0023374","C0085390","C0342773","C0342784","C0393814","C0221757","C3501835","C2700265","C0599973","C0079661","C0265246","C1847800","C0238357","C2930895","C0036391","C0220726","C0024530","C0238358","C0238357","C0220663","C0265234","C0039445","C0175699","C2931888","C0220658","C0265303","C0031269","C0206115","C2931803","C0043459","C0175713","C3179239","C0000744","C0085280","C0007965","C0265493","C0010324","C0018553","C0265252","C0549463","C0272324","C0272322","C0242292","C0022716","C0265275","C0272199","C0796016","C0265215","C0013903","C1263858","C0036323","C0004775","C1507149","C2931163","C0004903","C0001193","C1510455","C0342544","C1720416","C0398764","C1845069","C1856899","C0546125","C0078918","C0546123","C1836050","C2677897","C0432253","C1836602","C1850168","C2936880","C2676732","C1970009","C0242387","C0265241","C0751785","C0008924","C0270972","C0345210","C0079541","C3711749","C0859976","C0014848","C0345218","C1845068","C2675369","C2931811","C0152096","C2931705","C2675185","C2936830","C0152095","C0398692","C0221027","C0265428","C1837065","C0206680","C0268297","C3669122","C0346109","C0398562","C1860808","C0022595","C1857829","C0265338","C0236791","C0545080","C1266191","C0280028","C0002894","C0043379","C3266843","C1540912","C3472621","C0432443","C2931249","C0432442","C0346421","C1850184","C2936907","C1318558","C1842036","C0034960","C0265497","C2937419","C1837028","C0268147","C2931845","C1837028","C0272238","C1864923","C0016952","C0410203","C0432218","C1834674","C0410204","C3645536","C2930820","C0021171","C0022283","C0795868","C3267076","C0796072","C1834558","C0282525","C0002066","C2931645","C0001206","C0346072","C1838120","C0268631","C0342731","C1959626","C0265245","C0268130","C0220987","C0796147","C2931760","C0175701","C0027341","C0268575","C0018809","C0795864","C1849401","C0265496","C1863081","C0265475","C2931809","C0008928","C2930803","C0265223","C1865070","C0524528","C1859591","C1853919","C1858051","C0006845","C1837206","C1859317","C1837371","C1291245","C0268416","C0268314","C0268621","C1853258","C1850865","C1865695","C1843706","C1834523","C1862472","C1836862","C1260899","C2931850","C2751325","C1864840","C0020497","C1850625","C0005859","C0268548","C1866728","C0431401","C1866507","C1863878","C1864872","C0220662","C1852085","C1859721","C0027877","C1864670","C0022340","C1834523","C0796172","C0265257","C1856272","C0265965","C0013364","C0175691","C0265286","C0342436","C0271889","C0011436","C0034345","C2936911","C0263390","C1856061","C0574108","C0268418","C0026755","C0751753","C0268547","C2931781","C0268123","C0268465","C2936906","C0010964","C0345419","C0795950","C1832615","C2931685","C0152101","C0268059","C0235833","C0020256","C0342418","C0018609","C2931042","C0878544","C0268233","C0265240","C0432130","C0546264","C0265224","C0431289","C2931167","C0013481","C1851920","C0015923","C0814154","C2985290","C3146244","C0013581","C1851286","C2746069","C0345335","C3714581","C0795690","C0027819","C2931189","C3854181","C0265329","C0265281","C0039743","C0752354","C2931689","C0271829","C0268414","C0265449","C1849435","C1846496","C0432219","C1849678","C0342871","C0033770","C0265363","C0085261","C0221759","C1510479","C0031900"]'

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
