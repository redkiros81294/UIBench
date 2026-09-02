"""
Database connection module.
"""
import os
from urllib.parse import quote_plus
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()


class Database:
    def __init__(self):
        db_name = os.getenv("DB_NAME", "uibench")
        uri = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

    def close(self):
        self.client.close()


db_instance = Database()
