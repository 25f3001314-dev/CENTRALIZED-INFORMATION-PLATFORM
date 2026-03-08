import math
import hashlib
import json
from datetime import datetime


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance in km between two GPS coordinates."""
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def sha256_hash(data):
    """Generate SHA-256 hash of data."""
    if isinstance(data, dict):
        data = json.dumps(data, sort_keys=True)
    return hashlib.sha256(str(data).encode()).hexdigest()


def generate_issue_id():
    """Generate unique issue ID like CP-2024-001."""
    import random
    year = datetime.utcnow().year
    num = random.randint(10000, 99999)
    return f"CP-{year}-{num}"


def days_since(dt):
    """Return number of days since a given datetime."""
    if not dt:
        return 0
    return (datetime.utcnow() - dt).total_seconds() / 86400


def format_response(data=None, message="Success", status=200):
    """Standard JSON response format."""
    return {"status": "success" if status < 400 else "error", "message": message, "data": data}


def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
