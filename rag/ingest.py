import pymupdf
import re


def extract_text(pdf_path):
    doc = pymupdf.open(pdf_path)
    full_text = ''

    for i, page in enumerate(doc):
        if i in [0, 1, 2]:
            continue
        raw_text = page.get_text()
        clean_text = re.sub(r'\n+', '\n', raw_text)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        full_text += clean_text + ' '

    return full_text

def chunk_text(textin, chunk_size=500, overlap=100):
    start = 0
    chunks = []
    # breaks the text into chunks of 300 characters each
    while start < len(textin):
        end = start + chunk_size
        chunks.append(textin[start:end])
        start += chunk_size - overlap
    
    return chunks