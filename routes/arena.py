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


ARENA_ADMIN_USERNAME = 'user'


def _is_arena_admin():
    u = _current_user()
    return u is not None and u.username.lower() == ARENA_ADMIN_USERNAME


def arena_admin_required(f):
    """Faqat arena admin (username='user') uchun."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not _is_arena_admin():
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
    return dict(arena_user=u, is_arena_admin=_is_arena_admin())


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


def _diff_stars(difficulty: str) -> int:
    """Murakkablikka qarab masalaning yulduz qiymati: oson=10, o'rta=25, qiyin=50."""
    return {'easy': 10, 'medium': 25, 'hard': 50}.get(difficulty, 10)


def _calc_stars(passed: int, total: int, verdict: str, difficulty: str = 'easy') -> int:
    """Faqat barcha testlar to'g'ri o'tsa (AC) yulduz beradi, aks holda 0."""
    if total == 0:
        return _diff_stars(difficulty) if verdict == 'AC' else 0
    if passed >= total and verdict == 'AC':
        return _diff_stars(difficulty)
    return 0


@arena_bp.route('/problems/<int:pid>/submit', methods=['POST'])
@arena_required
def submit(pid):
    """Run code against ALL test cases (examples + hidden), record verdict, update stats."""
    problem = ArenaProblem.query.filter_by(id=pid, is_active=True).first_or_404()
    uid      = session['arena_user_id']

    data     = request.get_json(silent=True) or {}
    code     = data.get('code', '').strip()
    language = data.get('language', 'python')

    if not code:
        return jsonify({'verdict': 'CE', 'error': 'Kod bo\'sh.'})

    if language not in LANGUAGES:
        return jsonify({'verdict': 'CE', 'error': f'Til qo\'llab-quvvatlanmaydi: {language}'})

    time_limit = float(problem.time_limit or 5)

    # ── Load visible examples ──────────────────────────────────────────────────
    try:
        examples = json.loads(problem.examples or '[]')
    except (ValueError, TypeError):
        examples = []

    example_tests = [{'input': ex.get('input', ''), 'output': ex.get('output', '')}
                     for ex in examples if ex.get('output', '').strip()]

    # ── Load hidden tests ──────────────────────────────────────────────────────
    try:
        hidden_raw = json.loads(problem.hidden_tests or '[]')
    except (ValueError, TypeError):
        hidden_raw = []

    hidden_tests = [{'input': t.get('input', ''), 'output': t.get('output', '')}
                    for t in hidden_raw if t.get('output', '').strip()]

    # If no hidden tests, fall back to correct_answer as single hidden test
    if not hidden_tests and (problem.correct_answer or '').strip():
        hidden_tests = [{'input': '', 'output': problem.correct_answer.strip()}]

    # ── Combined test list: examples first, then hidden ────────────────────────
    all_tests = example_tests + hidden_tests

    if not all_tests:
        return jsonify({'verdict': 'CE', 'error': 'Masalada test holatlari topilmadi.'})

    # ── Run all tests, counting how many pass ──────────────────────────────────
    final_verdict = 'AC'
    final_output  = ''
    final_error   = ''
    final_time    = 0.0
    failed_test   = None
    passed_count  = 0
    total_count   = len(all_tests)

    for i, t in enumerate(all_tests, 1):
        result = judge_code(code, language, t['input'], t['output'], time_limit)
        final_time = max(final_time, result.get('time', 0))
        if result['verdict'] == 'AC':
            passed_count += 1
        else:
            if final_verdict == 'AC':
                # Record first failure info
                final_verdict = result['verdict']
                final_output  = result.get('output', '')
                final_error   = result.get('error', '')
                # Show only example test indices to user; hide hidden test numbers
                failed_test   = i if i <= len(example_tests) else None
            # TLE or CE will behave the same on all remaining tests — stop early
            if result['verdict'] in ('TLE', 'CE'):
                break

    stars = _calc_stars(passed_count, total_count, final_verdict, problem.difficulty)

    # ── Check before adding new submission ─────────────────────────────────────
    user = ArenaUser.query.get(uid)
    already_ac = (ArenaSubmission.query
                  .filter_by(user_id=uid, problem_id=pid, status='AC')
                  .first())

    # ── Record submission ──────────────────────────────────────────────────────
    sub = ArenaSubmission(
        user_id=uid,
        problem_id=pid,
        code=code,
        language=language,
        answer=final_output[:2000],
        status=final_verdict,
        time_used=round(final_time, 3),
        error_msg=final_error[:1000],
        tests_passed=passed_count,
        tests_total=total_count,
        stars=stars,
    )
    db.session.add(sub)

    # ── Update problem counters ────────────────────────────────────────────────
    problem.submission_count += 1
    if final_verdict == 'AC':
        problem.accepted_count += 1

    # ── Update user stats (only once per unique problem) ──────────────────────
    if final_verdict == 'AC' and not already_ac:
        user.problems_solved += 1
        pts = _diff_stars(problem.difficulty)
        user.rating += pts
        user.total_stars += pts

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.warning(f'Arena submit error: {e}')
        return jsonify({'verdict': 'CE', 'error': 'Server xatosi, qayta urinib ko\'ring.'})

    resp = {
        'verdict':      final_verdict,
        'output':       final_output,
        'error':        final_error,
        'time':         round(final_time, 3),
        'sub_id':       sub.id,
        'stars':        stars,
        'passed':       passed_count,
        'total':        total_count,
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
    
    # Admin har qanday submissionni ko'ra oladi
    if sub.user_id != uid and not _is_arena_admin():
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
        'username': sub.user.username,
        'submitted_at': sub.submitted_at.strftime('%Y-%m-%d %H:%M:%S')
    })


