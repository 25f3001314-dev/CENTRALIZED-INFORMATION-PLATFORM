from models import db
from datetime import datetime

class EscalationLog(db.Model):
    __tablename__ = 'escalation_logs'
    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.String(20), db.ForeignKey('issues.id'))
    reason = db.Column(db.Text)
    escalated_to = db.Column(db.String(100))
    triggered_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id, 'issue_id': self.issue_id, 'reason': self.reason,
            'escalated_to': self.escalated_to,
            'triggered_at': self.triggered_at.isoformat() if self.triggered_at else None
        }
