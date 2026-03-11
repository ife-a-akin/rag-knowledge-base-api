from sentence_transformers import SentenceTransformer
import numpy as np
import requests
# from rag.vectorstore import get_index
from rag.embeddings import get_embeddings
from fastapi import HTTPException
from rag.models import model

# model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def ask_me(input, inp_chunk, inp_index, debug=False):
    # _, _, chunks = get_embeddings()
    
    # index = get_index()

    chunks = inp_chunk
    index = inp_index

    query = input
    query_embeddings = model.encode([query])
    query_embeddings = np.array(query_embeddings).astype('float32')

    k = 3
    distance, indices = index.search(query_embeddings, k)

    print(f'\nVector distances: {distance}') # dimension (1,k)
    print(f'Query: {query}\n')
    # print(indices) # the position of the chunks that are the closest matches to the query

    retrieved_chunks = [chunks[i] for i in indices[0]]

    # concatenates the list elements and adds the string after each element in the list 
    context = '\n----\n'.join(retrieved_chunks)

    if distance[0][0] >= 1.5:
        prompt = 'Return this: The information is not available in the handbook'
    else:
        prompt = f"""
        You are an internal company policy assistant.

        Answer the question using ONLY the information provided in the context below.
        If the answer is not in the context, say:
        "The information is not available in the handbook."

        Context:
        {context}

        Question:
        {query}

        Answer:

        """

    # print(context)

    response = requests.post(
        'http://localhost:11434/api/generate',
        
        json = {
            'model': 'gpt-oss:120b-cloud',
            'prompt': prompt,
            'stream': False,
        }
    )

    if response.status_code == 200:
        result = response.json()
        answer = result['response']
        confidence = round(1 / (1 + float(distance[0][0])), 3)
        if not debug:
            return {
                'answer': answer,
                'confidence': confidence
            }
        else:
            return {
                'answer': answer,
                'confidence': confidence,
                'distance': round(float(distance[0][0]), 3),
                'indices': [int(i) for i in indices[0]] # return full list of indices
            }
    else:
        print(f"Error: {response.status_code} - {response.text}")
        raise HTTPException (
        status_code=response.status_code,
        detail=f"API call failed with status {response.status_code}: {response.text}"
    )

    