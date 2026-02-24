from ..VectorInterface import VectorInterface
from ..VectorDBEnums import (DistanceMethodEnums ,PgVectorTableSchemesEnums , 
                             PgVectorDistanceMethodEnums , PgVectorIndexTypeEnums)

from models.db_schemes import RetrievedDocument
import logging 
from typing import List
from sqlalchemy import text as sql_text
from sqlalchemy.exc import IntegrityError
import json 

class PGVectorProvider(VectorInterface):
    
    def __init__(self , db_client , default_vector_size:int = 786 , 
                 distance_method:str=None , index_threshold:int = 100):
        
        self.db_client = db_client
        self.default_vector_size = default_vector_size
        
        self.pgvector_table_prefix = PgVectorTableSchemesEnums._PREFIX.value
        self.logger = logging.getLogger("uvicorn")
        
        self.index_threshold = index_threshold
        
        if distance_method == DistanceMethodEnums.COSINE.value:
            distance_method = PgVectorDistanceMethodEnums.COSINE.value
        elif distance_method == DistanceMethodEnums.DOT.value:
            distance_method = PgVectorDistanceMethodEnums.DOT.value
        
        
        self.distance_method = distance_method
        self.default_index_name = lambda collection_name: f"{collection_name}_vector_idx"
    
    async def get_pgvector_index_name(self , collection_name:str): 
        return  f"{collection_name}_vector_idx"
        
    async def connect(self):
        try:
            async with self.db_client() as session:
                async with session.begin():
                    await session.execute(sql_text(
                        "CREATE EXTENSION IF NOT EXISTS vector;"
                    ))
                    await session.commit()
        except IntegrityError:
            # vector extension already exists — safe to ignore
            pass
        
    async def disconnect(self):
        pass
    
    async def is_collection_existed(self, collection_name: str) -> bool:
        record = None
        async with self.db_client() as session:
            async with session.begin():
                list_table = sql_text(
                    f"SELECT * FROM pg_tables WHERE tablename = '{collection_name}'"
                                      )
                result = await session.execute(list_table)
                record = result.scalar_one_or_none()
        return record
    
    async def list_all_collections(self) -> List:
        records = [] 
        async with self.db_client() as session:
            async with session.begin():
                list_table = sql_text(
                    "SELECT tablename FROM pg_tables WHERE tablename LIKE :prefix"
                )
                results = await session.execute(list_table, {"prefix": self.pgvector_table_prefix})
                records = results.scalars().all()
                
        return records

    async def get_collection_info(self, collection_name: str) -> dict:
        async with self.db_client() as session:
            async with session.begin():
                table_info_sql = sql_text("""
                    SELECT schemaname, tablename , tableowner , tablespace , hasindexes 
                    FROM pg_tables 
                    WHERE tablename = :collection_name
                """)
                count_sql = sql_text(f'SELECT COUNT(*) FROM {collection_name}')
                
                table_info_result = await session.execute(table_info_sql , {
                    "collection_name": collection_name
                })
                
                record_count = await session.execute(count_sql)
                
                table_Data = table_info_result.fetchone()
                if not table_Data:
                    return None 
                return {
                    "table_info" : {
                        "schemaname": table_Data[0],
                        "tablename": table_Data[1],
                        "tableowner": table_Data[2],
                        "tablespace": table_Data[3],
                        "hasindexes": table_Data[4]
                        },
                    "record_count": record_count.scalar_one()
                }
                
    async def delete_collection(self , collection_name:str):
        async with self.db_client() as session:
            async with session.begin():
                self.logger.info(f"Deleting collection {collection_name}")
                drop_table_sql = sql_text(f'DROP TABLE IF EXISTS {collection_name}')
                await session.execute(drop_table_sql, {"collection_name": collection_name})
                # when you drop or create you should commit the transaction immediately
                await session.commit()
            return True 
    
    async def create_collection(self , collection_name:str , embedding_size:int , do_reset:bool = False):
        if do_reset :
            _ = await self.delete_collection(collection_name=collection_name)
        
        is_collection_existed = await self.is_collection_existed(collection_name = collection_name)
        
        if not is_collection_existed:
            self.logger.info(f"creating collection {collection_name}")
            async with self.db_client() as session:
                async with session.begin():
                    create_sql = sql_text(
                        f'CREATE TABLE {collection_name} ('
                            f'{PgVectorTableSchemesEnums.ID.value} bigserial PRIMARY KEY,'
                            f'{PgVectorTableSchemesEnums.TEXT.value} text,'
                            f'{PgVectorTableSchemesEnums.VECTOR.value} vector ({embedding_size}),'
                            f'{PgVectorTableSchemesEnums.CHUNK_ID.value} integer,'
                            f'{PgVectorTableSchemesEnums.METADATA.value} jsonb DEFAULT \'{{}}\','
                            f'FOREIGN KEY ({PgVectorTableSchemesEnums.CHUNK_ID.value}) REFERENCES chunks(chunk_id)'
                            
                        ')'
                    )
                    await session.execute(create_sql)
                    await session.commit()
                return True
            
        return False


    async def is_index_existed(self , collection_name :str )-> bool:
        index_name = self.default_index_name(collection_name)
        async with self.db_client() as session:
            async with session.begin():
                index_check_sql = sql_text("""
                                           SELECT 1
                                           FROM pg_indexes 
                                           WHERE tablename = :collection_name
                                           AND indexname = :index_name
                                           """
                )
                result = await session.execute(index_check_sql , {
                    "collection_name": collection_name,
                    "index_name": index_name
                })
                
                return bool(result.scalar_one_or_none())
    
    async def create_vector_index(self , collection_name:str , index_type:str = PgVectorIndexTypeEnums.HNSW.value):
        is_index_existed = await self.is_index_existed(collection_name = collection_name)
        if is_index_existed:
            return False
        
        async with self.db_client() as session:
            async with session.begin():
                count_sql = sql_text(f'SELECT COUNT(*) FROM {collection_name}')
                result = await session.execute(count_sql)
                record_count = result.scalar_one()
                
                if record_count < self.index_threshold:
                    self.logger.info(f"Skipping index creation for collection {collection_name} as record count {record_count} is below threshold {self.index_threshold}")
                    return False
                
                self.logger.info(f"START : Creating index for collection {collection_name} with index type {index_type}")

                index_name = await self.get_pgvector_index_name(collection_name = collection_name)
                create_idx_sql = sql_text(
                    f'CREATE INDEX {index_name} ON {collection_name} '
                    f'USING {index_type} ({PgVectorTableSchemesEnums.VECTOR.value} {self.distance_method}) '
                )
                
                # for debugging purpose
                print(create_idx_sql)
                
                await session.execute(create_idx_sql)
                await session.commit()
                self.logger.info(f"END: Created vector index for collection {collection_name}")
                
                
    
    
    async def reset_vector_index(self , collection_name:str , 
                                 index_type:str = PgVectorIndexTypeEnums.HNSW.value) -> bool:
        index_name = self.default_index_name(collection_name)
        async with self.db_client() as session:
            async with session.begin():
                drop_sql = sql_text(f"DROP INDEX IF EXISTS {index_name}")
                await session.execute(drop_sql)
                await session.commit()
        
        return await self.create_vector_index(collection_name = collection_name , index_type = index_type)
        
    
    
    
    
    
    async def insert_one(self , collection_name:str , text:str , vector : List , 
                          metadata:dict = None,
                          record_id:str = None):
        
        is_collection_existed = await self.is_collection_existed(collection_name = collection_name)
        
        if not is_collection_existed:
            self.logger.error(f"can not insert to non-existing collection {collection_name}")
            return False
        
        if not record_id:
            self.logger.error(f"Can not insert new record without chunk_id: {collection_name}")
            return False
        
        async with self.db_client() as session:
            async with session.begin():
                insert_sql = sql_text(f'INSERT INTO {collection_name} '
                                      f'({PgVectorTableSchemesEnums.TEXT.value}, {PgVectorTableSchemesEnums.VECTOR.value}, {PgVectorTableSchemesEnums.METADATA.value}, {PgVectorTableSchemesEnums.CHUNK_ID.value}) '
                                      '(VALUES (:text, :vector, :metadata, :chunk_id))'
                                      )
                await session.execute(insert_sql, {
                    "text":text ,
                    # postgres expects vector in string format
                    "vector": "["+",".join([str(v) for v in vector]) + "]",
                    "metadata":json.dumps(metadata , ensure_ascii=False) if metadata else "{}",
                    "chunk_id": record_id
                })
                session.commit()
                
            await self.create_vector_index(collection_name = collection_name)
                
            return True
                                    
    async def insert_many(self , collection_name:str , texts:List , vectors:List , 
                           metadata:List = None,
                           record_ids:List = None , batch_size:int = 50):
        
        is_collection_existed = await self.is_collection_existed(collection_name = collection_name)
        
        if not is_collection_existed:
            self.logger.error(f"can not insert to non-existing collection {collection_name}")
            return False
        
        if len(vectors) != len(texts):
            self.logger.error(f"Invalid data items for collection: {collection_name}")
            return False
        
        if not metadata or len(metadata) == 0:
            metadata = [None] * len(texts)
        
        async with self.db_client() as session:
            async with session.begin():
                for i in range(0 , len(texts) , batch_size):
                    batch_texts = texts[i:i+batch_size]
                    batch_vectors = vectors[i:i+batch_size]
                    batch_metadata = metadata[i:i+batch_size]
                    batch_record_ids = record_ids[i:i+batch_size] 
                    
                    values = []
                    
                    for _text , _vector , _metadata , _record_id in zip(batch_texts , batch_vectors , batch_metadata , batch_record_ids):
                        meta_json = json.dumps(_metadata , ensure_ascii=False) if _metadata else "{}"
                        values.append({
                            "text": _text,
                            "vector": "["+",".join([str(v) for v in _vector]) + "]",
                            "metadata": meta_json,
                            "chunk_id": _record_id
                        })
                    
                    batch_insert_sql = sql_text(f'INSERT INTO {collection_name} '
                                          f'({PgVectorTableSchemesEnums.TEXT.value}, '
                                          f'{PgVectorTableSchemesEnums.VECTOR.value}, '
                                          f'{PgVectorTableSchemesEnums.METADATA.value}, '
                                          f'{PgVectorTableSchemesEnums.CHUNK_ID.value}) '
                                          'VALUES (:text, :vector, :metadata, :chunk_id)'
                                          )
                    await session.execute(batch_insert_sql , values)
                                    
            await self.create_vector_index(collection_name = collection_name)
            
            return True

    async def search_by_vector(self , collection_name:str , vector : List , limit:int) -> List[RetrievedDocument]:
        is_collection_existed = await self.is_collection_existed(collection_name = collection_name)
        if not is_collection_existed:
            self.logger.error(f"can not search in non-existing collection {collection_name}")
            return False
        
        vector = "["+",".join([str(v) for v in vector]) + "]"
        async with self.db_client() as session:
            async with session.begin():
                search_sql = sql_text(
                    f'SELECT {PgVectorTableSchemesEnums.TEXT.value} as text , '
                    f'1 - ({PgVectorTableSchemesEnums.VECTOR.value} <=> :vector) as score '
                    f'FROM {collection_name} '
                    f'ORDER BY score DESC '
                    f'LIMIT {limit}'
                )
                result = await session.execute(search_sql, {"vector": vector})
                records = result.fetchall()
                
                return [
                    RetrievedDocument(
                        text = record.text,
                        score = record.score
                    ) for record in records
                ]


