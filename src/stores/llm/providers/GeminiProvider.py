from stores.llm.LLMInterface import LLMInterface
import google.generativeai as genai
import logging
from stores.llm.LLMEnums import GeminiEnum


class GeminiProvider(LLMInterface):
    def __init__(self, api_key: str, api_url: str = None,
                 default_input_max_characters: int = 1000,
                 default_generation_max_output_tokens: int = 1000,
                 default_generation_temperature: float = 0.1):
        
        self.api_key = api_key
        self.api_url = api_url  # Note: Gemini does not support custom base URLs
        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature
        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None
        self.generation_model = None
        
        # Configure the Gemini API
        genai.configure(api_key=self.api_key)
        
        self.logger = logging.getLogger(__name__)
        
    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id
        self.generation_model = genai.GenerativeModel(model_id)
        
    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size
        
    def process_text(self, text: str):
        return text[:self.default_input_max_characters].strip()
    
    def generate_text(self, prompt: str, chat_history: list = [], max_output_tokens: int = None, temperature: float = None):
        
        if not self.generation_model:
            self.logger.error("Gemini generation model was not set")
            return None
        
        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
        temperature = temperature if temperature else self.default_generation_temperature
        
        try:
            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=max_output_tokens,
                temperature=temperature
            )
            
            # Convert chat history to Gemini format
            gemini_history = []
            for msg in chat_history:
                role = msg.get("role")
                content = msg.get("content")
                
                # Map roles to Gemini format (user/model)
                if role == GeminiEnum.USER.value:
                    gemini_history.append({"role": "user", "parts": [content]})
                elif role == GeminiEnum.ASSISTANT.value:
                    gemini_history.append({"role": "model", "parts": [content]})
            
            # Start chat with history
            chat = self.generation_model.start_chat(history=gemini_history)
            
            # Send the current prompt
            response = chat.send_message(
                self.process_text(prompt),
                generation_config=generation_config
            )
            
            if not response or not response.text:
                self.logger.error("Error while generating text with Gemini")
                return None
                
            return response.text
            
        except Exception as e:
            self.logger.error(f"Error while generating text with Gemini: {str(e)}")
            return None

    def embed_text(self, text: str, document_type: str = None):
        
        if not self.embedding_model_id:
            self.logger.error("Embedding model for Gemini was not set")
            return None
        
        try:
            # Set task type based on document_type
            task_type = "retrieval_document"
            if document_type == "query":
                task_type = "retrieval_query"
            
            # Prepare embedding parameters
            embed_params = {
                "model": self.embedding_model_id,
                "content": text,
                "task_type": task_type
            }
            
            # Add output_dimensionality if embedding_size is specified
            # Gemini supports flexible dimensions from 1-768 for text-embedding-004
            # Recommended values: 768, 1536, 3072 for gemini-embedding-001
            if self.embedding_size:
                embed_params["output_dimensionality"] = self.embedding_size
            
            # Generate embedding
            result = genai.embed_content(**embed_params)
            
            if not result or not result.get('embedding'):
                self.logger.error("Error while embedding text with Gemini")
                return None
            
            return result['embedding']
            
        except Exception as e:
            self.logger.error(f"Error while embedding text with Gemini: {str(e)}")
            return None
            
    def contruct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "content": self.process_text(prompt)
        }
