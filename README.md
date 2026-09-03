# Medical RAG System

A Retrieval-Augmented Generation (RAG) system for medical documents. Upload PDFs, and ask questions grounded in their content — powered by a FastAPI backend, a FAISS vector store, and a two-agent answer generation + validation pipeline, with a Streamlit frontend.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Running the App](#running-the-app)
- [API Reference](#api-reference)
- [How It Works](#how-it-works)
- [Testing Your Installation](#testing-your-installation)

## Features

- PDF upload and text extraction (PyMuPDF)
- Automatic classification of medical vs. non-medical documents
- Chunking and semantic search via FAISS
- Two-agent pipeline: one agent generates the answer, a second validates and refines it
- Simple Streamlit chat UI

## Architecture

```
PDF Upload → Text Extraction → Medical Doc Classification
    → Chunking → FAISS Vector Store
    → Question → Retrieval → Agent 1 (Generate) → Agent 2 (Validate) → Answer
```

## Requirements

- Python 3.10.x
- macOS / Windows / Linux
- Internet connection
- OpenAI API key

## Installation

### 1. Download the project

Clone the repository or extract the ZIP folder.

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
```

### 2. Create and activate a virtual environment

**macOS / Linux**

```bash
python3.10 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell)**

```powershell
py -3.10 -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

**Option A — Automatic install**

Create a `requirements.txt` file containing:

```
fastapi==0.110.0
uvicorn[standard]==0.29.0
pymupdf==1.23.26
sentence-transformers==2.2.2
faiss-cpu==1.7.4
numpy==1.26.4
openai==1.14.2
streamlit==1.31.0
requests==2.31.0
python-multipart==0.0.6
```

Then run:

```bash
pip install -r requirements.txt
```

**Option B — Manual install**

```bash
pip install fastapi uvicorn
pip install pymupdf
pip install sentence-transformers
pip install faiss-cpu
pip install numpy
pip install openai
pip install streamlit
pip install requests python-multipart
```

## Configuration

Open `backend/config.py` and set your OpenAI API key:

```python
OPENAI_API_KEY = "your_api_key_here"
```

> **Security note:** Avoid committing real API keys to version control. Consider loading the key from an environment variable (e.g. via `python-dotenv`) and adding `config.py` or `.env` to your `.gitignore` instead of hardcoding secrets.

## Project Structure

```
MedRag/
│
├── backend/
│   ├── main.py
│   ├── agents.py
│   ├── rag_pipeline.py
│   ├── pdf_processor.py
│   ├── vector_store.py
│   └── config.py
│
├── frontend/
│   ├── app.py
│   └── style.css
│
├── data/
│   ├── pdfs/
│   └── vector_store/
│
└── requirements.txt
```

## Running the App

### 1. Start the FastAPI backend

```bash
cd backend
uvicorn main:app --reload
```

You should see:

```
Uvicorn running on http://127.0.0.1:8000
```

### 2. Start the Streamlit frontend

In a second terminal:

```bash
cd frontend
streamlit run app.py
```

The UI will be available at [http://localhost:8501](http://localhost:8501).

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/upload` | Upload a PDF document |
| `GET`  | `/chat?q=your_question` | Ask a question against the uploaded documents |

**Example:**

```bash
curl -X POST http://127.0.0.1:8000/upload -F "file=@sample.pdf"
curl "http://127.0.0.1:8000/chat?q=What+is+the+patient's+diagnosis?"
```

## How It Works

1. User uploads a PDF.
2. Backend extracts text using PyMuPDF.
3. GPT classifies whether the document is medical in nature.
4. Text is chunked and stored in a FAISS vector database.
5. User asks a question.
6. The RAG pipeline retrieves the most relevant chunks.
7. **Agent 1** generates a medical answer from the retrieved context.
8. **Agent 2** validates and refines the answer.
9. The final answer is displayed in the UI.

## Testing Your Installation

Run the following to confirm everything is installed correctly:

```bash
python -c "import faiss; print('FAISS OK')"
python -c "from sentence_transformers import SentenceTransformer; print('ST OK')"
python -c "import openai; print('OpenAI OK')"
```

If all three print `OK`, your setup is complete.

## Disclaimer

This project is intended for research and educational purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment.

## License

Add your chosen license here (e.g. MIT, Apache 2.0).
