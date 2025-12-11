#!/usr/bin/env python3
"""
Seed default achievements for the platform.
"""

import json
from app import create_app
from app.extensions import db
from app.models import Achievement

def seed_achievements():
    """Seed default achievements."""
    app = create_app()
    
    with app.app_context():
        print("Seeding achievements...")
        
        achievements_data = [
            # First Steps
            {
                'name': 'First Step',
                'slug': 'first-step',
                'description': 'Complete your first lesson',
                'achievement_type': 'first_lesson',
                'criteria': json.dumps({'lessons_completed': 1}),
                'points': 10,
                'category': 'learning',
                'difficulty': 'bronze',
                'icon_class': 'fas fa-shoe-prints'
            },
            {
                'name': 'Python Novice',
                'slug': 'python-novice',
                'description': 'Enroll in your first Python course',
                'achievement_type': 'first_python_enrollment',
                'criteria': json.dumps({'course_type': 'python', 'enrollments': 1}),
                'points': 15,
                'category': 'learning',
                'difficulty': 'bronze',
                'icon_class': 'fab fa-python'
            },
            {
                'name': 'SQL Explorer',
                'slug': 'sql-explorer',
                'description': 'Enroll in your first SQL course',
                'achievement_type': 'first_sql_enrollment',
                'criteria': json.dumps({'course_type': 'sql', 'enrollments': 1}),
                'points': 15,
                'category': 'learning',
                'difficulty': 'bronze',
                'icon_class': 'fas fa-database'
            },
            
            # Course Completion
            {
                'name': 'Course Graduate',
                'slug': 'course-graduate',
                'description': 'Complete your first course',
                'achievement_type': 'first_course_completion',
                'criteria': json.dumps({'courses_completed': 1}),
                'points': 50,
                'category': 'learning',
                'difficulty': 'silver',
                'icon_class': 'fas fa-graduation-cap'
            },
            {
                'name': 'Python Master',
                'slug': 'python-master',
                'description': 'Complete 3 Python courses',
                'achievement_type': 'python_courses_completed',
                'criteria': json.dumps({'course_type': 'python', 'courses_completed': 3}),
                'points': 150,
                'category': 'mastery',
                'difficulty': 'gold',
                'icon_class': 'fab fa-python'
            },
            {
                'name': 'SQL Guru',
                'slug': 'sql-guru',
                'description': 'Complete 3 SQL courses',
                'achievement_type': 'sql_courses_completed',
                'criteria': json.dumps({'course_type': 'sql', 'courses_completed': 3}),
                'points': 150,
                'category': 'mastery',
                'difficulty': 'gold',
                'icon_class': 'fas fa-database'
            },
            {
                'name': 'Full-Stack Learner',
                'slug': 'full-stack-learner',
                'description': 'Complete at least 1 Python and 1 SQL course',
                'achievement_type': 'full_stack',
                'criteria': json.dumps({'python_courses': 1, 'sql_courses': 1}),
                'points': 100,
                'category': 'mastery',
                'difficulty': 'gold',
                'icon_class': 'fas fa-layer-group'
            },
            
            # Exercise Achievements
            {
                'name': 'Problem Solver',
                'slug': 'problem-solver',
                'description': 'Complete 10 exercises',
                'achievement_type': 'exercises_completed',
                'criteria': json.dumps({'exercises_completed': 10}),
                'points': 30,
                'category': 'learning',
                'difficulty': 'bronze',
                'icon_class': 'fas fa-puzzle-piece'
            },
            {
                'name': 'Code Warrior',
                'slug': 'code-warrior',
                'description': 'Complete 50 exercises',
                'achievement_type': 'exercises_completed',
                'criteria': json.dumps({'exercises_completed': 50}),
                'points': 100,
                'category': 'learning',
                'difficulty': 'silver',
                'icon_class': 'fas fa-code'
            },
            {
                'name': 'Exercise Master',
                'slug': 'exercise-master',
                'description': 'Complete 100 exercises',
                'achievement_type': 'exercises_completed',
                'criteria': json.dumps({'exercises_completed': 100}),
                'points': 200,
                'category': 'mastery',
                'difficulty': 'gold',
                'icon_class': 'fas fa-trophy'
            },
            
            # Streak Achievements
            {
                'name': 'Consistent Learner',
                'slug': 'consistent-learner',
                'description': 'Maintain a 7-day learning streak',
                'achievement_type': 'learning_streak',
                'criteria': json.dumps({'streak_days': 7}),
                'points': 50,
                'category': 'learning',
                'difficulty': 'silver',
                'icon_class': 'fas fa-fire'
            },
            {
                'name': 'Dedication',
                'slug': 'dedication',
                'description': 'Maintain a 30-day learning streak',
                'achievement_type': 'learning_streak',
                'criteria': json.dumps({'streak_days': 30}),
                'points': 150,
                'category': 'learning',
                'difficulty': 'gold',
                'icon_class': 'fas fa-fire-alt'
            },
            {
                'name': 'Unstoppable',
                'slug': 'unstoppable',
                'description': 'Maintain a 100-day learning streak',
                'achievement_type': 'learning_streak',
                'criteria': json.dumps({'streak_days': 100}),
                'points': 500,
                'category': 'mastery',
                'difficulty': 'platinum',
                'icon_class': 'fas fa-infinity'
            },
            
            # Quiz Achievements
            {
                'name': 'Quiz Master',
                'slug': 'quiz-master',
                'description': 'Pass 10 quizzes',
                'achievement_type': 'quizzes_passed',
                'criteria': json.dumps({'quizzes_passed': 10}),
                'points': 50,
                'category': 'learning',
                'difficulty': 'silver',
                'icon_class': 'fas fa-clipboard-check'
            },
            {
                'name': 'Perfect Score',
                'slug': 'perfect-score',
                'description': 'Get 100% on a quiz',
                'achievement_type': 'quiz_perfect_score',
                'criteria': json.dumps({'score': 100}),
                'points': 30,
                'category': 'learning',
                'difficulty': 'silver',
                'icon_class': 'fas fa-star'
            },
            
            # Social Achievements
            {
                'name': 'Reviewer',
                'slug': 'reviewer',
                'description': 'Write your first course review',
                'achievement_type': 'first_review',
                'criteria': json.dumps({'reviews_written': 1}),
                'points': 10,
                'category': 'social',
                'difficulty': 'bronze',
                'icon_class': 'fas fa-comment'
            },
            {
                'name': 'Helpful Reviewer',
                'slug': 'helpful-reviewer',
                'description': 'Write 5 course reviews',
                'achievement_type': 'reviews_written',
                'criteria': json.dumps({'reviews_written': 5}),
                'points': 50,
                'category': 'social',
                'difficulty': 'silver',
                'icon_class': 'fas fa-comments'
            },
            
            # Time-based Achievements
            {
                'name': 'Speed Learner',
                'slug': 'speed-learner',
                'description': 'Complete a course in under 7 days',
                'achievement_type': 'quick_completion',
                'criteria': json.dumps({'days': 7}),
                'points': 75,
                'category': 'mastery',
                'difficulty': 'gold',
                'icon_class': 'fas fa-bolt'
            },
            {
                'name': 'Night Owl',
                'slug': 'night-owl',
                'description': 'Complete 10 lessons after 10 PM',
                'achievement_type': 'late_night_learning',
                'criteria': json.dumps({'lessons_after_10pm': 10}),
                'points': 25,
                'category': 'learning',
                'difficulty': 'bronze',
                'icon_class': 'fas fa-moon',
                'is_hidden': True
            },
            {
                'name': 'Early Bird',
                'slug': 'early-bird',
                'description': 'Complete 10 lessons before 7 AM',
                'achievement_type': 'early_morning_learning',
                'criteria': json.dumps({'lessons_before_7am': 10}),
                'points': 25,
                'category': 'learning',
                'difficulty': 'bronze',
                'icon_class': 'fas fa-sun',
                'is_hidden': True
            },
        ]
        
        # Add achievements
        for achievement_data in achievements_data:
            existing = Achievement.query.filter_by(slug=achievement_data['slug']).first()
            if not existing:
                achievement = Achievement(**achievement_data)
                db.session.add(achievement)
                print(f"✓ Added achievement: {achievement.name}")
            else:
                print(f"⊘ Achievement already exists: {achievement_data['name']}")
        
        db.session.commit()
        print(f"\n✅ Seeded {len(achievements_data)} achievements!")

if __name__ == '__main__':
    seed_achievements()