# ─── Users / Leaderboard ──────────────────────────────────────────────────────

@arena_bp.route('/users')
def users():
    page   = request.args.get('page', 1, type=int)
    search = request.args.get('q', '').strip()
    sort   = request.args.get('sort', 'stars')

    q = ArenaUser.query
    if search:
        q = q.filter(ArenaUser.username.ilike(f'%{search}%') |
                     ArenaUser.full_name.ilike(f'%{search}%'))

    # Sorting options
    if sort == 'solved':
        q = q.order_by(ArenaUser.problems_solved.desc(), ArenaUser.rating.desc())
    elif sort == 'rating':
        q = q.order_by(ArenaUser.rating.desc(), ArenaUser.problems_solved.desc())
    elif sort == 'new':
        q = q.order_by(ArenaUser.created_at.desc())
    else:  # 'stars' — default: most rating (stars) first
        q = q.order_by(ArenaUser.rating.desc(),
                       ArenaUser.problems_solved.desc(),
                       ArenaUser.created_at.asc())

    paginated = q.paginate(page=page, per_page=25, error_out=False)

    return render_template('arena/users.html',
                           users=paginated,
                           search=search,
                           sort=sort)


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

@arena_bp.route('/sadmin/problems')
@super_admin_required
def admin_problems():
    problems = (ArenaProblem.query
                .order_by(ArenaProblem.code).all())
    return render_template('admin_arena_problems.html', problems=problems)


@arena_bp.route('/sadmin/problems/new', methods=['GET', 'POST'])
@super_admin_required
def admin_problem_new():
    return _problem_form(problem=None)


@arena_bp.route('/sadmin/problems/<int:pid>/edit', methods=['GET', 'POST'])
@super_admin_required
def admin_problem_edit(pid):
    problem = ArenaProblem.query.get_or_404(pid)
    return _problem_form(problem=problem)


