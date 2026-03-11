from sentence_transformers import SentenceTransformer
from rag.ingest import extract_text, chunk_text
import numpy as np
import pickle
import os
from rag.models import model

# model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def get_embeddings(pdf_path):
    text = extract_text(pdf_path)
    chunks = []

    # chunk_path = 'data/chunks.pkl'

    # if os.path.exists(chunk_path):
    #     # Load chunks from pickle
    #     with open(chunk_path, 'rb') as f:
    #         chunks = pickle.load(f)
    #     print("Loaded chunks from pickle.")
    # else:
    #     # Chunk the text
    #     chunks = chunk_text(text)
    #     # Save chunks to pickle
    #     os.makedirs(os.path.dirname(chunk_path), exist_ok=True)
    #     with open(chunk_path, 'wb') as f:
    #         pickle.dump(chunks, f)
    #     print("Chunked text and saved chunks to pickle.")

    chunks = chunk_text(text)
    

    embeddings = model.encode(chunks)

    # Converts embeddings to float32 for FAISS
    embedding_matrix = np.array(embeddings).astype('float32') # an array - rows (number of chunks); column (each value that represents the chunk)

    if len(embedding_matrix.shape) == 1:
        embedding_matrix = embedding_matrix.reshape(1, -1)

    dimension = embedding_matrix.shape[1] # dimension of embedding

    return dimension, embedding_matrix, chunks