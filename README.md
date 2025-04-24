- Evaluation Results
Eval 1, Eval 2, Eval 3, Eval 4, Eval 5:
These are the TruLens evaluation outputs and feedback logs for each query batch.

Query5.1 to Query5.5:
These are rerun results for Query 5, used to assess variation in LLM responses.

- System Code
eval_llama & evaluate(1).py:
Script for running evaluations using LLaMa-generated responses.

query_neo4j.py:
Handles query execution and retrieval from the Neo4j knowledge graph.

- Graph Data
graph_export.cypher:
A Cypher script containing the full exported Neo4j graph, including nodes, relationships, and constraints. Can be used to recreate the graph in a new Neo4j instance.

Ground Truth
ground_truth.txt:
Manually validated ground truth statements, extracted from source articles. Used for factuality comparison during evaluation.

Requires Python 3.10, Neo4j Desktop, TruLens, Mistral, Llama installed
