from datetime import datetime, timedelta
from bson import ObjectId
from database import get_db


async def create_complaint(complaint_data: dict) -> dict:
    db = get_db()
    now = datetime.utcnow()
    doc = {
        **complaint_data,
        "category": "Unknown",
        "status": "Pending",
        "priority_score": 0.0,
        "priority_level": "Low",
        "sentiment": "Neutral",
        "recommended_action": "",
        "is_duplicate": False,
        "duplicate_of": None,
        "similarity_score": 0.0,
        "created_at": now,
        "updated_at": now,
    }
    result = await db.complaints.insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc


async def get_complaint(complaint_id: str) -> dict | None:
    db = get_db()
    return await db.complaints.find_one({"_id": ObjectId(complaint_id)})


async def get_all_complaints(skip: int = 0, limit: int = 100) -> list[dict]:
    db = get_db()
    cursor = db.complaints.find().sort("created_at", -1).skip(skip).limit(limit)
    return await cursor.to_list(length=limit)


async def get_complaints_for_similarity() -> list[dict]:
    db = get_db()
    cursor = db.complaints.find(
        {"is_duplicate": False},
        {"_id": 1, "description": 1},
    )
    docs = await cursor.to_list(length=10000)
    return [{"id": str(d["_id"]), "description": d["description"]} for d in docs]


async def update_complaint_status(complaint_id: str, status: str) -> dict | None:
    db = get_db()
    await db.complaints.update_one(
        {"_id": ObjectId(complaint_id)},
        {"$set": {"status": status, "updated_at": datetime.utcnow()}},
    )
    return await get_complaint(complaint_id)


async def update_complaint_ai_fields(complaint_id: str, ai_result: dict) -> dict | None:
    db = get_db()
    ai_result["duplicate_of"] = (
        str(ai_result["duplicate_of"]) if ai_result.get("duplicate_of") else None
    )
    await db.complaints.update_one(
        {"_id": ObjectId(complaint_id)},
        {"$set": {**ai_result, "updated_at": datetime.utcnow()}},
    )
    return await get_complaint(complaint_id)


async def get_dashboard_stats() -> dict:
    db = get_db()
    total = await db.complaints.count_documents({})
    high_priority = await db.complaints.count_documents(
        {"priority_level": {"$in": ["High", "Critical"]}}
    )
    duplicates = await db.complaints.count_documents({"is_duplicate": True})
    resolved = await db.complaints.count_documents({"status": "Resolved"})
    return {
        "total_complaints": total,
        "high_priority": high_priority,
        "potential_duplicates": duplicates,
        "resolved": resolved,
    }


async def get_analytics() -> dict:
    db = get_db()

    cat_cursor = db.complaints.aggregate([
        {"$group": {"_id": "$category", "count": {"$sum": 1}}}
    ])
    cat_docs = await cat_cursor.to_list(length=50)
    category_dist = [{"category": d["_id"], "count": d["count"]} for d in cat_docs]

    pri_cursor = db.complaints.aggregate([
        {"$group": {"_id": "$priority_level", "count": {"$sum": 1}}}
    ])
    pri_docs = await pri_cursor.to_list(length=50)
    priority_dist = [{"level": d["_id"], "count": d["count"]} for d in pri_docs]

    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    trend_cursor = db.complaints.aggregate([
        {"$match": {"created_at": {"$gte": thirty_days_ago}}},
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
            "count": {"$sum": 1},
        }},
        {"$sort": {"_id": 1}},
    ])
    trend_docs = await trend_cursor.to_list(length=30)
    trend_data = [{"date": d["_id"], "count": d["count"]} for d in trend_docs]

    return {
        "category_distribution": category_dist,
        "priority_distribution": priority_dist,
        "trend_data": trend_data,
    }


async def search_complaints(
    query: str = "", category: str = "", status: str = ""
) -> list[dict]:
    db = get_db()
    filter_query = {}
    if query:
        filter_query["$or"] = [
            {"title": {"$regex": query, "$options": "i"}},
            {"description": {"$regex": query, "$options": "i"}},
        ]
    if category:
        filter_query["category"] = category
    if status:
        filter_query["status"] = status

    cursor = db.complaints.find(filter_query).sort("created_at", -1)
    return await cursor.to_list(length=500)


async def get_map_complaints() -> list[dict]:
    db = get_db()
    cursor = db.complaints.find(
        {"latitude": {"$ne": None}, "longitude": {"$ne": None}},
        {
            "_id": 1, "title": 1, "category": 1,
            "priority_level": 1, "status": 1,
            "latitude": 1, "longitude": 1, "location_name": 1,
        },
    )
    docs = await cursor.to_list(length=10000)
    return [
        {
            "id": str(d["_id"]),
            "title": d["title"],
            "category": d["category"],
            "priority_level": d["priority_level"],
            "status": d["status"],
            "latitude": d["latitude"],
            "longitude": d["longitude"],
            "location_name": d["location_name"],
        }
        for d in docs
    ]
