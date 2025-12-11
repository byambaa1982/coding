# app/python_practice/forms.py
"""Forms for Python practice exercises."""

from flask_wtf import FlaskForm
from wtforms import TextAreaField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Length


class CodeSubmissionForm(FlaskForm):
    """Form for submitting Python code."""
    
    code = TextAreaField(
        'Code',
        validators=[
            DataRequired(message='Code is required'),
            Length(max=10000, message='Code must be less than 10,000 characters')
        ]
    )
    
    exercise_id = HiddenField('Exercise ID', validators=[DataRequired()])
    
    submit = SubmitField('Run Code')