@arena_bp.route('/sadmin/problems/<int:pid>/delete', methods=['POST'])
@super_admin_required
def admin_problem_delete(pid):
    problem = ArenaProblem.query.get_or_404(pid)
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

        # Examples: up to 5 pairs (visible to users)
        examples = []
        for i in range(1, 6):
            inp = request.form.get(f'ex_input_{i}', '').strip()
            out = request.form.get(f'ex_output_{i}', '').strip()
            exp = request.form.get(f'ex_explanation_{i}', '').strip()
            if inp or out:
                examples.append({'input': inp, 'output': out,
                                  'explanation': exp})

        # Hidden tests: JSON textarea (not shown to users)
        hidden_tests_raw = request.form.get('hidden_tests_json', '').strip()
        hidden_tests = []
        if hidden_tests_raw:
            try:
                parsed = json.loads(hidden_tests_raw)
                if isinstance(parsed, list):
                    hidden_tests = [
                        {'input': str(t.get('input', '')), 'output': str(t.get('output', ''))}
                        for t in parsed
                        if isinstance(t, dict) and str(t.get('output', '')).strip()
                    ]
            except (ValueError, TypeError):
                error = 'Yashirin testlar JSON formati noto\'g\'ri.'

        if not error:
            if not code:
                error = 'Kod majburiy.'
            elif not title:
                error = 'Sarlavha majburiy.'
            elif not description:
                error = 'Tavsif majburiy.'
            elif difficulty not in ('easy', 'medium', 'hard'):
                error = 'Murakkablik noto\'g\'ri.'
            elif len(hidden_tests) < 10:
                error = f'Kamida 10 ta yashirin test talab qilinadi (hozir {len(hidden_tests)} ta). Sifatli tekshiruv uchun ko\'proq test qo\'shing.'
            else:
                existing = ArenaProblem.query.filter_by(code=code).first()
                if existing and (problem is None or existing.id != problem.id):
                    error = f'"{code}" kodi allaqachon mavjud.'

        if not error:
            if problem is None:
                problem = ArenaProblem()
                db.session.add(problem)
            problem.code          = code
            problem.title         = title
            problem.description   = description
            problem.input_format  = input_fmt
            problem.output_format = output_fmt
            problem.constraints   = constraints
            problem.examples      = json.dumps(examples, ensure_ascii=False)
            problem.hidden_tests  = json.dumps(hidden_tests, ensure_ascii=False, indent=2)
            problem.difficulty    = difficulty
            problem.category      = category
            problem.correct_answer = correct_ans
            problem.time_limit    = float(time_lim) if time_lim else 1.0
            problem.memory_limit  = int(mem_lim) if mem_lim else 256
            problem.is_active     = is_active
            db.session.commit()
            flash(f'Masala saqlandi. {len(hidden_tests)} ta yashirin test.', 'success')
            return redirect(url_for('arena.admin_problems'))

    # Parse existing examples and hidden_tests for form
    try:
        ex_list = json.loads(problem.examples) if problem and problem.examples else []
    except (ValueError, TypeError):
        ex_list = []
    while len(ex_list) < 5:
        ex_list.append({'input': '', 'output': '', 'explanation': ''})

    hidden_tests_pretty = (problem.hidden_tests or '[]') if problem else '[]'

    return render_template('admin_arena_problem_form.html',
                           problem=problem,
                           ex_list=ex_list,
                           hidden_tests_json=hidden_tests_pretty,
                           error=error)


# ─── Arena Admin Panel (username='user') ──────────────────────────────────────

@arena_bp.route('/admin')
@arena_admin_required
def arena_admin_dashboard():
    total_users    = ArenaUser.query.count()
    total_problems = ArenaProblem.query.count()
    active_problems = ArenaProblem.query.filter_by(is_active=True).count()
    total_subs     = ArenaSubmission.query.count()
    total_ac       = ArenaSubmission.query.filter_by(status='AC').count()
    recent_subs    = (ArenaSubmission.query
                      .order_by(ArenaSubmission.submitted_at.desc())
                      .limit(10).all())
    return render_template('arena/admin_dashboard.html',
                           total_users=total_users,
                           total_problems=total_problems,
                           active_problems=active_problems,
                           total_subs=total_subs,
                           total_ac=total_ac,
                           recent_subs=recent_subs)


