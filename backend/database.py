import os
import certifi
from pymongo import MongoClient
from pymongo.collection import Collection

MONGO_URI = os.environ.get(
    "NGO_URI",
"-"
)

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
