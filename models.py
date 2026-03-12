from datetime import datetime
from extensions import db

# Association table for control work questions
control_work_questions = db.Table(
    'control_work_questions',
    db.Column('control_work_id', db.Integer, db.ForeignKey('control_work.id'), primary_key=True),
    db.Column('question_id', db.Integer, db.ForeignKey('question.id'), primary_key=True)
)


class ControlWork(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    grade = db.Column(db.Integer, nullable=False)
    quarter = db.Column(db.Integer, nullable=False)
    time_limit = db.Column(db.Integer, default=40)  # minutes
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    subject = db.relationship('Subject', backref='control_works')
    questions = db.relationship(
        'Question',
        secondary=control_work_questions,
        lazy='subquery',
        backref=db.backref('control_works', lazy=True)
    )


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='teacher')  # 'admin' or 'teacher'
    phone_number = db.Column(db.String(20))
    email = db.Column(db.String(100))


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    name_ru = db.Column(db.String(50))
    name_en = db.Column(db.String(50))
    grades = db.Column(db.String(20), nullable=False)  # e.g. "5,6" or "7,8,9"
    is_protected = db.Column(db.Boolean, default=False)  # Anti-cheat protection
    question_count = db.Column(db.Integer, default=20)
    time_limit = db.Column(db.Integer, default=30)
    show_results = db.Column(db.Boolean, default=True)
    is_visible = db.Column(db.Boolean, default=True)


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    grade = db.Column(db.Integer, nullable=False)
    quarter = db.Column(db.Integer, nullable=False)
    difficulty = db.Column(db.Integer, default=2)  # 1=easy,2=medium,3=hard
    lesson = db.Column(db.Integer, nullable=True)
    question_text = db.Column(db.Text, nullable=False)
    question_text_ru = db.Column(db.Text)
    question_text_en = db.Column(db.Text)
    option_a = db.Column(db.String(200), nullable=False)
    option_a_ru = db.Column(db.String(200))
    option_a_en = db.Column(db.String(200))
    option_b = db.Column(db.String(200), nullable=False)
    option_b_ru = db.Column(db.String(200))
    option_b_en = db.Column(db.String(200))
    option_c = db.Column(db.String(200), nullable=False)
    option_c_ru = db.Column(db.String(200))
    option_c_en = db.Column(db.String(200))
    option_d = db.Column(db.String(200), nullable=False)
    option_d_ru = db.Column(db.String(200))
    option_d_en = db.Column(db.String(200))
    correct_answer = db.Column(db.String(1), nullable=False)  # A, B, C, or D

    subject = db.relationship('Subject', backref='questions')


class TestResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    grade = db.Column(db.Integer, nullable=False)
    class_number = db.Column(db.String(10), nullable=False)
    quarter = db.Column(db.Integer, nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, default=20)
    percentage = db.Column(db.Float, nullable=False)
    grade_text = db.Column(db.String(20), nullable=False)
    test_date = db.Column(db.DateTime, default=datetime.utcnow)
    answers_json = db.Column(db.Text)  # JSON format
    control_work_id = db.Column(db.Integer, db.ForeignKey('control_work.id'), nullable=True)

    control_work = db.relationship('ControlWork', backref='results')
    subject = db.relationship('Subject', backref='results')


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_uuid = db.Column(db.String(36), nullable=False)  # UUID for anonymity
    # Legacy fields (kept for backward compatibility / migrations)
    message = db.Column(db.Text, nullable=False)
    admin_response = db.Column(db.Text)

    # New chat-style fields
    sender = db.Column(db.String(10), default='student')  # 'student' | 'admin'
    text = db.Column(db.Text)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    responded_at = db.Column(db.DateTime)