@arena_bp.route('/admin/submissions')
@arena_admin_required
def arena_admin_submissions():
    status_f  = request.args.get('status', '')
    user_q    = request.args.get('user', '').strip()
    problem_q = request.args.get('problem', '').strip()
    page      = request.args.get('page', 1, type=int)

    q = ArenaSubmission.query
    if status_f in ('AC', 'WA', 'TLE', 'RE', 'CE', 'PE'):
        q = q.filter_by(status=status_f)
    if user_q:
        user_obj = ArenaUser.query.filter(
            func.lower(ArenaUser.username) == user_q.lower()).first()
        if user_obj:
            q = q.filter_by(user_id=user_obj.id)
        else:
            q = q.filter(False)
    if problem_q:
        prob_obj = ArenaProblem.query.filter(
            ArenaProblem.code.ilike(f'%{problem_q}%') |
            ArenaProblem.title.ilike(f'%{problem_q}%')).first()
        if prob_obj:
            q = q.filter_by(problem_id=prob_obj.id)
        else:
            q = q.filter(False)

    q = q.order_by(ArenaSubmission.submitted_at.desc())
    paginated = q.paginate(page=page, per_page=30, error_out=False)

    return render_template('arena/admin_submissions.html',
                           subs=paginated,
                           current_status=status_f,
                           user_q=user_q,
                           problem_q=problem_q)


@arena_bp.route('/admin/submissions/<int:sid>/delete', methods=['POST'])
@arena_admin_required
def arena_admin_submission_delete(sid):
    sub     = ArenaSubmission.query.get_or_404(sid)
    user    = ArenaUser.query.get(sub.user_id)
    problem = ArenaProblem.query.get(sub.problem_id)

    was_ac = sub.status == 'AC'

    if problem:
        if problem.submission_count > 0:
            problem.submission_count -= 1
        if was_ac and problem.accepted_count > 0:
            problem.accepted_count -= 1

    if was_ac and user:
        other_ac = (ArenaSubmission.query
                    .filter_by(user_id=sub.user_id, problem_id=sub.problem_id, status='AC')
                    .filter(ArenaSubmission.id != sid)
                    .first())
        if not other_ac:
            if user.problems_solved > 0:
                user.problems_solved -= 1
            pts = sub.stars or _diff_stars(problem.difficulty if problem else 'easy')
            user.rating      = max(0, user.rating - pts)
            user.total_stars = max(0, user.total_stars - pts)

    db.session.delete(sub)
    try:
        db.session.commit()
        flash('Urinish bekor qilindi va statistika yangilandi.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Xato: {e}', 'danger')

    return redirect(request.referrer or url_for('arena.arena_admin_submissions'))


@arena_bp.route('/admin/problems')
@arena_admin_required
def arena_admin_problems():
    diff   = request.args.get('diff', '')
    search = request.args.get('q', '').strip()
    q = ArenaProblem.query
    if diff in ('easy', 'medium', 'hard'):
        q = q.filter_by(difficulty=diff)
    if search:
        q = q.filter(ArenaProblem.title.ilike(f'%{search}%') |
                     ArenaProblem.code.ilike(f'%{search}%'))
    problems = q.order_by(ArenaProblem.code).all()
    return render_template('arena/admin_problems.html',
                           problems=problems,
                           current_diff=diff,
                           search=search)


@arena_bp.route('/admin/problems/new', methods=['GET', 'POST'])
@arena_admin_required
def arena_admin_problem_new():
    return _arena_problem_form(problem=None)


