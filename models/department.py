from models import db

class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    officer_in_charge = db.Column(db.String(100))
    total_issues = db.Column(db.Integer, default=0)
    resolve_rate = db.Column(db.Float, default=0.0)
    avg_days = db.Column(db.Float, default=0.0)

    def to_dict(self):
        return {
            'id': self.id, 'name': self.name, 'description': self.description,
            'officer_in_charge': self.officer_in_charge, 'total_issues': self.total_issues,
            'resolve_rate': self.resolve_rate, 'avg_days': self.avg_days
        }
