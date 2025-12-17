from fastapi import APIRouter, Depends, HTTPException, status
from app.models import QueryRequest, QueryResponse, IntentClassification, User
from app.auth import get_current_active_user
from app.rag_system import rag_system
from typing import List

router = APIRouter(prefix="/api/chat", tags=["Chat & Query"])


@router.post("/query", response_model=QueryResponse)
async def query_hr_system(
    request: QueryRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Query the HR RAG system
    
    This endpoint:
    1. Classifies the intent (policy vs personal data)
    2. Retrieves relevant information from documents
    3. Generates a response using the LLM
    4. Provides source citations
    5. Suggests follow-up questions
    
    Requires: Authentication
    """
    try:
        # Classify intent
        intent = await rag_system.classify_intent(request.question)
        
        # Query the RAG system
        result = await rag_system.query(
            question=request.question,
            chat_history=request.chat_history
        )
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["message"]
            )
        
        # Generate follow-up suggestions
        suggestions = generate_suggestions(request.question, intent)
        
        # Prepare response
        response = QueryResponse(
            status="success",
            answer=result["answer"],
            sources=result["sources"] if request.include_sources else None,
            question=result["question"],
            intent=intent,
            suggestions=suggestions
        )
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query processing failed: {str(e)}"
        )


@router.post("/classify-intent", response_model=IntentClassification)
async def classify_question_intent(
    question: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Classify the intent of a user question
    
    Returns:
    - "policy": Question about company policies, procedures, or general information
    - "personal_data": Question about personal employee data or specific employee requests
    
    Requires: Authentication
    """
    intent = await rag_system.classify_intent(question)
    
    return IntentClassification(
        question=question,
        intent=intent,
        confidence=0.85  # Placeholder - implement proper confidence scoring
    )


@router.post("/suggest")
async def get_suggestions(
    question: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get follow-up question suggestions based on a query
    
    Requires: Authentication
    """
    intent = await rag_system.classify_intent(question)
    suggestions = generate_suggestions(question, intent)
    
    return {
        "status": "success",
        "original_question": question,
        "intent": intent,
        "suggestions": suggestions
    }


def generate_suggestions(question: str, intent: str) -> List[str]:
    """
    Generate contextual follow-up suggestions
    """
    question_lower = question.lower()
    
    # Common HR-related suggestions
    common_suggestions = [
        "What is the leave policy?",
        "How do I apply for sick leave?",
        "What are the working hours?",
        "How is performance evaluation conducted?"
    ]
    
    # Intent-specific suggestions
    if "leave" in question_lower or "sick" in question_lower:
        return [
            "How many sick leaves do employees get?",
            "Can sick leave be encashed?",
            "How do I apply for leave?",
            "What is the privilege leave policy?"
        ]
    elif "salary" in question_lower or "pay" in question_lower:
        return [
            "When is the salary paid?",
            "What are the salary components?",
            "How is the bonus calculated?",
            "What deductions are made from salary?"
        ]
    elif "performance" in question_lower or "appraisal" in question_lower:
        return [
            "How often is performance reviewed?",
            "What are the performance metrics?",
            "How is the rating decided?",
            "When is the appraisal cycle?"
        ]
    elif "work" in question_lower or "hours" in question_lower:
        return [
            "What are the working hours?",
            "Is remote work allowed?",
            "What is the overtime policy?",
            "How many work days in a week?"
        ]
    elif "holiday" in question_lower:
        return [
            "How many holidays in a year?",
            "What are the public holidays?",
            "Are holidays paid?",
            "Can we work on holidays?"
        ]
    else:
        return common_suggestions


@router.get("/health")
async def check_chat_health():
    """
    Health check for chat system
    """
    stats = rag_system.get_collection_stats()
    
    return {
        "status": "healthy",
        "rag_system": "initialized",
        "documents_loaded": stats.get("document_count", 0),
        "ready_for_queries": stats.get("document_count", 0) > 0
    }
