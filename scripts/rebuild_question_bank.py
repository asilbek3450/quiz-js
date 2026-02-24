# pyright: reportCallIssue=false, reportAttributeAccessIssue=false
import sys
import os
import random
import string
from dataclasses import dataclass

# Allow importing app/models from repo root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app  # noqa: E402
from extensions import db  # noqa: E402
from models import Subject, Question, ControlWork  # noqa: E402


PRACTICE_PER_QUARTER = 200
CONTROL_PER_QUARTER = 100


def _norm_key(text: str) -> str:
    return " ".join((text or "").lower().split())


def _shuffle_options(answer: str, wrongs: list[str]) -> tuple[list[str], str]:
    options = [str(answer)] + [str(w) for w in wrongs if str(w) != str(answer)]
    # de-dup but preserve order as much as possible
    seen = set()
    uniq = []
    for o in options:
        if o not in seen:
            uniq.append(o)
            seen.add(o)

    # pad to 4
    while len(uniq) < 4:
        filler = f"Variant {len(uniq) + 1}"
        if filler not in seen:
            uniq.append(filler)
            seen.add(filler)

    final = uniq[:4]
    random.shuffle(final)
    correct_char = ["A", "B", "C", "D"][final.index(str(answer))]
    return final, correct_char


@dataclass(frozen=True)
class QItem:
    text: str
    answer: str
    wrongs: list[str]
    difficulty: int = 2  # 1=easy,2=medium,3=hard
    lesson: int | None = None


class QuestionFactory:
    def __init__(self) -> None:
        self._seen: set[str] = set()

    def build(self, subject_id: int, grade: int, quarter: int, item: QItem) -> Question | None:
        key = f"{subject_id}:{grade}:{quarter}:{_norm_key(item.text)}"
        if key in self._seen:
            return None
        self._seen.add(key)

        opts, correct = _shuffle_options(item.answer, item.wrongs)
        return Question(
            subject_id=subject_id,
            grade=grade,
            quarter=quarter,
            difficulty=item.difficulty,
            lesson=item.lesson,
            question_text=item.text,
            option_a=opts[0],
            option_b=opts[1],
            option_c=opts[2],
            option_d=opts[3],
            correct_answer=correct,
        )


# ------------------ Informatika (5-6) generators ------------------

def _variants(concept: str, definition: str, wrong_defs: list[str]) -> list[QItem]:
    t = [
        f"'{concept}' nima?",
        f"'{concept}' tushunchasining to‘g‘ri ta'rifini toping.",
        f"Kompyuterda '{concept}' nimaga xizmat qiladi?",
        f"Qaysi javob '{concept}' ga mos keladi?",
    ]
    return [QItem(text=qt, answer=definition, wrongs=wrong_defs, difficulty=2) for qt in t]


