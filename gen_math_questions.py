#!/usr/bin/env python3
"""
Matematika fani uchun har bir sinf (1-11) ga 250 tadan savol generatsiya qiladi.
200 ta MCQ + 50 ta ochiq (open_ended) savol.
Savollar O'zbekiston matematika o'quv dasturi kompetensiyalariga asoslangan.
"""
import sys, os, random, math
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('FLASK_ENV', 'development')

from app import create_app
from models import db, Subject, Question, Admin

# ─── Helpers ──────────────────────────────────────────────────────────────────

def nearby(correct, count=3, lo=1, hi=5):
    """Generate nearby wrong answers (integers)."""
    ds = set()
    attempts = 0
    while len(ds) < count and attempts < 100:
        delta = random.randint(lo, hi) * random.choice([-1, 1])
        d = correct + delta
        if d != correct:
            ds.add(d)
        attempts += 1
    # Fill remaining if needed
    while len(ds) < count:
        ds.add(correct + len(ds) + 1)
    return list(ds)[:count]


def nearby_float(correct, count=3, lo=0.1, hi=2.0, decimals=1):
    """Generate nearby wrong float answers."""
    ds = set()
    attempts = 0
    while len(ds) < count and attempts < 100:
        delta = round(random.uniform(lo, hi) * random.choice([-1, 1]), decimals)
        d = round(correct + delta, decimals)
        if d != correct:
            ds.add(d)
        attempts += 1
    while len(ds) < count:
        ds.add(round(correct + (len(ds) + 1) * 0.5, decimals))
    return list(ds)[:count]


def make_mcq(text, correct_val, distractors, difficulty=2):
    """Create MCQ dict. correct_val and distractors are strings."""
    correct_str = str(correct_val)
    dist_strs = [str(d) for d in distractors[:3]]
    options = [correct_str] + dist_strs
    random.shuffle(options)
    idx = options.index(correct_str)
    keys = ['A', 'B', 'C', 'D']
    return {
        'text': text,
        'a': options[0], 'b': options[1], 'c': options[2], 'd': options[3],
        'correct': keys[idx],
        'type': 'mcq',
        'difficulty': difficulty
    }


def make_open(text, difficulty=2):
    """Create open-ended question dict."""
    return {
        'text': text,
        'type': 'open_ended',
        'difficulty': difficulty
    }


def unique_questions(generator_func, needed, max_attempts=5000):
    """Generate unique questions from a generator function."""
    seen_texts = set()
    questions = []
    attempts = 0
    while len(questions) < needed and attempts < max_attempts:
        q = generator_func()
        if q['text'] not in seen_texts:
            seen_texts.add(q['text'])
            questions.append(q)
        attempts += 1
    return questions


def gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def lcm(a, b):
    return a * b // gcd(a, b)


# ═══════════════════════════════════════════════════════════════════════════════
#  GRADE 1 — 1-sinf: 20 ichida sonlar, qo'shish, ayirish
# ═══════════════════════════════════════════════════════════════════════════════

def grade_1_mcq():
    """Generate one MCQ for grade 1."""
    template = random.choice([
        'add', 'sub', 'compare', 'missing_add', 'missing_sub',
        'count', 'order', 'even_odd', 'next_number', 'before_number'
    ])
    
    if template == 'add':
        a, b = random.randint(1, 10), random.randint(1, 10)
        c = a + b
        return make_mcq(f"{a} + {b} = ?", c, nearby(c, 3, 1, 3), 1)
    
    elif template == 'sub':
        a = random.randint(5, 20)
        b = random.randint(1, a)
        c = a - b
        return make_mcq(f"{a} - {b} = ?", c, nearby(c, 3, 1, 3), 1)
    
    elif template == 'compare':
        a, b = random.sample(range(1, 21), 2)
        correct = ">" if a > b else "<"
        return make_mcq(
            f"{a} ☐ {b} orasiga qanday belgi qo'yiladi?",
            correct, ["<" if correct == ">" else ">", "=", "≥" if correct == "<" else "≤"], 1
        )
    
    elif template == 'missing_add':
        a = random.randint(1, 10)
        c = random.randint(a + 1, 18)
        b = c - a
        return make_mcq(f"{a} + ? = {c}. '?' o'rniga qanday son qo'yiladi?", b, nearby(b, 3, 1, 3), 2)
    
    elif template == 'missing_sub':
        a = random.randint(5, 18)
        c = random.randint(0, a - 1)
        b = a - c
        return make_mcq(f"{a} - ? = {c}. '?' o'rniga qanday son qo'yiladi?", b, nearby(b, 3, 1, 3), 2)
    
    elif template == 'count':
        n = random.randint(3, 15)
        return make_mcq(
            f"Sonlar qatorida {n} dan keyin qaysi son keladi?",
            n + 1, nearby(n + 1, 3, 1, 2), 1
        )
    
    elif template == 'order':
        a, b, c = sorted(random.sample(range(1, 20), 3))
        correct = f"{a}, {b}, {c}"
        wrong1 = f"{c}, {b}, {a}"
        wrong2 = f"{b}, {a}, {c}"
        wrong3 = f"{a}, {c}, {b}"
        return make_mcq(
            f"Sonlarni kichikdan kattaga tartiblang: {b}, {a}, {c}",
            correct, [wrong1, wrong2, wrong3], 2
        )
    
    elif template == 'even_odd':
        n = random.randint(1, 20)
        is_even = n % 2 == 0
        correct = "Juft" if is_even else "Toq"
        return make_mcq(f"{n} soni juft yoki toq?", correct, ["Toq" if is_even else "Juft", "Nol", "Manfiy"], 1)
    
    elif template == 'next_number':
        a = random.randint(1, 17)
        seq = [a, a + 1, a + 2]
        correct = a + 3
        return make_mcq(
            f"Ketma-ketlikni davom ettiring: {seq[0]}, {seq[1]}, {seq[2]}, ?",
            correct, nearby(correct, 3, 1, 2), 1
        )
    
    else:  # before_number
        n = random.randint(2, 20)
        return make_mcq(f"{n} sonidan oldin qaysi son keladi?", n - 1, nearby(n - 1, 3, 1, 2), 1)


def grade_1_open():
    """Generate one open-ended question for grade 1."""
    template = random.choice(['add', 'sub', 'word_add', 'word_sub', 'count_total'])
    
    if template == 'add':
        a, b = random.randint(1, 10), random.randint(1, 10)
        return make_open(f"{a} + {b} ning javobini yozing.", 1)
    elif template == 'sub':
        a = random.randint(5, 20)
        b = random.randint(1, a)
        return make_open(f"{a} - {b} ning javobini yozing.", 1)
    elif template == 'word_add':
        a = random.randint(2, 10)
        b = random.randint(1, 10)
        return make_open(f"Akbarning {a} ta olma bor edi. Unga yana {b} ta olma berishdi. Endi unda nechta olma bor? Javobni yozing.", 2)
    elif template == 'word_sub':
        a = random.randint(8, 18)
        b = random.randint(1, a - 1)
        return make_open(f"Gulnoraning {a} ta konfeti bor edi. U {b} tasini do'stiga berdi. Unda nechta konfet qoldi? Javobni yozing.", 2)
    else:
        a = random.randint(2, 8)
        b = random.randint(2, 8)
        return make_open(f"Birinchi qatorda {a} ta, ikkinchi qatorda {b} ta bola o'tiradi. Jami nechta bola bor? Javobni yozing.", 1)


# ═══════════════════════════════════════════════════════════════════════════════
#  GRADE 2 — 2-sinf: 100 ichida amallar, ko'paytirish jadvali
# ═══════════════════════════════════════════════════════════════════════════════

