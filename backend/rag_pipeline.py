from backend.vector_store import retrieve_top_chunks
from backend.agents import agent1_primary, agent2_validate

# ------------------------------
# Full RAG Pipeline
# ------------------------------
def run_rag_pipeline(question):
    
    # 1️⃣ Retrieve context from FAISS/ChromaDB
    context = retrieve_top_chunks(question)

    if not context or context.strip() == "":
        context = "No relevant text found in uploaded documents."

    # 2️⃣ Agent 1 — Primary reasoning
    agent1_output = agent1_primary(context, question)

    # 3️⃣ Agent 2 — Validate answer
    agent2_output = agent2_validate(agent1_output, question)

    # 4️⃣ Return structured output
    return {
        "context_used": context,
        "agent1_reasoning": agent1_output,
        "final": agent2_output
    }
