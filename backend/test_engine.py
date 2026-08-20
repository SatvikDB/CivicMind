from database import SessionLocal
import models
from ai_engine import process_complaint_ai

db = SessionLocal()
existing = db.query(models.Complaint).all()
existing_texts = [f"{c.title}. {c.description}" for c in existing]

print(f"Loaded {len(existing_texts)} existing complaints from database.")

# Test 1: Unique issue
res1 = process_complaint_ai(
    title="Broken CCTV Camera at North Gate",
    description="The security surveillance camera at the north entry gate is not functioning.",
    category_input="Safety",
    location="North Gate Ward 4",
    existing_complaints_texts=existing_texts
)
print("Test 1 Result:", res1)

# Test 2: Duplicate issue (Pothole near college gate)
res2 = process_complaint_ai(
    title="Deep Pothole near College Gate 2",
    description="Massive crater road defect near college gate 2 skidding two wheelers.",
    category_input="Road",
    location="College Gate Avenue",
    existing_complaints_texts=existing_texts
)
print("\nTest 2 (Duplicate Pothole) Result:")
print(f"Similarity Score: {res2['similarity_score']}%")
print(f"Priority Score: {res2['priority_score']} ({res2['priority_level']})")
print("Recommendation:", res2['recommendation'].encode('ascii', errors='ignore').decode())

assert res2["similarity_score"] >= 50.0, "Duplicate detection failed!"
assert "DUPLICATE ALERT" in res2["recommendation"], "Recommendation duplicate alert missing!"

print("\n[SUCCESS] ALL DIRECT AI ENGINE TESTS PASSED PERFECTLY!")
db.close()
