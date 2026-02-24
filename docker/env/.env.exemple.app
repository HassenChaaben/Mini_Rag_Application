APP_NAME="MINI_RAG_APP"
APP_VERSION="0.1"

FILE_ALLOWED_TYPES = ["text/plain","application/pdf"] 
FILE_MAX_SIZE = 10  # 10 MB
FILE_DEFAULT_CHUNK_SIZE = 512000  # Default chunk size for file processing equivalent to 500 KB

POSTGRES_USERNAME="postgres"
POSTGRES_PASSWORD="postgres_password"
POSTGRES_HOST="pgvector"
POSTGRES_PORT=5432
POSTGRES_MAIN_DATABASE="mini_rag"


# =============================== LLM Config ==========================
GENERATION_BACKEND_LITERAL = ["OPENAI", "COHERE", "Google" , "Perplexity"]
GENERATION_BACKEND = "OPENAI"
EMBEDDING_BACKEND_LITERAL = ["OPENAI", "COHERE", "Google"]
EMBEDDING_BACKEND = "Google"

OPENAI_API_KEY=""
OPENAI_API_URL = "https://openrouter.ai/api/v1"
# OPENAI_API_URL = "https://dedicatedly-damoda-deonna.ngrok-free.dev/v1/"
COHERE_API_KEY="your_cohere_api_key_here"
PERPLEXITY_API_KEY = ""
GEMINI_API_KEY=""

GENERATION_MODEL_ID = "arcee-ai/trinity-large-preview:free"
EMBEDDING_MODEL_ID = "models/gemini-embedding-001"
EMBEDDING_MODEL_SIZE = 768

default_input_max_characters=1024
default_generation_max_output_tokens=2000
default_generation_temperature=0.1


# =============================== Vector DB Config  ==========================
VECTOR_DB_BACKEND_LITERAL = ["QDRANT", "PGVECTOR"]
VECTOR_DB_BACKEND = "PGVECTOR"
VECTOR_DB_PATH = "qdrant_db"
VECTOR_DB_DISTANCE_METHOD_LITERAL = ["cosine", "dot"]
VECTOR_DB_DISTANCE_METHOD = "cosine"
VECTOR_DB_PGVECTOR_INDEX_THRESHOLD = 100
# =============================== Template Config  ==========================

PRIMARY_LANGUAGE = "en"
DEFAULT_LANGUAGE = "en"