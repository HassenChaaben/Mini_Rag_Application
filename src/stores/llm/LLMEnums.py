from enum import Enum 

class LLMEnum(Enum):
    OPENAI = "OPENAI"
    cohere = "COHERE"
    GEMINI = "Google"

class OpenAIEnum(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
class coHereEnum(Enum):
    SYSTEM = "SYSTEM"
    USER = "USER"
    ASSISTANT = "CHATBOT"
    DOCUMENT = "search_document"
    QUERY = "search_query"
    

class GeminiEnum(Enum):
    SYSTEM = "system"  
    USER = "user"
    ASSISTANT = "model"
    
class DocumentTypeEnum(Enum):
    DOCUMENT = "document"
    QUERY = "query"