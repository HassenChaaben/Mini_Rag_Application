from stores.llm.LLMInterface import LLMInterface
from openai import OpenAI
import logging
from  stores.llm.LLMEnums import OpenAIEnum 
class OPENAIProvider(LLMInterface):
    def __init__(self , api_key : str , api_url : str=None,
                default_input_max_characters:int=1000,
                default_generation_max_output_tokens:int=1000,
                default_generation_temperature:float=0.1):
        
        self.api_key = api_key
        self.api_url = api_url
        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature
        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None
        
        self.client = OpenAI(
            api_key = self.api_key,
            base_url = self.api_url 
        )
        
        self.Enums = OpenAIEnum
        
        self.logger = logging.getLogger(__name__)
        
    def set_generation_model(self , model_id:str):
        
        self.generation_model_id = model_id
        
    def set_embedding_model(self , model_id:str , embedding_size :int):
        
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size
        
    def process_text(self , text:str):
        return text[:self.default_input_max_characters].strip() # remove leading/trailing whitespace
    
    
        
    def generate_text(self , prompt:str, chat_history:list=[]  , max_output_tokens:int=None , temperature : float = None):
        
        if not self.client:
            self.logger.error("OpenAI client was not set")
            return None
        if not self.generation_model_id:
            self.logger.error("Generation model for OpenAI was not set")
            return None
        
        max_output_tokens = max_output_tokens if max_output_tokens  else self.default_generation_max_output_tokens
        temperature = temperature if temperature  else self.default_generation_temperature

        chat_history.append(self.contruct_prompt(prompt=prompt , role=OpenAIEnum.USER.value))
        response = self.client.chat.completions.create(
            model = self.generation_model_id ,
            messages = chat_history ,
            max_tokens = max_output_tokens ,
            temperature = temperature   
        )
        if not response or not response.choices or len(response.choices) == 0 or not response.choices[0].message:
            self.logger.error("Error while generating text with OpenAI")
            return None
        
        # Append assistant response to chat_history like in GeminiProvider
        assistant_message = response.choices[0].message.content
        chat_history.append(self.contruct_prompt(prompt=assistant_message, role=OpenAIEnum.ASSISTANT.value))
        
        return assistant_message

    def embed_text(self , text:str , document_type :str = None):
        # when dealing with third party , you should always over verfiy 
        # to metegate the error that means make the error lest harmfull
        
        if not self.client:
            # raise ValueError("OpenAI client is not initialized.") the error break the application 
            self.logger.error("OpenAI client was not set")
            return None 
        if not self.embedding_model_id:
            self.logger.error("Embedding model for OpenAI was not set") 
            return None 
        
        response = self.client.embeddings.create(
            model = self.embedding_model_id , 
            input = text
        )
        if not response or not response.data or len(response.data) == 0 or not response.data[0].embedding:
            self.logger.error("Error while embedding text with openAI")
            return None
        
        return response.data[0].embedding
            
    def contruct_prompt(self , prompt:str , role :str):
        return {
            "role":role,
            "content":self.process_text(prompt) # make sure that the prompt is not too long
        }
    
    
    
        
        
    
        
        
        
        