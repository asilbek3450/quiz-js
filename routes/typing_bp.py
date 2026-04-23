"""
Multiplayer typing-race module.
Rooms are ephemeral (in-memory only — no DB required).
PythonAnywhere-compatible: uses simple HTTP polling, no WebSockets.
"""
import json, random, string, time, threading
from flask import (Blueprint, render_template, request, session,
                   jsonify, redirect, url_for)
from extensions import csrf
from models import db, TypingResult

typing_bp = Blueprint('typing', __name__, url_prefix='/typing')

# ── In-memory store ────────────────────────────────────────────────────────────
_lock = threading.Lock()
ROOMS: dict = {}   # code → room_dict

# ── Texts loaded from static/texts.json ───────────────────────────────────────
_TEXTS_JSON_PATH = __file__[:__file__.rfind('routes')] + 'static/texts.json'
with open(_TEXTS_JSON_PATH, encoding='utf-8') as _f:
    _TEXTS_DATA: dict = json.load(_f)


def _pick_text(lang: str = 'uz', level: str = 'easy', exclude: str = None) -> str:
    candidates = _TEXTS_DATA.get(lang, {}).get(level) or _TEXTS_DATA.get('uz', {}).get('easy', [])
    texts = [item['text'] for item in candidates]
    if exclude and len(texts) > 1:
        texts = [t for t in texts if t != exclude]
    return random.choice(texts)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _new_uid() -> str:
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))


def _gen_code() -> str:
    for _ in range(200):
        c = ''.join(random.choices(string.digits, k=6))
        if c not in ROOMS:
            return c
    return ''.join(random.choices(string.digits, k=8))


def _new_participant(name: str) -> dict:
    return {
        'name': name,
        'progress': 0,
        'wpm': 0,
        'finished': False,
        'finish_time': None,
        'rank': None,
        'last_seen': time.time(),
    }


def _cleanup() -> None:
    now = time.time()
    with _lock:
        expired = [k for k, v in ROOMS.items() if now - v['created_at'] > 7200]
        for k in expired:
            del ROOMS[k]


def _get_uid() -> str:
    uid = session.get('typing_uid') or _new_uid()
    session['typing_uid'] = uid
    return uid


# ── Routes ─────────────────────────────────────────────────────────────────────

@typing_bp.route('/')
def index():
    return render_template('typing/index.html')


@typing_bp.route('/solo', methods=['POST'])
@csrf.exempt
def solo():
    data  = request.get_json(silent=True) or {}
    name  = (data.get('name') or '').strip()[:30]
    lang  = data.get('lang',  'uz')
    level = data.get('level', 'easy')
    if not name:
        return jsonify({'error': 'Ism kiritilmadi'}), 400

    uid = _get_uid()
    session['typing_name'] = name
    _cleanup()

    code = _gen_code()
    text = _pick_text(lang, level)
    now  = time.time()

    with _lock:
        ROOMS[code] = {
            'code':          code,
            'creator_id':    uid,
            'text':          text,
            'state':         'racing',
            'participants':  {uid: _new_participant(name)},
            'start_time':    now,
            'countdown_end': None,
            'finish_count':  0,
            'created_at':    now,
            'is_solo':       True,
            'reset_count':   0,
        }

    return jsonify({'code': code, 'url': url_for('typing.room', code=code)})


@typing_bp.route('/create', methods=['POST'])
@csrf.exempt
def create_room():
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or request.form.get('name') or '').strip()[:30]
    if not name:
        return jsonify({'error': 'Ism kiritilmadi'}), 400

    _cleanup()
    uid  = _get_uid()
    session['typing_name'] = name
    code = _gen_code()
    text = _pick_text('uz', 'easy')

    with _lock:
        ROOMS[code] = {
            'code':          code,
            'creator_id':    uid,
            'text':          text,
            'state':         'waiting',
            'participants':  {uid: _new_participant(name)},
            'start_time':    None,
            'countdown_end': None,
            'finish_count':  0,
            'created_at':    time.time(),
            'is_solo':       False,
            'reset_count':   0,
        }

    return jsonify({'code': code, 'url': url_for('typing.room', code=code)})


