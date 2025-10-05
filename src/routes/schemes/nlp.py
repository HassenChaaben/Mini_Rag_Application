from pydantic import BaseModel
from typing import Optional

class PushRequestschema(BaseModel):
    do_reset : Optional[int] = 0
    
class SearchRequestschema(BaseModel):
    text : str 
    limit : Optional[int] = 5