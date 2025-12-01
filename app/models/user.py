"""User model for authentication and profile management"""
from datetime import datetime
from flask_login import UserMixin
from app import db, bcrypt, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='student')  # student, admin
    avatar = db.Column(db.String(255), default='default.png')
    bio = db.Column(db.Text, nullable=True)
    total_score = db.Column(db.Integer, default=0)
    rank = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    progress = db.relationship('UserProgress', backref='user', lazy=True, cascade='all, delete-orphan')
    scores = db.relationship('UserScore', backref='user', lazy=True, cascade='all, delete-orphan')
    lab_submissions = db.relationship('LabSubmission', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def update_total_score(self):
        from app.models.progress import UserScore
        total = db.session.query(db.func.sum(UserScore.points)).filter_by(user_id=self.id).scalar()
        self.total_score = total or 0
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'avatar': self.avatar,
            'bio': self.bio,
            'total_score': self.total_score,
            'rank': self.rank,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<User {self.username}>'
