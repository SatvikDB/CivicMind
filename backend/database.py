import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv(".env.local")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "civicmind")

client: AsyncIOMotorClient = None
db = None


async def connect_db():
    global client, db
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    # Create indexes
    await db.complaints.create_index("category")
    await db.complaints.create_index("status")
    await db.complaints.create_index("priority_level")
    await db.complaints.create_index("is_duplicate")
    await db.complaints.create_index("created_at")
    await db.complaints.create_index([("latitude", 1), ("longitude", 1)])
    print(f"Connected to MongoDB: {DB_NAME}")


async def close_db():
    global client
    if client:
        client.close()
        print("MongoDB connection closed")


def get_db():
    return db
