from datetime import datetime, timedelta


def tashkent_now():
    """Hozirgi Toshkent vaqtini qaytaradi (UTC+5)."""
    return datetime.utcnow() + timedelta(hours=5)
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
    created_at = db.Column(db.DateTime, default=tashkent_now)

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
    creator_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=tashkent_now)

    creator = db.relationship('Admin', backref='subjects', foreign_keys=[creator_id])


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
    creator_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=tashkent_now)

    subject = db.relationship('Subject', backref='questions')
    creator = db.relationship('Admin', backref='questions', foreign_keys=[creator_id])

    __table_args__ = (
        db.Index('ix_question_subject_grade_quarter', 'subject_id', 'grade', 'quarter'),
        db.Index('ix_question_difficulty', 'difficulty'),
        db.Index('ix_question_creator', 'creator_id'),
    )


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
    test_date = db.Column(db.DateTime, default=tashkent_now)
    answers_json = db.Column(db.Text)  # JSON format
    control_work_id = db.Column(db.Integer, db.ForeignKey('control_work.id'), nullable=True)

    control_work = db.relationship('ControlWork', backref='results')
    subject = db.relationship('Subject', backref='results')

    __table_args__ = (
        db.Index('ix_result_subject_grade', 'subject_id', 'grade'),
        db.Index('ix_result_date', 'test_date'),
        db.Index('ix_result_quarter', 'quarter'),
    )


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
    created_at = db.Column(db.DateTime, default=tashkent_now)
    responded_at = db.Column(db.DateTime)


# ─── Arena Module ─────────────────────────────────────────────────────────────

class ArenaUser(db.Model):
    __tablename__ = 'arena_users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    password_hash = db.Column(db.String(256), nullable=False)
    bio = db.Column(db.Text, default='')
    rating = db.Column(db.Integer, default=0)
    problems_solved = db.Column(db.Integer, default=0)
    total_stars = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=tashkent_now)
    last_seen = db.Column(db.DateTime, default=tashkent_now)

    submissions = db.relationship('ArenaSubmission', backref='user', lazy='dynamic')

    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)

    __table_args__ = (
        db.Index('ix_arena_user_username', 'username'),
        db.Index('ix_arena_user_rating', 'rating'),
    )


class ArenaProblem(db.Model):
    __tablename__ = 'arena_problems'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)  # A001, M005
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    input_format = db.Column(db.Text, default='')
    output_format = db.Column(db.Text, default='')
    constraints = db.Column(db.Text, default='')
    examples = db.Column(db.Text, default='[]')  # JSON: [{input, output, explanation}]
    hidden_tests = db.Column(db.Text, default='[]')  # JSON: [{input, output}] — foydalanuvchiga ko'rsatilmaydi
    difficulty = db.Column(db.String(10), default='easy')   # easy / medium / hard
    category = db.Column(db.String(50), default='general')
    correct_answer = db.Column(db.Text, default='')          # for auto-grading
    time_limit = db.Column(db.Float, default=1.0)            # seconds (display)
    memory_limit = db.Column(db.Integer, default=256)        # MB (display)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=tashkent_now)
    accepted_count = db.Column(db.Integer, default=0)
    submission_count = db.Column(db.Integer, default=0)

    submissions = db.relationship('ArenaSubmission', backref='problem', lazy='dynamic')

    __table_args__ = (
        db.Index('ix_arena_problem_difficulty', 'difficulty'),
        db.Index('ix_arena_problem_category', 'category'),
        db.Index('ix_arena_problem_active', 'is_active'),
    )


# ─── Typing Race Module ───────────────────────────────────────────────────────

class TypingResult(db.Model):
    """Typing race natijasi — login talab qilinmaydi."""
    __tablename__ = 'typing_results'
    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(30), nullable=False)
    wpm          = db.Column(db.Integer, nullable=False)
    accuracy     = db.Column(db.Integer, nullable=False, default=100)  # 0–100 %
    chars_correct = db.Column(db.Integer, default=0)
    chars_total  = db.Column(db.Integer, default=0)
    is_solo      = db.Column(db.Boolean, default=False)
    created_at   = db.Column(db.DateTime, default=tashkent_now)

    __table_args__ = (
        db.Index('ix_typing_wpm', 'wpm'),
        db.Index('ix_typing_created', 'created_at'),
    )


class ArenaSubmission(db.Model):
    __tablename__ = 'arena_submissions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('arena_users.id'), nullable=False)
    problem_id = db.Column(db.Integer, db.ForeignKey('arena_problems.id'), nullable=False)
    code = db.Column(db.Text, default='')            # submitted source code
    language = db.Column(db.String(20), default='python')
    answer = db.Column(db.Text, default='')          # program's stdout (for display)
    status = db.Column(db.String(5), default='PE')   # AC / WA / TLE / RE / CE / PE
    time_used = db.Column(db.Float, default=0.0)     # execution time in seconds
    error_msg = db.Column(db.Text, default='')       # stderr / error text
    tests_passed = db.Column(db.Integer, default=0)  # nechta test o'tdi
    tests_total = db.Column(db.Integer, default=0)   # jami testlar soni
    stars = db.Column(db.Integer, default=0)         # 0–5 yulduz
    submitted_at = db.Column(db.DateTime, default=tashkent_now)

    __table_args__ = (
        db.Index('ix_arena_sub_user', 'user_id'),
        db.Index('ix_arena_sub_problem', 'problem_id'),
        db.Index('ix_arena_sub_user_status', 'user_id', 'status'),
    )
