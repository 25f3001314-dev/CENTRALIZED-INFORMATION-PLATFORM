from models import db

class Officer(db.Model):
    __tablename__ = 'officers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100))
    badge_number = db.Column(db.String(20))
    active_cases = db.Column(db.Integer, default=0)
    resolved_count = db.Column(db.Integer, default=0)
    avg_rating = db.Column(db.Float, default=0.0)
    gps_lat = db.Column(db.Float)
    gps_lng = db.Column(db.Float)

    def to_dict(self):
        return {
            'id': self.id, 'name': self.name, 'department': self.department,
            'badge_number': self.badge_number, 'active_cases': self.active_cases,
            'resolved_count': self.resolved_count, 'avg_rating': self.avg_rating,
            'gps_lat': self.gps_lat, 'gps_lng': self.gps_lng
        }
