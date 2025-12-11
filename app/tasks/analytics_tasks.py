# app/tasks/analytics_tasks.py
"""Celery tasks for analytics and maintenance."""

from datetime import datetime, timedelta
from app.celery_app import celery


@celery.task(name='app.tasks.analytics_tasks.update_user_statistics')
def update_user_statistics():
    """Update user learning statistics."""
    from app import create_app
    from app.extensions import db
    from app.models import TutorialUser, ExerciseSubmission, LessonProgress
    from sqlalchemy import func
    
    app = create_app()
    
    with app.app_context():
        try:
            # This is a placeholder - implement actual statistics update logic
            users = TutorialUser.query.filter_by(is_active=True).all()
            
            for user in users:
                # Count submissions
                submission_count = ExerciseSubmission.query.filter_by(
                    user_id=user.id
                ).count()
                
                # Count passed exercises
                passed_count = ExerciseSubmission.query.filter_by(
                    user_id=user.id,
                    status='passed'
                ).count()
                
                # Count completed lessons
                completed_lessons = LessonProgress.query.filter_by(
                    user_id=user.id,
                    is_completed=True
                ).count()
                
                # Store statistics (would need a UserStatistics model)
                # For now, just log
                print(f'User {user.id}: {submission_count} submissions, {passed_count} passed, {completed_lessons} lessons')
            
            return {'status': 'success', 'users_processed': len(users)}
            
        except Exception as e:
            print(f'Error updating user statistics: {str(e)}')
            return {'status': 'error', 'error': str(e)}


@celery.task(name='app.tasks.analytics_tasks.cleanup_old_submissions')
def cleanup_old_submissions(days=90):
    """
    Clean up old submission records.
    
    Args:
        days: Delete submissions older than this many days
    """
    from app import create_app
    from app.extensions import db
    from app.models import ExerciseSubmission
    
    app = create_app()
    
    with app.app_context():
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Delete old failed submissions (keep passed ones)
            deleted = ExerciseSubmission.query.filter(
                ExerciseSubmission.submitted_at < cutoff_date,
                ExerciseSubmission.status != 'passed'
            ).delete()
            
            db.session.commit()
            
            return {'status': 'success', 'deleted': deleted}
            
        except Exception as e:
            db.session.rollback()
            print(f'Error cleaning up submissions: {str(e)}')
            return {'status': 'error', 'error': str(e)}


@celery.task(name='app.tasks.analytics_tasks.generate_daily_report')
def generate_daily_report():
    """Generate daily analytics report."""
    from app import create_app
    from app.extensions import db
    from app.models import ExerciseSubmission, TutorialUser, TutorialEnrollment
    from sqlalchemy import func
    from datetime import datetime, timedelta
    
    app = create_app()
    
    with app.app_context():
        try:
            today = datetime.utcnow().date()
            yesterday = today - timedelta(days=1)
            
            # Count new users
            new_users = TutorialUser.query.filter(
                func.date(TutorialUser.created_at) == yesterday
            ).count()
            
            # Count new enrollments
            new_enrollments = TutorialEnrollment.query.filter(
                func.date(TutorialEnrollment.enrolled_at) == yesterday
            ).count()
            
            # Count submissions
            submissions = ExerciseSubmission.query.filter(
                func.date(ExerciseSubmission.submitted_at) == yesterday
            ).count()
            
            report = {
                'date': yesterday.isoformat(),
                'new_users': new_users,
                'new_enrollments': new_enrollments,
                'submissions': submissions
            }
            
            print(f'Daily report for {yesterday}: {report}')
            
            return {'status': 'success', 'report': report}
            
        except Exception as e:
            print(f'Error generating daily report: {str(e)}')
            return {'status': 'error', 'error': str(e)}
