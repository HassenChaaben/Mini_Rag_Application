from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    
    APP_NAME: str
    APP_VERSION: str
    OPENAI_API_KEY: str
    FILE_ALLOWED_TYPES: List[str]
    FILE_MAX_SIZE: int  # in MB
    FILE_DEFAULT_CHUNK_SIZE: int  # in bytes
    MONGODB_URL: str
    MONGODB_DATABASE: str
    
    GENERATION_BACKEND: str
    EMBEDDING_BACKEND: str
    
    OPENAI_API_KEY: str=None
    OPENAI_API_URL:str=None
    COHERE_API_KEY: str=None
    GEMINI_API_KEY: str=None
    
    GENERATION_MODEL_ID: str=None
    EMBEDDING_MODEL_ID: str=None
    EMBEDDING_MODEL_SIZE:int = None
    DEFAULT_INPUT_MAX_CHARACTERS: int=None
    default_generation_max_output_tokens: int=None
    DEFAULT_GENERATION_TEMPERATURE: float=None
    
    VECTOR_DB_BACKEND:str
    VECTOR_DB_PATH:str 
    VECTOR_DB_DISTANCE_METHOD:str = None
     
    

    class Config:
        env_file = ".env"

def get_settings():
    return Settings()