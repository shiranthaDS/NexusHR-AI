# NexusHR AI - Intelligent HR Assistant

A full-stack RAG (Retrieval-Augmented Generation) powered HR assistant built with FastAPI, Next.js, LangChain, ChromaDB, and Hugging Face models.

## 🎯 Features

### Backend (FastAPI + RAG)
- ✅ JWT Authentication with role-based access control
- ✅ RAG System with ChromaDB vector store
- ✅ Document Processing (PDF upload and parsing)
- ✅ Hugging Face Integration (embeddings + LLM)
- ✅ Intent Classification
- ✅ Source Citations
- ✅ Follow-up Suggestions

### Frontend (Next.js 16)
- ✅ Modern UI with Tailwind CSS
- ✅ Real-time Chat Interface
- ✅ Document Management
# NexusHR-AI

Modern, full-stack HR assistant using retrieval-augmented generation (RAG).

Key technologies: FastAPI (backend), Next.js (frontend), LangChain + ChromaDB (vector store), Hugging Face models.


Why this project
- Provide employees and HR teams with an intelligent assistant that answers policy questions using company documents (PDFs), and supports secure role-based access.

Features
- Secure authentication and role-based access (admin, hr_manager, employee)
- Document ingestion (PDF) with intelligent chunking and metadata
- Vector search with ChromaDB + sentence-transformers embeddings
- RAG-powered Q&A with context-aware retrieval and intent classification
- Web UI for chat and document management (Next.js + TypeScript)

Quick start (local)

Prerequisites
- Python 3.9+ (backend)
- Node.js 18+ / npm (frontend)
- Git

Backend
1. Open a terminal and enter the backend folder:

```bash
cd backend
```

2. Create and activate a Python virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install Python dependencies and configure environment:

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env to add HUGGINGFACE_API_TOKEN and SECRET_KEY
```

4. Run the backend server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend
1. Open a new terminal and enter the frontend folder:

```bash
cd frontend
```

2. Install and run:

```bash
npm install
npm run dev
```

API docs
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

Folder layout (high level)
- backend/: FastAPI app, RAG system, document ingestion scripts
- frontend/: Next.js app, chat UI, document manager
- chroma_db/: persisted Chroma DB
- uploads/: uploaded PDF files

