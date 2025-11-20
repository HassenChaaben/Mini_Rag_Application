from fastapi import FastAPI
from routes import base , data , nlp
from sqlalchemy.ext.asyncio import create_async_engine , AsyncSession
from sqlalchemy.orm import sessionmaker
from helpers.config import get_settings
from stores.llm import LLMProviderFactory
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory
from stores.llm.templates.template_parser import TemplateParser

app = FastAPI()  # creates the app.

@app.on_event("startup")
async def startup_span():
    settings = get_settings()

    
    postgres_conn = f"postgresql+asyncpg://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_MAIN_DATABASE}"
    app.db_engine = create_async_engine(postgres_conn)
    app.db_client = sessionmaker(
        app.db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    llm_provider_factory = LLMProviderFactory(config=settings)
    vectordb_provider_factory = VectorDBProviderFactory(config=settings , db_client = app.db_client)
    
    # generration client 
    app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)
    
    # embedding client
    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID , embedding_size=settings.EMBEDDING_MODEL_SIZE)
    
    # vectordb client
    app.vectordb_client = vectordb_provider_factory.create(provider=settings.VECTOR_DB_BACKEND)
    await app.vectordb_client.connect()
    
    # template parser
    app.template_parser = TemplateParser(language=settings.PRIMARY_LANGUAGE , default_language=settings.DEFAULT_LANGUAGE)
    
    
@app.on_event("shutdown")
async def shutdown_span():
    app.db_engine.dispose()
    await app.vectordb_client.disconnect()
app.include_router(base.base_router)  # includes the base router in the app.
app.include_router(data.data_router)  # includes the data router in the app.
app.include_router(nlp.nlp_router)  # includes the nlp router in the app.