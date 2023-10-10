import os
from dotenv import load_dotenv
load_dotenv()

class Config(object):
    # Env
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    JSON_AS_ASCII = False
    JSONIFY_PRETTYPRINT_REGULAR = True
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')