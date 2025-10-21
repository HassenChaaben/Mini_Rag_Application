import os 


# defined once in the main

class TemplateParser:
    def __init__(self , language:str=None , default_language:str="en"):
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        self.default_language = default_language
        self.language = None
        self.set_language(language)

    def set_language(self , language:str):
        if not language:
            self.language = self.default_language
            return None

        language_path = os.path.join(self.current_path , "locales" , language)
        if  os.path.exists(language_path):
            self.language = language
        else:
            self.language = self.default_language

    # we design a multilingual template parser from scratch that can load templates based on the user's language preference
    def get(self , group:str , key:str , vars:dict = {}):
        # in each language you will find group example rag
        # inside each group there are keys like system , document , footer
        # inside each key there are variables or maybe not
        
        if not group or not key:
            return None
        
        group_path = os.path.join(self.current_path , "locales" , self.language, f"{group}.py")
        
        targeted_language = self.language
        
        if not os.path.exists(group_path):
             group_path = os.path.join(self.current_path , "locales" , self.default_language, f"{group}.py")
             targeted_language = self.default_language


        if not os.path.exists(group_path):
            return None
        # import group module in Runtime
        # __import__ : we call it duck typing

        module = __import__(f"stores.llm.templates.locales.{targeted_language}.{group}", fromlist=[group])
        
        if not module :
            return None

        key_attribute = getattr(module, key) 
        return key_attribute.substitute(vars)
    
        