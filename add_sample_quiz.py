# add_sample_quiz.py
"""Add sample quiz data for testing Phase 4."""

import json
from app import create_app, db
from app.models import Lesson, Quiz, QuizQuestion

def add_sample_quiz():
    """Add a sample quiz to the first lesson."""
    app = create_app()
    
    with app.app_context():
        # Get first lesson
        lesson = Lesson.query.first()
        
        if not lesson:
            print("❌ No lessons found. Please create lessons first.")
            return
        
        # Check if quiz already exists
        existing = Quiz.query.filter_by(lesson_id=lesson.id).first()
        if existing:
            print(f"⚠️  Quiz already exists for lesson: {lesson.title}")
            return
        
        # Create quiz
        quiz = Quiz(
            lesson_id=lesson.id,
            tutorial_id=lesson.tutorial_id,
            title=f"{lesson.title} - Knowledge Check",
            description="Test your understanding of the concepts covered in this lesson.",
            passing_score=70.00,
            time_limit_minutes=10,
            max_attempts=3,
            shuffle_questions=True,
            shuffle_options=True,
            show_correct_answers=True,
            is_required=False
        )
        db.session.add(quiz)
        db.session.flush()  # Get quiz ID
        
        # Add sample questions
        questions = [
            {
                'question_text': 'What is the primary purpose of Python?',
                'question_type': 'multiple_choice',
                'options': json.dumps([
                    {'id': 'a', 'text': 'Web development only'},
                    {'id': 'b', 'text': 'General-purpose programming'},
                    {'id': 'c', 'text': 'Database management only'},
                    {'id': 'd', 'text': 'Mobile app development only'}
                ]),
                'correct_answer': 'b',
                'explanation': 'Python is a general-purpose programming language used for web development, data science, automation, and more.',
                'points': 10,
                'order_index': 1
            },
            {
                'question_text': 'Python is an interpreted language.',
                'question_type': 'true_false',
                'options': None,
                'correct_answer': 'true',
                'explanation': 'Python code is executed line by line by the Python interpreter.',
                'points': 10,
                'order_index': 2
            },
            {
                'question_text': 'Which keyword is used to define a function in Python?',
                'question_type': 'multiple_choice',
                'options': json.dumps([
                    {'id': 'a', 'text': 'function'},
                    {'id': 'b', 'text': 'def'},
                    {'id': 'c', 'text': 'func'},
                    {'id': 'd', 'text': 'define'}
                ]),
                'correct_answer': 'b',
                'explanation': 'The "def" keyword is used to define functions in Python.',
                'points': 10,
                'order_index': 3
            },
            {
                'question_text': 'Python uses indentation to define code blocks.',
                'question_type': 'true_false',
                'options': None,
                'correct_answer': 'true',
                'explanation': 'Python uses indentation (whitespace) to define code blocks, unlike many other languages that use braces.',
                'points': 10,
                'order_index': 4
            },
            {
                'question_text': 'What is the file extension for Python files?',
                'question_type': 'text',
                'options': None,
                'correct_answer': '.py',
                'explanation': 'Python source files use the .py extension.',
                'points': 10,
                'order_index': 5
            }
        ]
        
        for q_data in questions:
            question = QuizQuestion(
                quiz_id=quiz.id,
                **q_data
            )
            db.session.add(question)
        
        db.session.commit()
        
        print(f"✅ Sample quiz added to lesson: {lesson.title}")
        print(f"   Quiz ID: {quiz.id}")
        print(f"   Questions: {len(questions)}")
        print(f"   Passing score: {quiz.passing_score}%")
        print(f"   Time limit: {quiz.time_limit_minutes} minutes")

if __name__ == '__main__':
    add_sample_quiz()
