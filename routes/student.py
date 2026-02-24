from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from flask_babel import gettext as _, get_locale
from extensions import db
from models import Subject, Question, TestResult, ControlWork
from datetime import datetime, timedelta
import random
import json

student_bp = Blueprint('student', __name__, url_prefix='/student')

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

@student_bp.route('/start', methods=['GET', 'POST'])
def start():
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        grade = int(request.form['grade'])
        subject_id = int(request.form['subject_id'])
        
        # Resume logic: Check if session already exists for this student and subject
        if session.get('student_name') == name and \
           session.get('student_surname') == surname and \
           session.get('subject_id') == subject_id and \
           'question_ids' in session:
            session.permanent = True
            return redirect(url_for('student.test'))

        session['student_name'] = name
        session['student_surname'] = surname
        session['grade'] = grade
        session['class_number'] = request.form['class_number']
        session['quarter'] = int(request.form['quarter'])
        session['subject_id'] = subject_id
        session['start_time'] = datetime.now().timestamp()
        session.permanent = True
        
        subject = Subject.query.get(session['subject_id'])
        # Store protection status in session for frontend use
        session['is_protected'] = subject.is_protected if subject else False
        
        questions = Question.query.filter_by(
            subject_id=session['subject_id'],
            grade=session['grade'],
            quarter=session['quarter']
        ).all()
        
        if len(questions) < 20:
            flash(_('Kechirasiz, bu fan va chorak uchun yetarli savollar yo\'q ({} ta mavjud)').format(len(questions)), 'danger')
            return redirect(url_for('student.start'))
        
        selected_questions = random.sample(questions, 20)
        session['question_ids'] = [q.id for q in selected_questions]
        session['current_question'] = 0
        session['answers'] = {}
        session['option_map'] = {}  # Store random order of options per question
        session['marked_questions'] = [] # For "Mark for Review"
        session['violation_count'] = 0
        session['violation_details'] = []
        
        return redirect(url_for('student.test'))
    
    subjects = Subject.query.all()
    # Translate subject names for display
    # Need access to get_locale context or just rely on jinja? 
    # In route logic we might not have `g` or request context fully bound with babel selector if logic is separate?
    # Babel context selector works globally on app.
    
    # We'll just pass subjects, template handles translation logic mostly? 
    # Or pre-process here like original app.py
    # Since we imported get_locale, we can use it.
    
    # Note: get_locale() returns Locale object or string? Flask-Babel docs say string usually.
    # Be careful, str(get_locale())
    lang = str(get_locale())
    active_test_info = None
    
    if 'question_ids' in session:
        active_subject = Subject.query.get(session.get('subject_id'))
        subject_name = active_subject.name if active_subject else ""
        if lang == 'ru' and active_subject and active_subject.name_ru:
            subject_name = active_subject.name_ru
        elif lang == 'en' and active_subject and active_subject.name_en:
            subject_name = active_subject.name_en
            
        active_test_info = {
            'name': session.get('student_name'),
            'surname': session.get('student_surname'),
            'subject': subject_name
        }

    for s in subjects:
        if lang == 'ru' and s.name_ru:
            s.display_name = s.name_ru
        elif lang == 'en' and s.name_en:
            s.display_name = s.name_en
        else:
            s.display_name = s.name
            
    return render_template('student_start.html', subjects=subjects, active_test_info=active_test_info)

