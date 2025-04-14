import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    DB_NAME = os.getenv("DB_NAME", "youtube-comments")
    COLLECTION_NAME = os.getenv("COLLECTION_NAME", "posts")
    DETOXIFY_MODEL = os.getenv("DETOXIFY_MODEL", "original")

__all__ = ['Config']