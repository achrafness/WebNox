"""Lab routes for hands-on challenges"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models.lab import Lab, LabSubmission
from app.models.lab_instance import LabInstance
from app.models.progress import UserProgress, UserScore

labs_bp = Blueprint('labs', __name__)

@labs_bp.route('/')
def list_labs():
    labs = Lab.query.filter_by(is_active=True).order_by(Lab.order).all()
    
    # Get categories for filtering
    categories = db.session.query(Lab.category).distinct().all()
    categories = [c[0] for c in categories]
    
    # Get user completions if logged in
    completed_labs = []
    running_instances = {}
    if current_user.is_authenticated:
        submissions = LabSubmission.query.filter_by(
            user_id=current_user.id,
            is_correct=True
        ).all()
        completed_labs = [s.lab_id for s in submissions]
        
        # Get running instances
        instances = LabInstance.query.filter_by(
            user_id=current_user.id,
            status='running'
        ).all()
        running_instances = {i.lab_id: i for i in instances}
    
    return render_template('labs/list.html', 
                         labs=labs, 
                         categories=categories,
                         completed_labs=completed_labs,
                         running_instances=running_instances)

@labs_bp.route('/<slug>')
@login_required
def lab_detail(slug):
    lab = Lab.query.filter_by(slug=slug, is_active=True).first_or_404()
    
    # Get user submission
    submission = LabSubmission.query.filter_by(
        user_id=current_user.id,
        lab_id=lab.id
    ).first()
    
    # Get running instance
    instance = LabInstance.query.filter_by(
        user_id=current_user.id,
        lab_id=lab.id,
        status='running'
    ).first()
    
    # Track lab progress
    progress = UserProgress.query.filter_by(
        user_id=current_user.id,
        lab_id=lab.id,
        progress_type='lab'
    ).first()
    
    if not progress:
        progress = UserProgress(
            user_id=current_user.id,
            lab_id=lab.id,
            progress_type='lab',
            status='in_progress'
        )
        db.session.add(progress)
        db.session.commit()
    
    return render_template('labs/detail.html', 
                         lab=lab, 
                         submission=submission,
                         progress=progress,
                         instance=instance)

@labs_bp.route('/<slug>/submit', methods=['POST'])
@login_required
def submit_flag(slug):
    lab = Lab.query.filter_by(slug=slug, is_active=True).first_or_404()
    submitted_flag = request.form.get('flag', '').strip()
    
    if not submitted_flag:
        flash('Please enter a flag.', 'warning')
        return redirect(url_for('labs.lab_detail', slug=slug))
    
    # Check if already completed
    existing_correct = LabSubmission.query.filter_by(
        user_id=current_user.id,
        lab_id=lab.id,
        is_correct=True
    ).first()
    
    if existing_correct:
        flash('You have already completed this lab!', 'info')
        return redirect(url_for('labs.lab_detail', slug=slug))
    
    # Check flag
    is_correct = submitted_flag == lab.flag
    
    # Get or create submission
    submission = LabSubmission.query.filter_by(
        user_id=current_user.id,
        lab_id=lab.id
    ).first()
    
    if submission:
        submission.attempts += 1
        submission.submitted_flag = submitted_flag
        submission.is_correct = is_correct
    else:
        submission = LabSubmission(
            user_id=current_user.id,
            lab_id=lab.id,
            submitted_flag=submitted_flag,
            is_correct=is_correct
        )
        db.session.add(submission)
    
    if is_correct:
        submission.completed_at = datetime.utcnow()
        
        # Update progress
        progress = UserProgress.query.filter_by(
            user_id=current_user.id,
            lab_id=lab.id,
            progress_type='lab'
        ).first()
        
        if progress:
            progress.status = 'completed'
            progress.completed_at = datetime.utcnow()
            progress.progress_percentage = 100
        
        # Award points
        score = UserScore(
            user_id=current_user.id,
            source_type='lab',
            source_id=lab.id,
            points=lab.points,
            description=f'Completed lab: {lab.title}'
        )
        db.session.add(score)
        current_user.update_total_score()
        
        flash(f'🎉 Correct! You earned {lab.points} points!', 'success')
    else:
        flash('❌ Incorrect flag. Try again!', 'danger')
    
    db.session.commit()
    return redirect(url_for('labs.lab_detail', slug=slug))

@labs_bp.route('/<slug>/hint/<int:hint_num>')
@login_required
def get_hint(slug, hint_num):
    lab = Lab.query.filter_by(slug=slug, is_active=True).first_or_404()
    
    import json
    hints = json.loads(lab.hints) if lab.hints else []
    
    if hint_num < 1 or hint_num > len(hints):
        return jsonify({'error': 'Hint not found'}), 404
    
    return jsonify({'hint': hints[hint_num - 1]})


@labs_bp.route('/<slug>/start', methods=['POST'])
@login_required
def start_lab(slug):
    """Start a lab instance for the current user"""
    lab = Lab.query.filter_by(slug=slug, is_active=True).first_or_404()
    
    try:
        from app.services.lab_orchestrator import start_lab_instance, get_running_instance
        
        # Check if already running
        existing = get_running_instance(current_user.id, lab.id)
        if existing:
            flash(f'Lab is already running at {existing.lab_url}', 'info')
            return redirect(url_for('labs.lab_detail', slug=slug))
        
        # Start new instance
        instance, message = start_lab_instance(current_user.id, slug, lab.id)
        
        if instance:
            flash(f'🚀 Lab started successfully! Access it at: {instance.lab_url}', 'success')
        else:
            flash(f'Failed to start lab: {message}', 'danger')
            
    except ImportError:
        # Docker not available - provide static lab URL
        flash('Docker is not available. Using static lab environment.', 'warning')
    except Exception as e:
        flash(f'Error starting lab: {str(e)}', 'danger')
    
    return redirect(url_for('labs.lab_detail', slug=slug))


@labs_bp.route('/<slug>/stop', methods=['POST'])
@login_required
def stop_lab(slug):
    """Stop a running lab instance"""
    lab = Lab.query.filter_by(slug=slug, is_active=True).first_or_404()
    
    try:
        from app.services.lab_orchestrator import stop_lab_instance
        
        success, message = stop_lab_instance(user_id=current_user.id, lab_id=lab.id)
        
        if success:
            flash('Lab stopped successfully.', 'success')
        else:
            flash(f'Failed to stop lab: {message}', 'danger')
            
    except ImportError:
        flash('Docker is not available.', 'warning')
    except Exception as e:
        flash(f'Error stopping lab: {str(e)}', 'danger')
    
    return redirect(url_for('labs.lab_detail', slug=slug))


@labs_bp.route('/<slug>/status')
@login_required
def lab_status(slug):
    """Get lab instance status via AJAX"""
    lab = Lab.query.filter_by(slug=slug, is_active=True).first_or_404()
    
    instance = LabInstance.query.filter_by(
        user_id=current_user.id,
        lab_id=lab.id,
        status='running'
    ).first()
    
    if instance:
        return jsonify({
            'running': True,
            'url': instance.lab_url,
            'port': instance.port,
            'expires_at': instance.expires_at.isoformat() if instance.expires_at else None
        })
    
    return jsonify({'running': False})
