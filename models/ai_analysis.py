from models import db
from datetime import datetime

class AIAnalysis(db.Model):
    __tablename__ = 'ai_analyses'
    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.String(20), db.ForeignKey('issues.id'))
    category = db.Column(db.String(50))
    subcategory = db.Column(db.String(100))
    confidence = db.Column(db.Float)
    severity = db.Column(db.String(20))
    suggested_dept = db.Column(db.String(100))
    est_resolution = db.Column(db.String(50))
    ocr_text = db.Column(db.Text)
    photo_analysis = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id, 'issue_id': self.issue_id, 'category': self.category,
            'subcategory': self.subcategory, 'confidence': self.confidence,
            'severity': self.severity, 'suggested_dept': self.suggested_dept,
            'est_resolution': self.est_resolution, 'ocr_text': self.ocr_text,
            'photo_analysis': self.photo_analysis
        }
