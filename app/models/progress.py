"""User progress and scoring models"""
from datetime import datetime
from app import db

class UserProgress(db.Model):
    __tablename__ = 'user_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=True)
    lab_id = db.Column(db.Integer, db.ForeignKey('labs.id'), nullable=True)
    progress_type = db.Column(db.String(20), nullable=False)  # 'course', 'lesson', 'lab'
    status = db.Column(db.String(20), default='in_progress')  # in_progress, completed
    progress_percentage = db.Column(db.Integer, default=0)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'course_id': self.course_id,
            'lesson_id': self.lesson_id,
            'lab_id': self.lab_id,
            'progress_type': self.progress_type,
            'status': self.status,
            'progress_percentage': self.progress_percentage,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    def __repr__(self):
        return f'<UserProgress User:{self.user_id} Type:{self.progress_type}>'


class UserScore(db.Model):
    __tablename__ = 'user_scores'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    source_type = db.Column(db.String(20), nullable=False)  # 'course', 'lab', 'achievement'
    source_id = db.Column(db.Integer, nullable=False)
    points = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'source_type': self.source_type,
            'source_id': self.source_id,
            'points': self.points,
            'description': self.description,
            'earned_at': self.earned_at.isoformat()
        }
    
    def __repr__(self):
        return f'<UserScore User:{self.user_id} Points:{self.points}>'
