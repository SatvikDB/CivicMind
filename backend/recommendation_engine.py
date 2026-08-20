RECOMMENDATIONS = {
    ("Road", "Critical"): "Deploy emergency road repair team immediately. Place warning barricades and redirect traffic. Schedule urgent inspection within 2 hours.",
    ("Road", "High"): "Inspect the road within 24 hours. Place temporary warning signs and schedule repair within a week.",
    ("Road", "Medium"): "Schedule road inspection within 48 hours. Plan repair in the next maintenance cycle.",
    ("Road", "Low"): "Add to regular road maintenance schedule. Monitor for escalation.",

    ("Water", "Critical"): "Deploy emergency water management team immediately. Check for pipe burst or flooding. Coordinate with municipal water board.",
    ("Water", "High"): "Inspect water infrastructure within 24 hours. Arrange water supply alternatives if needed.",
    ("Water", "Medium"): "Schedule water system inspection within 48 hours. Check for leaks and pipe damage.",
    ("Water", "Low"): "Add to routine water infrastructure maintenance schedule.",

    ("Electricity", "Critical"): "Report to power utility immediately. Deploy safety team to secure the area. Risk of electrocution — cordon off the zone.",
    ("Electricity", "High"): "Notify electricity board within 4 hours. Arrange temporary power if needed.",
    ("Electricity", "Medium"): "Schedule electrical inspection within 48 hours.",
    ("Electricity", "Low"): "Log for routine electrical maintenance.",

    ("Garbage", "Critical"): "Deploy emergency cleanup crew. Health hazard — notify sanitation department immediately.",
    ("Garbage", "High"): "Arrange garbage collection within 24 hours. Check for health hazards.",
    ("Garbage", "Medium"): "Schedule waste collection within 48 hours.",
    ("Garbage", "Low"): "Add to regular waste collection route.",

    ("Noise", "High"): "Investigate noise source within 24 hours. Issue warning if violating regulations.",
    ("Noise", "Medium"): "Schedule noise level monitoring. Issue notice to offending party.",
    ("Noise", "Low"): "Log for periodic monitoring.",

    ("Public Safety", "Critical"): "Immediate police/security response. Cordon the area. Notify emergency services.",
    ("Public Safety", "High"): "Deploy security patrol within 2 hours. Increase surveillance in the area.",
    ("Public Safety", "Medium"): "Schedule security review within 24 hours.",
    ("Public Safety", "Low"): "Add to regular safety patrol route.",

    ("Infrastructure", "Critical"): "Emergency structural assessment. Evacuate if needed. Deploy engineering team immediately.",
    ("Infrastructure", "High"): "Structural inspection within 24 hours. Restrict access to affected area.",
    ("Infrastructure", "Medium"): "Schedule engineering assessment within 48 hours.",
    ("Infrastructure", "Low"): "Add to infrastructure maintenance schedule.",
}

DEFAULT_RECOMMENDATIONS = {
    "Critical": "Urgent attention required. Assign to senior officer for immediate review and action.",
    "High": "Priority case. Assign review officer and schedule assessment within 24 hours.",
    "Medium": "Schedule review within 48 hours. Assign to appropriate department.",
    "Low": "Standard processing. Add to regular review queue.",
}


def recommend_action(category: str, priority_level: str) -> str:
    key = (category, priority_level)
    if key in RECOMMENDATIONS:
        return RECOMMENDATIONS[key]
    return DEFAULT_RECOMMENDATIONS.get(priority_level, "Review and take appropriate action.")
