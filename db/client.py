from typing import Optional
from pymongo import MongoClient
from api.config import MONGO_URI, DB_NAME, COLLECTION, require_mongo_uri

_client: Optional[MongoClient] = None

def get_client() -> MongoClient:
    global _client
    if _client is None:
        require_mongo_uri()
        _client = MongoClient(MONGO_URI, uuidRepresentation="standard")
    return _client

def get_collection():
    client = get_client()
    return client[DB_NAME][COLLECTION]