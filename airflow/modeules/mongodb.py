import os
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()

class MongoDBConnector:
    def __init__(self):
        self.username = os.getenv('mongo_username')
        self.password = os.getenv('mongo_password')
        self.url = os.getenv('mongo_url')
        self.database = os.getenv('mongo_database')
        self.conn = MongoClient(f"mongodb+srv://{self.username}:{self.password}@{self.url}")
        self.mongo_db = self.conn[self.database]
        self.collections = self._initialize_collections()
    
    def get_collection(self, collection_name):
        return self.collections[collection_name]

    def _initialize_collections(self):
        collection_names = [
            'comment',
            'drama',
            'user',
            'user_rating',
            'drama_similarity_content_based',
            'drama_similarity_item_based',
            'drama_similarity_user_based'
        ]
        return {name: self.mongo_db[name] for name in collection_names}