# storage/mongo.py
from __future__ import annotations
import os
from datetime import datetime
from pymongo import MongoClient, errors
from pathlib import Path
from dotenv import load_dotenv

# --------------------------------------------------------------------
# Load environment (.env)
# --------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
else:
    print("⚠️  .env file not found — ensure MONGODB_URI is set manually")

# --------------------------------------------------------------------
# MongoDB Atlas Configuration
# --------------------------------------------------------------------
MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME", "code_translator")
COLL_NAME = os.getenv("COLLECTION_NAME", "job_history")

_client: MongoClient | None = None

# --------------------------------------------------------------------
# Connect / Get client
# --------------------------------------------------------------------
def _get_client() -> MongoClient:
    global _client
    if _client is not None:
        return _client

    if not MONGO_URI:
        raise RuntimeError("❌ MONGODB_URI not found in environment or .env file")

    try:
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        _client.admin.command("ping")
        print("✅ Connected to MongoDB Atlas successfully.")
        return _client
    except errors.ConnectionFailure as e:
        raise RuntimeError(f"❌ Could not connect to MongoDB Atlas: {e}") from e


# --------------------------------------------------------------------
# Store full job record
# --------------------------------------------------------------------
def save_full_job(job_data: dict):
    """Insert full job record (source, translated, report, metadata)."""
    try:
        client = _get_client()
        db = client[DB_NAME]
        coll = db[COLL_NAME]

        doc = {**job_data, "timestamp": datetime.utcnow()}
        result = coll.insert_one(doc)
        print(f"🟢 Stored job {doc.get('job_id')} in MongoDB (inserted_id={result.inserted_id})")

    except Exception as e:
        print(f"⚠️ Could not save job to MongoDB: {e}")



# --------------------------------------------------------------------
# Retrieve recent jobs
# --------------------------------------------------------------------
def list_recent_jobs(limit: int = 25):
    try:
        client = _get_client()
        db = client[DB_NAME]
        coll = db[COLL_NAME]
        print(f"Using DB={DB_NAME}, Collection={COLL_NAME}")
        count = coll.count_documents({})
        print(f"Total jobs in MongoDB: {count}")

        cur = coll.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit)
        jobs = list(cur)
        print(f"📄 Retrieved {len(jobs)} job docs.")
        return jobs
    except Exception as e:
        print(f"⚠️ Could not fetch jobs from MongoDB: {e}")
        return []
