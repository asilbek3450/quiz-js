# pyright: reportAttributeAccessIssue=false, reportOptionalMemberAccess=false, reportOptionalSubscript=false, reportCallIssue=false
import os
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from flask_babel import gettext as _, get_locale
from extensions import db
from models import Subject, Question, TestResult, ControlWork, Feedback
from datetime import datetime, timedelta, timezone


def tashkent_now():
    """Hozirgi Toshkent vaqtini qaytaradi (UTC+5)."""
    return datetime.now(timezone(timedelta(hours=5)))


def to_tashkent(dt):
    """DateTime ni Toshkent vaqtiga o'tkazadi (eski UTC yozuvlar uchun ham)."""
    if dt is None:
        return dt
    return dt + timedelta(hours=5)
from feature_store import attach_question_media, get_grade_info, get_question_image_url
import random
import json

student_bp = Blueprint('student', __name__, url_prefix='/student')


# ---------- Feedback (Student side) ----------
@student_bp.route('/feedback', methods=['POST'])
def submit_feedback():
    data = request.get_json(silent=True) or {}
    user_uuid = data.get('user_uuid') or request.form.get('user_uuid')
    message = (data.get('message') or request.form.get('message') or '').strip()

    if not user_uuid or not message:
        return jsonify({'success': False, 'error': _('Xabar yoki foydalanuvchi ID topilmadi')}), 400

    # Store UUID in session so get_my_feedbacks IDOR check passes
    session['feedback_uuid'] = user_uuid

    fb = Feedback(
        user_uuid=user_uuid,
        message=message,  # legacy
        sender='student',
        text=message,
        created_at=tashkent_now(),
        is_read=False,
    )
    db.session.add(fb)
    db.session.commit()

    return jsonify({'success': True, 'message': _('Xabaringiz yuborildi'), 'id': fb.id})


@student_bp.route('/my_feedbacks/<user_uuid>')
def get_my_feedbacks(user_uuid):
    # IDOR himoya: faqat o'z UUID'i bilan so'rov qilish mumkin
    if user_uuid != session.get('feedback_uuid'):
        from flask import abort
        abort(403)
    since_id = request.args.get('since_id', 0, type=int)
    query = Feedback.query.filter_by(user_uuid=user_uuid).order_by(Feedback.created_at.asc())
    if since_id:
        query = query.filter(Feedback.id > since_id)
    feedbacks = query.all()
    return jsonify([
        {
            'id': f.id,
            'sender': f.sender or 'student',
            'text': f.text or (f.message if (f.sender or 'student') == 'student' else f.admin_response) or '',
            'created_at': to_tashkent(f.created_at).strftime('%H:%M, %d-%m'),
        }
        for f in feedbacks
        if (f.text or f.message or f.admin_response)
    ])


def _safe_sample(seq, k: int):
    if k <= 0:
        return []
    if not seq:
        return []
    return random.sample(seq, min(len(seq), k))


