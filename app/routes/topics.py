"""Topic routes for security categories"""
from flask import Blueprint, render_template, jsonify
from flask_login import current_user
from app import db
from app.models.topic import Topic
from app.models.course import Course
from app.models.lab import Lab, LabSubmission
from app.models.progress import UserProgress

topics_bp = Blueprint('topics', __name__)


@topics_bp.route('/')
def list_topics():
    """List all security topics"""
    topics = Topic.query.filter_by(is_active=True).order_by(Topic.order).all()
    
    # Get user progress for each topic if logged in
    topic_progress = {}
    if current_user.is_authenticated:
        for topic in topics:
            completed_labs = 0
            total_labs = len([l for l in topic.labs if l.is_active])
            
            if total_labs > 0:
                for lab in topic.labs:
                    if lab.is_active:
                        submission = LabSubmission.query.filter_by(
                            user_id=current_user.id,
                            lab_id=lab.id,
                            is_correct=True
                        ).first()
                        if submission:
                            completed_labs += 1
            
            topic_progress[topic.id] = {
                'completed': completed_labs,
                'total': total_labs,
                'percentage': int((completed_labs / total_labs * 100)) if total_labs > 0 else 0
            }
    
    return render_template('topics/list.html', 
                         topics=topics,
                         topic_progress=topic_progress)


@topics_bp.route('/<slug>')
def topic_detail(slug):
    """Show topic details with related courses and labs"""
    topic = Topic.query.filter_by(slug=slug, is_active=True).first_or_404()
    
    # Get published courses for this topic
    courses = Course.query.filter_by(
        topic_id=topic.id, 
        is_published=True
    ).order_by(Course.order).all()
    
    # Get active labs for this topic
    labs = Lab.query.filter_by(
        topic_id=topic.id, 
        is_active=True
    ).order_by(Lab.order).all()
    
    # Get user progress if logged in
    completed_labs = []
    if current_user.is_authenticated:
        submissions = LabSubmission.query.filter_by(
            user_id=current_user.id,
            is_correct=True
        ).all()
        completed_labs = [s.lab_id for s in submissions]
    
    return render_template('topics/detail.html',
                         topic=topic,
                         courses=courses,
                         labs=labs,
                         completed_labs=completed_labs)


@topics_bp.route('/api/list')
def api_list_topics():
    """API endpoint for topics"""
    topics = Topic.query.filter_by(is_active=True).order_by(Topic.order).all()
    return jsonify([topic.to_dict() for topic in topics])
