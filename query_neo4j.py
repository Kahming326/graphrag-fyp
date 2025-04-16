from neo4j import GraphDatabase

# Neo4j Connection Details
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "research")  # Replace with your actual Neo4j credentials

# Initialize the Neo4j driver
driver = GraphDatabase.driver(URI, auth=AUTH)

def query_graph(user_query):
    """
    Query the Neo4j graph based on the user's question.
    Returns structured data about the relevant concepts.
    """
    # Create a session using the driver
    with driver.session() as session:
        # Map the user query to the appropriate Cypher query
        if "key differences between the attention mechanisms" in user_query:
            query = """
            MATCH (attention_paper:Paper {title: "Attention is All You Need"})-[:INTRODUCES]->(transformer:Model {name: "Transformer"})
            MATCH (transformer)-[:USES]->(scaled_dot_attention:Concept {name: "Scaled Dot-Product Attention"})
            MATCH (transformer)-[:USES]->(multi_head_attention:Concept {name: "Multi-Head Attention"})
            MATCH (bert_paper:Paper {title: "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding"})-[:DESCRIBES]->(bert:Model {name: "BERT"})-[:USES]->(bidirectional_attention:Concept {name: "Bidirectional Attention"})
            RETURN 
                attention_paper.title AS transformer_paper,
                transformer.name AS transformer_model,
                scaled_dot_attention.name AS scaled_dot_attention,
                multi_head_attention.name AS multi_head_attention,
                bert_paper.title AS bert_paper,
                bert.name AS bert_model,
                bidirectional_attention.name AS bidirectional_attention
            """
        elif "RNNs" in user_query and "BERT" in user_query:
            query = """
            MATCH (rnn:Model {name: "RNN"})-[:USED_FOR]->(task:Task {name: "Sequence-to-Sequence Learning"})
            MATCH (transformer:Model {name: "Transformer"})-[:USES]->(attention:Concept {name: "Attention Mechanism"})
            MATCH (bert:Model {name: "BERT"})-[:USES]->(bidirectional_attention:Concept {name: "Bidirectional Attention"})
            MATCH (bidirectional_attention)-[:REFINES]->(attention)
            MATCH (bidirectional_attention)-[:ENABLES]->(bidirectional_pretraining:Concept {name: "Bidirectional Pre-training"})
            MATCH (bidirectional_pretraining)-[:ENABLES]->(nsp_task:Task {name: "Next Sentence Prediction (NSP)"})
            MATCH (bidirectional_pretraining)-[:ENABLES]->(mlm_task:Task {name: "Masked Language Model (MLM)"})
            RETURN 
                rnn.name AS rnn_model,
                transformer.name AS transformer_model,
                bert.name AS bert_model,
                bidirectional_attention.name AS bidirectional_attention_concept,
                attention.name AS refined_concept,
                bidirectional_pretraining.name AS bidirectional_pretraining_concept,
                nsp_task.name AS nsp_task,
                mlm_task.name AS mlm_task
            """
        elif "Transformer architecture" in user_query or "Attention is All You Need" in user_query:
            query = """
            MATCH (a:Author)-[:WROTE]->(p:Paper {title: "Attention is All You Need"})-[:INTRODUCES]->(m:Model {name: "Transformer"})
            RETURN a.name AS author, p.title AS paper, m.name AS model
            """
        elif "Self-Attention" in user_query:
            query = """
            MATCH (p:Paper {title: "Attention is All You Need"})-[:INTRODUCES]->(m:Model {name: "Transformer"})-[:USES]->(sa:Concept {name: "Self-Attention"})
            RETURN p.title AS paper, m.name AS model, sa.name AS mechanism
            """
        elif "Multi-Head Attention" in user_query:
            query = """
            MATCH (p:Paper {title: "Attention is All You Need"})-[:INTRODUCES]->(m:Model {name: "Transformer"})-[:USES]->(mha:Concept {name: "Multi-Head Attention"})
            RETURN p.title AS paper, m.name AS model, mha.name AS mechanism
            """
        elif "Positional Encoding" in user_query:
            query = """
            MATCH (p:Paper {title: "Attention is All You Need"})-[:INTRODUCES]->(m:Model {name: "Transformer"})-[:USES]->(pe:Concept {name: "Positional Encoding"})
            RETURN p.title AS paper, m.name AS model, pe.name AS mechanism
            """
        elif "Attention Mechanism" in user_query:
            query = """
            MATCH (p:Paper {title: "Attention is All You Need"})-[:INTRODUCES]->(m:Model {name: "Transformer"})-[:USES]->(c:Concept {name: "Attention Mechanism"})
            RETURN p.title AS paper, m.name AS model, c.name AS concept
            """
        elif "Decoder" in user_query:
            query = """
            MATCH (p:Paper {title: "Attention is All You Need"})-[:INTRODUCES]->(m:Model {name: "Transformer"})-[:USES]->(c:Concept {name: "Decoder"})
            RETURN p.title AS paper, m.name AS model, c.name AS concept
            """
        elif "Encoder" in user_query:
            query = """
            MATCH (p:Paper {title: "Attention is All You Need"})-[:INTRODUCES]->(m:Model {name: "Transformer"})-[:USES]->(c:Concept {name: "Encoder"})
            RETURN p.title AS paper, m.name AS model, c.name AS concept
            """
        elif "Scaled Dot-Product Attention" in user_query:
            query = """
            MATCH (p:Paper {title: "Attention is All You Need"})-[:INTRODUCES]->(m:Model {name: "Transformer"})-[:USES]->(c:Concept {name: "Scaled Dot-Product Attention"})
            RETURN p.title AS paper, m.name AS model, c.name AS concept
            """
        elif "MoE" in user_query:
            query = """
            MATCH (m:Model {name: "MoE"})-[:USES]->(c:Concept)
            RETURN m.name AS model, COLLECT(c.name) AS concepts
            """
        elif "Deep Att" in user_query:
            query = """
            MATCH (m:Model {name: "Deep Att"})-[:USES]->(c:Concept)
            RETURN m.name AS model, COLLECT(c.name) AS concepts
            """
        elif "ConvS2S" in user_query:
            query = """
            MATCH (m:Model {name: "ConvS2S"})-[:USES]->(c:Concept)
            RETURN m.name AS model, COLLECT(c.name) AS concepts
            """
        elif "GNMT" in user_query:
            query = """
            MATCH (m:Model {name: "GNMT"})-[:USES]->(c:Concept)
            RETURN m.name AS model, COLLECT(c.name) AS concepts
            """
        elif "all models" in user_query:
            query = """
            MATCH (m:Model)-[:USES]->(c:Concept)
            RETURN m.name AS model, COLLECT(c.name) AS concepts
            """
        elif "contributions" in user_query or "key contributions" in user_query:
            query = """
            MATCH (p:Paper {title: "Attention is All You Need"})-[:INTRODUCES]->(m:Model {name: "Transformer"})-[:USES]->(c:Concept)
            RETURN p.title AS paper, m.name AS model, COLLECT(c.name) AS contributions
            """
        elif "limitations of multi-head attention" in user_query:
            query = """
            MATCH (transformer:Model {name: "Transformer"})-[:HAS_LIMITATION]->(limitation:Limitation)-[:ADDRESSED_BY]->(solution:Solution)<-[:ADDRESSES]-(transformer_xl:Model {name: "Transformer-XL"})
            RETURN transformer.name AS model, limitation.name AS limitation, solution.name AS solution, transformer_xl.name AS solution_provider
            """
        # NEW QUERY FOR QUESTION 1: Transformer vs. RNNs + BERT/Transformer-XL refinements
        elif "long-range dependencies" in user_query.lower() or "transformer improvements" in user_query.lower():
            query = """
            MATCH (seq2seq:Paper {title: "Sequence to Sequence Learning with Neural Networks"})-[:DESCRIBES]->(rnn:Model {name: "RNN"})
            MATCH (attention_paper:Paper {title: "Attention is All You Need"})-[:INTRODUCES]->(transformer:Model {name: "Transformer"})-[:USES]->(self_attention:Concept {name: "Self-Attention"})
            RETURN 
                seq2seq.title AS seq2seq_paper,
                rnn.name AS rnn_model,
                attention_paper.title AS transformer_paper,
                transformer.name AS transformer_model,
                self_attention.name AS transformer_mechanism
        """
        else:
            query = """
            MATCH (a:Author)-[:WROTE]->(p:Paper {title: "Attention is All You Need"})
            RETURN p.title AS paper, COLLECT(a.name) AS authors
            """
        
        # Execute the query and return the results
        try:
            result = session.run(query)
            data = result.data()
            print(f"Retrieved data: {data}")
            return data
        except Exception as e:
            print(f"Error querying Neo4j: {e}")
            return []