@student_bp.route('/control_start', methods=['GET', 'POST'])
def control_start():
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        class_number = request.form['class_number']
        grade = int(request.form['grade'])
        quarter = int(request.form['quarter'])
        
        cws = ControlWork.query.filter_by(grade=grade, quarter=quarter, is_active=True).all()
        if not cws:
            flash(_('Siz tanlagan sinf va chorak uchun faol nazorat ishi topilmadi.'), 'danger')
            return redirect(url_for('student.control_start'))
            
        cw = cws[0] # Take the first active control work that matches
        control_work_id = cw.id
            
        # Security: check if they are resuming their active test
        if session.get('student_name') == name and \
           session.get('student_surname') == surname and \
           session.get('control_work_id') == control_work_id and \
           'question_ids' in session:
            session.permanent = True
            return redirect(url_for('student.test'))

        # Prepare new session for Control Work
        session['student_name'] = name
        session['student_surname'] = surname
        session['grade'] = cw.grade
        session['class_number'] = class_number
        session['quarter'] = cw.quarter
        session['subject_id'] = cw.subject_id
        session['control_work_id'] = cw.id
        session['start_time'] = datetime.now().timestamp()
        session['cw_time_limit'] = cw.time_limit # minutes
        session.permanent = True
        
        # Store protection status (reuse subject's protection config)
        session['is_protected'] = cw.subject.is_protected if cw.subject else False
        
        base_questions = cw.questions
        
        if not base_questions:
            flash(_('Ushbu nazorat ishida hali savollar kiritilmagan.'), 'warning')
            return redirect(url_for('student.control_start'))
            
        selected_questions = []
        if cw.quarter > 1:
            review_count = 4
            
            prev_questions = Question.query.filter(
                Question.subject_id == cw.subject_id,
                Question.grade == cw.grade,
                Question.quarter < cw.quarter
            ).all()
            
            review_sample = random.sample(prev_questions, min(len(prev_questions), review_count))
            current_count = 20 - len(review_sample)
            
            current_sample = random.sample(base_questions, min(len(base_questions), current_count))
            selected_questions = current_sample + review_sample
        else:
            selected_questions = random.sample(base_questions, min(len(base_questions), 20))
            
        # Ensure the final selection is shuffled so review questions are mixed in
        random.shuffle(selected_questions)
            
        session['question_ids'] = [q.id for q in selected_questions]
        session['current_question'] = 0
        session['answers'] = {}
        session['option_map'] = {}
        session['marked_questions'] = []
        session['violation_count'] = 0
        session['violation_details'] = []
        
        return redirect(url_for('student.test'))
    
    # GET Request
    lang = str(get_locale())
    active_test_info = None
    
    if 'question_ids' in session and session.get('control_work_id'):
        cw = ControlWork.query.get(session.get('control_work_id'))
        subject_name = cw.subject.name if cw and cw.subject else ""
        
        active_test_info = {
            'name': session.get('student_name'),
            'surname': session.get('student_surname'),
            'subject': subject_name
        }
        
    control_works = ControlWork.query.filter_by(is_active=True).order_by(ControlWork.created_at.desc()).all()
    
    return render_template('student_control_start.html', control_works=control_works, active_test_info=active_test_info)

@student_bp.route('/test')
def test():
    if 'question_ids' not in session:
        return redirect(url_for('student.start'))
    
    current = session.get('current_question', 0)
    question_ids = session['question_ids']
    
    if current >= len(question_ids):
        return redirect(url_for('student.result'))
    
    question = Question.query.get(question_ids[current])
    answers = session.get('answers', {})
    
    lang = str(get_locale())
    
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

    options = [
        {'key': 'A', 'value': option_a},
        {'key': 'B', 'value': option_b},
        {'key': 'C', 'value': option_c},
        {'key': 'D', 'value': option_d}
    ]
    # Check if options are already shuffled for this specific question view?
    # Original app shuffled every load.
    
    
    # Persistent Randomization
    question_id_str = str(question.id)
    option_map = session.get('option_map', {})
    
    # If this question hasn't been blocked yet, create a random order
    if question_id_str not in option_map:
        indices = [0, 1, 2, 3]
        random.shuffle(indices)
        option_map[question_id_str] = indices
        session['option_map'] = option_map # Save to session
    
    # Apply the stored order
    indices = option_map[question_id_str]
    # Reorder options based on stored document
    # options = [options[i] for i in indices] # Simple reorder
    # Safety check in case options size mismatches indices? (Unlikely)
    shuffled_options = [options[i] for i in indices]
    options = shuffled_options

    is_protected = session.get('is_protected', False)
    is_blocked = session.get('is_blocked', False)
    marked_questions = session.get('marked_questions', [])

    cw_time_limit = session.get('cw_time_limit')
    time_remaining_ms = None

    if cw_time_limit:
        start_time_timestamp = session.get('start_time')
        if start_time_timestamp:
            elapsed_seconds = datetime.now().timestamp() - start_time_timestamp
            total_time_seconds = cw_time_limit * 60
            remaining_seconds = total_time_seconds - elapsed_seconds
            
            if remaining_seconds <= 0:
                # Time's up, force submit
                return redirect(url_for('student.navigate', direction='finish', force='1'))
                
            time_remaining_ms = int(remaining_seconds * 1000)

    return render_template('student_test.html', 
                         question=question,
                         question_text=question_text,
                         options=options,
                         current=current + 1, 
                         total=len(question_ids),
                         question_ids=question_ids,
                         answers=answers,
                         is_protected=is_protected,
                         is_blocked=is_blocked,
                         marked_questions=marked_questions,
                         time_remaining_ms=time_remaining_ms)

