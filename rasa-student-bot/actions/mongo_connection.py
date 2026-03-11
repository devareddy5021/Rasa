# ============================================================
# database/mongo_connection.py
# MongoDB Atlas Connection Manager
# ============================================================
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import logging

logger = logging.getLogger(__name__)

# ── MongoDB Atlas Connection String ────────────────────────
# Set this in your .env file or environment variable:
#   MONGODB_URI=mongodb+srv://<user>:<password>@cluster0.xxxxx.mongodb.net/
MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb+srv://devareddy5021_db_user:Y2tipZvQcl3R9cE4@cluster0.tzc2jbx.mongodb.net/school_db?retryWrites=true&w=majority"
)

DB_NAME = os.getenv("MONGODB_DB", "school_db")


class MongoConnection:
    """Singleton MongoDB Atlas connection."""
    _client: MongoClient = None
    _db = None

    @classmethod
    def get_db(cls):
        if cls._client is None:
            try:
                cls._client = MongoClient(
                    MONGODB_URI,
                    serverSelectionTimeoutMS=5000,
                    connectTimeoutMS=10000,
                )
                # Verify connection
                cls._client.admin.command("ping")
                cls._db = cls._client[DB_NAME]
                logger.info(f"✅ Connected to MongoDB Atlas → {DB_NAME}")
            except (ConnectionFailure, ServerSelectionTimeoutError) as e:
                logger.error(f"❌ MongoDB connection failed: {e}")
                raise
        return cls._db

    @classmethod
    def close(cls):
        if cls._client:
            cls._client.close()
            cls._client = None
            logger.info("🔒 MongoDB connection closed.")


def get_students_collection():
    return MongoConnection.get_db()["students"]

def get_courses_collection():
    return MongoConnection.get_db()["courses"]