@arena_bp.route('/admin/problems/<int:pid>/edit', methods=['GET', 'POST'])
@arena_admin_required
def arena_admin_problem_edit(pid):
    problem = ArenaProblem.query.get_or_404(pid)
    return _arena_problem_form(problem=problem)


@arena_bp.route('/admin/problems/<int:pid>/toggle', methods=['POST'])
@arena_admin_required
def arena_admin_problem_toggle(pid):
    problem = ArenaProblem.query.get_or_404(pid)
    problem.is_active = not problem.is_active
    db.session.commit()
    state = 'faollashtirildi' if problem.is_active else 'o\'chirildi'
    flash(f'"{problem.code}" {state}.', 'success')
    return redirect(request.referrer or url_for('arena.arena_admin_problems'))


@arena_bp.route('/admin/problems/<int:pid>/delete', methods=['POST'])
@arena_admin_required
def arena_admin_problem_delete(pid):
    problem = ArenaProblem.query.get_or_404(pid)
    ArenaSubmission.query.filter_by(problem_id=pid).delete()
    db.session.delete(problem)
    db.session.commit()
    flash('Masala o\'chirildi.', 'success')
    return redirect(url_for('arena.arena_admin_problems'))


@arena_bp.route('/admin/users')
@arena_admin_required
def arena_admin_users():
    search = request.args.get('q', '').strip()
    page   = request.args.get('page', 1, type=int)
    q = ArenaUser.query
    if search:
        q = q.filter(ArenaUser.username.ilike(f'%{search}%') |
                     ArenaUser.full_name.ilike(f'%{search}%'))
    q = q.order_by(ArenaUser.rating.desc(), ArenaUser.problems_solved.desc())
    paginated = q.paginate(page=page, per_page=30, error_out=False)
    return render_template('arena/admin_users.html',
                           users=paginated,
                           search=search)


@arena_bp.route('/admin/users/<int:uid>/recalc', methods=['POST'])
@arena_admin_required
def arena_admin_user_recalc(uid):
    """Foydalanuvchi statistikasini qayta hisoblash."""
    user = ArenaUser.query.get_or_404(uid)

    solved_problem_ids = set(
        r[0] for r in
        db.session.query(ArenaSubmission.problem_id)
        .filter_by(user_id=uid, status='AC').distinct().all()
    )
    user.problems_solved = len(solved_problem_ids)

    total_pts = 0
    for pid_ in solved_problem_ids:
        prob = ArenaProblem.query.get(pid_)
        if prob:
            total_pts += _diff_stars(prob.difficulty)
    user.rating      = total_pts
    user.total_stars = total_pts

    db.session.commit()
    flash(f'{user.username} statistikasi yangilandi: {user.problems_solved} masala, {user.rating} ball.', 'success')
    return redirect(request.referrer or url_for('arena.arena_admin_users'))


@arena_bp.route('/admin/users/<int:uid>/edit', methods=['GET', 'POST'])
@arena_admin_required
def arena_admin_user_edit(uid):
    """Admin: foydalanuvchini tahrirlash (username, full_name, age, bio)."""
    user = ArenaUser.query.get_or_404(uid)
    me   = _current_user()
    error = None
    success = None

    if request.method == 'POST':
        username  = request.form.get('username', '').strip()
        full_name = request.form.get('full_name', '').strip()
        age_raw   = request.form.get('age', '').strip()
        bio       = request.form.get('bio', '').strip()[:500]

        if not _validate_username(username):
            error = 'Username 3-30 ta harf/raqam/pastki chiziq (_) bo\'lishi kerak.'
        elif not full_name or len(full_name) < 3:
            error = 'Ism-familiya kamida 3 ta belgi bo\'lishi kerak.'
        elif age_raw and (not age_raw.isdigit() or not (5 <= int(age_raw) <= 100)):
            error = 'Yosh 5 dan 100 gacha bo\'lishi kerak.'
        else:
            # Username uniqueness (case-insensitive) — must not collide with another user
            dup = ArenaUser.query.filter(
                func.lower(ArenaUser.username) == username.lower(),
                ArenaUser.id != user.id
            ).first()
            if dup:
                error = f'"{username}" username allaqachon band.'
            # Admin o'z username'ini o'zgartira olmaydi (admin login = "user")
            elif user.username.lower() == ARENA_ADMIN_USERNAME and username.lower() != ARENA_ADMIN_USERNAME:
                error = 'Admin akkauntining username\'ini o\'zgartirib bo\'lmaydi.'
            else:
                user.username  = username
                user.full_name = full_name
                user.age       = int(age_raw) if age_raw else None
                user.bio       = bio
                db.session.commit()
                success = 'Foydalanuvchi yangilandi.'

    return render_template('arena/admin_user_edit.html',
                           u=user, me=me, error=error, success=success)


