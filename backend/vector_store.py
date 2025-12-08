import os
import json
import faiss
import numpy as np
from openai import OpenAI
from backend.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

INDEX_PATH = "backend/db/faiss.index"
CHUNKS_PATH = "backend/db/chunks.json"

EMBED_DIM = 1536  # For OpenAI text-embedding-3-small

# Load or init FAISS
if os.path.exists(INDEX_PATH):
    index = faiss.read_index(INDEX_PATH)
    with open(CHUNKS_PATH, "r") as f:
        chunks = json.load(f)
else:
    index = faiss.IndexFlatL2(EMBED_DIM)
    chunks = []
    os.makedirs("backend/db", exist_ok=True)

# Create OpenAI embeddings
def embed_text(texts):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )
    vectors = [r.embedding for r in response.data]
    return np.array(vectors).astype("float32")


# Add new chunks to FAISS
def add_chunks(new_chunks):
    global index, chunks

    vectors = embed_text(new_chunks)
    index.add(vectors)
    chunks.extend(new_chunks)

    faiss.write_index(index, INDEX_PATH)
    with open(CHUNKS_PATH, "w") as f:
        json.dump(chunks, f)


def retrieve_top_chunks(question, k=5):
    global index, chunks
    if index.ntotal == 0:
        return ""

    q_vec = embed_text([question])
    scores, ids = index.search(q_vec, k)

    return "\n".join([chunks[i] for i in ids[0] if i < len(chunks)])
