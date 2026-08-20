import os
import certifi
from pymongo import MongoClient
from pymongo.collection import Collection

MONGO_URI = os.environ.get(
    "NGO_URI",
    "mongodb+srv://satvikdb04_db_user:nq8ZR4L7CTjKdWGl@rvcookiebyte.ojr21j6.mongodb.net/vaulttag?retryWrites=true&w=majority&appName=RVCookieByteMongoDB"
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
