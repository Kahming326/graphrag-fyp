import subprocess
from neo4j import GraphDatabase

# Initialize Neo4j connection
uri = "bolt://localhost:7687"
username = "neo4j"
password = "research"

driver = GraphDatabase.driver(uri, auth=(username, password))

def get_rich_graph_data(query_type):
    """
    Query Neo4j for richer metadata based on query type.
    """
    if query_type == "transformer_architecture":
        query = """
        MATCH (a:Author)-[:WROTE]->(p:Paper {title: "Attention is All You Need"})
        OPTIONAL MATCH (p)-[:INTRODUCES]->(t:Concept {name: "Transformer"})
        OPTIONAL MATCH (t)-[:USES]->(c:Concept)
        RETURN a.name AS Author, 
               p.title AS Paper, 
               COLLECT(DISTINCT c.name) AS Concepts
        """
    elif query_type == "self_attention":
        query = """
        MATCH (p:Paper {title: "Attention is All You Need"})-[:INTRODUCES]->(t:Concept {name: "Self-Attention"})
        OPTIONAL MATCH (t)-[:USES|CONSISTS_OF|ACHIEVES]->(c:Concept)
        RETURN p.title AS Paper, 
               t.name AS Mechanism,
               COLLECT(DISTINCT c.name) AS RelatedConcepts
        """
    elif query_type == "multi_head_attention":
        query = """
        MATCH (p:Paper {title: "Attention is All You Need"})-[:INTRODUCES]->(t:Concept {name: "Multi-Head Attention"})
        OPTIONAL MATCH (t)-[:USES|CONSISTS_OF|ACHIEVES]->(c:Concept)
        RETURN p.title AS Paper, 
               t.name AS Mechanism,
               COLLECT(DISTINCT c.name) AS RelatedConcepts
        """
    else:
        query = """
        MATCH (a:Author)-[:WROTE]->(p:Paper {title: "Attention is All You Need"})
        RETURN a.name AS Author, p.title AS Paper
        """
    
    with driver.session() as session:
        result = session.run(query)
        data = result.data()
    
    print(f"Graph Data: {data}")  # Debugging: See what's being fetched
    return data

def construct_query_for_question(question, graph_data):
    """
    Construct a relevant query string based on the user question and graph data.
    """
    # Determine query type based on the question
    if "Transformer architecture" in question or "Transformer model" in question:
        query_type = "transformer_architecture"
    elif "Self-Attention" in question:
        query_type = "self_attention"
    elif "Multi-Head Attention" in question:
        query_type = "multi_head_attention"
    else:
        query_type = "general"
    
    # Format the graph data into a readable context
    context = []
    
    for record in graph_data:
        record_info = []
        for key, value in record.items():
            if isinstance(value, list):
                if value:  # Check if list is not empty
                    formatted_value = ", ".join(value)
                    record_info.append(f"{key}: {formatted_value}")
            else:
                record_info.append(f"{key}: {value}")
        
        context.append("; ".join(record_info))
    
    context_str = "\n".join(context) if context else "No specific information found in the knowledge graph."
    
    # Construct the query string with context
    query_string = f"""
    You are an AI assistant with expertise in natural language processing and deep learning.
    Answer the following question about the Transformer architecture based on this context:

    Context from knowledge graph:
    {context_str}

    Question: {question}

    Provide a comprehensive yet concise answer focusing only on what's directly relevant to the question.
    """
    
    return query_string

def chunk_text(text, max_tokens=3000):
    """
    Splits the text into chunks that respect the token limit for Llama.
    """
    tokens = text.split()  # Simple tokenization (space-based)
    chunks = []
    
    while len(tokens) > max_tokens:
        chunk = tokens[:max_tokens]
        chunks.append(" ".join(chunk))
        tokens = tokens[max_tokens:]  # Move to the next chunk
    
    # Add any remaining tokens as the final chunk
    if tokens:
        chunks.append(" ".join(tokens))
    
    return chunks

def get_llama_response(query_string):
    """
    Sends the structured query to Llama using subprocess and logs the output.
    """
    safe_query = query_string.replace('"', '\\"')
    command = f'ollama run llama3.1:70b-instruct-q2_K "{safe_query}" 2>nul'  # Redirect stderr
    query_chunks = chunk_text(safe_query, max_tokens=3000)

    all_responses = []

    for chunk in query_chunks:
        command = f'ollama run llama3.1:70b-instruct-q2_K "{chunk}"'
        
        try:
            # Use a timeout to prevent hanging
            process = subprocess.run(
                command, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                shell=True, 
                text=True,
                encoding='utf-8',
                errors='replace',
            )
            
            if process.stderr:
                print(f"Error: {process.stderr}")
            if process.stdout:
                all_responses.append(process.stdout)
        except Exception as e:
            print(f"Error executing command: {e}")
            all_responses.append(f"Error: {e}")

    final_response = "\n".join(all_responses)

    try:
        with open('llama_output.log', 'w', encoding='utf-8') as log_file:
            log_file.write(f"Llama Response:\n{final_response}\n")
    except Exception as e:
        print(f"Failed to write log: {e}")

    return final_response  # Return the actual response