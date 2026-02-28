from extensions import db
from datetime import datetime
import json

control_work_questions = db.Table('control_work_questions',
    db.Column('control_work_id', db.Integer, db.ForeignKey('control_work.id'), primary_key=True),
    db.Column('question_id', db.Integer, db.ForeignKey('question.id'), primary_key=True)
)

class ControlWork(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    grade = db.Column(db.Integer, nullable=False)
    quarter = db.Column(db.Integer, nullable=False)
    time_limit = db.Column(db.Integer, default=40) # in minutes
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    subject = db.relationship('Subject', backref='control_works')
    questions = db.relationship('Question', secondary=control_work_questions, lazy='subquery',
        backref=db.backref('control_works', lazy=True))
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    name_ru = db.Column(db.String(50))
    name_en = db.Column(db.String(50))
    grades = db.Column(db.String(20), nullable=False)  # "5,6" yoki "7,8,9"
    is_protected = db.Column(db.Boolean, default=False) # Anti-cheat protection
    question_count = db.Column(db.Integer, default=20)
    time_limit = db.Column(db.Integer, default=30)
    show_results = db.Column(db.Boolean, default=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    grade = db.Column(db.Integer, nullable=False)
    quarter = db.Column(db.Integer, nullable=False)
    # 1=easy, 2=medium, 3=hard (used for balanced quiz selection)
    difficulty = db.Column(db.Integer, default=2)
    # optional curriculum lesson marker (not required by app logic)
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
    control_work_id = db.Column(db.Integer, db.ForeignKey('control_work.id'), nullable=True) # None means regular test
    
    control_work = db.relationship('ControlWork', backref='results')
    
    subject = db.relationship('Subject', backref='results')
