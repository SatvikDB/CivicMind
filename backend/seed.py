"""
Seed the MongoDB 'civicmind' database with 30 realistic civic complaints.

Covers:
  - All 6 categories: Road, Water, Waste, Streetlight, Drainage, Safety
  - All statuses: Pending, In Progress, Resolved, OVERDUE
  - All priority levels: Critical, High, Medium, Low
  - Duplicate clusters (same issue reported by multiple citizens)
  - Auto-escalation levels (Level 1 / 2 / 3)
  - 5 resolved complaints with resolution notes
  - Realistic Indian city geography (Mysuru, Karnataka)

LOCAL IMAGES (optional):
  Drop JPEG/PNG files into  backend/seed_images/  matching the filenames
  listed under 'resolution_photo' below.  Missing files are silently skipped.

Run:
  cd backend && source venv/bin/activate && python3 seed.py
"""

import os
import base64
from datetime import datetime, timedelta
from database import get_complaints_collection, db

SEED_IMAGES_DIR = os.path.join(os.path.dirname(__file__), "seed_images")


def _load_image(filename: str | None) -> str | None:
    """Return a Base64 data-URI for a local image, or None if not found."""
    if not filename:
        return None
    path = os.path.join(SEED_IMAGES_DIR, filename)
    if not os.path.exists(path):
        return None
    ext = os.path.splitext(filename)[1].lower().lstrip(".")
    mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg",
            "png": "image/png", "webp": "image/webp"}.get(ext, "image/jpeg")
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    print(f"   📷 Loaded image: {filename}")
    return f"data:{mime};base64,{b64}"


# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------
# Each entry uses relative time via 'hours_ago' / 'resolved_hours_ago' so the
# SLA countdown and escalation logic stays realistic whenever you re-seed.
#
# Fields NOT listed here are derived in build_doc():
#   created_at, deadline_at, resolved_at, escalated_at
# ---------------------------------------------------------------------------

