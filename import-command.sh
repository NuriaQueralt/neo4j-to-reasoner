#!/bin/bash

NODEFILE='input/nodes_2017-11-28.csv'
RELFILE='input/edges_2017-11-05.csv'

/home/mmayers/software/neo4j-community-3.1.3/bin/neo4j-admin import --nodes $NODEFILE --relationships $RELFILE --report-file='import.report'
