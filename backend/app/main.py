from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import os

from app.config import settings
from app.routers import auth, documents, chat
from app.models import HealthCheck

# Create FastAPI app
app = FastAPI(
    title="NexusHR AI Backend",
    description="RAG-powered HR Assistant API using FastAPI, LangChain, and ChromaDB",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(chat.router)

# Ensure required directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.CHROMA_PERSIST_DIRECTORY, exist_ok=True)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to NexusHR AI Backend",
        "version": "1.0.0",
        "docs": "/api/docs",
        "status": "running"
    }


@app.get("/api/health", response_model=HealthCheck, tags=["Health"])
async def health_check():
    """
    Health check endpoint
    Returns system status and readiness
    """
    try:
        from app.rag_system import rag_system
        rag_initialized = rag_system.vectorstore is not None
    except:
        rag_initialized = False
    
    return HealthCheck(
        status="healthy",
        version="1.0.0",
        rag_system_initialized=rag_initialized,
        timestamp=datetime.now()
    )


@app.get("/api/info", tags=["Info"])
async def system_info():
    """
    Get system information and configuration
    """
    return {
        "status": "success",
        "system": {
            "name": "NexusHR AI",
            "version": "1.0.0",
            "description": "RAG-powered HR Assistant"
        },
        "models": {
            "embedding": settings.EMBEDDING_MODEL,
            "llm": settings.LLM_MODEL
        },
        "features": {
            "document_upload": True,
            "rag_query": True,
            "intent_classification": True,
            "authentication": True,
            "role_based_access": True
        },
        "endpoints": {
            "docs": "/api/docs",
            "health": "/api/health",
            "auth": "/api/auth",
            "documents": "/api/documents",
            "chat": "/api/chat"
        }
    }


@app.on_event("startup")
async def startup_event():
    """
    Startup event handler
    Initialize RAG system and other components
    """
    print("=" * 60)
    print("🚀 Starting NexusHR AI Backend")
    print("=" * 60)
    print(f"📊 Embedding Model: {settings.EMBEDDING_MODEL}")
    print(f"🤖 LLM Model: {settings.LLM_MODEL}")
    print(f"💾 ChromaDB Directory: {settings.CHROMA_PERSIST_DIRECTORY}")
    print(f"📁 Upload Directory: {settings.UPLOAD_DIR}")
    print(f"🌐 CORS Origins: {settings.origins_list}")
    print("=" * 60)
    
    try:
        from app.rag_system import rag_system
        print("✅ RAG System initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize RAG System: {str(e)}")
    
    print("=" * 60)
    print("🎉 NexusHR AI Backend is ready!")
    print(f"📖 API Documentation: http://{settings.API_HOST}:{settings.API_PORT}/api/docs")
    print("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Shutdown event handler
    Cleanup resources
    """
    print("=" * 60)
    print("👋 Shutting down NexusHR AI Backend")
    print("=" * 60)


# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={
            "status": "error",
            "message": "Endpoint not found",
            "path": str(request.url.path)
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors"""
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error",
            "detail": str(exc) if settings.API_HOST == "0.0.0.0" else "An error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )
