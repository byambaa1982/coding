# app/learning/routes.py
"""Routes for learning interface - lesson viewing, progress tracking, quizzes."""

import json
from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from sqlalchemy import func
from app.learning import learning_bp
from app.extensions import db
from app.models import (
    NewTutorial, Lesson, Quiz, QuizQuestion, QuizAttempt, QuizAnswer,
    TutorialEnrollment, LessonProgress, Exercise
)


@learning_bp.route('/tutorial/<int:tutorial_id>')
@login_required
def tutorial_overview(tutorial_id):
    """Display tutorial overview with curriculum."""
    tutorial = NewTutorial.query.get_or_404(tutorial_id)
    
    # Check if user is enrolled
    enrollment = TutorialEnrollment.query.filter_by(
        user_id=current_user.id,
        tutorial_id=tutorial_id,
        status='active'
    ).first()
    
    if not enrollment:
        flash('You need to enroll in this course first.', 'warning')
        return redirect(url_for('catalog.course_detail', slug=tutorial.slug))
    
    # Get all lessons grouped by section
    lessons = Lesson.query.filter_by(tutorial_id=tutorial_id).order_by(Lesson.order_index).all()
    
    # Group lessons by section
    sections = {}
    for lesson in lessons:
        section_name = lesson.section_name or 'General'
        if section_name not in sections:
            sections[section_name] = []
        
        # Get progress for this lesson
        progress = LessonProgress.query.filter_by(
            user_id=current_user.id,
            lesson_id=lesson.id
        ).first()
        
        sections[section_name].append({
            'lesson': lesson,
            'progress': progress
        })
    
    return render_template('learning/tutorial_overview.html',
                         tutorial=tutorial,
                         enrollment=enrollment,
                         sections=sections)


@learning_bp.route('/lesson/<int:lesson_id>')
@login_required
def view_lesson(lesson_id):
    """View a specific lesson."""
    lesson = Lesson.query.get_or_404(lesson_id)
    tutorial = lesson.tutorial
    
    # Check enrollment
    enrollment = TutorialEnrollment.query.filter_by(
        user_id=current_user.id,
        tutorial_id=tutorial.id,
        status='active'
    ).first()
    
    if not enrollment:
        flash('You need to enroll in this course first.', 'warning')
        return redirect(url_for('catalog.course_detail', slug=tutorial.slug))
    
    # Get or create lesson progress
    progress = LessonProgress.query.filter_by(
        user_id=current_user.id,
        lesson_id=lesson_id
    ).first()
    
    if not progress:
        progress = LessonProgress(
            user_id=current_user.id,
            lesson_id=lesson_id,
            enrollment_id=enrollment.id
        )
        db.session.add(progress)
        db.session.commit()
    else:
        # Update last accessed time
        progress.last_accessed_at = datetime.utcnow()
        db.session.commit()
    
    # Get all lessons for navigation
    all_lessons = Lesson.query.filter_by(tutorial_id=tutorial.id).order_by(Lesson.order_index).all()
    
    # Find previous and next lessons
    current_index = next((i for i, l in enumerate(all_lessons) if l.id == lesson_id), -1)
    prev_lesson = all_lessons[current_index - 1] if current_index > 0 else None
    next_lesson = all_lessons[current_index + 1] if current_index < len(all_lessons) - 1 else None
    
    # Get exercises for this lesson
    exercises = Exercise.query.filter_by(lesson_id=lesson_id).order_by(Exercise.order_index).all()
    
    # Get quizzes for this lesson
    quizzes = Quiz.query.filter_by(lesson_id=lesson_id).order_by(Quiz.order_index).all()
    
    return render_template('learning/lesson.html',
                         lesson=lesson,
                         tutorial=tutorial,
                         enrollment=enrollment,
                         progress=progress,
                         prev_lesson=prev_lesson,
                         next_lesson=next_lesson,
                         exercises=exercises,
                         quizzes=quizzes)


