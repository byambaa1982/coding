"""
Analytics utilities for tracking user learning statistics.
"""

from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
from app.extensions import db
from app.models import (
    UserAnalytics, LearningStreak, TutorialEnrollment,
    LessonProgress, ExerciseSubmission, QuizAttempt,
    NewTutorial, UserAchievement, Achievement
)


def get_or_create_user_analytics(user_id):
    """Get or create UserAnalytics record for user."""
    analytics = UserAnalytics.query.filter_by(user_id=user_id).first()
    if not analytics:
        analytics = UserAnalytics(user_id=user_id)
        db.session.add(analytics)
        db.session.commit()
    return analytics


def get_or_create_learning_streak(user_id):
    """Get or create LearningStreak record for user."""
    streak = LearningStreak.query.filter_by(user_id=user_id).first()
    if not streak:
        streak = LearningStreak(user_id=user_id)
        db.session.add(streak)
        db.session.commit()
    return streak


def update_user_analytics(user_id):
    """
    Update all analytics for a user.
    Call this after significant user actions.
    """
    analytics = get_or_create_user_analytics(user_id)
    
    # Get enrollments
    enrollments = TutorialEnrollment.query.filter_by(user_id=user_id).all()
    
    # Basic counts
    analytics.total_courses_enrolled = len(enrollments)
    analytics.total_courses_completed = sum(1 for e in enrollments if e.is_completed)
    
    # Lesson progress
    lesson_progress_count = LessonProgress.query.filter_by(
        user_id=user_id,
        is_completed=True
    ).count()
    analytics.total_lessons_completed = lesson_progress_count
    
    # Exercise stats
    passed_exercises = ExerciseSubmission.query.filter_by(
        user_id=user_id,
        status='passed'
    ).distinct(ExerciseSubmission.exercise_id).count()
    analytics.total_exercises_completed = passed_exercises
    
    # Quiz stats
    passed_quizzes = QuizAttempt.query.filter_by(
        user_id=user_id,
        passed=True
    ).distinct(QuizAttempt.quiz_id).count()
    analytics.total_quizzes_completed = passed_quizzes
    
    # Average quiz score
    avg_score = db.session.query(func.avg(QuizAttempt.score)).filter_by(
        user_id=user_id,
        status='completed'
    ).scalar()
    analytics.average_quiz_score = round(float(avg_score), 2) if avg_score else 0.00
    
    # Exercise success rate
    total_submissions = ExerciseSubmission.query.filter_by(user_id=user_id).count()
    passed_submissions = ExerciseSubmission.query.filter_by(user_id=user_id, status='passed').count()
    if total_submissions > 0:
        analytics.average_exercise_success_rate = round((passed_submissions / total_submissions) * 100, 2)
    
    # Course type breakdown
    python_completed = TutorialEnrollment.query.join(NewTutorial).filter(
        TutorialEnrollment.user_id == user_id,
        TutorialEnrollment.is_completed == True,
        NewTutorial.course_type == 'python'
    ).count()
    analytics.python_courses_completed = python_completed
    
    sql_completed = TutorialEnrollment.query.join(NewTutorial).filter(
        TutorialEnrollment.user_id == user_id,
        TutorialEnrollment.is_completed == True,
        NewTutorial.course_type == 'sql'
    ).count()
    analytics.sql_courses_completed = sql_completed
    
    # Learning time calculations
    total_time = db.session.query(func.sum(LessonProgress.time_spent_seconds)).filter_by(
        user_id=user_id
    ).scalar()
    if total_time:
        analytics.total_learning_time_minutes = int(total_time / 60)
    
    # Calculate time windows
    now = datetime.utcnow()
    seven_days_ago = now - timedelta(days=7)
    thirty_days_ago = now - timedelta(days=30)
    
    last_7_days = db.session.query(func.sum(LessonProgress.time_spent_seconds)).filter(
        LessonProgress.user_id == user_id,
        LessonProgress.last_accessed_at >= seven_days_ago
    ).scalar()
    analytics.last_7_days_time_minutes = int(last_7_days / 60) if last_7_days else 0
    
    last_30_days = db.session.query(func.sum(LessonProgress.time_spent_seconds)).filter(
        LessonProgress.user_id == user_id,
        LessonProgress.last_accessed_at >= thirty_days_ago
    ).scalar()
    analytics.last_30_days_time_minutes = int(last_30_days / 60) if last_30_days else 0
    
    # Days active
    unique_days = db.session.query(func.date(LessonProgress.last_accessed_at)).filter_by(
        user_id=user_id
    ).distinct().count()
    analytics.days_active = unique_days
    
    # Average daily time
    if analytics.days_active > 0:
        analytics.avg_daily_time_minutes = int(analytics.total_learning_time_minutes / analytics.days_active)
    
    # Points from achievements
    total_points = db.session.query(func.sum(Achievement.points)).join(
        UserAchievement, Achievement.id == UserAchievement.achievement_id
    ).filter(
        UserAchievement.user_id == user_id,
        UserAchievement.is_unlocked == True
    ).scalar()
    analytics.total_points_earned = int(total_points) if total_points else 0
    
    db.session.commit()
    return analytics


