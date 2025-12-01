"""
Lab Instance model for tracking user lab containers
"""
from datetime import datetime
from app import db

class LabInstance(db.Model):
    __tablename__ = 'lab_instances'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    lab_id = db.Column(db.Integer, db.ForeignKey('labs.id'), nullable=False)
    container_id = db.Column(db.String(100), nullable=True)
    container_name = db.Column(db.String(200), nullable=False)
    port = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, running, stopped, error
    lab_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime, nullable=True)
    stopped_at = db.Column(db.DateTime, nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('lab_instances', lazy=True))
    lab = db.relationship('Lab', backref=db.backref('instances', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'lab_id': self.lab_id,
            'container_id': self.container_id,
            'container_name': self.container_name,
            'port': self.port,
            'status': self.status,
            'lab_url': self.lab_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }
    
    def __repr__(self):
        return f'<LabInstance User:{self.user_id} Lab:{self.lab_id} Status:{self.status}>'
