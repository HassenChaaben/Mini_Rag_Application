from fastapi import FastAPI
from routes import base
from dotenv import load_dotenv
load_dotenv(".env")  # Load environment variables from a .env file

app = FastAPI()  # creates the app.
app.include_router(base.base_router)  # includes the base router in the app.