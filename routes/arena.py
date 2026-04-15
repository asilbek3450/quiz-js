from flask import (Blueprint, render_template, request, redirect,
                   url_for, session, jsonify, flash, abort, current_app)
from functools import wraps
from sqlalchemy import func
from models import db, ArenaUser, ArenaProblem, ArenaSubmission
from models import tashkent_now
import json, re
from judge import judge as judge_code, run_code, LANGUAGES

arena_bp = Blueprint('arena', __name__, url_prefix='/arena')

# ─── Helpers ──────────────────────────────────────────────────────────────────

def _current_user():
    uid = session.get('arena_user_id')
    if not uid:
        return None
    return ArenaUser.query.get(uid)


def arena_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('arena_user_id'):
            flash('Davom etish uchun tizimga kiring.', 'warning')
            return redirect(url_for('arena.login', next=request.full_path))
        return f(*args, **kwargs)
    return decorated


def super_admin_required(f):
    """Boshqaruv faqat super-admin 'asilbek' uchun."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_id') or session.get('admin_user') != 'asilbek':
            abort(403)
        return f(*args, **kwargs)
    return decorated


@arena_bp.context_processor
def _inject():
    u = _current_user()
    if u:
        u.last_seen = tashkent_now()
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
    return dict(arena_user=u)


def _validate_username(username):
    return bool(re.match(r'^[a-zA-Z0-9_]{3,30}$', username))


def _accepted_set(user_id):
    """Set of problem_ids that user has solved (AC)."""
    rows = (db.session.query(ArenaSubmission.problem_id)
            .filter_by(user_id=user_id, status='AC')
            .distinct().all())
    return {r[0] for r in rows}


def _attempted_set(user_id):
    """Set of problem_ids that user has attempted but not solved."""
    rows = (db.session.query(ArenaSubmission.problem_id)
            .filter_by(user_id=user_id)
            .filter(ArenaSubmission.status != 'AC')
            .distinct().all())
    return {r[0] for r in rows}


# ─── Auth ─────────────────────────────────────────────────────────────────────

@arena_bp.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('arena_user_id'):
        return redirect(url_for('arena.index'))

    error = None
    if request.method == 'POST':
        username  = request.form.get('username', '').strip()
        full_name = request.form.get('full_name', '').strip()
        age_raw   = request.form.get('age', '').strip()
        password  = request.form.get('password', '')
        confirm   = request.form.get('confirm_password', '')

        if not _validate_username(username):
            error = 'Username 3-30 ta harf/raqam/pastki chiziq (_) bo\'lishi kerak.'
        elif not full_name or len(full_name) < 3:
            error = 'Ism-familiya kamida 3 ta belgi bo\'lishi kerak.'
        elif age_raw and (not age_raw.isdigit() or not (5 <= int(age_raw) <= 100)):
            error = 'Yosh 5 dan 100 gacha bo\'lishi kerak.'
        elif len(password) < 6:
            error = 'Parol kamida 6 ta belgidan iborat bo\'lishi kerak.'
        elif password != confirm:
            error = 'Parollar mos kelmadi.'
        elif ArenaUser.query.filter(
                func.lower(ArenaUser.username) == username.lower()).first():
            error = f'"{username}" username allaqachon band.'
        else:
            user = ArenaUser(
                username=username,
                full_name=full_name,
                age=int(age_raw) if age_raw else None,
            )
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            session['arena_user_id'] = user.id
            session.permanent = True
            flash(f'Xush kelibsiz, {user.username}!', 'success')
            return redirect(url_for('arena.index'))

    return render_template('arena/register.html', error=error)


@arena_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('arena_user_id'):
        return redirect(url_for('arena.index'))

    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = ArenaUser.query.filter(
            func.lower(ArenaUser.username) == username.lower()).first()
        if not user or not user.check_password(password):
            error = 'Username yoki parol noto\'g\'ri.'
        else:
            session['arena_user_id'] = user.id
            session.permanent = True
            nxt = request.args.get('next')
            if nxt and nxt.startswith('/arena'):
                return redirect(nxt)
            return redirect(url_for('arena.index'))

    return render_template('arena/login.html', error=error)


@arena_bp.route('/logout')
def logout():
    session.pop('arena_user_id', None)
    return redirect(url_for('arena.login'))


# ─── Main index ───────────────────────────────────────────────────────────────

@arena_bp.route('/')
def index():
    total_users    = ArenaUser.query.count()
    total_problems = ArenaProblem.query.filter_by(is_active=True).count()
    total_subs     = ArenaSubmission.query.count()
    total_ac       = ArenaSubmission.query.filter_by(status='AC').count()

    # Top 5 users by problems_solved → rating
    top_users = (ArenaUser.query
                 .order_by(ArenaUser.problems_solved.desc(),
                            ArenaUser.rating.desc())
                 .limit(5).all())

    # Latest 10 AC submissions (public feed)
    recent_ac = (ArenaSubmission.query
                 .filter_by(status='AC')
                 .order_by(ArenaSubmission.submitted_at.desc())
                 .limit(10).all())

    return render_template('arena/index.html',
                           total_users=total_users,
                           total_problems=total_problems,
                           total_subs=total_subs,
                           total_ac=total_ac,
                           top_users=top_users,
                           recent_ac=recent_ac)


# ─── Problems ─────────────────────────────────────────────────────────────────

@arena_bp.route('/problems')
def problems():
    diff     = request.args.get('diff', '')
    cat      = request.args.get('cat', '')
    status_f = request.args.get('status', '')   # solved / unsolved / ''
    search   = request.args.get('q', '').strip()

    q = ArenaProblem.query.filter_by(is_active=True)
    if diff in ('easy', 'medium', 'hard'):
        q = q.filter_by(difficulty=diff)
    if cat:
        q = q.filter_by(category=cat)
    if search:
        q = q.filter(ArenaProblem.title.ilike(f'%{search}%') |
                     ArenaProblem.code.ilike(f'%{search}%'))
    q = q.order_by(ArenaProblem.code)
    all_problems = q.all()

    # Per-user solved set
    uid = session.get('arena_user_id')
    solved_ids   = _accepted_set(uid) if uid else set()
    attempted_ids = (_attempted_set(uid) - solved_ids) if uid else set()

    if status_f == 'solved':
        all_problems = [p for p in all_problems if p.id in solved_ids]
    elif status_f == 'unsolved':
        all_problems = [p for p in all_problems if p.id not in solved_ids]

    # All categories for filter dropdown
    cats = (db.session.query(ArenaProblem.category)
            .filter_by(is_active=True)
            .distinct()
            .order_by(ArenaProblem.category).all())
    categories = [c[0] for c in cats if c[0]]

    return render_template('arena/problems.html',
                           problems=all_problems,
                           solved_ids=solved_ids,
                           attempted_ids=attempted_ids,
                           categories=categories,
                           current_diff=diff,
                           current_cat=cat,
                           current_status=status_f,
                           search=search)


@arena_bp.route('/problems/<int:pid>')
def problem_detail(pid):
    problem = ArenaProblem.query.filter_by(id=pid, is_active=True).first_or_404()

    try:
        examples = json.loads(problem.examples or '[]')
    except (ValueError, TypeError):
        examples = []

    uid = session.get('arena_user_id')
    my_subs = []
    already_solved = False
    if uid:
        my_subs = (ArenaSubmission.query
                   .filter_by(user_id=uid, problem_id=pid)
                   .order_by(ArenaSubmission.submitted_at.desc())
                   .limit(10).all())
        already_solved = any(s.status == 'AC' for s in my_subs)

    # Adjacent problems (prev/next by code)
    prev_p = (ArenaProblem.query.filter_by(is_active=True)
              .filter(ArenaProblem.code < problem.code)
              .order_by(ArenaProblem.code.desc()).first())
    next_p = (ArenaProblem.query.filter_by(is_active=True)
              .filter(ArenaProblem.code > problem.code)
              .order_by(ArenaProblem.code.asc()).first())

    return render_template('arena/problem_detail.html',
                           problem=problem,
                           examples=examples,
                           my_subs=my_subs,
                           already_solved=already_solved,
                           prev_p=prev_p,
                           next_p=next_p)


@arena_bp.route('/problems/<int:pid>/run', methods=['POST'])
@arena_required
def run(pid):
    """AJAX: run code against a single test case (no DB record)."""
    problem = ArenaProblem.query.filter_by(id=pid, is_active=True).first_or_404()
    data     = request.get_json(silent=True) or {}
    code     = data.get('code', '').strip()
    language = data.get('language', 'python')
    stdin    = data.get('stdin', '')

    if not code:
        return jsonify({'verdict': 'CE', 'output': '', 'error': 'Kod bo\'sh.', 'time': 0})

    if language not in LANGUAGES:
        return jsonify({'verdict': 'CE', 'output': '',
                        'error': f'Til qo\'llab-quvvatlanmaydi: {language}', 'time': 0})

    result = run_code(code, language, stdin, time_limit=float(problem.time_limit or 5))
    return jsonify(result)


@arena_bp.route('/problems/<int:pid>/submit', methods=['POST'])
@arena_required
def submit(pid):
    """Run code against ALL test cases, record verdict, update stats."""
    problem = ArenaProblem.query.filter_by(id=pid, is_active=True).first_or_404()
    uid      = session['arena_user_id']

    data     = request.get_json(silent=True) or {}
    code     = data.get('code', '').strip()
    language = data.get('language', 'python')

    if not code:
        return jsonify({'verdict': 'CE', 'error': 'Kod bo\'sh.'})

    if language not in LANGUAGES:
        return jsonify({'verdict': 'CE', 'error': f'Til qo\'llab-quvvatlanmaydi: {language}'})

    # Load test cases from examples; fall back to correct_answer as single case
    try:
        examples = json.loads(problem.examples or '[]')
    except (ValueError, TypeError):
        examples = []

    time_limit = float(problem.time_limit or 5)

    # Build test list: [{input, output}, ...]
    tests = [{'input': ex.get('input', ''), 'output': ex.get('output', '')}
             for ex in examples if ex.get('output', '').strip()]

    # If no example outputs defined, use correct_answer with empty stdin
    if not tests and (problem.correct_answer or '').strip():
        tests = [{'input': '', 'output': problem.correct_answer.strip()}]

    if not tests:
        return jsonify({'verdict': 'CE', 'error': 'Masalada test holatlari topilmadi.'})

    # Run against each test; stop at first failure
    final_verdict = 'AC'
    final_output  = ''
    final_error   = ''
    final_time    = 0.0
    failed_test   = None

    for i, t in enumerate(tests, 1):
        result = judge_code(code, language, t['input'], t['output'], time_limit)
        final_time = max(final_time, result.get('time', 0))
        if result['verdict'] != 'AC':
            final_verdict = result['verdict']
            final_output  = result.get('output', '')
            final_error   = result.get('error', '')
            failed_test   = i
            break
        final_output = result.get('output', '')

    # SE (server xatosi) — submission saqlanmaydi, foydalanuvchiga qayta urinish tavsiya
    if final_verdict == 'SE':
        return jsonify({
            'verdict': 'SE',
            'output': '',
            'error': '',
            'time': round(final_time, 3),
        })

    # Record submission (faqat haqiqiy verdiktlar uchun)
    sub = ArenaSubmission(
        user_id=uid,
        problem_id=pid,
        code=code,
        language=language,
        answer=final_output[:2000],
        status=final_verdict,
        time_used=round(final_time, 3),
        error_msg=final_error[:1000],
    )
    db.session.add(sub)

    # Update problem counters
    problem.submission_count += 1
    if final_verdict == 'AC':
        problem.accepted_count += 1

    # Update user stats (only once per unique problem)
    user = ArenaUser.query.get(uid)
    already_ac = (ArenaSubmission.query
                  .filter_by(user_id=uid, problem_id=pid, status='AC')
                  .first())
    if final_verdict == 'AC' and not already_ac:
        user.problems_solved += 1
        diff_pts = {'easy': 10, 'medium': 25, 'hard': 50}
        user.rating += diff_pts.get(problem.difficulty, 10)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.warning(f'Arena submit error: {e}')
        return jsonify({'verdict': 'CE', 'error': 'Server xatosi, qayta urinib ko\'ring.'})

    resp = {
        'verdict':    final_verdict,
        'output':     final_output,
        'error':      final_error,
        'time':       round(final_time, 3),
        'sub_id':     sub.id,
    }
    if failed_test:
        resp['failed_test'] = failed_test
    return jsonify(resp)


# ─── Submissions ──────────────────────────────────────────────────────────────

@arena_bp.route('/submissions')
@arena_required
def submissions():
    uid = session['arena_user_id']
    status_f = request.args.get('status', '')
    page     = request.args.get('page', 1, type=int)

    q = ArenaSubmission.query.filter_by(user_id=uid)
    if status_f in ('AC', 'WA', 'PE'):
        q = q.filter_by(status=status_f)
    q = q.order_by(ArenaSubmission.submitted_at.desc())
    paginated = q.paginate(page=page, per_page=20, error_out=False)

    return render_template('arena/submissions.html',
                           subs=paginated,
                           current_status=status_f)


@arena_bp.route('/submissions/<int:sid>/code')
@arena_required
def submission_code(sid):
    """AJAX: Get submission code and metadata for viewing in a modal."""
    uid = session['arena_user_id']
    sub = ArenaSubmission.query.get_or_404(sid)
    
    # Ensure privacy: user can only see their own submissions
    if sub.user_id != uid:
        abort(403)
        
    return jsonify({
        'id': sub.id,
        'code': sub.code,
        'language': sub.language,
        'status': sub.status,
        'time_used': sub.time_used,
        'error_msg': sub.error_msg,
        'problem_code': sub.problem.code,
        'problem_title': sub.problem.title,
        'submitted_at': sub.submitted_at.strftime('%Y-%m-%d %H:%M:%S')
    })


# ─── Users / Leaderboard ──────────────────────────────────────────────────────

@arena_bp.route('/users')
def users():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('q', '').strip()

    q = ArenaUser.query
    if search:
        q = q.filter(ArenaUser.username.ilike(f'%{search}%') |
                     ArenaUser.full_name.ilike(f'%{search}%'))
    q = q.order_by(ArenaUser.problems_solved.desc(),
                   ArenaUser.rating.desc(),
                   ArenaUser.created_at.asc())
    paginated = q.paginate(page=page, per_page=25, error_out=False)

    return render_template('arena/users.html',
                           users=paginated,
                           search=search)


# ─── Profile ──────────────────────────────────────────────────────────────────

@arena_bp.route('/profile/<username>')
def profile(username):
    user = ArenaUser.query.filter(
        func.lower(ArenaUser.username) == username.lower()).first_or_404()

    solved_ids = _accepted_set(user.id)

    # All problems for the "solved map"
    all_problems = (ArenaProblem.query.filter_by(is_active=True)
                    .order_by(ArenaProblem.code).all())

    # Stats per difficulty
    def _solved_by_diff(diff):
        return sum(1 for p in all_problems
                   if p.difficulty == diff and p.id in solved_ids)

    stats = {
        'easy':   _solved_by_diff('easy'),
        'medium': _solved_by_diff('medium'),
        'hard':   _solved_by_diff('hard'),
    }

    # Global rank
    better = ArenaUser.query.filter(
        (ArenaUser.problems_solved > user.problems_solved) |
        ((ArenaUser.problems_solved == user.problems_solved) &
         (ArenaUser.rating > user.rating))
    ).count()
    rank = better + 1

    # Recent 5 AC submissions
    recent_ac = (ArenaSubmission.query
                 .filter_by(user_id=user.id, status='AC')
                 .order_by(ArenaSubmission.submitted_at.desc())
                 .limit(5).all())

    return render_template('arena/profile.html',
                           u=user,
                           all_problems=all_problems,
                           solved_ids=solved_ids,
                           stats=stats,
                           rank=rank,
                           recent_ac=recent_ac)


# ─── Settings ─────────────────────────────────────────────────────────────────

@arena_bp.route('/settings', methods=['GET', 'POST'])
@arena_required
def settings():
    user = _current_user()
    error = None
    success = None

    if request.method == 'POST':
        action = request.form.get('action', 'profile')

        if action == 'profile':
            full_name = request.form.get('full_name', '').strip()
            age_raw   = request.form.get('age', '').strip()
            bio       = request.form.get('bio', '').strip()[:500]

            if not full_name or len(full_name) < 3:
                error = 'Ism-familiya kamida 3 ta belgi bo\'lishi kerak.'
            elif age_raw and (not age_raw.isdigit() or not (5 <= int(age_raw) <= 100)):
                error = 'Yosh 5 dan 100 gacha bo\'lishi kerak.'
            else:
                user.full_name = full_name
                user.age = int(age_raw) if age_raw else None
                user.bio = bio
                db.session.commit()
                success = 'Profil yangilandi!'

        elif action == 'password':
            current_pw = request.form.get('current_password', '')
            new_pw     = request.form.get('new_password', '')
            confirm_pw = request.form.get('confirm_password', '')

            if not user.check_password(current_pw):
                error = 'Joriy parol noto\'g\'ri.'
            elif len(new_pw) < 6:
                error = 'Yangi parol kamida 6 ta belgidan iborat bo\'lishi kerak.'
            elif new_pw != confirm_pw:
                error = 'Yangi parollar mos kelmadi.'
            else:
                user.set_password(new_pw)
                db.session.commit()
                success = 'Parol muvaffaqiyatli o\'zgartirildi!'

    return render_template('arena/settings.html',
                           u=user, error=error, success=success)


# ─── Admin: Arena Problem Management ─────────────────────────────────────────
# These routes are only accessible when logged in as admin

@arena_bp.route('/admin/problems')
@super_admin_required
def admin_problems():
    problems = (ArenaProblem.query
                .order_by(ArenaProblem.code).all())
    return render_template('admin_arena_problems.html', problems=problems)


@arena_bp.route('/admin/problems/new', methods=['GET', 'POST'])
@super_admin_required
def admin_problem_new():
    return _problem_form(problem=None)


@arena_bp.route('/admin/problems/<int:pid>/edit', methods=['GET', 'POST'])
@super_admin_required
def admin_problem_edit(pid):
    problem = ArenaProblem.query.get_or_404(pid)
    return _problem_form(problem=problem)


@arena_bp.route('/admin/problems/<int:pid>/delete', methods=['POST'])
@super_admin_required
def admin_problem_delete(pid):
    problem = ArenaProblem.query.get_or_404(pid)
    # Delete submissions first
    ArenaSubmission.query.filter_by(problem_id=pid).delete()
    db.session.delete(problem)
    db.session.commit()
    flash('Masala o\'chirildi.', 'success')
    return redirect(url_for('arena.admin_problems'))


def _problem_form(problem):
    error = None
    if request.method == 'POST':
        code        = request.form.get('code', '').strip().upper()
        title       = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        input_fmt   = request.form.get('input_format', '').strip()
        output_fmt  = request.form.get('output_format', '').strip()
        constraints = request.form.get('constraints', '').strip()
        difficulty  = request.form.get('difficulty', 'easy')
        category    = request.form.get('category', 'general').strip()
        correct_ans = request.form.get('correct_answer', '').strip()
        time_lim    = request.form.get('time_limit', '1.0')
        mem_lim     = request.form.get('memory_limit', '256')
        is_active   = request.form.get('is_active') == '1'

        # Examples: up to 5 pairs
        examples = []
        for i in range(1, 6):
            inp = request.form.get(f'ex_input_{i}', '').strip()
            out = request.form.get(f'ex_output_{i}', '').strip()
            exp = request.form.get(f'ex_explanation_{i}', '').strip()
            if inp or out:
                examples.append({'input': inp, 'output': out,
                                  'explanation': exp})

        if not code:
            error = 'Kod majburiy.'
        elif not title:
            error = 'Sarlavha majburiy.'
        elif not description:
            error = 'Tavsif majburiy.'
        elif difficulty not in ('easy', 'medium', 'hard'):
            error = 'Murakkablik noto\'g\'ri.'
        else:
            # Uniqueness check
            existing = ArenaProblem.query.filter_by(code=code).first()
            if existing and (problem is None or existing.id != problem.id):
                error = f'"{code}" kodi allaqachon mavjud.'

        if not error:
            if problem is None:
                problem = ArenaProblem()
                db.session.add(problem)
            problem.code        = code
            problem.title       = title
            problem.description = description
            problem.input_format  = input_fmt
            problem.output_format = output_fmt
            problem.constraints   = constraints
            problem.examples      = json.dumps(examples, ensure_ascii=False)
            problem.difficulty    = difficulty
            problem.category      = category
            problem.correct_answer = correct_ans
            problem.time_limit    = float(time_lim) if time_lim else 1.0
            problem.memory_limit  = int(mem_lim) if mem_lim else 256
            problem.is_active     = is_active
            db.session.commit()
            flash('Masala saqlandi.', 'success')
            return redirect(url_for('arena.admin_problems'))

    # Parse existing examples for form
    try:
        ex_list = json.loads(problem.examples) if problem and problem.examples else []
    except (ValueError, TypeError):
        ex_list = []
    # Pad to 5 slots
    while len(ex_list) < 5:
        ex_list.append({'input': '', 'output': '', 'explanation': ''})

    return render_template('admin_arena_problem_form.html',
                           problem=problem,
                           ex_list=ex_list,
                           error=error)
