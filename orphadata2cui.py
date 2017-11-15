#
# given a json dump from orphadata, extract the UMLS CUIs
# output format has two columns
#   1: OrphaNumber
#   2: UMLS CUI
#

import requests
import json
import pprint

orphadataURL = "http://www.orphadata.org/data/export/en_product1.json"

response= requests.get(orphadataURL)
data = json.loads(response.text)   

count = 0
for d in data['JDBOR'][0]['DisorderList'][0]['Disorder']:
    #print("\n********DATA********\n"+str(d))
    #print("OrphaNumber: "+d['OrphaNumber'])
    #print("Label: "+d['Name'][0]['label'])
    #print("Count: "+d['ExternalReferenceList'][0]['count'])
    if int(d['ExternalReferenceList'][0]['count']) == 0:
        #print("SKIPPING...")
        continue
    for e in d['ExternalReferenceList'][0]['ExternalReference']:
        #print("E ("+e['Source']+"): "+e['Reference'])
        if(e['Source']=="UMLS"):
            print(d['OrphaNumber']+"\t"+e['Reference'])
    count = count + 1
    if( count == 500 ):
        break