SEED_DATA = [

    # ── ROAD ────────────────────────────────────────────────────────────────

    {   # 1 — Critical pothole, duplicate cluster A (matches #2)
        "name": "Aarav Sharma",
        "title": "Massive Pothole near College Gate 2",
        "description": "A deep crater-like pothole has formed right at the main entrance gate. Two two-wheelers skidded yesterday. Urgent asphalt repair required immediately!",
        "category": "Road", "location": "Main Campus Road, Ward 12",
        "latitude": 12.3124, "longitude": 76.6512,
        "severity": "Critical", "sentiment": "Urgent",
        "similarity_score": 85.5, "priority_score": 95, "priority_level": "Critical",
        "recommendation": "⚠️ DUPLICATE ALERT (85.5% match): Dispatch PWD Emergency Asphalt Crew within 6h to repair severe road hazard at Main Campus Road, Ward 12.",
        "status": "In Progress", "hours_ago": 8,
        "escalation_level": "Level 1: Local Authority",
        "complaint_photo": "complaint_road_pothole.jpg",
    },
    {   # 2 — Duplicate of #1
        "name": "Priya Nair",
        "title": "Large crater blocking traffic near college entrance",
        "description": "The pothole near Gate 2 has grown overnight. Buses are diverting. Bikes are falling. This road is completely destroyed during peak hours!",
        "category": "Road", "location": "College Gate 2 Avenue, Ward 12",
        "latitude": 12.3130, "longitude": 76.6518,
        "severity": "High", "sentiment": "Urgent",
        "similarity_score": 88.2, "priority_score": 91, "priority_level": "Critical",
        "recommendation": "⚠️ DUPLICATE ALERT (88.2% match): Merge with existing ticket #1. Combined community urgency — escalate to Ward Officer.",
        "status": "Pending", "hours_ago": 5,
        "escalation_level": "Level 1: Local Authority",
        "complaint_photo": "complaint_road_pothole.jpg",
    },
    {   # 3 — High, pending
        "name": "Sneha Kulkarni",
        "title": "Damaged Speed Breaker with Protruding Iron Rebar",
        "description": "The rubber speed breaker on Hunsur Road junction has worn down completely, exposing sharp iron rebar spikes that have punctured multiple car and bike tires this week.",
        "category": "Road", "location": "Hunsur Road Junction, Ward 8",
        "latitude": 12.3110, "longitude": 76.6310,
        "severity": "High", "sentiment": "Negative",
        "similarity_score": 20.0, "priority_score": 76, "priority_level": "High",
        "recommendation": "Schedule Ward Road Maintenance Unit to cut exposed rebar and re-lay rubberized speed breaker at Hunsur Road Junction within 24h.",
        "status": "Pending", "hours_ago": 18,
        "escalation_level": "Level 1: Local Authority",
        "complaint_photo": "complaint_road_pothole.jpg",
    },
    {   # 4 — Low, resolved
        "name": "Pooja Hegde",
        "title": "Faded Zebra Crossing Paint outside Primary School",
        "description": "The pedestrian crosswalk markings outside Demonstration School are completely faded. Vehicles are not stopping for children during school hours.",
        "category": "Road", "location": "Demonstration School Road, Ward 5",
        "latitude": 12.3075, "longitude": 76.6450,
        "severity": "Low", "sentiment": "Neutral",
        "similarity_score": 0.0, "priority_score": 35, "priority_level": "Low",
        "recommendation": "Schedule thermoplastic reflective road repainting for Demonstration School Road in next weekly maintenance run.",
        "status": "Resolved", "hours_ago": 120, "resolved_hours_ago": 90,
        "complaint_photo": "complaint_road_pothole.jpg",
        "resolution_photo": "zebra_crossing.jpg",
        "resolution_note": "PWD Squad #4 repainted high-visibility reflective thermoplastic crosswalk markings outside school gate. Paint fully cured and clearly visible.",
        "resolved_by": "PWD Painting Squad #4",
        "escalation_level": "Level 1: Local Authority",
    },
    {   # 5 — Medium, pending
        "name": "Rohan Desai",
        "title": "Road Surface Crumbling on Main Market Street",
        "description": "The asphalt on the main bazaar road has started crumbling near the vegetable market. Small loose stones are causing skidding, especially for two-wheelers carrying loads.",
        "category": "Road", "location": "Devaraja Market Main Road, Ward 3",
        "latitude": 12.3050, "longitude": 76.6560,
        "severity": "Medium", "sentiment": "Negative",
        "similarity_score": 14.0, "priority_score": 50, "priority_level": "Medium",
        "recommendation": "Log surface asphalt repair for Devaraja Market Main Road in the weekly PWD maintenance queue.",
        "status": "Pending", "hours_ago": 30,
        "escalation_level": "Level 1: Local Authority",
        "complaint_photo": "complaint_road_pothole.jpg",
    },

    # ── WATER ───────────────────────────────────────────────────────────────

    {   # 6 — Critical, overdue, escalated L2
        "name": "Kavitha Reddy",
        "title": "Contaminated Drinking Water with Foul Smell",
        "description": "The municipal tap water in our block has turned muddy brown with a strong chemical odor. Multiple families have complained of stomach issues. The entire Gokulam 3rd Stage is affected!",
        "category": "Water", "location": "Gokulam 3rd Stage, Ward 6",
        "latitude": 12.3245, "longitude": 76.6321,
        "severity": "Critical", "sentiment": "Urgent",
        "similarity_score": 12.0, "priority_score": 96, "priority_level": "Critical",
        "recommendation": "ALERT WATER BOARD IMMEDIATELY: Shut off contaminated main line & dispatch repair squad with tanker within 4h to Gokulam 3rd Stage.",
        "status": "OVERDUE", "hours_ago": 56,
        "escalation_level": "Level 2: Department Officer",
        "complaint_photo": "complaint_water.jpg",
    },
    {   # 7 — High, resolved with photo
        "name": "Divya Prakash",
        "title": "Underground Water Pipeline Burst on Footpath",
        "description": "Main supply line burst under sidewalk on Jayalakshmipuram 1st Main. Clean drinking water has been gushing onto the road since 6 AM, wasting thousands of litres.",
        "category": "Water", "location": "Jayalakshmipuram 1st Main, Ward 9",
        "latitude": 12.3160, "longitude": 76.6350,
        "severity": "High", "sentiment": "Urgent",
        "similarity_score": 62.4, "priority_score": 78, "priority_level": "High",
        "recommendation": "⚠️ DUPLICATE ALERT (62.4% match): Deploy Water Supply Engineer to isolate and repair burst pipeline at Jayalakshmipuram 1st Main within 12h.",
        "status": "Resolved", "hours_ago": 52, "resolved_hours_ago": 20,
        "complaint_photo": "complaint_water.jpg",
        "resolution_photo": "water_fix.jpg",
        "resolution_note": "Replaced the damaged 4-inch PVC main valve joint and sealed the sidewalk paving. Water supply fully restored. No leakage detected on re-inspection.",
        "resolved_by": "Eng. Ramesh V (Water Board, Ward 9)",
        "escalation_level": "Level 1: Local Authority",
    },
    {   # 8 — Medium, in progress, duplicate of #6 cluster
        "name": "Lakshmi Prasad",
        "title": "Brown muddy water coming from taps",
        "description": "Our entire apartment block is receiving discoloured water that smells like sewage. Children cannot drink it. This has been going on for 2 days now.",
        "category": "Water", "location": "Gokulam 2nd Stage, Ward 6",
        "latitude": 12.3240, "longitude": 76.6315,
        "severity": "High", "sentiment": "Frustrated",
        "similarity_score": 74.5, "priority_score": 84, "priority_level": "Critical",
        "recommendation": "⚠️ DUPLICATE ALERT (74.5% match): Part of Gokulam contamination cluster. Coordinate with ticket #6 water board response team.",
        "status": "In Progress", "hours_ago": 42,
        "escalation_level": "Level 1: Local Authority",
        "complaint_photo": "complaint_water.jpg",
    },
    {   # 9 — Low, resolved
        "name": "Arun Prasad",
        "title": "Very Low Water Pressure in Apartment Complex",
        "description": "Water pressure has been extremely weak for 3 days. Overhead tanks on upper floors are not filling. Residents on 3rd floor are suffering.",
        "category": "Water", "location": "Kuvempunagar Block M, Ward 11",
        "latitude": 12.2850, "longitude": 76.6390,
        "severity": "Low", "sentiment": "Neutral",
        "similarity_score": 8.0, "priority_score": 30, "priority_level": "Low",
        "recommendation": "Schedule a booster pump and valve pressure audit at Kuvempunagar Block M sub-station.",
        "status": "Resolved", "hours_ago": 100, "resolved_hours_ago": 72,
        "complaint_photo": "complaint_water.jpg",
        "resolution_photo": "water_pressure.jpg",
        "resolution_note": "Adjusted booster pump settings at sub-station 3. Water head pressure restored to standard 2.5 bar. Confirmed adequate flow on all floors.",
        "resolved_by": "Tech. Sunil Kumar (Water Division)",
        "escalation_level": "Level 1: Local Authority",
    },
    {   # 10 — Medium, pending
        "name": "Girish Nayak",
        "title": "Water Meter Leaking Continuously",
        "description": "The municipal water meter connection outside my house has a slow but constant drip. It has been running for over a week and is damaging the road surface underneath.",
        "category": "Water", "location": "Vijayanagar 5th Cross, Ward 7",
        "latitude": 12.3280, "longitude": 76.6200,
        "severity": "Medium", "sentiment": "Negative",
        "similarity_score": 5.0, "priority_score": 48, "priority_level": "Medium",
        "recommendation": "Dispatch plumber for meter fitting replacement at Vijayanagar 5th Cross during next service run.",
        "status": "Pending", "hours_ago": 40,
        "escalation_level": "Level 1: Local Authority",
        "complaint_photo": "complaint_water.jpg",
    },

    # ── WASTE ───────────────────────────────────────────────────────────────

    {   # 11 — High, overdue, escalated L3
        "name": "Suresh Babu",
        "title": "Garbage Dumpster Overflowing for 4 Days",
        "description": "The community dustbin on KD Road has not been cleared for 4 days. Waste is spilling 10 metres in every direction, creating a terrible stench and attracting stray dogs and rats.",
        "category": "Waste", "location": "KD Road Commercial Hub, Ward 3",
        "latitude": 12.3180, "longitude": 76.6480,
        "severity": "High", "sentiment": "Frustrated",
        "similarity_score": 35.0, "priority_score": 75, "priority_level": "High",
        "recommendation": "Deploy Heavy Sanitation Truck to KD Road Commercial Hub immediately. Issue warning notice to private waste contractor for SLA breach.",
        "status": "OVERDUE", "hours_ago": 80,
        "escalation_level": "Level 3: Senior Authority",
        "complaint_photo": "complaint_waste.jpg",
    },
    {   # 12 — Critical, pending, near health facility
        "name": "Karthik Subramanian",
        "title": "Bio-waste Dumped Outside Government Health Centre",
        "description": "Medical carton boxes with used syringes and waste bandages have been dumped along the outer wall of the Primary Health Centre. This is a serious infection risk for patients.",
        "category": "Waste", "location": "Agrahara PHC Perimeter, Ward 4",
        "latitude": 12.2920, "longitude": 76.6520,
        "severity": "High", "sentiment": "Urgent",
        "similarity_score": 67.5, "priority_score": 87, "priority_level": "Critical",
        "recommendation": "⚠️ DUPLICATE ALERT (67.5% match): Deploy Bio-hazard Sanitation Taskforce with PPE to Agrahara PHC immediately. File report with Health Dept.",
        "status": "Pending", "hours_ago": 6,
        "escalation_level": "Level 1: Local Authority",
        "complaint_photo": "complaint_waste.jpg",
    },
    {   # 13 — Medium, pending
        "name": "Vikram Singh",
        "title": "Construction Debris Blocking Footpath",
        "description": "A private construction contractor has dumped 2 tonnes of broken concrete, sand bags, and iron rods on the pedestrian footpath on TK Layout 3rd Cross. No notice was given.",
        "category": "Waste", "location": "TK Layout 3rd Cross, Ward 10",
        "latitude": 12.2930, "longitude": 76.6340,
        "severity": "Medium", "sentiment": "Frustrated",
        "similarity_score": 18.0, "priority_score": 54, "priority_level": "Medium",
        "recommendation": "Issue municipal penalty notice to contractor and dispatch debris removal truck to TK Layout 3rd Cross within 24h.",
        "status": "Pending", "hours_ago": 22,
        "escalation_level": "Level 1: Local Authority",
        "complaint_photo": "complaint_waste.jpg",
    },
    {   # 14 — Low, in progress
        "name": "Usha Rani",
        "title": "Broken Glass and Plastic Waste near Children's Park",
        "description": "Broken glass bottles and plastic waste are scattered around the children's play area in the residential park. Kids are getting hurt. Weekend volunteers have partially cleaned but it needs official removal.",
        "category": "Waste", "location": "Vijayanagar Children's Park, Ward 7",
        "latitude": 12.3295, "longitude": 76.6188,
        "severity": "Medium", "sentiment": "Negative",
        "similarity_score": 10.0, "priority_score": 52, "priority_level": "Medium",
        "recommendation": "Schedule dedicated park waste collection and glass debris removal at Vijayanagar Children's Park.",
        "status": "In Progress", "hours_ago": 16,
        "escalation_level": "Level 1: Local Authority",
        "complaint_photo": "complaint_waste.jpg",
    },

    # ── STREETLIGHT ─────────────────────────────────────────────────────────

    {   # 15 — High, in progress, duplicate cluster B (matches #16)
        "name": "Ananya Hegde",
        "title": "8 Consecutive Streetlights Out near Lake Road",
        "description": "All 8 LED streetlights along the Kukkarahalli Lake perimeter road have been non-functional for 3 nights. Women walking home after college are at serious risk.",
        "category": "Streetlight", "location": "Kukkarahalli Lake Perimeter Road, Ward 5",
        "latitude": 12.3050, "longitude": 76.6380,
        "severity": "High", "sentiment": "Negative",
        "similarity_score": 72.0, "priority_score": 76, "priority_level": "High",
        "recommendation": "⚠️ DUPLICATE ALERT (72.0% match): Assign Municipal Electrical Tech to identify root cause of cluster failure on Kukkarahalli Lake Road. Inspect feeder panel.",
        "status": "In Progress", "hours_ago": 28,
        "escalation_level": "Level 1: Local Authority",
        "complaint_photo": "complaint_streetlight.jpg",
    },
    {   # 16 — Duplicate of #15
        "name": "Ravi Shankar",
        "title": "Complete darkness on lake road for 3 nights",
        "description": "The entire stretch from the lake gate to the 4th cross junction is pitch black at night. I almost had an accident yesterday. This is extremely unsafe.",
        "category": "Streetlight", "location": "Kukkarahalli Lake Road, Ward 5",
        "latitude": 12.3055, "longitude": 76.6375,
        "severity": "High", "sentiment": "Urgent",
        "similarity_score": 80.0, "priority_score": 82, "priority_level": "Critical",
        "recommendation": "⚠️ DUPLICATE ALERT (80.0% match): Second community report confirms lake road blackout. Escalate electrical crew dispatch — prioritise tonight.",
        "status": "Pending", "hours_ago": 10,
        "escalation_level": "Level 1: Local Authority",
        "complaint_photo": "complaint_streetlight.jpg",
    },
    {   # 17 — High, in progress
        "name": "Meera Joshi",
        "title": "Streetlight Pole Tilted 45° After Truck Collision",
        "description": "A delivery truck hit the streetlight pole outside our gate at midnight. The pole is now leaning dangerously toward the footpath. A falling pole could cause a fatal accident.",
        "category": "Streetlight", "location": "Vijayanagar 2nd Stage, Ward 7",
        "latitude": 12.3290, "longitude": 76.6190,
        "severity": "High", "sentiment": "Negative",
        "similarity_score": 45.0, "priority_score": 74, "priority_level": "High",
        "recommendation": "Assign Municipal Electrical Tech with hydraulic support equipment to secure and replace damaged streetlight pole at Vijayanagar 2nd Stage within 24h.",
        "status": "In Progress", "hours_ago": 32,
        "escalation_level": "Level 1: Local Authority",
        "complaint_photo": "complaint_streetlight.jpg",
    },
    {   # 18 — Low, pending
        "name": "Chandan Kumar",
        "title": "Flickering Streetlight Causing Nuisance",
        "description": "The streetlight outside house #45 has been flickering continuously for 2 weeks. The rapid on-off blinking is causing discomfort and headaches to residents.",
        "category": "Streetlight", "location": "Saraswathipuram 7th Cross, Ward 2",
        "latitude": 12.3095, "longitude": 76.6425,
        "severity": "Low", "sentiment": "Neutral",
        "similarity_score": 0.0, "priority_score": 28, "priority_level": "Low",
        "recommendation": "Queue LED driver replacement for Saraswathipuram 7th Cross in next monthly electrical maintenance schedule.",
        "status": "Pending", "hours_ago": 200,
        "escalation_level": "Level 1: Local Authority",
        "complaint_photo": "complaint_streetlight.jpg",
    },

    # ── DRAINAGE ────────────────────────────────────────────────────────────

    {   # 19 — Critical, pending
        "name": "Mohammed Zaid",
        "title": "Open Manhole on Busy Footpath — Fall Risk",
        "description": "The concrete slab over the manhole near RTO Circle bus stop has collapsed into pieces, leaving a 4-foot open pit directly on the pedestrian walkway. A child nearly fell in last night.",
        "category": "Drainage", "location": "RTO Circle Bus Stop Footpath, Ward 1",
        "latitude": 12.2990, "longitude": 76.6550,
        "severity": "Critical", "sentiment": "Urgent",
        "similarity_score": 0.0, "priority_score": 96, "priority_level": "Critical",
        "recommendation": "URGENT DRAINAGE TEAM: Cordon area immediately and deploy crew to install temporary cover and permanent manhole slab at RTO Circle Bus Stop.",
        "status": "Pending", "hours_ago": 14,
        "escalation_level": "Level 1: Local Authority",
        "complaint_photo": "complaint_drainage.jpg",
    },
    {   # 20 — Critical, in progress, duplicate cluster C (matches #21)
        "name": "Nandini Gowda",
        "title": "Sewage Backflow Flooding Residential Street",
        "description": "The main sewer line on Boghadi Ring Road has blocked completely. Foul black sewage water is overflowing from all manhole chambers and flooding into house compound gates. Unbearable smell.",
        "category": "Drainage", "location": "Boghadi Ring Road Junction, Ward 14",
        "latitude": 12.2980, "longitude": 76.6120,
        "severity": "Critical", "sentiment": "Urgent",
        "similarity_score": 78.0, "priority_score": 93, "priority_level": "Critical",
        "recommendation": "⚠️ DUPLICATE ALERT (78.0% match): Deploy suction tanker and high-pressure jetting machine to unblock main sewer line at Boghadi Ring Road Junction immediately.",
        "status": "In Progress", "hours_ago": 12,
        "escalation_level": "Level 1: Local Authority",
        "complaint_photo": "complaint_drainage.jpg",
    },
    {   # 21 — Duplicate of #20
        "name": "Harish Babu",
        "title": "Sewer water overflowing into homes — Boghadi",
        "description": "Sewage is flowing into 6 houses on our street. The smell is nauseating. Old people and children are being evacuated. Nobody has responded to our calls to the ward office!",
        "category": "Drainage", "location": "Boghadi 2nd Cross, Ward 14",
        "latitude": 12.2975, "longitude": 76.6115,
        "severity": "Critical", "sentiment": "Frustrated",
        "similarity_score": 82.0, "priority_score": 94, "priority_level": "Critical",
        "recommendation": "⚠️ DUPLICATE ALERT (82.0% match): Third complaint on Boghadi sewer cluster. Immediate senior officer escalation required.",
        "status": "Pending", "hours_ago": 8,
        "escalation_level": "Level 1: Local Authority",
        "complaint_photo": "complaint_drainage.jpg",
    },
    {   # 22 — Medium, in progress
        "name": "Manjunath Rao",
        "title": "Storm Drain Blocked — Stagnant Water Breeding Mosquitoes",
        "description": "The stormwater drain on Hebbal Industrial Area Block B is blocked with plastic bags and mud. Water has been stagnant for over 10 days. There is a serious dengue and malaria risk.",
        "category": "Drainage", "location": "Hebbal Industrial Area Block B, Ward 13",
        "latitude": 12.3410, "longitude": 76.6210,
        "severity": "Medium", "sentiment": "Frustrated",
        "similarity_score": 22.0, "priority_score": 58, "priority_level": "Medium",
        "recommendation": "Dispatch Stormwater Drain Crew with desilting machine to Hebbal Industrial Area Block B. Spray anti-larval chemicals after clearing.",
        "status": "In Progress", "hours_ago": 38,
        "escalation_level": "Level 1: Local Authority",
        "complaint_photo": "complaint_drainage.jpg",
    },
    {   # 23 — Low, pending
        "name": "Savitha M",
        "title": "Drain Cover Broken — Mild Water Seepage",
        "description": "A plastic drain grille near the bus stand has cracked and water seeps onto the footpath during rain. Not critical but causes slippery surface for elderly.",
        "category": "Drainage", "location": "City Bus Stand Approach Road, Ward 1",
        "latitude": 12.3020, "longitude": 76.6540,
        "severity": "Low", "sentiment": "Neutral",
        "similarity_score": 3.0, "priority_score": 25, "priority_level": "Low",
        "recommendation": "Replace cracked drain grille at City Bus Stand Approach Road during next scheduled maintenance visit.",
        "status": "Pending", "hours_ago": 72,
        "escalation_level": "Level 1: Local Authority",
        "complaint_photo": "complaint_drainage.jpg",
    },

    # ── SAFETY ──────────────────────────────────────────────────────────────

    {   # 24 — Critical, overdue, escalated L2
        "name": "Rajesh Kumar",
        "title": "High Voltage Live Wire Hanging Near School Playground",
        "description": "A high-voltage electrical wire snapped from the pole and is hanging 2 metres above the ground near the primary school playground! Children are at extreme risk of electrocution. This is an emergency!!",
        "category": "Safety", "location": "Saraswathipuram 4th Main near MHPS, Ward 2",
        "latitude": 12.3089, "longitude": 76.6432,
        "severity": "Critical", "sentiment": "Urgent",
        "similarity_score": 0.0, "priority_score": 99, "priority_level": "Critical",
        "recommendation": "EMERGENCY ELECTRIC: Dispatch BESCOM Lineman squad immediately. Cordon school area. Restore insulated power line at Saraswathipuram 4th Main.",
        "status": "OVERDUE", "hours_ago": 58,
        "escalation_level": "Level 2: Department Officer",
        "complaint_photo": "complaint_safety.jpg",
    },
    {   # 25 — High, resolved with photo
        "name": "Deepak Mehta",
        "title": "Traffic Signal Malfunction — Simultaneous Red & Green",
        "description": "Both red and green lights at Metropole Circle Junction are flashing at the same time. Vehicles are confused, leading to near-miss collisions. Traffic constable needed urgently.",
        "category": "Safety", "location": "Metropole Circle Junction, Ward 1",
        "latitude": 12.3030, "longitude": 76.6470,
        "severity": "High", "sentiment": "Urgent",
        "similarity_score": 5.0, "priority_score": 79, "priority_level": "High",
        "recommendation": "Notify Traffic Control Division & BESCOM to jointly fix malfunctioning signal controller at Metropole Circle Junction within 6h.",
        "status": "Resolved", "hours_ago": 64, "resolved_hours_ago": 40,
        "complaint_photo": "complaint_safety.jpg",
        "resolution_photo": "traffic_signal.jpg",
        "resolution_note": "BESCOM technicians replaced the shorted traffic signal controller PCB. Signal re-synchronised with the central traffic management system. No further issues reported.",
        "resolved_by": "Sr. Officer K. Swamy (Traffic Signals Division)",
        "escalation_level": "Level 1: Local Authority",
    },
    {   # 26 — Medium, in progress
        "name": "Siddharth Rao",
        "title": "Large Tree Branch Fallen — Partially Blocking Lane",
        "description": "Strong winds last night broke a major Gulmohar tree branch on Vontikoppal Temple Road. It is resting on a power line and blocking one vehicle lane. Heavy vehicles cannot pass.",
        "category": "Safety", "location": "Vontikoppal Temple Road, Ward 8",
        "latitude": 12.3210, "longitude": 76.6410,
        "severity": "Medium", "sentiment": "Neutral",
        "similarity_score": 10.0, "priority_score": 52, "priority_level": "Medium",
        "recommendation": "Dispatch Parks & Forestry clearance team with chainsaw and crane to Vontikoppal Temple Road. Inspect power line for damage.",
        "status": "In Progress", "hours_ago": 20,
        "escalation_level": "Level 1: Local Authority",
        "complaint_photo": "complaint_safety.jpg",
    },
    {   # 27 — High, pending
        "name": "Pavithra S",
        "title": "Stray Dog Pack Attacking Pedestrians",
        "description": "A pack of 12+ aggressive stray dogs has been attacking pedestrians and cyclists near the school on Hebbal Road every morning. Three children have been bitten this week. Anti-rabies shots were administered but the threat remains.",
        "category": "Safety", "location": "Hebbal Road near Kendriya Vidyalaya, Ward 13",
        "latitude": 12.3405, "longitude": 76.6200,
        "severity": "High", "sentiment": "Urgent",
        "similarity_score": 0.0, "priority_score": 82, "priority_level": "Critical",
        "recommendation": "Dispatch Animal Husbandry Department dog-catching team to Hebbal Road. Conduct ABC (Animal Birth Control) programme. Alert school authorities.",
        "status": "Pending", "hours_ago": 10,
        "escalation_level": "Level 1: Local Authority",
        "complaint_photo": "complaint_safety.jpg",
    },
    {   # 28 — Medium, pending
        "name": "Pradeep Nair",
        "title": "No CCTV Coverage in Dark Lane — Harassment Incidents",
        "description": "The narrow lane behind the railway station has no street lighting and no CCTV. There have been 3 chain-snatching incidents in 2 weeks. Residents are afraid to walk after 7 PM.",
        "category": "Safety", "location": "Railway Station Back Lane, Ward 1",
        "latitude": 12.3015, "longitude": 76.6560,
        "severity": "Medium", "sentiment": "Frustrated",
        "similarity_score": 30.0, "priority_score": 60, "priority_level": "Medium",
        "recommendation": "Coordinate with Traffic Police to install 2 PTZ CCTV cameras and 3 new LED streetlights at Railway Station Back Lane. Increase police patrol frequency.",
        "status": "Pending", "hours_ago": 48,
        "escalation_level": "Level 1: Local Authority",
        "complaint_photo": "complaint_safety.jpg",
    },

    # ── ADDITIONAL VARIETY ──────────────────────────────────────────────────

    {   # 29 — High, overdue — water
        "name": "Bhavana Iyengar",
        "title": "No Water Supply for 3 Consecutive Days",
        "description": "Our entire ward has received zero water supply for 3 days. Water tankers sent by the corporation are insufficient. Families are buying water at high cost. Nobody from the ward office is responding.",
        "category": "Water", "location": "Srirampura 2nd Stage, Ward 15",
        "latitude": 12.3350, "longitude": 76.6440,
        "severity": "High", "sentiment": "Frustrated",
        "similarity_score": 40.0, "priority_score": 80, "priority_level": "High",
        "recommendation": "⚠️ DUPLICATE ALERT (40.0% match): Coordinate emergency tanker deployment to Srirampura 2nd Stage. Investigate main supply valve failure.",
        "status": "OVERDUE", "hours_ago": 74,
        "escalation_level": "Level 2: Department Officer",
        "complaint_photo": "complaint_water.jpg",
    },
    {   # 30 — High, pending — road
        "name": "Tejesh Murthy",
        "title": "Broken Road Divider Blocking Night Traffic",
        "description": "A concrete road divider on the outer ring road has been knocked down and is lying across the left lane. At night vehicles are running over it at speed. Someone will get killed.",
        "category": "Road", "location": "Outer Ring Road near Hebbal Flyover, Ward 13",
        "latitude": 12.3420, "longitude": 76.6215,
        "severity": "High", "sentiment": "Urgent",
        "similarity_score": 8.0, "priority_score": 77, "priority_level": "High",
        "recommendation": "Dispatch PWD Emergency Crew to remove fallen divider from carriageway and install reflective cones at Outer Ring Road near Hebbal Flyover. Repair within 24h.",
        "status": "Pending", "hours_ago": 9,
        "escalation_level": "Level 1: Local Authority",
        "complaint_photo": "complaint_road_pothole.jpg",
    },
]