@student_bp.route('/report_violation', methods=['POST'])
def report_violation():
    if 'question_ids' not in session:
        return jsonify({'error': 'Session expired'}), 400
    
    data = request.json or {}
    violation_type = data.get('type', 'Unknown')
    
    session['is_blocked'] = True
    session['violation_count'] = session.get('violation_count', 0) + 1
    
    details = session.get('violation_details', [])
    details.append({
        'type': violation_type,
        'timestamp': datetime.now().isoformat(),
        'question_index': session.get('current_question', 0) + 1
    })
    session['violation_details'] = details
    
    session.permanent = True
    return jsonify({'success': True})

@student_bp.route('/verify_unlock', methods=['POST'])
def verify_unlock():
    if 'question_ids' not in session:
        return jsonify({'error': 'Session expired'}), 400
    
    data = request.json
    password = data.get('password')
    
    # Use the same password as in the template: 'jahonschool'
    if password == 'jahonschool':
        session['is_blocked'] = False
        session.permanent = True
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Invalid password'}), 401

@student_bp.route('/answer', methods=['POST'])
def answer():
    if 'question_ids' not in session:
        return jsonify({'error': 'Session expired'}), 400
    
    data = request.json
    question_id = str(data['question_id'])
    answer = data['answer']
    
    answers = session.get('answers', {})
    answers[question_id] = answer
    session['answers'] = answers
    
    return jsonify({'success': True})

@student_bp.route('/mark_question', methods=['POST'])
def mark_question():
    if 'question_ids' not in session:
        return jsonify({'error': 'Session expired'}), 400
    
    data = request.json
    question_id = int(data['question_id'])
    marked = data.get('marked', False)
    
    marked_list = session.get('marked_questions', [])
    if marked and question_id not in marked_list:
        marked_list.append(question_id)
    elif not marked and question_id in marked_list:
        marked_list.remove(question_id)
        
    session['marked_questions'] = marked_list
    return jsonify({'success': True})

@student_bp.route('/navigate/<direction>')
def navigate(direction):
    if 'question_ids' not in session:
        return redirect(url_for('student.start'))
    
    current = session.get('current_question', 0)
    total = len(session['question_ids'])
    
    if direction == 'next' and current < total - 1:
        session['current_question'] = current + 1
    elif direction == 'prev' and current > 0:
        session['current_question'] = current - 1
    elif direction == 'finish':
        answers = session.get('answers', {})
        question_ids = session['question_ids']
        force = request.args.get('force') == '1'
        
        # Check for completeness unless forced
        if not force and len(answers) < len(question_ids):
            for idx, qid in enumerate(question_ids):
                if str(qid) not in answers:
                    session['current_question'] = idx
                    flash(_('Testni yakunlash uchun barcha savollarni belgilashingiz shart!'), 'danger')
                    return redirect(url_for('student.test'))
                    
        return redirect(url_for('student.result'))
    
    return redirect(url_for('student.test'))

@student_bp.route('/jump/<int:index>')
def jump(index):
    if 'question_ids' not in session:
        return redirect(url_for('student.start'))
    
    total = len(session['question_ids'])
    
    if 0 <= index < total:
        session['current_question'] = index
        
    return redirect(url_for('student.test'))

@student_bp.route('/result')
def result():
    if 'question_ids' not in session:
        return redirect(url_for('student.start'))
    
    question_ids = session['question_ids']
    answers = session.get('answers', {})
    
    score = 0
    results = []
    lang = str(get_locale())
    
    for qid in question_ids:
        question = Question.query.get(qid)
        user_answer = answers.get(str(qid), '')
        is_correct = str(user_answer).strip().lower() == str(question.correct_answer).strip().lower()
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
    
    start_time = session.get('start_time')
    current_time = datetime.now()
    duration_text = "00:00"
    
    if start_time:
        duration_seconds = int(current_time.timestamp() - start_time)
        mins = duration_seconds // 60
        secs = duration_seconds % 60
        duration_text = f"{mins:02d}:{secs:02d}"
    
    grade_text = calculate_grade(score, total)
    
    full_name = f"{session['student_name']} {session['student_surname']}"
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
        answers_json=json.dumps(answers),
        control_work_id=session.get('control_work_id')
    )
    db.session.add(result)
    db.session.commit()
    
    # Cleanup session but keep lang
    keys_to_keep = ['lang']
    for key in list(session.keys()):
        if key not in keys_to_keep:
            session.pop(key, None)
    
    return render_template('student_result.html', 
                         score=score, 
                         total=total, 
                         percentage=percentage,
                         grade_text=grade_text,
                         results=results)
