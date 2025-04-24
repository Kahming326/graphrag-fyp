import os
import pandas as pd
import time
import json
from trulens.core import TruSession, Feedback
from trulens.feedback import GroundTruthAgreement
import ollama
from trulens.dashboard import run_dashboard
from trulens.apps.basic import TruBasicApp
from query_neo4j import query_graph
from eval_llama import get_llama_response, construct_query_for_question, get_rich_graph_data

def ollama_evaluate(prompt):
    """
    Use mistral:7b to evaluate responses instead of OpenAI.
    """
    response = ollama.chat(model="mistral:7b", messages=[{"role": "user", "content": prompt}])
    return response['message']['content']

# Initialize TruSession
session = TruSession()

# Define your GraphRAG pipeline
def graphrag_pipeline(user_query, verbose=False):
    """
    Process a user query through the GraphRAG pipeline:
    1. Query Neo4j for relevant data
    2. Construct a prompt with context
    3. Get response from LLM
    """
    try:
        # Step 1: Query Neo4j
        retrieved_data = query_graph(user_query)
        if verbose:
            print(f"Retrieved Data: {retrieved_data}")
        
        if not retrieved_data:
            # Fallback to get general data about the paper if specific query returned no results
            if verbose:
                print("No specific data found, getting general paper information...")
            query_type = "general"
            if "Transformer architecture" in user_query:
                query_type = "transformer_architecture"
            elif "Self-Attention" in user_query:
                query_type = "self_attention"
            elif "Multi-Head Attention" in user_query:
                query_type = "multi_head_attention"
                
            retrieved_data = get_rich_graph_data(query_type)
        
        # Step 2: Construct the query for the LLM
        query_string = construct_query_for_question(user_query, retrieved_data)
        if verbose:
            print(f"Query String for LLM: {query_string}")
        
        # Step 3: Send the query to the LLM and get response
        response = get_llama_response(query_string)
        if verbose:
            print(f"LLM Response: {response}")
        
        # Return the response
        return response
    except Exception as e:
        print(f"Error in GraphRAG pipeline: {e}")
        return f"An error occurred: {str(e)}"

# Load ground truth data from a JSON file
def load_ground_truth(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        ground_truth_data = json.load(file)
    return ground_truth_data

# Replace the hardcoded ground_truth_data with data from the file
ground_truth_data = load_ground_truth('ground_truth.json')

# Initialize the feedback function
ground_truth_collection = Feedback(
    lambda user_input, model_output: ollama_evaluate(
        f"Evaluate the accuracy of this response based on the given question.\n\n"
        f"Question: {user_input}\n"
        f"Response: {model_output}\n"
        f"Score from 0 (completely incorrect) to 1 (perfectly correct):"
    ),
    name="Ground Truth Evaluation"
).on_input_output()


# Wrap your pipeline with TruLens
tru_recorder = TruBasicApp(
    graphrag_pipeline,
    app_id="GraphRAG System",
    feedbacks=[ground_truth_collection]
)

# List of evaluation questions
eval_questions = [
    "What is the Transformer architecture introduced in the 'Attention is All You Need' paper?"
]


# Main evaluation function
def run_evaluation():
    results = []
    
    try:
        with tru_recorder as recording:
            for question in eval_questions:
                print(f"\nEvaluating Question: {question}")
                
                try:
                    # Step 1: Get the system's response
                    response = graphrag_pipeline(question, verbose=False)  # Set verbose=False here
                    print(f"Question: {question}")
                    print(f"Response: {response}")
                    
                    # Step 2: Find the expected response from ground truth data
                    expected_response = None
                    for item in ground_truth_data:
                        if item["query"] == question:
                            expected_response = item["expected_response"]
                            break
                    
                    if expected_response is None:
                        print(f"No ground truth found for question: {question}")
                        metric = 0.0  # No ground truth, assume worst case
                    else:
                        # Step 3: Use Trulens' GroundTruthAgreement to evaluate the response
                        metric = ground_truth_collection(response, expected_response)
                        print(f"Trulens Evaluation Score: {metric}")
                    
                    # Step 4: Store the results
                    results.append({
                        "question": question,
                        "response": response,
                        "metric": metric
                    })
                    
                    # Add a small delay between questions to avoid overwhelming the LLM service
                    time.sleep(2)
                except Exception as e:
                    print(f"Error processing question: {e}")
                    results.append({
                        "question": question,
                        "response": f"Error: {str(e)}",
                        "metric": 0.0  # Error case, assume worst case
                    })
        
        # Convert results to a DataFrame
        results_df = pd.DataFrame(results)

        # Add 'app_name' column
        results_df['app_name'] = 'GraphRAG System'  # Replace with your app name

        # Print the DataFrame for debugging
        print("Results DataFrame:")
        print(results_df)

        # Save results to a file
        with open('evaluation_results.txt', 'w', encoding='utf-8') as f:
            for _, row in results_df.iterrows():
                f.write(f"Question: {row['question']}\n")
                f.write(f"Response: {row['response']}\n")
                f.write(f"Trulens Evaluation Score: {row['metric']}\n")
                f.write("-" * 50 + "\n")
        
        print("\nEvaluation complete. Results saved to evaluation_results.txt")
        
        # Launch the TruLens dashboard (if available)
        if hasattr(tru_recorder, 'launch_dashboard'):
            tru_recorder.launch_dashboard()
        else:
            print("Dashboard functionality not available in this version of trulens.")
        
    except Exception as e:
        print(f"Error in evaluation: {e}")

# Run the evaluation if this script is executed directly
if __name__ == "__main__":
    print("Starting GraphRAG evaluation...")
    run_evaluation()