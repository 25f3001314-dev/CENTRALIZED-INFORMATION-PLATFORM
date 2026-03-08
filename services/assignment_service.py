import logging
from utils.helpers import haversine_distance

logger = logging.getLogger(__name__)


def assign_officer(issue, db_session=None):
    """Assign best officer to an issue based on workload, proximity, and performance."""
    from models.officer import Officer

    department = issue.get('department') if isinstance(issue, dict) else issue.department
    lat = issue.get('lat') if isinstance(issue, dict) else issue.lat
    lng = issue.get('lng') if isinstance(issue, dict) else issue.lng

    officers = Officer.query.filter_by(department=department).all()
    if not officers:
        officers = Officer.query.all()
    if not officers:
        return None, None

    scored = []
    for officer in officers:
        # Workload score: fewer active cases = better (0-40 pts)
        max_cases = max((o.active_cases for o in officers), default=1) or 1
        workload_score = (1 - officer.active_cases / (max_cases + 1)) * 40

        # Proximity score (0-30 pts)
        proximity_score = 0
        if lat and lng and officer.gps_lat and officer.gps_lng:
            dist = haversine_distance(lat, lng, officer.gps_lat, officer.gps_lng)
            proximity_score = max(0, 30 - dist)
        else:
            proximity_score = 15  # neutral if no GPS

        # Performance score: higher resolve rate and rating = better (0-30 pts)
        total = officer.active_cases + officer.resolved_count
        resolve_rate = officer.resolved_count / total if total > 0 else 0.5
        perf_score = resolve_rate * 20 + (officer.avg_rating / 5) * 10

        total_score = workload_score + proximity_score + perf_score
        scored.append((officer, total_score))
        logger.debug("Officer %s score: workload=%.1f proximity=%.1f perf=%.1f total=%.1f",
                     officer.name, workload_score, proximity_score, perf_score, total_score)

    best_officer = max(scored, key=lambda x: x[1])[0]
    logger.info("Assigned officer %s to issue", best_officer.name)
    return best_officer.name, best_officer.id
