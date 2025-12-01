"""Topic model for organizing security vulnerability categories"""
from datetime import datetime
from app import db


class Topic(db.Model):
    __tablename__ = 'topics'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(50), default='shield-alt')  # FontAwesome icon
    color = db.Column(db.String(20), default='#0d6efd')  # Hex color
    severity = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    owasp_category = db.Column(db.String(100), nullable=True)  # OWASP Top 10 reference
    order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    courses = db.relationship('Course', backref='topic', lazy=True)
    labs = db.relationship('Lab', backref='topic', lazy=True)
    
    def get_total_courses(self):
        return len([c for c in self.courses if c.is_published])
    
    def get_total_labs(self):
        return len([l for l in self.labs if l.is_active])
    
    def get_total_points(self):
        """Calculate total available points for this topic"""
        course_points = sum(c.points for c in self.courses if c.is_published)
        lab_points = sum(l.points for l in self.labs if l.is_active)
        return course_points + lab_points
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'icon': self.icon,
            'color': self.color,
            'severity': self.severity,
            'owasp_category': self.owasp_category,
            'total_courses': self.get_total_courses(),
            'total_labs': self.get_total_labs(),
            'total_points': self.get_total_points(),
            'is_active': self.is_active
        }
    
    def __repr__(self):
        return f'<Topic {self.name}>'
