# -*- coding: utf-8 -*-
# This script converts a gMark output graph into a format that is accepted by the Neo4j importer.
# In addition, it converts gMark output Cypher queries into a JSON format that is accepted by Neo4j benchmarking tools.
# Built by Niels de Jong - June 2018
import sys
import csv
import os
import json
from lxml import etree

if(len(sys.argv) != 4):
    print("Wrong number of arguments! You currently have "+ str(len(sys.argv)-1)+" arguments, but need 3.")
    print("Make sure to run the script as follows:")
    print('converter.py "gMark output graph file" "gMark graph schema file" "gMark output queries folder"')
    print()
    print('Example command:')
    print('>python converter.py "demo/play/play-graph.txt0.txt", "/use-cases/test.xml", "demo/play/play-translated/"')
    #"C://Users//Niels de Jong//Desktop//gmark//demo//play//play-graph.txt0.txt" 
    #"C://Users//Niels de Jong//Desktop//gmark//use-cases//test.xml" 
    #"C://Users//Niels de Jong//Desktop//gmark//demo//play//play-translated"
    print()
    print("Output files (nodes.csv, relationships.csv & queries.json) will be created in the same folder as this script.")
else:
    graph_file = sys.argv[1]
    gmark_schema_file = sys.argv[2]
    gmark_queries_folder = sys.argv[3]
    
    # 1. This is where we convert the edges file to CSV and add header information that Neo4j can understand.
    print("Reading and converting the gMark output edges...")
    with open('relationships.csv', 'w') as csvfile:
        rel_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        rel_writer.writerow( [':START_ID', ':END_ID', ':TYPE'])
        with open(graph_file, "r") as ins:
            for line in ins:
                split_line = line.rstrip().split(' ')
                rel_writer.writerow([split_line[0], split_line[2], split_line[1]])
    
    # 2. This is where we explicitly tell Neo4j which label belongs to which node ID, rather than the implicit way this is defined in gMark.
    print("Resolving implicit node labels by their ID's...")
    with open('nodes.csv', 'w') as csvfile:
        array = []
        node_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        node_writer.writerow( ['nodeID:ID',':LABEL'])
        
        xml_tree = etree.parse(gmark_schema_file)
        total_node_count = int(xml_tree.find(".//nodes").text)
        node_proportions = xml_tree.findall(".//types/proportion")
                
        limit = 0
        node_id_limits = []
        
        # Find at which ID's the label of the node changes.
        for proportion in node_proportions:
            limit += total_node_count * float(proportion.text)
            node_id_limits.append(limit)
            
        # This loop assigns the correct label based on the node ID.
        for x in range(0, total_node_count):
            node_label_id = 0
            for limit in node_id_limits:
                if(x >= limit):
                    node_label_id += 1  
            node_writer.writerow([x, node_label_id])
            
        # Inform the user about them messing up the gMark schema.
        # if(len(xml_tree.find(".//generator/size").text) != '1'):
        # print("[WARNING] Your gMark schema specifies the generation of more than one graph. This is not supported by this script, the generated files might be wrong.")
        if(len(xml_tree.findall(".//types/fixed")) > 0):
            print("[WARNING] Your gMark schema contains a node type with a fixed size. This is not supported by this script, the generated files might be wrong.")
            
    # 3. This is where the translated gMark queries are put in a nice JSON file that the Neo4j benchmarking suite accepts.
    print("Converting gMark queries to JSON format...")
    with open('queries.json', 'w') as outfile:
        json_array = []
        for file in os.listdir(gmark_queries_folder):
            if file.endswith(".cypher"):
                json_data = {}
                with open(os.path.join(gmark_queries_folder, file), "r") as ins:
                    for line in ins:
                        json_data['name'] = file
                        json_data['queryString'] = line.rstrip()
                json_array.append(json_data)
        json.dump(json_array, outfile)
    print("Done!")
                



