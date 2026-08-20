# Person 6 -- Recommendation Engine
# Generates actionable resolution recommendations, officer assignments, SLAs, dispatch triggers and citizen guidance.

import logging
from typing import Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Data Structures
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class Recommendation:
    """Full recommendation output for a complaint."""
    category: str
    severity: str
    priority_level: str

    action_title: str
    action_steps: list

    department: str
    target_officer: str
    department_contact_hint: str

    sla_hours: int
    sla_label: str
    deadline: str
    dispatch_immediate_field_team: bool

    escalation_required: bool
    escalation_path: list

    citizen_tips: list
    tags: list
    cost_tier: str = "Medium"  # "Low" | "Medium" | "High"
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ──────────────────────────────────────────────────────────────────────────────
# Knowledge Base (30+ Category x Severity Rules)
# ──────────────────────────────────────────────────────────────────────────────

RECOMMENDATION_RULES = {
    # ── Road ──────────────────────────────────────────────────────────────────
    ("Road", "Critical"): {
        "action_title": "Emergency Road Barricading & Immediate Repair",
        "action_steps": [
            "Immediately dispatch road safety team to barricade the hazard.",
            "Place high-visibility warning signs and cones within 1 hour.",
            "Alert traffic police to divert vehicles from the area.",
            "Schedule emergency cold-mix asphalt repair within 24 hours.",
            "Document damage with geotagged photos for contractor accountability.",
            "Issue public traffic advisory via municipal portal.",
        ],
        "department": "Public Works Department (PWD)",
        "target_officer": "Executive Engineer (Road Infrastructure)",
        "sla_hours": 24,
        "dispatch_immediate_field_team": True,
        "cost_tier": "High",
        "tags": ["emergency", "road-safety", "barricade", "pwd"],
    },
    ("Road", "High"): {
        "action_title": "Priority Road Inspection & Repair Scheduling",
        "action_steps": [
            "Inspect the reported location within 48 hours.",
            "Assess repair scope and assign empanelled contractor.",
            "Place reflective warning markers at the site.",
            "Schedule road resurfacing work within 7 days.",
            "Conduct post-repair quality verification inspection.",
        ],
        "department": "Public Works Department (PWD)",
        "target_officer": "Assistant Engineer (Ward Maintenance)",
        "sla_hours": 168,
        "dispatch_immediate_field_team": False,
        "cost_tier": "Medium",
        "tags": ["road-repair", "inspection", "pwd"],
    },
    ("Road", "Medium"): {
        "action_title": "Road Maintenance & Scheduled Patchwork",
        "action_steps": [
            "Log complaint and add to the zonal road maintenance schedule.",
            "Visual inspection by local ward supervisor within 5 days.",
            "Include in next maintenance batch (within 15 days).",
            "Notify complainant of scheduled repair timeline.",
        ],
        "department": "Municipal Road Maintenance Wing",
        "target_officer": "Ward Junior Engineer",
        "sla_hours": 360,
        "dispatch_immediate_field_team": False,
        "cost_tier": "Low",
        "tags": ["road-maintenance", "scheduled-repair"],
    },
    ("Road", "Low"): {
        "action_title": "Routine Road Assessment & Maintenance",
        "action_steps": [
            "Add to routine road maintenance master list.",
            "Address during next scheduled ward maintenance cycle.",
            "Update complaint status once actioned.",
        ],
        "department": "Municipal Road Maintenance Wing",
        "target_officer": "Ward Inspector",
        "sla_hours": 720,
        "dispatch_immediate_field_team": False,
        "cost_tier": "Low",
        "tags": ["routine-maintenance"],
    },

    # ── Water ─────────────────────────────────────────────────────────────────
    ("Water", "Critical"): {
        "action_title": "Emergency Water Supply & Pipeline Repair",
        "action_steps": [
            "Dispatch emergency plumbing team immediately.",
            "Shut off main feeder valve to prevent flooding and road erosion.",
            "Arrange emergency water tanker supply for affected households.",
            "Excavate and repair burst pipeline within 12 hours.",
            "Conduct chemical and biological water quality test post-repair.",
            "Issue contamination advisory and notify residents upon restoration.",
        ],
        "department": "Water Works / Jal Board",
        "target_officer": "Zonal Water Works Engineer",
        "sla_hours": 12,
        "dispatch_immediate_field_team": True,
        "cost_tier": "High",
        "tags": ["emergency", "water-supply", "pipeline-repair", "jal-board"],
    },
    ("Water", "High"): {
        "action_title": "Priority Pipeline Inspection & Contamination Control",
        "action_steps": [
            "Inspect pipeline and isolate leak source within 24 hours.",
            "Execute repair within 3 days.",
            "Arrange interim tanker supply if residential supply is disrupted.",
            "Test water quality after pipe repair.",
        ],
        "department": "Water Works / Jal Board",
        "target_officer": "Assistant Engineer (Water Supply)",
        "sla_hours": 72,
        "dispatch_immediate_field_team": False,
        "cost_tier": "Medium",
        "tags": ["pipeline-repair", "water-shortage", "inspection"],
    },
    ("Water", "Medium"): {
        "action_title": "Water Infrastructure Check & Drain Clearing",
        "action_steps": [
            "Log and assign to local water supply maintenance crew.",
            "Site visit and pressure check within 5 days.",
            "Schedule cleaning/minor pipe replacement within 10 days.",
        ],
        "department": "Water Works / Jal Board",
        "target_officer": "Ward Plumbing Supervisor",
        "sla_hours": 240,
        "dispatch_immediate_field_team": False,
        "cost_tier": "Low",
        "tags": ["water-maintenance", "inspection"],
    },
    ("Water", "Low"): {
        "action_title": "Routine Water System Inspection",
        "action_steps": [
            "Add to water board routine survey list.",
            "Inspect valve and meter during regular beat cycle.",
        ],
        "department": "Water Works / Jal Board",
        "target_officer": "Meter Reader / Line Inspector",
        "sla_hours": 480,
        "dispatch_immediate_field_team": False,
        "cost_tier": "Low",
        "tags": ["routine-maintenance"],
    },

    # ── Electricity ───────────────────────────────────────────────────────────
    ("Electricity", "Critical"): {
        "action_title": "Emergency Electrical Hazard Mitigation",
        "action_steps": [
            "Immediately dispatch emergency lineman rapid response team.",
            "De-energise affected power feeder/transformer to prevent electrocution.",
            "Cordon off danger zone with warning tape.",
            "Replace faulty wiring / pole / transformer within 6 hours.",
            "Perform insulation and grounding safety tests before re-powering.",
            "Notify local emergency authorities.",
        ],
        "department": "Electricity Distribution Company (DISCOM)",
        "target_officer": "Sub-Divisional Officer (Electrical Safety)",
        "sla_hours": 6,
        "dispatch_immediate_field_team": True,
        "cost_tier": "Medium",
        "tags": ["emergency", "electrical-hazard", "discom", "life-safety"],
    },
    ("Electricity", "High"): {
        "action_title": "Priority Street Light / Power Restoration",
        "action_steps": [
            "Inspect reported location within 24 hours.",
            "Replace damaged cables/bulbs within 48 hours.",
            "Inspect local distribution box for load imbalance.",
            "Verify complete illumination/supply with photo proof.",
        ],
        "department": "Electricity Distribution Company (DISCOM)",
        "target_officer": "Junior Engineer (Distribution)",
        "sla_hours": 48,
        "dispatch_immediate_field_team": False,
        "cost_tier": "Low",
        "tags": ["street-light", "power-outage", "discom"],
    },
    ("Electricity", "Medium"): {
        "action_title": "Electrical Maintenance & Streetlight Repair",
        "action_steps": [
            "Log complaint and allocate to area maintenance crew.",
            "Perform day-time circuit inspection within 3 days.",
            "Complete repair within 7 days.",
        ],
        "department": "Electricity Distribution Company (DISCOM)",
        "target_officer": "Area Lineman Supervisor",
        "sla_hours": 168,
        "dispatch_immediate_field_team": False,
        "cost_tier": "Low",
        "tags": ["electrical-maintenance"],
    },

    # ── Garbage ───────────────────────────────────────────────────────────────
    ("Garbage", "Critical"): {
        "action_title": "Emergency Waste Clearance & Epidemic Prevention",
        "action_steps": [
            "Dispatch emergency sanitation compactor truck within 4 hours.",
            "Clear hazardous waste pile and disinfect area with bleaching powder.",
            "Alert health inspector to assess vector-borne disease risk.",
            "Issue strict penalty notice to commercial illegal dumpers.",
            "Install surveillance camera or warning signage.",
        ],
        "department": "Municipal Sanitation / Health Department",
        "target_officer": "Chief Sanitary Inspector",
        "sla_hours": 8,
        "dispatch_immediate_field_team": True,
        "cost_tier": "Medium",
        "tags": ["emergency-sanitation", "health-hazard", "illegal-dumping"],
    },
    ("Garbage", "High"): {
        "action_title": "Priority Garbage Collection & Sanitation Drive",
        "action_steps": [
            "Deploy secondary collection vehicle within 24 hours.",
            "Conduct thorough sweeping and washing of the spot.",
            "Increase daily collection frequency for the locality.",
            "Notify ward councillor on clearance status.",
        ],
        "department": "Municipal Sanitation Department",
        "target_officer": "Ward Sanitation Officer",
        "sla_hours": 24,
        "dispatch_immediate_field_team": False,
        "cost_tier": "Low",
        "tags": ["garbage-collection", "sanitation", "priority-cleanup"],
    },
    ("Garbage", "Medium"): {
        "action_title": "Scheduled Waste Collection & Bin Placement",
        "action_steps": [
            "Schedule additional waste collection run within 3 days.",
            "Evaluate placement of additional community dustbins.",
            "Organise ward-level cleanup drive.",
        ],
        "department": "Municipal Sanitation Department",
        "target_officer": "Sanitary Supervisor",
        "sla_hours": 72,
        "dispatch_immediate_field_team": False,
        "cost_tier": "Low",
        "tags": ["garbage-collection", "sanitation"],
    },

    # ── Safety ────────────────────────────────────────────────────────────────
    ("Safety", "Critical"): {
        "action_title": "EMERGENCY: Police & Civil Protection Mobilisation",
        "action_steps": [
            "Immediately notify local police station and PCR vans.",
            "Deploy security personnel/wardens to secure vulnerable area.",
            "Coordinate with emergency helpline (112) for rapid intervention.",
            "Install high-intensity mobile floodlights for dark spots.",
            "Initiate immediate CCTV footage review.",
            "Publish community safety advisory.",
        ],
        "department": "Local Police / Municipal Safety Cell",
        "target_officer": "Station House Officer (SHO) / Municipal Security Officer",
        "sla_hours": 2,
        "dispatch_immediate_field_team": True,
        "cost_tier": "High",
        "tags": ["emergency", "police", "life-safety", "crime-prevention"],
    },
    ("Safety", "High"): {
        "action_title": "Hazard Removal & Safety Inspection",
        "action_steps": [
            "Dispatch safety inspection team within 24 hours.",
            "Barricade dangerous structures or open pits.",
            "Repair or install functional lighting in poorly lit passages.",
            "Increase police night patrolling frequency.",
        ],
        "department": "Municipal Safety / Public Works / Police",
        "target_officer": "Assistant Commissioner of Police / Safety Inspector",
        "sla_hours": 48,
        "dispatch_immediate_field_team": False,
        "cost_tier": "Medium",
        "tags": ["safety-inspection", "hazard-removal", "security"],
    },

    # ── Default Fallback ──────────────────────────────────────────────────────
    ("ANY", "ANY"): {
        "action_title": "General Civic Complaint Review & Action",
        "action_steps": [
            "Acknowledge complaint and log into municipal ticketing system.",
            "Assign to appropriate zonal officer for field assessment.",
            "Contact complainant for verification if required.",
            "Execute necessary corrective maintenance.",
            "Update complaint status and record citizen feedback.",
        ],
        "department": "Ward Office / Municipal Corporation",
        "target_officer": "Ward Grievance Officer",
        "sla_hours": 240,
        "dispatch_immediate_field_team": False,
        "cost_tier": "Low",
        "tags": ["general-complaint"],
    },
}

