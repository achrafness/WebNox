"""Course routes"""
from flask import Blueprint, render_template, abort, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models.course import Course, Lesson
from app.models.progress import UserProgress, UserScore

courses_bp = Blueprint('courses', __name__)

@courses_bp.route('/')
def list_courses():
    courses = Course.query.filter_by(is_published=True).order_by(Course.order).all()
    
    # Get categories for filtering
    categories = db.session.query(Course.category).distinct().all()
    categories = [c[0] for c in categories]
    
    return render_template('courses/list.html', courses=courses, categories=categories)

@courses_bp.route('/<slug>')
def course_detail(slug):
    course = Course.query.filter_by(slug=slug, is_published=True).first_or_404()
    
    # Get user progress if logged in
    user_progress = None
    completed_lessons = []
    if current_user.is_authenticated:
        user_progress = UserProgress.query.filter_by(
            user_id=current_user.id,
            course_id=course.id,
            progress_type='course'
        ).first()
        
        completed_lesson_progress = UserProgress.query.filter_by(
            user_id=current_user.id,
            course_id=course.id,
            progress_type='lesson',
            status='completed'
        ).all()
        completed_lessons = [p.lesson_id for p in completed_lesson_progress]
    
    return render_template('courses/detail.html', 
                         course=course, 
                         user_progress=user_progress,
                         completed_lessons=completed_lessons)

@courses_bp.route('/<slug>/start')
@login_required
def start_course(slug):
    course = Course.query.filter_by(slug=slug, is_published=True).first_or_404()
    
    # Check if already started
    existing = UserProgress.query.filter_by(
        user_id=current_user.id,
        course_id=course.id,
        progress_type='course'
    ).first()
    
    if not existing:
        progress = UserProgress(
            user_id=current_user.id,
            course_id=course.id,
            progress_type='course',
            status='in_progress'
        )
        db.session.add(progress)
        db.session.commit()
        flash('Course started! Good luck!', 'success')
    
    # Redirect to first lesson
    first_lesson = Lesson.query.filter_by(course_id=course.id).order_by(Lesson.order).first()
    if first_lesson:
        return redirect(url_for('courses.lesson', slug=slug, lesson_slug=first_lesson.slug))
    
    return redirect(url_for('courses.course_detail', slug=slug))

@courses_bp.route('/<slug>/lesson/<lesson_slug>')
@login_required
def lesson(slug, lesson_slug):
    course = Course.query.filter_by(slug=slug, is_published=True).first_or_404()
    lesson = Lesson.query.filter_by(course_id=course.id, slug=lesson_slug).first_or_404()
    
    # Get all lessons for navigation
    lessons = Lesson.query.filter_by(course_id=course.id).order_by(Lesson.order).all()
    current_index = next((i for i, l in enumerate(lessons) if l.id == lesson.id), 0)
    
    prev_lesson = lessons[current_index - 1] if current_index > 0 else None
    next_lesson = lessons[current_index + 1] if current_index < len(lessons) - 1 else None
    
    # Track lesson progress
    lesson_progress = UserProgress.query.filter_by(
        user_id=current_user.id,
        lesson_id=lesson.id,
        progress_type='lesson'
    ).first()
    
    if not lesson_progress:
        lesson_progress = UserProgress(
            user_id=current_user.id,
            course_id=course.id,
            lesson_id=lesson.id,
            progress_type='lesson',
            status='in_progress'
        )
        db.session.add(lesson_progress)
        db.session.commit()
    
    return render_template('courses/lesson.html',
                         course=course,
                         lesson=lesson,
                         lessons=lessons,
                         prev_lesson=prev_lesson,
                         next_lesson=next_lesson,
                         lesson_progress=lesson_progress)

@courses_bp.route('/<slug>/lesson/<lesson_slug>/complete')
@login_required
def complete_lesson(slug, lesson_slug):
    course = Course.query.filter_by(slug=slug, is_published=True).first_or_404()
    lesson = Lesson.query.filter_by(course_id=course.id, slug=lesson_slug).first_or_404()
    
    # Mark lesson as completed
    lesson_progress = UserProgress.query.filter_by(
        user_id=current_user.id,
        lesson_id=lesson.id,
        progress_type='lesson'
    ).first()
    
    if lesson_progress and lesson_progress.status != 'completed':
        lesson_progress.status = 'completed'
        lesson_progress.completed_at = datetime.utcnow()
        lesson_progress.progress_percentage = 100
        db.session.commit()
        
        # Check if all lessons are completed
        total_lessons = Lesson.query.filter_by(course_id=course.id).count()
        completed_lessons = UserProgress.query.filter_by(
            user_id=current_user.id,
            course_id=course.id,
            progress_type='lesson',
            status='completed'
        ).count()
        
        # Update course progress
        course_progress = UserProgress.query.filter_by(
            user_id=current_user.id,
            course_id=course.id,
            progress_type='course'
        ).first()
        
        if course_progress:
            course_progress.progress_percentage = int((completed_lessons / total_lessons) * 100)
            
            if completed_lessons == total_lessons:
                course_progress.status = 'completed'
                course_progress.completed_at = datetime.utcnow()
                
                # Award points
                score = UserScore(
                    user_id=current_user.id,
                    source_type='course',
                    source_id=course.id,
                    points=course.points,
                    description=f'Completed course: {course.title}'
                )
                db.session.add(score)
                current_user.update_total_score()
                
                flash(f'Congratulations! You completed the course and earned {course.points} points!', 'success')
            
            db.session.commit()
        
        flash('Lesson completed!', 'success')
    
    # Go to next lesson or course page
    lessons = Lesson.query.filter_by(course_id=course.id).order_by(Lesson.order).all()
    current_index = next((i for i, l in enumerate(lessons) if l.id == lesson.id), 0)
    
    if current_index < len(lessons) - 1:
        next_lesson = lessons[current_index + 1]
        return redirect(url_for('courses.lesson', slug=slug, lesson_slug=next_lesson.slug))
    
    return redirect(url_for('courses.course_detail', slug=slug))
