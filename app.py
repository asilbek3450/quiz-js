from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, g
from flask_babel import Babel, _, gettext
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import random
import json
from deep_translator import GoogleTranslator




app = Flask(__name__, template_folder="templates")
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_platform.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
babel = Babel(app)

def get_locale():
    # If the user has a saved language in session, use it
    if 'lang' in session:
        return session['lang']
    # Otherwise, try to match the best language from the browser
    return request.accept_languages.best_match(['uz', 'ru', 'en'])

babel.init_app(app, locale_selector=get_locale)

@app.context_processor
def inject_conf_var():
    return dict(get_locale=get_locale)


# ============= MODELS =============

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

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    grade = db.Column(db.Integer, nullable=False)
    quarter = db.Column(db.Integer, nullable=False)
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
    class_number = db.Column(db.String(10), nullable=False)  # Changed to String to accept 'A', 'B', etc.
    quarter = db.Column(db.Integer, nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, default=20)
    percentage = db.Column(db.Float, nullable=False)
    grade_text = db.Column(db.String(20), nullable=False)
    test_date = db.Column(db.DateTime, default=datetime.utcnow)
    answers_json = db.Column(db.Text)  # JSON format
    
    subject = db.relationship('Subject', backref='results')

# ============= HELPER FUNCTIONS =============

def calculate_grade(score, total=20):
    percentage = (score / total) * 100
    if percentage >= 85:
        return _("A'lo (5)")
    elif percentage >= 70:
        return _("Yaxshi (4)")
    elif percentage >= 65:
        return _("Qoniqarli (3)")
    else:
        return _("Qoniqarsiz (2)")

def auto_translate(text, target):
    try:
        return GoogleTranslator(source='auto', target=target).translate(text)
    except:
        return text

def init_db():
    with app.app_context():
        db.create_all()
        
        # Admin yaratish
        if not Admin.query.first():
            admin = Admin(
                username='asilbek',
                password_hash=generate_password_hash('jahonschool'),
                full_name='Administrator'
            )
            db.session.add(admin)
        
        # Fanlarni yaratish
        if not Subject.query.first():
            informatika = Subject(name='Informatika', grades='5,6')
            python = Subject(name='Python', grades='7,8,9')
            db.session.add(informatika)
            db.session.add(python)
        
        # Namunaviy savollar (Informatika 5-sinf, 1-chorak)
        if Question.query.count() < 10:
            sample_questions = [
                {
                    'subject': 1, 'grade': 5, 'quarter': 1,
                    'text': 'Kompyuterning miyasi deb nimaga aytiladi?',
                    'a': 'Monitor', 'b': 'Protsessor', 'c': 'Klaviatura', 'd': 'Sichqoncha',
                    'correct': 'B'
                },
                {
                    'subject': 1, 'grade': 5, 'quarter': 1,
                    'text': 'Qaysi qurilma ma\'lumot kiritish uchun ishlatiladi?',
                    'a': 'Printer', 'b': 'Monitor', 'c': 'Klaviatura', 'd': 'Kolonka',
                    'correct': 'C'
                },
                {
                    'subject': 1, 'grade': 5, 'quarter': 1,
                    'text': 'ROM xotira nima?',
                    'a': 'Doimiy xotira', 'b': 'Operativ xotira', 'c': 'Tashqi xotira', 'd': 'Kesh xotira',
                    'correct': 'A'
                },
                {
                    'subject': 1, 'grade': 5, 'quarter': 1,
                    'text': 'Internet nima?',
                    'a': 'Kompyuter o\'yini', 'b': 'Global tarmoq', 'c': 'Dastur', 'd': 'Qurilma',
                    'correct': 'B'
                },
                {
                    'subject': 1, 'grade': 5, 'quarter': 1,
                    'text': 'Fayl kengaytmasi .txt nimani bildiradi?',
                    'a': 'Rasm', 'b': 'Matn hujjati', 'c': 'Video', 'd': 'Audio',
                    'correct': 'B'
                }
            ]
            
            for q in sample_questions:
                question = Question(
                    subject_id=q['subject'],
                    grade=q['grade'],
                    quarter=q['quarter'],
                    question_text=q['text'],
                    option_a=q['a'],
                    option_b=q['b'],
                    option_c=q['c'],
                    option_d=q['d'],
                    correct_answer=q['correct']
                )
                db.session.add(question)
        
        db.session.commit()

