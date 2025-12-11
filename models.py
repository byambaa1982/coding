from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from db import db



class Language(db.Model):
    __tablename__ = 'language'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    def __str__(self):
        return self.name

class Topic(db.Model):
    __tablename__ = 'topic'
    id = db.Column(db.Integer, primary_key=True)
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    language = db.relationship('Language', backref=db.backref('topics', lazy=True))

    def __str__(self):
        return f"{self.language.name} - {self.title}"

    __table_args__ = (
        db.UniqueConstraint('language_id', 'title', name='unique_title_per_language'),
    )

class Subtopic(db.Model):
    __tablename__ = 'subtopics'
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
    subtitle = db.Column(db.String(200), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    topic = db.relationship('Topic', backref=db.backref('subtopics', lazy=True))

    def __str__(self):
        return f"{self.topic.title} - {self.subtitle}"

    __table_args__ = (
        db.UniqueConstraint('topic_id', 'order', name='unique_order_per_topic'),
    )

class Task2(db.Model):
    __tablename__ = 'tasks2'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Subtopic_id = db.Column(db.Integer, db.ForeignKey('subtopics.id'), nullable=False)
    instruction = db.Column(db.Text, nullable=False)  # Instructions for the task
    sample_code = db.Column(db.Text, nullable=True)  # Pre-filled sample code, if any
    expected_output = db.Column(db.Text, nullable=False)  # Expected output for validation
    hint = db.Column(db.Text, nullable=True)  # Hint for the task
    order = db.Column(db.Integer, nullable=False)  # Order of tasks in the section
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    subtopic = db.relationship('Subtopic', backref=db.backref('tasks', lazy=True))

    def __str__(self):
        return f"Task {self.id} - {self.instruction[:50]}..."

    __table_args__ = (
        db.UniqueConstraint('Subtopic_id', 'order', name='unique_order_per_subtopic'),
    )


class UserProgress(db.Model):
    __tablename__ = 'user_progress'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
    subtopic_id = db.Column(db.Integer, db.ForeignKey('subtopics.id'), nullable=False)
    is_completed = db.Column(db.Boolean, default=False, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    users_code = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    # Relationships
    user = db.relationship('User', backref=db.backref('progress', lazy=True))
    topic = db.relationship('Topic', backref=db.backref('user_progress', lazy=True))
    subtopic = db.relationship('Subtopic', backref=db.backref('user_progress', lazy=True))

    def __str__(self):
        try:
            username = self.user.username if self.user else f"User ID {self.user_id}"
            topic_title = self.topic.title if self.topic else f"Topic ID {self.topic_id}"
            subtopic_title = self.subtopic.subtitle if self.subtopic else f"Subtopic ID {self.subtopic_id}"
            status = 'Completed' if self.is_completed else 'In Progress'
            return f"{username} - {topic_title} - {subtopic_title} - {status}"
        except:
            return f"UserProgress ID {self.id}"

    def __repr__(self):
        return f"<UserProgress(id={self.id}, user_id={self.user_id}, topic_id={self.topic_id}, subtopic_id={self.subtopic_id}, is_completed={self.is_completed})>"

    def mark_completed(self):
        """Mark this subtopic as completed"""
        self.is_completed = True
        self.completed_at = db.func.now()
        self.updated_at = db.func.now()
    
    def mark_incomplete(self):
        """Mark this subtopic as incomplete"""
        self.is_completed = False
        self.completed_at = None
        self.updated_at = db.func.now()
    
    @property
    def progress_percentage(self):
        """Calculate progress percentage for this user's topic"""
        if not self.topic:
            return 0
        
        total_subtopics = len(self.topic.subtopics)
        if total_subtopics == 0:
            return 0
        
        completed_subtopics = UserProgress.query.filter_by(
            user_id=self.user_id,
            topic_id=self.topic_id,
            is_completed=True
        ).count()
        
        return (completed_subtopics / total_subtopics) * 100

    __table_args__ = (
        db.UniqueConstraint('user_id', 'topic_id', 'subtopic_id', name='unique_user_topic_subtopic'),
    )

class TaskProgress(db.Model):
    __tablename__ = 'task_progress'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks2.id'), nullable=False)
    user_code = db.Column(db.Text, nullable=True)  # User's submitted code for this specific task
    is_completed = db.Column(db.Boolean, default=False, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    # Relationships
    user = db.relationship('User', backref=db.backref('task_progress', lazy=True))
    task = db.relationship('Task2', backref=db.backref('task_progress', lazy=True))

    def __str__(self):
        try:
            username = self.user.username if self.user else f"User ID {self.user_id}"
            task_info = f"Task ID {self.task_id}"
            if self.task and self.task.instruction:
                task_info = f"Task: {self.task.instruction[:50]}..."
            status = 'Completed' if self.is_completed else 'In Progress'
            return f"{username} - {task_info} - {status}"
        except:
            return f"TaskProgress ID {self.id}"

    def __repr__(self):
        return f"<TaskProgress(id={self.id}, user_id={self.user_id}, task_id={self.task_id}, is_completed={self.is_completed})>"

    def mark_completed(self):
        """Mark this task as completed"""
        self.is_completed = True
        self.completed_at = db.func.now()
        self.updated_at = db.func.now()

    def mark_incomplete(self):
        """Mark this task as incomplete"""
        self.is_completed = False
        self.completed_at = None
        self.updated_at = db.func.now()

    __table_args__ = (
        db.UniqueConstraint('user_id', 'task_id', name='unique_user_task'),
    )

