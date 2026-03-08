from models import db
from datetime import datetime

class Timeline(db.Model):
    __tablename__ = 'timelines'
    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.String(20), db.ForeignKey('issues.id'))
    step_name = db.Column(db.String(100))
    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='done')  # done/current/pending

    def to_dict(self):
        return {
            'id': self.id, 'issue_id': self.issue_id, 'step_name': self.step_name,
            'description': self.description,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'status': self.status
        }
