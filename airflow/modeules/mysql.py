import os
from dotenv import load_dotenv
import pymysql
load_dotenv()

class MySQLConnector:
    def __init__(self):
        self.host = os.environ.get('DB_HOST')
        self.username = os.environ.get('DB_USERNAME')
        self.password = os.environ.get('DB_PASSWORD')
        self.database = os.environ.get('DB_DATABASE')
        self.connection = None
        self.cursor = None

    def connect(self):
        self.connection = pymysql.connect(
            host=self.host,
            user=self.username,
            password=self.password,
            database=self.database,
            autocommit=True
        )
        self.cursor = self.connection.cursor()
        return self.cursor

    def disconnect(self):
        if self.connection:
            self.connection.close()