DEPARTMENT_CONTACTS = {
    "Public Works Department (PWD)":              "PWD Helpline: 1800-111-793 | www.pwd.gov.in",
    "Water Works / Jal Board":                    "Jal Board Helpline: 1916 | www.jalboard.gov.in",
    "Electricity Distribution Company (DISCOM)":  "DISCOM Emergency: 19100 | www.discom.gov.in",
    "Municipal Sanitation Department":            "Sanitation Helpline: 1533 | Municipal App",
    "Municipal Sanitation / Health Department":   "Public Health Cell: 104 | www.health.gov.in",
    "Local Police / Municipal Safety Cell":       "Police Control Room: 100 | Emergency: 112",
    "Municipal Safety / Public Works / Police":   "Emergency: 112 | PWD: 1800-111-793",
    "Ward Office / Municipal Corporation":        "Citizen Helpdesk: 1533 | Ward Office",
}

CITIZEN_TIPS = {
    "Road":         ["Attach clear geotagged photos of road defects to speed up contractor assignment.",
                     "Specify exact landmarks or kilometer stones if available.",
                     "Alert co-commuters by marking dangerous craters safely if possible."],
    "Water":        ["Store emergency water safely while maintenance is underway.",
                     "Request an emergency municipal water tanker on helpline 1916.",
                     "Boil drinking water if contamination or discoloration is noticed."],
    "Electricity":  ["Stay at least 15 feet away from fallen or dangling electric wires.",
                     "Call DISCOM emergency line immediately to report sparking.",
                     "Unplug sensitive home appliances during voltage surges."],
    "Garbage":      ["Segregate dry, wet, and medical/sanitary waste before disposal.",
                     "Report repeated commercial violators directly to the Sanitary Inspector.",
                     "Keep neighborhood dustbin lids closed to prevent vector breeding."],
    "Safety":       ["Dial 112 immediately in case of active danger or suspicious activity.",
                     "Avoid traveling alone through unlit stretches until repaired.",
                     "Share complaint ticket number with neighborhood welfare association."],
}

