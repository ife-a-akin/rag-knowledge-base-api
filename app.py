from rag.pipeline import ask_me
from fastapi import FastAPI, File, UploadFile, Security, status
from fastapi.security.api_key import APIKeyHeader
from fastapi import HTTPException
from pydantic import BaseModel
from rag.embeddings import get_embeddings
from rag.database import create_tables, check_if_exists, insert_document, get_document_by_name
from rag.ingest import extract_text, chunk_text
import faiss
import pickle
import logging, time, os
from rag.vectorstore import get_index_and_chunks

app = FastAPI()

# index = None
# chunks = None
# index_filename = 'data/faiss_index.bin'

logging.basicConfig(level=logging.INFO)

class QueryRequest(BaseModel):
    query: str
    document_name: str
    debug: bool = False 

@app.on_event('startup')
def load_resource():
    create_tables()
    logging.info("Database tables ensured.")

    
   
#send name to db, db returns chunks and index, put those in

@app.post('/query')
def prompt_me(request: QueryRequest):
#send name to db, use name to get chunks and index
    try:
        start = time.time()
        _, index_file, chunks_file = get_document_by_name(request.document_name)
        index = faiss.read_index(index_file)
        logging.info("Loaded FAISS index from file.")

        with open(chunks_file, 'rb') as f:
            chunks = pickle.load(f)
        
        logging.info("Loaded chunks from pickle.")

        result = ask_me(request.query, chunks, index, request.debug)
        duration = time.time() - start
    
        logging.info({
            'query': request.query,
            'response_time': f'{round(duration, 3)}s'  
                      })
        return {'result': result}
    except Exception as e:
        logging.error(f'Error processing query: {str(e)}')
        raise HTTPException(status_code=500, detail=str(e))


API_KEY = 'pass123'
api_key_header = APIKeyHeader(name='THE-API-KEY', auto_error=False)

async def get_api_key(api_key: str = Security(api_key_header)):
    print(f"Received API key: {api_key}")
    if api_key == API_KEY:
        return api_key
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid API key!!!!')


@app.post('/upload')
async def upload_file(file: UploadFile = File(...), api_key: str = Security(get_api_key)):
    folder = '../docs'
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, file.filename)

    if os.path.exists(file_path):
        raise HTTPException(status_code=400, detail="File already exists.")

    #'opens' file as a promise - its not actually opened it yet. buffer is like a file object for interacting with said file
    with open(file_path, 'wb') as buffer:
        content = await file.read()
        buffer.write(content)
        
    _, chunki, index_filename, chunks_filename = get_index_and_chunks(file_path, file.filename)

    result = check_if_exists(file.filename)

    if result:
        logging.info("Document already registered in database.")
    else:
        insert_document(
            document_name=file.filename,
            num_chunks=len(chunki),
            index_file=index_filename,
            chunks_file=chunks_filename
        )
        logging.info("Document metadata inserted into database.")
    return {'file': file.filename}

#upload file, create chunks and embs, store index and pkl with filename

@app.get("/health")
def health():
    return {"status": "ok"}