@arena_bp.route('/admin/users/<int:uid>/reset_password', methods=['POST'])
@arena_admin_required
def arena_admin_user_reset_password(uid):
    """Admin: foydalanuvchi parolini tiklash (yangi parol o'rnatish)."""
    user = ArenaUser.query.get_or_404(uid)
    new_pw     = request.form.get('new_password', '')
    confirm_pw = request.form.get('confirm_password', '')

    if len(new_pw) < 6:
        flash('Yangi parol kamida 6 ta belgidan iborat bo\'lishi kerak.', 'danger')
    elif new_pw != confirm_pw:
        flash('Parollar mos kelmadi.', 'danger')
    else:
        user.set_password(new_pw)
        db.session.commit()
        flash(f'{user.username} uchun parol yangilandi.', 'success')

    return redirect(url_for('arena.arena_admin_user_edit', uid=uid))


@arena_bp.route('/admin/users/<int:uid>/clear_subs', methods=['POST'])
@arena_admin_required
def arena_admin_user_clear_subs(uid):
    """Admin: foydalanuvchining barcha urinishlarini o'chirish (akkaunt qoladi)."""
    user = ArenaUser.query.get_or_404(uid)

    subs = ArenaSubmission.query.filter_by(user_id=uid).all()
    # Update problem counters
    for s in subs:
        prob = ArenaProblem.query.get(s.problem_id)
        if prob:
            if prob.submission_count > 0:
                prob.submission_count -= 1
            if s.status == 'AC' and prob.accepted_count > 0:
                prob.accepted_count -= 1

    ArenaSubmission.query.filter_by(user_id=uid).delete()

    # Reset user stats
    user.problems_solved = 0
    user.rating          = 0
    user.total_stars     = 0

    try:
        db.session.commit()
        flash(f'{user.username} foydalanuvchining barcha urinishlari o\'chirildi.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Xato: {e}', 'danger')

    return redirect(url_for('arena.arena_admin_user_edit', uid=uid))


@arena_bp.route('/admin/users/<int:uid>/delete', methods=['POST'])
@arena_admin_required
def arena_admin_user_delete(uid):
    """Admin: foydalanuvchini va uning urinishlarini butunlay o'chirish."""
    user = ArenaUser.query.get_or_404(uid)
    me   = _current_user()

    # Adminni o'zini o'chirib bo'lmaydi
    if me and user.id == me.id:
        flash('O\'zingizni o\'chira olmaysiz.', 'danger')
        return redirect(url_for('arena.arena_admin_user_edit', uid=uid))
    if user.username.lower() == ARENA_ADMIN_USERNAME:
        flash('Admin akkauntini o\'chirib bo\'lmaydi.', 'danger')
        return redirect(url_for('arena.arena_admin_user_edit', uid=uid))

    # Confirm typing
    typed = request.form.get('confirm_username', '').strip()
    if typed != user.username:
        flash('Tasdiqlash uchun username noto\'g\'ri kiritildi.', 'danger')
        return redirect(url_for('arena.arena_admin_user_edit', uid=uid))

    # Decrement problem counters for each submission
    subs = ArenaSubmission.query.filter_by(user_id=uid).all()
    for s in subs:
        prob = ArenaProblem.query.get(s.problem_id)
        if prob:
            if prob.submission_count > 0:
                prob.submission_count -= 1
            if s.status == 'AC' and prob.accepted_count > 0:
                prob.accepted_count -= 1

    ArenaSubmission.query.filter_by(user_id=uid).delete()
    uname = user.username
    db.session.delete(user)

    try:
        db.session.commit()
        flash(f'"{uname}" foydalanuvchisi va uning barcha urinishlari o\'chirildi.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Xato: {e}', 'danger')
        return redirect(url_for('arena.arena_admin_user_edit', uid=uid))

    return redirect(url_for('arena.arena_admin_users'))


