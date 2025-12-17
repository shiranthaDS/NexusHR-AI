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
            
            # Create prompt
            prompt = f"""Answer the question based on the context below.

Context: {doc_context}

Question: {full_query}

Answer:"""
            
            # Get LLM response
            try:
                answer = self.llm.invoke(prompt)
                print(f"[RAG] Answer generated: {answer[:100]}...")
            except Exception as llm_error:
                print(f"[RAG] LLM invocation failed, using intelligent extraction: {str(llm_error)}")
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
        # Check for "how to" or procedural questions first
        if any(phrase in question for phrase in ['how do i', 'how to', 'how can i', 'process for', 'procedure']):
            # For procedural questions, give a concise answer
            if 'apply' in question and 'leave' in question:
                return "To apply for leave, please contact your HR manager or supervisor with your leave request, specifying the dates and type of leave (Casual, Sick, or Privilege Leave). Medical certificates are required for sick leave exceeding 2 consecutive days."
            elif 'apply' in question:
                return "Please contact your HR department or supervisor to initiate the application process. They will guide you through the required steps and documentation."
        
        # Define keyword mappings to sections
        section_keywords = {
            'benefits': ['benefit', 'insurance', '401', 'dental', 'vision', 'retirement', 'allowance'],
            'leave': ['leave', 'annual', 'sick', 'casual', 'privilege', 'maternity', 'paternity', 'vacation', 'pl', 'cl', 'sl'],
            'hours': ['hour', 'working hour', 'work time', '9:00', '5:00', 'schedule', 'attendance', 'late'],
            'salary': ['salary', 'pay', 'payment', 'payroll', 'compensation', 'wage'],
        }
        
        # Find which section the question is about
        question_section = None
        for section, keywords in section_keywords.items():
            if any(keyword in question for keyword in keywords):
                question_section = section
                break
        
        if not question_section:
            # If no specific section found, return a concise summary
            lines = context.split('\n')
            return self._create_summary_answer(question, lines)
        
        # Extract the relevant section from context
        # Note: Context comes as long strings, not line-by-line
        
        # Define section headers and boundaries
        section_mapping = {
            'benefits': {
                'start': '5. Employee Benefits',
                'keywords': ['employee benefits', 'health insurance', 'learning allowance']
            },
            'leave': {
                'start': '4. Leave Policy',
                'keywords': ['leave policy', 'casual leave', 'sick leave', 'privilege leave']
            },
            'hours': {
                'start': '2. Work Hours & Attendance',
                'keywords': ['work hours', 'standard hours', '9:00 am', 'attendance']
            },
            'salary': {
                'start': 'Salary',
                'keywords': ['salary', 'compensation', 'pay']
            }
        }
        
        section_info = section_mapping.get(question_section)
        if not section_info:
            return self._create_summary_answer(question, context.split('\n'))
        
        # Find section start
        context_lower = context.lower()
        start_marker = section_info['start'].lower()
        
        start_idx = context_lower.find(start_marker)
        if start_idx == -1:
            # Try keywords
            for keyword in section_info['keywords']:
                start_idx = context_lower.find(keyword)
                if start_idx != -1:
                    break
        
        if start_idx == -1:
            # Section not found, use summary
            return self._create_summary_answer(question, context.split('\n'))
        
        # Extract section content (find next numbered section to stop)
        section_text = context[start_idx:]
        
        # Find next section (numbered like "3. ", "4. ", "5. ", "6. ")
        import re
        next_section_match = re.search(r'\d+\.\s+[A-Z]', section_text[50:])  # Skip first 50 chars to avoid matching current section
        
        if next_section_match:
            section_text = section_text[:50 + next_section_match.start()]
        
        # Limit length to 500 chars max for conciseness
        if len(section_text) > 500:
            section_text = section_text[:500] + '...'
        
        # Clean up and format
        section_text = section_text.strip()
        if section_text:
            return f"Based on the company policies:\n\n{section_text}"
        
        # Fallback
        return self._create_summary_answer(question, context.split('\n'))
    
    def _create_summary_answer(self, question: str, lines: List[str]) -> str:
        """Create a concise, focused summary answer from context lines"""
        # Filter to non-empty lines with meaningful content
        content_lines = [line.strip() for line in lines if line.strip() and not line.strip().startswith('---') and len(line.strip()) > 10]
        
        # Extract meaningful keywords (excluding common words)
        common_words = {'what', 'how', 'when', 'where', 'who', 'is', 'are', 'the', 'a', 'an', 'do', 'does', 'can', 'i', 'my', 'about', 'for', 'with', 'that', 'this', 'be', 'to', 'of', 'in', 'on', 'at', 'tell', 'me', 'company'}
        question_keywords = [w.strip('?.,!').lower() for w in question.split() if w.lower() not in common_words and len(w) > 2]
        
        # If question is too general, provide a concise overview
        if len(question_keywords) <= 1 or any(word in question.lower() for word in ['tell me about', 'what is', 'explain', 'overview']):
            # For general questions, give a brief summary
            intro_lines = []
            for line in content_lines[:20]:  # Check first 20 lines
                # Skip section headers and list items
                if line.endswith(':') or line.startswith('•') or line.startswith('-'):
                    continue
                if len(line) > 30:  # Only substantial lines
                    intro_lines.append(line)
                    if len(intro_lines) >= 3:  # Max 3 lines for overview
                        break
            
            if intro_lines:
                return "Based on the company policies:\n\n" + '\n\n'.join(intro_lines)
        
        # For specific questions, find most relevant lines
        relevant_lines = []
        for line in content_lines:
            line_lower = line.lower()
            # Count keyword matches
            matches = sum(1 for kw in question_keywords if kw in line_lower)
            if matches > 0:
                relevant_lines.append((matches, line))
        
        # Sort by relevance and take top 4 lines (more concise)
        relevant_lines.sort(reverse=True, key=lambda x: x[0])
        best_lines = [line for _, line in relevant_lines[:4]]
        
        if best_lines:
            return "Based on the company policies:\n\n" + '\n'.join(best_lines)
        
        # Absolute fallback
        return "I apologize, but I couldn't find specific information to answer your question in the uploaded documents. Please try rephrasing or contact HR directly."
    
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