def informatics_pool(grade: int, quarter: int) -> list[QItem]:
    pool: list[QItem] = []

    if grade == 5 and quarter == 1:
        items = [
            ("CPU (protsessor)", "Buyruqlarni bajaradi va hisob-kitob qiladi", ["Ma'lumotni ekranga chiqaradi", "Matn kiritadi", "Qog‘ozga chop etadi"]),
            ("RAM", "Dasturlar ishlayotganda vaqtincha ma'lumot saqlaydi", ["Doimiy saqlash qurilmasi", "Internet tarqatadi", "Ovoz yozadi"]),
            ("HDD/SSD", "Ma'lumotni doimiy saqlaydi", ["Faqat vaqtincha saqlaydi", "Rasm chizadi", "Tarmoq kabeli"]),
            ("Operatsion tizim", "Kompyuter resurslarini boshqaradi (masalan Windows)", ["Faqat brauzer", "Faqat o‘yin", "Matn muharriri"]),
            ("Fayl kengaytmasi", "Fayl turini bildiruvchi oxirgi qism (masalan .docx)", ["Fayl hajmi", "Internet tezligi", "Parol turi"]),
            ("Papka (folder)", "Fayllarni tartib bilan saqlash uchun konteyner", ["Virus", "Monitor", "Protsessor"]),
        ]
        for c, d, w in items:
            pool += _variants(c, d, w)

        for _ in range(800):
            a = random.randint(5, 99)
            b = random.randint(2, 15)
            op = random.choice(["+", "-", "*", "//", "%"])
            if op == "//":
                ans = str(a // b)
                wrongs = [str(a / b), str(a % b), str(a // (b + 1))]
            elif op == "%":
                ans = str(a % b)
                wrongs = [str(a // b), str(b % a), str((a + b) % b)]
            elif op == "*":
                ans = str(a * b)
                wrongs = [str(a + b), str(a * (b - 1)), str(a * b + 1)]
            elif op == "-":
                ans = str(a - b)
                wrongs = [str(b - a), str(a + b), str(a - b - 1)]
            else:
                ans = str(a + b)
                wrongs = [str(a - b), str(a + b + 1), str(a + b - 1)]
            pool.append(
                QItem(
                    text=f"Quyidagi ifoda natijasi nechchi?\n\n{a} {op} {b}",
                    answer=ans,
                    wrongs=wrongs,
                )
            )

    elif grade == 5 and quarter == 2:
        items = [
            ("Paint", "Rasm chizish va tahrirlash dasturi", ["Matn muharriri", "Jadval dasturi", "Brauzer"]),
            ("PNG", "Shaffof fonni qo‘llab-quvvatlaydigan rasm formati", ["Faqat audio formati", "Faqat video formati", "Fayl siqmaydi"]),
            ("JPG", "Fotosuratlar uchun keng ishlatiladigan siqilgan rasm formati", ["Faqat matn", "Animatsiya", "Dastur kodi"]),
            ("Ctrl+Z", "Oxirgi amalni bekor qiladi", ["Nusxalaydi", "Saqlaydi", "Chop etadi"]),
            ("Ctrl+S", "Hujjatni saqlaydi", ["Topadi", "Almashtiradi", "Yopadi"]),
        ]
        for c, d, w in items:
            pool += _variants(c, d, w)

        tools = [
            ("Qalam", "Chiziq chizish", "O‘chirg‘ich", "O‘chirish"),
            ("To‘ldirish (Fill)", "Yopiq sohaga rang berish", "Lupa", "Kattalashtirish"),
            ("Matn (Text)", "Rasmga yozuv kiritish", "Pipetka", "Rang tanlash"),
        ]
        for a, a_def, b, b_def in tools:
            pool.append(
                QItem(
                    text=f"Paint’da {a} va {b} asboblarining vazifasi to‘g‘ri berilgan variantni toping.",
                    answer=f"{a}: {a_def}; {b}: {b_def}",
                    wrongs=[
                        f"{a}: {b_def}; {b}: {a_def}",
                        f"{a}: {a_def}; {b}: {a_def}",
                        f"{a}: {b_def}; {b}: {b_def}",
                    ],
                )
            )

        # Parametrli (unikal) amaliy savollar — havzani katta qilish uchun
        format_cases = [
            ("Shaffof fon kerak", "PNG", ["JPG", "BMP", "GIF"]),
            ("Fotosurat hajmini kichraytirib yuborish kerak", "JPG", ["PNG", "BMP", "TXT"]),
            ("Eng yuqori sifat (siqilmagan) kerak", "BMP", ["JPG", "PNG", "MP3"]),
        ]
        for _ in range(1500):
            case, ans, wrongs = random.choice(format_cases)
            fname = "".join(random.choices("abcdxyz", k=5))
            pool.append(
                QItem(
                    text=f"Rasmni saqlash: {case}. Qaysi formatni tanlash ma'qul?\n\nFayl nomi: {fname}.?",
                    answer=ans,
                    wrongs=wrongs,
                )
            )

        paint_actions = [
            ("Rasmni 90° ga aylantirish", "Rotate", ["Resize", "Crop", "Fill"]),
            ("Rasm o‘lchamini kichraytirish/kattalashtirish", "Resize", ["Rotate", "Brush", "Pipetka"]),
            ("Tasvirning bir qismini belgilab kesib olish", "Select", ["Text", "Fill", "Eraser"]),
            ("Yopiq sohani rang bilan bo‘yash", "Fill", ["Brush", "Select", "Zoom"]),
            ("Keraksiz qismni o‘chirish", "O‘chirg‘ich", ["Qalam", "Matn", "Pipetka"]),
        ]
        for _ in range(1500):
            act, ans, wrongs = random.choice(paint_actions)
            color = random.choice(["qizil", "ko‘k", "yashil", "sariq", "oq", "qora"])
            size = random.choice(["kichik", "o‘rta", "katta"])
            pool.append(
                QItem(
                    text=f"Paint’da amaliy topshiriq: {act}. (rang: {color}, chiziq: {size}) Buning uchun qaysi asbob/bo‘lim eng mos?",
                    answer=ans,
                    wrongs=wrongs,
                )
            )

    elif grade == 5 and quarter == 3:
        items = [
            ("Excel katak manzili", "Ustun harfi + qator raqami (masalan A1)", ["Qator harfi + ustun raqami", "Faqat raqam", "Faqat harf"]),
            ("Formula", "Hisob-kitobni avtomatlashtiruvchi ifoda (=...)", ["Rasm", "Papka", "Parol"]),
            ("SUM()", "Yig‘indini hisoblaydi", ["O‘rtacha", "Eng katta", "Matn uzunligi"]),
            ("AVERAGE()", "O‘rtachani topadi", ["Yig‘indi", "Eng kichik", "Matnni bo‘ladi"]),
        ]
        for c, d, w in items:
            pool += _variants(c, d, w)

        cols = list("ABCDEFGH")
        for _ in range(1200):
            c = random.choice(cols)
            r = random.randint(1, 120)
            ans = f"{c}{r}"
            pool.append(
                QItem(
                    text=f"Excel’da {c}-ustun va {r}-qator kesishgan katak manzili qaysi?",
                    answer=ans,
                    wrongs=[f"{r}{c}", f"{c}:{r}", f"{c}-{r}"],
                )
            )

        for _ in range(600):
            f = random.choice(["SUM", "AVERAGE", "MAX", "MIN", "COUNT"])
            a1 = random.choice(cols[:3]) + str(random.randint(1, 5))
            a2 = random.choice(cols[:3]) + str(random.randint(6, 12))
            rng = f"{a1}:{a2}"
            ans_map = {"SUM": "Yig‘indi", "AVERAGE": "O‘rtacha", "MAX": "Eng katta", "MIN": "Eng kichik", "COUNT": "Sonli kataklar soni"}
            ans = ans_map[f]
            pool.append(
                QItem(
                    text=f"Excel’da `={f}({rng})` formulasi nimani hisoblaydi?",
                    answer=ans,
                    wrongs=[v for k, v in ans_map.items() if k != f][:3],
                )
            )

    elif grade == 5 and quarter == 4:
        items = [
            ("URL", "Veb-sahifa manzili", ["Kompyuter paroli", "Fayl nomi", "Dastur turi"]),
            ("Brauzer", "Veb-sahifalarni ko‘rish dasturi", ["Matn muharriri", "Antivirus", "Arxivator"]),
            ("HTTPS", "Shifrlangan xavfsiz aloqa protokoli", ["Faqat rasm formati", "Operatsion tizim", "Video pleer"]),
            ("Phishing", "Soxta sahifa/xat orqali ma'lumot o‘g‘irlash", ["Fayl siqish", "Tezlashtirish", "Kompyuterni tozalash"]),
            ("Kuchli parol", "Uzun va murakkab (harf+son+belgi) parol", ["Faqat 12345", "Faqat ism", "Faqat tug‘ilgan yil"]),
        ]
        for c, d, w in items:
            pool += _variants(c, d, w)

        for _ in range(900):
            domain = random.choice(["school.uz", "example.com", "jahonschool.uz", "edu.uz"])
            path = random.choice(["/login", "/news", "/profile", "/courses"])
            proto = random.choice(["http", "https"])
            url = f"{proto}://{domain}{path}"
            pool.append(
                QItem(
                    text=f"Quyidagi URL’da domen qismi qaysi?\n\n{url}",
                    answer=domain,
                    wrongs=[proto, path, url],
                )
            )

        # Ko‘proq unikal: parol kuchliligini baholash va fishing belgilari
        for _ in range(1600):
            base = random.choice(["Ali", "user", "school", "python", "test"])
            pwd = random.choice(
                [
                    f"{base}123",
                    f"{base}{random.randint(10,99)}",
                    f"{base.capitalize()}_{random.randint(10,99)}!",
                    f"{base}{random.choice('!@#$')}{random.randint(100,999)}Aa",
                ]
            )
            is_strong = (
                len(pwd) >= 8
                and any(c.islower() for c in pwd)
                and any(c.isupper() for c in pwd)
                and any(c.isdigit() for c in pwd)
                and any(c in "!@#$%^&*_" for c in pwd)
            )
            ans = "Kuchli" if is_strong else "Kuchsiz"
            pool.append(
                QItem(
                    text=f"Parolni baholang: `{pwd}`. Bu parol kuchlimi?",
                    answer=ans,
                    wrongs=["Kuchli", "Kuchsiz", "Aniqlab bo‘lmaydi"],
                )
            )

        phishing_samples = [
            ("Havola domeni tanish emas (xatoda yozilgan)", "Phishing belgisi", ["Xavfsiz belgi", "Brauzer xatosi", "Internet tezligi"]),
            ("Parolni shoshilinch kiritishni so‘raydi", "Phishing belgisi", ["Antivirus xabari", "Oddiy reklama", "Fayl formati"]),
            ("HTTPS yo‘q va qulf belgisi ko‘rinmaydi", "Xavfsizlik past bo‘lishi mumkin", ["Doim xavfsiz", "Internet uzildi", "Kompyuter o‘chdi"]),
        ]
        for _ in range(1400):
            sign, ans, wrongs = random.choice(phishing_samples)
            domain = random.choice(["paypaI.com", "g00gle.com", "jahonschooI.uz", "secure-login.example.com"])
            pool.append(
                QItem(
                    text=f"Ehtiyot bo‘ling: `{domain}` saytida {sign}. Bu holat nimani anglatadi?",
                    answer=ans,
                    wrongs=wrongs,
                )
            )

    elif grade == 6 and quarter == 1:
        items = [
            ("Ctrl+C", "Tanlangan matn/obyektni nusxalaydi", ["Qirqib oladi", "Joylashtiradi", "Saqlaydi"]),
            ("Ctrl+V", "Buferdagi ma'lumotni joylashtiradi", ["Nusxalaydi", "Qidiradi", "Chop etadi"]),
            ("Ctrl+X", "Tanlanganini qirqib buferga oladi", ["Saqlaydi", "Bekor qiladi", "Qalin qiladi"]),
            ("Ctrl+F", "Hujjat ichidan qidiradi", ["Almashtiradi", "Nusxalaydi", "Ochadi"]),
            ("Ctrl+H", "Find/Replace (almashtirish) oynasini ochadi", ["Chop etadi", "Yopadi", "Yangi hujjat"]),
            ("Header", "Sahifaning yuqori qismidagi takrorlanuvchi qism", ["Pastki qism", "Jadval", "Rasm"]),
            ("Footer", "Sahifaning pastki qismidagi takrorlanuvchi qism", ["Yuqori qism", "Grafik", "Matn qatori"]),
        ]
        for c, d, w in items:
            pool += _variants(c, d, w)

        for _ in range(1000):
            a = random.randint(1, 50)
            b = random.randint(1, 50)
            op = random.choice(["+", "-", "*"])
            expr = f"{a} {op} {b}"
            ans = str(eval(expr))
            pool.append(
                QItem(
                    text=f"Word/Excel’da hisob-kitob emas, mantiq: quyidagi ifoda natijasi nechchi?\n\n{expr}",
                    answer=ans,
                    wrongs=[str(int(ans) + 1), str(int(ans) - 1), str(a)],
                )
            )

    elif grade == 6 and quarter == 2:
        items = [
            ("$A$1", "Absolyut katak manzili (ko‘chirganda o‘zgarmaydi)", ["Nisbiy manzil", "Xato manzil", "Format"]),
            ("Sort", "Ma'lumotlarni tartiblash", ["Chop etish", "Rasm chizish", "Internetga ulash"]),
            ("Filter", "Kerakli ma'lumotlarni saralab ko‘rsatish", ["Qirqish", "Nusxalash", "O‘chirish"]),
            ("Workbook", "Excel fayli (bir nechta sheet bo‘lishi mumkin)", ["Bitta katak", "Bitta formula", "Rasm"]),
        ]
        for c, d, w in items:
            pool += _variants(c, d, w)

        for _ in range(1200):
            nums = [random.randint(1, 25) for _ in range(5)]
            f = random.choice(["MAX", "MIN", "SUM"])
            ans = str(max(nums) if f == "MAX" else min(nums) if f == "MIN" else sum(nums))
            pool.append(
                QItem(
                    text=f"Excel’da `={f}({', '.join(map(str, nums))})` ma'nosi bo‘yicha natija qaysi?",
                    answer=ans,
                    wrongs=[str(sum(nums)), str(max(nums)), str(min(nums))],
                )
            )

    elif grade == 6 and quarter == 3:
        items = [
            ("Algoritm", "Amallar ketma-ketligi", ["Kompyuter qismi", "Rasm formati", "Parol"]),
            ("Blok-sxema", "Algoritmning grafik ko‘rinishi", ["Matn muharriri", "Disk", "Internet"]),
            ("Repeat", "Bir amalni bir necha marta takrorlash bloki", ["Rasmni o‘chirish", "Internet tezligi", "Ovoz"]),
            ("If", "Shart tekshirish bloki", ["Tasodifiy rang", "Matn yozish", "Fayl ochish"]),
        ]
        for c, d, w in items:
            pool += _variants(c, d, w)

        # Ko‘proq kombinatsiyalar: n diapazonini kengaytiramiz va turli algoritm savollari
        for _ in range(1400):
            n = random.randint(5, 400)
            ans_int = n * (n + 1) // 2
            pool.append(
                QItem(
                    text=(
                        "Algoritm: 1 dan n gacha sonlar yig‘indisini toping.\n\n"
                        f"n = {n}"
                    ),
                    answer=str(ans_int),
                    wrongs=[str(n * (n - 1) // 2), str(n * n), str(ans_int + random.randint(1, 9))],
                )
            )

        for _ in range(1400):
            start = random.randint(1, 50)
            step = random.randint(2, 9)
            k = random.randint(5, 30)
            last = start + step * (k - 1)
            pool.append(
                QItem(
                    text=(
                        "Algoritm: start qiymatdan boshlab har safar step ga oshirib k marta yozildi. Oxirgi qiymat nechchi?\n\n"
                        f"start={start}, step={step}, k={k}"
                    ),
                    answer=str(last),
                    wrongs=[str(last - step), str(start + step * k), str(start * step)],
                )
            )

    else:  # grade == 6 and quarter == 4
        items = [
            ("Slayd", "Taqdimotdagi alohida sahifa", ["Excel katagi", "Word paragrafi", "Fayl kengaytmasi"]),
            ("F5", "Taqdimotni birinchi slayddan boshlaydi", ["Saqlaydi", "Yopadi", "Nusxalaydi"]),
            ("Transition", "Slaydlar almashish effekti", ["Shrift rangi", "Matn tekislash", "Jadval"]),
            ("Animation", "Slayd ichidagi obyekt harakati effekti", ["Slayd o‘lchami", "Fayl nomi", "Parol"]),
        ]
        for c, d, w in items:
            pool += _variants(c, d, w)

        for _ in range(1400):
            a = random.randint(5, 500)  # MB
            b = random.randint(1, 50)   # MB/s
            pool.append(
                QItem(
                    text=f"Internet tezligi: {a} MB fayl {b} MB/s tezlikda taxminan necha sekundda yuklanadi? (butun qismini oling)",
                    answer=str(a // b),
                    wrongs=[str(a / b), str((a + b) // b), str(a // (b + 1))],
                )
            )

        for _ in range(1400):
            slides = random.randint(5, 40)
            sec = random.randint(3, 15)
            total = slides * sec
            pool.append(
                QItem(
                    text=f"PowerPoint: {slides} ta slayd har biri {sec} sekunddan avtomatik almashsa, taqdimot taxminan necha sekund davom etadi?",
                    answer=str(total),
                    wrongs=[str(total - sec), str(total + sec), str(slides + sec)],
                )
            )

    random.shuffle(pool)
    return pool


# ------------------ Python (7-9) generators ------------------

def _rand_ident() -> str:
    return random.choice(string.ascii_lowercase) + random.choice(["", str(random.randint(1, 9))])


def _py_code_q(code: str, ans: str, wrongs: list[str]) -> QItem:
    return QItem(
        text=f"Quyidagi kod natijasi nima?\n\n```python\n{code}\n```",
        answer=ans,
        wrongs=wrongs,
    )


def _py_code_qd(code: str, ans: str, wrongs: list[str], difficulty: int, lesson: int | None = None) -> QItem:
    return QItem(
        text=f"Quyidagi kod natijasi nima?\n\n```python\n{code}\n```",
        answer=ans,
        wrongs=wrongs,
        difficulty=difficulty,
        lesson=lesson,
    )


def python_pool(grade: int, quarter: int) -> list[QItem]:
    pool: list[QItem] = []

    # Curriculum-driven pools (7→8→9 murakkablashadi), difficulty tagged for balanced selection.
    if grade == 7 and quarter == 1:
        # 1–6-dars: dastur tushunchasi, print, variables, types, arithmetic, sodda masalalar
        pool.append(
            QItem(
                text="Dastur nima?",
                answer="Kompyuter bajaradigan buyruqlar ketma-ketligi",
                wrongs=["Faqat kompyuterni yoqish", "Internetdagi sahifa", "Klaviatura tugmasi"],
                difficulty=2,
                lesson=1,
            )
        )
        pool.append(
            QItem(
                text="Python’da ekranga chiqarish funksiyasi qaysi?",
                answer="print()",
                wrongs=["input()", "show()", "write()"],
                difficulty=2,
                lesson=2,
            )
        )

        for _ in range(2200):
            v = _rand_ident()
            val = random.randint(-100, 300)
            code = f"{v} = {val}\nprint({v})"
            pool.append(_py_code_qd(code, str(val), [str(val + 1), str(val - 1), "Xatolik"], 2, 3))

        for _ in range(1400):
            val = random.choice([random.randint(1, 50), round(random.uniform(1, 50), 2), f"'{random.choice(['salom','python','dastur'])}'"])
            code = f"x = {val}\nprint(type(x))"
            if isinstance(val, str) and val.startswith("'"):
                ans = "<class 'str'>"
            elif isinstance(val, float):
                ans = "<class 'float'>"
            else:
                ans = "<class 'int'>"
            pool.append(_py_code_qd(code, ans, ["<class 'int'>", "<class 'float'>", "<class 'str'>"], 2, 4))

        for _ in range(2000):
            a = random.randint(2, 30)
            b = random.randint(2, 20)
            code = f"print({a} + {b} * 2)"
            ans = str(a + b * 2)
            pool.append(_py_code_qd(code, ans, [str((a + b) * 2), str(a + b), "Xatolik"], 3, 5))

        for _ in range(1600):
            x = random.randint(10, 99)
            y = random.randint(1, 9)
            code = f"x = {x}\ny = {y}\nprint(x // y, x % y)"
            ans = f"{x // y} {x % y}"
            pool.append(_py_code_qd(code, ans, [f"{x / y} {x % y}", f"{x % y} {x // y}", "Xatolik"], 3, 5))

    elif grade == 7 and quarter == 2:
        # 10–15-dars: strings, index/slicing, methods, type errors
        words = ["Python", "Dasturlash", "Algoritm", "Kompyuter", "JahonSchool"]
        for _ in range(2400):
            s = random.choice(words) + random.choice(["", str(random.randint(1, 99))])
            i = random.randint(0, len(s) - 1)
            code = f"s = '{s}'\nprint(s[{i}])"
            pool.append(_py_code_qd(code, s[i], [s[0], s[-1], "Xatolik"], 2, 11))

        for _ in range(2200):
            s = random.choice(words) + random.choice(["_uz", "_py", "_dev"])
            a = random.randint(0, max(0, len(s) - 3))
            b = random.randint(a + 1, len(s))
            step = random.choice([1, 2])
            code = f"s = '{s}'\nprint(s[{a}:{b}:{step}])"
            ans = s[a:b:step]
            pool.append(_py_code_qd(code, ans, [s[a:b], s[b:a], "Xatolik"], 3, 11))

        for _ in range(2200):
            s = random.choice(["  python  ", "PyThOn", "hello world", "salom dunyo"])
            method = random.choice(["strip", "lower", "upper", "title", "replace"])
            if method == "replace":
                old = random.choice(list(set([c for c in s if c.isalpha()]))) if any(c.isalpha() for c in s) else "o"
                new = random.choice(["a", "X", "1"])
                code = f"s = '{s}'\nprint(s.replace('{old}', '{new}'))"
                ans = s.replace(old, new)
            else:
                code = f"s = '{s}'\nprint(s.{method}())"
                ans = getattr(s, method)()
            pool.append(_py_code_qd(code, ans, [s, s.strip(), "Xatolik"], 2, 12))

        for _ in range(2000):
            # type-error lesson
            a = random.randint(1, 20)
            b = str(random.randint(1, 20))
            code = f"x = {a}\ny = '{b}'\nprint(x + y)"
            pool.append(
                QItem(
                    text=f"Quyidagi kodda nima sodir bo‘ladi?\n\n```python\n{code}\n```",
                    answer="TypeError (int va str qo‘shilmaydi)",
                    wrongs=["Natija chiqadi", "SyntaxError", "x+y satr bo‘ladi"],
                    difficulty=3,
                    lesson=13,
                )
            )

    elif grade == 7 and quarter == 3:
        # 17–31-dars: if/elif/else, mantiq, for/while, break/continue, list basics + ATM
        for _ in range(2600):
            x = random.randint(-50, 150)
            y = random.randint(-50, 150)
            code = (
                f"x = {x}\n"
                f"y = {y}\n"
                "if x > y:\n"
                "    print('Katta')\n"
                "elif x == y:\n"
                "    print('Teng')\n"
                "else:\n"
                "    print('Kichik')"
            )
            ans = "Katta" if x > y else "Teng" if x == y else "Kichik"
            pool.append(_py_code_qd(code, ans, ["Katta", "Teng", "Kichik"], 2, 18))

        for _ in range(2400):
            n = random.randint(5, 30)
            step = random.choice([1, 2, 3])
            code = f"s = 0\nfor i in range(1, {n+1}, {step}):\n    if i % 2 == 0:\n        continue\n    s += i\nprint(s)"
            ans = str(sum(i for i in range(1, n + 1, step) if i % 2 != 0))
            pool.append(_py_code_qd(code, ans, [str(n), "0", "Xatolik"], 3, 24))

        for _ in range(2400):
            lst = [random.randint(1, 20) for _ in range(5)]
            idx = random.randint(-5, 4)
            code = f"L = {lst}\nprint(L[{idx}])"
            ans = str(lst[idx])
            pool.append(_py_code_qd(code, ans, [str(lst[0]), str(len(lst)), "Xatolik"], 2, 29))

        for _ in range(1800):
            bal = random.randint(50, 500) * 1000
            wd = random.randint(10, 600) * 1000
            code = (
                f"balans = {bal}\n"
                f"yechish = {wd}\n"
                "if yechish > balans:\n"
                "    print('Yetarli emas')\n"
                "else:\n"
                "    print(balans - yechish)"
            )
            ans = "Yetarli emas" if wd > bal else str(bal - wd)
            pool.append(_py_code_qd(code, ans, ["0", str(bal), str(wd)], 3, 21))

    elif grade == 7 and quarter == 4:
        # umumiy (I–III) bo‘yicha: murakkab aralash
        # Medium: string + list + simple loops (high variety)
        for _ in range(3400):
            t = random.choice(["slice_upper", "list_sum", "if_str", "loop_count"])
            if t == "slice_upper":
                s = random.choice(["python", "dastur", "algoritm", "maktab", "jahonschool"]) + str(random.randint(1, 999))
                a = random.randint(0, 2)
                b = random.randint(a + 2, min(len(s), a + 8))
                code = f"s = '{s}'\nprint(s[{a}:{b}].upper())"
                ans = s[a:b].upper()
                pool.append(_py_code_qd(code, ans, [s.upper(), s[a:b], "Xatolik"], 2, None))
            elif t == "list_sum":
                nums = [random.randint(-5, 20) for _ in range(6)]
                code = f"nums = {nums}\nprint(sum(nums[:3]) - sum(nums[-2:]))"
                ans = str(sum(nums[:3]) - sum(nums[-2:]))
                pool.append(_py_code_qd(code, ans, [str(sum(nums)), "0", "Xatolik"], 2, None))
            elif t == "if_str":
                s = random.choice(["Python", "dastur", "algoritm", "maktab"]) + random.choice(["", "!", "??"])
                code = f"s = '{s}'\nprint('ok' if 'a' in s.lower() else 'no')"
                ans = "ok" if "a" in s.lower() else "no"
                pool.append(_py_code_qd(code, ans, ["ok", "no", "Xatolik"], 2, None))
            else:
                n = random.randint(10, 120)
                m = random.randint(2, 9)
                code = f"cnt = 0\nfor i in range({n}):\n    if i % {m} == 0:\n        cnt += 1\nprint(cnt)"
                ans = str(len([i for i in range(n) if i % m == 0]))
                pool.append(_py_code_qd(code, ans, [str(n//m), str(n), "Xatolik"], 2, None))

        # Hard: mixed branching+loops+lists (ensure >80 unique easily)
        for _ in range(4200):
            t = random.choice(["mod3_list", "break_continue", "nested", "while_atmish"])
            if t == "mod3_list":
                n = random.randint(20, 250)
                a = random.randint(1, 6)
                b = random.randint(7, 12)
                code = (
                    f"res = []\nfor i in range({n}):\n"
                    f"    if i % {a} == 0:\n"
                    f"        res.append(i)\n"
                    f"    elif i % {b} == 0:\n"
                    f"        res.append(-i)\n"
                    "print(res[0], res[-1], len(res))"
                )
                res = []
                for i in range(n):
                    if i % a == 0:
                        res.append(i)
                    elif i % b == 0:
                        res.append(-i)
                ans = f"{res[0]} {res[-1]} {len(res)}"
                pool.append(_py_code_qd(code, ans, ["0 0 0", str(n), "Xatolik"], 3, None))
            elif t == "break_continue":
                limit = random.randint(15, 120)
                stop = random.randint(3, min(50, limit - 1))
                skip = random.randint(2, min(20, stop))
                code = (
                    f"s = 0\nfor i in range(1, {limit}):\n"
                    f"    if i == {skip}:\n"
                    "        continue\n"
                    f"    if i == {stop}:\n"
                    "        break\n"
                    "    s += i\nprint(s)"
                )
                s = 0
                for i in range(1, limit):
                    if i == skip:
                        continue
                    if i == stop:
                        break
                    s += i
                pool.append(_py_code_qd(code, str(s), [str(s+1), str(stop), "Xatolik"], 3, None))
            elif t == "nested":
                n = random.randint(2, 6)
                m = random.randint(2, 6)
                code = f"c = 0\nfor i in range({n}):\n    for j in range({m}):\n        if (i+j) % 2 == 0:\n            c += 1\nprint(c)"
                c = 0
                for i in range(n):
                    for j in range(m):
                        if (i + j) % 2 == 0:
                            c += 1
                pool.append(_py_code_qd(code, str(c), [str(n*m), "0", "Xatolik"], 3, None))
            else:
                bal = random.randint(100, 900) * 1000
                fee = random.choice([0, 1000, 2000, 5000])
                wd = random.randint(50, 950) * 1000
                code = (
                    f"balans={bal}\nkomissiya={fee}\nyechish={wd}\n"
                    "if yechish <= 0:\n"
                    "    print('Xato')\n"
                    "elif yechish + komissiya > balans:\n"
                    "    print('Rad')\n"
                    "else:\n"
                    "    print(balans - yechish - komissiya)"
                )
                if wd <= 0:
                    ans = "Xato"
                elif wd + fee > bal:
                    ans = "Rad"
                else:
                    ans = str(bal - wd - fee)
                pool.append(_py_code_qd(code, ans, ["Rad", "Xato", str(bal)], 3, None))

    elif grade == 8 and quarter == 1:
        # Kirish + 7-sinf takror + murakkab if/loop
        for _ in range(2600):
            x = random.randint(-20, 120)
            y = random.randint(-20, 120)
            z = random.randint(-20, 120)
            code = (
                f"x={x}\ny={y}\nz={z}\n"
                "if x < y and y <= z:\n"
                "    print('A')\n"
                "elif x == z:\n"
                "    print('B')\n"
                "else:\n"
                "    print('C')"
            )
            ans = "A" if (x < y and y <= z) else "B" if x == z else "C"
            pool.append(_py_code_qd(code, ans, ["A", "B", "C"], 2, 2))

        for _ in range(2400):
            n = random.randint(6, 40)
            code = f"s = 0\nfor i in range(1, {n}):\n    s += i\nprint(s)"
            ans = str(sum(range(1, n)))
            pool.append(_py_code_qd(code, ans, [str(n), "0", "Xatolik"], 2, 3))

        # Hard: while/for murakkabroq (ko‘proq kombinatsiya)
        for _ in range(3600):
            t = random.choice(["while_mul", "while_dec", "for_break", "logic_or"])
            if t == "while_mul":
                n = random.randint(10, 500)
                mul = random.choice([2, 3])
                code = f"i = 1\nwhile i < {n}:\n    i *= {mul}\nprint(i)"
                i = 1
                while i < n:
                    i *= mul
                pool.append(_py_code_qd(code, str(i), [str(n), str(i // mul), "Cheksiz"], 3, 3))
            elif t == "while_dec":
                start = random.randint(30, 200)
                dec = random.randint(2, 9)
                limit = random.randint(0, 25)
                code = f"i = {start}\nstep = 0\nwhile i > {limit}:\n    i -= {dec}\n    step += 1\nprint(step, i)"
                i = start
                step = 0
                while i > limit:
                    i -= dec
                    step += 1
                pool.append(_py_code_qd(code, f"{step} {i}", [f"{step+1} {i}", f"{step} {i+dec}", "Xatolik"], 3, 3))
            elif t == "for_break":
                n = random.randint(10, 200)
                stop = random.randint(2, min(50, n - 1))
                code = f"s=0\nfor i in range({n}):\n    if i=={stop}:\n        break\n    s+=i\nprint(s)"
                s = sum(range(stop))
                pool.append(_py_code_qd(code, str(s), [str(s+1), str(stop), "Xatolik"], 3, 3))
            else:
                a = random.randint(-20, 120)
                b = random.randint(-20, 120)
                c = random.randint(-20, 120)
                code = f"a={a}\nb={b}\nc={c}\nprint((a<0) or (b>c and c%2==0))"
                ans = str((a < 0) or (b > c and c % 2 == 0))
                pool.append(_py_code_qd(code, ans, [str(not ((a < 0) or (b > c and c % 2 == 0))), "None", "Xatolik"], 3, 2))

    elif grade == 8 and quarter == 2:
        # List methods, tuple, dict + amaliy
        for _ in range(2600):
            lst = [random.randint(1, 20) for _ in range(5)]
            v = random.randint(1, 30)
            code = f"L = {lst}\nL.append({v})\nL.sort()\nprint(L[-1])"
            ans = str(max(lst + [v]))
            pool.append(_py_code_qd(code, ans, [str(v), str(len(lst)), "Xatolik"], 2, 5))

        for _ in range(2400):
            tup = tuple(random.randint(1, 20) for _ in range(4))
            code = f"t = {tup}\nprint(t[1:])"
            ans = str(tup[1:])
            pool.append(_py_code_qd(code, ans, [str(tup[:-1]), str(tup), "Xatolik"], 2, 6))

        for _ in range(2600):
            keys = ["ism", "yosh", "sinf", "shahar"]
            k1, k2 = random.sample(keys, 2)
            v1, v2 = random.randint(10, 20), random.randint(21, 40)
            code = f"d = {{'{k1}': {v1}, '{k2}': {v2}}}\nprint(d.get('{k2}', 0) + d.get('{k1}', 0))"
            ans = str(v1 + v2)
            pool.append(_py_code_qd(code, ans, [str(v1), str(v2), "Xatolik"], 3, 7))

    elif grade == 8 and quarter == 3:
        # String methods + f-strings + comprehension + functions + *args/**kwargs
        for _ in range(2400):
            name = random.choice(["Ali", "Olim", "Nodira", "Zarina"])
            age = random.randint(10, 30)
            code = f"name = '{name}'\nage = {age}\nprint(f'{name} {age+1}')"
            ans = f"{name} {age+1}"
            pool.append(_py_code_qd(code, ans, [f"{name} {age}", f"{name}{age+1}", "Xatolik"], 2, 11))

        for _ in range(2400):
            nums = [random.randint(-10, 30) for _ in range(6)]
            code = f"nums = {nums}\nprint([x*x for x in nums if x > 0])"
            ans = str([x * x for x in nums if x > 0])
            pool.append(_py_code_qd(code, ans, [str(nums), "[]", "Xatolik"], 3, 12))

        for _ in range(2400):
            a, b, c = random.randint(1, 9), random.randint(1, 9), random.randint(1, 9)
            code = "def f(*args):\n    return sum(args)\nprint(f({}, {}, {}))".format(a, b, c)
            ans = str(a + b + c)
            pool.append(_py_code_qd(code, ans, [str(a*b*c), str(a+b), "Xatolik"], 2, 14))

        for _ in range(2400):
            n = random.randint(2, 8)
            code = "def g(**kw):\n    return len(kw)\nprint(g(a=1, b=2, c={}))".format(n)
            ans = "3"
            pool.append(_py_code_qd(code, ans, ["2", "4", "Xatolik"], 3, 14))

    elif grade == 8 and quarter == 4:
        # umumiy
        for _ in range(3200):
            t = random.choice(["sum_max", "even_filter", "dict_len"])
            if t == "sum_max":
                nums = [random.randint(-10, 50) for _ in range(6)]
                code = f"nums = {nums}\nprint(sum(nums) - max(nums) - min(nums))"
                ans = str(sum(nums) - max(nums) - min(nums))
                pool.append(_py_code_qd(code, ans, [str(sum(nums)), str(max(nums)), "Xatolik"], 2, None))
            elif t == "even_filter":
                nums = [random.randint(-20, 40) for _ in range(7)]
                code = f"nums = {nums}\nprint([x for x in nums if x % 2 == 0])"
                ans = str([x for x in nums if x % 2 == 0])
                pool.append(_py_code_qd(code, ans, [str(nums), "[]", "Xatolik"], 2, None))
            else:
                keys = random.sample(["a", "b", "c", "d", "e", "f"], k=3)
                vals = [random.randint(1, 9) for _ in range(3)]
                d = {keys[i]: vals[i] for i in range(3)}
                code = f"d = {d}\nprint(len(d), sum(d.values()))"
                ans = f"{len(d)} {sum(d.values())}"
                pool.append(_py_code_qd(code, ans, [str(len(d)), str(sum(d.values())), "Xatolik"], 2, None))

        for _ in range(4200):
            t = random.choice(["strip_title", "fstring_mix", "comp_len", "args_kwargs"])
            if t == "strip_title":
                s = random.choice(["  Hello World  ", "pyTHon rocks", "maktab loyihasi", "  jahonschool  "])
                pad = " " * random.randint(0, 3)
                ss = pad + s + pad
                code = f"s = '{ss}'\nprint(s.strip().title())"
                ans = ss.strip().title()
                pool.append(_py_code_qd(code, ans, [ss, ss.strip(), "Xatolik"], 3, None))
            elif t == "fstring_mix":
                name = random.choice(["Ali", "Olim", "Nodira", "Zarina"])
                a = random.randint(1, 50)
                b = random.randint(1, 50)
                code = f"name='{name}'\na={a}\nb={b}\nprint(f'{name}:{a+b}:{(a*b)%10}')"
                ans = f"{name}:{a+b}:{(a*b)%10}"
                pool.append(_py_code_qd(code, ans, [name, str(a+b), "Xatolik"], 3, None))
            elif t == "comp_len":
                n = random.randint(10, 120)
                m = random.randint(2, 9)
                code = f"print(len([i for i in range({n}) if i % {m} == 0]))"
                ans = str(len([i for i in range(n) if i % m == 0]))
                pool.append(_py_code_qd(code, ans, [str(n//m), str(n), "Xatolik"], 3, None))
            else:
                x, y, z = random.randint(1, 9), random.randint(1, 9), random.randint(1, 9)
                code = "def f(*a, **kw):\n    return sum(a) + len(kw)\nprint(f({}, {}, {}, a=1, b=2))".format(x, y, z)
                ans = str(x + y + z + 2)
                pool.append(_py_code_qd(code, ans, [str(x+y+z), "2", "Xatolik"], 3, None))

    elif grade == 9 and quarter == 1:
        # 8-sinf takror + strings intro
        for _ in range(2600):
            a = random.randint(-30, 50)
            b = random.randint(-30, 50)
            code = f"a={a}\nb={b}\nprint('Ha' if a<b else 'Yo\\'q')"
            ans = "Ha" if a < b else "Yo'q"
            pool.append(_py_code_qd(code, ans, ["Ha", "Yo'q", "Xatolik"], 2, 1))

        for _ in range(2600):
            s = random.choice(["Python", "Dasturlash", "Algoritm"]) + random.choice(["", "  ", "!!!"])
            code = f"s = '{s}'\nprint(s.strip().lower())"
            ans = s.strip().lower()
            pool.append(_py_code_qd(code, ans, [s, s.lower(), "Xatolik"], 2, 3))

        # Hard: string bo‘lish, slicing, count/find va xatoliklar (ko‘p kombinatsiya)
        for _ in range(4200):
            t = random.choice(["split", "slice_step", "count_find", "type_err"])
            if t == "split":
                w1 = random.choice(["python", "maktab", "algoritm", "dastur", "loyiha"])
                w2 = random.choice(["kurs", "dars", "sinov", "amaliyot", "nazorat"])
                w3 = str(random.randint(1, 999))
                sep = random.choice([" ", "  ", "_", "-"])
                s = sep.join([w1, w2, w3])
                code = f"s = '{s}'\nprint(s.split('{sep}'))"
                ans = str(s.split(sep))
                pool.append(_py_code_qd(code, ans, [str(s.split()), "[]", "Xatolik"], 3, 3))
            elif t == "slice_step":
                s = "".join(random.choices("AbcdefGHIjklMNopQRstUVwxYZ", k=random.randint(10, 18)))
                a = random.randint(0, 4)
                b = random.randint(a + 5, len(s))
                step = random.choice([2, 3])
                code = f"s = '{s}'\nprint(s[{a}:{b}:{step}])"
                ans = s[a:b:step]
                pool.append(_py_code_qd(code, ans, [s[a:b], s[::-1], "Xatolik"], 3, 3))
            elif t == "count_find":
                s = "".join(random.choices("abcaBCAB__123", k=random.randint(12, 20)))
                ch = random.choice(["a", "A", "_"])
                code = f"s = '{s}'\nprint(s.count('{ch}'), s.find('{ch}'))"
                ans = f"{s.count(ch)} {s.find(ch)}"
                pool.append(_py_code_qd(code, ans, [str(s.count(ch)), "0 -1", "Xatolik"], 3, 3))
            else:
                a = random.randint(1, 20)
                b = str(random.randint(1, 20))
                code = f"x = {a}\ny = '{b}'\nprint(x + int(y))"
                ans = str(a + int(b))
                pool.append(_py_code_qd(code, ans, [str(a), b, "Xatolik"], 3, 1))

    elif grade == 9 and quarter == 2:
        # shart/sikl takror + string methods chuqurroq
        for _ in range(2400):
            n = random.randint(10, 60)
            code = f"cnt=0\nfor i in range({n}):\n    if i%5==0:\n        cnt+=1\nprint(cnt)"
            ans = str(len([i for i in range(n) if i % 5 == 0]))
            pool.append(_py_code_qd(code, ans, [str(n//5), "0", "Xatolik"], 2, 2))

        for _ in range(2400):
            s = "".join(random.choices("abcABC123_", k=random.randint(8, 14)))
            code = f"s = '{s}'\nprint(s.count('A') + s.count('a'))"
            ans = str(s.count("A") + s.count("a"))
            pool.append(_py_code_qd(code, ans, [str(s.count("A")), str(s.count("a")), "0"], 2, 3))

        for _ in range(2400):
            s = random.choice(["python", "maktab", "dasturlash"])
            t = random.choice(["x", "a", "p"])
            code = f"s = '{s}'\nprint(s.replace('{t}', '{t.upper()}'))"
            ans = s.replace(t, t.upper())
            pool.append(_py_code_qd(code, ans, [s, s.upper(), "Xatolik"], 3, 3))

        for _ in range(4200):
            t = random.choice(["strip_split_join", "formatting", "error_cast", "find_slice"])
            if t == "strip_split_join":
                w = random.choice(["python", "maktab", "algoritm", "dasturlash", "loyiha"])
                n = random.randint(1, 999)
                s = f"  {w}-{n}  "
                code = f"s = '{s}'\nprint(' '.join(s.strip().split('-')))"
                ans = " ".join(s.strip().split("-"))
                pool.append(_py_code_qd(code, ans, [s, s.strip(), "Xatolik"], 3, 3))
            elif t == "formatting":
                a = random.randint(1, 50)
                b = random.randint(1, 50)
                code = f"a={a}\nb={b}\nprint(f'{a}+{b}={a+b}')"
                ans = f"{a}+{b}={a+b}"
                pool.append(_py_code_qd(code, ans, [str(a+b), f"{a}+{b}", "Xatolik"], 3, 2))
            elif t == "error_cast":
                x = random.randint(1, 30)
                s = random.choice(["10", "20", "abc", "3.14"])
                code = f"x={x}\ns='{s}'\nprint(x + int(s))"
                if s.isdigit():
                    ans = str(x + int(s))
                    wrongs = [str(x), s, "Xatolik"]
                else:
                    ans = "ValueError"
                    wrongs = ["TypeError", "Natija chiqadi", "0"]
                pool.append(_py_code_qd(code, ans, wrongs, 3, 2))
            else:
                s = "".join(random.choices("abcaBC__XYZ123", k=random.randint(14, 22)))
                ch = random.choice(["a", "B", "_", "1"])
                code = f"s = '{s}'\ni = s.find('{ch}')\nprint(i, s[i:i+3])"
                i = s.find(ch)
                ans = f"{i} {s[i:i+3]}" if i != -1 else "-1 "
                pool.append(_py_code_qd(code, ans, [str(i), "0", "Xatolik"], 3, 3))

    elif grade == 9 and quarter == 3:
        # list/tuple/set/dict, methods, ATM, algorithm, functions+modules, *args/**kwargs, school project
        for _ in range(2600):
            lst = [random.randint(-10, 40) for _ in range(6)]
            code = f"L = {lst}\nL2 = sorted(set(L))\nprint(L2[:3])"
            ans = str(sorted(set(lst))[:3])
            pool.append(_py_code_qd(code, ans, [str(lst[:3]), "[]", "Xatolik"], 2, 4))

        for _ in range(2600):
            d = {"a": random.randint(1, 9), "b": random.randint(10, 19), "c": random.randint(20, 29)}
            k = random.choice(["a", "b", "c", "d"])
            code = f"d = {d}\nprint(d.get('{k}', 0))"
            ans = str(d.get(k, 0))
            pool.append(_py_code_qd(code, ans, [str(0), str(sum(d.values())), "KeyError"], 2, 5))

        for _ in range(2200):
            bal = random.randint(100, 900) * 1000
            wd = random.randint(50, 950) * 1000
            fee = random.choice([0, 1000, 2000])
            code = (
                f"balans={bal}\nyechish={wd}\nkomissiya={fee}\n"
                "if yechish + komissiya > balans:\n"
                "    print('Rad')\n"
                "else:\n"
                "    print(balans - yechish - komissiya)"
            )
            ans = "Rad" if wd + fee > bal else str(bal - wd - fee)
            pool.append(_py_code_qd(code, ans, ["0", str(bal), "Xatolik"], 3, 6))

        for _ in range(2200):
            a = random.randint(10, 200)
            b = random.randint(2, 20)
            code = f"def f(x, y):\n    return x//y, x%y\nprint(f({a}, {b}))"
            ans = str((a // b, a % b))
            pool.append(_py_code_qd(code, ans, [str(a / b), str((a % b, a // b)), "Xatolik"], 3, 10))

        for _ in range(2200):
            x, y, z = random.randint(1, 9), random.randint(1, 9), random.randint(1, 9)
            code = "def s(*a):\n    return sum(a)\nprint(s({}, {}, {}))".format(x, y, z)
            ans = str(x + y + z)
            pool.append(_py_code_qd(code, ans, [str(x*y*z), str(x+y), "Xatolik"], 2, 11))

    else:  # grade == 9 and quarter == 4
        # files + OOP + inheritance + projects
        for _ in range(3200):
            text = "".join(random.choices("abdefghijklmno pqrs tuvxyz", k=random.randint(5, 20))).strip()
            code = "data = '{}\\n'.strip()\\nprint(len(data))".format(text)
            ans = str(len(text))
            pool.append(_py_code_qd(code, ans, [str(len(text)+1), "0", "Xatolik"], 2, 13))

        for _ in range(2600):
            # medium: "with" va rejimlar bo‘yicha tushuncha
            q = random.choice(
                [
                    ("Faylga oxiridan qo‘shib yozish (append) rejimi qaysi?", "a", ["r", "w", "x"]),
                    ("Faylni xavfsiz yopilishini kafolatlaydigan operator qaysi?", "with", ["open", "close", "exit"]),
                    ("Faylni o‘qish rejimi qaysi?", "r", ["w", "a", "rw"]),
                    ("Faylni yaratib, eski ma'lumotni o‘chirib yozish rejimi qaysi?", "w", ["r", "a", "x"]),
                ]
            )
            pool.append(QItem(text=q[0], answer=q[1], wrongs=q[2], difficulty=2, lesson=13))

        for _ in range(3600):
            name = random.choice(["Ali", "Olim", "Nodira", "Zarina", "Sardor", "Malika", "Sabrina", "Jasur"])
            age = random.randint(10, 45)
            grade = random.randint(7, 11)
            cls = random.choice(["A", "B", "C"])
            code = (
                "class O:\n"
                "    def __init__(self, name, age, grade, cls):\n"
                "        self.name=name\n"
                "        self.age=age\n"
                "        self.grade=grade\n"
                "        self.cls=cls\n"
                "    def info(self):\n"
                "        return f\"{self.name}-{self.age}-{self.grade}{self.cls}\"\n"
                f"o=O('{name}', {age}, {grade}, '{cls}')\n"
                "print(o.info())"
            )
            ans = f"{name}-{age}-{grade}{cls}"
            pool.append(_py_code_qd(code, ans, [name, str(age), "Xatolik"], 2, 17))

        for _ in range(2400):
            base = random.randint(2, 20)
            extra = random.randint(1, 10)
            code = (
                "class A:\n"
                "    def __init__(self, x):\n"
                "        self.x=x\n"
                "    def v(self):\n"
                "        return self.x\n"
                "class B(A):\n"
                "    def v(self):\n"
                "        return self.x + {}\n"
                f"b=B({base})\n"
                "print(b.v())"
            ).format(extra)
            ans = str(base + extra)
            pool.append(_py_code_qd(code, ans, [str(base), str(extra), "Xatolik"], 3, 20))

        for _ in range(3200):
            t = random.choice(["inherit2", "method_super", "file_modes", "class_list"])
            if t == "inherit2":
                x = random.randint(1, 50)
                a = random.randint(1, 20)
                b = random.randint(1, 20)
                code = (
                    "class A:\n"
                    "    def __init__(self, x):\n"
                    "        self.x=x\n"
                    "    def v(self):\n"
                    "        return self.x\n"
                    "class B(A):\n"
                    "    def v(self):\n"
                    "        return self.x + {}\n"
                    "class C(B):\n"
                    "    def v(self):\n"
                    "        return self.x + {} + {}\n"
                    f"c=C({x})\n"
                    "print(c.v())"
                ).format(a, a, b)
                ans = str(x + a + b)
                pool.append(_py_code_qd(code, ans, [str(x+a), str(x+b), "Xatolik"], 3, 20))
            elif t == "method_super":
                base = random.randint(1, 30)
                inc = random.randint(1, 15)
                code = (
                    "class A:\n"
                    "    def f(self, x):\n"
                    "        return x + 1\n"
                    "class B(A):\n"
                    "    def f(self, x):\n"
                    "        return super().f(x) + {}\n"
                    f"b=B()\nprint(b.f({base}))"
                ).format(inc)
                ans = str((base + 1) + inc)
                pool.append(_py_code_qd(code, ans, [str(base+inc), str(base+1), "Xatolik"], 3, 20))
            elif t == "file_modes":
                mode = random.choice(["r", "w", "a"])
                q = (
                    "Fayl bilan ishlashda qaysi rejim faylni yaratib/yangilab ichidagi eski ma'lumotni o'chirib yozadi?"
                )
                pool.append(
                    QItem(
                        text=q,
                        answer="w",
                        wrongs=["r", "a", "x"],
                        difficulty=3,
                        lesson=13,
                    )
                )
            else:
                ages = [random.randint(10, 30) for _ in range(3)]
                code = (
                    "class O:\n"
                    "    def __init__(self, age):\n"
                    "        self.age=age\n"
                    "L=[O({}), O({}), O({})]\n"
                    "print(sum(o.age for o in L))"
                ).format(ages[0], ages[1], ages[2])
                ans = str(sum(ages))
                pool.append(_py_code_qd(code, ans, [str(max(ages)), str(min(ages)), "Xatolik"], 3, 17))

    random.shuffle(pool)
    return pool


# ------------------ DB rebuild orchestration ------------------

def get_or_create_subject(name: str, grades: str, protected: bool = True) -> Subject:
    subject = Subject.query.filter_by(name=name).first()
    if not subject:
        subject = Subject(name=name, grades=grades, is_protected=protected)
        db.session.add(subject)
        db.session.commit()
        return subject

    subject.grades = grades
    subject.is_protected = protected
    db.session.commit()
    return subject


def purge_subject_questions(subject_id: int, grades: list[int]) -> None:
    # Remove control work link rows first
    db.session.execute(
        db.text(
            "DELETE FROM control_work_questions WHERE control_work_id IN (SELECT id FROM control_work WHERE subject_id = :sid)"
        ),
        {"sid": subject_id},
    )
    ControlWork.query.filter(ControlWork.subject_id == subject_id, ControlWork.grade.in_(grades)).delete(
        synchronize_session=False
    )
    Question.query.filter(Question.subject_id == subject_id, Question.grade.in_(grades)).delete(synchronize_session=False)
    db.session.commit()


def ensure_control_work(subject_id: int, grade: int, quarter: int, title: str) -> ControlWork:
    cw = ControlWork.query.filter_by(subject_id=subject_id, grade=grade, quarter=quarter, title=title).first()
    if not cw:
        cw = ControlWork(title=title, subject_id=subject_id, grade=grade, quarter=quarter, time_limit=40, is_active=True)
        db.session.add(cw)
        db.session.flush()
    else:
        cw.is_active = True
        cw.time_limit = cw.time_limit or 40
        cw.questions = []
        db.session.flush()
    return cw


def build_subject(subject: Subject, grades: list[int], pool_fn) -> None:
    factory = QuestionFactory()
    new_questions: list[Question] = []
    cw_to_qs: dict[tuple[int, int], list[Question]] = {}

    balanced = (subject.name == "Python")

    for g in grades:
        for q in [1, 2, 3, 4]:
            pool = pool_fn(g, q)
            # Balanced targets so student selection can pick 10 medium + 5 hard reliably.
            # Only required for Python (7–9). Other subjects can be filled without difficulty split.
            practice_medium_target = 120 if balanced else PRACTICE_PER_QUARTER
            practice_hard_target = PRACTICE_PER_QUARTER - practice_medium_target
            control_medium_target = 50 if balanced else CONTROL_PER_QUARTER
            control_hard_target = CONTROL_PER_QUARTER - control_medium_target

            medium_items = [i for i in pool if (i.difficulty or 2) == 2]
            hard_items = [i for i in pool if (i.difficulty or 2) >= 3]
            if not balanced:
                # For non-Python, treat everything as medium and do not require hard bucket
                medium_items = pool
                hard_items = []

            def _fill(items: list[QItem], target: int) -> list[Question]:
                out: list[Question] = []
                if not items or target <= 0:
                    return out

                attempts = 0
                max_attempts = max(20000, target * 2000)
                idx = 0
                buf = items[:]
                random.shuffle(buf)

                while len(out) < target and attempts < max_attempts:
                    attempts += 1
                    if idx >= len(buf):
                        random.shuffle(buf)
                        idx = 0
                    item = buf[idx]
                    idx += 1
                    qq = factory.build(subject.id, g, q, item)
                    if qq:
                        out.append(qq)
                return out

            practice: list[Question] = []
            control: list[Question] = []

            practice.extend(_fill(medium_items, practice_medium_target))
            practice.extend(_fill(hard_items, practice_hard_target))
            control.extend(_fill(medium_items, control_medium_target))
            control.extend(_fill(hard_items, control_hard_target))

            if len(practice) != PRACTICE_PER_QUARTER or len(control) != CONTROL_PER_QUARTER:
                raise RuntimeError(
                    f"Insufficient unique questions for {subject.name} G{g} Q{q}: practice={len(practice)} control={len(control)}"
                )

            new_questions.extend(practice)
            new_questions.extend(control)
            cw_to_qs[(g, q)] = control

    # Save questions in chunks
    chunk = 500
    for i in range(0, len(new_questions), chunk):
        db.session.bulk_save_objects(new_questions[i : i + chunk])
        db.session.commit()

    # Now fetch inserted IDs for control mapping (bulk_save doesn't guarantee in-memory IDs)
    # We'll re-query by (subject_id, grade, quarter) and separate by control marker using question_text matching.
    for (g, q), control_objs in cw_to_qs.items():
        title = f"{g}-sinf {q}-chorak Nazorat ishi"
        cw = ensure_control_work(subject.id, g, q, title)

        control_texts = [_norm_key(x.question_text) for x in control_objs]
        rows = (
            Question.query.filter_by(subject_id=subject.id, grade=g, quarter=q)
            .all()
        )
        # Match control questions by text normalization
        control_set = set(control_texts)
        attach = [r for r in rows if _norm_key(r.question_text) in control_set]

        if len(attach) != CONTROL_PER_QUARTER:
            # Fallback: attach any 100 from this quarter, but keep count strict
            attach = random.sample(rows, CONTROL_PER_QUARTER)

        cw.questions.extend(attach)
        db.session.commit()


def main() -> None:
    app = create_app()
    with app.app_context():
        # Subjects to enforce per requirements
        informatics = get_or_create_subject("Informatika", "5,6", protected=True)
        python = get_or_create_subject("Python", "7,8,9", protected=True)

        # Purge and rebuild only these grade bands
        purge_subject_questions(informatics.id, [5, 6, 7, 8, 9])
        purge_subject_questions(python.id, [7, 8, 9])

        build_subject(informatics, [5, 6], informatics_pool)
        build_subject(python, [7, 8, 9], python_pool)

        # Extra safety: remove Informatika questions for 7-9 if any existed
        Question.query.filter(Question.subject_id == informatics.id, Question.grade.in_([7, 8, 9])).delete(
            synchronize_session=False
        )
        db.session.commit()

        print("DONE: Question bank rebuilt for Informatika (5-6) and Python (7-9).")


if __name__ == "__main__":
    random.seed()  # system entropy
    main()

