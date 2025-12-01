"""Main routes - Home, Dashboard, Leaderboard"""
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.course import Course
from app.models.lab import Lab
from app.models.progress import UserProgress, UserScore

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    courses = Course.query.filter_by(is_published=True).order_by(Course.order).limit(6).all()
    labs = Lab.query.filter_by(is_active=True).order_by(Lab.order).limit(6).all()
    
    # Stats
    total_users = User.query.count()
    total_courses = Course.query.filter_by(is_published=True).count()
    total_labs = Lab.query.filter_by(is_active=True).count()
    
    return render_template('main/home.html', 
                         courses=courses, 
                         labs=labs,
                         total_users=total_users,
                         total_courses=total_courses,
                         total_labs=total_labs)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Get user progress
    completed_courses = UserProgress.query.filter_by(
        user_id=current_user.id, 
        progress_type='course', 
        status='completed'
    ).count()
    
    completed_labs = UserProgress.query.filter_by(
        user_id=current_user.id, 
        progress_type='lab', 
        status='completed'
    ).count()
    
    # Recent activity
    recent_progress = UserProgress.query.filter_by(user_id=current_user.id)\
        .order_by(UserProgress.started_at.desc()).limit(5).all()
    
    # Recent scores
    recent_scores = UserScore.query.filter_by(user_id=current_user.id)\
        .order_by(UserScore.earned_at.desc()).limit(5).all()
    
    # Recommended courses (not started)
    started_course_ids = [p.course_id for p in UserProgress.query.filter_by(
        user_id=current_user.id, progress_type='course').all()]
    
    recommended_courses = Course.query.filter(
        Course.is_published == True,
        ~Course.id.in_(started_course_ids) if started_course_ids else True
    ).limit(3).all()
    
    # Calculate rank
    users_above = User.query.filter(User.total_score > current_user.total_score).count()
    current_user.rank = users_above + 1
    
    return render_template('main/dashboard.html',
                         completed_courses=completed_courses,
                         completed_labs=completed_labs,
                         recent_progress=recent_progress,
                         recent_scores=recent_scores,
                         recommended_courses=recommended_courses)

@main_bp.route('/leaderboard')
def leaderboard():
    # Get top users
    top_users = User.query.order_by(User.total_score.desc()).limit(50).all()
    
    # Assign ranks
    for i, user in enumerate(top_users, 1):
        user.rank = i
    
    return render_template('main/leaderboard.html', users=top_users)

@main_bp.route('/about')
def about():
    return render_template('main/about.html')
