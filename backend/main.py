from fastapi import FastAPI, UploadFile
from backend.pdf_processor import save_pdf, extract_pdf_text, chunk_text
from backend.vector_store import add_chunks
from backend.rag_pipeline import run_rag_pipeline
from backend.agents import classification_agent


app = FastAPI()

@app.post("/upload")
async def upload_pdf(file: UploadFile):
    try:
        path = save_pdf(file)
        text = extract_pdf_text(path)

        # 🔥 Debug Extraction
        print("TEXT EXTRACTED (first 300 chars):")
        print(text[:300])

        # Strict GPT classification
        is_medical = classification_agent(text)

        if not is_medical:
            return {"status": "error", "message": "NOT_MEDICAL_PDF"}

        chunks = chunk_text(text if text != "IMAGE_ONLY_PDF" else "")
        add_chunks(chunks)

        return {"status": "success", "chunks_added": len(chunks)}

    except Exception as e:
        return {"status": "error", "message": str(e)}



@app.get("/chat")
async def ask_chat(q: str):
    return run_rag_pipeline(q)
