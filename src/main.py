from fastapi import FastAPI
from routes import base , data
app = FastAPI()  # creates the app.
app.include_router(base.base_router)  # includes the base router in the app.
app.include_router(data.data_router)  # includes the data router in the app.