def grade_2_mcq():
    template = random.choice([
        'add', 'sub', 'mul', 'div', 'compare', 'missing',
        'place_value', 'word_problem', 'sequence', 'double'
    ])
    
    if template == 'add':
        a, b = random.randint(10, 50), random.randint(10, 50)
        c = a + b
        return make_mcq(f"{a} + {b} = ?", c, nearby(c, 3, 1, 5), 1)
    
    elif template == 'sub':
        a = random.randint(30, 99)
        b = random.randint(10, a)
        c = a - b
        return make_mcq(f"{a} - {b} = ?", c, nearby(c, 3, 1, 5), 1)
    
    elif template == 'mul':
        a = random.randint(2, 9)
        b = random.randint(2, 9)
        c = a * b
        return make_mcq(f"{a} × {b} = ?", c, nearby(c, 3, 1, 5), 1)
    
    elif template == 'div':
        b = random.randint(2, 9)
        c = random.randint(2, 9)
        a = b * c
        return make_mcq(f"{a} ÷ {b} = ?", c, nearby(c, 3, 1, 3), 2)
    
    elif template == 'compare':
        a = random.randint(10, 99)
        b = random.randint(10, 99)
        while b == a:
            b = random.randint(10, 99)
        correct = ">" if a > b else "<"
        return make_mcq(f"{a} ☐ {b}. Mosini toping.", correct, ["<" if correct == ">" else ">", "=", "≠"], 1)
    
    elif template == 'missing':
        a = random.randint(10, 50)
        b = random.randint(10, 50)
        c = a + b
        return make_mcq(f"? + {b} = {c}. '?' o'rniga qanday son qo'yiladi?", a, nearby(a, 3, 2, 8), 2)
    
    elif template == 'place_value':
        n = random.randint(10, 99)
        tens = n // 10
        ones = n % 10
        q_type = random.choice(['tens', 'ones'])
        if q_type == 'tens':
            return make_mcq(f"{n} sonidagi o'nliklar soni nechta?", tens, nearby(tens, 3, 1, 3), 1)
        else:
            return make_mcq(f"{n} sonidagi birliklar soni nechta?", ones, nearby(ones, 3, 1, 3), 1)
    
    elif template == 'word_problem':
        a = random.randint(10, 40)
        b = random.randint(10, 40)
        c = a + b
        return make_mcq(
            f"Do'konda {a} ta olma va {b} ta nok bor. Jami nechta meva bor?",
            c, nearby(c, 3, 2, 8), 2
        )
    
    elif template == 'sequence':
        start = random.randint(2, 5)
        step = random.randint(2, 5)
        seq = [start + step * i for i in range(4)]
        correct = start + step * 4
        return make_mcq(
            f"Ketma-ketlikni davom ettiring: {seq[0]}, {seq[1]}, {seq[2]}, {seq[3]}, ?",
            correct, nearby(correct, 3, 1, step), 2
        )
    
    else:  # double
        n = random.randint(5, 45)
        return make_mcq(f"{n} ning ikki baravari nechaga teng?", n * 2, nearby(n * 2, 3, 1, 5), 1)


def grade_2_open():
    template = random.choice(['add', 'sub', 'mul', 'word', 'sequence'])
    
    if template == 'add':
        a, b = random.randint(15, 60), random.randint(15, 40)
        return make_open(f"{a} + {b} ning javobini yozing.", 1)
    elif template == 'sub':
        a = random.randint(40, 99)
        b = random.randint(10, a)
        return make_open(f"{a} - {b} ning javobini yozing.", 1)
    elif template == 'mul':
        a, b = random.randint(2, 9), random.randint(2, 9)
        return make_open(f"{a} × {b} ning javobini yozing.", 1)
    elif template == 'word':
        a = random.randint(15, 45)
        b = random.randint(10, a)
        return make_open(
            f"Kutubxonada {a} ta kitob bor edi. {b} tasi o'quvchilarga berildi. Nechta kitob qoldi? Javobni yozing.", 2
        )
    else:
        start = random.randint(2, 10)
        step = random.randint(2, 5)
        seq = [start + step * i for i in range(3)]
        return make_open(f"Ketma-ketlikdagi keyingi sonni toping: {seq[0]}, {seq[1]}, {seq[2]}, ? Javobni yozing.", 2)


# ═══════════════════════════════════════════════════════════════════════════════
#  GRADE 3 — 3-sinf: Ko'p xonali sonlar, sodda kasrlar
# ═══════════════════════════════════════════════════════════════════════════════

def grade_3_mcq():
    template = random.choice([
        'add3', 'sub3', 'mul2', 'div_rem', 'fraction_read',
        'perimeter', 'compare3', 'round', 'time', 'word3'
    ])
    
    if template == 'add3':
        a = random.randint(100, 500)
        b = random.randint(100, 500)
        c = a + b
        return make_mcq(f"{a} + {b} = ?", c, nearby(c, 3, 5, 20), 1)
    
    elif template == 'sub3':
        a = random.randint(300, 999)
        b = random.randint(100, a)
        c = a - b
        return make_mcq(f"{a} - {b} = ?", c, nearby(c, 3, 5, 20), 1)
    
    elif template == 'mul2':
        a = random.randint(10, 50)
        b = random.randint(2, 9)
        c = a * b
        return make_mcq(f"{a} × {b} = ?", c, nearby(c, 3, 5, 20), 2)
    
    elif template == 'div_rem':
        b = random.randint(2, 9)
        c = random.randint(5, 20)
        r = random.randint(1, b - 1)
        a = b * c + r
        return make_mcq(f"{a} ni {b} ga bo'lganda qoldiq nechaga teng?", r, nearby(r, 3, 1, 3), 2)
    
    elif template == 'fraction_read':
        num = random.randint(1, 5)
        den = random.choice([2, 3, 4, 5, 6, 8])
        while num >= den:
            num = random.randint(1, den - 1)
        correct = f"{num}/{den}"
        wrongs = []
        wrongs.append(f"{den}/{num}")
        wrongs.append(f"{num + 1}/{den}")
        wrongs.append(f"{num}/{den + 1}")
        return make_mcq(
            f"Doirani {den} ga teng bo'lakka bo'ldik. {num} ta bo'lakni belgiladik. Kasrni yozing.",
            correct, wrongs, 2
        )
    
    elif template == 'perimeter':
        a = random.randint(3, 15)
        b = random.randint(3, 15)
        p = 2 * (a + b)
        return make_mcq(
            f"To'g'ri to'rtburchakning tomonlari {a} cm va {b} cm. Perimetri necha cm?",
            p, nearby(p, 3, 2, 8), 2
        )
    
    elif template == 'compare3':
        a = random.randint(100, 999)
        b = random.randint(100, 999)
        while b == a:
            b = random.randint(100, 999)
        mx = max(a, b)
        return make_mcq(f"{a} va {b} sonlaridan qaysi biri katta?", mx, [min(a, b), mx + 1, mx - 1], 1)
    
    elif template == 'round':
        n = random.randint(10, 99) * 10 + random.randint(1, 9)
        rounded = round(n, -1)
        return make_mcq(
            f"{n} sonini eng yaqin o'nlikka yahlitlang.",
            rounded, nearby(rounded, 3, 10, 10), 2
        )
    
    elif template == 'time':
        h = random.randint(1, 12)
        m = random.choice([0, 15, 30, 45])
        total = h * 60 + m
        return make_mcq(
            f"Soat {h}:{m:02d} dan 30 daqiqa o'tgach soat nechani ko'rsatadi?",
            f"{(h + (m + 30) // 60)}:{(m + 30) % 60:02d}",
            [f"{h}:{(m + 15) % 60:02d}", f"{h + 1}:{m:02d}", f"{h}:{(m + 45) % 60:02d}"], 2
        )
    
    else:  # word3
        a = random.randint(100, 400)
        b = random.randint(100, 400)
        c = a + b
        return make_mcq(
            f"Fermer {a} kg bug'doy va {b} kg arpa yig'di. Jami necha kg don yig'ildi?",
            c, nearby(c, 3, 10, 30), 2
        )


def grade_3_open():
    template = random.choice(['mul', 'div', 'perimeter', 'word', 'fraction'])
    
    if template == 'mul':
        a = random.randint(10, 50)
        b = random.randint(2, 9)
        return make_open(f"{a} × {b} ning javobini yozing.", 1)
    elif template == 'div':
        b = random.randint(2, 9)
        c = random.randint(5, 15)
        a = b * c
        return make_open(f"{a} ÷ {b} ning javobini yozing.", 1)
    elif template == 'perimeter':
        a = random.randint(5, 20)
        return make_open(f"Tomoni {a} cm bo'lgan kvadratning perimetrini toping. Javobni cm da yozing.", 2)
    elif template == 'word':
        a = random.randint(100, 500)
        b = random.randint(50, a)
        return make_open(
            f"Bog'da {a} ta daraxt bor edi. {b} tasi olma daraxti. Qolgan daraxtlar nechta? Javobni yozing.", 2
        )
    else:
        num = random.randint(1, 3)
        den = random.choice([4, 5, 6, 8])
        return make_open(f"Chiziqda {den} ta teng bo'lakdan {num} tasini belgilang va kasrni yozing.", 2)


# ═══════════════════════════════════════════════════════════════════════════════
#  GRADE 4 — 4-sinf: Ko'p xonali sonlar, kasrlar, ko'paytirish
# ═══════════════════════════════════════════════════════════════════════════════

