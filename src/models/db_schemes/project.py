from pydantic import BaseModel, Field, validator, ConfigDict
from typing import Optional
from bson.objectid import ObjectId

class Project(BaseModel):
    #  tells Pydantic to accept fields with types that are not built-in or standard Pydantic types. This is useful when your model includes custom classes or third-party objects. Without this setting,
    # Pydantic would raise a validation error if you tried to use such types.
    
    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)

    id : Optional[ObjectId] = Field(default=None, alias="_id")
    # ... means the field is required , min_length condition
    project_id : str = Field(..., min_length=1)
    
    
    # create a validator manualy
    @validator('project_id')
    def validate_project_id(cls , value):
        if not value.isalnum():
            raise ValueError('Project ID must be alphanumeric')
        
        return value
    
    @classmethod
    def get_indexes(cls):
        return [
            {
                "key":[
                    ("project_id",1)
                ],
                "name":"project_id_index_1",
                "unique":True
            }
        ]
    