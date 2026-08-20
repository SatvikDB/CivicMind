"""
Seed the MongoDB complaints collection with 18 realistic demo complaints.
Run:  python3 seed.py
"""

from datetime import datetime, timedelta
from database import get_complaints_collection, db

def seed_database():
    col = get_complaints_collection()
    col.drop()
    db["counters"].drop()

    # Reset auto-increment counter
    db["counters"].insert_one({"_id": "complaint_id", "seq": 0})

    now = datetime.utcnow()

    seed_data = [
        {
            "name": "Aarav Sharma",
            "title": "Massive Pothole near College Gate 2",
            "description": "A deep crater-like pothole has developed right at the main entrance gate. Two two-wheelers skidded yesterday. Urgent asphalt patch required.",
            "category": "Road",
            "location": "Main Campus Road, Ward 12",
            "latitude": 12.3124, "longitude": 76.6512,
            "severity": "Critical", "sentiment": "Urgent",
            "similarity_score": 85.5, "priority_score": 92, "priority_level": "Critical",
            "recommendation": "⚠️ DUPLICATE ALERT (85.5% match): Dispatch PWD Emergency Asphalt Crew within 6h to inspect and repair severe road hazard at Main Campus Road, Ward 12.",
            "status": "In Progress", "hours_ago": 6,
            "escalation_level": "Level 1: Local Authority",
        },
        {
            "name": "Priya N",
            "title": "Deep crater on college gate road",
            "description": "Large road defect causing heavy traffic bottleneck near college gate 2 during peak hours. Needs immediate paving.",
            "category": "Road",
            "location": "College Gate 2 Avenue",
            "latitude": 12.3128, "longitude": 76.6515,
            "severity": "High", "sentiment": "Urgent",
            "similarity_score": 88.2, "priority_score": 89, "priority_level": "Critical",
            "recommendation": "⚠️ DUPLICATE ALERT (88.2% match): Combine repair order with ticket #1 on Main Campus Road.",
            "status": "Pending", "hours_ago": 4,
            "escalation_level": "Level 1: Local Authority",
        },
        {
            "name": "Rajesh Kumar",
            "title": "Exposed Live Wire hanging from Electrical Pole",
            "description": "High voltage wire snapped and hanging dangerously low near the primary school playground. Potential electrocution risk!",
            "category": "Safety",
            "location": "Saraswathipuram 4th Main",
            "latitude": 12.3089, "longitude": 76.6432,
            "severity": "Critical", "sentiment": "Urgent",
            "similarity_score": 0.0, "priority_score": 98, "priority_level": "Critical",
            "recommendation": "EMERGENCY ELECTRIC: Dispatch Lineman immediately to fix exposed live wire/blackout pole at Saraswathipuram 4th Main.",
            "status": "OVERDUE", "hours_ago": 54,
            "escalation_level": "Level 2: Department Officer",
        },
        {
            "name": "Kavitha R",
            "title": "Contaminated Water Supply with Foul Smell",
            "description": "Drinking water coming out of municipal tap is muddy brown and has a foul chemical odor. Entire block affected.",
            "category": "Water",
            "location": "Gokulam 3rd Stage",
            "latitude": 12.3245, "longitude": 76.6321,
            "severity": "Critical", "sentiment": "Frustrated",
            "similarity_score": 12.0, "priority_score": 86, "priority_level": "Critical",
            "recommendation": "ALERT WATER BOARD: Shut off damaged main line & dispatch repair squad within 4h at Gokulam 3rd Stage.",
            "status": "Pending", "hours_ago": 42,
            "escalation_level": "Level 1: Local Authority",
        },
        {
            "name": "Suresh Babu",
            "title": "Overflowing Garbage Dumpster on Commercial Street",
            "description": "Community bin has not been cleared for 4 days. Waste spilled onto street, creating foul smell and attracting stray animals.",
            "category": "Waste",
            "location": "KD Road Commercial Hub",
            "latitude": 12.3180, "longitude": 76.6480,
            "severity": "High", "sentiment": "Frustrated",
            "similarity_score": 35.0, "priority_score": 75, "priority_level": "High",
            "recommendation": "Assign Ward Sanitation Crew for bin clearance and debris removal within 12h at KD Road Commercial Hub.",
            "status": "OVERDUE", "hours_ago": 76,
            "escalation_level": "Level 3: Senior Authority",
        },
        {
            "name": "Ananya Hegde",
            "title": "Unlit Streetlights for 500 meters",
            "description": "All 8 LED streetlights along the park stretch are completely dark. Safety hazard for women and pedestrians walking at night.",
            "category": "Streetlight",
            "location": "Kukkarahalli Lake Perimeter Road",
            "latitude": 12.3050, "longitude": 76.6380,
            "severity": "High", "sentiment": "Negative",
            "similarity_score": 15.0, "priority_score": 71, "priority_level": "High",
            "recommendation": "Assign Municipal Electrical Tech to replace faulty LED streetlight fixtures at Kukkarahalli Lake Perimeter Road within 24h.",
            "status": "In Progress", "hours_ago": 24,
            "escalation_level": "Level 1: Local Authority",
        },
        {
            "name": "Mohammed Zaid",
            "title": "Open Manhole Cover on Bus Stop Footpath",
            "description": "Concrete manhole slab broken into pieces leaving a 4ft open pit on the busy footpath. Pedestrians can fall in at night.",
            "category": "Drainage",
            "location": "RTO Circle Bus Stop",
            "latitude": 12.2990, "longitude": 76.6550,
            "severity": "Critical", "sentiment": "Urgent",
            "similarity_score": 0.0, "priority_score": 95, "priority_level": "Critical",
            "recommendation": "URGENT DRAINAGE TEAM: Deploy suction tanker & jetting machine to replace slab and unblock manhole at RTO Circle Bus Stop.",
            "status": "Pending", "hours_ago": 12,
            "escalation_level": "Level 1: Local Authority",
        },
        {
            "name": "Divya Prakash",
            "title": "Water Pipeline Leakage Wasting Drinking Water",
            "description": "Underground main line valve burst under sidewalk. Clean drinking water gushing onto the main road since morning.",
            "category": "Water",
            "location": "Jayalakshmipuram 1st Main",
            "latitude": 12.3160, "longitude": 76.6350,
            "severity": "High", "sentiment": "Urgent",
            "similarity_score": 62.4, "priority_score": 78, "priority_level": "High",
            "recommendation": "⚠️ DUPLICATE ALERT (62.4% match): Deploy Water Supply Engineer to inspect pipeline leak at Jayalakshmipuram 1st Main within 12h.",
            "status": "Resolved", "hours_ago": 48, "resolved_hours_ago": 18,
            "resolution_photo": "https://images.unsplash.com/photo-1584992236310-6edddc08acff?auto=format&fit=crop&w=600&q=80",
            "resolution_note": "Replaced damaged 4-inch PVC main valve connection and sealed sidewalk paving. Water pressure restored to normal.",
            "resolved_by": "Eng. Ramesh V (Water Board Ward 4)",
            "escalation_level": "Level 1: Local Authority",
        },
        {
            "name": "Manjunath V",
            "title": "Stagnant Drainage Water breeding mosquitoes",
            "description": "Stormwater drain blocked with plastic bottles and silt. Water standing still for over a week, posing dengue risk.",
            "category": "Drainage",
            "location": "Hebbal Industrial Area Block B",
            "latitude": 12.3410, "longitude": 76.6210,
            "severity": "Medium", "sentiment": "Frustrated",
            "similarity_score": 22.0, "priority_score": 58, "priority_level": "Medium",
            "recommendation": "Dispatch Stormwater Drain Crew to clear silt and debris blockage at Hebbal Industrial Area Block B.",
            "status": "In Progress", "hours_ago": 36,
            "escalation_level": "Level 1: Local Authority",
        },
        {
            "name": "Deepak Mehta",
            "title": "Traffic Signal Malfunction causing congestion",
            "description": "Both red and green signals flashing simultaneously at major crossroad. Chaotic vehicle movements and minor collisions.",
            "category": "Safety",
            "location": "Metropole Circle Junction",
            "latitude": 12.3030, "longitude": 76.6470,
            "severity": "High", "sentiment": "Urgent",
            "similarity_score": 5.0, "priority_score": 79, "priority_level": "High",
            "recommendation": "Notify Traffic Control & Municipal Safety Inspector to resolve signal malfunction at Metropole Circle Junction.",
            "status": "Resolved", "hours_ago": 60, "resolved_hours_ago": 38,
            "resolution_photo": "https://images.unsplash.com/photo-1508873696983-2df515122519?auto=format&fit=crop&w=600&q=80",
            "resolution_note": "Replaced shorted traffic signal controller circuit board. Synchronized timing with traffic control center.",
            "resolved_by": "Officer K. Swamy (Traffic Signals Div)",
            "escalation_level": "Level 1: Local Authority",
        },
        {
            "name": "Siddharth Rao",
            "title": "Fallen Tree Branch blocking half lane",
            "description": "Heavy monsoon wind broke large Gulmohar branch which is resting on street power line and partial lane.",
            "category": "Safety",
            "location": "Vontikoppal Temple Road",
            "latitude": 12.3210, "longitude": 76.6410,
            "severity": "Medium", "sentiment": "Neutral",
            "similarity_score": 10.0, "priority_score": 52, "priority_level": "Medium",
            "recommendation": "Dispatch Parks & Forestry clearance team with wood cutter to Vontikoppal Temple Road.",
            "status": "Resolved", "hours_ago": 72, "resolved_hours_ago": 50,
            "resolution_photo": "https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?auto=format&fit=crop&w=600&q=80",
            "resolution_note": "Forestry crew sawed fallen branches and cleared roadway completely. Power line re-inspected safely.",
            "resolved_by": "Parks Supervisor T. Narayan",
            "escalation_level": "Level 1: Local Authority",
        },
        {
            "name": "Meera Joshi",
            "title": "Broken Streetlight Pole tilted precariously",
            "description": "Delivery truck hit streetlight pole midnight. Pole is bent at 45 degree angle towards sidewalk.",
            "category": "Streetlight",
            "location": "Vijayanagar 2nd Stage",
            "latitude": 12.3290, "longitude": 76.6190,
            "severity": "High", "sentiment": "Negative",
            "similarity_score": 45.0, "priority_score": 74, "priority_level": "High",
            "recommendation": "Assign Municipal Electrical Tech to secure and replace damaged streetlight pole at Vijayanagar 2nd Stage.",
            "status": "In Progress", "hours_ago": 30,
            "escalation_level": "Level 1: Local Authority",
        },
        {
            "name": "Vikram Singh",
            "title": "Construction Waste Dumped on Footpath",
            "description": "Private contractor dumped 2 tons of concrete debris and sand bags on pedestrian sidewalk.",
            "category": "Waste",
            "location": "TK Layout 3rd Cross",
            "latitude": 12.2930, "longitude": 76.6340,
            "severity": "Medium", "sentiment": "Frustrated",
            "similarity_score": 18.0, "priority_score": 54, "priority_level": "Medium",
            "recommendation": "Issue municipal penalty notice and dispatch debris truck to TK Layout 3rd Cross.",
            "status": "Pending", "hours_ago": 15,
            "escalation_level": "Level 1: Local Authority",
        },
        {
            "name": "Nandini Gowda",
            "title": "Sewage Backflow in Residential Street",
            "description": "Main sewer line blocked causing foul black water to overflow from chambers onto domestic compound gates.",
            "category": "Drainage",
            "location": "Boghadi Ring Road Junction",
            "latitude": 12.2980, "longitude": 76.6120,
            "severity": "Critical", "sentiment": "Urgent",
            "similarity_score": 78.0, "priority_score": 91, "priority_level": "Critical",
            "recommendation": "⚠️ DUPLICATE ALERT (78.0% match): Deploy suction tanker & jetting machine to unblock flooding sewer line at Boghadi Ring Road Junction.",
            "status": "In Progress", "hours_ago": 10,
            "escalation_level": "Level 1: Local Authority",
        },
        {
            "name": "Arun Prasad",
            "title": "Low Water Pressure in Top Floors",
            "description": "Over the last 3 days water pressure is extremely low, barely filling overhead tanks in the residential area.",
            "category": "Water",
            "location": "Kuvempunagar Block M",
            "latitude": 12.2850, "longitude": 76.6390,
            "severity": "Low", "sentiment": "Neutral",
            "similarity_score": 12.0, "priority_score": 38, "priority_level": "Low",
            "recommendation": "Schedule valve and pipe pressure audit at Kuvempunagar Block M.",
            "status": "Resolved", "hours_ago": 96, "resolved_hours_ago": 70,
            "resolution_photo": "https://images.unsplash.com/photo-1581094794329-c8112a89af12?auto=format&fit=crop&w=600&q=80",
            "resolution_note": "Adjusted booster pump pressure at sub-station 3. Water head pressure restored to standard 2.5 bar.",
            "resolved_by": "Tech. Sunil Kumar (Water Div)",
            "escalation_level": "Level 1: Local Authority",
        },
        {
            "name": "Sneha K",
            "title": "Damaged Speed Breaker with protruding iron rebar",
            "description": "Speed bump worn out exposing sharp iron rebar spikes that puncture car and bike tires.",
            "category": "Road",
            "location": "Hunsur Road Junction",
            "latitude": 12.3110, "longitude": 76.6310,
            "severity": "High", "sentiment": "Negative",
            "similarity_score": 20.0, "priority_score": 76, "priority_level": "High",
            "recommendation": "Schedule Ward Road Maintenance Unit to cut exposed rebar and re-lay rubberized speed breaker at Hunsur Road.",
            "status": "Pending", "hours_ago": 14,
            "escalation_level": "Level 1: Local Authority",
        },
        {
            "name": "Karthik Subramanian",
            "title": "Garbage Heap near Government Primary Health Center",
            "description": "Uncollected medical carton boxes and household waste piled up outside clinic perimeter wall.",
            "category": "Waste",
            "location": "Agrahara Health Center Alley",
            "latitude": 12.2920, "longitude": 76.6520,
            "severity": "High", "sentiment": "Urgent",
            "similarity_score": 67.5, "priority_score": 81, "priority_level": "Critical",
            "recommendation": "⚠️ DUPLICATE ALERT (67.5% match): Deploy Sanitation Taskforce immediately for bio-cleanup at Agrahara Health Center.",
            "status": "Pending", "hours_ago": 5,
            "escalation_level": "Level 1: Local Authority",
        },
        {
            "name": "Pooja Hegde",
            "title": "Faded Zebra Crossing Paint outside School",
            "description": "Pedestrian crosswalk lines completely faded. Vehicles do not slow down for school children crossing.",
            "category": "Road",
            "location": "Demonstration School Road",
            "latitude": 12.3075, "longitude": 76.6450,
            "severity": "Low", "sentiment": "Neutral",
            "similarity_score": 0.0, "priority_score": 35, "priority_level": "Low",
            "recommendation": "Log thermoplastic reflective road repainting task for Demonstration School Road.",
            "status": "Resolved", "hours_ago": 120, "resolved_hours_ago": 90,
            "resolution_photo": "https://images.unsplash.com/photo-1590674899484-d5640e854abe?auto=format&fit=crop&w=600&q=80",
            "resolution_note": "Repainted high-visibility reflective thermoplastic crosswalk lines outside school gate.",
            "resolved_by": "PWD Painting Squad #4",
            "escalation_level": "Level 1: Local Authority",
        },
    ]

    docs = []
    for idx, item in enumerate(seed_data, start=1):
        hrs = item.pop("hours_ago")
        resolved_hrs = item.pop("resolved_hours_ago", None)

        created_dt  = now - timedelta(hours=hrs)
        deadline_dt = created_dt + timedelta(hours=48)
        resolved_dt = (now - timedelta(hours=resolved_hrs)) if resolved_hrs is not None else None
        escalated_dt = deadline_dt if (now > deadline_dt and item.get("status") in ("OVERDUE", "ESCALATED")) else None

        doc = {
            "id": idx,
            **item,
            "created_at":  created_dt,
            "deadline_at": deadline_dt,
            "resolved_at": resolved_dt,
            "escalated_at": escalated_dt,
            "resolution_photo": item.get("resolution_photo"),
            "resolution_note": item.get("resolution_note"),
            "resolved_by": item.get("resolved_by"),
        }
        docs.append(doc)

    col.insert_many(docs)

    # Advance the counter past the last seeded id
    db["counters"].update_one(
        {"_id": "complaint_id"},
        {"$set": {"seq": len(docs)}},
        upsert=True,
    )

    print(f"✅ Successfully seeded {len(docs)} complaints into MongoDB Atlas!")


if __name__ == "__main__":
    seed_database()
