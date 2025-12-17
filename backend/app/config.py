from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Hugging Face Configuration
    HUGGINGFACE_API_TOKEN: str
    
    # Model Configuration
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    LLM_MODEL: str = "google/flan-t5-large"
    
    # ChromaDB Configuration
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    COLLECTION_NAME: str = "hr_documents"
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS Origins
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:3001"
    
    # Upload Configuration
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10485760  # 10MB
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


settings = Settings()
