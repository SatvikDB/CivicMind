import os
import certifi
from pymongo import MongoClient
from pymongo.collection import Collection

# Load .env file if present
_env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(_env_path):
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip())

MONGO_URI = os.environ.get("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError("MONGO_URI not set. Add it to backend/.env")

# Use "civicmind" as the database name within the cluster
DB_NAME = "civicmind"

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client[DB_NAME]

def get_complaints_collection() -> Collection:
    return db["complaints"]

def ping():
    """Quick connectivity check."""
    client.admin.command("ping")
    return True
