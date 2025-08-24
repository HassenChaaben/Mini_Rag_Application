from pydantic import BaseModel, Field, validator, ConfigDict
from bson.objectid import ObjectId
from typing import Optional


class DataChunk(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    # __id : Optional[ObjectId] 
    id : Optional[ObjectId] = Field(default=None, alias="_id") 
    chunk_text : str = Field(..., min_length=1)
    chunk_metadata : dict 
    # greater than 0
    chunk_order : int = Field(..., gt=0)
    chunk_project_id:ObjectId
    
    
    @classmethod
    def get_indexes(cls):
        return [
            {
                "key":[
                    ("chunk_project_id",1)
                ],
                "name":"chunk_project_id_index_1",
                "unique":False
            }
        ]