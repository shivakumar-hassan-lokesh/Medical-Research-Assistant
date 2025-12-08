import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import os
import json

model = SentenceTransformer("all-MiniLM-L6-v2")

INDEX_PATH = "backend/db/faiss.index"
CHUNKS_PATH = "backend/db/chunks.json"

# Load / init
if os.path.exists(INDEX_PATH):
    index = faiss.read_index(INDEX_PATH)
    with open(CHUNKS_PATH, "r") as f:
        chunks = json.load(f)
else:
    index = faiss.IndexFlatL2(384)
    chunks = []
    os.makedirs("backend/db", exist_ok=True)


# ------------------------------
# Add new chunks from uploaded PDF
# ------------------------------
def add_chunks(new_chunks):
    global index, chunks

    embeddings = model.encode(new_chunks)
    vectors = np.array(embeddings).astype("float32")

    index.add(vectors)
    chunks.extend(new_chunks)

    # Save updated index + chunks
    faiss.write_index(index, INDEX_PATH)
    with open(CHUNKS_PATH, "w") as f:
        json.dump(chunks, f)


# ------------------------------
# Retrieve chunks most relevant to question
# ------------------------------
def retrieve_top_chunks(question, k=5):
    global index, chunks

    if index.ntotal == 0:
        return ""

    q_embed = model.encode([question]).astype("float32")
    scores, ids = index.search(q_embed, k)

    results = [chunks[i] for i in ids[0] if i < len(chunks)]

    return "\n".join(results)
