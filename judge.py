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

# Python traceback belgilari — haqiqiy kod xatosi
_PY_ERROR = re.compile(
    r'Traceback \(most recent call last\)|'
    r'(SyntaxError|NameError|TypeError|ValueError|IndexError|'
    r'KeyError|AttributeError|ZeroDivisionError|RecursionError|'
    r'MemoryError|RuntimeError|StopIteration|IndentationError):',
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


def run_code(code: str, language: str, stdin_data: str, time_limit: float = 10.0):
    """
    Kodni ishlatadi. Qaytaradi:
      {'verdict': 'OK'|'TLE'|'RE'|'CE'|'SE', 'output': str, 'error': str, 'time': float}

    Verdiktlar:
      OK  — muvaffaqiyatli bajarildi
      TLE — vaqt limiti oshdi (yoki OS tomonidan o'ldirildi)
      RE  — foydalanuvchi kodi xatosi (Python Traceback bor)
      CE  — kompilyatsiya / taqiqlangan operatsiya xatosi
      SE  — server infra xatosi (foydalanuvchi kodi bilan bog'liq emas)
    """
    if language not in LANGUAGES:
        return {'verdict': 'CE', 'output': '',
                'error': f"Til qo'llab-quvvatlanmaydi: {language}", 'time': 0.0}

    ok, msg = _check(code)
    if not ok:
        return {'verdict': 'CE', 'output': '', 'error': msg, 'time': 0.0}

    lang = LANGUAGES[language]

    # Server xatolari uchun 2 marta qayta urinish (jami 3 ta urinish)
    for attempt in range(3):
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

            if proc.returncode == 0:
                # Muvaffaqiyatli — stderr (warnings) e'tiborsiz
                return {'verdict': 'OK', 'output': stdout, 'error': '', 'time': elapsed}

            # returncode < 0 → OS SIGKILL/SIGTERM (resurs limiti) → TLE sifatida
            if proc.returncode < 0:
                return {'verdict': 'TLE', 'output': '',
                        'error': 'Vaqt yoki xotira limiti oshdi.', 'time': elapsed}

            # returncode > 0 — Python traceback bormi? → haqiqiy RE
            if _PY_ERROR.search(stderr):
                # Faqat muhim qism: oxirgi 10 qator
                lines = stderr.strip().splitlines()
                short = '\n'.join(lines[-10:]) if len(lines) > 10 else stderr.strip()
                return {'verdict': 'RE', 'output': stdout, 'error': short, 'time': elapsed}

            # returncode > 0, Python traceback yo'q:
            # Agar stdout mavjud bo'lsa — kod to'g'ri ishlagan, exit code muhit xatosi
            # (PythonAnywhere va ba'zi serverlarda to'g'ri kod ham non-zero qaytarishi mumkin)
            if stdout.strip():
                return {'verdict': 'OK', 'output': stdout, 'error': '', 'time': elapsed}

            # stdout ham yo'q → server/muhit xatosi, qayta urinish
            if attempt < 2:
                time.sleep(0.3 * (attempt + 1))  # 0.3s, 0.6s
                continue
            return {'verdict': 'SE', 'output': '', 'error': '', 'time': elapsed}

        except subprocess.TimeoutExpired:
            return {'verdict': 'TLE', 'output': '',
                    'error': f'Vaqt limiti oshdi ({time_limit}s).', 'time': time_limit}

        except (OSError, PermissionError, FileNotFoundError):
            # Server infra muammosi — qayta urinib ko'ramiz
            if attempt < 2:
                time.sleep(0.3 * (attempt + 1))
                continue
            return {'verdict': 'SE', 'output': '', 'error': '', 'time': 0.0}

        except Exception as e:
            # Boshqa kutilmagan xato
            err_str = str(e)
            if _PY_ERROR.search(err_str):
                return {'verdict': 'RE', 'output': '', 'error': err_str, 'time': 0.0}
            return {'verdict': 'SE', 'output': '', 'error': '', 'time': 0.0}

        finally:
            if tmp:
                try:
                    os.unlink(tmp)
                except OSError:
                    pass

    return {'verdict': 'SE', 'output': '', 'error': '', 'time': 0.0}


def _norm(s: str) -> str:
    return s.strip().replace('\r\n', '\n').replace('\r', '\n')


def judge(code: str, language: str, test_input: str,
          expected_output: str, time_limit: float = 10.0):
    """
    Kodni ishlatib, natijani expected_output bilan solishtiradi.
    Qaytaradi: run_code natijasiga qo'shimcha 'verdict' AC|WA|TLE|RE|CE|SE.
    """
    result = run_code(code, language, test_input, time_limit)

    if result['verdict'] in ('TLE', 'CE', 'SE'):
        return result

    # RE → WA: kod xatosi bo'lsa ham faqat "Wrong Answer" ko'rsatiladi
    if result['verdict'] == 'RE':
        result['verdict'] = 'WA'
        result['error']   = ''
        return result

    user_out = _norm(result['output'])
    expected = _norm(expected_output or '')

    result['verdict'] = 'AC' if user_out == expected else 'WA'
    return result
