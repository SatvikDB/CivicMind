from typing import Optional
from pydantic import BaseModel

class User(BaseModel):
    id: str
    email: str
    name: str
    role: str  # "citizen" or "admin"
    ward: Optional[str] = "Central Zone"
    avatar: Optional[str] = None

# Preset Demo Accounts for Hackathon Demonstration
DEMO_USERS = {
    "citizen@civicmind.ai": User(
        id="usr_citizen_01",
        email="citizen@civicmind.ai",
        name="Aarav Sharma",
        role="citizen",
        ward="Ward 12 - Campus Area",
        avatar="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=200&q=80"
    ),
    "admin@civicmind.ai": User(
        id="usr_admin_01",
        email="admin@civicmind.ai",
        name="Eng. Ramesh V (Ward Officer)",
        role="admin",
        ward="Central Municipal Zone",
        avatar="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=200&q=80"
    )
}

def authenticate_user(email: str, password: str) -> Optional[User]:
    """Authenticate user credentials or return preset demo profile."""
    email_clean = email.strip().lower()
    if email_clean in DEMO_USERS:
        return DEMO_USERS[email_clean]
    
    # Custom registration / runtime user fallback
    if "admin" in email_clean:
        return User(
            id=f"usr_admin_{hash(email_clean) % 1000}",
            email=email_clean,
            name="Municipal Officer",
            role="admin",
            ward="City HQ Zone"
        )
    return User(
        id=f"usr_citizen_{hash(email_clean) % 1000}",
        email=email_clean,
        name=email_clean.split("@")[0].capitalize(),
        role="citizen",
        ward="Local Ward"
    )
