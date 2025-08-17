# A base.py file in a Python folder usually contains base classes,
# shared functions, or common logic that other modules in the package 
# can inherit from or use. 
# It's not a special file like __init__.py, 
# but is a common convention to organize reusable code and 
# avoid duplication within the package.

'''
FastAPI

is the main application class used to create your web app. 
You define your app with app = FastAPI() 
and run it as the entry point.

APIRouter

is used to organize groups of related routes. 
You create routers with router = APIRouter(), 
define endpoints on them, and then include them in your main 
FastAPI app. 
This helps keep your code modular and organized, 
especially for larger projects.

'''

from fastapi import FastAPI , APIRouter , Depends
import os 
from helpers.config import get_settings , Settings

base_router = APIRouter(
    prefix="/api/v1",
    tags=["api_v1"],
)
@base_router.get('/')
async def welcome(app_settings: Settings = Depends(get_settings)):
    # app_settings = get_settings()
    app_name = app_settings.APP_NAME
    app_version = app_settings.APP_VERSION
    return {
        "app_name": app_name,
        "app_version": app_version,
    }