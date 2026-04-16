"""
Arena kod baholash (judge) moduli.
PythonAnywhere uchun optimallashtirilgan: exec() + threading.
subprocess ishlatilmaydi — server cheklovlarisiz barqaror ishlaydi.
"""
import sys, re, io, time, threading, types
import builtins as _builtins

# ── Qo'llab-quvvatlanadigan tillar ────────────────────────────────────────────
LANGUAGES = {
    'python': {'ext': '.py'},
}

# ── Xavfli pattern'lar (maktab muhiti uchun) ─────────────────────────────────
_BANNED = re.compile(
    r'(__import__\s*\(|importlib\s*\.|subprocess|shutil\s*\.\s*rmtree|'
    r'os\s*\.\s*(?:remove|unlink|system|popen|exec[lv]?[pe]?)|'
    r'socket\s*\.|ctypes)',
    re.IGNORECASE
)

MAX_OUTPUT = 4096   # bayt
MAX_CODE   = 16384  # bayt

# Ruxsat etilgan import'lar
_ALLOWED_IMPORTS = frozenset({
    'math', 'cmath', 'random', 'string', 'itertools', 'functools',
    'collections', 'heapq', 'bisect', 'decimal', 'fractions',
    'statistics', 'operator', 'copy', 're', 'datetime',
    'array', 'struct', 'io', 'json', 'time', 'calendar',
    'abc', 'enum', 'dataclasses', 'typing',
})

# Xavfli builtin'lar — exec namespace dan olib tashlanadi
_BLOCKED_BUILTINS = frozenset({
    'exec', 'eval', 'compile', 'open', '__loader__', '__spec__',
    'breakpoint', 'help', 'credits', 'license', 'copyright',
    'quit', 'exit',
})


def _check(code: str):
    if len(code) > MAX_CODE:
        return False, "Kod juda uzun (16 KB dan oshmasin)."
    m = _BANNED.search(code)
    if m:
        return False, f"Taqiqlangan operatsiya: `{m.group()}`"
    return True, ""


