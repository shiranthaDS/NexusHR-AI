# NexusHR AI Backend

A RAG-powered HR Assistant API built with FastAPI, LangChain, ChromaDB, and Hugging Face models.

## 🚀 Features

- **RAG System**: Retrieval-Augmented Generation for accurate HR policy responses
- **Document Management**: Upload and process HR policy documents (PDFs)
- **Authentication**: JWT-based authentication with role-based access control
- **Intent Classification**: Automatically classifies queries as policy or personal data requests
- **Follow-up Suggestions**: Context-aware question suggestions
- **Vector Storage**: ChromaDB for efficient document retrieval
- **Hugging Face Integration**: Uses all-MiniLM-L6-v2 for embeddings and Mistral-7B for generation

## 🛠️ Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **LangChain**: Framework for building LLM applications
- **ChromaDB**: Vector database for embeddings
- **Hugging Face**: Pre-trained models for embeddings and generation
- **JWT**: Secure authentication
- **Python 3.8+**

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## 🔧 Installation

### 1. Clone the repository

```bash
cd backend
```

### 2. Create and activate virtual environment

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

The `.env` file is already created with your Hugging Face token. You can modify other settings if needed:

```bash
# Check .env file
cat .env
```

Key configuration options:
- `HUGGINGFACE_API_TOKEN`: Your Hugging Face API token
- `EMBEDDING_MODEL`: Model for text embeddings
- `LLM_MODEL`: Large language model for generation
- `SECRET_KEY`: JWT secret key (change in production)
- `API_PORT`: Server port (default: 8000)

## 🚀 Running the Server

### Development mode (with auto-reload):

```bash
python run.py
```

Or using uvicorn directly:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The server will start at: `http://localhost:8000`

### API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## 👤 Default Users

The system comes with three pre-configured users for testing:

| Username | Password | Role | Access Level |
|----------|----------|------|--------------|
| hr_admin | admin123 | admin | Full access (upload, delete, query) |
| hr_manager | manager123 | hr_manager | Upload & query documents |
| employee | employee123 | employee | Query documents only |

## 📡 API Endpoints

### Authentication
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/logout` - Logout

### Document Management
- `POST /api/documents/upload` - Upload a PDF document (Admin/HR Manager)
- `POST /api/documents/upload-multiple` - Upload multiple PDFs (Admin/HR Manager)
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

## 💡 Usage Examples

### 1. Login

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=hr_manager&password=manager123"
```

Response:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### 2. Upload a Document

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

## 🏗️ Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── models.py            # Pydantic models
│   ├── auth.py              # Authentication logic
│   ├── rag_system.py        # RAG implementation
│   └── routers/
│       ├── __init__.py
│       ├── auth.py          # Auth endpoints
│       ├── documents.py     # Document endpoints
│       └── chat.py          # Chat endpoints
├── uploads/                 # Uploaded documents
├── chroma_db/              # ChromaDB storage
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
├── .env.example           # Example environment file
├── .gitignore             # Git ignore rules
├── run.py                 # Server entry point
└── README.md              # This file
```

## 🔒 Security Notes

- The default `SECRET_KEY` in `.env` should be changed in production
- Use HTTPS in production environments
- Store sensitive credentials securely
- Implement rate limiting for production
- Add input validation and sanitization
- Use a real database instead of `fake_users_db` in production

## 🧪 Testing the System

### 1. Start the server
```bash
python run.py
```

### 2. Open API documentation
Visit: http://localhost:8000/api/docs

### 3. Authenticate
- Click on "Authorize" button
- Login with: `hr_manager` / `manager123`

### 4. Upload a document
- Go to `POST /api/documents/upload`
- Upload an HR policy PDF

### 5. Query the system
- Go to `POST /api/chat/query`
- Ask: "How many sick leaves do employees get?"

## 🐛 Troubleshooting

### ImportError: No module named 'app'
```bash
# Make sure you're in the backend directory
cd backend
python run.py
```

### ChromaDB initialization error
```bash
# Remove existing ChromaDB and restart
rm -rf chroma_db/
python run.py
```

### Hugging Face model loading error
```bash
# Check your internet connection and Hugging Face token
# Models are downloaded on first run
```

### Port already in use
```bash
# Change the port in .env file
API_PORT=8001
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangChain Documentation](https://python.langchain.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Hugging Face Documentation](https://huggingface.co/docs)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 License

This project is part of the NexusHR AI system.

## 📧 Support

For issues and questions, please create an issue in the repository.

---

Built with ❤️ for NexusHR AI Project
