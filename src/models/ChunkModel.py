from .BaseDataModel import BaseDataModel
from .db_schemes import DataChunk
from .enums.DataBaseEnum import DataBaseEnum
from pymongo import InsertOne
from bson.objectid import ObjectId

class ChunkModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]
    
    @classmethod
    async def create_instance(cls , db_client:object):
        instance = cls(db_client=db_client)
        await instance.init_collection()
        return instance
    
    async def init_collection(self):
        all_collections = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_CHUNK_NAME.value not in all_collections:
            self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]
            indexes = DataChunk.get_indexes()
            for index in indexes:
                await self.collection.create_index(index["key"], name=index["name"], unique=index["unique"])

    async def create_chunk(self , chunk: DataChunk):
        result = await self.collection.insert_one(chunk.dict(by_alias=True, exclude_unset=True))
        chunk.id = result.inserted_id
        return chunk
    
    async def get_chunk(self , chunk_id: str):
        record = await self.collection.find_one({
            "_id": chunk_id
        })
        if record is None:
            return None
        return DataChunk(**record)
    
    async def insert_multiple_chunks(self , chunks:list , Batch_size=100):
        
        for i in range(0,len(chunks), Batch_size):
            batch = chunks[i:i+Batch_size]
            # prepare the operation
            operations = [InsertOne(chunk.dict(by_alias=True, exclude_unset=True)) for chunk in batch]
            # insert many causea lot of promblems
            await self.collection.bulk_write(operations)
        return len(chunks)
    
    async def delete_chunks_by_project_id(self , project_id: ObjectId):
        result = await self.collection.delete_many({
            "chunk_project_id": project_id
        })
        return result.deleted_count
        
