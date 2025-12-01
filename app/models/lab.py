"""Lab model for hands-on security challenges"""
from datetime import datetime
from app import db

class Lab(db.Model):
    __tablename__ = 'labs'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)  # Markdown instructions
    difficulty = db.Column(db.String(20), default='beginner')
    category = db.Column(db.String(100), nullable=False)
    vulnerability_type = db.Column(db.String(100), nullable=False)  # XSS, SQLi, CSRF, etc.
    points = db.Column(db.Integer, default=50)
    flag = db.Column(db.String(255), nullable=False)  # The flag to capture
    hints = db.Column(db.Text, nullable=True)  # JSON array of hints
    docker_image = db.Column(db.String(255), nullable=True)
    docker_port = db.Column(db.Integer, default=8080)
    has_bot = db.Column(db.Boolean, default=False)  # Whether lab has XSS bot
    bot_interval = db.Column(db.Integer, default=30)  # Bot visit interval in seconds
    is_active = db.Column(db.Boolean, default=True)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    submissions = db.relationship('LabSubmission', backref='lab', lazy=True, cascade='all, delete-orphan')
    
    def get_completion_count(self):
        return LabSubmission.query.filter_by(lab_id=self.id, is_correct=True).count()
    
    def to_dict(self, include_flag=False):
        data = {
            'id': self.id,
            'course_id': self.course_id,
            'title': self.title,
            'slug': self.slug,
            'description': self.description,
            'instructions': self.instructions,
            'difficulty': self.difficulty,
            'category': self.category,
            'vulnerability_type': self.vulnerability_type,
            'points': self.points,
            'hints': self.hints,
            'docker_image': self.docker_image,
            'docker_port': self.docker_port,
            'is_active': self.is_active,
            'completions': self.get_completion_count()
        }
        if include_flag:
            data['flag'] = self.flag
        return data
    
    def __repr__(self):
        return f'<Lab {self.title}>'


class LabSubmission(db.Model):
    __tablename__ = 'lab_submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    lab_id = db.Column(db.Integer, db.ForeignKey('labs.id'), nullable=False)
    submitted_flag = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    attempts = db.Column(db.Integer, default=1)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'lab_id': self.lab_id,
            'is_correct': self.is_correct,
            'attempts': self.attempts,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    def __repr__(self):
        return f'<LabSubmission User:{self.user_id} Lab:{self.lab_id}>'
