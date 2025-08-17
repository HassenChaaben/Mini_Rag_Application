from .BaseController import BaseController
from .ProjectController import ProjectController
from fastapi import UploadFile
from models import ResponseSignal
import re
import os 
class DataController(BaseController):
    def __init__(self):
        super().__init__()
    def validate_uploaded_file(self, file: UploadFile):
        allowed_TYPES = self.app_settings.FILE_ALLOWED_TYPES
        max_size = self.app_settings.FILE_MAX_SIZE * 1024 * 1024
        
        if file.content_type not in allowed_TYPES:
            return False , ResponseSignal.FILE_TYPE_NOT_ALLOWED.value
        if file.size > max_size:
            return False, f'{ResponseSignal.FILE_SIZE_EXCEEDED.value} {max_size / (1024 * 1024)} MB. Your actual file size is {file.size / (1024 * 1024)} MB.'

        return True, ResponseSignal.FILE_VALIDATED_SUCCESS.value
    def generate_unique_file_name(self, original_file_name : str , project_id: str = None) -> str:
        random_key = self.generate_random_string()
        project_path = ProjectController().get_project_path(project_id)
        cleaned_file_name = self.get_clean_file_name(original_file_name)
        
        new_file_path = os.path.join(
            project_path,
            f"{random_key}_{cleaned_file_name}"
        )
        
        while os.path.exists(new_file_path):
            random_key = self.generate_random_string()
            new_file_path = os.path.join(
                project_path,
                f"{random_key}_{cleaned_file_name}"
            )
        return new_file_path, random_key + "_" + cleaned_file_name
    
    def get_clean_file_name(self, orig_file_name: str):

        # remove any special characters, except underscore and .
        cleaned_file_name = re.sub(r'[^\w.]', '', orig_file_name.strip())

        # replace spaces with underscore
        cleaned_file_name = cleaned_file_name.replace(" ", "_")

        return cleaned_file_name