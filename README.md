
# NexusHR-AI

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-✓-009688) ![Next.js](https://img.shields.io/badge/Next.js-13-000000?logo=next.js&logoColor=white) ![LangChain](https://img.shields.io/badge/LangChain-0.1-4B5563?logo=langchain&logoColor=white) ![ChromaDB](https://img.shields.io/badge/ChromaDB-persist-4C1) ![HuggingFace](https://img.shields.io/badge/HuggingFace-Models-FF6A00?logo=huggingface&logoColor=white)


production-oriented HR assistant that uses Retrieval-Augmented Generation (RAG) to answer policy questions from uploaded documents (PDFs).

### Backend (FastAPI + RAG)
- ✅ JWT Authentication with role-based access control
- ✅ RAG System with ChromaDB vector store
- ✅ Document Processing (PDF upload and parsing)
- ✅ Hugging Face Integration (embeddings + LLM)
- ✅ LangChain – RAG orchestration and retrieval pipeline

### Frontend (Next.js 16)
- ✅ Modern UI with Tailwind CSS
- ✅ Real-time Chat Interface
- ✅ Document Management


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

- Python 3.9+
- Node.js 18+ and npm
- Git

Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env to add HUGGINGFACE_API_TOKEN and SECRET_KEY
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend

```bash
cd frontend
npm install
npm run dev
```

## 🔐 Demo Accounts
- Admin: `hr_admin` / `admin123`
- Manager: `hr_manager` / `manager123`
- Employee: `employee` / `employee123`

## 📚 API Documentation
- Swagger: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## 🛠️ Tech Stack
- **Backend**: FastAPI, LangChain, ChromaDB, Hugging Face
- **Frontend**: Next.js 16, TypeScript, Tailwind CSS
- **ML**: sentence-transformers, google/flan-t5-large

---
