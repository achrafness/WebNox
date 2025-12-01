"""API routes for AJAX requests and external integrations"""
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.course import Course, Lesson
from app.models.lab import Lab, LabSubmission
from app.models.progress import UserProgress, UserScore

api_bp = Blueprint('api', __name__)

# User API
@api_bp.route('/user/profile')
@login_required
def get_profile():
    return jsonify(current_user.to_dict())

@api_bp.route('/user/stats')
@login_required
def get_user_stats():
    completed_courses = UserProgress.query.filter_by(
        user_id=current_user.id,
        progress_type='course',
        status='completed'
    ).count()
    
    completed_labs = LabSubmission.query.filter_by(
        user_id=current_user.id,
        is_correct=True
    ).count()
    
    total_courses = Course.query.filter_by(is_published=True).count()
    total_labs = Lab.query.filter_by(is_active=True).count()
    
    # Calculate rank
    users_above = User.query.filter(User.total_score > current_user.total_score).count()
    rank = users_above + 1
    
    return jsonify({
        'username': current_user.username,
        'total_score': current_user.total_score,
        'rank': rank,
        'completed_courses': completed_courses,
        'completed_labs': completed_labs,
        'total_courses': total_courses,
        'total_labs': total_labs,
        'course_progress': int((completed_courses / total_courses) * 100) if total_courses > 0 else 0,
        'lab_progress': int((completed_labs / total_labs) * 100) if total_labs > 0 else 0
    })

# Courses API
@api_bp.route('/courses')
def get_courses():
    courses = Course.query.filter_by(is_published=True).order_by(Course.order).all()
    return jsonify([c.to_dict() for c in courses])

@api_bp.route('/courses/<int:course_id>')
def get_course(course_id):
    course = Course.query.get_or_404(course_id)
    data = course.to_dict()
    data['lessons'] = [l.to_dict() for l in course.lessons]
    return jsonify(data)

@api_bp.route('/courses/<int:course_id>/progress')
@login_required
def get_course_progress(course_id):
    progress = UserProgress.query.filter_by(
        user_id=current_user.id,
        course_id=course_id,
        progress_type='course'
    ).first()
    
    completed_lessons = UserProgress.query.filter_by(
        user_id=current_user.id,
        course_id=course_id,
        progress_type='lesson',
        status='completed'
    ).count()
    
    total_lessons = Lesson.query.filter_by(course_id=course_id).count()
    
    return jsonify({
        'started': progress is not None,
        'status': progress.status if progress else None,
        'progress_percentage': progress.progress_percentage if progress else 0,
        'completed_lessons': completed_lessons,
        'total_lessons': total_lessons
    })

# Labs API
@api_bp.route('/labs')
def get_labs():
    labs = Lab.query.filter_by(is_active=True).order_by(Lab.order).all()
    return jsonify([l.to_dict() for l in labs])

@api_bp.route('/labs/<int:lab_id>')
def get_lab(lab_id):
    lab = Lab.query.get_or_404(lab_id)
    return jsonify(lab.to_dict())

@api_bp.route('/labs/<int:lab_id>/status')
@login_required
def get_lab_status(lab_id):
    submission = LabSubmission.query.filter_by(
        user_id=current_user.id,
        lab_id=lab_id
    ).first()
    
    return jsonify({
        'attempted': submission is not None,
        'completed': submission.is_correct if submission else False,
        'attempts': submission.attempts if submission else 0
    })

# Leaderboard API
@api_bp.route('/leaderboard')
def get_leaderboard():
    users = User.query.order_by(User.total_score.desc()).limit(50).all()
    
    leaderboard = []
    for i, user in enumerate(users, 1):
        leaderboard.append({
            'rank': i,
            'username': user.username,
            'avatar': user.avatar,
            'total_score': user.total_score,
            'is_current_user': current_user.is_authenticated and user.id == current_user.id
        })
    
    return jsonify(leaderboard)

# Activity API
@api_bp.route('/user/activity')
@login_required
def get_activity():
    scores = UserScore.query.filter_by(user_id=current_user.id)\
        .order_by(UserScore.earned_at.desc()).limit(10).all()
    
    return jsonify([s.to_dict() for s in scores])