@typing_bp.route('/join', methods=['POST'])
@csrf.exempt
def join_room_req():
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or request.form.get('name') or '').strip()[:30]
    code = (data.get('code') or request.form.get('code') or '').strip()

    if not name:
        return jsonify({'error': 'Ism kiritilmadi'}), 400
    if not code:
        return jsonify({'error': 'Xona kodi kiritilmadi'}), 400

    with _lock:
        if code not in ROOMS:
            return jsonify({'error': "Bunday xona topilmadi. Kodni tekshiring."}), 404
        room = ROOMS[code]
        if room['state'] != 'waiting':
            return jsonify({'error': "Poyga boshlangan. Keyingi poyga kuting."}), 400
        if len(room['participants']) >= 50:
            return jsonify({'error': "Xona to'ldi (max 50 kishi)."}), 400

        uid = _get_uid()
        session['typing_name'] = name
        room['participants'][uid] = _new_participant(name)

    return jsonify({'code': code, 'url': url_for('typing.room', code=code)})


@typing_bp.route('/room/<code>')
def room(code):
    with _lock:
        if code not in ROOMS:
            return redirect(url_for('typing.index'))
        room_data = dict(ROOMS[code])

    uid = session.get('typing_uid')
    if not uid or uid not in room_data['participants']:
        return redirect(url_for('typing.index'))

    return render_template(
        'typing/room.html',
        room=room_data,
        code=code,
        is_creator=(room_data['creator_id'] == uid),
        my_uid=uid,
        text=room_data['text'],
        is_solo=room_data.get('is_solo', False),
    )


@typing_bp.route('/api/room/<code>/state')
@csrf.exempt
def room_state(code):
    with _lock:
        if code not in ROOMS:
            return jsonify({'error': 'not_found'}), 404
        room = ROOMS[code]

    uid = session.get('typing_uid')
    now = time.time()

    with _lock:
        if uid and uid in room['participants']:
            room['participants'][uid]['last_seen'] = now

        if room['state'] == 'waiting':
            stale = [
                k for k, v in room['participants'].items()
                if now - v.get('last_seen', now) > 15
                and k != room['creator_id']
            ]
            for k in stale:
                del room['participants'][k]

        if room['state'] == 'countdown' and room.get('countdown_end'):
            if now >= room['countdown_end']:
                room['state'] = 'racing'
                room['start_time'] = room['countdown_end']

        text_len = len(room['text'])
        participants_out = [
            {
                'id':       k,
                'name':     v['name'],
                'progress': v['progress'],
                'wpm':      v['wpm'],
                'finished': v['finished'],
                'rank':     v['rank'],
                'is_me':    k == uid,
                'pct':      round(v['progress'] / text_len * 100) if text_len else 0,
            }
            for k, v in room['participants'].items()
        ]

    participants_out.sort(key=lambda x: (-x['pct'], x['name']))

    return jsonify({
        'state':         room['state'],
        'text':          room['text'],
        'text_len':      text_len,
        'reset_count':   room.get('reset_count', 0),
        'participants':  participants_out,
        'countdown_end': room.get('countdown_end'),
        'start_time':    room.get('start_time'),
        'is_creator':    uid == room.get('creator_id'),
        'is_solo':       room.get('is_solo', False),
        'code':          code,
    })


@typing_bp.route('/api/room/<code>/start', methods=['POST'])
@csrf.exempt
def start_race(code):
    with _lock:
        if code not in ROOMS:
            return jsonify({'error': 'not_found'}), 404
        room = ROOMS[code]
        uid  = session.get('typing_uid')

        if room['creator_id'] != uid:
            return jsonify({'error': 'Faqat yaratuvchi boshlaydi'}), 403
        if room['state'] != 'waiting':
            return jsonify({'error': 'Allaqachon boshlangan'}), 400

        data  = request.get_json(silent=True) or {}
        lang  = data.get('lang',  'uz')
        level = data.get('level', 'easy')
        room['text']          = _pick_text(lang, level, exclude=room.get('text'))
        room['state']         = 'countdown'
        room['countdown_end'] = time.time() + 3.5

    return jsonify({'ok': True})


