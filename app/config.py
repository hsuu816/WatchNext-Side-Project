import os
from dotenv import load_dotenv
load_dotenv()

class Config(object):
    # Env
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    JSON_AS_ASCII = False
    JSONIFY_PRETTYPRINT_REGULAR = True
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')

    # Database
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{os.environ.get('DB_USERNAME')}:{os.environ.get('DB_PASSWORD')}@{os.environ.get('DB_HOST')}:3306/{os.environ.get('DB_DATABASE')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DB_HOST = os.environ.get('DB_HOST')
    DB_USERNAME = os.environ.get('DB_USERNAME')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_DATABASE = os.environ.get('DB_DATABASE')