@learning_bp.route('/lesson/<int:lesson_id>/mark-complete', methods=['POST'])
@login_required
def mark_lesson_complete(lesson_id):
    """Mark a lesson as complete."""
    lesson = Lesson.query.get_or_404(lesson_id)
    
    # Get enrollment
    enrollment = TutorialEnrollment.query.filter_by(
        user_id=current_user.id,
        tutorial_id=lesson.tutorial_id,
        status='active'
    ).first()
    
    if not enrollment:
        return jsonify({'success': False, 'message': 'Not enrolled'}), 403
    
    # Get or create progress
    progress = LessonProgress.query.filter_by(
        user_id=current_user.id,
        lesson_id=lesson_id
    ).first()
    
    if not progress:
        progress = LessonProgress(
            user_id=current_user.id,
            lesson_id=lesson_id,
            enrollment_id=enrollment.id
        )
        db.session.add(progress)
    
    # Mark as complete
    progress.mark_complete()
    
    return jsonify({
        'success': True,
        'message': 'Lesson marked as complete!',
        'progress_percentage': float(enrollment.progress_percentage)
    })


@learning_bp.route('/lesson/<int:lesson_id>/update-video-progress', methods=['POST'])
@login_required
def update_video_progress(lesson_id):
    """Update video playback progress."""
    lesson = Lesson.query.get_or_404(lesson_id)
    data = request.get_json()
    
    position = data.get('position', 0)
    duration = data.get('duration', 0)
    
    # Get enrollment
    enrollment = TutorialEnrollment.query.filter_by(
        user_id=current_user.id,
        tutorial_id=lesson.tutorial_id,
        status='active'
    ).first()
    
    if not enrollment:
        return jsonify({'success': False}), 403
    
    # Get or create progress
    progress = LessonProgress.query.filter_by(
        user_id=current_user.id,
        lesson_id=lesson_id
    ).first()
    
    if not progress:
        progress = LessonProgress(
            user_id=current_user.id,
            lesson_id=lesson_id,
            enrollment_id=enrollment.id
        )
        db.session.add(progress)
    
    # Update video progress
    progress.video_position_seconds = int(position)
    if duration > 0:
        progress.video_watched_percentage = (position / duration) * 100
        
        # Auto-complete if watched 90%+
        if progress.video_watched_percentage >= 90 and not progress.is_completed:
            progress.mark_complete()
    
    db.session.commit()
    
    return jsonify({'success': True})


@learning_bp.route('/lesson/<int:lesson_id>/bookmark', methods=['POST'])
@login_required
def toggle_bookmark(lesson_id):
    """Toggle lesson bookmark."""
    lesson = Lesson.query.get_or_404(lesson_id)
    
    # Get enrollment
    enrollment = TutorialEnrollment.query.filter_by(
        user_id=current_user.id,
        tutorial_id=lesson.tutorial_id,
        status='active'
    ).first()
    
    if not enrollment:
        return jsonify({'success': False}), 403
    
    # Get or create progress
    progress = LessonProgress.query.filter_by(
        user_id=current_user.id,
        lesson_id=lesson_id
    ).first()
    
    if not progress:
        progress = LessonProgress(
            user_id=current_user.id,
            lesson_id=lesson_id,
            enrollment_id=enrollment.id
        )
        db.session.add(progress)
    
    # Toggle bookmark
    progress.is_bookmarked = not progress.is_bookmarked
    db.session.commit()
    
    return jsonify({
        'success': True,
        'bookmarked': progress.is_bookmarked
    })


