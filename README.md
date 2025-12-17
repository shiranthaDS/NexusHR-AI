# 🤖 NexusHR AI - Intelligent HR Assistant

A production-ready RAG (Retrieval-Augmented Generation) powered HR Assistant that helps employees query company policies and HR information using natural language.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green)
![LangChain](https://img.shields.io/badge/LangChain-0.1.5-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🌟 Features

- 🔍 **RAG-Powered Responses**: Accurate answers grounded in company documents
- 📄 **Document Management**: Upload and process HR policy PDFs
- 🔐 **Secure Authentication**: JWT-based auth with role-based access control
- 🎯 **Intent Classification**: Automatic classification of queries
- 💡 **Smart Suggestions**: Context-aware follow-up questions
- 📊 **Source Citations**: Every answer includes source references
- 🚀 **Fast & Scalable**: Built with FastAPI and ChromaDB

## 🏗️ Architecture

```
Frontend (Next.js) ←→ Backend (FastAPI) ←→ RAG System (LangChain + ChromaDB) ←→ Hugging Face
```

**Technology Stack:**
- **Backend**: FastAPI, Python 3.8+
- **RAG Framework**: LangChain
- **Vector Store**: ChromaDB
- **Embeddings**: all-MiniLM-L6-v2 (Hugging Face)
- **LLM**: Mistral-7B-Instruct-v0.2 (Hugging Face)
- **Auth**: JWT with role-based access
- **Document Processing**: PyPDF, RecursiveCharacterTextSplitter

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Hugging Face API token (provided in .env)

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd NexusHR-AI
```

2. **Navigate to backend**
```bash
cd backend
```

3. **Run setup script**
```bash
./setup.sh
```

Or manually:
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p uploads chroma_db
```

4. **Start the server**
```bash
python run.py
```

The server will start at: `http://localhost:8000`

### 🧪 Test the Installation

```bash
python test_setup.py
```

## 📚 API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## 👤 Default Users

| Username | Password | Role | Permissions |
|----------|----------|------|-------------|
| hr_admin | admin123 | Admin | Full access (all operations) |
| hr_manager | manager123 | HR Manager | Upload documents, query system |
| employee | employee123 | Employee | Query system only |

## 🎯 Usage Example

### 1. Login

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=hr_manager&password=manager123"
```

### 2. Upload HR Policy Document

```bash
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@Employee_Handbook.pdf"
```

### 3. Query the System

```bash
curl -X POST "http://localhost:8000/api/chat/query" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How many sick leaves do employees get?",
    "include_sources": true
  }'
```

**Response:**
```json
{
  "status": "success",
  "answer": "According to the 2025 Leave Policy (Section 4.2), each employee is entitled to 12 days of sick leave per year. Sick leave cannot be encashed and will lapse on December 31st.",
  "sources": [
    {
      "content": "LEAVE POLICY - SECTION 4.2...",
      "metadata": {"filename": "Employee_Handbook.pdf", "page": 5}
    }
  ],
  "intent": "policy",
  "suggestions": [
    "Can sick leave be encashed?",
    "How do I apply for leave?",
    "What is the privilege leave policy?"
  ]
}
```

## 📖 API Endpoints

### Authentication
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/logout` - Logout

### Document Management
- `POST /api/documents/upload` - Upload PDF document (Admin/HR Manager)
- `POST /api/documents/upload-multiple` - Upload multiple PDFs
- `GET /api/documents/stats` - Get collection statistics
- `GET /api/documents/list` - List uploaded documents
- `DELETE /api/documents/all` - Delete all documents (Admin only)

### Chat & Query
- `POST /api/chat/query` - Query the HR system
- `POST /api/chat/classify-intent` - Classify question intent
- `POST /api/chat/suggest` - Get follow-up suggestions
- `GET /api/chat/health` - Chat system health check

### System
- `GET /` - Root endpoint
- `GET /api/health` - Health check
- `GET /api/info` - System information

## 🔐 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access Control (RBAC)**: Three user roles with different permissions
- **File Validation**: Type and size validation for uploads
- **CORS Configuration**: Controlled cross-origin access
- **Password Hashing**: Bcrypt for secure password storage

## 📂 Project Structure

