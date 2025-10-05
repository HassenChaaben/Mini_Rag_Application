from fastapi import FastAPI
from routes import base , data , nlp
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from stores.llm import LLMProviderFactory
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory
app = FastAPI()  # creates the app.

@app.on_event("startup")
async def startup_span():
    settings = get_settings()
    app.mongodb_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongodb_conn[settings.MONGODB_DATABASE]
    llm_provider_factory = LLMProviderFactory(config=settings)
    vectordb_provider_factory = VectorDBProviderFactory(config=settings)
    
    # generration client 
    app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)
    
    # embedding client
    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID , embedding_size=settings.EMBEDDING_MODEL_SIZE)
    
    # vectordb client
    app.vectordb_client = vectordb_provider_factory.create(provider=settings.VECTOR_DB_BACKEND)
    app.vectordb_client.connect()
    
    
@app.on_event("shutdown")
async def shutdown_span():
    app.mongodb_conn.close()
    app.vectordb_client.disconnect()
app.include_router(base.base_router)  # includes the base router in the app.
app.include_router(data.data_router)  # includes the data router in the app.
app.include_router(nlp.nlp_router)  # includes the nlp router in the app.