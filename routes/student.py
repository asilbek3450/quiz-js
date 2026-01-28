from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from flask_babel import gettext as _, get_locale
from extensions import db
from models import Subject, Question, TestResult
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
        session['student_name'] = request.form['name']
        session['student_surname'] = request.form['surname']
        session['grade'] = int(request.form['grade'])
        session['class_number'] = request.form['class_number']
        session['quarter'] = int(request.form['quarter'])
        session['subject_id'] = int(request.form['subject_id'])
        session['start_time'] = datetime.now().timestamp()
        
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
    for s in subjects:
        if lang == 'ru' and s.name_ru:
            s.display_name = s.name_ru
        elif lang == 'en' and s.name_en:
            s.display_name = s.name_en
        else:
            s.display_name = s.name
            
    return render_template('student_start.html', subjects=subjects)

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

    return render_template('student_test.html', 
                         question=question,
                         question_text=question_text,
                         options=options,
                         current=current + 1, 
                         total=len(question_ids),
                         question_ids=question_ids,
                         answers=answers,
                         is_protected=is_protected)

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
        
        # Check for completeness
        if len(answers) < len(question_ids):
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
        answers_json=json.dumps(answers)
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