def run_code(code: str, language: str, stdin_data: str, time_limit: float = 10.0):
    """
    Kodni exec() + threading orqali ishlatadi.
    Qaytaradi:
      {'verdict': 'OK'|'TLE'|'RE'|'CE', 'output': str, 'error': str, 'time': float}

    Verdiktlar:
      OK  — muvaffaqiyatli bajarildi
      TLE — vaqt limiti oshdi
      RE  — foydalanuvchi kodi xatosi (exception yuz berdi)
      CE  — sintaksis xatosi yoki taqiqlangan operatsiya
    """
    if language not in LANGUAGES:
        return {'verdict': 'CE', 'output': '',
                'error': f"Til qo'llab-quvvatlanmaydi: {language}", 'time': 0.0}

    ok, msg = _check(code)
    if not ok:
        return {'verdict': 'CE', 'output': '', 'error': msg, 'time': 0.0}

    # Sintaksis tekshiruvi (tez xatolikni aniqlash)
    try:
        compiled = compile(code, '<student_code>', 'exec')
    except SyntaxError as e:
        return {'verdict': 'CE', 'output': '',
                'error': f'SyntaxError: {e.msg} (qator {e.lineno})', 'time': 0.0}

    stdout_buf = io.StringIO()
    stdin_buf  = io.StringIO(stdin_data or '')
    result     = {'verdict': 'OK', 'output': '', 'error': '', 'time': 0.0}
    done_event = threading.Event()

    def _run():
        # ── I/O funksiyalari ──────────────────────────────────────────────────
        def _safe_print(*args, sep=' ', end='\n', file=None, flush=False):  # file/flush: print() bilan moslik uchun
            if stdout_buf.tell() < MAX_OUTPUT:
                stdout_buf.write(sep.join(str(a) for a in args) + end)

        def _safe_input(prompt=''):
            if prompt:
                _safe_print(str(prompt), end='')
            return stdin_buf.readline().rstrip('\n')

        # ── Fake sys moduli (stdin/stdout yo'naltirish uchun) ─────────────────
        fake_sys = types.ModuleType('sys')
        fake_sys.stdin   = stdin_buf
        fake_sys.stdout  = stdout_buf
        fake_sys.stderr  = io.StringIO()
        fake_sys.argv    = ['<student_code>']
        fake_sys.version = sys.version
        fake_sys.version_info = sys.version_info
        fake_sys.maxsize = sys.maxsize
        fake_sys.path    = []
        fake_sys.setrecursionlimit = lambda n: None   # no-op (xavfsizlik uchun)
        fake_sys.getrecursionlimit = lambda: 1000
        fake_sys.exit    = lambda *a: (_ for _ in ()).throw(SystemExit(*a))

        # ── Xavfsiz import ────────────────────────────────────────────────────
        def _safe_import(name, globals=None, locals=None, fromlist=(), level=0):
            base = name.split('.')[0]
            if base == 'sys':
                return fake_sys
            if base in _ALLOWED_IMPORTS:
                return __import__(name, globals, locals, fromlist, level)
            raise ImportError(
                f"'{name}' moduli bu muhitda ruxsat etilmagan.\n"
                f"Ruxsat etilganlar: {', '.join(sorted(_ALLOWED_IMPORTS))}"
            )

        # ── Xavfsiz builtin'lar ───────────────────────────────────────────────
        safe_builtins = {
            name: getattr(_builtins, name)
            for name in dir(_builtins)
            if not name.startswith('_') and name not in _BLOCKED_BUILTINS
        }
        safe_builtins['print']      = _safe_print
        safe_builtins['input']      = _safe_input
        safe_builtins['__import__'] = _safe_import

        # ── Exec namespace ────────────────────────────────────────────────────
        globs = {
            '__name__':     '__main__',
            '__doc__':      None,
            '__package__':  None,
            '__builtins__': safe_builtins,
            '__import__':   _safe_import,
            'sys':          fake_sys,
        }

        try:
            exec(compiled, globs)
        except SystemExit:
            pass   # exit() chaqirildi — normal holat sifatida qabul qilamiz
        except RecursionError:
            result['verdict'] = 'RE'
            result['error']   = 'RecursionError: rekursiya chuqurligi limiti oshdi.'
        except MemoryError:
            result['verdict'] = 'RE'
            result['error']   = 'MemoryError: xotira yetishmadi.'
        except Exception as e:
            result['verdict'] = 'RE'
            result['error']   = f'{type(e).__name__}: {e}'
        finally:
            done_event.set()

    t0     = time.monotonic()
    worker = threading.Thread(target=_run, daemon=True)
    worker.start()
    finished = done_event.wait(timeout=time_limit)
    elapsed  = round(time.monotonic() - t0, 3)

    result['time'] = elapsed

    if not finished:
        # Worker hali ham ishlayapti — TLE
        result['verdict'] = 'TLE'
        result['output']  = ''
        result['error']   = f'Vaqt limiti oshdi ({time_limit}s).'
    else:
        result['output'] = stdout_buf.getvalue()[:MAX_OUTPUT]

    return result


def _norm(s: str) -> str:
    return s.strip().replace('\r\n', '\n').replace('\r', '\n')


def judge(code: str, language: str, test_input: str,
          expected_output: str, time_limit: float = 10.0):
    """
    Kodni ishlatib, natijani expected_output bilan solishtiradi.
    Qaytaradi: run_code natijasiga qo'shimcha 'verdict' AC|WA|TLE|RE|CE.
    """
    result = run_code(code, language, test_input, time_limit)

    if result['verdict'] in ('TLE', 'CE'):
        return result

    # RE → WA: foydalanuvchiga "Wrong Answer" ko'rsatiladi
    if result['verdict'] == 'RE':
        result['verdict'] = 'WA'
        result['error']   = ''
        return result

    user_out = _norm(result['output'])
    expected = _norm(expected_output or '')
    result['verdict'] = 'AC' if user_out == expected else 'WA'
    return result
