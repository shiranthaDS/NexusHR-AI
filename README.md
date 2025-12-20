
# NexusHR-AI

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-✓-009688) ![Next.js](https://img.shields.io/badge/Next.js-13-000000?logo=next.js&logoColor=white) ![LangChain](https://img.shields.io/badge/LangChain-0.1-4B5563?logo=langchain&logoColor=white) ![ChromaDB](https://img.shields.io/badge/ChromaDB-persist-4C1) ![HuggingFace](https://img.shields.io/badge/HuggingFace-Models-FF6A00?logo=huggingface&logoColor=white)

Modern, production-oriented HR assistant that uses Retrieval-Augmented Generation (RAG) to answer policy questions from uploaded documents (PDFs).

Why this is recruiter-friendly

- Role: Full-stack product combining backend, frontend, and ML infra
- Impact: faster employee support, searchable policy knowledgebase, secure access controls
- Key skills demonstrated: Python, FastAPI, LangChain, vector search (Chroma), transformer-based embeddings, Next.js, TypeScript

Core features

- Secure authentication & role-based access (admin, hr_manager, employee)
- Document ingestion & intelligent chunking (PDF -> metadata + vectors)
- Vector search with ChromaDB + embeddings
- RAG-powered Q&A with intent classification and reranking
- Web UI: chat interface + document manager (upload / delete)

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

API docs

- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

High-level repo layout

- `backend/` — FastAPI app, RAG system, document ingestion scripts
- `frontend/` — Next.js app, chat UI, document manager
- `chroma_db/` — persisted Chroma DB
- `uploads/` — uploaded PDF files

For recruiters / hiring managers

- Suggested interview topics: architecture of a RAG system, vector DB tradeoffs, chunking strategies, evaluation of retrieved context, LLM prompt design, access control and secure file handling
- Time-to-demo: ~10 minutes (start backend + frontend and upload a sample PDF)

Assets

- Add `docs/screenshot.png` to show the chat UI (placeholder used above).

Next steps I can do for you

- Add CI badges and a GitHub Actions workflow
- Add `LICENSE` (MIT/Apache) and `CONTRIBUTING.md`
- Create a short one-page demo script for interviews

---

