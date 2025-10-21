
from enum import Enum

class ResponseSignal(Enum):
    FILE_VALIDATED_SUCCESS = "File validated successfully."
    FILE_VALIDATION_FAILED = "File validation failed."
    FILE_TYPE_NOT_ALLOWED = "File type is not allowed."
    FILE_SIZE_EXCEEDED = "File size exceeds the maximum limit."
    FILE_UPLOAD_SUCCESS = "File uploaded successfully."
    FILE_UPLOAD_FAILED = "File upload failed."
    FILE_CHUNKING_FAILED = "File chunking failed."
    FILE_CHUNKING_SUCCESS = "File chunking succeeded."
    PROCESSING_FAILED = "Processing failed."
    NO_FILES_ERROR = "No files found."
    NO_FILE_ERROR = "This file was not found."
    PROJECT_NOT_FOUND = "Project not found."
    INSERT_INTO_VECTORDB_ERROR = "Error inserting into vector database." 
    INSERT_INTO_VECTORDB_SUCCESS = "Successfully inserted into vector database."
    VECTORDB_COLLECTION_RETRIEVED = "VectorDB collection retrieved."
    SEARCH_IN_VECTORDB_ERROR = "vectordb_search_error"
    VECTOR_SEARCH_SUCCESS = "vectordb_search_success"
    RAG_ANSWER_GENERATION_ERROR = "rag_answer_error"
    RAG_ANSWER_GENERATION_SUCCESS = "rag_answer_success"
    