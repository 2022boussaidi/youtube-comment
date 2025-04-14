from pymongo import MongoClient
from config.settings import Config

class MongoService:
    def __init__(self):
        self.client = MongoClient(Config.MONGO_URI)
        self.db = self.client[Config.DB_NAME]
        self.collection = self.db[Config.COLLECTION_NAME]
    
    def insert_comment(self, comment_data):
        return self.collection.insert_one(comment_data)
    
    def close_connection(self):
        self.client.close()