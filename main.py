
from fastapi import FastAPI
app = FastAPI()  # creates the app.

@app.get('/welcome')
def welcome():
    return {"message": "Welcome to our website!"}