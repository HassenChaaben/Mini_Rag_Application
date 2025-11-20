from .BaseController import BaseController
from fastapi import UploadFile
import os

class ProjectController(BaseController):
    def __init__(self):
        super().__init__()
        
    def get_project_path(self, project_id: str):
        project_directory = os.path.join(self.files_dir, str(project_id))
        
        if not os.path.exists(project_directory):
            os.makedirs(project_directory)  # Create the directory if it does not exist
        return project_directory