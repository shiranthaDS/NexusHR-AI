#!/usr/bin/env python3
"""
Quick test script to verify the backend setup
"""

import sys
import os

def check_imports():
    """Check if all required packages are installed"""
    print("🔍 Checking required packages...\n")
    
    required_packages = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("langchain", "LangChain"),
        ("chromadb", "ChromaDB"),
        ("transformers", "Transformers"),
        ("sentence_transformers", "Sentence Transformers"),
        ("pypdf", "PyPDF"),
        ("jose", "Python-JOSE"),
        ("passlib", "Passlib"),
    ]
    
    all_ok = True
    for module, name in required_packages:
        try:
            __import__(module)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} - Not installed")
            all_ok = False
    
    return all_ok

def check_env_file():
    """Check if .env file exists and has required variables"""
    print("\n🔍 Checking environment configuration...\n")
    
    if not os.path.exists(".env"):
        print("❌ .env file not found")
        return False
    
    print("✅ .env file exists")
    
    required_vars = [
        "HUGGINGFACE_API_TOKEN",
        "SECRET_KEY",
        "EMBEDDING_MODEL",
        "LLM_MODEL"
    ]
    
    with open(".env", "r") as f:
        content = f.read()
    
    all_vars_present = True
    for var in required_vars:
        if var in content:
            print(f"✅ {var} configured")
        else:
            print(f"❌ {var} missing")
            all_vars_present = False
    
    return all_vars_present

def check_directories():
    """Check if required directories exist"""
    print("\n🔍 Checking directories...\n")
    
    directories = ["uploads", "chroma_db"]
    all_ok = True
    
    for directory in directories:
        if os.path.exists(directory):
            print(f"✅ {directory}/ exists")
        else:
            print(f"⚠️  {directory}/ doesn't exist (will be created on startup)")
    
    return all_ok

def test_rag_system():
    """Test if RAG system can be initialized"""
    print("\n🔍 Testing RAG system initialization...\n")
    
    try:
        from app.rag_system import rag_system
        print("✅ RAG system initialized successfully")
        
        # Get stats
        stats = rag_system.get_collection_stats()
        print(f"✅ Vector store ready (documents: {stats.get('document_count', 0)})")
        return True
    except Exception as e:
        print(f"❌ RAG system initialization failed: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("  NexusHR AI Backend - Setup Verification")
    print("=" * 60)
    print()
    
    results = []
    
    # Check imports
    results.append(("Package Installation", check_imports()))
    
    # Check environment
    results.append(("Environment Configuration", check_env_file()))
    
    # Check directories
    results.append(("Directory Structure", check_directories()))
    
    # Test RAG system
    results.append(("RAG System", test_rag_system()))
    
    # Summary
    print("\n" + "=" * 60)
    print("  Summary")
    print("=" * 60)
    print()
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("✅ All checks passed! You're ready to start the server.")
        print("\n🚀 Run: python run.py")
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("\n💡 Tip: Run ./setup.sh to auto-configure the environment")
        return 1

if __name__ == "__main__":
    sys.exit(main())