@learning_bp.route('/lesson/<int:lesson_id>/notes', methods=['POST'])
@login_required
def save_notes(lesson_id):
    """Save lesson notes."""
    lesson = Lesson.query.get_or_404(lesson_id)
    data = request.get_json()
    notes = data.get('notes', '')
    
    # Get enrollment
    enrollment = TutorialEnrollment.query.filter_by(
        user_id=current_user.id,
        tutorial_id=lesson.tutorial_id,
        status='active'
    ).first()
    
    if not enrollment:
        return jsonify({'success': False}), 403
    
    # Get or create progress
    progress = LessonProgress.query.filter_by(
        user_id=current_user.id,
        lesson_id=lesson_id
    ).first()
    
    if not progress:
        progress = LessonProgress(
            user_id=current_user.id,
            lesson_id=lesson_id,
            enrollment_id=enrollment.id
        )
        db.session.add(progress)
    
    # Save notes
    progress.notes = notes
    db.session.commit()
    
    return jsonify({'success': True})


@learning_bp.route('/quiz/<int:quiz_id>')
@login_required
def take_quiz(quiz_id):
    """Start or continue a quiz."""
    quiz = Quiz.query.get_or_404(quiz_id)
    lesson = quiz.lesson
    tutorial = quiz.tutorial
    
    # Check enrollment
    enrollment = TutorialEnrollment.query.filter_by(
        user_id=current_user.id,
        tutorial_id=tutorial.id,
        status='active'
    ).first()
    
    if not enrollment:
        flash('You need to enroll in this course first.', 'warning')
        return redirect(url_for('catalog.course_detail', slug=tutorial.slug))
    
    # Check if user has an in-progress attempt
    attempt = QuizAttempt.query.filter_by(
        user_id=current_user.id,
        quiz_id=quiz_id,
        status='in_progress'
    ).first()
    
    # Check attempt limit
    total_attempts = QuizAttempt.query.filter_by(
        user_id=current_user.id,
        quiz_id=quiz_id
    ).count()
    
    if not attempt:
        if quiz.max_attempts and total_attempts >= quiz.max_attempts:
            flash(f'You have reached the maximum number of attempts ({quiz.max_attempts}) for this quiz.', 'warning')
            return redirect(url_for('learning.quiz_results', quiz_id=quiz_id))
        
        # Create new attempt
        attempt = QuizAttempt(
            user_id=current_user.id,
            quiz_id=quiz_id,
            enrollment_id=enrollment.id,
            attempt_number=total_attempts + 1
        )
        db.session.add(attempt)
        db.session.commit()
    
    # Get questions
    questions = list(quiz.questions.order_by(QuizQuestion.order_index).all())
    
    # Shuffle if needed
    if quiz.shuffle_questions:
        import random
        random.shuffle(questions)
    
    # Get existing answers
    existing_answers = {
        answer.question_id: answer.user_answer
        for answer in attempt.answers
    }
    
    return render_template('learning/quiz.html',
                         quiz=quiz,
                         lesson=lesson,
                         tutorial=tutorial,
                         attempt=attempt,
                         questions=questions,
                         existing_answers=existing_answers)


@learning_bp.route('/quiz/<int:quiz_id>/submit', methods=['POST'])
@login_required
def submit_quiz(quiz_id):
    """Submit quiz answers."""
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Get current attempt
    attempt = QuizAttempt.query.filter_by(
        user_id=current_user.id,
        quiz_id=quiz_id,
        status='in_progress'
    ).first()
    
    if not attempt:
        flash('No active quiz attempt found.', 'error')
        return redirect(url_for('learning.take_quiz', quiz_id=quiz_id))
    
    # Get submitted answers
    answers_data = request.form.to_dict()
    
    # Process each question
    for question in quiz.questions:
        answer_key = f'question_{question.id}'
        user_answer = answers_data.get(answer_key, '').strip()
        
        # Check if answer exists
        existing_answer = QuizAnswer.query.filter_by(
            attempt_id=attempt.id,
            question_id=question.id
        ).first()
        
        if existing_answer:
            existing_answer.user_answer = user_answer
            existing_answer.is_correct = (user_answer.lower() == question.correct_answer.lower())
        else:
            answer = QuizAnswer(
                attempt_id=attempt.id,
                question_id=question.id,
                user_answer=user_answer,
                is_correct=(user_answer.lower() == question.correct_answer.lower())
            )
            db.session.add(answer)
    
    # Calculate elapsed time
    elapsed = datetime.utcnow() - attempt.started_at
    attempt.time_taken_seconds = int(elapsed.total_seconds())
    
    # Mark attempt as completed
    attempt.status = 'completed'
    attempt.completed_at = datetime.utcnow()
    
    # Calculate score
    attempt.calculate_score()
    
    db.session.commit()
    
    flash(f'Quiz submitted! Your score: {attempt.score:.1f}%', 'success')
    return redirect(url_for('learning.quiz_result', attempt_id=attempt.id))


