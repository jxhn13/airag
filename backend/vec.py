import os
import cohere
import numpy as np
import uuid
import random
import streamlit as st
from qdrant_client import QdrantClient, models



os.environ["COHERE_API_KEY"] = " "
api_key = os.getenv("COHERE_API_KEY")
if not api_key:
    st.error("COHERE_API_KEY is not set in the environment variables.")
    st.stop()

co = cohere.Client(api_key)



client = QdrantClient(path=":memory:")  # Saves the collection on disk

collection_name = "text_embeddings"
dimension = 1024
if collection_name not in [col.name for col in client.get_collections().collections]:
    print(f"Creating collection '{collection_name}'...")
    client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(size=dimension, distance=models.Distance.COSINE),
    )
else:
    print(f"Collection '{collection_name}' already exists.")
def generate_embeddings(text, input_type="search_query"):
    """Generates embeddings using Cohere's API."""
    try:
        response = co.embed(texts=[text], model="embed-english-v3.0", input_type=input_type)
        return np.array(response.embeddings[0], dtype=np.float32)
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return None


def store_embeddings(text):
    """Generates and stores text embeddings in Qdrant."""
    embeddings = generate_embeddings(text, input_type="search_document")
    if embeddings is None:
        return None

    point_id = uuid.uuid4().hex  
    client.upsert(
        collection_name=collection_name,
        points=[
            models.PointStruct(
                id=point_id,
                vector=embeddings.tolist(),
                payload={"text": text}  
            )
        ],
    )
    return point_id

def search_similar_text(query_text, limit=3):
    """Search for similar text in Qdrant using Cohere embeddings."""
    query_embedding = generate_embeddings(query_text, input_type="search_query")
    if query_embedding is None:
        return []

    search_results = client.search(
        collection_name=collection_name,
        query_vector=query_embedding.tolist(), 
        limit=limit,
    )

    return [(result.payload.get("text"), result.score) for result in search_results]

def generate_answer(query):
    """Generates an AI-powered answer using Cohere based on retrieved text chunks."""
    relevant_chunks = search_similar_text(query)
    
    if not relevant_chunks:
        context = "No relevant context found."
    else:
        context = " ".join([chunk[0] for chunk in relevant_chunks])[:2000]  


    prompt = f"Context: {context}\n\nQuestion: {query}\nAnswer:"
    
    try:
        response = co.generate(
            model="command",
            prompt=prompt,
            max_tokens=150,
            temperature=0.5
        )
        return response.generations[0].text.strip()
    
    except Exception as e:
        return f"Error generating answer: {str(e)}"

def generate_question():
    """Generates a follow-up question based on the document content."""
    question_prompts = [
        "What is the main idea of this document?",
        "Can you summarize this document in a few sentences?",
        "What are the key points mentioned in this document?",
        "Does this document discuss any important events?",
        "What are the conclusions drawn in this document?"
    ]
    return random.choice(question_prompts)

