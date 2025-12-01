"""Admin routes for platform management"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models.user import User
from app.models.course import Course, Lesson
from app.models.lab import Lab

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    stats = {
        'total_users': User.query.count(),
        'total_courses': Course.query.count(),
        'total_labs': Lab.query.count(),
        'total_lessons': Lesson.query.count()
    }
    
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', stats=stats, recent_users=recent_users)

# User Management
@admin_bp.route('/users')
@login_required
@admin_required
def users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Cannot modify your own admin status.', 'warning')
    else:
        user.role = 'student' if user.role == 'admin' else 'admin'
        db.session.commit()
        flash(f'User {user.username} role updated to {user.role}.', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Cannot delete yourself.', 'warning')
    else:
        db.session.delete(user)
        db.session.commit()
        flash(f'User {user.username} deleted.', 'success')
    return redirect(url_for('admin.users'))

# Course Management
@admin_bp.route('/courses')
@login_required
@admin_required
def courses():
    courses = Course.query.order_by(Course.order).all()
    return render_template('admin/courses.html', courses=courses)

@admin_bp.route('/courses/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_course():
    if request.method == 'POST':
        course = Course(
            title=request.form['title'],
            slug=request.form['slug'],
            description=request.form['description'],
            difficulty=request.form['difficulty'],
            category=request.form['category'],
            duration_minutes=int(request.form.get('duration_minutes', 60)),
            points=int(request.form.get('points', 100)),
            order=int(request.form.get('order', 0)),
            is_published=request.form.get('is_published') == 'on'
        )
        db.session.add(course)
        db.session.commit()
        flash('Course created successfully!', 'success')
        return redirect(url_for('admin.courses'))
    
    return render_template('admin/course_form.html', course=None)

@admin_bp.route('/courses/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_course(course_id):
    course = Course.query.get_or_404(course_id)
    
    if request.method == 'POST':
        course.title = request.form['title']
        course.slug = request.form['slug']
        course.description = request.form['description']
        course.difficulty = request.form['difficulty']
        course.category = request.form['category']
        course.duration_minutes = int(request.form.get('duration_minutes', 60))
        course.points = int(request.form.get('points', 100))
        course.order = int(request.form.get('order', 0))
        course.is_published = request.form.get('is_published') == 'on'
        
        db.session.commit()
        flash('Course updated successfully!', 'success')
        return redirect(url_for('admin.courses'))
    
    return render_template('admin/course_form.html', course=course)

@admin_bp.route('/courses/<int:course_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    flash('Course deleted successfully!', 'success')
    return redirect(url_for('admin.courses'))

# Lesson Management
@admin_bp.route('/courses/<int:course_id>/lessons')
@login_required
@admin_required
def lessons(course_id):
    course = Course.query.get_or_404(course_id)
    return render_template('admin/lessons.html', course=course)

@admin_bp.route('/courses/<int:course_id>/lessons/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_lesson(course_id):
    course = Course.query.get_or_404(course_id)
    
    if request.method == 'POST':
        lesson = Lesson(
            course_id=course.id,
            title=request.form['title'],
            slug=request.form['slug'],
            content=request.form['content'],
            order=int(request.form.get('order', 0)),
            duration_minutes=int(request.form.get('duration_minutes', 15)),
            video_url=request.form.get('video_url')
        )
        db.session.add(lesson)
        db.session.commit()
        flash('Lesson created successfully!', 'success')
        return redirect(url_for('admin.lessons', course_id=course.id))
    
    return render_template('admin/lesson_form.html', course=course, lesson=None)

@admin_bp.route('/courses/<int:course_id>/lessons/<int:lesson_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_lesson(course_id, lesson_id):
    course = Course.query.get_or_404(course_id)
    lesson = Lesson.query.get_or_404(lesson_id)
    
    if request.method == 'POST':
        lesson.title = request.form['title']
        lesson.slug = request.form['slug']
        lesson.content = request.form['content']
        lesson.order = int(request.form.get('order', 0))
        lesson.duration_minutes = int(request.form.get('duration_minutes', 15))
        lesson.video_url = request.form.get('video_url')
        
        db.session.commit()
        flash('Lesson updated successfully!', 'success')
        return redirect(url_for('admin.lessons', course_id=course.id))
    
    return render_template('admin/lesson_form.html', course=course, lesson=lesson)

@admin_bp.route('/courses/<int:course_id>/lessons/<int:lesson_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_lesson(course_id, lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    course_id = lesson.course_id
    db.session.delete(lesson)
    db.session.commit()
    flash('Lesson deleted successfully!', 'success')
    return redirect(url_for('admin.lessons', course_id=course_id))

# Lab Management
@admin_bp.route('/labs')
@login_required
@admin_required
def labs():
    labs = Lab.query.order_by(Lab.order).all()
    return render_template('admin/labs.html', labs=labs)

@admin_bp.route('/labs/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_lab():
    courses = Course.query.all()
    
    if request.method == 'POST':
        lab = Lab(
            course_id=request.form.get('course_id') or None,
            title=request.form['title'],
            slug=request.form['slug'],
            description=request.form['description'],
            instructions=request.form['instructions'],
            difficulty=request.form['difficulty'],
            category=request.form['category'],
            vulnerability_type=request.form['vulnerability_type'],
            points=int(request.form.get('points', 50)),
            flag=request.form['flag'],
            hints=request.form.get('hints'),
            docker_image=request.form.get('docker_image'),
            docker_port=int(request.form.get('docker_port', 8080)),
            order=int(request.form.get('order', 0)),
            is_active=request.form.get('is_active') == 'on'
        )
        db.session.add(lab)
        db.session.commit()
        flash('Lab created successfully!', 'success')
        return redirect(url_for('admin.labs'))
    
    return render_template('admin/lab_form.html', lab=None, courses=courses)

@admin_bp.route('/labs/<int:lab_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_lab(lab_id):
    lab = Lab.query.get_or_404(lab_id)
    courses = Course.query.all()
    
    if request.method == 'POST':
        lab.course_id = request.form.get('course_id') or None
        lab.title = request.form['title']
        lab.slug = request.form['slug']
        lab.description = request.form['description']
        lab.instructions = request.form['instructions']
        lab.difficulty = request.form['difficulty']
        lab.category = request.form['category']
        lab.vulnerability_type = request.form['vulnerability_type']
        lab.points = int(request.form.get('points', 50))
        lab.flag = request.form['flag']
        lab.hints = request.form.get('hints')
        lab.docker_image = request.form.get('docker_image')
        lab.docker_port = int(request.form.get('docker_port', 8080))
        lab.order = int(request.form.get('order', 0))
        lab.is_active = request.form.get('is_active') == 'on'
        
        db.session.commit()
        flash('Lab updated successfully!', 'success')
        return redirect(url_for('admin.labs'))
    
    return render_template('admin/lab_form.html', lab=lab, courses=courses)

@admin_bp.route('/labs/<int:lab_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_lab(lab_id):
    lab = Lab.query.get_or_404(lab_id)
    db.session.delete(lab)
    db.session.commit()
    flash('Lab deleted successfully!', 'success')
    return redirect(url_for('admin.labs'))
