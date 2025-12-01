"""
WebNoX - Web Application Security Training Platform
Run script for development
"""
from app import create_app, db
from app.models import User, Course, Lesson, Lab, LabSubmission, UserProgress, UserScore

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Course': Course,
        'Lesson': Lesson,
        'Lab': Lab,
        'LabSubmission': LabSubmission,
        'UserProgress': UserProgress,
        'UserScore': UserScore
    }

if __name__ == '__main__':
    import os
    debug = os.environ.get('FLASK_ENV', 'production') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=5000, use_reloader=False)
