# -*- coding: utf-8 -*-
# Generates a correlated data graph.
import sys
import csv
import os
import json
from lxml import etree
import re
import random

if(len(sys.argv) != 1):
    print("Wrong number of arguments! You currently have "+ str(len(sys.argv)-1)+" arguments, but need zero.")
    print("Make sure to run the script as follows:")
    print()
    print("Output files (nodes.csv, relationships.csv & queries.json) will be created in the same folder as this script.")
else:

    # 1. This is where we convert the edges to CSV.
    #total_relationship_count = 5000
    max_query_length = 10
    nodes_per_label = 1000
    print("Generating some edges...")
    with open('relationships.csv', 'w') as csvfile:
        rel_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        rel_writer.writerow( [':START_ID', ':END_ID', ':TYPE'])

        #(0...1999) = A
        #(2000...3999) = B        
        #(4000...5999) = C
        #(6000...7999) = D
        
        #(:A)-[:X]->(:B)
        print("length","edges   ","in_path", "loose")
        for query_length in range(0,max_query_length):

            #nodes_count_part_of_path = nodes_per_label-(100*(query_length)) #- (0 - query_length)
            #rel_count_not_in_path = nodes_per_label - nodes_count_part_of_path  - (0 - query_length)
            nodes_count_part_of_path = (nodes_per_label)-(100*(query_length)) 
            rel_count_not_in_path = nodes_per_label - nodes_count_part_of_path  - (  query_length)
            for x in range(0, nodes_count_part_of_path): 
                # part of the longer path
                start_node_id = query_length * nodes_per_label + x 
                end_node_id = (1 + query_length) * nodes_per_label + x
                edge_label =  "x"+str(query_length)
                rel_writer.writerow([start_node_id,end_node_id,edge_label])
            
            for x in range(0, rel_count_not_in_path): 
                # not part of any path. but we still want to make sure #(:A)-[:X]-(:B) = 1000 to fool the old estimator
                start_node_id = query_length * nodes_per_label + (nodes_per_label - query_length - 1) 
                end_node_id = (1 + query_length) * nodes_per_label + (nodes_per_label - query_length - 1) 
                edge_label =  "x"+str(query_length)
                rel_writer.writerow([start_node_id,end_node_id,edge_label])
            
            print(str(query_length+1) +"     ", 
                  str(nodes_count_part_of_path+rel_count_not_in_path) +"     ", 
                  str(nodes_count_part_of_path) +"     ",
                  str(rel_count_not_in_path))
        #(:B)-[:Y]->(:C) 
        # We make sure that 10 of the node ID's are overlapping -->  #(:A)-[:X]->(:B)-[:Y]->(:C)  = 10
    #    for x in range(0, 1000): 
     #       rel_writer.writerow([x+2990,x+4000, "y"])
                    #(:B)-[:Y]->(:C) 
                    
        # We make sure that 750 of the node ID's are overlapping. -->  #(:B)-[:Y]->(:C)-[:Z]->(:D)  = 750
    #    $for x in range(0, 1000): 
        #    rel_writer.writerow([x+4000,x+6000, "z"])
            
    # 2. This is where we explicitly tell Neo4j which label belongs to which node ID.
    print("Generating nodes and their labels...")
    total_node_count = nodes_per_label*(1+max_query_length)
    with open('nodes.csv', 'w') as csvfile:
        array = []
        node_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        node_writer.writerow( ['nodeID:ID',':LABEL'])
        for x in range(0, total_node_count): 
            node_writer.writerow([x, "n" + str(int(x / nodes_per_label))])
            
            
    # 3. Generate some queries.
    def getLength(custom):
        return custom['length']

    def useLinearQueries():
            print("using custom generated queries into a JSON format...")
            with open('queries.json', 'w') as outfile:
                    json_array = []
                    max_length = 10
                    for i in range(0,max_length):
                        json_data = {}
                        #print(i)
                        query = "(n10:n10)"
                        length = i+1
                        for j in range(0, length):
                            query = "-[x" + str(max_length-j-1) +":x" + str(max_length-j-1) +"]->" + query
                            query = "(n"+str(max_length-j-1)+":n" + str(max_length-j-1) +")" + query            
                        query += " RETURN *;"
                        query = "MATCH "+ query
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


    def useCustomGeneratedQueries():
        print("using custom generated queries into a JSON format...")
        with open('queries.json', 'w') as outfile:
                json_array = []
                node_labels = [0,1,2,3]
                for i in range(0,30):
                    json_data = {}
                    #print(i)
                    query = "MATCH "+ "(a0:n" + str(random.choice (node_labels)) +")"
                    length = ((int)(i/3)+1)
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
    
    # Pick one of the two here.
    #useCustomGeneratedQueries()
    #usegMarkGeneratedQueries()
    useLinearQueries()
    print("Done!")  
                



