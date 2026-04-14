"""
Arena kod baholash (judge) moduli.
Foydalanuvchi kodini subprocess orqali ishlatib, natijani tekshiradi.
"""
import subprocess, tempfile, os, sys, time, re

# ── Qo'llab-quvvatlanadigan tillar ────────────────────────────────────────────
LANGUAGES = {
    'python': {
        'ext': '.py',
        'cmd': [sys.executable, '{file}'],
    },
}

# ── Xavfli pattern'lar (maktab muhiti uchun) ─────────────────────────────────
_BANNED = re.compile(
    r'(__import__|importlib|subprocess|shutil\.rmtree|os\.remove|'
    r'os\.unlink|os\.system|os\.popen|socket\.|ctypes|'
    r'open\s*\(.*["\'][aw]["\'])',
    re.IGNORECASE
)

MAX_OUTPUT = 4096   # bayt
MAX_CODE   = 16384  # bayt


def _check(code: str):
    if len(code) > MAX_CODE:
        return False, "Kod juda uzun (16 KB dan oshmasin)."
    m = _BANNED.search(code)
    if m:
        return False, f"Taqiqlangan operatsiya: `{m.group()}`"
    return True, ""


def run_code(code: str, language: str, stdin_data: str, time_limit: float = 5.0):
    """
    Kodni ishlatadi. Qaytaradi:
      {'verdict': 'OK'|'TLE'|'RE'|'CE', 'output': str, 'error': str, 'time': float}
    """
    if language not in LANGUAGES:
        return {'verdict': 'CE', 'output': '',
                'error': f"Til qo'llab-quvvatlanmaydi: {language}", 'time': 0.0}

    ok, msg = _check(code)
    if not ok:
        return {'verdict': 'CE', 'output': '', 'error': msg, 'time': 0.0}

    lang = LANGUAGES[language]
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(
                suffix=lang['ext'], delete=False,
                mode='w', encoding='utf-8') as f:
            f.write(code)
            tmp = f.name

        cmd = [c.replace('{file}', tmp) for c in lang['cmd']]
        t0  = time.monotonic()

        proc = subprocess.run(
            cmd,
            input=stdin_data or '',
            capture_output=True,
            text=True,
            timeout=time_limit,
        )
        elapsed = round(time.monotonic() - t0, 3)

        stdout = proc.stdout[:MAX_OUTPUT]
        stderr = proc.stderr[:1024]

        if proc.returncode != 0:
            return {'verdict': 'RE', 'output': stdout, 'error': stderr, 'time': elapsed}

        return {'verdict': 'OK', 'output': stdout, 'error': stderr, 'time': elapsed}

    except subprocess.TimeoutExpired:
        return {'verdict': 'TLE', 'output': '',
                'error': f'Vaqt limiti oshdi ({time_limit}s)', 'time': time_limit}
    except Exception as e:
        return {'verdict': 'RE', 'output': '', 'error': str(e), 'time': 0.0}
    finally:
        if tmp:
            try:
                os.unlink(tmp)
            except OSError:
                pass


def _norm(s: str) -> str:
    return s.strip().replace('\r\n', '\n').replace('\r', '\n')


def judge(code: str, language: str, test_input: str,
          expected_output: str, time_limit: float = 5.0):
    """
    Kodni ishlatib, natijani expected_output bilan solishtiradi.
    Qaytaradi: run_code natijasiга qo'shimcha 'verdict' AC|WA|TLE|RE|CE.
    """
    result = run_code(code, language, test_input, time_limit)

    if result['verdict'] in ('TLE', 'RE', 'CE'):
        return result            # allaqachon to'g'ri verdict

    user_out = _norm(result['output'])
    expected = _norm(expected_output or '')

    result['verdict'] = 'AC' if user_out == expected else 'WA'
    result['expected'] = expected     # debuglash uchun (WA da ko'rsatilmaydi)
    return result
