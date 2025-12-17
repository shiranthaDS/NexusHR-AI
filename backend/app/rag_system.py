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
            
            # Initialize LLM with better parameters for concise answers
            print(f"Loading LLM: {settings.LLM_MODEL}")
            self.llm = HuggingFaceEndpoint(
                repo_id=settings.LLM_MODEL,
                huggingfacehub_api_token=settings.HUGGINGFACE_API_TOKEN,
                task="text2text-generation",
                temperature=0.3,  # Lower temperature for more focused answers
                max_new_tokens=150,  # Limit response length
                timeout=30  # Increase timeout to 30 seconds
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
            chat_context = ""
            if chat_history:
                chat_context = "\n".join([
                    f"User: {msg['question']}\nAssistant: {msg['answer']}"
                    for msg in chat_history[-3:]  # Last 3 exchanges
                ])
            
            # Prepare the query - use only the current question for retrieval
            print(f"[RAG] Current question: {question}")
            
            # Retrieve relevant documents based on CURRENT question only
            retriever = self.vectorstore.as_retriever(search_kwargs={"k": 3})
            docs = retriever.get_relevant_documents(question)
            
            # Build document context from retrieved documents
            doc_context = "\n\n".join([doc.page_content for doc in docs])
            
            # Create full query with chat history for context-aware responses
            full_query = f"{chat_context}\nUser: {question}" if chat_context else question
            
            # Create a focused prompt that limits the response length
            prompt = f"""Based on the context provided, answer the question concisely and directly.

Context:
{doc_context}

Question: {question}

Provide a clear, direct answer in 2-3 sentences. Only include information from the context that directly answers the question.

Answer:"""
            
            # Get LLM response
            try:
                answer = self.llm.invoke(prompt)
                print(f"[RAG] LLM answer: {answer[:150]}...")
                
                # Clean up the answer if it's too verbose
                if len(answer) > 600:
                    print("[RAG] LLM response too long, using intelligent extraction")
                    answer = self._extract_relevant_answer(question.lower(), doc_context)
            except Exception as llm_error:
                print(f"[RAG] LLM invocation failed ({str(llm_error)}), using intelligent extraction")
                # Intelligent extraction based on CURRENT question keywords only
                answer = self._extract_relevant_answer(question.lower(), doc_context)
            
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
    
    def _extract_relevant_answer(self, question: str, context: str) -> str:
        """
        Extract relevant information from context based on question keywords
        
        Args:
            question: User's question (lowercase)
            context: Full document context
        
        Returns:
            Relevant extracted answer
        """
        # Specific question pattern matching for precise answers
        lines = context.split('\n')
        question_lower = question.lower()
        
        # Pattern 1: Direct keyword matching in lines
        # Look for lines that contain key terms from the question
        question_keywords = set(question_lower.split())
        question_keywords.discard('how')
        question_keywords.discard('many')
        question_keywords.discard('what')
        question_keywords.discard('when')
        question_keywords.discard('where')
        question_keywords.discard('is')
        question_keywords.discard('are')
        question_keywords.discard('the')
        question_keywords.discard('do')
        question_keywords.discard('does')
        question_keywords.discard('can')
        
        # Find the most relevant lines (with highest keyword matches)
        scored_lines = []
        for i, line in enumerate(lines):
            line_lower = line.lower()
            score = sum(1 for kw in question_keywords if kw in line_lower)
            if score > 0 and line.strip():
                scored_lines.append((score, i, line.strip()))
        
        # Sort by score (highest first)
        scored_lines.sort(reverse=True, key=lambda x: x[0])
        
        # Get the top matching line and surrounding context
        if scored_lines:
            best_score, best_idx, best_line = scored_lines[0]
            
            # Collect context around the best match (3 lines before and 5 after)
            start_idx = max(0, best_idx - 3)
            end_idx = min(len(lines), best_idx + 6)
            
            context_lines = []
            for i in range(start_idx, end_idx):
                line = lines[i].strip()
                if line:
                    context_lines.append(line)
            
            # Format as a concise answer
            answer_text = '\n'.join(context_lines[:8])  # Limit to 8 lines max
            
            # If the answer is too long, try to find just the specific sub-section
            if len(answer_text) > 500:
                # Extract just the immediate answer
                immediate_answer = []
                found_answer = False
                for line in context_lines:
                    if any(kw in line.lower() for kw in question_keywords):
                        found_answer = True
                        immediate_answer.append(line)
                    elif found_answer and line.startswith('•'):
                        immediate_answer.append(line)
                    elif found_answer and not line.startswith('•') and len(immediate_answer) > 1:
                        break
                
                if immediate_answer:
                    answer_text = '\n'.join(immediate_answer[:5])
            
            return answer_text
        
        # Fallback: return first 5 non-empty lines
        content_lines = [line.strip() for line in lines if line.strip()][:5]
        return '\n'.join(content_lines)
    
    def _create_summary_answer(self, question: str, lines: List[str]) -> str:
        """Create a summary answer from context lines"""
        # Filter to non-empty lines
        content_lines = [line for line in lines if line.strip() and not line.strip().startswith('---')]
        
        # Try to find lines that contain key question words
        question_words = set(question.lower().split())
        relevant_lines = []
        
        for line in content_lines:
            line_words = set(line.lower().split())
            if question_words & line_words:  # If there's any overlap
                relevant_lines.append(line)
        
        if relevant_lines:
            return "Based on the company policies:\n\n" + '\n'.join(relevant_lines[:10])
        
        # Final fallback
        return "Based on the company policies:\n\n" + '\n'.join(content_lines[:10])
    
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
    
    async def delete_document(self, filename: str) -> Dict[str, Any]:
        """
        Delete a specific document from the vector store
        
        Args:
            filename: Name of the file to delete
        
        Returns:
            Dictionary with deletion status
        """
        try:
            collection = self.vectorstore._collection
            
            # Get all documents and filter by filename
            all_results = collection.get(include=['metadatas'])
            
            # Find IDs that match the filename
            ids_to_delete = []
            if all_results and all_results['ids']:
                for i, metadata in enumerate(all_results['metadatas']):
                    if metadata and 'source' in metadata:
                        # Check if filename is in the source path
                        if filename in metadata['source']:
                            ids_to_delete.append(all_results['ids'][i])
            
            if ids_to_delete:
                # Delete all chunks associated with this document
                collection.delete(ids=ids_to_delete)
                self.vectorstore.persist()
                
                return {
                    "status": "success",
                    "message": f"Document {filename} deleted from vector store",
                    "chunks_deleted": len(ids_to_delete)
                }
            else:
                return {
                    "status": "success",
                    "message": f"No vectors found for {filename}",
                    "chunks_deleted": 0
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to delete document: {str(e)}"
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
