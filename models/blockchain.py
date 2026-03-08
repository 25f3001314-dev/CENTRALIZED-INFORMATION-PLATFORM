from models import db
from datetime import datetime

class BlockchainRecord(db.Model):
    __tablename__ = 'blockchain_records'
    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.String(20), db.ForeignKey('issues.id'))
    action = db.Column(db.String(100))
    data_hash = db.Column(db.String(64))
    prev_hash = db.Column(db.String(64))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    nonce = db.Column(db.Integer, default=0)
    block_index = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'id': self.id, 'issue_id': self.issue_id, 'action': self.action,
            'data_hash': self.data_hash, 'prev_hash': self.prev_hash,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'nonce': self.nonce, 'block_index': self.block_index
        }
