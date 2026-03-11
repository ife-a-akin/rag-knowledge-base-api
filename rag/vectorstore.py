from rag.embeddings import get_embeddings
import os, pickle, faiss, logging

logging.basicConfig(level=logging.INFO)

def get_index_and_chunks(pdf_path, filename):
    # folder_path = f'data/{filename}'

    # if not os.path.exists(folder_path):
    #     os.makedirs(folder_path)

    index_filename = f'data/{filename}/{filename}_index.bin'
    chunks_filename = f'data/{filename}/{filename}_chunks.pkl'

    dir_name = os.path.dirname(index_filename)
    try:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)
    except OSError as e:
        print(f"Error creating directory {dir_name}: {e}")
        raise

    index_exists = os.path.exists(index_filename)
    chunks_exists = os.path.exists(chunks_filename)

    try:
        if index_exists and chunks_exists:
            # Both files exist
            index = faiss.read_index(index_filename)
            with open(chunks_filename, 'rb') as f:
                chunks = pickle.load(f)
            
            logging.info("Loaded FAISS index from file.")
            logging.info("Loaded chunks from pickle.")

            return index, chunks, index_filename, chunks_filename

        elif not index_exists and not chunks_exists:
            # Generate everything
            dimension, embedding_matrix, chunks = get_embeddings(pdf_path)
            index = faiss.IndexFlatL2(dimension)
            index.add(embedding_matrix)
            # Save index
            faiss.write_index(index, index_filename)
            logging.info("Created and saved new FAISS index.")

            # Save chunks
            with open(chunks_filename, 'wb') as f:
                pickle.dump(chunks, f)

            logging.info("Generated and saved chunks.")
            
            return index, chunks, index_filename, chunks_filename

        elif index_exists and not chunks_exists:
            # Load index, generate chunks
            index = faiss.read_index(index_filename)
            logging.info("Loaded FAISS index from file.")

            _, _, chunks = get_embeddings(pdf_path)
            with open(chunks_filename, 'wb') as f:
                pickle.dump(chunks, f)

            logging.info("Generated and saved chunks.")
            
            return index, chunks, index_filename, chunks_filename

        elif not index_exists and chunks_exists:
            # Generate index, load chunks
            dimension, embedding_matrix, _ = get_embeddings(pdf_path)
            index = faiss.IndexFlatL2(dimension)
            index.add(embedding_matrix)
            # Save index
            faiss.write_index(index, index_filename)
            logging.info("Created and saved new FAISS index.")
            
            # Load chunks
            with open(chunks_filename, 'rb') as f:
                chunks = pickle.load(f)
            
            logging.info("Loaded chunks from pickle.")

            return index, chunks, index_filename, chunks_filename

    except FileNotFoundError as e:
        print(f"File not found: {e}")
        raise
    except OSError as e:
        print(f"OS error: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise



    # if os.path.exists(index_filename):
    #     return faiss.read_index(index_filename)
    # else:
    #     dimension, embedding_matrix, chunks = get_embeddings(pdf_path)
    #     index = faiss.IndexFlatL2(dimension)
    #     index.add(embedding_matrix)
    #     faiss.write_index(index, index_filename)
    #     return index

    
