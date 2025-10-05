from qdrant_client import QdrantClient , models
from ..VectorInterface import VectorInterface
from ..VectorDBEnums import DistanceMethodEnums
import logging 
from typing import List
import json

class QdrantDBProvider(VectorInterface):
    def __init__(self , db_path :str , distance_method:str):
        
        self.client = None 
        self.db_path = db_path
        self.distance_method = None 
        
        if distance_method == DistanceMethodEnums.COSINE.value:
            self.distance_method = models.Distance.COSINE
        elif distance_method == DistanceMethodEnums.DOT.value:
            self.distance_method = models.Distance.DOT
            
        self.logger = logging.getLogger(__name__)
        
    def connect(self):
        self.client = QdrantClient(path=self.db_path)
    
    def disconnect(self):
        self.client = None 
        
    def is_collection_existed(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name = collection_name)
    
    def list_all_collections(self) -> List:
        return self.client.get_collections()
    
    def get_collection_info(self, collection_name: str) -> dict:
        return self.client.get_collection(collection_name = collection_name)
    
    def delete_collection(self , collection_name:str):
        if self.is_collection_existed(collection_name):
            return self.client.delete_collection(collection_name = collection_name)
        return None
        
    def create_collection(self , collection_name:str , embedding_size:int , do_reset:int = 0):
        if do_reset :
            # _ means the return value is ignored
            _ = self.delete_collection(collection_name=collection_name)
            
             
        if not self.is_collection_existed(collection_name):
            _ = self.client.create_collection(
                collection_name = collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_size,
                    distance = self.distance_method
                ))
            return True
         
        return False
    
    def insert_one(self , collection_name:str , text:str , vector : List , 
                          metadata:dict = None,
                          record_id:str = None):
        # insert a row 
        if not self.is_collection_existed(collection_name):
            self.logger.error(f"Collection {collection_name} does not exist.")
            return False 
        
        try:
            record_params = {
                "vector": vector,
                "payload": {
                    "text": text,
                    "metadata": metadata
                }
            }
            if record_id is not None:
                record_params["id"] = record_id
            
            _ = self.client.upload_records(
                collection_name = collection_name,
                records = [models.Record(**record_params)]
            )
        except Exception as e:
            self.logger.error(f"Error inserting record into {collection_name}: {e}")
            return False
        
        return True
    
    def insert_many(self , collection_name:str , texts:List , vectors:List , 
                           metadata:List = None,
                           record_ids:List = None , batch_size:int = 50):
        if metadata is None:
            metadata = [None] * len(texts)
        if record_ids is None:
            record_ids = [None] * len(texts)
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            batch_vectors = vectors[i:i+batch_size]
            batch_metadata = metadata[i:i+batch_size]
            batch_records_ids = record_ids[i:i+batch_size]
            
            batch_records = []
            for x in range(len(batch_texts)):
                record_params = {
                    "vector": batch_vectors[x],
                    "payload": {
                        "text": batch_texts[x],
                        "metadata": batch_metadata[x]
                    }
                }
                if batch_records_ids[x] is not None:
                    record_params["id"] = batch_records_ids[x]
                
                batch_records.append(models.Record(**record_params))
            try:
                _ = self.client.upload_records(
                    collection_name = collection_name,
                    records = batch_records
                )
            except Exception as e:
                self.logger.error(f"Error inserting batch into {collection_name}: {e}")
                return False
        return True
    
    
    def search_by_vector(self , collection_name:str , vector : List , limit:int = 5):
        results = self.client.search(
            collection_name = collection_name,
            query_vector = vector,
            limit = limit
        )
        if not results:
            return False
        
        # the results may contain non-serializable objects, convert them to dict
        return json.loads(json.dumps(results, default=lambda x: x.__dict__))