```
NexusHR-AI/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration management
│   │   ├── models.py            # Pydantic models
│   │   ├── auth.py              # Authentication logic
│   │   ├── rag_system.py        # RAG implementation
│   │   └── routers/
│   │       ├── auth.py          # Auth endpoints
│   │       ├── documents.py     # Document endpoints
│   │       └── chat.py          # Chat endpoints
│   ├── uploads/                 # Uploaded documents
│   ├── chroma_db/              # Vector store
│   ├── requirements.txt        # Python dependencies
│   ├── .env                    # Environment variables
│   ├── run.py                  # Server entry point
│   ├── setup.sh               # Setup script
│   ├── test_setup.py          # Setup verification
│   ├── README.md              # Backend documentation
│   └── API_TESTING.md         # API testing guide
├── frontend/                   # (To be implemented)
├── PROJECT_OVERVIEW.md        # Project architecture
└── README.md                  # This file
```

## 🧠 How It Works

### RAG Pipeline

1. **Document Ingestion**
   - HR Manager uploads PDF document
   - System extracts text using PyPDF
   - Text is split into chunks (1000 chars, 200 overlap)
   - Each chunk is converted to embeddings
   - Embeddings stored in ChromaDB

2. **Query Processing**
   - User asks question
   - Question converted to embedding
   - ChromaDB finds top 3 similar chunks
   - Chunks sent to LLM as context
   - LLM generates answer with citations

3. **Intent Classification**
   - System classifies query type (policy vs personal data)
   - Routes to appropriate handler
   - Generates contextual follow-up suggestions

## 🎓 For Academic/Interview Presentations

### Key Highlights:

✅ **Production-Ready Architecture**: Not a toy project, built with best practices  
✅ **Complete RAG Implementation**: From PDF upload to contextual responses  
✅ **Enterprise Security**: Authentication, authorization, role-based access  
✅ **Scalable Design**: Modular, extensible, follows SOLID principles  
✅ **Real-World Use Case**: Solves actual HR department challenges  
✅ **Comprehensive Documentation**: API docs, setup guides, testing instructions  

### Technologies Demonstrated:

- Natural Language Processing (NLP)
- Vector Databases & Similarity Search
- Large Language Models (LLMs)
- RESTful API Design
- Authentication & Authorization
- Document Processing & Chunking
- Embeddings & Retrieval-Augmented Generation

## 🐛 Troubleshooting

### Server won't start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Or change port in .env file
API_PORT=8001
```

### ChromaDB errors
```bash
# Clear ChromaDB and restart
rm -rf chroma_db/
python run.py
```

### Model loading issues
```bash
# Check internet connection
# Models are downloaded on first run (may take time)
# Verify Hugging Face token in .env
```

## 🔄 Roadmap

### Phase 1: Backend ✅ (Complete)
- [x] RAG system implementation
- [x] Document upload & processing
- [x] Query endpoints
- [x] Authentication & authorization
- [x] API documentation

### Phase 2: Frontend (Upcoming)
- [ ] Next.js setup
- [ ] Login page
- [ ] Chat interface
- [ ] Admin dashboard
- [ ] Real-time suggestions
- [ ] Chat history

### Phase 3: Enhancements
- [ ] Conversation history in database
- [ ] Advanced intent classification
- [ ] Multi-language support
- [ ] Analytics dashboard
- [ ] Email notifications

### Phase 4: Deployment
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] Cloud deployment
- [ ] Production monitoring

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Hugging Face**: For providing amazing pre-trained models
- **LangChain**: For the excellent RAG framework
- **ChromaDB**: For the efficient vector database
- **FastAPI**: For the modern Python web framework

## 📧 Contact

**Project Maintainer**: Shiran Thadissanayake  
**Project Link**: [GitHub Repository](https://github.com/yourusername/NexusHR-AI)

---

## 📊 System Requirements

- **Python**: 3.8 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: 2GB free space (for models and documents)
- **Internet**: Required for initial model download

---

## 🎉 Get Started Now!

```bash
cd backend
./setup.sh
python run.py
```

Then visit: http://localhost:8000/api/docs

---

**Built with ❤️ for the NexusHR AI Project**

*Empowering HR teams with AI-powered assistance*
