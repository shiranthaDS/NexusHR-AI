from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from typing import List
import os
import shutil
from datetime import datetime
from app.models import (
    DocumentIngestionResponse,
    DocumentMetadata,
    CollectionStats,
    User
)
from app.auth import get_admin_user, get_current_active_user
from app.rag_system import rag_system
from app.config import settings

router = APIRouter(prefix="/api/documents", tags=["Document Management"])

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=DocumentIngestionResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_admin_user)
):
    """
    Upload and ingest a PDF document into the RAG system
    
    Requires: Admin or HR Manager role
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported"
        )
    
    # Check file size
    contents = await file.read()
    if len(contents) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE} bytes"
        )
    
    try:
        # Save file temporarily
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(settings.UPLOAD_DIR, filename)
        
        with open(file_path, "wb") as buffer:
            buffer.write(contents)
        
        # Prepare metadata
        metadata = {
            "filename": file.filename,
            "uploaded_by": current_user.username,
            "upload_date": datetime.now().isoformat(),
            "document_id": filename,
            "document_type": "policy"
        }
        
        # Ingest document
        result = await rag_system.ingest_document(file_path, metadata)
        
        if result["status"] == "success":
            result["document_id"] = filename
            return DocumentIngestionResponse(**result)
        else:
            # Clean up file if ingestion failed
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["message"]
            )
    
    except Exception as e:
        # Clean up on error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process document: {str(e)}"
        )


@router.post("/upload-multiple")
async def upload_multiple_documents(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_admin_user)
):
    """
    Upload and ingest multiple PDF documents
    
    Requires: Admin or HR Manager role
    """
    results = []
    
    for file in files:
        try:
            # Validate file type
            if not file.filename.endswith('.pdf'):
                results.append({
                    "filename": file.filename,
                    "status": "error",
                    "message": "Only PDF files are supported"
                })
                continue
            
            # Read file
            contents = await file.read()
            
            # Check file size
            if len(contents) > settings.MAX_FILE_SIZE:
                results.append({
                    "filename": file.filename,
                    "status": "error",
                    "message": f"File size exceeds maximum allowed size"
                })
                continue
            
            # Save file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{file.filename}"
            file_path = os.path.join(settings.UPLOAD_DIR, filename)
            
            with open(file_path, "wb") as buffer:
                buffer.write(contents)
            
            # Prepare metadata
            metadata = {
                "filename": file.filename,
                "uploaded_by": current_user.username,
                "upload_date": datetime.now().isoformat(),
                "document_id": filename,
                "document_type": "policy"
            }
            
            # Ingest document
            result = await rag_system.ingest_document(file_path, metadata)
            result["filename"] = file.filename
            results.append(result)
            
        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "error",
                "message": str(e)
            })
    
    return {"results": results}


@router.get("/stats", response_model=CollectionStats)
async def get_collection_stats(current_user: User = Depends(get_current_active_user)):
    """
    Get statistics about the document collection
    
    Requires: Authentication
    """
    stats = rag_system.get_collection_stats()
    if stats["status"] == "error":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=stats["message"]
        )
    return CollectionStats(**stats)


@router.delete("/all")
async def delete_all_documents(current_user: User = Depends(get_admin_user)):
    """
    Delete all documents from the vector store
    
    Requires: Admin role only
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete all documents"
        )
    
    result = await rag_system.delete_all_documents()
    
    if result["status"] == "error":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["message"]
        )
    
    # Also delete uploaded files
    try:
        for filename in os.listdir(settings.UPLOAD_DIR):
            file_path = os.path.join(settings.UPLOAD_DIR, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
    except Exception as e:
        print(f"Error cleaning up upload directory: {str(e)}")
    
    return result


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a single uploaded document (file + vectors)

    Requires: Admin or the user who uploaded the document
    """
    # Permission: allow admin or uploader (best-effort via metadata).
    # We attempt to determine uploader from stored metadatas; if not found, admins may proceed.
    try:
        uploader = None
        original_name = None
        if "_" in document_id:
            parts = document_id.split("_")
            original_name = "_".join(parts[1:])

        try:
            collection = rag_system.vectorstore._collection
            docs = collection.get(include=["metadatas"]) or {}
            metas = docs.get("metadatas", [])
            for meta in metas:
                if not meta or not isinstance(meta, dict):
                    continue
                if meta.get("document_id") == document_id or meta.get("filename") == document_id or (original_name and meta.get("filename") == original_name):
                    uploader = meta.get("uploaded_by") or uploader
                    break
                src = meta.get("source")
                if src and src.endswith(document_id):
                    uploader = meta.get("uploaded_by") or uploader
                    break
        except Exception:
            # best-effort, continue
            uploader = None

        # Enforce permissions: admin or uploader
        if current_user.role != "admin" and uploader and uploader != current_user.username:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin or uploader can delete this document")

        # Attempt to delete vectors/meta via rag_system
        result = await rag_system.delete_document(document_id)
        if result.get("status") == "error":
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=result.get("message"))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to remove document from vector store: {str(e)}")

    # Remove file from uploads directory if present
    try:
        file_path = os.path.join(settings.UPLOAD_DIR, document_id)
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Failed to remove file {file_path}: {str(e)}")

    # Return success and include deleted_count if available
    response = {"status": "success", "message": f"Document {document_id} deleted"}
    if isinstance(result, dict) and "deleted_count" in result:
        response["deleted_count"] = result["deleted_count"]

    return response


@router.get("/list")
async def list_uploaded_documents(current_user: User = Depends(get_current_active_user)):
    """
    List all uploaded documents
    
    Requires: Authentication
    """
    try:
        files = []
        if os.path.exists(settings.UPLOAD_DIR):
            for filename in os.listdir(settings.UPLOAD_DIR):
                file_path = os.path.join(settings.UPLOAD_DIR, filename)
                if os.path.isfile(file_path):
                    stat = os.stat(file_path)
                    files.append({
                        "filename": filename,
                        "size": stat.st_size,
                        "uploaded_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
        
        return {
            "status": "success",
            "documents": files,
            "total": len(files)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list documents: {str(e)}"
        )
