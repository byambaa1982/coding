"""
Achievement tracking and unlocking utilities.
"""

import json
from datetime import datetime
from app.extensions import db
from app.models import (
    Achievement, UserAchievement, TutorialEnrollment,
    LessonProgress, ExerciseSubmission, QuizAttempt,
    Review, LearningStreak, NewTutorial, Notification
)


def check_and_unlock_achievements(user_id, trigger_type=None, context=None):
    """
    Check and unlock achievements for a user.
    
    Args:
        user_id: User ID
        trigger_type: Type of action that triggered the check
        context: Additional context dict
    
    Returns:
        list: List of newly unlocked achievements
    """
    newly_unlocked = []
    
    # Get all active achievements
    achievements = Achievement.query.filter_by(is_active=True).all()
    
    for achievement in achievements:
        # Skip if already unlocked
        user_achievement = UserAchievement.query.filter_by(
            user_id=user_id,
            achievement_id=achievement.id
        ).first()
        
        if user_achievement and user_achievement.is_unlocked:
            continue
        
        # Check if criteria is met
        is_met, progress_current, progress_target = check_achievement_criteria(
            user_id, achievement, context
        )
        
        if not user_achievement:
            # Create new user achievement record
            user_achievement = UserAchievement(
                user_id=user_id,
                achievement_id=achievement.id,
                progress_current=progress_current,
                progress_target=progress_target
            )
            db.session.add(user_achievement)
        else:
            # Update progress
            user_achievement.progress_current = progress_current
            user_achievement.progress_target = progress_target
        
        # Unlock if criteria met
        if is_met and not user_achievement.is_unlocked:
            user_achievement.is_unlocked = True
            user_achievement.unlocked_at = datetime.utcnow()
            newly_unlocked.append(achievement)
            
            # Create notification
            create_achievement_notification(user_id, achievement)
    
    db.session.commit()
    return newly_unlocked


def check_achievement_criteria(user_id, achievement, context=None):
    """
    Check if achievement criteria is met.
    
    Returns:
        tuple: (is_met: bool, progress_current: int, progress_target: int)
    """
    criteria = json.loads(achievement.criteria) if achievement.criteria else {}
    achievement_type = achievement.achievement_type
    
    # First lesson
    if achievement_type == 'first_lesson':
        count = LessonProgress.query.filter_by(
            user_id=user_id,
            is_completed=True
        ).count()
        target = criteria.get('lessons_completed', 1)
        return count >= target, count, target
    
    # First Python enrollment
    elif achievement_type == 'first_python_enrollment':
        count = TutorialEnrollment.query.join(NewTutorial).filter(
            TutorialEnrollment.user_id == user_id,
            NewTutorial.course_type == 'python'
        ).count()
        target = criteria.get('enrollments', 1)
        return count >= target, count, target
    
    # First SQL enrollment
    elif achievement_type == 'first_sql_enrollment':
        count = TutorialEnrollment.query.join(NewTutorial).filter(
            TutorialEnrollment.user_id == user_id,
            NewTutorial.course_type == 'sql'
        ).count()
        target = criteria.get('enrollments', 1)
        return count >= target, count, target
    
    # Course completion
    elif achievement_type == 'first_course_completion':
        count = TutorialEnrollment.query.filter_by(
            user_id=user_id,
            is_completed=True
        ).count()
        target = criteria.get('courses_completed', 1)
        return count >= target, count, target
    
    # Python courses completed
    elif achievement_type == 'python_courses_completed':
        count = TutorialEnrollment.query.join(NewTutorial).filter(
            TutorialEnrollment.user_id == user_id,
            TutorialEnrollment.is_completed == True,
            NewTutorial.course_type == 'python'
        ).count()
        target = criteria.get('courses_completed', 3)
        return count >= target, count, target
    
    # SQL courses completed
    elif achievement_type == 'sql_courses_completed':
        count = TutorialEnrollment.query.join(NewTutorial).filter(
            TutorialEnrollment.user_id == user_id,
            TutorialEnrollment.is_completed == True,
            NewTutorial.course_type == 'sql'
        ).count()
        target = criteria.get('courses_completed', 3)
        return count >= target, count, target
    
    # Full-stack learner
    elif achievement_type == 'full_stack':
        python_count = TutorialEnrollment.query.join(NewTutorial).filter(
            TutorialEnrollment.user_id == user_id,
            TutorialEnrollment.is_completed == True,
            NewTutorial.course_type == 'python'
        ).count()
        sql_count = TutorialEnrollment.query.join(NewTutorial).filter(
            TutorialEnrollment.user_id == user_id,
            TutorialEnrollment.is_completed == True,
            NewTutorial.course_type == 'sql'
        ).count()
        python_target = criteria.get('python_courses', 1)
        sql_target = criteria.get('sql_courses', 1)
        is_met = python_count >= python_target and sql_count >= sql_target
        progress = min(python_count, python_target) + min(sql_count, sql_target)
        target = python_target + sql_target
        return is_met, progress, target
    
    # Exercises completed
    elif achievement_type == 'exercises_completed':
        # Count unique exercises passed
        count = ExerciseSubmission.query.filter_by(
            user_id=user_id,
            status='passed'
        ).distinct(ExerciseSubmission.exercise_id).count()
        target = criteria.get('exercises_completed', 10)
        return count >= target, count, target
    
    # Learning streak
    elif achievement_type == 'learning_streak':
        streak = LearningStreak.query.filter_by(user_id=user_id).first()
        current_streak = streak.current_streak if streak else 0
        target = criteria.get('streak_days', 7)
        return current_streak >= target, current_streak, target
    
    # Quizzes passed
    elif achievement_type == 'quizzes_passed':
        count = QuizAttempt.query.filter_by(
            user_id=user_id,
            passed=True
        ).distinct(QuizAttempt.quiz_id).count()
        target = criteria.get('quizzes_passed', 10)
        return count >= target, count, target
    
    # Perfect quiz score
    elif achievement_type == 'quiz_perfect_score':
        perfect_count = QuizAttempt.query.filter_by(
            user_id=user_id,
            score=100.00,
            status='completed'
        ).count()
        target = 1
        return perfect_count >= target, perfect_count, target
    
    # First review
    elif achievement_type == 'first_review':
        count = Review.query.filter_by(user_id=user_id).count()
        target = criteria.get('reviews_written', 1)
        return count >= target, count, target
    
    # Reviews written
    elif achievement_type == 'reviews_written':
        count = Review.query.filter_by(user_id=user_id).count()
        target = criteria.get('reviews_written', 5)
        return count >= target, count, target
    
    # Default: not met
    return False, 0, 1


