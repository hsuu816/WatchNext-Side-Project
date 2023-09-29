import os
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()

# password = os.getenv('mongo_password')
# conn = MongoClient(f"mongodb+srv://hsuu816:{password}@watchnext.edwg2oq.mongodb.net/")
# mongo_db = conn.watchnext
# collection = mongo_db.drama

class MongoDBConnector:
    def __init__(self, database_name, collection_name):
        self.password = os.getenv('mongo_password')
        self.conn = MongoClient(f"mongodb+srv://hsuu816:{self.password}@watchnext.edwg2oq.mongodb.net/")
        self.mongo_db = self.conn[database_name]
        self.collection = self.mongo_db[collection_name]
    
    def get_collection(self):
        return self.collection