# ============= ROUTES =============

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/set_language/<lang>')
def set_language(lang):
    if lang in ['uz', 'ru', 'en']:
        session['lang'] = lang
    return redirect(request.referrer or url_for('index'))


@app.route('/student/start', methods=['GET', 'POST'])
def student_start():
    if request.method == 'POST':
        # O'quvchi ma'lumotlarini olish
        session['student_name'] = request.form['name']
        session['student_surname'] = request.form['surname']
        session['grade'] = int(request.form['grade'])
        session['class_number'] = request.form['class_number']  # Keep as string
        session['quarter'] = int(request.form['quarter'])
        session['subject_id'] = int(request.form['subject_id'])
        session['start_time'] = datetime.now().timestamp()
        
        # Testni boshlash
        subject = Subject.query.get(session['subject_id'])
        questions = Question.query.filter_by(
            subject_id=session['subject_id'],
            grade=session['grade'],
            quarter=session['quarter']
        ).all()
        
        if len(questions) < 20:
            flash(_('Kechirasiz, bu fan va chorak uchun yetarli savollar yo\'q ({} ta mavjud)').format(len(questions)), 'danger')
            return redirect(url_for('student_start'))
        
        # 20 ta tasodifiy savol tanlash
        selected_questions = random.sample(questions, 20)
        session['question_ids'] = [q.id for q in selected_questions]
        session['current_question'] = 0
        session['answers'] = {}
        
        return redirect(url_for('student_test'))
    
    subjects = Subject.query.all()
    # Translate subject names for display
    lang = get_locale()
    for s in subjects:
        if lang == 'ru' and s.name_ru:
            s.display_name = s.name_ru
        elif lang == 'en' and s.name_en:
            s.display_name = s.name_en
        else:
            s.display_name = s.name
            
    return render_template('student_start.html', subjects=subjects)

@app.route('/student/test')
def student_test():
    if 'question_ids' not in session:
        return redirect(url_for('student_start'))
    
    current = session.get('current_question', 0)
    question_ids = session['question_ids']
    
    if current >= len(question_ids):
        return redirect(url_for('student_result'))
    
    question = Question.query.get(question_ids[current])
    answers = session.get('answers', {})
    
    # Determine language-specific fields
    lang = get_locale()
    
    if lang == 'ru':
        question_text = question.question_text_ru or question.question_text
        option_a = question.option_a_ru or question.option_a
        option_b = question.option_b_ru or question.option_b
        option_c = question.option_c_ru or question.option_c
        option_d = question.option_d_ru or question.option_d
    elif lang == 'en':
        question_text = question.question_text_en or question.question_text
        option_a = question.option_a_en or question.option_a
        option_b = question.option_b_en or question.option_b
        option_c = question.option_c_en or question.option_c
        option_d = question.option_d_en or question.option_d
    else:
        question_text = question.question_text
        option_a = question.option_a
        option_b = question.option_b
        option_c = question.option_c
        option_d = question.option_d

    # Randomize options
    options = [
        {'key': 'A', 'value': option_a},
        {'key': 'B', 'value': option_b},
        {'key': 'C', 'value': option_c},
        {'key': 'D', 'value': option_d}
    ]
    random.shuffle(options)

    return render_template('student_test.html', 
                         question=question,
                         question_text=question_text,
                         options=options,
                         current=current + 1, 
                         total=len(question_ids),
                         answers=answers)

@app.route('/student/answer', methods=['POST'])
def student_answer():
    if 'question_ids' not in session:
        return jsonify({'error': 'Session expired'}), 400
    
    data = request.json
    question_id = str(data['question_id'])
    answer = data['answer']
    
    answers = session.get('answers', {})
    answers[question_id] = answer
    session['answers'] = answers
    
    return jsonify({'success': True})

