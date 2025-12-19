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
- ✅ Authentication Flow
- ✅ Source Display
- ✅ One-click Suggestions

## 🚀 Quick Start

### Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your Hugging Face token
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup
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
Made with ❤️ for NexusHR
