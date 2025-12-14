"""Forms for instructor panel."""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DecimalField, SelectField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, URL


class CourseForm(FlaskForm):
    """Form for creating/editing courses."""
    title = StringField('Course Title', validators=[
        DataRequired(message='Title is required'),
        Length(min=3, max=300, message='Title must be between 3 and 300 characters')
    ])
    
    short_description = TextAreaField('Short Description', validators=[
        DataRequired(message='Short description is required'),
        Length(max=500, message='Short description must be less than 500 characters')
    ])
    
    description = TextAreaField('Full Description', validators=[
        DataRequired(message='Description is required')
    ])
    
    course_type = SelectField('Course Type', 
        choices=[('python', 'Python'), ('sql', 'SQL')],
        validators=[DataRequired()])
    
    category = StringField('Category', validators=[
        DataRequired(message='Category is required'),
        Length(max=100)
    ])
    
    difficulty_level = SelectField('Difficulty Level',
        choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')],
        validators=[DataRequired()])
    
    price = DecimalField('Price (USD)', validators=[
        DataRequired(message='Price is required'),
        NumberRange(min=0, message='Price must be 0 or greater')
    ], places=2)
    
    is_free = BooleanField('Make this course free')
    
    estimated_duration_hours = DecimalField('Estimated Duration (Hours)', validators=[
        Optional(),
        NumberRange(min=0.5, max=999, message='Duration must be between 0.5 and 999 hours')
    ], places=2)
    
    thumbnail_url = StringField('Thumbnail URL', validators=[Optional(), URL()])
    preview_video_url = StringField('Preview Video URL', validators=[Optional(), URL()])
    tags = StringField('Tags (comma-separated)', validators=[Optional()])


class LessonForm(FlaskForm):
    """Form for creating/editing lessons."""
    title = StringField('Lesson Title', validators=[
        DataRequired(message='Title is required'),
        Length(min=3, max=300, message='Title must be between 3 and 300 characters')
    ])
    
    description = TextAreaField('Description', validators=[Optional()])
    
    section_name = StringField('Section Name (optional)', validators=[
        Optional(),
        Length(max=200)
    ])
    
    content_type = SelectField('Content Type',
        choices=[('text', 'Text/Markdown'), ('video', 'Video')],
        validators=[DataRequired()])
    
    content = TextAreaField('Content (Markdown)', validators=[
        DataRequired(message='Content is required')
    ])
    
    video_url = StringField('Video URL (if applicable)', validators=[Optional(), URL()])
    video_duration_seconds = IntegerField('Video Duration (seconds)', validators=[Optional()])
    
    estimated_duration_minutes = IntegerField('Estimated Duration (minutes)', validators=[
        Optional(),
        NumberRange(min=1, max=999)
    ])
    
    is_free_preview = BooleanField('Allow free preview')
    order_index = IntegerField('Order (position in course)', validators=[
        DataRequired(message='Order is required'),
        NumberRange(min=0)
    ])


class ExerciseForm(FlaskForm):
    """Form for creating/editing exercises."""
    title = StringField('Exercise Title', validators=[
        DataRequired(message='Title is required'),
        Length(min=3, max=300)
    ])
    
    lesson_id = SelectField('Lesson (Optional)', coerce=int, validators=[Optional()])
    
    description = TextAreaField('Description', validators=[
        DataRequired(message='Description is required')
    ])
    
    exercise_type = SelectField('Exercise Type',
        choices=[('python', 'Python'), ('sql', 'SQL')],
        validators=[DataRequired()])
    
    difficulty = SelectField('Difficulty',
        choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')],
        validators=[DataRequired()])
    
    starter_code = TextAreaField('Starter Code', validators=[Optional()])
    solution_code = TextAreaField('Solution Code', validators=[Optional()])
    
    test_cases = TextAreaField('Test Cases (JSON format)', validators=[Optional()])
    hints = TextAreaField('Hints (JSON array)', validators=[Optional()])
    
    # SQL-specific fields
    database_schema = TextAreaField('Database Schema (DDL)', validators=[Optional()])
    sample_data = TextAreaField('Sample Data (INSERT statements)', validators=[Optional()])
    expected_output = TextAreaField('Expected Output (JSON)', validators=[Optional()])
    
    points = IntegerField('Points', validators=[
        DataRequired(),
        NumberRange(min=1, max=100)
    ])
    
    order_index = IntegerField('Order', validators=[
        DataRequired(),
        NumberRange(min=0)
    ])


class QuizForm(FlaskForm):
    """Form for creating/editing quizzes."""
    title = StringField('Quiz Title', validators=[
        DataRequired(message='Title is required'),
        Length(min=3, max=300)
    ])
    
    description = TextAreaField('Description', validators=[Optional()])
    
    lesson_id = SelectField('Lesson', coerce=int, validators=[DataRequired(message='Lesson is required')])
    
    passing_score = DecimalField('Passing Score (%)', validators=[
        DataRequired(),
        NumberRange(min=0, max=100, message='Score must be between 0 and 100')
    ], places=2)
    
    time_limit_minutes = IntegerField('Time Limit (minutes, 0 = no limit)', validators=[
        Optional(),
        NumberRange(min=0, max=999)
    ])
    
    max_attempts = IntegerField('Maximum Attempts', validators=[
        DataRequired(),
        NumberRange(min=1, max=99, message='Must allow at least 1 attempt')
    ])
    
    shuffle_questions = BooleanField('Shuffle Questions')
    shuffle_options = BooleanField('Shuffle Answer Options')
    show_correct_answers = BooleanField('Show Correct Answers After Completion')
    is_required = BooleanField('Required for Course Completion')
    
    order_index = IntegerField('Order', validators=[
        DataRequired(),
        NumberRange(min=0)
    ])


class QuizQuestionForm(FlaskForm):
    """Form for creating/editing quiz questions."""
    question_text = TextAreaField('Question Text', validators=[
        DataRequired(message='Question text is required')
    ])
    
    question_type = SelectField('Question Type',
        choices=[
            ('multiple_choice', 'Multiple Choice'),
            ('true_false', 'True/False'),
            ('text', 'Short Text Answer')
        ],
        validators=[DataRequired()])
    
    # For multiple choice questions
    option_a = StringField('Option A', validators=[Optional()])
    option_b = StringField('Option B', validators=[Optional()])
    option_c = StringField('Option C', validators=[Optional()])
    option_d = StringField('Option D', validators=[Optional()])
    
    correct_answer = StringField('Correct Answer', validators=[
        DataRequired(message='Correct answer is required')
    ])
    
    explanation = TextAreaField('Explanation (optional)', validators=[Optional()])
    
    points = IntegerField('Points', validators=[
        DataRequired(),
        NumberRange(min=1, max=10)
    ])
    
    order_index = IntegerField('Order', validators=[
        DataRequired(),
        NumberRange(min=0)
    ])


class TestCaseForm(FlaskForm):
    """Form for adding test cases to exercises."""
    description = StringField('Test Case Description', validators=[
        DataRequired(message='Description is required'),
        Length(max=200)
    ])
    
    input_data = TextAreaField('Input', validators=[
        DataRequired(message='Input is required')
    ])
    
    expected_output = TextAreaField('Expected Output', validators=[
        DataRequired(message='Expected output is required')
    ])
    
    is_hidden = BooleanField('Hidden Test Case (not shown to students)')
    points = IntegerField('Points', validators=[
        DataRequired(),
        NumberRange(min=1, max=10)
    ])
