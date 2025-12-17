# NexusHR AI - Project Overview

## 🎯 Project Goal

Build a RAG-powered HR Assistant that helps employees query company policies and HR information using natural language.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                    │
│  - User Authentication UI                                    │
│  - Chat Interface                                            │
│  - Admin Dashboard (Document Upload)                         │
│  - Follow-up Suggestions Display                             │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST API
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Authentication Layer (JWT)                          │  │
│  │  - Login/Logout                                      │  │
│  │  - Role-based Access Control                         │  │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  RAG System (LangChain)                              │  │
│  │  ┌────────────────────────────────────────────────┐ │  │
│  │  │  1. Document Processing                        │ │  │
│  │  │     - PDF Loader (PyPDF)                       │ │  │
│  │  │     - Text Splitter                            │ │  │
│  │  │     - Metadata Extraction                      │ │  │
│  │  └────────────────────────────────────────────────┘ │  │
│  │  ┌────────────────────────────────────────────────┐ │  │
│  │  │  2. Embeddings Generation                      │ │  │
│  │  │     - Model: all-MiniLM-L6-v2                 │ │  │
│  │  │     - Sentence Transformers                    │ │  │
│  │  └────────────────────────────────────────────────┘ │  │
│  │  ┌────────────────────────────────────────────────┐ │  │
│  │  │  3. Vector Storage                             │ │  │
│  │  │     - ChromaDB                                 │ │  │
│  │  │     - Similarity Search                        │ │  │
│  │  └────────────────────────────────────────────────┘ │  │
│  │  ┌────────────────────────────────────────────────┐ │  │
│  │  │  4. Query Processing                           │ │  │
│  │  │     - Intent Classification                    │ │  │
│  │  │     - Context Retrieval                        │ │  │
│  │  │     - Response Generation (Mistral-7B)        │ │  │
│  │  └────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
          ┌──────────────────────────────┐
          │   Hugging Face API           │
          │   - Embeddings Model         │
          │   - LLM (Mistral-7B)        │
          └──────────────────────────────┘
```

## 🔄 User Workflow

### Phase 1: Authentication
1. User opens the application
2. Enters credentials (username/password)
3. System validates and issues JWT token
4. User is redirected to dashboard

### Phase 2: Document Upload (Admin Only)
1. HR Manager logs in
2. Navigates to Admin Dashboard
3. Uploads HR policy PDF (Employee_Handbook.pdf)
4. System processes document:
   - Extracts text from PDF
   - Splits into chunks
   - Generates embeddings
   - Stores in ChromaDB
5. Success confirmation displayed

### Phase 3: Querying
1. Employee asks question: "How many sick leaves for employees?"
2. System classifies intent (Policy Question)
3. RAG Process:
   - Convert question to embedding
   - Search ChromaDB for similar content
   - Retrieve top 3 relevant chunks
   - Send to LLM with context
4. LLM generates answer with citations
5. Display answer + sources + follow-up suggestions

### Phase 4: Follow-up
1. User clicks on suggestion or asks follow-up
2. System maintains conversation context
3. Generates contextual response

## 📦 Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **LangChain**: RAG orchestration
- **ChromaDB**: Vector database
- **Hugging Face**: Pre-trained models
- **PyPDF**: PDF processing
- **JWT**: Authentication

### Models
- **Embeddings**: all-MiniLM-L6-v2 (384 dimensions)
- **LLM**: Mistral-7B-Instruct-v0.2

### Frontend (To be implemented)
- **Next.js**: React framework
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **Axios**: API calls

## 🔐 Security Features

1. **JWT Authentication**: Secure token-based auth
2. **Role-Based Access**:
   - Admin: Full access
   - HR Manager: Upload + Query
   - Employee: Query only
3. **File Validation**: PDF type and size checks
4. **CORS**: Configured for specific origins

## 📊 Key Features Implemented

### ✅ Backend (Current)
- [x] RAG system with LangChain
- [x] ChromaDB integration
- [x] Document upload and processing
- [x] Query endpoint with source citations
- [x] Intent classification
- [x] JWT authentication
- [x] Role-based access control
- [x] Follow-up suggestions
- [x] API documentation (Swagger)

### 🔜 Frontend (Next)
- [ ] Login page
- [ ] Chat interface
- [ ] Admin dashboard
- [ ] Document upload UI
- [ ] Real-time suggestions
- [ ] Chat history

## 🎓 Academic/Interview Value

### What Makes This Project Stand Out:

1. **Complete RAG Implementation**
   - Not just a demo, but production-ready architecture
   - Shows understanding of embeddings, vector stores, and LLMs

2. **Real-World Use Case**
   - Solves actual HR problem
   - Shows business understanding

3. **Security & Authorization**
   - Role-based access
   - JWT implementation
   - Shows enterprise-grade thinking

4. **Scalable Architecture**
   - Modular design
   - Easy to add features
   - Follows best practices

5. **Documentation**
   - API docs
   - Setup guides
   - Testing instructions

## 🚀 Next Steps

### Phase 1: Backend Enhancement (Optional)
- [ ] Add database for user management
- [ ] Implement conversation history storage
- [ ] Add more sophisticated intent classification
- [ ] Implement rate limiting
- [ ] Add logging and monitoring

### Phase 2: Frontend Development
- [ ] Set up Next.js project
- [ ] Create authentication flow
- [ ] Build chat interface
- [ ] Implement admin dashboard
- [ ] Add real-time features

### Phase 3: Deployment
- [ ] Dockerize application
- [ ] Set up CI/CD pipeline
- [ ] Deploy to cloud (AWS/Azure/GCP)
- [ ] Configure domain and SSL

## 📈 Performance Considerations

- **Chunk Size**: 1000 characters (optimal for context)
- **Overlap**: 200 characters (maintains context)
- **Top-K Retrieval**: 3 documents (balance between context and speed)
- **Token Limit**: 512 tokens (LLM generation)

## 🧪 Testing

### API Endpoints Tested:
- ✅ Health check
- ✅ Authentication
- ✅ Document upload
- ✅ Query processing
- ✅ Intent classification
- ✅ Stats retrieval

### Sample Queries:
- "How many sick leaves do employees get?"
- "Can sick leave be encashed?"
- "What are the working hours?"
- "When is salary paid?"

## 📝 Notes for Presentation

### Key Points to Highlight:

1. **RAG Architecture**
   - Explain why RAG over fine-tuning
   - Cost and flexibility benefits

2. **Model Selection**
   - all-MiniLM-L6-v2: Fast, efficient embeddings
   - Mistral-7B: Good balance of quality and speed

3. **Real-World Application**
   - Reduces HR workload
   - 24/7 availability
   - Consistent answers

4. **Extensibility**
   - Easy to add more document types
   - Can extend to other departments
   - Scalable architecture

---

**Project Status**: ✅ Backend Complete | 🔄 Frontend Pending

**Repository**: NexusHR-AI
**Author**: Shiran Thadissanayake
**Date**: December 2025