@app.route('/student/navigate/<direction>')
def student_navigate(direction):
    if 'question_ids' not in session:
        return redirect(url_for('student_start'))
    
    current = session.get('current_question', 0)
    total = len(session['question_ids'])
    
    if direction == 'next' and current < total - 1:
        session['current_question'] = current + 1
    elif direction == 'prev' and current > 0:
        session['current_question'] = current - 1
    elif direction == 'finish':
        return redirect(url_for('student_result'))
    
    return redirect(url_for('student_test'))

@app.route('/student/result')
def student_result():
    if 'question_ids' not in session:
        return redirect(url_for('student_start'))
    
    question_ids = session['question_ids']
    answers = session.get('answers', {})
    
    score = 0
    results = []
    lang = get_locale()
    
    for qid in question_ids:
        question = Question.query.get(qid)
        user_answer = answers.get(str(qid), '')
        is_correct = user_answer == question.correct_answer
        if is_correct:
            score += 1
        
        if lang == 'ru':
             q_text_display = question.question_text_ru or question.question_text
        elif lang == 'en':
             q_text_display = question.question_text_en or question.question_text
        else:
             q_text_display = question.question_text
        
        results.append({
            'question': q_text_display,
            'user_answer': user_answer,
            'correct_answer': question.correct_answer,
            'is_correct': is_correct
        })
    
    total = len(question_ids)
    percentage = (score / total) * 100
    
    # Calculate duration
    start_time = session.get('start_time')
    duration_text = "00:00"
    # Timezone correction: Tashkent is UTC+5, datetime.now() usually returns local system time.
    # We will ensure the saved time is accurate.
    current_time = datetime.now()
    
    if start_time:
        duration_seconds = int(current_time.timestamp() - start_time)
        mins = duration_seconds // 60
        secs = duration_seconds % 60
        duration_text = f"{mins:02d}:{secs:02d}"
    
    grade_text = calculate_grade(score, total)
    
    # Natijani saqlash
    full_name = f"{session['student_name']} {session['student_surname']}"
    
    # Tashkent time is UTC+5
    tashkent_time = datetime.utcnow() + timedelta(hours=5)
    
    result = TestResult(
        full_name=full_name,
        grade=session['grade'],
        class_number=session['class_number'],
        quarter=session['quarter'],
        subject_id=session['subject_id'],
        score=score,
        total_questions=total,
        percentage=percentage,
        grade_text=grade_text,
        test_date=tashkent_time,
        answers_json=json.dumps(answers)
    )
    db.session.add(result)
    db.session.commit()
    

    
    # Sessionni tozalash
    keys_to_keep = []
    for key in list(session.keys()):
        if key not in keys_to_keep:
            session.pop(key, None)
    
    return render_template('student_result.html', 
                         score=score, 
                         total=total, 
                         percentage=percentage,
                         grade_text=grade_text,
                         results=results)