def grade_4_mcq():
    template = random.choice([
        'mul_big', 'div_big', 'fraction_add', 'fraction_compare',
        'decimal_intro', 'area', 'order_ops', 'word4', 'roman', 'divisibility'
    ])
    
    if template == 'mul_big':
        a = random.randint(10, 99)
        b = random.randint(10, 99)
        c = a * b
        return make_mcq(f"{a} × {b} = ?", c, nearby(c, 3, 20, 100), 2)
    
    elif template == 'div_big':
        b = random.randint(2, 12)
        c = random.randint(10, 80)
        a = b * c
        return make_mcq(f"{a} ÷ {b} = ?", c, nearby(c, 3, 2, 10), 2)
    
    elif template == 'fraction_add':
        den = random.choice([4, 5, 6, 8, 10])
        a = random.randint(1, den // 2)
        b = random.randint(1, den // 2)
        c = a + b
        return make_mcq(
            f"{a}/{den} + {b}/{den} = ?",
            f"{c}/{den}", [f"{c + 1}/{den}", f"{c}/{den + 1}", f"{a + b + 1}/{den}"], 2
        )
    
    elif template == 'fraction_compare':
        den = random.choice([4, 5, 6, 8])
        a = random.randint(1, den - 2)
        b = a + 1
        correct = f"{b}/{den}"
        return make_mcq(
            f"Qaysi kasr kattaroq: {a}/{den} yoki {b}/{den}?",
            correct, [f"{a}/{den}", f"{a}/{den + 1}", f"{b}/{den + 1}"], 1
        )
    
    elif template == 'decimal_intro':
        whole = random.randint(1, 20)
        dec = random.randint(1, 9)
        n = float(f"{whole}.{dec}")
        return make_mcq(
            f"{whole} butun {dec} o'ndan birni o'nli kasr shaklida yozing.",
            f"{n}", [f"{whole + 1}.{dec}", f"{whole}.{dec + 1 if dec < 9 else 0}", f"{n + 1}"], 1
        )
    
    elif template == 'area':
        a = random.randint(3, 15)
        b = random.randint(3, 15)
        s = a * b
        return make_mcq(
            f"To'g'ri to'rtburchakning tomonlari {a} cm va {b} cm. Yuzi necha cm²?",
            s, nearby(s, 3, 3, 10), 2
        )
    
    elif template == 'order_ops':
        a = random.randint(2, 10)
        b = random.randint(2, 5)
        c = random.randint(1, 10)
        result = a + b * c
        return make_mcq(f"{a} + {b} × {c} = ?", result, [a * b + c, (a + b) * c, result + b], 2)
    
    elif template == 'word4':
        price = random.randint(5, 50)
        count = random.randint(3, 12)
        total = price * count
        return make_mcq(
            f"Bir daftar {price} so'm. {count} ta daftar necha so'm turadi?",
            total, nearby(total, 3, 10, 30), 2
        )
    
    elif template == 'roman':
        mapping = {1: 'I', 4: 'IV', 5: 'V', 9: 'IX', 10: 'X', 14: 'XIV', 15: 'XV', 20: 'XX'}
        n, roman = random.choice(list(mapping.items()))
        return make_mcq(f"Rim raqami {roman} ning qiymati nechaga teng?", n, nearby(n, 3, 1, 5), 1)
    
    else:  # divisibility
        n = random.randint(10, 100)
        d = random.choice([2, 3, 5])
        is_div = n % d == 0
        correct = "Ha" if is_div else "Yo'q"
        return make_mcq(
            f"{n} soni {d} ga bo'linadimi?",
            correct, ["Yo'q" if is_div else "Ha", "Ba'zan", "Faqat qoldiqli"], 1
        )


def grade_4_open():
    template = random.choice(['mul', 'area', 'fraction', 'word', 'order_ops'])
    
    if template == 'mul':
        a = random.randint(12, 50)
        b = random.randint(10, 30)
        return make_open(f"{a} × {b} ning javobini yozing.", 2)
    elif template == 'area':
        a = random.randint(5, 20)
        return make_open(f"Tomoni {a} cm bo'lgan kvadratning yuzini toping. Javobni cm² da yozing.", 1)
    elif template == 'fraction':
        den = random.choice([4, 5, 6, 8])
        a = random.randint(1, den - 2)
        b = random.randint(1, den - a)
        return make_open(f"{a}/{den} + {b}/{den} ni hisoblang. Javobni kasr shaklida yozing.", 2)
    elif template == 'word':
        speed = random.randint(30, 80)
        time = random.randint(2, 5)
        return make_open(f"Mashina soatiga {speed} km tezlikda {time} soat yurdi. Qancha masofani bosib o'tdi? Javobni km da yozing.", 2)
    else:
        a = random.randint(5, 15)
        b = random.randint(2, 5)
        c = random.randint(3, 8)
        return make_open(f"{a} + {b} × {c} ni hisoblang. Amallar tartibiga rioya qiling. Javobni yozing.", 2)


# ═══════════════════════════════════════════════════════════════════════════════
#  GRADE 5 — 5-sinf: Kasrlar, foiz, tenglamalar
# ═══════════════════════════════════════════════════════════════════════════════

def grade_5_mcq():
    template = random.choice([
        'fraction_ops', 'decimal_ops', 'percent', 'equation',
        'area_triangle', 'volume', 'lcm_gcf', 'mixed_number',
        'proportion', 'negative'
    ])
    
    if template == 'fraction_ops':
        d1 = random.choice([3, 4, 5, 6, 8])
        d2 = d1
        n1 = random.randint(1, d1 - 1)
        n2 = random.randint(1, d2 - 1)
        op = random.choice(['+', '-'])
        if op == '+':
            result_n = n1 + n2
        else:
            n1, n2 = max(n1, n2), min(n1, n2)
            result_n = n1 - n2
        return make_mcq(
            f"{n1}/{d1} {op} {n2}/{d2} = ?",
            f"{result_n}/{d1}", [f"{result_n + 1}/{d1}", f"{result_n}/{d1 + 1}", f"{result_n - 1 if result_n > 0 else result_n + 2}/{d1}"], 2
        )
    
    elif template == 'decimal_ops':
        a = round(random.uniform(1, 20), 1)
        b = round(random.uniform(1, 10), 1)
        op = random.choice(['+', '-', '×'])
        if op == '+':
            c = round(a + b, 1)
        elif op == '-':
            a, b = max(a, b), min(a, b)
            c = round(a - b, 1)
        else:
            c = round(a * b, 1)
        return make_mcq(f"{a} {op} {b} = ?", c, nearby_float(c, 3, 0.5, 3.0, 1), 2)
    
    elif template == 'percent':
        total = random.choice([100, 200, 50, 150, 300, 400, 500])
        pct = random.choice([10, 20, 25, 30, 50, 75])
        result = total * pct // 100
        return make_mcq(f"{total} ning {pct}% ini toping.", result, nearby(result, 3, 5, 20), 2)
    
    elif template == 'equation':
        x = random.randint(2, 20)
        a = random.randint(2, 8)
        b = a * x
        return make_mcq(f"{a}x = {b} tenglamaning yechimini toping.", x, nearby(x, 3, 1, 5), 2)
    
    elif template == 'area_triangle':
        a = random.randint(4, 20)
        h = random.randint(4, 20)
        s = a * h / 2
        if s == int(s):
            s = int(s)
        return make_mcq(
            f"Uchburchakning asosi {a} cm, balandligi {h} cm. Yuzini toping.",
            f"{s} cm²", [f"{a * h} cm²", f"{int(s) + 5} cm²", f"{int(s) - 3} cm²"], 2
        )
    
    elif template == 'volume':
        a = random.randint(2, 8)
        b = random.randint(2, 8)
        c = random.randint(2, 8)
        v = a * b * c
        return make_mcq(
            f"To'g'ri burchakli parallelepiped o'lchamlari: {a} cm, {b} cm, {c} cm. Hajmi?",
            f"{v} cm³", [f"{a * b + c} cm³", f"{v + a} cm³", f"{2 * (a * b + b * c + a * c)} cm³"], 2
        )
    
    elif template == 'lcm_gcf':
        a = random.choice([6, 8, 10, 12, 15, 18, 20, 24])
        b = random.choice([4, 6, 8, 9, 10, 12, 15, 16])
        g = gcd(a, b)
        q_type = random.choice(['gcd', 'lcm'])
        if q_type == 'gcd':
            return make_mcq(f"{a} va {b} ning EKUB ini toping.", g, nearby(g, 3, 1, 3), 2)
        else:
            l = lcm(a, b)
            return make_mcq(f"{a} va {b} ning EKUK ini toping.", l, nearby(l, 3, 5, 15), 3)
    
    elif template == 'mixed_number':
        whole = random.randint(1, 5)
        num = random.randint(1, 4)
        den = random.choice([3, 4, 5, 6])
        while num >= den:
            num = random.randint(1, den - 1)
        improper_num = whole * den + num
        return make_mcq(
            f"{whole} butun {num}/{den} aralash sonni noto'g'ri kasrga aylantiring.",
            f"{improper_num}/{den}", [f"{whole * num}/{den}", f"{improper_num + 1}/{den}", f"{improper_num}/{den + 1}"], 2
        )
    
    elif template == 'proportion':
        a = random.randint(2, 10)
        b = random.randint(2, 10)
        k = random.randint(2, 5)
        c = a * k
        d = b * k
        return make_mcq(
            f"{a} : {b} = {c} : ? Noma'lumni toping.",
            d, nearby(d, 3, 1, 5), 2
        )
    
    else:  # negative
        a = random.randint(1, 15)
        b = random.randint(1, 15)
        result = -a + b
        return make_mcq(f"(-{a}) + {b} = ?", result, nearby(result, 3, 1, 5), 2)


def grade_5_open():
    template = random.choice(['equation', 'percent', 'fraction', 'area', 'word'])
    
    if template == 'equation':
        x = random.randint(2, 15)
        a = random.randint(2, 7)
        b = random.randint(1, 20)
        c = a * x + b
        return make_open(f"{a}x + {b} = {c} tenglamani yeching. x ni toping.", 2)
    elif template == 'percent':
        total = random.choice([200, 300, 500, 800])
        pct = random.choice([15, 20, 25, 40])
        return make_open(f"{total} ning {pct}% ini hisoblang. Javobni yozing.", 2)
    elif template == 'fraction':
        d = random.choice([6, 8, 10, 12])
        n1 = random.randint(1, d // 2)
        n2 = random.randint(1, d // 2)
        return make_open(f"{n1}/{d} + {n2}/{d} ni hisoblang va soddalashtirilgan shaklda yozing.", 2)
    elif template == 'area':
        a = random.randint(5, 15)
        h = random.randint(4, 12)
        return make_open(f"Uchburchakning asosi {a} cm, balandligi {h} cm. Yuzini hisoblang.", 2)
    else:
        speed = random.randint(40, 100)
        time_h = random.randint(2, 6)
        return make_open(f"Poyezd soatiga {speed} km tezlikda {time_h} soat yurdi. Bosib o'tgan masofani yozing.", 1)


# ═══════════════════════════════════════════════════════════════════════════════
#  GRADE 6 — 6-sinf: EKUB, EKUK, ratsional sonlar, tenglamalar
# ═══════════════════════════════════════════════════════════════════════════════

def grade_6_mcq():
    template = random.choice([
        'rational_ops', 'equation_linear', 'proportion', 'coordinate',
        'percent_word', 'gcf_lcm', 'negative_ops', 'absolute',
        'fraction_mul', 'geometry'
    ])
    
    if template == 'rational_ops':
        a = random.randint(-10, 10)
        b = random.randint(-10, 10)
        while b == 0:
            b = random.randint(-10, 10)
        op = random.choice(['+', '-', '×'])
        if op == '+': c = a + b
        elif op == '-': c = a - b
        else: c = a * b
        return make_mcq(f"({a}) {op} ({b}) = ?", c, nearby(c, 3, 1, 5), 2)
    
    elif template == 'equation_linear':
        x = random.randint(-8, 8)
        while x == 0:
            x = random.randint(-8, 8)
        a = random.randint(2, 6)
        b = random.randint(1, 15)
        c = a * x + b
        return make_mcq(f"{a}x + {b} = {c}. x = ?", x, nearby(x, 3, 1, 4), 2)
    
    elif template == 'proportion':
        a = random.randint(3, 15)
        b = random.randint(2, 10)
        c = random.randint(3, 15)
        d = a * c // b if a * c % b == 0 else round(a * c / b, 1)
        # Ensure clean answer
        b2 = random.randint(2, 8)
        a2 = b2 * random.randint(2, 5)
        c2 = random.randint(2, 8)
        d2 = a2 * c2 // b2
        return make_mcq(f"{a2}/{b2} = {c2}/x. x ni toping.", d2, nearby(d2, 3, 1, 5), 2)
    
    elif template == 'coordinate':
        x = random.randint(-5, 5)
        y = random.randint(-5, 5)
        return make_mcq(
            f"Koordinata tekisligida A({x}; {y}) nuqta qaysi chorakda joylashgan?",
            "I" if x > 0 and y > 0 else ("II" if x < 0 and y > 0 else ("III" if x < 0 and y < 0 else "IV")),
            ["I", "II", "III", "IV"][:3] if x != 0 and y != 0 else ["I", "II", "O'qda"], 2
        )
    
    elif template == 'percent_word':
        total = random.choice([120, 150, 200, 250, 300, 400, 500])
        pct = random.choice([10, 15, 20, 25, 30, 40, 50])
        result = total * pct // 100
        return make_mcq(
            f"Sinfda {total} ta o'quvchi bor. Ularning {pct}% i a'lochi. Nechta a'lochi bor?",
            result, nearby(result, 3, 3, 10), 2
        )
    
    elif template == 'gcf_lcm':
        nums = [(12, 18), (15, 25), (24, 36), (20, 30), (14, 21), (18, 27), (16, 24), (30, 45)]
        a, b = random.choice(nums)
        q_type = random.choice(['gcd', 'lcm'])
        if q_type == 'gcd':
            g = gcd(a, b)
            return make_mcq(f"EKUB({a}, {b}) = ?", g, nearby(g, 3, 1, 4), 2)
        else:
            l = lcm(a, b)
            return make_mcq(f"EKUK({a}, {b}) = ?", l, nearby(l, 3, 5, 20), 3)
    
    elif template == 'negative_ops':
        a = random.randint(1, 15)
        b = random.randint(1, 15)
        result = (-a) * (-b)
        return make_mcq(f"(-{a}) × (-{b}) = ?", result, [-(a * b), a * b + a, -(a + b)], 1)
    
    elif template == 'absolute':
        n = random.randint(-20, 20)
        while n == 0:
            n = random.randint(-20, 20)
        return make_mcq(f"|{n}| = ?", abs(n), [n, -abs(n), abs(n) + 1], 1)
    
    elif template == 'fraction_mul':
        n1 = random.randint(1, 5)
        d1 = random.choice([3, 4, 5, 6, 7])
        n2 = random.randint(1, 5)
        d2 = random.choice([3, 4, 5, 6, 7])
        rn = n1 * n2
        rd = d1 * d2
        g = gcd(rn, rd)
        rn //= g
        rd //= g
        return make_mcq(
            f"{n1}/{d1} × {n2}/{d2} = ?",
            f"{rn}/{rd}", [f"{n1 * n2}/{d1 + d2}", f"{n1 + n2}/{d1 * d2}", f"{rn + 1}/{rd}"], 2
        )
    
    else:  # geometry
        a = random.randint(3, 12)
        h = random.randint(3, 12)
        area = a * h
        return make_mcq(
            f"Parallelogrammning asosi {a} cm, balandligi {h} cm. Yuzi necha cm²?",
            area, nearby(area, 3, 3, 10), 2
        )


def grade_6_open():
    template = random.choice(['equation', 'proportion', 'gcf', 'rational', 'word'])
    
    if template == 'equation':
        x = random.randint(-10, 10)
        while x == 0:
            x = random.randint(-10, 10)
        a = random.randint(2, 7)
        b = random.randint(1, 20)
        c = a * x + b
        return make_open(f"{a}x + {b} = {c} tenglamani yeching.", 2)
    elif template == 'proportion':
        a = random.randint(3, 12)
        b = random.randint(2, 8)
        c = random.randint(3, 12)
        return make_open(f"{a}:{b} = x:{c} proportsiyadan x ni toping.", 2)
    elif template == 'gcf':
        a = random.choice([12, 18, 24, 30, 36, 48, 60])
        b = random.choice([8, 15, 20, 25, 36, 42, 45])
        return make_open(f"{a} va {b} ning EKUBini toping.", 2)
    elif template == 'rational':
        a = random.randint(-10, -1)
        b = random.randint(1, 15)
        return make_open(f"({a}) + {b} ni hisoblang. Javobni yozing.", 1)
    else:
        total = random.choice([200, 300, 400, 500, 600])
        pct = random.choice([15, 20, 25, 30, 35, 40])
        return make_open(f"{total} ning {pct} foizini toping.", 2)


# ═══════════════════════════════════════════════════════════════════════════════
#  GRADE 7 — 7-sinf: Algebraik ifodalar, funksiya, tenglamalar
# ═══════════════════════════════════════════════════════════════════════════════

def grade_7_mcq():
    template = random.choice([
        'monomial', 'polynomial_add', 'factoring', 'linear_func',
        'system', 'power', 'inequality', 'identity', 'graph', 'word7'
    ])
    
    if template == 'monomial':
        a = random.randint(2, 8)
        b = random.randint(2, 8)
        result = a * b
        n = random.randint(2, 4)
        m = random.randint(2, 4)
        return make_mcq(
            f"{a}x^{n} · {b}x^{m} = ?",
            f"{result}x^{n + m}", [f"{result}x^{n * m}", f"{a + b}x^{n + m}", f"{result}x^{n}"], 2
        )
    
    elif template == 'polynomial_add':
        a = random.randint(2, 8)
        b = random.randint(1, 6)
        c = random.randint(1, 6)
        d = random.randint(1, 6)
        result_x = a + c
        result_c = b + d
        return make_mcq(
            f"({a}x + {b}) + ({c}x + {d}) = ?",
            f"{result_x}x + {result_c}",
            [f"{a * c}x + {b + d}", f"{result_x}x + {b * d}", f"{result_x + 1}x + {result_c}"], 2
        )
    
    elif template == 'factoring':
        a = random.randint(2, 8)
        b = random.randint(2, 8)
        # a²-b² = (a-b)(a+b)
        return make_mcq(
            f"{a**2} - {b**2} ni ko'paytuvchilarga ajrating.",
            f"({a} - {b})({a} + {b})",
            [f"({a} - {b})²", f"({a} + {b})²", f"{a}({a} - {b**2 // a if a != 0 else 1})"], 2
        )
    
    elif template == 'linear_func':
        k = random.randint(-5, 5)
        while k == 0:
            k = random.randint(-5, 5)
        b = random.randint(-8, 8)
        x = random.randint(-3, 5)
        y = k * x + b
        return make_mcq(
            f"y = {k}x {'+' if b >= 0 else '-'} {abs(b)} funksiyada x = {x} bo'lganda y = ?",
            y, nearby(y, 3, 1, 5), 2
        )
    
    elif template == 'system':
        x = random.randint(1, 6)
        y = random.randint(1, 6)
        a1, b1 = random.randint(1, 4), random.randint(1, 4)
        c1 = a1 * x + b1 * y
        a2, b2 = random.randint(1, 4), random.randint(1, 4)
        c2 = a2 * x - b2 * y
        return make_mcq(
            f"{a1}x + {b1}y = {c1} va {a2}x - {b2}y = {c2} tenglamalar sistemasida x = ?",
            x, nearby(x, 3, 1, 3), 3
        )
    
    elif template == 'power':
        base = random.randint(2, 5)
        exp = random.randint(2, 5)
        result = base ** exp
        return make_mcq(f"{base}^{exp} = ?", result, nearby(result, 3, 5, 20), 1)
    
    elif template == 'inequality':
        a = random.randint(2, 6)
        b = random.randint(1, 15)
        # ax > b => x > b/a
        if b % a == 0:
            ans = b // a
            return make_mcq(
                f"{a}x > {b} tengsizlikning yechimini toping.",
                f"x > {ans}", [f"x < {ans}", f"x > {ans + 1}", f"x ≥ {ans + 1}"], 2
            )
        else:
            ans = round(b / a, 1)
            return make_mcq(
                f"{a}x > {b} tengsizlikning yechimini toping.",
                f"x > {ans}", [f"x < {ans}", f"x > {round(ans + 1, 1)}", f"x ≥ {round(ans + 0.5, 1)}"], 2
            )
    
    elif template == 'identity':
        a = random.randint(2, 8)
        b = random.randint(1, 6)
        # (a+b)² = a² + 2ab + b²
        result = a ** 2 + 2 * a * b + b ** 2
        return make_mcq(
            f"({a} + {b})² = ?",
            result, [a ** 2 + b ** 2, a ** 2 + a * b + b ** 2, result + b], 2
        )
    
    elif template == 'graph':
        k = random.choice([-3, -2, -1, 1, 2, 3, 4])
        desc = "o'suvchi" if k > 0 else "kamayuvchi"
        return make_mcq(
            f"y = {k}x funksiya grafigi qanday?",
            f"To'g'ri chiziq, {desc}",
            [f"Parabola, {desc}", f"To'g'ri chiziq, {'kamayuvchi' if k > 0 else 'o`suvchi'}",
             f"Giperbola"], 2
        )
    
    else:  # word7
        rate = random.randint(3, 12)
        hours = random.randint(2, 8)
        total = rate * hours
        return make_mcq(
            f"Ishchi soatiga {rate} ta detal yasaydi. {hours} soatda nechta detal yasaydi?",
            total, nearby(total, 3, 3, 10), 1
        )


def grade_7_open():
    template = random.choice(['simplify', 'equation', 'system', 'power', 'factoring'])
    
    if template == 'simplify':
        a = random.randint(2, 8)
        b = random.randint(1, 6)
        c = random.randint(1, 6)
        return make_open(f"({a}x + {b}) - ({c}x - {random.randint(1, 5)}) ifodani soddalashtiring.", 2)
    elif template == 'equation':
        x = random.randint(-5, 10)
        a = random.randint(2, 6)
        b = random.randint(1, 20)
        c = random.randint(1, 10)
        rhs = a * x + b - c
        return make_open(f"{a}x + {b} = {rhs + c} tenglamani yeching. x = ?", 2)
    elif template == 'system':
        return make_open(
            f"x + y = {random.randint(5, 15)} va x - y = {random.randint(1, 7)} tenglamalar sistemasini yeching.",
            3
        )
    elif template == 'power':
        a = random.randint(2, 5)
        n = random.randint(2, 4)
        m = random.randint(2, 4)
        return make_open(f"{a}^{n} × {a}^{m} ni hisoblang.", 2)
    else:
        a = random.randint(2, 10)
        return make_open(f"{a}x² - {a * random.randint(2, 8)} x ni umumiy ko'paytuvchiga chiqaring.", 2)


# ═══════════════════════════════════════════════════════════════════════════════
#  GRADE 8 — 8-sinf: Kvadrat ildiz, tengsizlik, trigonometrik nisbatlar
# ═══════════════════════════════════════════════════════════════════════════════

def grade_8_mcq():
    template = random.choice([
        'sqrt', 'quadratic', 'inequality_system', 'pythagorean',
        'trig_basic', 'quadratic_formula', 'absolute_value',
        'rational_expression', 'circle', 'discriminant'
    ])
    
    if template == 'sqrt':
        perfect = random.choice([4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144, 169])
        root = int(math.sqrt(perfect))
        return make_mcq(f"√{perfect} = ?", root, nearby(root, 3, 1, 3), 1)
    
    elif template == 'quadratic':
        x1 = random.randint(-5, 5)
        x2 = random.randint(-5, 5)
        while x2 == x1:
            x2 = random.randint(-5, 5)
        # (x - x1)(x - x2) = x² - (x1+x2)x + x1*x2
        b = -(x1 + x2)
        c = x1 * x2
        sign_b = '+' if b >= 0 else '-'
        sign_c = '+' if c >= 0 else '-'
        return make_mcq(
            f"x² {sign_b} {abs(b)}x {sign_c} {abs(c)} = 0 tenglamaning ildizlari?",
            f"x₁ = {min(x1,x2)}, x₂ = {max(x1,x2)}",
            [f"x₁ = {x1 + 1}, x₂ = {x2 + 1}", f"x₁ = {-x1}, x₂ = {-x2}", f"x₁ = {x1 * 2}, x₂ = {x2}"], 2
        )
    
    elif template == 'inequality_system':
        a = random.randint(1, 8)
        b = random.randint(a + 2, 15)
        return make_mcq(
            f"x > {a} va x < {b} tengsizliklar sistemasining yechimi?",
            f"{a} < x < {b}", [f"x > {b}", f"x < {a}", f"{a} ≤ x ≤ {b}"], 2
        )
    
    elif template == 'pythagorean':
        triples = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (6, 8, 10), (9, 12, 15), (7, 24, 25)]
        a, b, c = random.choice(triples)
        return make_mcq(
            f"To'g'ri burchakli uchburchakning katetlari {a} va {b}. Gipotenuzani toping.",
            c, nearby(c, 3, 1, 3), 2
        )
    
    elif template == 'trig_basic':
        angle = random.choice([30, 45, 60])
        func = random.choice(['sin', 'cos', 'tan'])
        values = {
            (30, 'sin'): '1/2', (30, 'cos'): '√3/2', (30, 'tan'): '√3/3',
            (45, 'sin'): '√2/2', (45, 'cos'): '√2/2', (45, 'tan'): '1',
            (60, 'sin'): '√3/2', (60, 'cos'): '1/2', (60, 'tan'): '√3',
        }
        correct = values[(angle, func)]
        all_vals = list(set(values.values()) - {correct})
        random.shuffle(all_vals)
        return make_mcq(f"{func}({angle}°) = ?", correct, all_vals[:3], 2)
    
    elif template == 'quadratic_formula':
        a = 1
        b_coeff = random.choice([-6, -4, -2, 2, 4, 6, -8, 8])
        # discriminant = b² - 4ac, ensure D >= 0
        x1 = random.randint(-5, 5)
        x2 = random.randint(-5, 5)
        b_coeff = -(x1 + x2)
        c_coeff = x1 * x2
        d = b_coeff ** 2 - 4 * a * c_coeff
        return make_mcq(
            f"x² {'+' if b_coeff >= 0 else '-'} {abs(b_coeff)}x {'+' if c_coeff >= 0 else '-'} {abs(c_coeff)} = 0 tenglamaning diskriminantini toping.",
            d, nearby(d, 3, 2, 10), 2
        )
    
    elif template == 'absolute_value':
        a = random.randint(1, 10)
        return make_mcq(
            f"|x| = {a} tenglamaning nechta yechimi bor?",
            2, [1, 0, 3], 1
        )
    
    elif template == 'rational_expression':
        a = random.randint(2, 8)
        b = random.randint(1, 6)
        # (a²-b²)/(a-b) = a+b
        return make_mcq(
            f"({a}² - {b}²) / ({a} - {b}) = ?",
            a + b, [a - b, a * b, a ** 2 - b], 2
        )
    
    elif template == 'circle':
        r = random.randint(2, 10)
        circumference = round(2 * 3.14 * r, 2)
        return make_mcq(
            f"Radiusi {r} cm bo'lgan aylananing uzunligini toping (π ≈ 3.14).",
            f"{circumference} cm",
            [f"{round(3.14 * r * r, 2)} cm", f"{round(3.14 * r, 2)} cm", f"{round(circumference + r, 2)} cm"], 2
        )
    
    else:  # discriminant
        a = 1
        b = random.randint(-8, 8)
        while b == 0:
            b = random.randint(-8, 8)
        c = random.randint(-10, 10)
        d = b * b - 4 * a * c
        has_roots = "2 ta" if d > 0 else ("1 ta" if d == 0 else "yechimi yo'q")
        return make_mcq(
            f"x² {'+' if b >= 0 else '-'} {abs(b)}x {'+' if c >= 0 else '-'} {abs(c)} = 0 tenglamaning nechta haqiqiy ildizi bor?",
            has_roots, ["2 ta", "1 ta", "yechimi yo'q", "cheksiz"][:3], 2
        )


def grade_8_open():
    template = random.choice(['quadratic', 'sqrt', 'pythagorean', 'trig', 'circle'])
    
    if template == 'quadratic':
        x1 = random.randint(1, 8)
        x2 = random.randint(1, 8)
        b = -(x1 + x2)
        c = x1 * x2
        return make_open(f"x² {'+' if b >= 0 else '-'} {abs(b)}x {'+' if c >= 0 else '-'} {abs(c)} = 0 tenglamani yeching.", 2)
    elif template == 'sqrt':
        n = random.choice([4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144])
        return make_open(f"√{n} ni hisoblang.", 1)
    elif template == 'pythagorean':
        a, b = random.choice([(3, 4), (5, 12), (6, 8), (8, 15)])
        return make_open(f"To'g'ri burchakli uchburchakning katetlari {a} va {b}. Gipotenuzani toping.", 2)
    elif template == 'trig':
        angle = random.choice([30, 45, 60])
        func = random.choice(['sin', 'cos', 'tg'])
        return make_open(f"{func} {angle}° ning qiymatini yozing.", 2)
    else:
        r = random.randint(3, 12)
        return make_open(f"Radiusi {r} cm bo'lgan doiraning yuzini hisoblang (π ≈ 3.14).", 2)


# ═══════════════════════════════════════════════════════════════════════════════
#  GRADE 9 — 9-sinf: Funksiya, progressiya, trigonometriya
# ═══════════════════════════════════════════════════════════════════════════════

def grade_9_mcq():
    template = random.choice([
        'arithmetic_prog', 'geometric_prog', 'quadratic_func',
        'trig_identity', 'statistics', 'system_nonlinear',
        'inequality_quadratic', 'sequence_sum', 'function_domain', 'probability'
    ])
    
    if template == 'arithmetic_prog':
        a1 = random.randint(1, 10)
        d = random.randint(1, 5)
        n = random.randint(5, 15)
        an = a1 + (n - 1) * d
        return make_mcq(
            f"Arifmetik progressiyada a₁ = {a1}, d = {d}. a_{n} ni toping.",
            an, nearby(an, 3, 2, 8), 2
        )
    
    elif template == 'geometric_prog':
        b1 = random.randint(1, 5)
        q = random.randint(2, 4)
        n = random.randint(3, 6)
        bn = b1 * q ** (n - 1)
        return make_mcq(
            f"Geometrik progressiyada b₁ = {b1}, q = {q}. b_{n} ni toping.",
            bn, nearby(bn, 3, 10, 50), 2
        )
    
    elif template == 'quadratic_func':
        a = random.choice([-2, -1, 1, 2, 3])
        h = random.randint(-3, 3)
        k = random.randint(-5, 5)
        direction = "yuqoriga" if a > 0 else "pastga"
        return make_mcq(
            f"y = {a}(x - {h})² + {k} funksiya grafigining uchi qaysi nuqtada?",
            f"({h}; {k})", [f"({-h}; {k})", f"({h}; {-k})", f"({k}; {h})"], 2
        )
    
    elif template == 'trig_identity':
        angle = random.choice([0, 30, 45, 60, 90, 120, 180])
        sin_val = round(math.sin(math.radians(angle)), 2)
        cos_val = round(math.cos(math.radians(angle)), 2)
        result = round(sin_val ** 2 + cos_val ** 2, 2)
        return make_mcq(
            f"sin²({angle}°) + cos²({angle}°) = ?",
            1, [0, 2, round(sin_val + cos_val, 2)], 1
        )
    
    elif template == 'statistics':
        data = sorted(random.sample(range(1, 20), 5))
        median = data[2]
        return make_mcq(
            f"Ma'lumotlar: {', '.join(map(str, data))}. Medianani toping.",
            median, nearby(median, 3, 1, 3), 2
        )
    
    elif template == 'system_nonlinear':
        x = random.randint(1, 5)
        y = random.randint(1, 5)
        s = x + y
        p = x * y
        return make_mcq(
            f"x + y = {s} va xy = {p}. x² + y² = ?",
            s ** 2 - 2 * p, [s ** 2 + 2 * p, s ** 2 - p, s * p], 3
        )
    
    elif template == 'inequality_quadratic':
        a = random.randint(1, 5)
        b = random.randint(a + 1, 10)
        return make_mcq(
            f"(x - {a})(x - {b}) < 0 tengsizlikning yechimini toping.",
            f"{a} < x < {b}", [f"x < {a} yoki x > {b}", f"x > {b}", f"x < {a}"], 2
        )
    
    elif template == 'sequence_sum':
        a1 = random.randint(1, 5)
        d = random.randint(1, 4)
        n = random.randint(5, 10)
        sn = n * (2 * a1 + (n - 1) * d) // 2
        return make_mcq(
            f"Arifmetik progressiyada a₁ = {a1}, d = {d}. S_{n} ni toping.",
            sn, nearby(sn, 3, 10, 30), 3
        )
    
    elif template == 'function_domain':
        a = random.randint(1, 10)
        return make_mcq(
            f"y = √(x - {a}) funksiyaning aniqlanish sohasi?",
            f"x ≥ {a}", [f"x > {a}", f"x ≤ {a}", f"x ≠ {a}"], 2
        )
    
    else:  # probability
        total = random.choice([6, 10, 12, 20, 36, 50])
        favorable = random.randint(1, total - 1)
        g = gcd(favorable, total)
        num, den = favorable // g, total // g
        return make_mcq(
            f"Qutida {total} ta shar bor, {favorable} tasi qizil. Tasodifan olingan sharning qizil bo'lish ehtimoli?",
            f"{num}/{den}", [f"{den}/{num}" if num != den else f"1/{den + 1}", f"{favorable + 1}/{total}", f"{total - favorable}/{total}"], 2
        )


def grade_9_open():
    template = random.choice(['progression', 'quadratic_func', 'system', 'statistics', 'trig'])
    
    if template == 'progression':
        a1 = random.randint(2, 8)
        d = random.randint(2, 5)
        n = random.randint(8, 15)
        return make_open(f"Arifmetik progressiyada a₁ = {a1}, d = {d}. a_{n} ni toping.", 2)
    elif template == 'quadratic_func':
        a = random.choice([1, 2, -1, -2])
        b = random.randint(-6, 6)
        c = random.randint(-5, 5)
        return make_open(f"y = {a}x² {'+' if b >= 0 else '-'} {abs(b)}x {'+' if c >= 0 else '-'} {abs(c)} funksiyaning uchini toping.", 3)
    elif template == 'system':
        return make_open(f"x + y = {random.randint(5, 12)}, x - y = {random.randint(1, 5)} sistemani yeching.", 2)
    elif template == 'statistics':
        data = random.sample(range(2, 20), 7)
        return make_open(f"Ma'lumotlar: {', '.join(map(str, data))}. O'rta arifmetik qiymatini toping.", 2)
    else:
        return make_open(f"sin²α + cos²α = 1 asosiy trigonometrik ayniyatdan foydalanib, agar sinα = {random.choice(['3/5', '4/5', '5/13', '12/13'])} bo'lsa, cosα ni toping.", 3)


# ═══════════════════════════════════════════════════════════════════════════════
#  GRADE 10 — 10-sinf: Vektor, logarifm, trigonometrik funktsiyalar
# ═══════════════════════════════════════════════════════════════════════════════

def grade_10_mcq():
    template = random.choice([
        'logarithm', 'vector', 'trig_func', 'combinatorics',
        'series', 'log_properties', 'radian', 'trig_equation',
        'vector_ops', 'exponential'
    ])
    
    if template == 'logarithm':
        base = random.choice([2, 3, 5, 10])
        exp = random.randint(1, 5)
        n = base ** exp
        return make_mcq(f"log_{base}({n}) = ?", exp, nearby(exp, 3, 1, 2), 2)
    
    elif template == 'vector':
        x1, y1 = random.randint(-5, 5), random.randint(-5, 5)
        x2, y2 = random.randint(-5, 5), random.randint(-5, 5)
        rx, ry = x1 + x2, y1 + y2
        return make_mcq(
            f"a⃗({x1}; {y1}) + b⃗({x2}; {y2}) = ?",
            f"({rx}; {ry})", [f"({x1 * x2}; {y1 * y2})", f"({rx + 1}; {ry - 1})", f"({x1 - x2}; {y1 - y2})"], 2
        )
    
    elif template == 'trig_func':
        x = random.choice([0, 30, 45, 60, 90, 120, 135, 150, 180, 270, 360])
        func = random.choice(['sin', 'cos'])
        val = round(math.sin(math.radians(x)) if func == 'sin' else math.cos(math.radians(x)), 2)
        
        known = {
            ('sin', 0): '0', ('sin', 30): '0.5', ('sin', 45): '√2/2', ('sin', 60): '√3/2',
            ('sin', 90): '1', ('sin', 180): '0', ('sin', 270): '-1', ('sin', 360): '0',
            ('cos', 0): '1', ('cos', 30): '√3/2', ('cos', 45): '√2/2', ('cos', 60): '0.5',
            ('cos', 90): '0', ('cos', 180): '-1', ('cos', 270): '0', ('cos', 360): '1',
        }
        
        if (func, x) in known:
            correct = known[(func, x)]
            all_vals = list(set(known.values()) - {correct})
            random.shuffle(all_vals)
            return make_mcq(f"{func}({x}°) = ?", correct, all_vals[:3], 2)
        else:
            return make_mcq(f"{func}({x}°) ning qiymati taxminan?", val, nearby_float(val, 3, 0.1, 0.5, 2), 2)
    
    elif template == 'combinatorics':
        n = random.randint(4, 8)
        r = random.randint(2, min(4, n))
        # C(n, r) = n! / (r! * (n-r)!)
        c = math.comb(n, r)
        return make_mcq(f"C({n}, {r}) = ?", c, nearby(c, 3, 2, 10), 2)
    
    elif template == 'series':
        a1 = random.randint(1, 5)
        r = random.choice([Fraction(1, 2), Fraction(1, 3)])
        # S = a1 / (1 - r)
        s = a1 / (1 - float(r))
        return make_mcq(
            f"Cheksiz kamayuvchi geometrik progressiyada b₁ = {a1}, q = {r}. Yig'indisini toping.",
            f"{round(s, 1) if s != int(s) else int(s)}",
            [f"{round(s + 1, 1)}", f"{round(s * 2, 1)}", f"{round(s - 1, 1)}"], 3
        )
    
    elif template == 'log_properties':
        a = random.randint(2, 8)
        b = random.randint(2, 8)
        # log(a*b) = log(a) + log(b)
        return make_mcq(
            f"lg({a} × {b}) = ?",
            f"lg{a} + lg{b}", [f"lg{a} × lg{b}", f"lg{a} - lg{b}", f"lg({a} + {b})"], 1
        )
    
    elif template == 'radian':
        degrees = random.choice([30, 45, 60, 90, 120, 150, 180, 270, 360])
        radian_map = {30: 'π/6', 45: 'π/4', 60: 'π/3', 90: 'π/2', 120: '2π/3', 150: '5π/6', 180: 'π', 270: '3π/2', 360: '2π'}
        correct = radian_map[degrees]
        all_r = list(set(radian_map.values()) - {correct})
        random.shuffle(all_r)
        return make_mcq(f"{degrees}° ni radianga aylantiring.", correct, all_r[:3], 2)
    
    elif template == 'trig_equation':
        # sin(x) = 0 => x = πn
        val = random.choice([0, 1, -1])
        if val == 0:
            return make_mcq("sin(x) = 0 tenglamaning umumiy yechimi?", "x = πn", ["x = π/2 + πn", "x = 2πn", "x = π/4 + πn"], 2)
        elif val == 1:
            return make_mcq("sin(x) = 1 tenglamaning umumiy yechimi?", "x = π/2 + 2πn", ["x = πn", "x = 2πn", "x = π + 2πn"], 3)
        else:
            return make_mcq("cos(x) = -1 tenglamaning umumiy yechimi?", "x = π + 2πn", ["x = πn", "x = 2πn", "x = π/2 + 2πn"], 3)
    
    elif template == 'vector_ops':
        x, y = random.randint(1, 8), random.randint(1, 8)
        length_sq = x ** 2 + y ** 2
        length = round(math.sqrt(length_sq), 2)
        return make_mcq(
            f"a⃗({x}; {y}) vektorning uzunligi?",
            f"√{length_sq}" if length != int(length) else str(int(length)),
            [f"√{length_sq + x}", f"{x + y}", f"√{x * y}"], 2
        )
    
    else:  # exponential
        base = random.choice([2, 3, 5])
        x = random.randint(1, 5)
        result = base ** x
        return make_mcq(f"{base}^x = {result}. x = ?", x, nearby(x, 3, 1, 2), 2)


def grade_10_open():
    template = random.choice(['log', 'vector', 'trig', 'combinatorics', 'series'])
    
    if template == 'log':
        base = random.choice([2, 3, 5, 10])
        n = base ** random.randint(2, 4)
        return make_open(f"log_{base}({n}) ni hisoblang.", 2)
    elif template == 'vector':
        x1, y1 = random.randint(-5, 5), random.randint(-5, 5)
        x2, y2 = random.randint(-5, 5), random.randint(-5, 5)
        return make_open(f"a⃗({x1}; {y1}) va b⃗({x2}; {y2}) vektorlarning skalyar ko'paytmasini toping.", 2)
    elif template == 'trig':
        angle = random.choice([30, 45, 60, 120, 150])
        return make_open(f"sin²({angle}°) + cos²({angle}°) qiymatini hisoblang.", 1)
    elif template == 'combinatorics':
        n = random.randint(5, 10)
        r = random.randint(2, min(4, n))
        return make_open(f"C({n}, {r}) ni hisoblang.", 2)
    else:
        a1 = random.randint(2, 6)
        q = random.choice([2, 3])
        n = random.randint(4, 7)
        return make_open(f"Geometrik progressiyada b₁ = {a1}, q = {q}. S_{n} ni toping.", 3)


# ═══════════════════════════════════════════════════════════════════════════════
#  GRADE 11 — 11-sinf: Limit, hosila, integral, ehtimollik
# ═══════════════════════════════════════════════════════════════════════════════

def grade_11_mcq():
    template = random.choice([
        'limit', 'derivative', 'integral', 'probability',
        'statistics', 'derivative_rules', 'definite_integral',
        'extremum', 'tangent_line', 'complex'
    ])
    
    if template == 'limit':
        a = random.randint(1, 5)
        b = random.randint(1, 5)
        # lim (ax + b) as x -> c
        c = random.randint(1, 5)
        result = a * c + b
        return make_mcq(
            f"lim(x→{c}) ({a}x + {b}) = ?",
            result, nearby(result, 3, 1, 5), 1
        )
    
    elif template == 'derivative':
        n = random.randint(2, 6)
        a = random.randint(1, 5)
        # d/dx(ax^n) = anx^(n-1)
        coeff = a * n
        return make_mcq(
            f"f(x) = {a}x^{n} bo'lsa, f'(x) = ?",
            f"{coeff}x^{n - 1}", [f"{a}x^{n - 1}", f"{coeff}x^{n}", f"{a * (n + 1)}x^{n}"], 2
        )
    
    elif template == 'integral':
        n = random.randint(1, 5)
        a = random.randint(1, 5)
        # ∫ax^n dx = a/(n+1) * x^(n+1) + C
        new_exp = n + 1
        return make_mcq(
            f"∫{a}x^{n} dx = ?",
            f"{a}/{new_exp} · x^{new_exp} + C" if a % new_exp != 0 else f"{a // new_exp}x^{new_exp} + C",
            [f"{a}x^{new_exp} + C", f"{a * new_exp}x^{n} + C", f"{a}/{n}x^{n} + C"], 2
        )
    
    elif template == 'probability':
        n = random.randint(2, 6)
        p = round(random.choice([0.1, 0.2, 0.25, 0.3, 0.4, 0.5]), 2)
        q = round(1 - p, 2)
        k = random.randint(1, min(3, n))
        c = math.comb(n, k)
        prob = round(c * p ** k * q ** (n - k), 4)
        return make_mcq(
            f"Bernulli formulasi: n={n}, p={p}, k={k}. P({k}) ni toping.",
            f"{prob}", [f"{round(prob + 0.05, 4)}", f"{round(prob * 2, 4)}", f"{round(prob / 2, 4)}"], 3
        )
    
    elif template == 'statistics':
        data = random.sample(range(1, 30), 6)
        mean = round(sum(data) / len(data), 1)
        return make_mcq(
            f"Ma'lumotlar: {', '.join(map(str, data))}. O'rta arifmetik?",
            mean, nearby_float(mean, 3, 0.5, 3.0, 1), 2
        )
    
    elif template == 'derivative_rules':
        func = random.choice(['sin', 'cos', 'e^x', 'ln'])
        derivatives = {
            'sin': ('sin(x)', 'cos(x)', ['-sin(x)', 'tan(x)', '-cos(x)']),
            'cos': ('cos(x)', '-sin(x)', ['sin(x)', '-cos(x)', 'tan(x)']),
            'e^x': ('e^x', 'e^x', ['xe^(x-1)', 'e^(x+1)', 'xe^x']),
            'ln': ('ln(x)', '1/x', ['x', 'ln(x)/x', '1/x²']),
        }
        f_name, correct, wrongs = derivatives[func]
        return make_mcq(f"f(x) = {f_name} bo'lsa, f'(x) = ?", correct, wrongs, 2)
    
    elif template == 'definite_integral':
        a_coeff = random.randint(1, 4)
        n = random.randint(1, 3)
        lower = 0
        upper = random.randint(1, 3)
        # ∫ a*x^n dx from lower to upper = a/(n+1) * (upper^(n+1) - lower^(n+1))
        result = a_coeff * (upper ** (n + 1)) / (n + 1)
        if result == int(result):
            result = int(result)
        else:
            result = round(result, 2)
        return make_mcq(
            f"∫₀^{upper} {a_coeff}x^{n} dx = ?",
            result, nearby(int(result), 3, 1, 5) if isinstance(result, int) else nearby_float(result, 3, 0.5, 3.0, 2), 2
        )
    
    elif template == 'extremum':
        a = random.randint(1, 3)
        b = random.randint(-6, 6)
        while b == 0:
            b = random.randint(-6, 6)
        # f(x) = ax² + bx + c, f'(x) = 2ax + b = 0 => x = -b/(2a)
        x_ext = round(-b / (2 * a), 2)
        if x_ext == int(x_ext):
            x_ext = int(x_ext)
        return make_mcq(
            f"f(x) = {a}x² {'+' if b >= 0 else '-'} {abs(b)}x funksiyaning ekstremum nuqtasini toping.",
            f"x = {x_ext}", [f"x = {-x_ext if x_ext != 0 else 1}", f"x = {x_ext + 1 if isinstance(x_ext, int) else round(x_ext + 1, 2)}", f"x = 0"], 2
        )
    
    elif template == 'tangent_line':
        a = random.randint(1, 3)
        x0 = random.randint(1, 4)
        # f(x) = ax², f'(x) = 2ax, f(x0) = ax0², slope = 2ax0
        y0 = a * x0 ** 2
        slope = 2 * a * x0
        return make_mcq(
            f"f(x) = {a}x² funksiyaga x₀ = {x0} nuqtada urinma chiziqning burchak koeffitsiyenti?",
            slope, nearby(slope, 3, 1, 4), 2
        )
    
    else:  # complex
        a = random.randint(1, 8)
        b = random.randint(1, 8)
        modulus = round(math.sqrt(a ** 2 + b ** 2), 2)
        return make_mcq(
            f"|{a} + {b}i| kompleks sonning moduli?",
            f"√{a ** 2 + b ** 2}", [f"{a + b}", f"√{a * b}", f"{a ** 2 + b ** 2}"], 2
        )


def grade_11_open():
    template = random.choice(['derivative', 'integral', 'limit', 'probability', 'extremum'])
    
    if template == 'derivative':
        a = random.randint(1, 5)
        n = random.randint(2, 5)
        return make_open(f"f(x) = {a}x^{n} + {random.randint(1, 10)}x funksiyaning hosilasini toping.", 2)
    elif template == 'integral':
        a = random.randint(1, 4)
        n = random.randint(1, 3)
        return make_open(f"∫{a}x^{n} dx aniqsiz integralni hisoblang.", 2)
    elif template == 'limit':
        a = random.randint(1, 5)
        b = random.randint(1, 5)
        c = random.randint(1, 3)
        return make_open(f"lim(x→{c}) ({a}x² + {b}x) ni hisoblang.", 2)
    elif template == 'probability':
        n = random.randint(3, 6)
        k = random.randint(1, 3)
        return make_open(f"C({n}, {k}) ni hisoblang.", 1)
    else:
        a = random.randint(1, 3)
        b = random.randint(-8, 8)
        while b == 0:
            b = random.randint(-8, 8)
        c = random.randint(-5, 5)
        return make_open(f"f(x) = {a}x² {'+' if b >= 0 else '-'} {abs(b)}x {'+' if c >= 0 else '-'} {abs(c)} funksiyaning ekstremum nuqtalarini va qiymatini toping.", 3)


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN: Generator dispatcher
# ═══════════════════════════════════════════════════════════════════════════════

GRADE_GENERATORS = {
    1:  (grade_1_mcq, grade_1_open),
    2:  (grade_2_mcq, grade_2_open),
    3:  (grade_3_mcq, grade_3_open),
    4:  (grade_4_mcq, grade_4_open),
    5:  (grade_5_mcq, grade_5_open),
    6:  (grade_6_mcq, grade_6_open),
    7:  (grade_7_mcq, grade_7_open),
    8:  (grade_8_mcq, grade_8_open),
    9:  (grade_9_mcq, grade_9_open),
    10: (grade_10_mcq, grade_10_open),
    11: (grade_11_mcq, grade_11_open),
}

MCQ_PER_GRADE = 200
OPEN_PER_GRADE = 50


def main():
    app = create_app()
    with app.app_context():
        # Find or create primary admin
        primary_admin = Admin.query.filter_by(role='admin').first() or Admin.query.first()
        if not primary_admin:
            print("ERROR: No admin found! Run the app first to create default admin.")
            sys.exit(1)
        
        # Delete old Matematika subject if exists (fresh start)
        old_subject = Subject.query.filter_by(name='Matematika').first()
        if old_subject:
            print(f"Eski 'Matematika' fani topildi (id={old_subject.id}). Savollarni o'chiramiz...")
            Question.query.filter_by(subject_id=old_subject.id).delete()
            db.session.delete(old_subject)
            db.session.commit()
            print("  Eski ma'lumotlar o'chirildi.")
        
        # Create Matematika subject
        matematika = Subject(
            name='Matematika',
            name_ru='Математика',
            name_en='Mathematics',
            grades='1,2,3,4,5,6,7,8,9,10,11',
            is_protected=True,
            question_count=20,       # 20 MCQ in test
            open_ended_count=5,      # 5 open-ended in test
            time_limit=40,           # 40 minutes
            show_results=True,
            is_visible=True,
            creator_id=primary_admin.id,
        )
        db.session.add(matematika)
        db.session.commit()
        print(f"\n✅ 'Matematika' fani yaratildi (id={matematika.id})")
        print(f"   Sinflar: 1-11, MCQ: 20, Ochiq: 5, Vaqt: 40 daq\n")
        
        total_created = 0
        
        for grade in range(1, 12):
            mcq_gen, open_gen = GRADE_GENERATORS[grade]
            
            print(f"📚 {grade}-sinf savollarini generatsiya qilmoqda...")
            
            # Generate MCQ questions
            mcq_questions = unique_questions(mcq_gen, MCQ_PER_GRADE)
            if len(mcq_questions) < MCQ_PER_GRADE:
                print(f"  ⚠️  MCQ: faqat {len(mcq_questions)}/{MCQ_PER_GRADE} ta noyob savol yaratildi")
            
            # Generate open-ended questions
            open_questions = unique_questions(open_gen, OPEN_PER_GRADE)
            if len(open_questions) < OPEN_PER_GRADE:
                print(f"  ⚠️  Ochiq: faqat {len(open_questions)}/{OPEN_PER_GRADE} ta noyob savol yaratildi")
            
            # Insert MCQ questions
            for q in mcq_questions:
                question = Question(
                    subject_id=matematika.id,
                    grade=grade,
                    quarter=0,  # 0 = Yillik
                    difficulty=q['difficulty'],
                    q_type='mcq',
                    question_text=q['text'],
                    option_a=q['a'],
                    option_b=q['b'],
                    option_c=q['c'],
                    option_d=q['d'],
                    correct_answer=q['correct'],
                    creator_id=primary_admin.id,
                )
                db.session.add(question)
            
            # Insert open-ended questions
            for q in open_questions:
                question = Question(
                    subject_id=matematika.id,
                    grade=grade,
                    quarter=0,  # 0 = Yillik
                    difficulty=q['difficulty'],
                    q_type='open_ended',
                    question_text=q['text'],
                    option_a='',
                    option_b='',
                    option_c='',
                    option_d='',
                    correct_answer='',
                    creator_id=primary_admin.id,
                )
                db.session.add(question)
            
            grade_total = len(mcq_questions) + len(open_questions)
            total_created += grade_total
            print(f"  ✅ {grade}-sinf: {len(mcq_questions)} MCQ + {len(open_questions)} ochiq = {grade_total} ta savol")
        
        db.session.commit()
        print(f"\n{'='*60}")
        print(f"🎉 JAMI: {total_created} ta savol bazaga yozildi!")
        print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