def _build_balanced_practice_set(subject_id: int, grade: int, quarter: int):
    subject = Subject.query.get(subject_id)
    mcq_needed = subject.question_count if subject else 20
    open_needed = subject.open_ended_count if subject else 0
    total_needed = mcq_needed + open_needed

    # ── Yillik rejim (quarter == 0): barcha choraklardagi savollar ──
    if quarter == 0:
        all_mcq = (
            Question.query.filter_by(subject_id=subject_id, grade=grade)
            .filter(Question.q_type != 'open_ended')
            .filter(~Question.control_works.any())
            .all()
        )
        all_open = (
            Question.query.filter_by(subject_id=subject_id, grade=grade, q_type='open_ended')
            .filter(~Question.control_works.any())
            .all()
        )

        if len(all_mcq) < mcq_needed:
            return None, len(all_mcq) + len(all_open)

        selected_mcq = _safe_sample(all_mcq, mcq_needed)
        selected_open = _safe_sample(all_open, open_needed)
        selected = selected_mcq + selected_open

        if len(selected) < total_needed:
            # Fill shortfall from MCQ pool
            used_ids = {q.id for q in selected}
            remaining = [q for q in all_mcq if q.id not in used_ids]
            selected.extend(_safe_sample(remaining, total_needed - len(selected)))

        if len(selected) < mcq_needed:
            return None, len(all_mcq) + len(all_open)

        random.shuffle(selected)
        return selected, len(all_mcq) + len(all_open)

    # ── Chorak rejimi (quarter 1-4): eski logika ──
    base = (
        Question.query.filter_by(subject_id=subject_id, grade=grade, quarter=quarter)
        .filter(~Question.control_works.any())
        .all()
    )

    # Split into MCQ and open-ended for this quarter
    base_mcq = [q for q in base if (q.q_type or 'mcq') != 'open_ended']
    base_open = [q for q in base if (q.q_type or 'mcq') == 'open_ended']

    min_mcq = max(mcq_needed - 5, 10)  # at least 10 MCQ from this quarter
    if len(base_mcq) < min_mcq:
        return None, len(base)

    # Review pool from previous quarters (practice-only, MCQ only)
    review_pool = []
    if quarter > 1:
        review_pool = (
            Question.query.filter(
                Question.subject_id == subject_id,
                Question.grade == grade,
                Question.quarter < quarter,
                Question.q_type != 'open_ended',
            )
            .filter(~Question.control_works.any())
            .all()
        )

    review_qs = _safe_sample(review_pool, 5)
    used_ids = {q.id for q in review_qs}

    base_medium = [q for q in base_mcq if (q.difficulty or 2) == 2 and q.id not in used_ids]
    base_hard = [q for q in base_mcq if (q.difficulty or 2) >= 3 and q.id not in used_ids]
    base_other = [q for q in base_mcq if q.id not in used_ids and q not in base_medium and q not in base_hard]

    selected = []
    selected.extend(review_qs)
    selected.extend(_safe_sample(base_medium, 10))
    used_ids.update(q.id for q in selected)

    hard_pick = _safe_sample([q for q in base_hard if q.id not in used_ids], 5)
    selected.extend(hard_pick)
    used_ids.update(q.id for q in selected)

    # Fill MCQ slots
    if len(selected) < mcq_needed:
        remaining = [q for q in base_other + base_medium + base_hard if q.id not in used_ids]
        selected.extend(_safe_sample(remaining, mcq_needed - len(selected)))

    if len(selected) < mcq_needed:
        more_review = [q for q in review_pool if q.id not in used_ids]
        selected.extend(_safe_sample(more_review, mcq_needed - len(selected)))

    if len(selected) < mcq_needed:
        return None, len(base)

    random.shuffle(selected)

    # Add open-ended questions at the end
    if open_needed > 0:
        open_pick = _safe_sample(base_open, open_needed)
        random.shuffle(open_pick)
        selected.extend(open_pick)

    return selected, len(base)

def calculate_grade(score, total=20, subject_id=None):
    percentage = (score / total) * 100 if total else 0
    return get_grade_info(percentage, subject_id)

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
        session['start_time'] = datetime.now(timezone.utc).timestamp()
        session.permanent = True
        
        subject = Subject.query.get(session['subject_id'])
        if not subject or not subject.is_visible:
            flash(_('Bu fan hozirda yopiq.'), 'danger')
            return redirect(url_for('student.start'))
            
        # Store protection status in session for frontend use
        session['is_protected'] = subject.is_protected
        
        selected_questions, base_count = _build_balanced_practice_set(
            session['subject_id'], session['grade'], session['quarter']
        )

        if not selected_questions:
            flash(_('Kechirasiz, bu fan va chorak uchun yetarli savollar yo\'q ({} ta mavjud)').format(base_count), 'danger')
            return redirect(url_for('student.start'))

        session['question_ids'] = [q.id for q in selected_questions]
        session['current_question'] = 0
        session['answers'] = {}
        session['option_map'] = {}  # Store random order of options per question
        session['marked_questions'] = [] # For "Mark for Review"
        session['violation_count'] = 0
        session['violation_details'] = []
        
        return redirect(url_for('student.test'))
    
    subjects = Subject.query.filter_by(is_visible=True).all()
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

@student_bp.route('/api/available_quarters')
def available_quarters():
    subject_id = request.args.get('subject_id', type=int)
    grade = request.args.get('grade', type=int)
    if not subject_id or not grade:
        return jsonify([])
    
    # Baza orqali shu fan va sinf uchun qaysi choraklarda savollar borligini aniqlash
    quarters = db.session.query(Question.quarter).filter_by(
        subject_id=subject_id, 
        grade=grade
    ).filter(~Question.control_works.any()).distinct().all()
    
    available = [q[0] for q in quarters if q[0] is not None]
    return jsonify(available)

