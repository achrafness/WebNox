"""Course and Lesson models for educational content"""
from datetime import datetime
from app import db

class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(20), default='beginner')  # beginner, intermediate, advanced
    category = db.Column(db.String(100), nullable=False)  # XSS, SQLi, CSRF, SSRF, IDOR, etc.
    image = db.Column(db.String(255), default='course-default.png')
    duration_minutes = db.Column(db.Integer, default=60)
    points = db.Column(db.Integer, default=100)
    order = db.Column(db.Integer, default=0)
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    lessons = db.relationship('Lesson', backref='course', lazy=True, cascade='all, delete-orphan', order_by='Lesson.order')
    labs = db.relationship('Lab', backref='course', lazy=True)
    
    def get_total_lessons(self):
        return len(self.lessons)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'description': self.description,
            'difficulty': self.difficulty,
            'category': self.category,
            'image': self.image,
            'duration_minutes': self.duration_minutes,
            'points': self.points,
            'total_lessons': self.get_total_lessons(),
            'is_published': self.is_published
        }
    
    def __repr__(self):
        return f'<Course {self.title}>'


class Lesson(db.Model):
    __tablename__ = 'lessons'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)  # Markdown content
    order = db.Column(db.Integer, default=0)
    duration_minutes = db.Column(db.Integer, default=15)
    video_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'title': self.title,
            'slug': self.slug,
            'content': self.content,
            'order': self.order,
            'duration_minutes': self.duration_minutes,
            'video_url': self.video_url
        }
    
    def __repr__(self):
        return f'<Lesson {self.title}>'