@typing_bp.route('/api/room/<code>/reset', methods=['POST'])
@csrf.exempt
def reset_room(code):
    uid = session.get('typing_uid')
    with _lock:
        if code not in ROOMS:
            return jsonify({'ok': False, 'error': 'Xona topilmadi'}), 404
        room = ROOMS[code]
        if room['creator_id'] != uid:
            return jsonify({'ok': False, 'error': "Faqat yaratuvchi qayta boshlaydi"}), 403

        data  = request.get_json(silent=True) or {}
        lang  = data.get('lang',  'uz')
        level = data.get('level', 'easy')

        room['state']         = 'waiting'
        room['start_time']    = None
        room['countdown_end'] = None
        room['finish_count']  = 0
        room['text']          = _pick_text(lang, level, exclude=room.get('text'))
        room['reset_count']   = room.get('reset_count', 0) + 1
        room['created_at']    = time.time()

        for p in room['participants'].values():
            p['progress']    = 0
            p['wpm']         = 0
            p['finished']    = False
            p['finish_time'] = None
            p['rank']        = None
            p['last_seen']   = time.time()

    return jsonify({'ok': True})


@typing_bp.route('/api/room/<code>/progress', methods=['POST'])
@csrf.exempt
def update_progress(code):
    with _lock:
        if code not in ROOMS:
            return jsonify({'error': 'not_found'}), 404
        room = ROOMS[code]

    uid = session.get('typing_uid')
    if not uid or uid not in room['participants']:
        return jsonify({'error': 'not_in_room'}), 403

    if room['state'] not in ('racing', 'countdown'):
        return jsonify({'ok': True})

    data          = request.get_json(silent=True) or {}
    text_len      = len(room['text'])
    progress      = min(max(int(data.get('progress', 0)), 0), text_len)
    wpm           = max(0, min(int(data.get('wpm', 0)), 999))
    accuracy      = max(0, min(int(data.get('accuracy', 100)), 100))
    chars_correct = max(0, int(data.get('chars_correct', 0)))
    just_finished = False

    with _lock:
        p = room['participants'][uid]
        p['progress']  = progress
        p['wpm']       = wpm
        p['last_seen'] = time.time()

        if progress >= text_len and not p['finished']:
            p['finished']    = True
            p['finish_time'] = time.time()
            room['finish_count'] += 1
            p['rank']        = room['finish_count']
            just_finished    = True

        if (room['state'] == 'racing'
                and all(v['finished'] for v in room['participants'].values())):
            room['state'] = 'finished'

    if just_finished and wpm > 0:
        name = room['participants'][uid]['name']
        try:
            record = TypingResult(
                name=name,
                wpm=wpm,
                accuracy=accuracy,
                chars_correct=chars_correct,
                chars_total=text_len,
                is_solo=room.get('is_solo', False),
            )
            db.session.add(record)
            db.session.commit()
        except Exception:
            db.session.rollback()

    return jsonify({'ok': True})


@typing_bp.route('/leaderboard')
@csrf.exempt
def leaderboard():
    is_admin = session.get('admin_user') == 'asilbek'
    top = (TypingResult.query
           .order_by(TypingResult.wpm.desc())
           .limit(10).all())
    rows = []
    for i, r in enumerate(top):
        row = {
            'rank':     i + 1,
            'name':     r.name,
            'wpm':      r.wpm,
            'accuracy': r.accuracy,
            'date':     r.created_at.strftime('%d.%m.%Y'),
            'is_solo':  r.is_solo,
        }
        if is_admin:
            row['id'] = r.id
        rows.append(row)
    return jsonify(rows)


@typing_bp.route('/leaderboard/<int:rid>/delete', methods=['POST'])
@csrf.exempt
def leaderboard_delete(rid):
    if session.get('admin_user') != 'asilbek':
        return jsonify({'error': 'Ruxsat yo\'q'}), 403
    r = TypingResult.query.get_or_404(rid)
    db.session.delete(r)
    db.session.commit()
    return jsonify({'ok': True})


@typing_bp.route('/leaderboard/clear', methods=['POST'])
@csrf.exempt
def leaderboard_clear():
    if session.get('admin_user') != 'asilbek':
        return jsonify({'error': 'Ruxsat yo\'q'}), 403
    TypingResult.query.delete()
    db.session.commit()
    return jsonify({'ok': True})