@student_bp.route('/control_start', methods=['GET', 'POST'])
def control_start():
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        class_number = request.form['class_number']
        grade = int(request.form['grade'])
        quarter = int(request.form['quarter'])
        
        cws = ControlWork.query.join(Subject).filter(
            ControlWork.grade == grade,
            ControlWork.quarter == quarter,
            ControlWork.is_active == True,
            Subject.is_visible == True
        ).all()
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
        session['start_time'] = datetime.now(timezone.utc).timestamp()
        session['cw_time_limit'] = cw.time_limit # minutes
        session.permanent = True
        
        # Store protection status (reuse subject's protection config)
        session['is_protected'] = cw.subject.is_protected if cw.subject else False
        
        base_questions = cw.questions
        
        if not base_questions:
            flash(_('Ushbu nazorat ishida hali savollar kiritilmagan.'), 'warning')
            return redirect(url_for('student.control_start'))
            
        selected_questions = []
        # Review questions for control work: previous quarters' control questions
        review_sample = []
        if cw.quarter > 1:
            prev_control_questions = (
                Question.query.filter(
                    Question.subject_id == cw.subject_id,
                    Question.grade == cw.grade,
                    Question.quarter < cw.quarter,
                )
                .filter(Question.control_works.any())
                .all()
            )
            review_sample = _safe_sample(prev_control_questions, 5)

        used_ids = {q.id for q in review_sample}
        current_pool = [q for q in base_questions if q.id not in used_ids]
        current_medium = [q for q in current_pool if (q.difficulty or 2) == 2]
        current_hard = [q for q in current_pool if (q.difficulty or 2) >= 3]
        current_other = [q for q in current_pool if q not in current_medium and q not in current_hard]

        selected_questions.extend(review_sample)
        selected_questions.extend(_safe_sample(current_medium, 10))
        used_ids.update(q.id for q in selected_questions)
        selected_questions.extend(_safe_sample([q for q in current_hard if q.id not in used_ids], 5))
        used_ids.update(q.id for q in selected_questions)

        if len(selected_questions) < 20:
            remaining = [q for q in current_other + current_medium + current_hard if q.id not in used_ids]
            selected_questions.extend(_safe_sample(remaining, 20 - len(selected_questions)))
            
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
        
    control_works = ControlWork.query.join(Subject).filter(
        ControlWork.is_active == True,
        Subject.is_visible == True
    ).order_by(ControlWork.created_at.desc()).all()
    
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
    attach_question_media(question)
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
            elapsed_seconds = datetime.now(timezone.utc).timestamp() - start_time_timestamp
            total_time_seconds = cw_time_limit * 60
            remaining_seconds = total_time_seconds - elapsed_seconds
            
            if remaining_seconds <= 0:
                # Time's up, force submit
                return redirect(url_for('student.navigate', direction='finish', force='1'))
                
            time_remaining_ms = int(remaining_seconds * 1000)

    # Calculate violation end time if blocked
    violation_end_time = session.get('violation_end_time')
    if is_blocked and violation_end_time:
        now = datetime.now(timezone.utc).timestamp()
        if now >= violation_end_time:
            # Time has passed, auto-unblock
            session.pop('is_blocked', None)
            session.pop('violation_end_time', None)
            is_blocked = False
            violation_end_time = None
    
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
                         violation_end_time=violation_end_time,
                         marked_questions=marked_questions,
                         question_image_url=question.image_url,
                         time_remaining_ms=time_remaining_ms)

@student_bp.route('/report_violation', methods=['POST'])
def report_violation():
    if 'question_ids' not in session:
        return jsonify({'error': 'Session expired'}), 400
    
    # If already blocked, don't overlap violations unless it's a new one after expiry?
    # Actually, if we are already in red screen, we don't need to extend it usually.
    # But let's check current time.
    now = datetime.now(timezone.utc).timestamp()
    existing_end = session.get('violation_end_time', 0)
    
    if existing_end > now:
        return jsonify({'success': True, 'already_blocked': True})

    data = request.json or {}
    violation_type = data.get('type', 'Unknown')
    
    # Progressive penalty: 1st=15s, others=30s
    v_count = session.get('violation_count', 0)
    penalty_seconds = 15 if v_count == 0 else 30
    
    session['is_blocked'] = True
    session['violation_count'] = v_count + 1
    session['violation_end_time'] = now + penalty_seconds
    
    details = session.get('violation_details', [])
    details.append({
        'type': violation_type,
        'timestamp': tashkent_now().isoformat(),
        'question_index': session.get('current_question', 0) + 1,
        'penalty': penalty_seconds
    })
    session['violation_details'] = details
    
    session.permanent = True
    return jsonify({
        'success': True, 
        'penalty_seconds': penalty_seconds,
        'violation_end_time': session['violation_end_time']
    })

@student_bp.route('/clear_violation', methods=['POST'])
def clear_violation():
    # Only clear if time has actually passed
    now = datetime.now(timezone.utc).timestamp()
    end_time = session.get('violation_end_time', 0)
    
    if now >= end_time:
        session.pop('is_blocked', None)
        session.pop('violation_end_time', None)
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'remaining': int(end_time - now)})


