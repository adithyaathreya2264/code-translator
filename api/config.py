from dotenv import load_dotenv
load_dotenv() 
import os

# Simple config loader. Reads Mongo URI from env.
MONGO_URI = os.getenv("MONGODB_URI", "").strip()
DB_NAME = os.getenv("MONGODB_DB", "code_translator")
COLLECTION = os.getenv("MONGODB_COLLECTION", "verifications")

# Fail fast if URI missing when API starts
def require_mongo_uri():
    if not MONGO_URI:
        raise RuntimeError(
            "MONGODB_URI not set. Define it in your environment (Atlas connection string)."
        )