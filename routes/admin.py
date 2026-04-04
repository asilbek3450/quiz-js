from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from flask_babel import gettext as _
from werkzeug.security import check_password_hash
from extensions import db
from models import Admin, Subject, Question, TestResult, ControlWork, Feedback
from feature_store import (
    attach_question_media,
    delete_question_image_file,
    get_grade_info,
    get_question_image_relative_path,
    get_question_image_url,
    get_subject_grade_settings,
    remove_question_image,
    remove_subject_grade_settings,
    save_question_image_upload,
    set_question_image,
    set_subject_grade_settings,
    validate_grade_settings,
)
from deep_translator import GoogleTranslator
from datetime import datetime, timedelta


def tashkent_now():
    """Hozirgi Toshkent vaqtini qaytaradi (UTC+5)."""
    return datetime.utcnow() + timedelta(hours=5)


def to_tashkent(dt):
    """DateTime ni Toshkent vaqtiga o'tkazadi (eski UTC yozuvlar uchun ham)."""
    if dt is None:
        return dt
    return dt + timedelta(hours=5)
import json
from sqlalchemy import func
from functools import wraps
import secrets
import string
from werkzeug.security import generate_password_hash
# import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def staff_required(f):
    """Allow any authenticated staff (admin or teacher)."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if 'admin_id' not in session:
            if is_ajax or request.is_json:
                return jsonify({'success': False, 'error': _('Tizimga kirish talab qilinadi')}), 401
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if 'admin_id' not in session:
            if is_ajax:
                return jsonify({'success': False, 'error': _('Tizimga kirish talab qilinadi')}), 401
            return redirect(url_for('admin.login'))
        if session.get('admin_role') != 'admin':
            if is_ajax:
                return jsonify({'success': False, 'error': _('Bu amalni bajarish uchun admin huquqi kerak')}), 403
            flash(_('Bu amalni bajarish uchun admin huquqi kerak'), 'danger')
            return redirect(url_for('admin.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/feedbacks')
@admin_bp.route('/feedbacks/<user_uuid>')
@staff_required
def feedbacks(user_uuid=None):
    # Group by user_uuid and get the latest message for each
    subquery = db.session.query(
        Feedback.user_uuid,
        func.max(Feedback.created_at).label('latest_msg')
    ).group_by(Feedback.user_uuid).subquery()

    conversations = db.session.query(Feedback).join(
        subquery, (Feedback.user_uuid == subquery.c.user_uuid) & (Feedback.created_at == subquery.c.latest_msg)
    ).order_by(Feedback.created_at.desc()).all()

    # Get unread counts for each user
    unread_counts = db.session.query(
        Feedback.user_uuid,
        func.count(Feedback.id)
    ).filter(Feedback.is_read == False).group_by(Feedback.user_uuid).all()
    unread_map = {u[0]: u[1] for u in unread_counts}

    active_messages = []
    if user_uuid:
        active_messages = Feedback.query.filter_by(user_uuid=user_uuid).order_by(Feedback.created_at.asc()).all()
        # Mark as read for this specific user
        Feedback.query.filter_by(user_uuid=user_uuid, is_read=False).update({Feedback.is_read: True})
        db.session.commit()
    
    return render_template('admin_feedbacks.html', 
                           conversations=conversations, 
                           active_messages=active_messages,
                           active_uuid=user_uuid,
                           unread_map=unread_map)

@admin_bp.route('/api/feedback/conversations')
@staff_required
def api_conversations():
    # Similar grouping to feedbacks route but returns JSON
    subquery = db.session.query(
        Feedback.user_uuid,
        func.max(Feedback.created_at).label('latest_msg')
    ).group_by(Feedback.user_uuid).subquery()

    conversations = db.session.query(Feedback).join(
        subquery, (Feedback.user_uuid == subquery.c.user_uuid) & (Feedback.created_at == subquery.c.latest_msg)
    ).order_by(Feedback.created_at.desc()).all()

    unread_counts = db.session.query(
        Feedback.user_uuid,
        func.count(Feedback.id)
    ).filter(Feedback.is_read == False).group_by(Feedback.user_uuid).all()
    unread_map = {u[0]: u[1] for u in unread_counts}

    return jsonify([{
        'user_uuid': c.user_uuid,
        'message': (c.text or c.message or c.admin_response or ''),
        'created_at': to_tashkent(c.created_at).strftime('%H:%M'),
        'unread_count': unread_map.get(c.user_uuid, 0)
    } for c in conversations])

@admin_bp.route('/api/feedback/messages/<user_uuid>')
@staff_required
def api_messages(user_uuid):
    since_id = request.args.get('since_id', type=int)
    
    query = Feedback.query.filter_by(user_uuid=user_uuid).order_by(Feedback.created_at.asc())
    if since_id:
        query = query.filter(Feedback.id > since_id)
        
    messages = query.all()
    
    # Mark as read when fetched via API too
    if messages:
        Feedback.query.filter_by(user_uuid=user_uuid, is_read=False).update({Feedback.is_read: True})
        db.session.commit()
    
    return jsonify([{
        'id': m.id,
        'sender': m.sender or 'student',
        'text': (m.text or m.message or m.admin_response or ''),
        'created_at': to_tashkent(m.created_at).strftime('%H:%M, %d-%m'),
    } for m in messages if (m.text or m.message or m.admin_response)])

@admin_bp.route('/feedback/respond/<user_uuid>', methods=['POST'])
@staff_required
def respond_feedback(user_uuid):
    response_text = request.form.get('response', '').strip()
    is_ajax = (
        request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        or request.args.get('ajax') == '1'
        or request.form.get('ajax') == '1'
        or request.is_json
    )
    
    if response_text:
        msg = Feedback(
            user_uuid=user_uuid,
            message='',  # legacy non-null column
            sender='admin',
            text=response_text,
            is_read=True,
            created_at=tashkent_now(),
        )
        db.session.add(msg)
        db.session.commit()

        if is_ajax:
            return jsonify({
                'success': True,
                'message': _('Javobingiz muvaffaqiyatli yuborildi'),
            })
        flash(_('Javobingiz muvaffaqiyatli yuborildi'), 'success')
    else:
        if is_ajax:
            return jsonify({'success': False, 'error': _('Javob matni bo\'sh bo\'lmasligi kerak')}), 400
        flash(_('Javob matni bo\'sh bo\'lmasligi kerak'), 'warning')
    
    return redirect(url_for('admin.feedbacks', user_uuid=user_uuid))

@admin_bp.route('/feedback/clear/<user_uuid>', methods=['POST', 'DELETE'])
@admin_required
def clear_feedback(user_uuid):
    """Delete all feedback messages for a user (single conversation). Supports AJAX/JSON, DELETE, and regular POST."""
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json
    try:
        Feedback.query.filter_by(user_uuid=user_uuid).delete()
        db.session.commit()
        if is_ajax or request.method == 'DELETE':
            return jsonify({'success': True, 'message': _('Chat muvaffaqiyatli tozalandi')})
        flash(_('Chat muvaffaqiyatli tozalandi'), 'success')
        return redirect(url_for('admin.feedbacks'))
    except Exception as e:
        db.session.rollback()
        if is_ajax or request.method == 'DELETE':
            return jsonify({'success': False, 'error': str(e)}), 500
        flash(_('Chatni o‘chirishda xatolik: {}').format(str(e)), 'danger')
        return redirect(url_for('admin.feedbacks', user_uuid=user_uuid))

@admin_bp.route('/api/feedback/bulk-delete', methods=['POST', 'DELETE'])
@admin_required
def bulk_delete_feedback():
    """Bulk delete conversations. Works with JSON payload or form-data (user_uuids)."""
    data = request.get_json(silent=True) or {}
    user_uuids = data.get('user_uuids')
    if not user_uuids:
        user_uuids = request.form.getlist('user_uuids')
    if not user_uuids:
        error_msg = _('Hech qanday chat tanlanmadi')
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.method == 'DELETE':
            return jsonify({'success': False, 'error': error_msg}), 400
        flash(error_msg, 'warning')
        return redirect(url_for('admin.feedbacks'))
    
    try:
        Feedback.query.filter(Feedback.user_uuid.in_(user_uuids)).delete(synchronize_session=False)
        db.session.commit()
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.method == 'DELETE':
            return jsonify({'success': True, 'message': _('Tanlangan chatlar muvaffaqiyatli o\'chirildi')})
        flash(_('Tanlangan chatlar muvaffaqiyatli o\'chirildi'), 'success')
        return redirect(url_for('admin.feedbacks'))
    except Exception as e:
        db.session.rollback()
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.method == 'DELETE':
            return jsonify({'success': False, 'error': str(e)}), 500
        flash(_('Chatlarni o‘chirishda xatolik: {}').format(str(e)), 'danger')
        return redirect(url_for('admin.feedbacks'))

@admin_bp.route('/api/feedback/clear-all', methods=['POST', 'DELETE'])
@admin_required
def clear_all_feedback():
    """Delete every feedback conversation. Supports JSON/DELETE and form POST."""
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json
    try:
        Feedback.query.delete()
        db.session.commit()
        if is_ajax or request.method == 'DELETE':
            return jsonify({'success': True, 'message': _('Barcha chatlar muvaffaqiyatli tozalandi')})
        flash(_('Barcha chatlar muvaffaqiyatli tozalandi'), 'success')
        return redirect(url_for('admin.feedbacks'))
    except Exception as e:
        db.session.rollback()
        if is_ajax or request.method == 'DELETE':
            return jsonify({'success': False, 'error': str(e)}), 500
        flash(_('Barcha chatlarni o‘chirishda xatolik: {}').format(str(e)), 'danger')
        return redirect(url_for('admin.feedbacks'))

@admin_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    admin = Admin.query.get_or_404(session['admin_id'])
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        phone = request.form.get('phone_number')
        email = request.form.get('email')
        new_password = request.form.get('new_password')
        
        admin.full_name = full_name
        admin.phone_number = phone
        admin.email = email
        
        if new_password:
            if len(new_password) < 6:
                flash(_('Parol kamida 6 ta belgidan iborat bo\'lishi kerak'), 'danger')
            else:
                admin.password_hash = generate_password_hash(new_password)
                flash(_('Parol muvaffaqiyatli yangilandi'), 'success')
        
        db.session.commit()
        flash(_('Profil ma\'lumotlari yangilandi'), 'success')
        return redirect(url_for('admin.profile'))
        
    return render_template('admin_profile.html', admin=admin)

def auto_translate(text, target):
    if not text or not target:
        return text
    try:
        # Use a timeout and handle empty strings
        translator = GoogleTranslator(source='auto', target=target)
        return translator.translate(text)
    except Exception as e:
        print(f"Translation error ({target}): {e}")
        return text



@admin_bp.before_request
def require_login():
    # Only login route is allowed without check
    if request.endpoint == 'admin.login':
        return
        
    if 'admin_id' not in session:
        return redirect(url_for('admin.login'))

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'admin_id' in session:
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password_hash, password):
            session['admin_id'] = admin.id
            session['admin_name'] = admin.full_name
            session['admin_role'] = admin.role or 'teacher'
            flash(_('Xush kelibsiz {}!').format(admin.full_name), 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash(_('Login yoki parol noto\'g\'ri'), 'danger')

    return render_template('admin_login.html')

@admin_bp.route('/logout')
def logout():
    session.pop('admin_id', None)
    session.pop('admin_name', None)
    session.pop('admin_role', None)
    flash(_('Tizimdan chiqdingiz'), 'info')
    return redirect(url_for('main.index'))

@admin_bp.route('/dashboard')
def dashboard():
    total_questions = Question.query.count()
    subjects = Subject.query.all()
    recent_results = TestResult.query.order_by(TestResult.test_date.desc()).limit(10).all()
    result_stats = TestResult.query.with_entities(TestResult.subject_id, TestResult.percentage).all()
    total_results = len(result_stats)

    for result in recent_results:
        result.grade_info = get_grade_info(result.percentage, result.subject_id)

    # Passing means "qoniqarli" or higher for the given subject.
    passing_results_count = sum(
        1 for subject_id, percentage in result_stats
        if get_grade_info(percentage, subject_id)['level'] != 'fail'
    )
    pass_rate = (passing_results_count / total_results * 100) if total_results > 0 else 0

    # Subject Analytics using aggregation
    subject_stats_raw = db.session.query(
        TestResult.subject_id,
        func.count(TestResult.id)
    ).group_by(TestResult.subject_id).all()
    
    res_counts_map = {sid: count for sid, count in subject_stats_raw}
    
    subject_names = [s.name for s in subjects]
    question_counts = [Question.query.filter_by(subject_id=s.id).count() for s in subjects]
    result_counts = [res_counts_map.get(s.id, 0) for s in subjects]

    # Analytics: Top 5 Difficult Questions (Limit to last 500 results for performance)
    difficult_questions_data = []
    try:
        recent_analytics_results = TestResult.query.order_by(TestResult.test_date.desc()).limit(500).all()
        
        if recent_analytics_results:
            question_stats = {} # {question_id: {'wrong': 0, 'total': 0}}
            all_q_ids_set = set()
            
            for r in recent_analytics_results:
                try:
                    answers = json.loads(r.answers_json or '{}')
                    if not isinstance(answers, dict): continue
                    for q_id, user_ans in answers.items():
                        try:
                            q_id_int = int(q_id)
                            if q_id_int not in question_stats:
                                question_stats[q_id_int] = {'wrong': 0, 'total': 0}
                            question_stats[q_id_int]['total'] += 1
                            all_q_ids_set.add(q_id_int)
                        except (ValueError, TypeError): continue
                except: continue

            if all_q_ids_set:
                # Chunk IDs to avoid SQLite limit (usually 999 variables)
                all_q_ids = list(all_q_ids_set)
                questions_db = {}
                chunk_size = 500
                for i in range(0, len(all_q_ids), chunk_size):
                    chunk = all_q_ids[i:i + chunk_size]
                    qs = Question.query.filter(Question.id.in_(chunk)).all()
                    for q in qs:
                        questions_db[q.id] = q
                
                for r in recent_analytics_results:
                    try:
                        answers = json.loads(r.answers_json or '{}')
                        if not isinstance(answers, dict): continue
                        for q_id, user_ans in answers.items():
                            try:
                                q_id_int = int(q_id)
                                q_obj = questions_db.get(q_id_int)
                                if q_obj and user_ans != q_obj.correct_answer:
                                    question_stats[q_id_int]['wrong'] += 1
                            except: continue
                    except: continue

                for q_id, stats in question_stats.items():
                    if stats['total'] > 3: # Lower threshold for limited sample
                        stats['fail_rate'] = (stats['wrong'] / stats['total']) * 100
                        q_obj = questions_db.get(q_id)
                        if q_obj:
                            difficult_questions_data.append({
                                'text': q_obj.question_text[:100] + '...',
                                'fail_rate': stats['fail_rate'],
                                'wrong_count': stats['wrong'],
                                'total_count': stats['total'],
                                'subject': q_obj.subject.name if q_obj.subject else _('Noma\'lum')
                            })
                difficult_questions_data = sorted(difficult_questions_data, key=lambda x: x['fail_rate'], reverse=True)[:5]
    except Exception as e:
        # Prevent analytics errors from crashing the dashboard
        print(f"Analytics error: {e}")
        difficult_questions_data = []

    return render_template('admin_dashboard.html',
                         total_questions=total_questions,
                         total_results=total_results,
                         subjects=subjects,
                         recent_results=recent_results,
                         subject_names=subject_names,
                         question_counts=question_counts,
                         result_counts=result_counts,
                         pass_rate=pass_rate,
                         difficult_questions=difficult_questions_data)

@admin_bp.route('/questions')
def questions():
    subject_id = request.args.get('subject_id', type=int)
    grade = request.args.get('grade', type=int)
    quarter = request.args.get('quarter', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = 25

    query = Question.query
    if subject_id:
        query = query.filter_by(subject_id=subject_id)
    if grade:
        query = query.filter_by(grade=grade)
    if quarter:
        query = query.filter_by(quarter=quarter)
        
    is_control_work = request.args.get('is_control_work')
    if is_control_work == '1':
        query = query.filter(Question.control_works.any())
    elif is_control_work == '0':
        query = query.filter(~Question.control_works.any())

    search = request.args.get('search')
    if search:
        search_term = f"%{search}%"
        query = query.filter(Question.question_text.ilike(search_term))

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    questions = pagination.items
    for question in questions:
        attach_question_media(question)

    # Efficiently get statistics using aggregation
    stats_raw = db.session.query(
        Question.subject_id, 
        Question.grade, 
        Question.quarter, 
        func.count(Question.id)
    ).group_by(Question.subject_id, Question.grade, Question.quarter).all()

    # Convert to a dictionary for easier access in template
    stats_dict = {}
    for sid, grade, quarter, count in stats_raw:
        if sid not in stats_dict: stats_dict[sid] = {}
        if grade not in stats_dict[sid]: stats_dict[sid][grade] = {}
        stats_dict[sid][grade][quarter] = count

    subjects = Subject.query.all()

    return render_template('admin_questions.html',
                         questions=questions,
                         stats_dict=stats_dict,
                         pagination=pagination,
                         subjects=subjects)

@admin_bp.route('/question/add', methods=['GET', 'POST'])
def question_add():
    if request.method == 'POST':
        uploaded_image = request.files.get('question_image')
        saved_image_path = None
        question_id = None
        try:
            subject_id = int(request.form.get('subject_id', 0))
            grade = int(request.form.get('grade', 0))
            quarter = int(request.form.get('quarter', 0))
            q_text = request.form.get('question_text', '').strip()
            opt_a = request.form.get('option_a', '').strip()
            opt_b = request.form.get('option_b', '').strip()
            opt_c = request.form.get('option_c', '').strip()
            opt_d = request.form.get('option_d', '').strip()
            correct = request.form.get('correct_answer', '').upper().strip()

            if not all([subject_id, grade, quarter, q_text, opt_a, opt_b, opt_c, opt_d, correct]):
                flash(_('Barcha maydonlarni to\'ldiring'), 'warning')
                return redirect(url_for('admin.question_add'))

            subject = Subject.query.get(subject_id)
            if not subject:
                flash(_('Fan topilmadi'), 'danger')
                return redirect(url_for('admin.question_add'))

            question = Question(
                subject_id=subject_id,
                grade=grade,
                quarter=quarter,
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
                correct_answer=correct
            )
            db.session.add(question)
            db.session.flush()
            question_id = question.id

            if uploaded_image and uploaded_image.filename:
                saved_image_path = save_question_image_upload(uploaded_image)
                set_question_image(question_id, saved_image_path)

            db.session.commit()
            flash(_('Savol muvaffaqiyatli qo\'shildi va tarjima qilindi'), 'success')
            return redirect(url_for('admin.questions'))
        except Exception as e:
            db.session.rollback()
            if question_id and saved_image_path:
                remove_question_image(question_id)
                delete_question_image_file(saved_image_path)
            flash(_('Xatolik yuz berdi: {}').format(str(e)), 'danger')
            return redirect(url_for('admin.question_add'))

    subjects = Subject.query.all()
    return render_template('admin_question_form.html', subjects=subjects, question=None, question_image_url=None)

@admin_bp.route('/question/edit/<int:id>', methods=['GET', 'POST'])
def question_edit(id):
    question = Question.query.get_or_404(id)
    attach_question_media(question)

    if request.method == 'POST':
        uploaded_image = request.files.get('question_image')
        remove_existing_image = request.form.get('remove_image') == '1'
        previous_image_path = get_question_image_relative_path(question.id)
        saved_image_path = None
        image_store_updated = False

        try:
            question.subject_id = int(request.form['subject_id'])
            question.grade = int(request.form['grade'])
            question.quarter = int(request.form['quarter'])

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

            if uploaded_image and uploaded_image.filename:
                saved_image_path = save_question_image_upload(uploaded_image)
                set_question_image(question.id, saved_image_path)
                image_store_updated = True
            elif remove_existing_image and previous_image_path:
                remove_question_image(question.id)
                image_store_updated = True

            db.session.commit()

            try:
                if saved_image_path and previous_image_path:
                    delete_question_image_file(previous_image_path)
                elif remove_existing_image and previous_image_path:
                    delete_question_image_file(previous_image_path)
            except Exception as cleanup_error:
                print(f"Question image cleanup warning: {cleanup_error}")

            flash(_('Savol muvaffaqiyatli o\'zgartirildi'), 'success')
            return redirect(url_for('admin.questions'))
        except Exception as e:
            db.session.rollback()
            if saved_image_path:
                delete_question_image_file(saved_image_path)
            if image_store_updated:
                if previous_image_path:
                    set_question_image(question.id, previous_image_path)
                else:
                    remove_question_image(question.id)
            flash(_('Xatolik yuz berdi: {}').format(str(e)), 'danger')
            return redirect(url_for('admin.question_edit', id=id))
    subjects = Subject.query.all()
    return render_template(
        'admin_question_form.html',
        subjects=subjects,
        question=question,
        question_image_url=question.image_url,
    )

@admin_bp.route('/questions/translate_missing', methods=['POST'])
def translate_missing_questions():
    try:
        subject_id = request.json.get('subject_id')
        grade = request.json.get('grade')
        quarter = request.json.get('quarter')
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400
        
@admin_bp.route('/question/delete/<int:id>', methods=['GET'])
@admin_required
def question_delete(id):
    question = Question.query.get_or_404(id)
    existing_image_path = get_question_image_relative_path(question.id)
    db.session.delete(question)
    db.session.commit()

    try:
        removed_image_path = remove_question_image(question.id)
        delete_question_image_file(removed_image_path or existing_image_path)
    except Exception as cleanup_error:
        print(f"Question image cleanup warning: {cleanup_error}")
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return {'success': True}
        
    flash(_('Savol o\'chirildi'), 'success')
    return redirect(url_for('admin.questions'))

@admin_bp.route('/import/questions', methods=['POST'])
def import_questions():
    try:
        if 'file' not in request.files:
            flash(_('Fayl tanlanmagan'), 'danger')
            return redirect(url_for('admin.questions'))

        file = request.files['file']
        if file.filename == '':
            flash(_('Fayl tanlanmagan'), 'danger')
            return redirect(url_for('admin.questions'))

        if not file.filename.lower().endswith(('.xlsx', '.xls')):
            flash(_('Faqat Excel (.xlsx, .xls) fayllari qabul qilinadi'), 'danger')
            return redirect(url_for('admin.questions'))

        subject_id = request.form.get('subject_id', type=int)
        grade = request.form.get('grade', type=int)
        quarter = request.form.get('quarter', type=int)

        if not all([subject_id, grade, quarter]):
            flash(_('Fan, sinf va chorakni tanlang'), 'warning')
            return redirect(url_for('admin.questions'))

        subject = Subject.query.get(subject_id)
        if not subject:
            flash(_('Fan topilmadi'), 'danger')
            return redirect(url_for('admin.questions'))

        import pandas as pd
        try:
            # Using engine='openpyxl' for modern excel files
            df = pd.read_excel(file)
        except Exception as e:
            flash(_('Excel faylini o\'qishda xatolik: {}').format(str(e)), 'danger')
            return redirect(url_for('admin.questions'))

        if df.empty:
            flash(_('Fayl bo\'sh'), 'warning')
            return redirect(url_for('admin.questions'))

        # Strip whitespace from column names and handle potential case mismatch
        df.columns = [str(col).strip() for col in df.columns]

        required_cols = ['Question', 'A', 'B', 'C', 'D', 'Correct']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            flash(_('Fayl ustunlari noto\'g\'ri! Quyidagilar yetishmayapti: {}').format(", ".join(missing_cols)), 'danger')
            return redirect(url_for('admin.questions'))

        # Handle NaN values early
        df = df.fillna('')

        count = 0
        skipped = 0
        for index, row in df.iterrows():
            q_text = str(row['Question']).strip()
            opt_a = str(row['A']).strip()
            opt_b = str(row['B']).strip()
            opt_c = str(row['C']).strip()
            opt_d = str(row['D']).strip()
            correct = str(row['Correct']).upper().strip()

            if not q_text or not correct or correct not in ['A', 'B', 'C', 'D']:
                skipped += 1
                continue

            question = Question(
                subject_id=subject_id,
                grade=grade,
                quarter=quarter,
                question_text=q_text,
                option_a=opt_a,
                option_b=opt_b,
                option_c=opt_c,
                option_d=opt_d,
                correct_answer=correct
            )
            # Translations are now LAZY or BATCHED to avoid timeouts during import
            db.session.add(question)
            count += 1

        db.session.commit()
        msg = _('{} ta savol muvaffaqiyatli yuklandi').format(count)
        if skipped > 0:
            msg += _('. {} ta qator noto\'g\'ri ma\'lumot sababli tashlab ketildi').format(skipped)
        flash(msg, 'success')

    except Exception as e:
        db.session.rollback()
        flash(_('Xatolik yuz berdi: {}').format(str(e)), 'danger')

    return redirect(url_for('admin.questions'))

    return redirect(url_for('admin.questions'))

    return redirect(url_for('admin.questions'))

@admin_bp.route('/download/template')
def download_template():
    import pandas as pd
    from io import BytesIO
    from flask import send_file

    # Create sample data
    data = [
        {
            'Question': "O'zbekiston poytaxti qaysi shahar?",
            'A': 'Samarqand',
            'B': 'Toshkent',
            'C': 'Buxoro',
            'D': 'Xiva',
            'Correct': 'B'
        },
        {
            'Question': "2 + 2 = ?",
            'A': '3',
            'B': '5',
            'C': '4',
            'D': '10',
            'Correct': 'C'
        },
        {
            'Question': "Water chemical formula?",
            'A': 'H2O',
            'B': 'CO2',
            'C': 'O2',
            'D': 'N2',
            'Correct': 'A'
        }
    ]

    df = pd.DataFrame(data)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Template')

        # Auto-adjust column width (approximate)
        worksheet = writer.sheets['Template']
        for idx, col in enumerate(df.columns):
            max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.column_dimensions[chr(65 + idx)].width = max_len

    output.seek(0)

    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='savollar_namuna.xlsx'
    )

@admin_bp.route('/export/results')
def export_results():
    import pandas as pd
    from io import BytesIO
    from flask import send_file

    subject_id = request.args.get('subject_id', type=int)
    grade = request.args.get('grade', type=int)
    quarter = request.args.get('quarter', type=int)
    control_work_id = request.args.get('control_work_id', type=int)
    filter_date = request.args.get('filter_date')
    sort_by = request.args.get('sort_by', 'newest')

    query = TestResult.query
    if subject_id:
        query = query.filter_by(subject_id=subject_id)
    if grade:
        query = query.filter_by(grade=grade)
    if quarter:
        query = query.filter_by(quarter=quarter)
    if control_work_id:
        query = query.filter_by(control_work_id=control_work_id)

    if filter_date:
        try:
            target_date = datetime.strptime(filter_date, '%Y-%m-%d').date()
            start_dt = datetime.combine(target_date, datetime.min.time())
            end_dt = datetime.combine(target_date, datetime.max.time())
            query = query.filter(TestResult.test_date >= start_dt, TestResult.test_date <= end_dt)
        except:
            pass

    if sort_by == 'score_desc':
        query = query.order_by(TestResult.score.desc())
    elif sort_by == 'score_asc':
        query = query.order_by(TestResult.score.asc())
    else: # newest
        query = query.order_by(TestResult.test_date.desc())

    results = query.all()

    data = []
    for r in results:
        grade_info = get_grade_info(r.percentage, r.subject_id)
        data.append({
            _('Ism Familiya'): r.full_name,
            _('Fan'): r.subject.name if r.subject else '',
            _('Sinf'): f"{r.grade}-{r.class_number}",
            _('Chorak'): r.quarter,
            _('Ball'): r.score,
            _('Jami savollar'): r.total_questions,
            _('Foiz'): f"{int(r.percentage)}%",
            _('Baho'): grade_info['label'],
            _('Sana'): to_tashkent(r.test_date).strftime('%Y-%m-%d %H:%M')
        })

    df = pd.DataFrame(data)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Natijalar')

    output.seek(0)

    filename = f"results_{tashkent_now().strftime('%Y%m%d_%H%M')}.xlsx"
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )

@admin_bp.route('/results')
def results():
    subject_id = request.args.get('subject_id', type=int)
    grade = request.args.get('grade', type=int)
    quarter = request.args.get('quarter', type=int)
    control_work_id = request.args.get('control_work_id', type=int)

    filter_date = request.args.get('filter_date')
    sort_by = request.args.get('sort_by', 'newest')

    query = TestResult.query
    if subject_id:
        query = query.filter_by(subject_id=subject_id)
    if grade:
        query = query.filter_by(grade=grade)
    if quarter:
        query = query.filter_by(quarter=quarter)
    if control_work_id:
        query = query.filter_by(control_work_id=control_work_id)

    if filter_date:
        try:
            target_date = datetime.strptime(filter_date, '%Y-%m-%d').date()
            start_dt = datetime.combine(target_date, datetime.min.time())
            end_dt = datetime.combine(target_date, datetime.max.time())
            query = query.filter(TestResult.test_date >= start_dt, TestResult.test_date <= end_dt)
        except:
            pass

    if sort_by == 'score_desc':
        query = query.order_by(TestResult.score.desc())
    elif sort_by == 'score_asc':
        query = query.order_by(TestResult.score.asc())
    else: # newest
        query = query.order_by(TestResult.test_date.desc())

    # Calculate stats before pagination on the filtered result set.
    filtered_stats = query.with_entities(TestResult.subject_id, TestResult.percentage).all()
    total_count = len(filtered_stats)
    excellent_count = sum(
        1 for subject_id, percentage in filtered_stats
        if get_grade_info(percentage, subject_id)['level'] == 'excellent'
    )

    stats_tuple = query.with_entities(
        func.avg(TestResult.percentage),
        func.avg(TestResult.score)
    ).first()
    
    avg_percentage = stats_tuple[0] or 0
    avg_score = stats_tuple[1] or 0

    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 100
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    results = pagination.items
    for result in results:
        result.grade_info = get_grade_info(result.percentage, result.subject_id)
        result.display_grade_text = result.grade_info['label']

    subjects = Subject.query.all()
    control_works_list = ControlWork.query.order_by(ControlWork.created_at.desc()).all()

    return render_template('admin_results.html',
                         results=results,
                         pagination=pagination,
                         subjects=subjects,
                         control_works_list=control_works_list,
                         total_count=total_count,
                         excellent_count=excellent_count,
                         avg_percentage=round(avg_percentage, 1),
                         avg_score=round(avg_score, 1))

@admin_bp.route('/result/delete/<int:id>', methods=['POST'])
@admin_required
def result_delete(id):
    result = TestResult.query.get_or_404(id)
    db.session.delete(result)
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return {'success': True}
        
    flash(_('Natija muvaffaqiyatli o\'chirildi'), 'success')
    return redirect(url_for('admin.results'))

@admin_bp.route('/results/delete-by-date', methods=['POST'])
@admin_required
def results_delete_by_date():
    date_str = request.form['delete_date']
    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
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

    return redirect(url_for('admin.results'))

@admin_bp.route('/subjects')
def subjects():
    subjects = Subject.query.all()
    for subject in subjects:
        subject.grade_settings = get_subject_grade_settings(subject.id)
    return render_template('admin_subjects.html', subjects=subjects)

@admin_bp.route('/subject/add', methods=['GET', 'POST'])
def subject_add():
    if request.method == 'POST':
        subject_id = None
        try:
            name = request.form.get('name', '').strip()
            grades = request.form.get('grades', '').strip()
            is_protected = 'is_protected' in request.form
            question_count = int(request.form.get('question_count', 20))
            time_limit = int(request.form.get('time_limit', 30)) # Added time_limit
            show_results = 'show_results' in request.form
            is_visible = 'is_visible' in request.form
            excellent_min = int(request.form.get('excellent_min', 85))
            good_min = int(request.form.get('good_min', 70))
            satisfactory_min = int(request.form.get('satisfactory_min', 65))
            fail_max = int(request.form.get('fail_max', satisfactory_min - 1))

            if not name or not grades:
                flash(_('Nom va sinflarni kiriting'), 'warning')
                return redirect(url_for('admin.subject_add'))

            validation_error = validate_grade_settings(excellent_min, good_min, satisfactory_min, fail_max)
            if validation_error:
                flash(validation_error, 'warning')
                return redirect(url_for('admin.subject_add'))

            subject = Subject(
                name=name,
                grades=grades,
                name_ru=auto_translate(name, 'ru'),
                name_en=auto_translate(name, 'en'),
                is_protected=is_protected,
                question_count=question_count,
                time_limit=time_limit, # Added time_limit
                show_results=show_results,
                is_visible=is_visible
            )
            db.session.add(subject)
            db.session.flush()
            subject_id = subject.id
            set_subject_grade_settings(subject_id, excellent_min, good_min, satisfactory_min, fail_max)
            db.session.commit()
            flash(_('Fan muvaffaqiyatli qo\'shildi va tarjima qilindi'), 'success')
            return redirect(url_for('admin.subjects'))
        except Exception as e:
            db.session.rollback()
            if subject_id:
                remove_subject_grade_settings(subject_id)
            flash(_('Xatolik yuz berdi: {}').format(str(e)), 'danger')
            return redirect(url_for('admin.subject_add'))

    return render_template(
        'admin_subject_form.html',
        subject=None,
        grading_settings=get_subject_grade_settings(None),
    )

@admin_bp.route('/subject/edit/<int:id>', methods=['GET', 'POST'])
def subject_edit(id):
    subject = Subject.query.get_or_404(id)
    grading_settings = get_subject_grade_settings(subject.id)

    if request.method == 'POST':
        try:
            excellent_min = int(request.form.get('excellent_min', 85))
            good_min = int(request.form.get('good_min', 70))
            satisfactory_min = int(request.form.get('satisfactory_min', 65))
            fail_max = int(request.form.get('fail_max', satisfactory_min - 1))

            validation_error = validate_grade_settings(excellent_min, good_min, satisfactory_min, fail_max)
            if validation_error:
                flash(validation_error, 'warning')
                return redirect(url_for('admin.subject_edit', id=id))

            subject.name = request.form['name']
            subject.name_ru = auto_translate(subject.name, 'ru')
            subject.name_en = auto_translate(subject.name, 'en')

            subject.grades = request.form['grades']
            subject.is_protected = 'is_protected' in request.form
            subject.question_count = int(request.form.get('question_count', 20))
            subject.time_limit = int(request.form.get('time_limit', 30))
            subject.show_results = 'show_results' in request.form
            subject.is_visible = 'is_visible' in request.form

            set_subject_grade_settings(subject.id, excellent_min, good_min, satisfactory_min, fail_max)
            db.session.commit()
            flash(_('Fan muvaffaqiyatli o\'zgartirildi'), 'success')
            return redirect(url_for('admin.subjects'))
        except Exception as e:
            db.session.rollback()
            set_subject_grade_settings(
                subject.id,
                grading_settings['excellent_min'],
                grading_settings['good_min'],
                grading_settings['satisfactory_min'],
                grading_settings['fail_max'],
            )
            flash(_('Xatolik yuz berdi: {}').format(str(e)), 'danger')
            return redirect(url_for('admin.subject_edit', id=id))

    return render_template('admin_subject_form.html', subject=subject, grading_settings=grading_settings)

@admin_bp.route('/subject/delete/<int:id>')
@admin_required
def subject_delete(id):
    subject = Subject.query.get_or_404(id)
    if subject.questions or subject.results:
        flash(_('Bu fanga tegishli savollar yoki natijalar mavjud. Oldin ularni o\'chiring.'), 'danger')
        return redirect(url_for('admin.subjects'))

    db.session.delete(subject)
    db.session.commit()
    try:
        remove_subject_grade_settings(id)
    except Exception as cleanup_error:
        print(f"Subject grading cleanup warning: {cleanup_error}")
    flash(_('Fan o\'chirildi'), 'success')
    return redirect(url_for('admin.subjects'))

# --- Nazorat Ishlari (Control Works) ---

@admin_bp.route('/control_works')
def control_works():
    cws = ControlWork.query.order_by(ControlWork.created_at.desc()).all()
    return render_template('admin_control_works.html', control_works=cws)

@admin_bp.route('/control_work/add', methods=['GET', 'POST'])
def control_work_add():
    if request.method == 'POST':
        try:
            title = request.form.get('title', '').strip()
            subject_id = request.form.get('subject_id', type=int)
            grade = request.form.get('grade', type=int)
            quarter = request.form.get('quarter', type=int)
            time_limit = request.form.get('time_limit', type=int, default=40)
            is_active = 'is_active' in request.form
            question_ids = request.form.getlist('question_ids')

            if not all([title, subject_id, grade, quarter]):
                flash(_('Barcha majburiy maydonlarni to\'ldiring'), 'warning')
                return redirect(url_for('admin.control_work_add'))

            new_cw = ControlWork(
                title=title,
                subject_id=subject_id,
                grade=grade,
                quarter=quarter,
                time_limit=time_limit,
                is_active=is_active
            )
            
            # Attach selected questions
            if question_ids:
                questions = Question.query.filter(Question.id.in_(question_ids)).all()
                new_cw.questions.extend(questions)

            db.session.add(new_cw)
            db.session.commit()
            flash(_('Nazorat ishi muvaffaqiyatli qo\'shildi'), 'success')
            return redirect(url_for('admin.control_works'))
            
        except Exception as e:
            db.session.rollback()
            flash(_('Xatolik yuz berdi: {}').format(str(e)), 'danger')
            return redirect(url_for('admin.control_work_add'))

    subjects = Subject.query.all()
    return render_template('admin_control_work_form.html', subjects=subjects, control_work=None)

@admin_bp.route('/control_work/edit/<int:id>', methods=['GET', 'POST'])
def control_work_edit(id):
    cw = ControlWork.query.get_or_404(id)

    if request.method == 'POST':
        try:
            cw.title = request.form.get('title', '').strip()
            cw.subject_id = request.form.get('subject_id', type=int)
            cw.grade = request.form.get('grade', type=int)
            cw.quarter = request.form.get('quarter', type=int)
            cw.time_limit = request.form.get('time_limit', type=int, default=40)
            cw.is_active = 'is_active' in request.form
            
            question_ids = request.form.getlist('question_ids')

            # Update assigned questions
            cw.questions = []
            if question_ids:
                questions = Question.query.filter(Question.id.in_(question_ids)).all()
                cw.questions.extend(questions)

            db.session.commit()
            flash(_('Nazorat ishi muvaffaqiyatli o\'zgartirildi'), 'success')
            return redirect(url_for('admin.control_works'))
            
        except Exception as e:
            db.session.rollback()
            flash(_('Xatolik yuz berdi: {}').format(str(e)), 'danger')
            return redirect(url_for('admin.control_work_edit', id=id))

    subjects = Subject.query.all()
    return render_template('admin_control_work_form.html', subjects=subjects, control_work=cw)

@admin_bp.route('/control_work/delete/<int:id>')
@admin_required
def control_work_delete(id):
    cw = ControlWork.query.get_or_404(id)
    # Removing relations with results (set to NULL via db behavior, or cascade depending on schema)
    # Actually, SQLAlchemy might not set to null automatically unless specified. Let's do it:
    for result in cw.results:
        result.control_work_id = None
        
    db.session.delete(cw)
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return {'success': True}
        
    flash(_('Nazorat ishi o\'chirildi'), 'success')
    return redirect(url_for('admin.control_works'))

@admin_bp.route('/api/questions')
def api_get_questions():
    subject_id = request.args.get('subject_id', type=int)
    grade = request.args.get('grade', type=int)
    quarter = request.args.get('quarter', type=int)
    
    if not all([subject_id, grade, quarter]):
        return jsonify({'questions': []})
        
    questions = Question.query.filter_by(
        subject_id=subject_id,
        grade=grade,
        quarter=quarter
    ).all()
    
    data = []
    for q in questions:
        data.append({
            'id': q.id,
            'text': q.question_text,
            'image_url': get_question_image_url(q.id),
            'a': q.option_a,
            'b': q.option_b,
            'c': q.option_c,
            'd': q.option_d,
            'correct': q.correct_answer
        })
        
    return {'questions': data}

# --- Teacher Management ---

@admin_bp.route('/teachers')
@admin_required
def teachers():
    teachers_list = Admin.query.filter_by(role='teacher').all()
    return render_template('admin_teachers.html', teachers=teachers_list)

@admin_bp.route('/teachers/add', methods=['GET', 'POST'])
@admin_required
def teacher_add():
    if request.method == 'POST':
        username = request.form.get('username')
        full_name = request.form.get('full_name')
        phone = request.form.get('phone_number')
        email = request.form.get('email')
        
        if Admin.query.filter_by(username=username).first():
            flash(_('Bu username band'), 'danger')
            return redirect(url_for('admin.teacher_add'))
            
        # Generate random 8-char password (alphabet + digits)
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for i in range(8))
        
        new_teacher = Admin(
            username=username,
            password_hash=generate_password_hash(password),
            full_name=full_name,
            role='teacher',
            phone_number=phone,
            email=email
        )
        db.session.add(new_teacher)
        db.session.commit()
        
        flash(_('O\'qituvchi muvaffaqiyatli qo\'shildi. Parol: {}').format(password), 'success')
        return redirect(url_for('admin.teachers'))
        
    return render_template('admin_teacher_add.html')

@admin_bp.route('/teachers/delete/<int:id>')
@admin_required
def teacher_delete(id):
    teacher = Admin.query.get_or_404(id)
    if teacher.role == 'admin':
        flash(_('Adminni o\'chirib bo\'lmaydi'), 'danger')
    else:
        db.session.delete(teacher)
        db.session.commit()
        flash(_('O\'qituvchi o\'chirildi'), 'success')
    return redirect(url_for('admin.teachers'))

@admin_bp.route('/teachers/reset-password/<int:id>')
@admin_required
def teacher_reset_password(id):
    teacher = Admin.query.get_or_404(id)
    if teacher.role == 'admin':
        flash(_('Admin parolini bu yerdan o\'zgartirib bo\'lmaydi'), 'danger')
        return redirect(url_for('admin.teachers'))
        
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(8))
    
    teacher.password_hash = generate_password_hash(password)
    db.session.commit()
    
    flash(_('{} uchun yangi parol: {}').format(teacher.full_name, password), 'success')
    return redirect(url_for('admin.teachers'))