# ============= ADMIN ROUTES =============

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if 'admin_id' in session:
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password_hash, password):
            session['admin_id'] = admin.id
            session['admin_name'] = admin.full_name
            flash(_('Xush kelibsiz {}!').format(admin.full_name), 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash(_('Login yoki parol noto\'g\'ri'), 'danger')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    session.pop('admin_name', None)
    flash(_('Tizimdan chiqdingiz'), 'info')
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    total_questions = Question.query.count()
    total_results = TestResult.query.count()
    subjects = Subject.query.all()
    recent_results = TestResult.query.order_by(TestResult.test_date.desc()).limit(10).all()
    
    # Prepare data for charts
    subject_names = [s.name for s in subjects]
    question_counts = [len(s.questions) for s in subjects]
    result_counts = [len(s.results) for s in subjects]
    
    return render_template('admin_dashboard.html',
                         total_questions=total_questions,
                         total_results=total_results,
                         subjects=subjects,
                         recent_results=recent_results,
                         subject_names=subject_names,
                         question_counts=question_counts,
                         result_counts=result_counts)

@app.route('/admin/questions')
def admin_questions():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    # Filtrlash parametrlari
    subject_id = request.args.get('subject_id', type=int)
    grade = request.args.get('grade', type=int)
    quarter = request.args.get('quarter', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = 25
    
    # Query yaratish
    query = Question.query
    if subject_id:
        query = query.filter_by(subject_id=subject_id)
    if grade:
        query = query.filter_by(grade=grade)
    if quarter:
        query = query.filter_by(quarter=quarter)
    
    # Pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    questions = pagination.items
    
    # Barcha savollar (statistika uchun)
    all_questions = Question.query.all()
    subjects = Subject.query.all()
    
    return render_template('admin_questions.html', 
                         questions=questions,
                         all_questions=all_questions,
                         pagination=pagination,
                         subjects=subjects)

@app.route('/admin/question/add', methods=['GET', 'POST'])
def admin_question_add():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        q_text = request.form['question_text']
        opt_a = request.form['option_a']
        opt_b = request.form['option_b']
        opt_c = request.form['option_c']
        opt_d = request.form['option_d']
        
        question = Question(
            subject_id=int(request.form['subject_id']),
            grade=int(request.form['grade']),
            quarter=int(request.form['quarter']),
            question_text=q_text,
            question_text_ru=auto_translate(q_text, 'ru'),
            question_text_en=auto_translate(q_text, 'en'),
            option_a=opt_a,
            option_a_ru=auto_translate(opt_a, 'ru'),
            option_a_en=auto_translate(opt_a, 'en'),
            option_b=opt_b,
            option_b_ru=auto_translate(opt_b, 'ru'),
            option_b_en=auto_translate(opt_b, 'en'),
            option_c=opt_c,
            option_c_ru=auto_translate(opt_c, 'ru'),
            option_c_en=auto_translate(opt_c, 'en'),
            option_d=opt_d,
            option_d_ru=auto_translate(opt_d, 'ru'),
            option_d_en=auto_translate(opt_d, 'en'),
            correct_answer=request.form['correct_answer'].upper()
        )
        db.session.add(question)
        db.session.commit()
        flash(_('Savol muvaffaqiyatli qo\'shildi va tarjima qilindi'), 'success')
        return redirect(url_for('admin_questions'))
    
    subjects = Subject.query.all()
    return render_template('admin_question_form.html', subjects=subjects, question=None)

@app.route('/admin/question/edit/<int:id>', methods=['GET', 'POST'])
def admin_question_edit(id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    question = Question.query.get_or_404(id)
    
    if request.method == 'POST':
        question.subject_id = int(request.form['subject_id'])
        question.grade = int(request.form['grade'])
        question.quarter = int(request.form['quarter'])
        
        # Only re-translate if text changed (optimization could be added, but for now simple update)
        q_text = request.form['question_text']
        question.question_text = q_text
        question.question_text_ru = auto_translate(q_text, 'ru')
        question.question_text_en = auto_translate(q_text, 'en')
        
        question.option_a = request.form['option_a']
        question.option_a_ru = auto_translate(question.option_a, 'ru')
        question.option_a_en = auto_translate(question.option_a, 'en')
        
        question.option_b = request.form['option_b']
        question.option_b_ru = auto_translate(question.option_b, 'ru')
        question.option_b_en = auto_translate(question.option_b, 'en')
        
        question.option_c = request.form['option_c']
        question.option_c_ru = auto_translate(question.option_c, 'ru')
        question.option_c_en = auto_translate(question.option_c, 'en')
        
        question.option_d = request.form['option_d']
        question.option_d_ru = auto_translate(question.option_d, 'ru')
        question.option_d_en = auto_translate(question.option_d, 'en')
        
        question.correct_answer = request.form['correct_answer'].upper()
        
        db.session.commit()
        flash(_('Savol muvaffaqiyatli o\'zgartirildi'), 'success')
        return redirect(url_for('admin_questions'))
    
    subjects = Subject.query.all()
    return render_template('admin_question_form.html', subjects=subjects, question=question)

@app.route('/admin/question/delete/<int:id>')
def admin_question_delete(id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    question = Question.query.get_or_404(id)
    db.session.delete(question)
    db.session.commit()
    flash(_('Savol o\'chirildi'), 'success')
    return redirect(url_for('admin_questions'))

@app.route('/admin/result/delete/<int:id>', methods=['POST'])
def admin_result_delete(id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    result = TestResult.query.get_or_404(id)
    db.session.delete(result)
    db.session.commit()
    flash(_('Natija muvaffaqiyatli o\'chirildi'), 'success')
    return redirect(url_for('admin_results'))

@app.route('/admin/results/delete-by-date', methods=['POST'])
def admin_results_delete_by_date():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    date_str = request.form['delete_date']
    try:
        # Parse date from string YYYY-MM-DD
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # We need to filter by the date part of the datetime column
        # SQLite specific: strftime based filtering might be needed or range check
        # Let's try range check for safety
        start_dt = datetime.combine(target_date, datetime.min.time())
        end_dt = datetime.combine(target_date, datetime.max.time())
        
        deleted_count = TestResult.query.filter(
            TestResult.test_date >= start_dt,
            TestResult.test_date <= end_dt
        ).delete()
        
        db.session.commit()
        flash(_('{} ta natija o\'chirildi').format(deleted_count), 'success')
    except Exception as e:
        flash(_('Xatolik yuz berdi: {}').format(str(e)), 'danger')
        
    return redirect(url_for('admin_results'))

@app.route('/admin/results')
def admin_results():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    subject_id = request.args.get('subject_id', type=int)
    grade = request.args.get('grade', type=int)
    quarter = request.args.get('quarter', type=int)
    
    query = TestResult.query
    if subject_id:
        query = query.filter_by(subject_id=subject_id)
    if grade:
        query = query.filter_by(grade=grade)
    if quarter:
        query = query.filter_by(quarter=quarter)
    
    results = query.order_by(TestResult.test_date.desc()).all()
    subjects = Subject.query.all()
    
    return render_template('admin_results.html', 
                         results=results, 
                         subjects=subjects)

@app.route('/admin/subjects')
def admin_subjects():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    subjects = Subject.query.all()
    return render_template('admin_subjects.html', subjects=subjects)

@app.route('/admin/subject/add', methods=['GET', 'POST'])
def admin_subject_add():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        name = request.form['name']
        grades = request.form['grades'] # e.g., "5,6"
        
        subject = Subject(
            name=name, 
            grades=grades,
            name_ru=auto_translate(name, 'ru'),
            name_en=auto_translate(name, 'en')
        )
        db.session.add(subject)
        db.session.commit()
        flash(_('Fan muvaffaqiyatli qo\'shildi va tarjima qilindi'), 'success')
        return redirect(url_for('admin_subjects'))
    
    return render_template('admin_subject_form.html', subject=None)

@app.route('/admin/subject/edit/<int:id>', methods=['GET', 'POST'])
def admin_subject_edit(id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    subject = Subject.query.get_or_404(id)
    
    if request.method == 'POST':
        subject.name = request.form['name']
        subject.name_ru = auto_translate(subject.name, 'ru')
        subject.name_en = auto_translate(subject.name, 'en')
        
        subject.grades = request.form['grades']
        
        db.session.commit()
        flash(_('Fan muvaffaqiyatli o\'zgartirildi'), 'success')
        return redirect(url_for('admin_subjects'))
    
    return render_template('admin_subject_form.html', subject=subject)

@app.route('/admin/subject/delete/<int:id>')
def admin_subject_delete(id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    subject = Subject.query.get_or_404(id)
    
    # Check if subject has questions or results
    if subject.questions or subject.results:
        flash(_('Bu fanga tegishli savollar yoki natijalar mavjud. Oldin ularni o\'chiring.'), 'danger')
        return redirect(url_for('admin_subjects'))
        
    db.session.delete(subject)
    db.session.commit()
    flash(_('Fan o\'chirildi'), 'success')
    return redirect(url_for('admin_subjects'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)