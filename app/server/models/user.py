from server import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from server.models.mongodb import MongoDBConnector

mongo_connect_drama = MongoDBConnector('watchnext', 'user')
user_collection = mongo_connect_drama.get_collection()

class User(UserMixin):

    def __init__(self, user_dict):
        self.id = user_dict['_id']
        self.email = user_dict['email']
        self.username = user_dict['username']
        self.password_hash = user_dict['password_hash']
    def get_id(self):
        return str(self.email)

@login_manager.user_loader
def load_user(user_email):
    user_dict = user_collection.find_one({"email": user_email})
    if user_dict:
        return User(user_dict)
    return None