def create_achievement_notification(user_id, achievement):
    """Create notification for unlocked achievement."""
    notification = Notification(
        user_id=user_id,
        notification_type='achievement',
        title=f'Achievement Unlocked: {achievement.name}!',
        message=achievement.description,
        action_url='/account/achievements',
        action_text='View Achievements',
        icon_class=achievement.icon_class or 'fas fa-trophy',
        priority='normal',
        related_type='achievement',
        related_id=achievement.id
    )
    db.session.add(notification)


def get_user_achievements(user_id, include_locked=True):
    """
    Get all achievements for a user.
    
    Args:
        user_id: User ID
        include_locked: Include locked achievements
    
    Returns:
        dict: Achievements organized by category
    """
    # Get all achievements
    all_achievements = Achievement.query.filter_by(
        is_active=True,
        is_hidden=False
    ).all()
    
    # Get user achievement records
    user_achievements = UserAchievement.query.filter_by(user_id=user_id).all()
    user_achievement_map = {ua.achievement_id: ua for ua in user_achievements}
    
    # Organize by category
    achievements_by_category = {}
    
    for achievement in all_achievements:
        category = achievement.category or 'other'
        if category not in achievements_by_category:
            achievements_by_category[category] = []
        
        # Get user progress
        user_achievement = user_achievement_map.get(achievement.id)
        
        achievement_data = {
            'achievement': achievement,
            'is_unlocked': user_achievement.is_unlocked if user_achievement else False,
            'unlocked_at': user_achievement.unlocked_at if user_achievement else None,
            'progress_current': user_achievement.progress_current if user_achievement else 0,
            'progress_target': user_achievement.progress_target if user_achievement else 1,
            'progress_percentage': (
                (user_achievement.progress_current / user_achievement.progress_target * 100)
                if user_achievement and user_achievement.progress_target > 0
                else 0
            )
        }
        
        # Only include if unlocked or if we want to show locked
        if achievement_data['is_unlocked'] or include_locked:
            achievements_by_category[category].append(achievement_data)
    
    return achievements_by_category


def get_achievement_stats(user_id):
    """
    Get achievement statistics for a user.
    
    Returns:
        dict: Achievement statistics
    """
    total_achievements = Achievement.query.filter_by(
        is_active=True,
        is_hidden=False
    ).count()
    
    unlocked_achievements = UserAchievement.query.filter_by(
        user_id=user_id,
        is_unlocked=True
    ).count()
    
    total_points = db.session.query(db.func.sum(Achievement.points)).join(
        UserAchievement
    ).filter(
        UserAchievement.user_id == user_id,
        UserAchievement.is_unlocked == True
    ).scalar() or 0
    
    return {
        'total_achievements': total_achievements,
        'unlocked_achievements': unlocked_achievements,
        'locked_achievements': total_achievements - unlocked_achievements,
        'completion_percentage': round((unlocked_achievements / total_achievements * 100), 1) if total_achievements > 0 else 0,
        'total_points': int(total_points)
    }


def trigger_achievement_check(user_id, event_type, **kwargs):
    """
    Convenience function to trigger achievement check after events.
    
    Args:
        user_id: User ID
        event_type: Type of event (lesson_completed, course_completed, etc.)
        **kwargs: Additional context
    """
    context = {'event_type': event_type, **kwargs}
    return check_and_unlock_achievements(user_id, event_type, context)