def get_dashboard_stats(user_id):
    """
    Get dashboard statistics for a user.
    
    Returns:
        dict: Dashboard statistics
    """
    analytics = get_or_create_user_analytics(user_id)
    streak = get_or_create_learning_streak(user_id)
    
    # Get recent activity
    recent_completions = LessonProgress.query.filter_by(
        user_id=user_id,
        is_completed=True
    ).order_by(LessonProgress.completed_at.desc()).limit(5).all()
    
    # Get active enrollments
    active_enrollments = TutorialEnrollment.query.filter_by(
        user_id=user_id,
        status='active',
        is_completed=False
    ).order_by(TutorialEnrollment.enrolled_at.desc()).all()
    
    # Get unlocked achievements (recent)
    recent_achievements = UserAchievement.query.filter_by(
        user_id=user_id,
        is_unlocked=True
    ).order_by(UserAchievement.unlocked_at.desc()).limit(3).all()
    
    return {
        'analytics': analytics,
        'streak': streak,
        'recent_completions': recent_completions,
        'active_enrollments': active_enrollments,
        'recent_achievements': recent_achievements,
        'completion_rate': calculate_completion_rate(user_id),
        'weekly_progress': get_weekly_progress(user_id),
    }


def calculate_completion_rate(user_id):
    """Calculate overall course completion rate."""
    total_enrolled = TutorialEnrollment.query.filter_by(user_id=user_id).count()
    if total_enrolled == 0:
        return 0
    
    completed = TutorialEnrollment.query.filter_by(
        user_id=user_id,
        is_completed=True
    ).count()
    
    return round((completed / total_enrolled) * 100, 1)


def get_weekly_progress(user_id):
    """
    Get progress for the last 7 days.
    
    Returns:
        list: List of dicts with date and minutes learned
    """
    now = datetime.utcnow()
    weekly_data = []
    
    for i in range(6, -1, -1):
        date = (now - timedelta(days=i)).date()
        
        # Get time spent on this date
        time_spent = db.session.query(func.sum(LessonProgress.time_spent_seconds)).filter(
            LessonProgress.user_id == user_id,
            func.date(LessonProgress.last_accessed_at) == date
        ).scalar()
        
        minutes = int(time_spent / 60) if time_spent else 0
        
        weekly_data.append({
            'date': date.strftime('%a'),  # Mon, Tue, etc.
            'minutes': minutes
        })
    
    return weekly_data


def get_learning_insights(user_id):
    """
    Generate personalized learning insights.
    
    Returns:
        list: List of insight strings
    """
    insights = []
    analytics = get_or_create_user_analytics(user_id)
    streak = get_or_create_learning_streak(user_id)
    
    # Streak insights
    if streak.current_streak >= 7:
        insights.append(f"🔥 Amazing! You're on a {streak.current_streak}-day learning streak!")
    elif streak.current_streak >= 3:
        insights.append(f"🔥 Great job! {streak.current_streak} days in a row!")
    
    # Time insights
    if analytics.last_7_days_time_minutes > 0:
        daily_avg = analytics.last_7_days_time_minutes / 7
        insights.append(f"📚 You've averaged {int(daily_avg)} minutes of learning per day this week.")
    
    # Progress insights
    if analytics.total_courses_completed > 0:
        insights.append(f"🎓 You've completed {analytics.total_courses_completed} course(s)! Keep it up!")
    
    # Exercise insights
    if analytics.average_exercise_success_rate > 80:
        insights.append(f"💪 Your exercise success rate is {analytics.average_exercise_success_rate}%! Excellent work!")
    
    # Quiz insights
    if analytics.average_quiz_score >= 90:
        insights.append(f"⭐ Your average quiz score is {analytics.average_quiz_score}%! You're mastering the material!")
    
    # Recommendations
    active_enrollments = TutorialEnrollment.query.filter_by(
        user_id=user_id,
        status='active',
        is_completed=False
    ).count()
    
    if active_enrollments == 0 and analytics.total_courses_completed > 0:
        insights.append("💡 Ready for your next challenge? Browse our course catalog!")
    
    return insights


def track_lesson_time(user_id, lesson_id, enrollment_id, seconds_spent):
    """
    Track time spent on a lesson.
    
    Args:
        user_id: User ID
        lesson_id: Lesson ID
        enrollment_id: Enrollment ID
        seconds_spent: Time spent in seconds
    """
    progress = LessonProgress.query.filter_by(
        user_id=user_id,
        lesson_id=lesson_id
    ).first()
    
    if not progress:
        progress = LessonProgress(
            user_id=user_id,
            lesson_id=lesson_id,
            enrollment_id=enrollment_id
        )
        db.session.add(progress)
    
    progress.time_spent_seconds += seconds_spent
    progress.last_accessed_at = datetime.utcnow()
    
    db.session.commit()
    
    # Update streak
    streak = get_or_create_learning_streak(user_id)
    streak.update_streak()
