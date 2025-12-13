# app/admin/forms.py
"""Forms for admin course management."""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DecimalField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, Optional, NumberRange, URL


class TutorialForm(FlaskForm):
    """Form for creating/editing tutorials."""
    
    title = StringField('Title', validators=[
        DataRequired(),
        Length(min=5, max=300, message='Title must be between 5 and 300 characters')
    ])
    
    slug = StringField('Slug (URL)', validators=[
        DataRequired(),
        Length(min=3, max=350)
    ])
    
    short_description = TextAreaField('Short Description', validators=[
        Optional(),
        Length(max=500)
    ])
    
    description = TextAreaField('Full Description', validators=[
        DataRequired(),
        Length(min=50, message='Description must be at least 50 characters')
    ])
    
    course_type = SelectField('Course Type', validators=[DataRequired()], choices=[
        ('python', 'Python'),
        ('sql', 'SQL')
    ])
    
    category = StringField('Category', validators=[
        DataRequired(),
        Length(max=100)
    ])
    
    difficulty_level = SelectField('Difficulty Level', validators=[DataRequired()], choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced')
    ])
    
    price = DecimalField('Price (USD)', validators=[
        DataRequired(),
        NumberRange(min=0, max=9999.99)
    ], places=2)
    
    is_free = BooleanField('Free Course')
    is_featured = BooleanField('Featured Course')
    
    thumbnail_url = StringField('Thumbnail URL', validators=[Optional(), URL()])
    preview_video_url = StringField('Preview Video URL', validators=[Optional(), URL()])
    
    tags = StringField('Tags (comma-separated)', validators=[Optional()])
    
    estimated_duration_hours = DecimalField('Estimated Duration (hours)', validators=[
        Optional(),
        NumberRange(min=0.5, max=999)
    ], places=2)
    
    status = SelectField('Status', validators=[DataRequired()], choices=[
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived')
    ])


class LessonForm(FlaskForm):
    """Form for creating/editing lessons."""
    
    title = StringField('Lesson Title', validators=[
        DataRequired(),
        Length(min=3, max=300)
    ])
    
    slug = StringField('Slug', validators=[
        DataRequired(),
        Length(min=3, max=350)
    ])
    
    description = TextAreaField('Description', validators=[Optional()])
    
    content_type = SelectField('Content Type', validators=[DataRequired()], choices=[
        ('text', 'Text Content'),
        ('video', 'Video'),
        ('quiz', 'Quiz')
    ])
    
    content = TextAreaField('Content (Text/Markdown)', validators=[Optional()])
    
    video_url = StringField('Video URL', validators=[Optional(), URL()])
    
    video_duration_seconds = IntegerField('Video Duration (seconds)', validators=[
        Optional(),
        NumberRange(min=0)
    ])
    
    section_name = StringField('Section Name (for grouping)', validators=[Optional()])
    
    order_index = IntegerField('Order', validators=[
        DataRequired(),
        NumberRange(min=0)
    ])
    
    is_free_preview = BooleanField('Free Preview')
    
    estimated_duration_minutes = IntegerField('Estimated Duration (minutes)', validators=[
        Optional(),
        NumberRange(min=1)
    ])


class ExerciseForm(FlaskForm):
    """Form for creating/editing exercises."""
    
    title = StringField('Exercise Title', validators=[
        DataRequired(),
        Length(min=3, max=300)
    ])
    
    slug = StringField('Slug', validators=[
        DataRequired(),
        Length(min=3, max=350)
    ])
    
    description = TextAreaField('Description/Instructions', validators=[
        DataRequired(),
        Length(min=20)
    ])
    
    exercise_type = SelectField('Exercise Type', validators=[DataRequired()], choices=[
        ('python', 'Python'),
        ('sql', 'SQL')
    ])
    
    difficulty = SelectField('Difficulty', validators=[DataRequired()], choices=[
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard')
    ])
    
    starter_code = TextAreaField('Starter Code', validators=[Optional()])
    solution_code = TextAreaField('Solution Code', validators=[Optional()])
    test_cases = TextAreaField('Test Cases (JSON format)', validators=[Optional()])
    hints = TextAreaField('Hints (JSON array)', validators=[Optional()])
    expected_output = TextAreaField('Expected Output (JSON format)', validators=[Optional()])
    
    # SQL-specific fields
    database_schema = TextAreaField('Database Schema (DDL)', validators=[Optional()])
    sample_data = TextAreaField('Sample Data (INSERT statements)', validators=[Optional()])
    
    order_index = IntegerField('Order', validators=[
        DataRequired(),
        NumberRange(min=0)
    ])
    
    points = IntegerField('Points', validators=[
        DataRequired(),
        NumberRange(min=1, max=1000)
    ])
