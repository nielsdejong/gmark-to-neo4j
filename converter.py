# -*- coding: utf-8 -*-
# This script converts a gMark output graph into a format that is accepted by the Neo4j importer.
# In addition, it converts gMark output Cypher queries into a JSON format that is accepted by Neo4j benchmarking tools.
# Built by Niels de Jong - June 2018
import sys
import csv
import os
import json
from lxml import etree
import re
import random

if(len(sys.argv) != 4):
    print("Wrong number of arguments! You currently have "+ str(len(sys.argv)-1)+" arguments, but need 3.")
    print("Make sure to run the script as follows:")
    print('converter.py "gMark output graph file" "gMark graph schema file" "gMark output queries folder"')
    print()
    print('Example command:')
    print('>python converter.py "demo/play/play-graph.txt0.txt", "/use-cases/test.xml", "demo/play/play-translated/"')
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
                rel_writer.writerow([split_line[0], split_line[2], "p"+split_line[1]])
    
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
        node_labels = []
        
        i = 0
        # Find at which ID's the label of the node changes.
        for proportion in node_proportions:
            limit += total_node_count * float(proportion.text)
            node_labels += str(i)
            node_id_limits.append(limit)
            i+=1
            
        # This loop assigns the correct label based on the node ID.
        for x in range(0, total_node_count):
            node_label_id = 0

            for limit in node_id_limits:
                if(x >= limit):
                    node_label_id += 1  
            node_writer.writerow([x, "n" + str(node_label_id)])
            
            
        # This measns that we probably assign wrong labels to nodes
        if(len(xml_tree.findall(".//types/fixed")) > 0):
            print("[WARNING] Your gMark schema contains a node type with a fixed size. This is not supported by this script, the generated files might be wrong.")
            
    # 3. This is where the translated gMark queries are put in a nice JSON file that the Neo4j benchmarking suite accepts.
    
    def getLength(custom):
        return custom['length']

    def useCustomGeneratedQueries():
        print("using custom generated queries into a JSON format...")
        with open('queries.json', 'w') as outfile:
                json_array = []
                for i in range(0,30):
                    json_data = {}
                    length = ((int)(i/3)+1)
                    print(i)
                    query = "MATCH "+ "(a0:n" + str(10-length) +")"
                    
                    #for j in range(1, length+1):
                    #    if(random.choice([True])):
                    #        query += "-[:x" + str(10-length+j-1) +"]->"
                    #    else:
                    #        query += "<-[:p" + str(random.choice (node_labels)) +"]-"
                    #    query += "(a"+str(j)+":n" + str(10-length+j) +")"             
                    #query += " RETURN *;"
                    
                    query = "MATCH "+ "(a0:n" + str(random.choice (node_labels)) +")"
                    
                    for j in range(1, length+1):
                        if(random.choice([True, False])):
                            query += "-[:p" + str(random.choice (node_labels)) +"]->"
                        else:
                            query += "<-[:p" + str(random.choice (node_labels)) +"]-"
                        query += "(a"+str(j)+":n" + str(random.choice (node_labels)) +")"             
                    query += " RETURN COUNT(*);"
                    
                    json_data['queryString'] = query
                    json_data['name'] = "query "+ str(i) + " (len="+ str(length) +")"
                    json_data['parameterFile'] = "query_1_param.txt"
                    json_data['length'] = length
                    print(json_data['name'])                    
                    print(json_data['queryString'])
                    json_array.append(json_data)
                    #MATCH (x0:n1)<-[:p3]-(:n2)-[:p0]->(:n1)-[:p0]->(:n2)-[:p1]->(:n2)-[:p1]->(:n1)<-[:p3]-(x1:n3) RETURN *       ;
                json_array = sorted(json_array, key=getLength)
                json.dump(json_array, outfile)
    def usegMarkGeneratedQueries():
        print("Converting gMark queries to JSON format...")
        with open('queries.json', 'w') as outfile:
            json_array = []
            for file in os.listdir(gmark_queries_folder):
                if file.endswith(".cypher"):
                    json_data = {}
                    with open(os.path.join(gmark_queries_folder, file), "r") as ins:
                        for line in ins:
                            # The name of the query contains the number of relationships (length)
                            json_data['name'] = file + "(len="+ str(line.count("[")) +")"
                            json_data['parameterFile'] = "query_1_param.txt"
                            json_data['length'] =line.count("[")
    
                            #This python magic makes the generated query into valid cypher and adds random node labels to pattern query nodes.
                            json_data['queryString'] = re.sub(r'\)', lambda x: ":n" + str(random.choice (node_labels)) +")", line.rstrip()).replace("UNION","").replace("\"true\"","*").replace("LIMIT 1","")
                            print(json_data['name'])                    
                            print(json_data['queryString'])
                        json_array.append(json_data)
            json_array = sorted(json_array, key=getLength)
            json.dump(json_array, outfile)
    
    # Pick one of the two here.
    useCustomGeneratedQueries()
    #usegMarkGeneratedQueries()
    print("Done!")  
                



