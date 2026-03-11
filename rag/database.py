import psycopg2
import os

DB_HOST = "localhost"
DB_NAME = "ragdb"
DB_USER = "raguser"
DB_PASS = "ragpass"
DB_PORT = "5432"

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS documents (
            id SERIAL PRIMARY KEY,
            document_name TEXT NOT NULL,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            num_chunks INTEGER,
            index_file TEXT,
            chunks_file TEXT
        );
    """
    )

    conn.commit()
    cursor.close()
    conn.close()


def check_if_exists(document_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id FROM documents WHERE document_name = %s
    """, (document_name,))

    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row:
        return True
    else:
        return False
    
def insert_document(document_name, num_chunks, index_file, chunks_file):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO documents (document_name, num_chunks, index_file, chunks_file)
        VALUES (%s, %s, %s, %s)
    """, (document_name, num_chunks, index_file, chunks_file))

    conn.commit()
    cur.close()
    conn.close()

def get_document_by_name(document_name):
    conn = get_connection()
    cursor  = conn.cursor()

    cursor.execute("""
        SELECT document_name, index_file, chunks_file FROM documents WHERE document_name = %s
    """, (document_name,))

    row = cursor.fetchone()

    if row:
        name, index, chunks = row
        cursor.close()
        conn.close()
        return name, index, chunks
    else:
        cursor.close()
        conn.close()
        return None

    cursor.close()
    conn.close()

    return row