from models import db
from datetime import datetime

class Issue(db.Model):
    __tablename__ = 'issues'
    id = db.Column(db.String(20), primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))
    department = db.Column(db.String(100))
    officer = db.Column(db.String(100))
    officer_id = db.Column(db.Integer, db.ForeignKey('officers.id'))
    priority = db.Column(db.String(20), default='Medium')
    status = db.Column(db.String(30), default='Filed')
    progress = db.Column(db.Integer, default=0)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    location = db.Column(db.String(200))
    photos = db.Column(db.Text, default='{}')  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    escalated = db.Column(db.Boolean, default=False)
    citizen_name = db.Column(db.String(100))
    citizen_phone = db.Column(db.String(20))
    citizen_email = db.Column(db.String(100))

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'department': self.department,
            'officer': self.officer,
            'priority': self.priority,
            'status': self.status,
            'progress': self.progress,
            'lat': self.lat,
            'lng': self.lng,
            'location': self.location,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'escalated': self.escalated,
            'citizen_name': self.citizen_name,
            'citizen_phone': self.citizen_phone,
            'citizen_email': self.citizen_email,
        }
