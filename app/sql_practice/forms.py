from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, IntegerField, SelectField, HiddenField
from wtforms.validators import DataRequired, Length, Optional


class SQLQueryForm(FlaskForm):
    """Form for executing SQL queries"""
    query = TextAreaField('SQL Query', validators=[
        DataRequired(message='Query is required'),
        Length(max=10000, message='Query is too long')
    ])
    exercise_id = IntegerField('Exercise ID', validators=[Optional()])
    schema_id = StringField('Schema ID', validators=[Optional()])


class SQLExerciseSubmissionForm(FlaskForm):
    """Form for submitting SQL exercise solutions"""
    exercise_id = IntegerField('Exercise ID', validators=[DataRequired()])
    query = TextAreaField('SQL Query', validators=[
        DataRequired(message='Query is required'),
        Length(max=10000, message='Query is too long')
    ])


class SchemaSelectionForm(FlaskForm):
    """Form for selecting database schema"""
    schema_id = SelectField('Schema', validators=[DataRequired()], coerce=int)