def build_doc(idx: int, item: dict, now: datetime) -> dict:
    """Construct the full MongoDB document from a seed entry."""
    data = dict(item)
    hrs          = data.pop("hours_ago")
    resolved_hrs = data.pop("resolved_hours_ago", None)
    res_photo    = data.pop("resolution_photo", None)
    res_note     = data.pop("resolution_note", None)
    res_by       = data.pop("resolved_by", None)
    comp_photo   = data.pop("complaint_photo", None)

    created_dt  = now - timedelta(hours=hrs)
    deadline_dt = created_dt + timedelta(hours=48)
    resolved_dt = (now - timedelta(hours=resolved_hrs)) if resolved_hrs is not None else None

    # Set escalated_at to when the deadline was first breached for overdue items
    overdue = data.get("status") in ("OVERDUE",) and now > deadline_dt
    escalated_dt = deadline_dt if overdue else None

    return {
        "id":               idx,
        **data,
        "created_at":       created_dt,
        "deadline_at":      deadline_dt,
        "resolved_at":      resolved_dt,
        "escalated_at":     escalated_dt,
        "complaint_photo":  _load_image(comp_photo),
        "resolution_photo": _load_image(res_photo),
        "resolution_note":  res_note,
        "resolved_by":      res_by,
    }


def seed_database():
    col = get_complaints_collection()

    print("🗑️  Dropping existing complaints and counters...")
    col.drop()
    db["counters"].drop()
    db["counters"].insert_one({"_id": "complaint_id", "seq": 0})

    now  = datetime.utcnow()
    docs = [build_doc(idx, item, now) for idx, item in enumerate(SEED_DATA, start=1)]

    col.insert_many(docs)

    db["counters"].update_one(
        {"_id": "complaint_id"},
        {"$set": {"seq": len(docs)}},
        upsert=True,
    )

    # ── Summary ──────────────────────────────────────────────────────────────
    from collections import Counter
    statuses    = Counter(d["status"] for d in docs)
    categories  = Counter(d["category"] for d in docs)
    priorities  = Counter(d["priority_level"] for d in docs)
    images      = sum(1 for d in docs if d.get("resolution_photo"))
    comp_images = sum(1 for d in docs if d.get("complaint_photo"))
    duplicates  = sum(1 for d in docs if d.get("similarity_score", 0) >= 50.0)

    print(f"\n✅ Seeded {len(docs)} complaints into MongoDB Atlas (civicmind db)\n")
    print("📊 By Status:   ", dict(statuses))
    print("📂 By Category: ", dict(categories))
    print("🔺 By Priority: ", dict(priorities))
    print(f"🔁 Duplicates (≥50% match): {duplicates}")
    print(f"📷 Complaint photos (citizen): {comp_images}")
    print(f"✅ Resolution photos (authority): {images}")
    print("\nDone! Start the backend with:  uvicorn main:app --reload")


if __name__ == "__main__":
    seed_database()
