
from .providers import GeminiProvider
from .LLMEnums import LLMEnum
from .providers import OPENAIProvider
from .providers import coHereProvider
from .providers import GeminiProvider
from .providers import PerplexityProvider

class LLMProviderFactory:
    def __init__(self , config : dict):
        self.config = config 
    def create(self , provider:str):
        if provider == LLMEnum.OPENAI.value:
            return  OPENAIProvider(
                api_key = self.config.OPENAI_API_KEY,
                api_url = self.config.OPENAI_API_URL,
                default_input_max_characters = self.config.DEFAULT_INPUT_MAX_CHARACTERS,
                default_generation_max_output_tokens = self.config.default_generation_max_output_tokens,
                default_generation_temperature = self.config.DEFAULT_GENERATION_TEMPERATURE
            )
        if provider == LLMEnum.cohere.value:
            return coHereProvider(
                api_key = self.config.COHERE_API_KEY,
                default_input_max_characters = self.config.DEFAULT_INPUT_MAX_CHARACTERS,
                default_generation_max_output_tokens = self.config.default_generation_max_output_tokens,
                default_generation_temperature = self.config.DEFAULT_GENERATION_TEMPERATURE
            )
        
        if provider == LLMEnum.GEMINI.value:
            return GeminiProvider(
                api_key = self.config.GEMINI_API_KEY,
                default_input_max_characters = self.config.DEFAULT_INPUT_MAX_CHARACTERS,
                default_generation_max_output_tokens = self.config.default_generation_max_output_tokens,
                default_generation_temperature = self.config.DEFAULT_GENERATION_TEMPERATURE
            )
        if provider == LLMEnum.PERPLEXITY.value:
            return PerplexityProvider(
                api_key = self.config.PERPLEXITY_API_KEY,
                default_input_max_characters = self.config.DEFAULT_INPUT_MAX_CHARACTERS,
                default_generation_max_output_tokens = self.config.default_generation_max_output_tokens,
                default_generation_temperature = self.config.DEFAULT_GENERATION_TEMPERATURE
            )
        return None 