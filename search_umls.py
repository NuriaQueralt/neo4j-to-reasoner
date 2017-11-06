#################################################################################
# usage of the script
# usage: python search-terms.py -k APIKEY -v VERSION -s STRING
# see https://documentation.uts.nlm.nih.gov/rest/search/index.html for full docs
# on the /search endpoint
# 
# originally based on 
#   https://github.com/HHS/uts-rest-api/blob/master/samples/python/search-terms.py
#################################################################################

from __future__ import print_function
from Authentication import *
import requests
import json
import argparse
import yaml
import pandas as pd
import urllib3

urllib3.disable_warnings()

parser = argparse.ArgumentParser(description='process user given parameters')
parser.add_argument("-k", "--apikey", required = False, dest = "apikey", help = "enter api key from your UTS Profile")
parser.add_argument("-v", "--version", required =  False, dest="version", default = "current", help = "enter version example-2015AA")
parser.add_argument("-s", "--string", required =  False, dest="string", help = "enter a search term, like 'diabetic foot'")
parser.add_argument("-S", "--settingsFile", required =  False, dest="settingsFile", help = "enter a path to a settings file (YAML)")
parser.add_argument("-d", "--debug", required =  False, dest="debug", action="store_true", default = False, help = "enter debug mode")
parser.add_argument("-i", "--inputFile", required =  False, dest="inputFile", help = "specify an input file of search terms (instead of -s flag)")
parser.add_argument("-o", "--outputFile", required =  False, dest="outputFile", help = "specify an output file to which to the results should be written")
parser.add_argument("-H", "--header", required =  False, dest="header", default = None, action="store_true", help = "if an inputFile is specified, this flag indicates a header line exists")

args = parser.parse_args()
if args.settingsFile:
    f = open(args.settingsFile,'r')
    settings = yaml.load(f)
    apikey = settings['UMLS_API_KEY']
    f.close()
else: 
    apikey = args.apikey
version = args.version
string = args.string
debug = args.debug
header = args.header
inputFile = args.inputFile
outputFile = args.outputFile

# convert header for pandas
if(header==True):
    header=0

uri = "https://uts-ws.nlm.nih.gov"
content_endpoint = "/rest/search/"+version

if(debug):
    print("API key: ", apikey)
    print("string: ", string)
    print("version: ", version)
    print("debug: ", debug)
    print("header: ", header)
    print("inputFile: ", inputFile)
    print("outputFile: ", outputFile)

if( apikey == None ):
    exit("No apikey specified. Exiting.")

def getUMLSid(string):
    ##generate a new service ticket for each page if needed

    ticket = AuthClient.getst(tgt)
    query = {'string':string,'ticket':ticket, 'pageNumber':'1'}
    #query['includeObsolete'] = 'true'
    #query['includeSuppressible'] = 'true'
    #query['returnIdType'] = "sourceConcept"
    #query['sabs'] = "SNOMEDCT_US"
    r = requests.get(uri+content_endpoint,params=query)
    r.encoding = 'utf-8'
    items  = json.loads(r.text)
    jsonData = items["result"]
    #print (json.dumps(items, indent = 4))

#    print("Results for page " + str(pageNumber)+"\n")
    
    for result in jsonData["results"]:
        
      '''
      try:
        print("ui: " + result["ui"])
      except:
        NameError
      try:
        print("uri: " + result["uri"])
      except:
        NameError
      '''
      try:
        name = result["name"]
      except:
        NameError
      if( debug ):
        print("name: " + result["name"])
      if( string.strip('.,- ').lower() == name.strip('.,- ').lower() ): 
        if( debug ):
          print("MATCHED!")
        try:
          ui = result["ui"]
        except:
          print("NO URI ERROR")
          ui = None
        return(ui)  
      '''
      try:
        print("Source Vocabulary: " + result["rootSource"])
      except:
        NameError
      '''
    
    ##Either our search returned nothing, or we're at the end
    if(debug):
        print("NO MATCH FOUND")
    if jsonData["results"][0]["ui"] == "NONE":
        return(None)
    return(None)


##get at ticket granting ticket for the session
AuthClient = Authentication(apikey)
tgt = AuthClient.gettgt()


if( inputFile ):
    data = pd.read_csv( inputFile, header=header, sep="\t" )
    dataCUI = pd.DataFrame().reindex_like(data)
    dataCUI.is_copy = False

    colNames = list(data)

    for index, row in data.iterrows():
        for col in colNames:
            if(debug):
               print(index, col, row[col])
            #dataCUI.set_value(index,col, getUMLSid( row[col] ))
            ### TODO: create a local cache so same term does not 
            ### need to be repeatedly looked up
            dataCUI[col][index] = getUMLSid( row[col] )

    if(debug):
        print(list(data))
        print(data.head(10))
        print(dataCUI.head(10))

    dataCUI.columns = dataCUI.columns+"CUI"
    outputDF = pd.concat([data.reset_index(drop=True), dataCUI], axis=1)
    if(outputFile):
        ### TODO: change to write output file iteratively so errors do 
        ### not require restarting from the beginning
        outputDF.to_csv(outputFile, sep="\t", index=False)
    else:
        print(outputDF)

elif( string ):
    print(getUMLSid( string ))
else:
    print("Specify either inputFile or string as query")
