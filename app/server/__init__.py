from flask import Flask
from werkzeug.exceptions import HTTPException

app = Flask(__name__)

@app.errorhandler(404)
def server_error(error):
    return "Page not found", 404

@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return e
    return "Internal Server Error", 500

from server.controllers import drama_controller