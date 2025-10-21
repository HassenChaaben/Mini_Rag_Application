from stores.llm.LLMInterface import LLMInterface
from stores.llm.LLMEnums import GeminiEnum
import google.generativeai as genai
import logging

logger = logging.getLogger(__name__)

class GeminiProvider(LLMInterface):
    def __init__(self, api_key: str, api_url: str = None,
                 default_input_max_characters: int = 1000,
                 default_generation_max_output_tokens: int = 1000,
                 default_generation_temperature: float = 0.1):
        
        self.api_key = api_key
        # Note: Gemini doesn't support custom base URLs, api_url is ignored
        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature
        
        # Configure the API
        genai.configure(api_key=self.api_key)
        
        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None
        
        self.Enums = GeminiEnum
        self.logger = logging.getLogger(__name__)
        
    def set_generation_model(self, model_id: str):
        """Set the generation model"""
        self.generation_model_id = model_id
        self.logger.info(f"Generation model set to: {model_id}")
        
    def set_embedding_model(self, model_id: str, embedding_size: int):
        """Set the embedding model"""
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size
        self.logger.info(f"Embedding model set to: {model_id} with size: {embedding_size}")
        
    def process_text(self, text: str):
        """Truncate text to default max characters"""
        return text[:self.default_input_max_characters].strip()
    
    def generate_text(self, prompt: str, chat_history: list = [], max_output_tokens: int = None, temperature: float = None):
        """
        Generate text using Gemini's chat API
        Note: System messages in chat_history are handled as system_instruction in Gemini
        """
        if not self.generation_model_id:
            self.logger.error("Generation model not set. Call set_generation_model() first.")
            return None
        
        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
        temperature = temperature if temperature else self.default_generation_temperature
        
        # Set generation config
        generation_config = genai.types.GenerationConfig(
            max_output_tokens=max_output_tokens,
            temperature=temperature
        )
        
        # Configure safety settings to be very permissive
        safety_settings = {
            genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
            genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH: genai.types.HarmBlockThreshold.BLOCK_NONE,
            genai.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: genai.types.HarmBlockThreshold.BLOCK_NONE,
            genai.types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
        }
        
        # Extract system instruction and build chat history
        system_instruction = None
        gemini_history = []
        
        for message in chat_history:
            role = message.get("role", "")
            
            # Get content - handle both formats
            content = message.get("content") or (message.get("parts", [None])[0] if message.get("parts") else None)
            
            if not content:
                continue
            
            # System messages become system_instruction
            if role in ["system", GeminiEnum.SYSTEM.value]:
                system_instruction = content
            elif role in ["user", GeminiEnum.USER.value]:
                gemini_history.append({"role": "user", "parts": [content]})
            elif role in ["assistant", "model", GeminiEnum.ASSISTANT.value]:
                gemini_history.append({"role": "model", "parts": [content]})
        
        # Log for debugging
        self.logger.info(f"System instruction length: {len(system_instruction) if system_instruction else 0}")
        self.logger.info(f"Chat history messages: {len(gemini_history)}")
        self.logger.info(f"Prompt length: {len(prompt)}")
        self.logger.info(f"Prompt preview (first 300 chars): {prompt[:300]}")
        
        # Create model with system instruction if available
        try:
            if system_instruction:
                model = genai.GenerativeModel(
                    self.generation_model_id,
                    system_instruction=system_instruction,
                    safety_settings=safety_settings
                )
                self.logger.info("Model created WITH system instruction and safety settings")
            else:
                model = genai.GenerativeModel(
                    self.generation_model_id,
                    safety_settings=safety_settings
                )
                self.logger.info("Model created WITHOUT system instruction but with safety settings")
            
            # Start chat with history
            chat = model.start_chat(history=gemini_history)
            self.logger.info("Chat started with history")
            
            # Send message
            response = chat.send_message(
                self.process_text(prompt),
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            # Check if response was blocked by safety filters
            if response.candidates:
                candidate = response.candidates[0]
                finish_reason = candidate.finish_reason
                
                # Log finish reason for debugging
                self.logger.info(f"Response finish_reason: {finish_reason}")
                
                # Check if blocked by safety (finish_reason == 2 is SAFETY)
                if finish_reason == 2:
                    self.logger.error("Response blocked by safety filters")
                    # Log safety ratings
                    if hasattr(candidate, 'safety_ratings') and candidate.safety_ratings:
                        self.logger.error(f"Safety ratings: {candidate.safety_ratings}")
                    
                    # Try to get partial content if available
                    try:
                        if hasattr(candidate, 'content') and candidate.content and hasattr(candidate.content, 'parts'):
                            parts = candidate.content.parts
                            if parts:
                                partial_text = ''.join([part.text for part in parts if hasattr(part, 'text')])
                                if partial_text:
                                    self.logger.info("Returning partial text before safety block")
                                    return partial_text
                    except:
                        pass
                    
                    # Return None or a fallback message
                    self.logger.error("No valid content available due to safety block")
                    return None
                
                # Check for other non-success finish reasons
                if finish_reason != 1:  # 1 is STOP (success)
                    self.logger.warning(f"Response finished with non-success reason: {finish_reason}")
            
            # Try to get the text
            try:
                response_text = response.text
            except ValueError as e:
                self.logger.error(f"Cannot access response.text: {str(e)}")
                return None
            
            if not response_text:
                self.logger.error("Empty response from Gemini")
                return None
            
            self.logger.info(f"Text generation successful. Response length: {len(response_text)}")
            
            # Append to chat_history like OpenAI
            chat_history.append(self.contruct_prompt(prompt=prompt, role=GeminiEnum.USER.value))
            chat_history.append(self.contruct_prompt(prompt=response_text, role=GeminiEnum.ASSISTANT.value))
            
            return response_text
            
        except Exception as e:
            self.logger.error(f"Error generating text with Gemini: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return None

    def embed_text(self, text: str, document_type: str = None):
        """Generate embeddings using Gemini's embedding API"""
        if not self.embedding_model_id:
            self.logger.error("Embedding model not set. Call set_embedding_model() first.")
            return None
        
        try:
            # Determine task type
            task_type = "RETRIEVAL_DOCUMENT" if document_type == "document" else "RETRIEVAL_QUERY"
            
            # Generate embedding
            result = genai.embed_content(
                model=self.embedding_model_id,
                content=text,
                task_type=task_type,
                output_dimensionality=self.embedding_size
            )
            
            if not result or 'embedding' not in result:
                self.logger.error("Error while embedding text with Gemini")
                return None
            
            return result['embedding']
            
        except Exception as e:
            self.logger.error(f"Error generating embedding with Gemini: {str(e)}")
            return None
            
    def contruct_prompt(self, prompt: str, role: str):
        """Construct a prompt - uses OpenAI-style format internally for consistency"""
        return {
            "role": role,
            "content": self.process_text(prompt)
        }