@student_bp.route('/verify_unlock', methods=['POST'])
def verify_unlock():
    if 'question_ids' not in session:
        return jsonify({'error': 'Session expired'}), 400
    
    data = request.json
    password = data.get('password')
    
    unlock_password = os.environ.get('UNLOCK_PASSWORD', 'jahonschool')
    if password == unlock_password:
        session['is_blocked'] = False
        session.permanent = True
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': _('Parol noto\'g\'ri')}), 401

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
    
    mcq_score = 0
    open_ended_score = 0
    is_graded = True
    results = []
    lang = str(get_locale())
    subject_id = session['subject_id']
    
    # N+1 oldini olish: barcha savollarni bitta query bilan olamiz
    questions_map = {q.id: q for q in Question.query.filter(Question.id.in_(question_ids)).all()}

    for qid in question_ids:
        question = questions_map.get(qid)
        if not question:
            continue
        user_answer = answers.get(str(qid), '').strip().lower()
        
        visual_user_answer = ''
        visual_correct_answer = ''
        is_correct = False
        is_open_ended = question.q_type == 'open_ended'
        
        if not is_open_ended:
            correct_answer = str(question.correct_answer).strip().lower()
            is_correct = user_answer == correct_answer
            if is_correct:
                mcq_score += 1
        else:
            is_graded = False
        
        if lang == 'ru':
             q_text_display = question.question_text_ru or question.question_text
        elif lang == 'en':
             q_text_display = question.question_text_en or question.question_text
        else:
             q_text_display = question.question_text

        # We save what the user sent
        actual_answer_key = user_answer
        answers[str(qid)] = actual_answer_key
        
        # Calculate visual label for display
        option_map = session.get('option_map', {})
        db_keys = ['a', 'b', 'c', 'd']
        
        if is_open_ended:
            visual_user_answer = answers.get(str(qid), '')
            visual_correct_answer = _("O'qituvchi tekshirishi kutilmoqda")
            is_correct = None # null indicates pending
        elif str(qid) in option_map:
            if user_answer in db_keys:
                orig_idx = db_keys.index(user_answer)
                try:
                    vis_idx = option_map[str(qid)].index(orig_idx)
                    visual_user_answer = db_keys[vis_idx].upper()
                except ValueError:
                    visual_user_answer = user_answer.upper()
                    
            if correct_answer in db_keys:
                orig_correct_idx = db_keys.index(correct_answer)
                try:
                    vis_correct_idx = option_map[str(qid)].index(orig_correct_idx)
                    visual_correct_answer = db_keys[vis_correct_idx].upper()
                except ValueError:
                    visual_correct_answer = correct_answer.upper()
        else:
            visual_user_answer = user_answer.upper() if user_answer else ''
            visual_correct_answer = correct_answer.upper()
        
        results.append({
            'question': q_text_display,
            'image_url': get_question_image_url(qid),
            'user_answer': visual_user_answer, 
            'correct_answer': visual_correct_answer, 
            'is_correct': is_correct,
            'q_type': question.q_type
        })
    
    total = len(question_ids)
    score = mcq_score + open_ended_score
    percentage = (score / total) * 100 if total > 0 else 0
    
    start_time = session.get('start_time')
    duration_text = "00:00"

    if start_time:
        duration_seconds = int(datetime.now(timezone.utc).timestamp() - start_time)
        mins = duration_seconds // 60
        secs = duration_seconds % 60
        duration_text = f"{mins:02d}:{secs:02d}"
    
    grade_info = calculate_grade(score, total, subject_id)
    grade_text = grade_info['label']
    
    full_name = f"{session['student_name']} {session['student_surname']}"
    tashkent_time = tashkent_now()
    
    result = TestResult(
        full_name=full_name,
        grade=session['grade'],
        class_number=session['class_number'],
        quarter=session['quarter'],
        subject_id=subject_id,
        score=score,
        mcq_score=mcq_score,
        open_ended_score=open_ended_score,
        is_graded=is_graded,
        total_questions=total,
        percentage=percentage,
        grade_text=grade_text,
        test_date=tashkent_time,
        answers_json=json.dumps(answers),
        control_work_id=session.get('control_work_id')
    )
    db.session.add(result)
    db.session.commit()
    
    subject = Subject.query.get(subject_id)
    show_detailed_results = subject.show_results if subject else True
    
    # Cleanup session but keep lang
    keys_to_keep = ['lang']
    for key in list(session.keys()):
        if key not in keys_to_keep:
            session.pop(key, None)
    
    return render_template('student_result.html', 
                         score=score, 
                         is_graded=is_graded,
                         total=total, 
                         percentage=percentage,
                         grade_info=grade_info,
                         grade_text=grade_text,
                         results=results,
                         show_results=show_detailed_results)