def _arena_problem_form(problem):
    """Arena admin problem form (arena layout)."""
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

        examples = []
        for i in range(1, 6):
            inp = request.form.get(f'ex_input_{i}', '').strip()
            out = request.form.get(f'ex_output_{i}', '').strip()
            exp = request.form.get(f'ex_explanation_{i}', '').strip()
            if inp or out:
                examples.append({'input': inp, 'output': out, 'explanation': exp})

        hidden_tests_raw = request.form.get('hidden_tests_json', '').strip()
        hidden_tests = []
        if hidden_tests_raw:
            try:
                parsed = json.loads(hidden_tests_raw)
                if isinstance(parsed, list):
                    hidden_tests = [
                        {'input': str(t.get('input', '')), 'output': str(t.get('output', ''))}
                        for t in parsed
                        if isinstance(t, dict) and str(t.get('output', '')).strip()
                    ]
            except (ValueError, TypeError):
                error = 'Yashirin testlar JSON formati noto\'g\'ri.'

        if not error:
            if not code:
                error = 'Kod majburiy.'
            elif not title:
                error = 'Sarlavha majburiy.'
            elif not description:
                error = 'Tavsif majburiy.'
            elif difficulty not in ('easy', 'medium', 'hard'):
                error = 'Murakkablik noto\'g\'ri.'
            elif len(hidden_tests) < 10:
                error = f'Kamida 10 ta yashirin test talab qilinadi (hozir {len(hidden_tests)} ta).'
            else:
                existing = ArenaProblem.query.filter_by(code=code).first()
                if existing and (problem is None or existing.id != problem.id):
                    error = f'"{code}" kodi allaqachon mavjud.'

        if not error:
            if problem is None:
                problem = ArenaProblem()
                db.session.add(problem)
            problem.code           = code
            problem.title          = title
            problem.description    = description
            problem.input_format   = input_fmt
            problem.output_format  = output_fmt
            problem.constraints    = constraints
            problem.examples       = json.dumps(examples, ensure_ascii=False)
            problem.hidden_tests   = json.dumps(hidden_tests, ensure_ascii=False, indent=2)
            problem.difficulty     = difficulty
            problem.category       = category
            problem.correct_answer = correct_ans
            problem.time_limit     = float(time_lim) if time_lim else 1.0
            problem.memory_limit   = int(mem_lim) if mem_lim else 256
            problem.is_active      = is_active
            db.session.commit()
            flash(f'Masala saqlandi. {len(hidden_tests)} ta yashirin test.', 'success')
            return redirect(url_for('arena.arena_admin_problems'))

    try:
        ex_list = json.loads(problem.examples) if problem and problem.examples else []
    except (ValueError, TypeError):
        ex_list = []
    while len(ex_list) < 5:
        ex_list.append({'input': '', 'output': '', 'explanation': ''})

    hidden_tests_pretty = (problem.hidden_tests or '[]') if problem else '[]'

    return render_template('arena/admin_problem_form.html',
                           problem=problem,
                           ex_list=ex_list,
                           hidden_tests_json=hidden_tests_pretty,
                           error=error)
