# app/account/utils.py
"""Utility functions for account management."""

import logging
from datetime import datetime
from flask import url_for
from app.models import (
    TutorialEnrollment, Lesson, Exercise, LessonProgress, ExerciseSubmission
)
from app.extensions import db

logger = logging.getLogger(__name__)


def get_continue_learning_destination(user_id, enrollment_id):
    """
    Determine where user should continue learning.
    
    Args:
        user_id: ID of the user
        enrollment_id: ID of the enrollment
    
    Returns:
        dict with keys: 'type', 'id', 'url'
        Examples:
        - {'type': 'lesson', 'id': 5, 'url': '/learning/lesson/5'}
        - {'type': 'exercise', 'id': 12, 'url': '/practice/exercise/12'}
    """
    
    # 1. Get enrollment record with eager loading
    enrollment = TutorialEnrollment.query\
        .options(
            db.joinedload(TutorialEnrollment.tutorial),
            db.joinedload(TutorialEnrollment.last_accessed_lesson)
        )\
        .filter_by(id=enrollment_id)\
        .first()
    
    if not enrollment:
        logger.error(f"Enrollment {enrollment_id} not found")
        return {'type': 'catalog', 'url': url_for('catalog.index')}
    
    # 2. Determine current lesson
    current_lesson = None
    if enrollment.last_accessed_lesson_id:
        current_lesson = enrollment.last_accessed_lesson
    
    if not current_lesson:
        # Start from beginning
        current_lesson = Lesson.query.filter_by(
            tutorial_id=enrollment.tutorial_id
        ).order_by(Lesson.order_index).first()
    
    if not current_lesson:
        logger.warning(f"No lessons found for tutorial {enrollment.tutorial_id}")
        return {
            'type': 'catalog',
            'url': url_for('catalog.course_detail', slug=enrollment.tutorial.slug)
        }
    
    # 3. Check if current lesson is completed
    lesson_progress = LessonProgress.query.filter_by(
        user_id=user_id,
        lesson_id=current_lesson.id
    ).first()
    
    if lesson_progress and lesson_progress.is_completed:
        # Move to next lesson
        next_lesson = Lesson.query.filter(
            Lesson.tutorial_id == enrollment.tutorial_id,
            Lesson.order_index > current_lesson.order_index
        ).order_by(Lesson.order_index).first()
        
        if next_lesson:
            current_lesson = next_lesson
        else:
            # Course completed!
            logger.info(f"User {user_id} completed course {enrollment.tutorial_id}")
            return {
                'type': 'completion',
                'url': url_for('catalog.course_detail', slug=enrollment.tutorial.slug)
            }
    
    # 4. Check for exercises in current lesson
    exercises = Exercise.query.filter_by(
        lesson_id=current_lesson.id
    ).order_by(Exercise.order_index).all()
    
    if exercises:
        # Find first incomplete exercise
        for exercise in exercises:
            submission = ExerciseSubmission.query.filter_by(
                user_id=user_id,
                exercise_id=exercise.id,
                status='passed'
            ).first()
            
            if not submission:
                # Found incomplete exercise!
                logger.info(f"Routing user {user_id} to exercise {exercise.id}")
                
                # Determine practice route based on exercise type
                if exercise.exercise_type == 'python':
                    return {
                        'type': 'exercise',
                        'id': exercise.id,
                        'url': url_for('python_practice.view_exercise', exercise_id=exercise.id)
                    }
                elif exercise.exercise_type == 'sql':
                    return {
                        'type': 'exercise',
                        'id': exercise.id,
                        'url': url_for('sql_practice.view_exercise', exercise_id=exercise.id)
                    }
    
    # 5. All exercises completed (or no exercises), go to lesson
    logger.info(f"Routing user {user_id} to lesson {current_lesson.id}")
    return {
        'type': 'lesson',
        'id': current_lesson.id,
        'url': url_for('learning.view_lesson', lesson_id=current_lesson.id)
    }


def get_continue_learning_destination_optimized(user_id, enrollment_id):
    """
    Optimized version with fewer database queries.
    
    Args:
        user_id: ID of the user
        enrollment_id: ID of the enrollment
    
    Returns:
        dict with keys: 'type', 'id', 'url'
    """
    
    # Single query with eager loading
    enrollment = TutorialEnrollment.query\
        .options(
            db.joinedload(TutorialEnrollment.tutorial),
            db.joinedload(TutorialEnrollment.last_accessed_lesson)
        )\
        .filter_by(id=enrollment_id)\
        .first()
    
    if not enrollment:
        return {'type': 'catalog', 'url': url_for('catalog.index')}
    
    # Get all lesson progress in one query
    lesson_progress_map = {
        lp.lesson_id: lp 
        for lp in LessonProgress.query.filter_by(
            user_id=user_id,
            enrollment_id=enrollment_id
        ).all()
    }
    
    # Get all passed exercises in one query
    passed_exercises = {
        es.exercise_id 
        for es in ExerciseSubmission.query.filter_by(
            user_id=user_id,
            status='passed'
        ).all()
    }
    
    # Get all lessons for the tutorial
    lessons = Lesson.query.filter_by(
        tutorial_id=enrollment.tutorial_id
    ).order_by(Lesson.order_index).all()
    
    if not lessons:
        return {
            'type': 'catalog',
            'url': url_for('catalog.course_detail', slug=enrollment.tutorial.slug)
        }
    
    # Find current lesson
    current_lesson = None
    if enrollment.last_accessed_lesson_id:
        current_lesson = next(
            (l for l in lessons if l.id == enrollment.last_accessed_lesson_id),
            None
        )
    
    if not current_lesson:
        current_lesson = lessons[0]
    
    # Check if current lesson is completed
    current_progress = lesson_progress_map.get(current_lesson.id)
    if current_progress and current_progress.is_completed:
        # Find next lesson
        current_index = lessons.index(current_lesson)
        if current_index + 1 < len(lessons):
            current_lesson = lessons[current_index + 1]
        else:
            # Course completed
            return {
                'type': 'completion',
                'url': url_for('catalog.course_detail', slug=enrollment.tutorial.slug)
            }
    
    # Get exercises for current lesson
    exercises = Exercise.query.filter_by(
        lesson_id=current_lesson.id
    ).order_by(Exercise.order_index).all()
    
    # Find first incomplete exercise
    for exercise in exercises:
        if exercise.id not in passed_exercises:
            # Route based on exercise type
            if exercise.exercise_type == 'python':
                return {
                    'type': 'exercise',
                    'id': exercise.id,
                    'url': url_for('python_practice.view_exercise', exercise_id=exercise.id)
                }
            elif exercise.exercise_type == 'sql':
                return {
                    'type': 'exercise',
                    'id': exercise.id,
                    'url': url_for('sql_practice.view_exercise', exercise_id=exercise.id)
                }
    
    # Go to lesson content
    return {
        'type': 'lesson',
        'id': current_lesson.id,
        'url': url_for('learning.view_lesson', lesson_id=current_lesson.id)
    }
