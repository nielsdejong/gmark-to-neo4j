# gmark-to-neo4j
Converts gMark generated graphs and queries into a format supported by Neo4j for import.

This script converts a gMark output graph into a format that is accepted by the Neo4j importer.
In addition, it converts gMark output Cypher queries into a JSON format that is accepted by Neo4j benchmarking tools.

It has three main functionalities:
1. We convert the gMark output edges file to CSV and add header information that Neo4j can understand.
2. We explicitly tell Neo4j which label belongs to which node ID, rather than the implicit way this is defined in gMark.
3. The translated gMark queries are put in a nice JSON file that the Neo4j benchmarking suite accepts.

## How to run the Script
Make sure to run the script as follows:
>`converter.py "gMark output graph file" "gMark graph schema file" "gMark output queries folder"`

On one of the example gMark use-cases the command will look like this:
>`python converter.py "demo/play/play-graph.txt0.txt", "/use-cases/test.xml", "demo/play/play-translated/"`

Output files (`nodes.csv` and `relationships.csv`) will be created in the same folder as this script.
