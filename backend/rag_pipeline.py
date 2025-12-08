from backend.vector_store import retrieve_top_chunks
from backend.agents import agent1_primary, agent2_validate

def run_rag_pipeline(question):
    context = retrieve_top_chunks(question)
    if not context:
        context = "No relevant context found in uploaded documents."

    # Agent 1
    initial = agent1_primary(context, question)

    # Agent 2
    final = agent2_validate(initial, question)

    return {
        "context_used": context,
        "agent1_reasoning": initial,
        "final": final
    }
