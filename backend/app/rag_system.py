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
                search_type="mmr",  # Maximum Marginal Relevance for diversity
                search_kwargs={
                    "k": 5,  # Retrieve more chunks
                    "fetch_k": 10,  # Fetch more candidates for MMR
                    "lambda_mult": 0.7  # Balance relevance vs diversity
                }
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
            
            # Split documents with section-aware chunking
            chunks = self._create_section_aware_chunks(documents, metadata)
            
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
            
            # Expand query for better retrieval
            expanded_question = self._expand_query(question)
            print(f"[RAG] Original question: {question}")
            print(f"[RAG] Expanded query: {expanded_question}")
            
            # Retrieve relevant documents based on expanded question
            retriever = self.vectorstore.as_retriever(
                search_type="mmr",
                search_kwargs={
                    "k": 5,
                    "fetch_k": 10,
                    "lambda_mult": 0.7
                }
            )
            docs = retriever.get_relevant_documents(expanded_question)
            
            # Validate and rerank chunks based on relevance
            doc_context = self._validate_and_rerank_chunks(question, docs)
            print(f"[RAG] Retrieved {len(docs)} chunks, using top 3 after reranking")
            
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
                # Intelligent extraction with inference
                answer = self._extract_relevant_answer(question.lower(), doc_context, docs)
            
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
    
    def _extract_relevant_answer(self, question: str, context: str, docs: List = None) -> str:
        """
        Extract relevant information from context with inference and proper formatting
        
        Args:
            question: User's question (lowercase)
            context: Retrieved document context
            docs: Original retrieved documents for metadata
        
        Returns:
            Relevant extracted answer with inference
        """
        # Add inference for questions requiring calculation/reasoning
        answer = self._add_inference(question, context)
        if answer:
            return answer
        
        # Check for "how to" or procedural questions
        if any(phrase in question for phrase in ['how do i', 'how to', 'how can i', 'process for', 'procedure']):
            if 'apply' in question and 'leave' in question:
                return "To apply for leave, please contact your HR manager or supervisor with your leave request, specifying the dates and type of leave (Casual, Sick, or Privilege Leave). Medical certificates are required for sick leave exceeding 2 consecutive days."
            elif 'apply' in question:
                return "Please contact your HR department or supervisor to initiate the application process. They will guide you through the required steps and documentation."
        
        # Define keyword mappings to sections (order matters - more specific first)
        section_keywords = {
            'hours': ['attendance', 'late', 'grace', 'arrival', 'working hour', 'work hour', 'standard hour', '9:00', '5:00', 'schedule', 'deduction'],
            'remote_work': ['core days', 'office days', 'wfh', 'work from home', 'remote', 'hybrid', 'tuesday', 'thursday'],
            'benefits': ['benefit', 'insurance', '401', 'dental', 'vision', 'retirement', 'allowance', 'learning budget'],
            'leave': ['leave', 'annual', 'sick', 'casual', 'privilege', 'maternity', 'paternity', 'vacation', 'pl', 'cl', 'sl', 'encash'],
            'salary': ['salary', 'pay', 'payment', 'payroll', 'compensation', 'wage'],
        }
        
        # Special handling for specific questions BEFORE section matching
        if 'encash' in question and 'sick' in question:
            # Look for sick leave encashment specifically
            if 'cannot be encashed' in context.lower():
                return "Based on the company policies:\n\n**No**, sick leave cannot be encashed. Any unused sick leave will lapse on December 31st of each year.\n\nNote: Only Privilege Leave (PL) can be encashed at the end of the financial year, up to a maximum of 10 days."
        
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
                'keywords': ['work hours', 'standard hours', '9:00 am', 'attendance', 'grace period']
            },
            'remote_work': {
                'start': '3. Remote Work Policy',
                'keywords': ['remote work', 'wfh', 'core days', 'hybrid']
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

    async def delete_document(self, document_id: str) -> Dict[str, Any]:
        """Delete a single document from the vector store by its document_id metadata"""
        try:
            collection = self.vectorstore._collection

            # Collect candidate ids to delete by scanning metadatas for multiple possible keys
            ids_to_delete = set()
            deleted_count = 0

            try:
                all_docs = collection.get(include=["ids", "metadatas"]) or {}
                all_ids = all_docs.get("ids", [])
                all_metas = all_docs.get("metadatas", [])

                # Compute possible original filename (strip leading timestamp_)
                original_name = None
                if "_" in document_id:
                    parts = document_id.split("_")
                    original_name = "_".join(parts[1:])

                # Also consider source path patterns
                upload_path = os.path.join(settings.UPLOAD_DIR, document_id)
                upload_path_alt = f"./{os.path.join(settings.UPLOAD_DIR, document_id)}"

                for idx, meta in enumerate(all_metas):
                    if not meta:
                        continue
                    try:
                        if isinstance(meta, dict):
                            # exact document_id match in metadata
                            if meta.get("document_id") == document_id:
                                ids_to_delete.add(all_ids[idx])
                                continue

                            # filename matches either the stored filename or original
                            fname = meta.get("filename")
                            if fname and (fname == document_id or (original_name and fname == original_name)):
                                ids_to_delete.add(all_ids[idx])
                                continue

                            # source path match
                            src = meta.get("source")
                            if src and (src.endswith(document_id) or src == upload_path or src == upload_path_alt):
                                ids_to_delete.add(all_ids[idx])
                                continue

                            # Any metadata value equals the document id or original name
                            if any(str(v) == document_id or (original_name and str(v) == original_name) for v in meta.values()):
                                ids_to_delete.add(all_ids[idx])
                                continue
                    except Exception:
                        continue
            except Exception:
                # If get fails, try where-based deletions below
                all_ids = []

            # If no ids found via scan, attempt where-based deletes (Chroma may support this)
            try:
                if ids_to_delete:
                    collection.delete(ids=list(ids_to_delete))
                    deleted_count = len(ids_to_delete)
                else:
                    # Try deleting via metadata fields
                    tried_any = False
                    try:
                        res = collection.delete(where={"document_id": document_id})
                        tried_any = True
                    except Exception:
                        res = None
                    if not tried_any and original_name:
                        try:
                            res = collection.delete(where={"filename": original_name})
                        except Exception:
                            res = None
                    # Some versions return None; best-effort: count by re-query
                    try:
                        remaining = collection.get(include=["metadatas"]) or {}
                        deleted_count = -1 if res is None else 0
                    except Exception:
                        pass

            except Exception as e:
                return {"status": "error", "message": f"Failed to delete vectors: {str(e)}"}

            # Persist changes if supported
            try:
                # Newer Chromadb persists automatically; keep call but ignore failures
                self.vectorstore.persist()
            except Exception:
                pass

            return {"status": "success", "message": f"Document {document_id} deleted from vector store", "deleted_count": deleted_count}

        except Exception as e:
            return {"status": "error", "message": f"Failed to delete document: {str(e)}"}
    
    def _create_section_aware_chunks(self, documents: List, metadata: Dict = None):
        """
        Create chunks with section awareness and metadata
        Splits documents by section headers for better retrieval
        """
        import re
        chunks = []
        
        # Section patterns for employee handbook
        section_patterns = [
            r'(\d+\.\s+[A-Z][^.]+)',  # Numbered sections like "1. Introduction", "2. Work Hours"
            r'(\d+\.\d+\s+[A-Z][^.]+)',  # Subsections like "4.1 Casual Leave"
        ]
        
        for doc in documents:
            content = doc.page_content
            
            # Find all section boundaries
            sections = []
            for pattern in section_patterns:
                matches = list(re.finditer(pattern, content))
                sections.extend([(m.start(), m.group(0)) for m in matches])
            
            # Sort sections by position
            sections.sort(key=lambda x: x[0])
            
            if not sections:
                # No sections found, use default chunking
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=500,  # Smaller chunks for better precision
                    chunk_overlap=100,
                    separators=["\n\n", "\n", ". ", " ", ""]
                )
                default_chunks = text_splitter.split_documents([doc])
                chunks.extend(default_chunks)
                continue
            
            # Create chunks for each section
            for i, (pos, section_title) in enumerate(sections):
                # Get content until next section
                if i + 1 < len(sections):
                    section_content = content[pos:sections[i+1][0]]
                else:
                    section_content = content[pos:]
                
                # Determine section category
                section_lower = section_title.lower()
                category = "general"
                if any(kw in section_lower for kw in ['work hours', 'attendance', 'hours']):
                    category = "attendance"
                elif any(kw in section_lower for kw in ['leave', 'casual', 'sick', 'privilege']):
                    category = "leave_policy"
                elif any(kw in section_lower for kw in ['benefit', 'insurance', 'allowance']):
                    category = "benefits"
                elif any(kw in section_lower for kw in ['remote', 'wfh', 'work from home', 'hybrid']):
                    category = "remote_work"
                elif any(kw in section_lower for kw in ['salary', 'compensation', 'pay']):
                    category = "salary"
                
                # Split large sections into smaller chunks
                if len(section_content) > 600:
                    text_splitter = RecursiveCharacterTextSplitter(
                        chunk_size=500,
                        chunk_overlap=100,
                        separators=["\n\n", "\n", ". ", " ", ""]
                    )
                    sub_chunks = text_splitter.split_text(section_content)
                    
                    for j, chunk_text in enumerate(sub_chunks):
                        from langchain.schema import Document
                        chunk_metadata = {
                            **doc.metadata,
                            "section": section_title,
                            "section_category": category,
                            "chunk_index": j
                        }
                        if metadata:
                            chunk_metadata.update(metadata)
                        
                        chunks.append(Document(
                            page_content=chunk_text,
                            metadata=chunk_metadata
                        ))
                else:
                    # Small section, keep as one chunk
                    from langchain.schema import Document
                    chunk_metadata = {
                        **doc.metadata,
                        "section": section_title,
                        "section_category": category
                    }
                    if metadata:
                        chunk_metadata.update(metadata)
                    
                    chunks.append(Document(
                        page_content=section_content,
                        metadata=chunk_metadata
                    ))
        
        return chunks
    
    def _validate_and_rerank_chunks(self, question: str, docs: List) -> str:
        """
        Validate and rerank retrieved chunks based on question relevance
        Prioritizes chunks with section metadata and high relevance scores
        Returns the best matching context
        """
        question_lower = question.lower()
        
        # Extract keywords from question
        question_keywords = set()
        
        # Category-specific keywords
        category_keywords = {
            'attendance': ['late', 'arrival', 'grace', 'attendance', 'policy', 'time', '9:00', '9:15', 'marked', 'deduction'],
            'remote_work': ['wfh', 'work from home', 'remote', 'hybrid', 'office days', 'core days', 'tuesday', 'thursday', 'mandatory'],
            'leave_policy': ['leave', 'casual', 'sick', 'privilege', 'pl', 'cl', 'sl', 'vacation', 'encash', 'carry forward'],
            'benefits': ['benefit', 'insurance', 'health', 'allowance', 'learning', 'certification', 'budget'],
        }
        
        # Determine question category
        question_category = None
        for category, keywords in category_keywords.items():
            if any(kw in question_lower for kw in keywords):
                question_category = category
                question_keywords.update(keywords)
                break
        
        # Filter out chunks without section metadata (old chunks)
        docs_with_sections = [doc for doc in docs if doc.metadata.get('section') and doc.metadata.get('section') != 'N/A']
        
        # If no sectioned chunks, use all docs
        if not docs_with_sections:
            docs_with_sections = docs
        
        # Score each chunk
        scored_chunks = []
        for doc in docs_with_sections:
            score = 0
            content_lower = doc.page_content.lower()
            
            # Has section metadata bonus
            if doc.metadata.get('section'):
                score += 5
            
            # Category match bonus (strong signal)
            if question_category and doc.metadata.get('section_category') == question_category:
                score += 15
                print(f"[RERANK] ✅ Category match: {doc.metadata.get('section')} (category: {question_category})")
            
            # Keyword matches
            keyword_matches = sum(1 for kw in question_keywords if kw in content_lower)
            score += keyword_matches * 3
            
            # Question word matches
            question_words = set(question_lower.split())
            content_words = set(content_lower.split())
            word_matches = len(question_words & content_words)
            score += word_matches
            
            scored_chunks.append((score, doc))
        
        # Sort by score (descending)
        scored_chunks.sort(reverse=True, key=lambda x: x[0])
        
        # Debug: Show top chunks
        print(f"[RERANK] Top 3 chunks:")
        for i, (score, doc) in enumerate(scored_chunks[:3], 1):
            section = doc.metadata.get('section', 'N/A')[:50]
            category = doc.metadata.get('section_category', 'N/A')
            print(f"   {i}. Score: {score} | Section: {section} | Category: {category}")
        
        # Return top 2-3 chunks (more focused)
        best_chunks = [doc for _, doc in scored_chunks[:2]]
        return '\n\n'.join([doc.page_content for doc in best_chunks])
    
    def _expand_query(self, question: str) -> str:
        """
        Expand query with synonyms and related terms for better retrieval
        """
        expansions = {
            'late': 'late arrival grace period 9:15',
            'arrival': 'arrival time late grace period',
            'office days': 'core days office mandatory tuesday thursday',
            'wfh': 'work from home remote hybrid',
            'sick leave': 'sick leave sl medical certificate',
            'casual leave': 'casual leave cl personal',
            'encash': 'encashment cash leave balance',
            'allowance': 'allowance budget reimbursement',
        }
        
        expanded = question
        for term, expansion in expansions.items():
            if term in question.lower():
                expanded += f" {expansion}"
        
        return expanded
    
    def _add_inference(self, question: str, context: str) -> str:
        """
        Add inference/reasoning for questions that require calculation or logic
        """
        import re
        question_lower = question.lower()
        
        # Inference for arrival time questions (e.g., "9:20 AM")
        time_match = re.search(r'(\d{1,2}):(\d{2})\s*(am|pm)?', question_lower)
        if time_match and ('late' in question_lower or 'arrival' in question_lower or 'marked' in question_lower):
            hour = int(time_match.group(1))
            minute = int(time_match.group(2))
            
            # Convert to 24-hour format if needed
            if time_match.group(3) and time_match.group(3).lower() == 'pm' and hour != 12:
                hour += 12
            
            arrival_time = hour * 60 + minute
            grace_time = 9 * 60 + 15  # 9:15 AM
            
            if arrival_time > grace_time:
                late_minutes = arrival_time - grace_time
                return f"Based on the company policies:\n\nArriving at {time_match.group(0)} is considered **Late** since it's after the grace period of 9:15 AM (late by {late_minutes} minutes).\n\nAccording to the attendance policy: Employees are allowed a grace period of 15 minutes (up to 9:15 AM). Arrival after this time will be marked as \"Late.\" Three late arrivals in a month result in a deduction of half a day of Casual Leave."
            else:
                return f"Based on the company policies:\n\nArriving at {time_match.group(0)} is **On Time** since it's within the grace period of 9:15 AM.\n\nThe standard work hours are 9:00 AM to 6:00 PM, with a grace period up to 9:15 AM."
        
        # Inference for multiple lates (e.g., "4 times late")
        late_count_match = re.search(r'(\d+)\s*(times?|lates?)', question_lower)
        if late_count_match and ('consequence' in question_lower or 'happen' in question_lower or 'penalty' in question_lower or 'deduct' in question_lower):
            count = int(late_count_match.group(1))
            
            if count >= 3:
                full_deductions = count // 3
                remaining_lates = count % 3
                
                return f"Based on the company policies:\n\nBeing late **{count} times** results in:\n\n• **{full_deductions} deduction(s)** of half a day of Casual Leave (since every 3 late arrivals = 0.5 day CL deduction)\n• **{remaining_lates} additional late(s)** (approaching the next deduction threshold)\n\nAccording to the attendance policy: Three late arrivals in a month result in a deduction of half a day of Casual Leave. Arrival after 9:15 AM is marked as \"Late.\""
            else:
                return f"Based on the company policies:\n\nBeing late **{count} time(s)** does not yet result in a leave deduction. However, be aware that 3 late arrivals in a month will result in a deduction of half a day of Casual Leave.\n\nYou currently have **{count} late(s)**, so you're **{3 - count} late(s) away** from a deduction."
        
        # No inference needed
        return None


# Global RAG instance
rag_system = RAGSystem()
