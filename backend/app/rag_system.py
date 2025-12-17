from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from typing import List, Dict, Any
import os
from app.config import settings


class RAGSystem:
    """
    Core RAG System for NexusHR AI
    Handles document ingestion, vector storage, and retrieval
    """
    
    def __init__(self):
        self.embedding_model = None
        self.vectorstore = None
        self.llm = None
        self.retrieval_chain = None
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize embeddings, vector store, and LLM"""
        try:
            # Initialize embeddings
            print(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
            self.embedding_model = HuggingFaceEmbeddings(
                model_name=settings.EMBEDDING_MODEL,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            
            # Initialize or load ChromaDB
            print(f"Initializing ChromaDB at: {settings.CHROMA_PERSIST_DIRECTORY}")
            os.makedirs(settings.CHROMA_PERSIST_DIRECTORY, exist_ok=True)
            
            self.vectorstore = Chroma(
                collection_name=settings.COLLECTION_NAME,
                embedding_function=self.embedding_model,
                persist_directory=settings.CHROMA_PERSIST_DIRECTORY
            )
            
            # Initialize LLM
            print(f"Loading LLM: {settings.LLM_MODEL}")
            self.llm = HuggingFaceEndpoint(
                repo_id=settings.LLM_MODEL,
                huggingfacehub_api_token=settings.HUGGINGFACE_API_TOKEN,
                task="text2text-generation",
                temperature=0.7,
                max_new_tokens=256
            )
            
            # Create retrieval chain
            self._create_retrieval_chain()
            
            print("RAG System initialized successfully")
            
        except Exception as e:
            print(f"Error initializing RAG System: {str(e)}")
            raise
    
    def _create_retrieval_chain(self):
        """Create the retrieval QA chain"""
        if self.vectorstore and self.llm:
            retriever = self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 3}
            )
            
            # Create a prompt template for FLAN-T5
            prompt_template = """Answer the question based on the context below.

Context: {context}

Question: {question}

Answer:"""
            
            PROMPT = PromptTemplate(
                template=prompt_template,
                input_variables=["context", "question"]
            )
            
            self.retrieval_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=retriever,
                return_source_documents=True,
                chain_type_kwargs={"prompt": PROMPT}
            )
    
    async def ingest_document(self, file_path: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Ingest a PDF document into the vector store
        
        Args:
            file_path: Path to the PDF file
            metadata: Additional metadata for the document
        
        Returns:
            Dictionary with ingestion status and details
        """
        try:
            # Load PDF
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            
            # Add metadata
            if metadata:
                for doc in documents:
                    doc.metadata.update(metadata)
            
            # Split documents
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
                separators=["\n\n", "\n", " ", ""]
            )
            chunks = text_splitter.split_documents(documents)
            
            # Add to vector store
            self.vectorstore.add_documents(chunks)
            self.vectorstore.persist()
            
            return {
                "status": "success",
                "message": f"Successfully ingested document: {os.path.basename(file_path)}",
                "chunks_created": len(chunks),
                "pages_processed": len(documents)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to ingest document: {str(e)}"
            }
    
    async def query(self, question: str, chat_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Query the RAG system
        
        Args:
            question: User's question
            chat_history: Previous chat messages for context
        
        Returns:
            Dictionary with answer and source documents
        """
        try:
            if not self.retrieval_chain:
                return {
                    "status": "error",
                    "message": "RAG system not properly initialized"
                }
            
            # Build context from chat history
            context = ""
            if chat_history:
                context = "\n".join([
                    f"User: {msg['question']}\nAssistant: {msg['answer']}"
                    for msg in chat_history[-3:]  # Last 3 exchanges
                ])
            
            # Prepare the query
            full_query = f"{context}\nUser: {question}" if context else question
            
            # Get response - using manual RAG instead of RetrievalQA due to HF API issues
            print(f"[RAG] Querying with: {full_query[:100]}...")
            
            # Retrieve relevant documents
            retriever = self.vectorstore.as_retriever(search_kwargs={"k": 3})
            docs = retriever.get_relevant_documents(full_query)
            
            # Build context from retrieved documents
            context = "\n\n".join([doc.page_content for doc in docs])
            
            # Create prompt
            prompt = f"""Answer the question based on the context below.

Context: {context}

Question: {full_query}

Answer:"""
            
            # Get LLM response
            try:
                answer = self.llm.invoke(prompt)
                print(f"[RAG] Answer generated: {answer[:100]}...")
            except Exception as llm_error:
                print(f"[RAG] LLM invocation failed, using fallback: {str(llm_error)}")
                # Fallback to context-based answer
                answer = f"Based on the company policies: {context[:500]}..."
            
            # Extract source documents
            sources = []
            for doc in docs:
                sources.append({
                    "content": doc.page_content[:200] + "...",
                    "metadata": doc.metadata
                })
            
            return {
                "status": "success",
                "answer": answer,
                "sources": sources,
                "question": question
            }
            
        except Exception as e:
            print(f"[RAG] Query error: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "message": f"Query failed: {type(e).__name__}: {str(e)}"
            }
    
    async def classify_intent(self, question: str) -> str:
        """
        Classify user intent (Policy Question vs Personal Data Request)
        
        Args:
            question: User's question
        
        Returns:
            Intent type: "policy" or "personal_data"
        """
        # Simple keyword-based classification
        personal_keywords = ["my", "i have", "i want", "can i", "do i"]
        policy_keywords = ["policy", "how many", "what is", "when", "who can"]
        
        question_lower = question.lower()
        
        personal_count = sum(1 for kw in personal_keywords if kw in question_lower)
        policy_count = sum(1 for kw in policy_keywords if kw in question_lower)
        
        return "personal_data" if personal_count > policy_count else "policy"
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store collection"""
        try:
            collection = self.vectorstore._collection
            count = collection.count()
            
            return {
                "status": "success",
                "collection_name": settings.COLLECTION_NAME,
                "document_count": count,
                "embedding_model": settings.EMBEDDING_MODEL
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get stats: {str(e)}"
            }
    
    async def delete_all_documents(self) -> Dict[str, Any]:
        """Clear all documents from the vector store"""
        try:
            # Get all IDs and delete them
            collection = self.vectorstore._collection
            collection.delete()
            
            # Reinitialize the collection
            self.vectorstore = Chroma(
                collection_name=settings.COLLECTION_NAME,
                embedding_function=self.embedding_model,
                persist_directory=settings.CHROMA_PERSIST_DIRECTORY
            )
            
            return {
                "status": "success",
                "message": "All documents deleted successfully"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to delete documents: {str(e)}"
            }


# Global RAG instance
rag_system = RAGSystem()
