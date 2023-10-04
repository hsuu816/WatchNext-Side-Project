from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_login import LoginManager
# from werkzeug.exceptions import HTTPException


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@app.errorhandler(404)
def server_error(error):
    return "Page not found", 404

# @app.errorhandler(Exception)
# def handle_exception(e):
#     if isinstance(e, HTTPException):
#         return e
#     return "Internal Server Error", 500

from server.controllers import drama_controller, user_controller