@learning_bp.route('/quiz/attempt/<int:attempt_id>/result')
@login_required
def quiz_result(attempt_id):
    """Show quiz results."""
    attempt = QuizAttempt.query.get_or_404(attempt_id)
    
    # Verify ownership
    if attempt.user_id != current_user.id:
        abort(403)
    
    quiz = attempt.quiz
    
    # Get all answers with questions
    answers = []
    for answer in attempt.answers:
        question = answer.question
        
        # Parse options if multiple choice
        options = None
        if question.options:
            try:
                options = json.loads(question.options)
            except:
                options = None
        
        answers.append({
            'question': question,
            'answer': answer,
            'options': options
        })
    
    return render_template('learning/quiz_result.html',
                         attempt=attempt,
                         quiz=quiz,
                         answers=answers)


@learning_bp.route('/quiz/<int:quiz_id>/results')
@login_required
def quiz_results(quiz_id):
    """Show all quiz attempts."""
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Get all attempts for this user
    attempts = QuizAttempt.query.filter_by(
        user_id=current_user.id,
        quiz_id=quiz_id,
        status='completed'
    ).order_by(QuizAttempt.completed_at.desc()).all()
    
    return render_template('learning/quiz_results.html',
                         quiz=quiz,
                         attempts=attempts)


@learning_bp.route('/progress')
@login_required
def progress_dashboard():
    """Show user's learning progress dashboard."""
    # Get all enrollments
    enrollments = TutorialEnrollment.query.filter_by(
        user_id=current_user.id,
        status='active'
    ).order_by(TutorialEnrollment.enrolled_at.desc()).all()
    
    # Calculate statistics
    total_courses = len(enrollments)
    completed_courses = sum(1 for e in enrollments if e.is_completed)
    total_lessons_completed = sum(e.lessons_completed for e in enrollments)
    
    # Get recent activity (last 10 lesson completions)
    recent_progress = LessonProgress.query.filter_by(
        user_id=current_user.id,
        is_completed=True
    ).order_by(LessonProgress.completed_at.desc()).limit(10).all()
    
    # Get bookmarked lessons
    bookmarked = LessonProgress.query.filter_by(
        user_id=current_user.id,
        is_bookmarked=True
    ).order_by(LessonProgress.last_accessed_at.desc()).all()
    
    # Calculate learning streak (simplified)
    today = datetime.utcnow().date()
    streak = 0
    check_date = today
    
    while True:
        day_progress = LessonProgress.query.filter(
            LessonProgress.user_id == current_user.id,
            func.date(LessonProgress.last_accessed_at) == check_date
        ).first()
        
        if day_progress:
            streak += 1
            check_date = check_date.replace(day=check_date.day - 1)
        else:
            break
        
        if streak > 30:  # Max reasonable streak to check
            break
    
    return render_template('learning/progress_dashboard.html',
                         enrollments=enrollments,
                         total_courses=total_courses,
                         completed_courses=completed_courses,
                         total_lessons_completed=total_lessons_completed,
                         recent_progress=recent_progress,
                         bookmarked=bookmarked,
                         streak=streak)