ESCALATION_PATHS = {
    "CRITICAL": [
        "1. Ward Executive Officer",
        "2. Zonal Additional Commissioner",
        "3. Municipal Commissioner",
        "4. District Magistrate / Collector",
        "5. State Grievance Cell (CM Helpline 1076)"
    ],
    "HIGH": [
        "1. Ward Junior Engineer / Inspector",
        "2. Assistant Executive Engineer",
        "3. Zonal Commissioner",
    ],
    "MEDIUM": [
        "1. Ward Junior Engineer",
        "2. Zonal Officer",
    ],
    "LOW": [
        "1. Ward Office Helpdesk",
    ],
}


# ──────────────────────────────────────────────────────────────────────────────
# Main Recommendation Engine Facade
# ──────────────────────────────────────────────────────────────────────────────

class RecommendationEngine:
    def __init__(self):
        self._rules = RECOMMENDATION_RULES
        self._contacts = DEPARTMENT_CONTACTS
        self._citizen_tips = CITIZEN_TIPS
        self._escalation = ESCALATION_PATHS
        logger.info("RecommendationEngine initialised")

    def recommend(
        self,
        category: Optional[str],
        severity: Optional[str],
        priority_level: str = "MEDIUM"
    ) -> Recommendation:
        cat_key = str(category).title() if category else "Other"
        sev_key = str(severity).title() if severity else "Medium"
        prio_key = str(priority_level).upper() if priority_level else "MEDIUM"

        rule = (
            self._rules.get((cat_key, sev_key))
            or self._rules.get((cat_key, "High"))
            or self._rules.get((cat_key, "Medium"))
            or self._rules.get(("ANY", "ANY"))
        )

        department = rule["department"]
        target_officer = rule.get("target_officer", "Ward Officer")
        contact = self._contacts.get(department, "Municipal Helpline: 1533")
        sla_hours = rule["sla_hours"]
        sla_label = self._sla_label(sla_hours)
        deadline = (datetime.now(timezone.utc) + timedelta(hours=sla_hours)).isoformat()
        dispatch_team = rule.get("dispatch_immediate_field_team", prio_key == "CRITICAL")
        cost_tier = rule.get("cost_tier", "Medium")

        escalation_required = prio_key in ("HIGH", "CRITICAL")
        escalation_path = self._escalation.get(prio_key, self._escalation["LOW"])

        tips = self._citizen_tips.get(cat_key, [
            "Attach photos to strengthen your complaint.",
            "Provide exact location landmarks.",
            "Keep contact number updated for follow-ups.",
        ])

        return Recommendation(
            category=cat_key,
            severity=sev_key,
            priority_level=prio_key,
            action_title=rule["action_title"],
            action_steps=rule["action_steps"],
            department=department,
            target_officer=target_officer,
            department_contact_hint=contact,
            sla_hours=sla_hours,
            sla_label=sla_label,
            deadline=deadline,
            dispatch_immediate_field_team=dispatch_team,
            escalation_required=escalation_required,
            escalation_path=escalation_path,
            citizen_tips=tips,
            cost_tier=cost_tier,
            tags=rule.get("tags", [])
        )

    def _sla_label(self, hours: int) -> str:
        if hours <= 6:
            return f"Within {hours} hours (EMERGENCY)"
        elif hours <= 24:
            return f"Within {hours} hours (Same Day)"
        elif hours <= 72:
            return f"Within {hours // 24} days (High Priority)"
        elif hours <= 168:
            return f"Within {hours // 24} days (Standard)"
        else:
            return f"Within {hours // 24} days (Routine)"

    def to_dict(self, rec: Recommendation) -> dict:
        return {
            "category": rec.category,
            "severity": rec.severity,
            "priority_level": rec.priority_level,
            "action_title": rec.action_title,
            "action_steps": rec.action_steps,
            "department": rec.department,
            "target_officer": rec.target_officer,
            "department_contact_hint": rec.department_contact_hint,
            "sla_hours": rec.sla_hours,
            "sla_label": rec.sla_label,
            "deadline": rec.deadline,
            "dispatch_immediate_field_team": rec.dispatch_immediate_field_team,
            "escalation_required": rec.escalation_required,
            "escalation_path": rec.escalation_path,
            "citizen_tips": rec.citizen_tips,
            "cost_tier": rec.cost_tier,
            "tags": rec.tags,
            "generated_at": rec.generated_at,
        }


# ──────────────────────────────────────────────────────────────────────────────
# Module Singleton
# ──────────────────────────────────────────────────────────────────────────────
_rec_instance: Optional[RecommendationEngine] = None

def get_recommendation_engine() -> RecommendationEngine:
    global _rec_instance
    if _rec_instance is None:
        _rec_instance = RecommendationEngine()
    return _rec_instance
