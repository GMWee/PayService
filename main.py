from fastapi import FastAPI
from src.router import router
import logging

app = FastAPI()
app.include_router(router)
logger = logging.getLogger(__name__)

