# pyright: reportCallIssue=false, reportAttributeAccessIssue=false
"""
Yangi avlod savollar bazasi generatori (Informatika 5-6, Python 7-9).

Asosiy farqlar (v1 -> v2):
  * Har bir parametrik shablon EN KO'PI bilan 10 ta variant qaytaradi
    (sonlari/parametrlari farqlanuvchi takrorlar 5-10 dan oshmaydi).
  * Har bir sinf-chorak uchun 40-60 ta yagona kontseptual mavzu × 4 ta
    so'roq qoliplari bilan birikib, 160+ noyob nazariy savollar beradi.
  * Yana 15-25 parametrik shablon × 8-10 variant ~ 150 amaliy savol.
  * Jami 320+ noyob savol — script 300 tasini saqlaydi (200 amaliyot
    + 100 nazorat ishi).
  * Mavzular o'quv dasturiga (lesson) muvofiq belgilanadi.
"""
from __future__ import annotations

import sys
import os
import random
from dataclasses import dataclass
from typing import Callable

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app  # noqa: E402
from extensions import db  # noqa: E402
from models import Subject, Question, ControlWork  # noqa: E402


PRACTICE_PER_QUARTER = 200
CONTROL_PER_QUARTER = 100
MAX_VARIANTS_PER_TEMPLATE = 10
TARGET_POOL_MIN = 320


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _norm_key(text: str) -> str:
    return " ".join((text or "").lower().split())


def _shuffle_options(answer: str, wrongs: list[str]) -> tuple[list[str], str]:
    options = [str(answer)] + [str(w) for w in wrongs if str(w) != str(answer)]
    seen = set()
    uniq: list[str] = []
    for o in options:
        if o not in seen:
            uniq.append(o)
            seen.add(o)
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
    difficulty: int = 2  # 1=easy, 2=medium, 3=hard
    lesson: int | None = None


class QuestionFactory:
    """Bir grade-quarter ichida question_text bo'yicha dedup qiladi."""

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


def _conceptual(concept: str, definition: str, wrongs: list[str],
                lesson: int | None = None, difficulty: int = 2) -> list[QItem]:
    """Bitta tushuncha uchun 4 xil savol qolipi qaytaradi."""
    templates = [
        f"'{concept}' tushunchasining ta'rifi qaysi?",
        f"'{concept}' nima vazifani bajaradi?",
        f"Quyidagilardan qaysi biri '{concept}' tushunchasiga to‘g‘ri keladi?",
        f"'{concept}' so‘zining mazmuni qaysi?",
    ]
    return [QItem(text=t, answer=definition, wrongs=list(wrongs),
                  difficulty=difficulty, lesson=lesson) for t in templates]


def _capped(gen_fn: Callable[[], QItem], max_count: int = MAX_VARIANTS_PER_TEMPLATE,
            attempts_per_item: int = 40) -> list[QItem]:
    """gen_fn() ni chaqirib, max_count ta UNIKAL (text bo'yicha) item to'plab qaytaradi."""
    seen: set[str] = set()
    out: list[QItem] = []
    a = 0
    while len(out) < max_count and a < max_count * attempts_per_item:
        a += 1
        try:
            item = gen_fn()
        except Exception:
            continue
        if item.text in seen:
            continue
        seen.add(item.text)
        out.append(item)
    return out


# Many wrong-answer pools used across topics
DEFAULT_WRONGS_DEVICE = ["Internetga ulanish moslamasi", "Antivirus dasturi", "Operatsion tizim turi"]
DEFAULT_WRONGS_SOFT = ["Texnik qurilma", "Kabel turi", "Klaviatura tugmasi"]


# ─── INFORMATIKA — 5-sinf 1-chorak ───────────────────────────────────────────
# Mavzu: Kompyuter qurilmalari, axborot, fayl/papka, dastlabki tushunchalar.

INF_5_Q1_CONCEPTS: list[tuple[str, str, list[str], int]] = [
    ("Kompyuter", "Axborotni qabul qilish, qayta ishlash va saqlash uchun mo‘ljallangan elektron qurilma",
     ["Faqat o‘yin uchun mo‘ljallangan asbob", "Maxsus televizor", "Faqat hisoblash mashinasi"], 1),
    ("Hardware (apparat ta'minoti)", "Kompyuterning fizik qismlari (qurilmalar)",
     ["Kompyuter dasturlari", "Fayl turi", "Internet manzili"], 1),
    ("Software (dasturiy ta'minot)", "Kompyuterda ishlovchi dasturlar majmuasi",
     ["Kompyuterning fizik qismi", "Sichqoncha turi", "Ekran o‘lchami"], 1),
    ("CPU (protsessor)", "Buyruqlarni bajaradigan markaziy qurilma",
     ["Doimiy xotira", "Kirish qurilmasi", "Tarmoq kabeli"], 2),
    ("RAM (operativ xotira)", "Dastur ishlayotganda vaqtinchalik ma'lumot saqlovchi xotira",
     ["Doimiy ma'lumot saqlovchi disk", "Internet kabeli", "Klaviatura turi"], 2),
    ("ROM (doimiy xotira)", "Faqat o‘qish uchun mo‘ljallangan, o‘chmaydigan xotira",
     ["Tezkor xotira", "Tarmoq kartasi", "Sichqoncha"], 2),
    ("HDD (qattiq disk)", "Magnit asosida ma'lumot doimiy saqlanadigan qurilma",
     ["Operativ xotira", "Monitor", "Tugmacha"], 2),
    ("SSD", "Tez ishlaydigan, harakatlanuvchi qismsiz doimiy xotira",
     ["RAM turi", "Kabel turi", "Brauzer"], 2),
    ("Monitor", "Tasvirni ko‘rsatuvchi chiqish qurilmasi",
     ["Klavyaturasi", "Sichqoncha", "Disk"], 1),
    ("Klaviatura", "Matn va buyruq kiritish uchun ishlatiladigan kirish qurilmasi",
     ["Chiqish qurilmasi", "Xotira qurilmasi", "Operatsion tizim"], 1),
    ("Sichqoncha (mouse)", "Ekranda kursorni boshqaruvchi kirish qurilmasi",
     ["Chop etish qurilmasi", "Disk turi", "Internet portali"], 1),
    ("Printer", "Hujjatlarni qog‘ozga chop etuvchi chiqish qurilmasi",
     ["Internetga ulanish moslamasi", "Hisoblash blogi", "Skaner turi"], 2),
    ("Skaner", "Qog‘ozdagi tasvirni raqamli ko‘rinishga o‘tkazuvchi qurilma",
     ["Chop etuvchi qurilma", "Tovush kuchaytirgich", "Ovoz yozuvchi"], 2),
    ("Karnay (speaker)", "Ovozni eshittiruvchi chiqish qurilmasi",
     ["Ovoz yozuvchi qurilma", "Klaviatura", "Diskni o‘qiydigan qurilma"], 2),
    ("Mikrofon", "Ovozni kompyuterga kiritish uchun qurilma",
     ["Ovoz chiqaruvchi", "Disk", "Tugmacha"], 2),
    ("Veb-kamera", "Real vaqt tasvirini kompyuterga uzatuvchi qurilma",
     ["Faqat fotoapparat", "Disk yozuvchi", "Mikrofon"], 2),
    ("USB", "Universal ketma-ket shina — qurilmalarni kompyuterga ulash standarti",
     ["Faqat zaryadlash kabeli", "Internet protokoli", "Hisoblash xotirasi"], 2),
    ("Flesh xotira (USB flash)", "Olib yuriluvchi kichik doimiy xotira qurilmasi",
     ["Operativ xotira", "Klaviatura", "Monitor"], 2),
    ("Bit", "Axborotning eng kichik birligi — 0 yoki 1",
     ["Bayt", "Kilobayt", "Megabayt"], 3),
    ("Bayt", "8 bitdan iborat axborot birligi",
     ["1 bit", "1 KB", "100 bit"], 3),
    ("Kilobayt (KB)", "1024 bayt — kichik fayllar uchun o‘lchov",
     ["8 bayt", "1024 MB", "1 GB"], 3),
    ("Megabayt (MB)", "1024 KB — rasm yoki musiqa hajmi uchun o‘lchov",
     ["1024 GB", "100 KB", "8 bit"], 3),
    ("Gigabayt (GB)", "1024 MB — film yoki katta fayllar hajmi uchun o‘lchov",
     ["1024 KB", "100 MB", "8 bayt"], 3),
    ("Terabayt (TB)", "1024 GB — eng katta hajmlardan biri",
     ["1024 KB", "100 MB", "10 GB"], 3),
    ("Operatsion tizim (OT)", "Kompyuter resurslarini boshqaradigan asosiy dastur",
     ["Veb-brauzer", "Antivirus", "Faqat o‘yin"], 4),
    ("Windows", "Microsoft kompaniyasining mashhur operatsion tizimi",
     ["Faqat brauzer", "Matn muharriri", "Antivirus"], 4),
    ("Linux", "Ochiq kodli operatsion tizim",
     ["Office paketi", "Faqat o‘yin", "Faqat ma'lumot bazasi"], 4),
    ("macOS", "Apple kompaniyasining operatsion tizimi",
     ["Microsoft mahsuloti", "Linux turi", "Brauzer"], 4),
    ("Fayl", "Ma'lumotlar saqlanadigan nomli birlik",
     ["Faqat papka", "Klaviatura tugmasi", "Disk turi"], 5),
    ("Papka (folder)", "Fayllarni tartibli saqlash uchun konteyner",
     ["Faqat rasm", "Operatsion tizim", "Tarmoq turi"], 5),
    ("Fayl kengaytmasi", "Fayl turini ko‘rsatuvchi nuqtadan keyingi qism",
     ["Fayl hajmi", "Papka nomi", "Internet tezligi"], 5),
    (".docx", "Microsoft Word matn hujjati kengaytmasi",
     ["Rasm formati", "Audio formati", "Video formati"], 5),
    (".txt", "Oddiy matn fayli kengaytmasi",
     ["Rasm formati", "Excel jadvali", "Dastur"], 5),
    (".jpg", "Suratlar uchun keng ishlatiladigan rasm formati",
     ["Matn formati", "Video formati", "Operatsion tizim"], 5),
    (".png", "Shaffof fonni qo‘llab-quvvatlovchi rasm formati",
     ["Audio fayl", "Word hujjati", "Skript"], 5),
    (".mp3", "Musiqa va ovoz fayllari uchun keng ishlatiladigan format",
     ["Rasm formati", "Matn formati", "Excel formati"], 5),
    (".mp4", "Video fayllar uchun keng tarqalgan format",
     ["Audio formati", "Word hujjati", "Brauzer"], 5),
    (".pdf", "Sahifa ko‘rinishini saqlovchi hujjat formati",
     ["Audio format", "Excel format", "Brauzer"], 5),
    ("Yorliq (shortcut)", "Faylga tezkor ishora qiladigan piktogramma",
     ["Asl fayl", "Operatsion tizim", "Klaviatura tugmasi"], 5),
    ("Ish stoli (Desktop)", "Operatsion tizim ishga tushgach ko‘rinadigan asosiy ekran",
     ["Brauzer oynasi", "Faqat fayl ro‘yxati", "Word hujjati"], 4),
    ("Savatcha (Recycle Bin)", "O‘chirilgan fayllar vaqtincha saqlanadigan joy",
     ["Doimiy saqlash xotirasi", "Klaviatura tugmasi", "Brauzer"], 4),
    ("Sichqoncha kursori", "Ekrandagi sichqoncha holatini ko‘rsatuvchi belgi",
     ["Faqat klaviatura tugmasi", "Disk indikator", "Internet kabeli"], 1),
    ("Axborot", "Inson uchun foydali ma'noga ega ma'lumot",
     ["Faqat raqam", "Faqat tovush", "Faqat rasm"], 1),
    ("Ma'lumot", "Bitta-bitta belgi yoki son ko‘rinishidagi xom holatdagi axborot",
     ["Tayyor xulosa", "Tugatilgan tahlil", "Diagramma"], 1),
    ("1-avlod kompyuterlari", "Vakuumli lampalardan iborat bo‘lgan dastlabki kompyuterlar",
     ["Tranzistorlardan iborat", "Mikroprotsessorli", "Sun'iy intellektli"], 6),
    ("2-avlod kompyuterlari", "Tranzistorlar asosida ishlagan kompyuterlar",
     ["Mikrosxemalardan iborat", "Vakuumli lampalardan", "Kvant qurilma"], 6),
    ("3-avlod kompyuterlari", "Integral mikrosxemalardan iborat kompyuterlar",
     ["Vakuumli lampalardan iborat", "Sun'iy intellektli", "Kvant kompyuter"], 6),
    ("4-avlod kompyuterlari", "Mikroprotsessorlar asosida ishlovchi kompyuterlar",
     ["Vakuumli lampalardan iborat", "Tranzistorlardan iborat", "Faqat o‘yin uchun"], 6),
    ("Charles Babbage", "Birinchi mexanik hisoblash mashinasi g‘oyasini ilgari surgan olim",
     ["Birinchi dasturchi ayol", "Microsoft asoschisi", "Apple asoschisi"], 6),
    ("Ada Lovelace", "Tarixda birinchi dasturchi sifatida tanilgan ayol",
     ["Birinchi kompyuter ixtirochisi", "Microsoft asoschisi", "Apple asoschisi"], 6),
]


def _info5_q1_pool() -> list[QItem]:
    pool: list[QItem] = []
    for c, d, w, l in INF_5_Q1_CONCEPTS:
        pool += _conceptual(c, d, w, lesson=l)

    # Parametric: arifmetik (cheklangan, max 10)
    def t_add():
        a = random.randint(11, 89); b = random.randint(11, 99)
        return QItem(text=f"Quyidagi ifoda natijasini hisoblang:\n\n{a} + {b}",
                     answer=str(a + b),
                     wrongs=[str(a + b + 1), str(a + b - 1), str(abs(a - b))],
                     difficulty=1)

    def t_sub():
        a = random.randint(50, 99); b = random.randint(11, 49)
        return QItem(text=f"Quyidagi ifoda natijasini hisoblang:\n\n{a} - {b}",
                     answer=str(a - b),
                     wrongs=[str(a - b + 1), str(a - b - 1), str(b - a)],
                     difficulty=1)

    def t_mul():
        a = random.randint(11, 19); b = random.randint(2, 9)
        return QItem(text=f"Quyidagi ifoda natijasini hisoblang:\n\n{a} * {b}",
                     answer=str(a * b),
                     wrongs=[str(a + b), str(a * b + 1), str(a * (b - 1))],
                     difficulty=2)

    def t_kb_to_b():
        kb = random.randint(2, 8)
        return QItem(text=f"{kb} KB necha baytga teng?",
                     answer=str(kb * 1024),
                     wrongs=[str(kb * 1000), str(kb * 8), str(kb * 100)],
                     difficulty=2, lesson=3)

    def t_mb_to_kb():
        mb = random.randint(2, 8)
        return QItem(text=f"{mb} MB taxminan necha KB ga teng?",
                     answer=str(mb * 1024),
                     wrongs=[str(mb * 1000), str(mb), str(mb * 8)],
                     difficulty=2, lesson=3)

    def t_byte_to_bit():
        b = random.randint(2, 9)
        return QItem(text=f"{b} bayt necha bitga teng?",
                     answer=str(b * 8),
                     wrongs=[str(b), str(b * 10), str(b + 8)],
                     difficulty=2, lesson=3)

    def t_extension_match():
        cases = [
            ("rasm", ".jpg", [".docx", ".mp3", ".txt"]),
            ("matn hujjati", ".docx", [".jpg", ".mp3", ".mp4"]),
            ("musiqa", ".mp3", [".docx", ".jpg", ".pdf"]),
            ("video", ".mp4", [".jpg", ".docx", ".txt"]),
            ("oddiy matn", ".txt", [".jpg", ".mp4", ".mp3"]),
        ]
        case, ans, wrongs = random.choice(cases)
        fname = random.choice(["maktab", "darslik", "kitob", "rasm1", "uy_vazifasi"])
        return QItem(text=f"`{fname}` faylini {case} sifatida saqlash kerak. Qaysi kengaytma to‘g‘ri?",
                     answer=ans, wrongs=list(wrongs), difficulty=2, lesson=5)

    def t_input_output():
        cases = [
            ("Klaviatura", "Kirish qurilmasi", ["Chiqish qurilmasi", "Xotira", "Operatsion tizim"]),
            ("Monitor", "Chiqish qurilmasi", ["Kirish qurilmasi", "Xotira", "Tarmoq qurilmasi"]),
            ("Sichqoncha", "Kirish qurilmasi", ["Chiqish qurilmasi", "Xotira", "Tarmoq"]),
            ("Printer", "Chiqish qurilmasi", ["Kirish qurilmasi", "Xotira", "Operatsion tizim"]),
            ("Skaner", "Kirish qurilmasi", ["Chiqish qurilmasi", "Xotira", "Operatsion tizim"]),
            ("Karnay", "Chiqish qurilmasi", ["Kirish qurilmasi", "Xotira", "Operatsion tizim"]),
            ("Mikrofon", "Kirish qurilmasi", ["Chiqish qurilmasi", "Xotira", "Operatsion tizim"]),
            ("Veb-kamera", "Kirish qurilmasi", ["Chiqish qurilmasi", "Xotira", "Operatsion tizim"]),
        ]
        dev, ans, wrongs = random.choice(cases)
        return QItem(text=f"`{dev}` qaysi turdagi qurilmaga kiradi?",
                     answer=ans, wrongs=list(wrongs), difficulty=2, lesson=2)

    pool += _capped(t_add)
    pool += _capped(t_sub)
    pool += _capped(t_mul)
    pool += _capped(t_kb_to_b)
    pool += _capped(t_mb_to_kb)
    pool += _capped(t_byte_to_bit)
    pool += _capped(t_extension_match)
    pool += _capped(t_input_output)

    # Standalone (yana noyob savollar)
    discrete = [
        QItem("Kompyuterning miyasi deb qaysi qurilma yuritiladi?", "CPU (protsessor)",
              ["RAM", "HDD", "Monitor"], 2, 2),
        QItem("Internetga simli ulanish uchun ishlatiladigan port qaysi?", "Ethernet (LAN) porti",
              ["USB-C porti", "HDMI porti", "AUX porti"], 2, 2),
        QItem("Kompyuter o‘chgach ma'lumot qayerda saqlanib qoladi?", "HDD/SSD da",
              ["RAM da", "Monitorda", "Klaviaturada"], 2, 2),
        QItem("Kompyuterni ishga tushirish jarayoni nima deb ataladi?", "Yuklanish (boot)",
              ["Yopilish", "O‘chirish", "Saqlash"], 2, 4),
        QItem("Faylni vaqtincha xotirada saqlovchi xotira qaysi?", "RAM",
              ["HDD", "ROM", "Flesh xotira"], 2, 2),
        QItem("Kompyuter klaviaturasidagi 'Enter' tugmasi nima vazifasini bajaradi?",
              "Buyruq yoki yangi qatorga o‘tishni tasdiqlaydi",
              ["Faqat o‘chiradi", "Faqat saqlaydi", "Faqat chop etadi"], 1, 1),
        QItem("Kompyuter klaviaturasidagi 'Esc' tugmasi nima uchun ishlatiladi?",
              "Amaldagi amalni bekor qilish",
              ["Faylni saqlash", "Faylni nusxalash", "Yangi hujjat ochish"], 2, 1),
        QItem("Kompyuter klaviaturasidagi 'Backspace' tugmasi nima qiladi?",
              "Kursordan oldingi belgini o‘chiradi",
              ["Yangi qatorga o‘tadi", "Faylni yopadi", "Brauzerni ochadi"], 1, 1),
        QItem("Kompyuter klaviaturasidagi 'Caps Lock' tugmasi qanday vazifani bajaradi?",
              "Bosh harflar rejimini yoqadi/o‘chiradi",
              ["Faqat raqam yozadi", "Brauzerni ochadi", "Faylni saqlaydi"], 2, 1),
        QItem("Kompyuter klaviaturasidagi 'Shift' tugmasi nimaga xizmat qiladi?",
              "Vaqtinchalik bosh harf yoki ikkinchi belgini chiqaradi",
              ["Faqat o‘chiradi", "Faqat saqlaydi", "Faqat yopadi"], 2, 1),
        QItem("Kompyuter klaviaturasidagi 'Tab' tugmasi nimaga ishlatiladi?",
              "Bo‘sh joy (chekinish) qo‘yadi yoki keyingi maydonga o‘tadi",
              ["Faylni nusxalaydi", "Brauzerni ochadi", "Tovushni o‘chiradi"], 2, 1),
        QItem("Faylni ochish uchun odatda sichqonchaning qaysi tugmasini bosish kerak?",
              "Chap tugmasini ikki marta",
              ["O‘ng tugmasini bir marta", "O‘rtadagi g‘ildirakni", "Hech qanday tugmani"], 1, 1),
        QItem("Sichqonchani o‘ng tugmasini bosganda nima ochiladi?", "Kontekst (qo‘shimcha) menyu",
              ["Brauzer", "Word hujjati", "Hech narsa"], 2, 1),
        QItem("Faylni doimiy o‘chirish uchun qaysi tugmalar birikmasi ishlatiladi?", "Shift + Delete",
              ["Ctrl + S", "Alt + F4", "Ctrl + N"], 3, 4),
        QItem("Belgilangan qurilma 'Plug and Play' tushunchasi nimani anglatadi?",
              "Ulagandan so‘ng o‘zi tanilib, ishga tayyor bo‘ladi",
              ["Doim qo‘l bilan o‘rnatish kerak", "Faqat zaryadlash kerak", "Internet talab qiladi"], 3, 2),
        QItem("Quyidagilardan qaysi biri kompyuter virusining belgisi emas?",
              "Kompyuter avvalgidan barqarorroq ishlaydi",
              ["Kompyuter sekinlashadi", "Notanish fayllar paydo bo‘ladi",
               "Reklama oynalari ko‘payadi"], 3, 4),
        QItem("Quyidagilardan qaysi biri RAM xususiyati emas?",
              "Kompyuter o‘chgach ham ma'lumot saqlanadi",
              ["Tezkor ishlaydi", "Vaqtinchalik xotira", "Operativ xotira"], 3, 2),
        QItem("HDD va SSD orasidagi asosiy farq nima?",
              "SSD harakatlanuvchi qismsiz, tezroq ishlaydi",
              ["HDD doim tezroq ishlaydi", "SSD ko‘proq joy oladi",
               "Ular butunlay bir xil"], 3, 2),
        QItem("Kompyuter avlodlari qaysi mezon bo‘yicha tasniflanadi?",
              "Asosiy elektron elementlari (lampa, tranzistor, mikrosxema, mikroprotsessor)",
              ["Kompyuter rangi", "Klaviatura turi", "Sichqoncha shakli"], 3, 6),
        QItem("Birinchi dasturchi sifatida tarixga kim kirgan?", "Ada Lovelace",
              ["Charles Babbage", "Bill Gates", "Steve Jobs"], 2, 6),
    ]
    pool += discrete

    random.shuffle(pool)
    return pool


# ─── INFORMATIKA — 5-sinf 2-chorak ───────────────────────────────────────────
# Mavzu: Paint, rasm chizish, rasm formatlari, asboblar.

INF_5_Q2_CONCEPTS = [
    ("Paint", "Microsoft Windowsdagi oddiy rasm chizish va tahrirlash dasturi",
     ["Matn muharriri", "Brauzer", "Antivirus"], 1),
    ("Tuval (Canvas)", "Paintda rasm chiziladigan ish maydoni",
     ["Klaviatura tugmasi", "Sichqoncha tugmasi", "Brauzer oynasi"], 1),
    ("Asboblar paneli", "Paintdagi asboblar (qalam, cho‘tka va h.k.) joylashgan panel",
     ["Internet manzil paneli", "Disk indikatori", "Brauzer paneli"], 2),
    ("Ranglar paneli", "Rasmga rang tanlash uchun mavjud ranglar to‘plami",
     ["Disk hajmi indikatori", "Internet tezligi", "Klaviatura tilini ko‘rsatkichi"], 2),
    ("Qalam (Pencil)", "Yupqa, aniq chiziq chizish asbobi",
     ["O‘chirgich", "Lupa", "To‘ldirish asbobi"], 3),
    ("Cho‘tka (Brush)", "Qalin va turli shakldagi chiziq chizish asbobi",
     ["Yupqa chiziq chizish asbobi", "O‘chirgich", "Lupa"], 3),
    ("O‘chirgich (Eraser)", "Tasvirning bir qismini o‘chirib tashlash asbobi",
     ["Rasmni saqlash asbobi", "Rang tanlash", "Faylni ochish"], 3),
    ("To‘ldirish (Fill / Bucket)", "Yopiq sohani bir rang bilan to‘ldirish asbobi",
     ["Faqat chiziq chizadi", "Rasm formatini o‘zgartiradi", "Faylni saqlaydi"], 3),
    ("Pipetka (Color picker)", "Rasmdan rangni olib (tanlab) ishlatish asbobi",
     ["Faqat o‘chiradi", "Faqat to‘ldiradi", "Brauzerni ochadi"], 3),
    ("Lupa (Magnifier / Zoom)", "Rasmning bir qismini kattalashtirib ko‘rish asbobi",
     ["Rasmni kichraytiradi va saqlaydi", "Rangni o‘zgartiradi", "Klaviaturani yoqadi"], 3),
    ("Tanlash (Select)", "Rasmning ma'lum sohasini ajratib olish asbobi",
     ["Rasmni saqlash", "Faqat chiziq chizish", "Brauzerni ochish"], 3),
    ("Matn (Text) asbobi", "Rasmga yozuv qo‘shish asbobi",
     ["Faylni saqlash", "Rasmni chop etish", "Faqat o‘chirish"], 3),
    ("Geometrik shakl (Shapes)", "To‘rtburchak, doira va boshqa shakllarni chizish asbobi",
     ["Faqat matn yozish", "Rasmni saqlash", "Pikselni o‘zgartirish"], 4),
    ("Rotate (90°)", "Rasmni 90° ga aylantirish amali",
     ["Rasmni o‘chirish", "Rasmni saqlash", "Rangni o‘zgartirish"], 4),
    ("Resize (Resize/Skew)", "Rasm o‘lchamini o‘zgartirish amali",
     ["Faqat aylantirish", "Faqat o‘chirish", "Faqat saqlash"], 4),
    ("Crop", "Rasmning ortiqcha qismini kesib tashlash amali",
     ["Faqat ranglash", "Brauzerni ochish", "Faylni nusxalash"], 4),
    ("PNG formati", "Shaffof fonni qo‘llab-quvvatlovchi rasm formati",
     ["Faqat audio formati", "Matn formati", "Video formati"], 5),
    ("JPG (JPEG) formati", "Suratlar uchun keng ishlatiladigan siqilgan rasm formati",
     ["Audio formati", "Matn formati", "Brauzer formati"], 5),
    ("BMP formati", "Siqilmagan, katta hajmli rasm formati",
     ["Faqat shaffof", "Faqat matn", "Faqat ovoz"], 5),
    ("GIF formati", "Animatsiyali rasmlar uchun ishlatiladigan format",
     ["Faqat ovoz", "Faqat matn", "Hujjat formati"], 5),
    ("Piksel", "Tasvir tashkil etiluvchi eng kichik nuqta",
     ["Faqat ranglar paleti", "Brauzer", "Hujjat sahifasi"], 6),
    ("Rezolyutsiya (Resolution)", "Tasvirdagi pikselllar soni — aniqlik darajasi",
     ["Faqat fayl hajmi", "Internet tezligi", "RAM hajmi"], 6),
    ("RGB", "Qizil, yashil, ko‘k ranglardan iborat raqamli rang modeli",
     ["Faqat oq-qora rang", "Faqat sariq rang", "Audio formati"], 6),
    ("Ranglar palitrasi", "Tanlanadigan tayyor ranglar to‘plami",
     ["Brauzer oynasi", "Disk hajmi", "Klaviatura tugmasi"], 2),
    ("Ctrl+Z", "Oxirgi amalni bekor qilish (undo) tugmalar birikmasi",
     ["Saqlash", "Yopish", "Chop etish"], 7),
    ("Ctrl+Y", "Bekor qilingan amalni qaytarish (redo) tugmalar birikmasi",
     ["Saqlash", "Yopish", "Bekor qilish"], 7),
    ("Ctrl+S", "Faylni saqlash tugmalar birikmasi",
     ["Yopish", "Topish", "Yangi"], 7),
    ("Ctrl+N", "Yangi hujjat ochish tugmalar birikmasi",
     ["Saqlash", "Yopish", "Topish"], 7),
    ("Ctrl+P", "Hujjatni chop etish tugmalar birikmasi",
     ["Saqlash", "Yopish", "Topish"], 7),
    ("Faylni 'Save As'", "Faylni boshqa nom yoki formatda saqlash",
     ["Faqat ochish", "Faqat o‘chirish", "Faqat chop etish"], 7),
    ("Background (fon)", "Rasmning orqa fonidagi rang yoki tasvir",
     ["Faqat birinchi reja", "Faqat matn rangi", "Faqat fayl nomi"], 4),
    ("Foreground (asosiy reja)", "Rasmning oldingi qismidagi asosiy tasvir",
     ["Faqat fon", "Faqat fayl nomi", "Faqat ovoz"], 4),
    ("Chiziq qalinligi (Line size)", "Qalam yoki cho‘tka chiziqlarining qalinligini sozlash",
     ["Brauzer parametri", "Disk hajmi", "Klaviatura tili"], 3),
    ("Color1 (Asosiy rang)", "Sichqonchaning chap tugmasi bosilganda chiziluvchi rang",
     ["Faqat fon rangi", "Faqat matn", "Faqat o‘lcham"], 2),
    ("Color2 (Yordamchi rang)", "Sichqonchaning o‘ng tugmasi bosilganda chiziluvchi rang",
     ["Faqat asosiy rang", "Faqat o‘lcham", "Faqat shrift"], 2),
    ("Edit Colors", "Yangi shaxsiy rang yaratish va palitra ga qo‘shish funksiyasi",
     ["Faqat saqlash", "Faqat chop etish", "Faqat o‘chirish"], 2),
    ("Selection — Rectangular", "To‘rtburchak shaklida soha tanlash usuli",
     ["Aylanma soha tanlash", "Erkin soha tanlash", "Faqat to‘ldirish"], 3),
    ("Selection — Free-form", "Erkin shaklda soha tanlash usuli",
     ["Faqat to‘rtburchak", "Faqat aylana", "Faqat saqlash"], 3),
    ("Status bar", "Paint oynasining pastki qismidagi axborot satri",
     ["Asboblar paneli", "Ranglar paneli", "Menyu satri"], 1),
    ("Menyu (Ribbon)", "Buyruqlar joylashgan yuqorigi panel",
     ["Faqat asboblar", "Faqat status satr", "Faqat ranglar"], 1),
]


def _info5_q2_pool() -> list[QItem]:
    pool: list[QItem] = []
    for c, d, w, l in INF_5_Q2_CONCEPTS:
        pool += _conceptual(c, d, w, lesson=l)

    def t_format_choose():
        cases = [
            ("Shaffof fon kerak", "PNG", ["JPG", "BMP", "GIF"]),
            ("Fotosurat hajmini kichraytirish kerak", "JPG", ["BMP", "PNG", "TXT"]),
            ("Eng yuqori sifatda saqlash kerak (siqilmagan)", "BMP", ["JPG", "PNG", "MP3"]),
            ("Animatsiyali rasm kerak", "GIF", ["JPG", "TXT", "MP3"]),
            ("Veb-saytga kichik hajmda yuklash kerak", "JPG", ["BMP", "TXT", "WAV"]),
        ]
        case, ans, wrongs = random.choice(cases)
        fname = random.choice(["rasm", "surat", "logo", "fon", "ekran"])
        return QItem(text=f"{case}. `{fname}` faylini qaysi formatda saqlash ma'qul?",
                     answer=ans, wrongs=list(wrongs), difficulty=2, lesson=5)

    def t_action_tool():
        cases = [
            ("Yopiq sohaga rang berish", "To‘ldirish (Fill)", ["Qalam", "O‘chirgich", "Lupa"]),
            ("Yupqa chiziq chizish", "Qalam (Pencil)", ["Cho‘tka", "Lupa", "Matn"]),
            ("Tasvirdan rangni olish", "Pipetka", ["Cho‘tka", "Qalam", "O‘chirgich"]),
            ("Rasmga yozuv qo‘shish", "Matn (Text)", ["O‘chirgich", "Cho‘tka", "Lupa"]),
            ("Bir qismni belgilab olish", "Tanlash (Select)", ["Cho‘tka", "Lupa", "Matn"]),
            ("Rasm o‘lchamini o‘zgartirish", "Resize", ["Crop", "Fill", "Eraser"]),
            ("Rasmni 90° aylantirish", "Rotate", ["Resize", "Crop", "Fill"]),
            ("Ortiqcha qismni kesish", "Crop", ["Resize", "Rotate", "Fill"]),
        ]
        action, ans, wrongs = random.choice(cases)
        return QItem(text=f"Paint dasturida quyidagi vazifa: '{action}'. Qaysi asbob/amal eng mos?",
                     answer=ans, wrongs=list(wrongs), difficulty=2, lesson=3)

    def t_color_mix():
        cases = [
            ("Qizil + Yashil", "Sariq", ["Ko‘k", "Pushti", "Jigarrang"]),
            ("Qizil + Ko‘k", "Pushti/binafsha", ["Yashil", "Sariq", "Qora"]),
            ("Sariq + Ko‘k", "Yashil", ["Qizil", "Pushti", "Oq"]),
        ]
        c, ans, wrongs = random.choice(cases)
        return QItem(text=f"RGB modelida {c} ranglarini birlashtirsak qanday rang hosil bo‘ladi?",
                     answer=ans, wrongs=list(wrongs), difficulty=2, lesson=6)

    def t_resolution():
        w = random.choice([640, 800, 1024, 1280, 1920])
        h = random.choice([480, 600, 720, 800, 1080])
        return QItem(text=f"Tasvir o‘lchami {w}×{h} piksel bo‘lsa, undagi pikselllar umumiy soni nechta?",
                     answer=str(w * h),
                     wrongs=[str(w + h), str(w * h + 1000), str(w - h)],
                     difficulty=3, lesson=6)

    def t_shortcut():
        cases = [
            ("Oxirgi amalni bekor qilish", "Ctrl+Z", ["Ctrl+S", "Ctrl+P", "Ctrl+N"]),
            ("Faylni saqlash", "Ctrl+S", ["Ctrl+Z", "Ctrl+P", "Ctrl+Y"]),
            ("Yangi hujjat ochish", "Ctrl+N", ["Ctrl+S", "Ctrl+Z", "Ctrl+P"]),
            ("Hujjatni chop etish", "Ctrl+P", ["Ctrl+S", "Ctrl+N", "Ctrl+Z"]),
            ("Bekor qilingan amalni qaytarish", "Ctrl+Y", ["Ctrl+Z", "Ctrl+S", "Ctrl+N"]),
        ]
        c, ans, wrongs = random.choice(cases)
        return QItem(text=f"Paintda '{c}' uchun tugmalar birikmasi qaysi?",
                     answer=ans, wrongs=list(wrongs), difficulty=1, lesson=7)

    pool += _capped(t_format_choose)
    pool += _capped(t_action_tool)
    pool += _capped(t_color_mix)
    pool += _capped(t_resolution)
    pool += _capped(t_shortcut)

    discrete = [
        QItem("Paintda rasmni saqlamasdan oynani yopsak nima sodir bo‘ladi?",
              "Saqlanmagan o‘zgarishlar yo‘qoladi",
              ["Avtomatik saqlanadi", "Faqat asbob yo‘qoladi", "Hech nima o‘zgarmaydi"], 2, 7),
        QItem("Paintda chiziq qalinligini qayerdan o‘zgartiramiz?",
              "Asboblar panelidagi 'Size' menyusidan",
              ["Brauzerdan", "Status bardan", "Klaviaturadan faqat"], 2, 3),
        QItem("Paint qaysi turdagi rasm muharririga kiradi?", "Rastrli rasm muharriri",
              ["Vektorli muharrir", "3D modelyator", "Audio muharrir"], 3, 1),
        QItem("Rastrli tasvir qanday tashkil topadi?", "Pikselllardan",
              ["Faqat chiziqlardan", "Faqat matndan", "Faqat tovushdan"], 3, 6),
        QItem("Rasm fayli hajmi 5 MB ekan. Bu necha KB ga teng?",
              "5120 KB", ["500 KB", "5000 KB", "8 KB"], 2, 6),
        QItem("Paintda matn yozayotganda shrift turini qayerdan o‘zgartiramiz?",
              "'Text' asbobi tanlanganda yuqorida ochiladigan paneldan",
              ["Brauzerdan", "Status bardan", "Faqat klaviaturadan"], 2, 3),
        QItem("PNG va JPG formatlari orasidagi farq nimada?",
              "PNG shaffoflikni qo‘llab-quvvatlaydi, JPG yo‘q",
              ["Ular bir xil", "JPG faqat oq-qora", "PNG faqat matn saqlaydi"], 3, 5),
        QItem("Rasmni cheksiz ko‘paytirsak nima sodir bo‘ladi (rastrli rasm)?",
              "Pikselllar ko‘rinib, rasm sifati pasayadi",
              ["Sifat o‘zgarmaydi", "Rang yo‘qoladi", "Format o‘zgaradi"], 3, 6),
        QItem("Paintda 'Brush' bilan 'Pencil' farqi nimada?",
              "Brush — qalin va turli shaklda chiziq, Pencil — yupqa va aniq",
              ["Bir xil asbob", "Brush faqat oq", "Pencil faqat qora"], 2, 3),
        QItem("Shaffof fonli logotipni saqlash uchun qaysi format eng mos?",
              "PNG", ["JPG", "BMP", "TXT"], 2, 5),
        QItem("Vektorli grafika nimasi bilan rastrlidan farqlanadi?",
              "Pikselllarga emas, matematik chiziqlarga asoslanadi",
              ["Hech qanday farqi yo‘q", "Faqat matn saqlaydi", "Faqat oq-qora"], 3, 6),
        QItem("Paintda 'Eyedropper' (pipetka) asbobi nima qiladi?",
              "Tasvirdagi rangni olib, faol rang sifatida qo‘yadi",
              ["O‘chiradi", "To‘ldiradi", "Saqlaydi"], 2, 3),
        QItem("Rasmga avtomatik shakl (to‘rtburchak) qo‘shish uchun qaysi bo‘limni tanlash kerak?",
              "Shapes (shakllar) bo‘limini",
              ["Tools", "Colors", "File"], 2, 4),
        QItem("Tasvirni 180° ga aylantirsak natija nima bo‘ladi?",
              "Rasm teskari (boshini pastga) aylanadi",
              ["Faqat ranglar o‘zgaradi", "Hech nima o‘zgarmaydi", "Rasm o‘chadi"], 2, 4),
        QItem("Rasm fayli kengaytmasini bilmasak, qaysi joydan ko‘rishimiz mumkin?",
              "Fayl nomidan keyingi nuqtadan keyingi qismdan",
              ["Disk hajmidan", "Klaviaturadan", "Brauzerdan"], 1, 5),
        QItem("Paintda 'Save' va 'Save As' farqi nimada?",
              "'Save' — eski faylga yozadi, 'Save As' — yangi nom/format bilan saqlaydi",
              ["Bir xil amallar", "Faqat ochish", "Faqat chop etish"], 2, 7),
        QItem("Paintda 'Crop' amalini bajarish uchun avval nima qilish kerak?",
              "Kerakli sohani tanlash (Select)",
              ["Hech nima qilish kerak emas", "Faylni saqlash", "Brauzerni ochish"], 2, 4),
        QItem("Tasvir hajmini kamaytirish uchun rezolyutsiyani nima qilamiz?",
              "Pasaytiramiz (kamroq piksellar)",
              ["Doim oshiramiz", "O‘zgartirmaymiz", "Faqat ranglarni o‘zgartiramiz"], 3, 6),
    ]
    pool += discrete
    random.shuffle(pool)
    return pool


# ─── INFORMATIKA — 5-sinf 3-chorak ───────────────────────────────────────────
# Mavzu: Excel asoslari — kataklar, formulalar (SUM/AVG/MAX/MIN/COUNT).

INF_5_Q3_CONCEPTS = [
    ("Microsoft Excel", "Jadvallar yaratish va ma'lumotlarni hisoblash dasturi",
     ["Brauzer", "Antivirus", "Rasm chizish dasturi"], 1),
    ("Workbook (kitob)", "Excel fayli — bir nechta varaqdan iborat bo‘lishi mumkin",
     ["Faqat bitta katak", "Faqat formula", "Faqat rasm"], 1),
    ("Worksheet (varaq)", "Bir Excel fayli ichidagi alohida jadval sahifasi",
     ["Faqat menyu", "Faqat fayl turi", "Faqat formula"], 1),
    ("Katak (Cell)", "Ustun va satr kesishmasidagi alohida joy",
     ["Faqat ustun", "Faqat satr", "Faqat fayl"], 2),
    ("Ustun (Column)", "Excelda harf bilan belgilangan vertikal qator",
     ["Faqat son bilan belgilanadi", "Faqat formula", "Faqat ranglar"], 2),
    ("Satr (Row)", "Excelda raqam bilan belgilangan gorizontal qator",
     ["Harf bilan belgilanadi", "Faqat formula", "Faqat ranglar"], 2),
    ("Katak manzili", "Ustun harfi va satr raqami birikmasi (masalan A1)",
     ["Faqat son", "Faqat harf", "Satr raqami + ustun harfi (teskari)"], 3),
    ("Formula", "Hisob-kitobni avtomatlashtiruvchi ifoda — `=` bilan boshlanadi",
     ["Oddiy matn", "Faqat rasm", "Faqat son"], 4),
    ("=SUM()", "Tanlangan kataklar yig‘indisini hisoblovchi formula",
     ["O‘rtachani", "Maksimumni", "Minimumni"], 4),
    ("=AVERAGE()", "Tanlangan kataklar o‘rtacha qiymatini hisoblovchi formula",
     ["Yig‘indini", "Maksimumni", "Minimumni"], 4),
    ("=MAX()", "Tanlangan kataklar orasidagi eng katta qiymatni topuvchi formula",
     ["O‘rtachani", "Eng kichikni", "Yig‘indini"], 4),
    ("=MIN()", "Tanlangan kataklar orasidagi eng kichik qiymatni topuvchi formula",
     ["Eng kattani", "O‘rtachani", "Yig‘indini"], 4),
    ("=COUNT()", "Diapazondagi sonli (raqam) kataklar sonini topuvchi formula",
     ["Yig‘indini", "Eng kattani", "O‘rtachani"], 4),
    ("Diapazon (Range)", "Bir nechta katakdan iborat soha (masalan A1:A10)",
     ["Faqat bitta katak", "Faqat ustun", "Faqat satr"], 3),
    ("Operator '+'", "Excelda qo‘shish amali",
     ["Ko‘paytirish", "Bo‘lish", "Ayirish"], 4),
    ("Operator '-'", "Excelda ayirish amali",
     ["Qo‘shish", "Ko‘paytirish", "Bo‘lish"], 4),
    ("Operator '*'", "Excelda ko‘paytirish amali",
     ["Qo‘shish", "Bo‘lish", "Ayirish"], 4),
    ("Operator '/'", "Excelda bo‘lish amali",
     ["Qo‘shish", "Ko‘paytirish", "Ayirish"], 4),
    ("Format kataklar", "Katakdagi son/sana/matn ko‘rinishini sozlash imkoniyati",
     ["Faqat ranglash", "Faqat saqlash", "Faqat o‘chirish"], 5),
    ("Bosh sahifa (Home) tab", "Excelning asosiy tahrirlash bo‘limi",
     ["Brauzer paneli", "Faylni saqlovchi panel", "Antivirus"], 1),
    ("Insert tab", "Yangi rasm, jadval, diagramma kabilarni qo‘shish bo‘limi",
     ["Faqat fayl saqlash", "Faqat o‘chirish", "Faqat ranglar"], 1),
    ("Diagramma (Chart)", "Sonli ma'lumotlarning grafik ko‘rinishi",
     ["Oddiy matn", "Faqat fayl nomi", "Faqat formula"], 6),
    ("Bar chart (ustunli diagramma)", "Qiymatlarni ustunlar bilan ko‘rsatuvchi diagramma",
     ["Doira diagrammasi", "Chiziqli diagramma", "Faqat matn"], 6),
    ("Pie chart (doira)", "Ulushlarni doirada ko‘rsatuvchi diagramma",
     ["Ustunli diagramma", "Chiziqli diagramma", "Faqat son"], 6),
    ("Line chart (chiziqli)", "Qiymatlar o‘zgarishini chiziq bilan ko‘rsatuvchi diagramma",
     ["Doira diagrammasi", "Faqat matn", "Faqat fayl turi"], 6),
    ("Saqlash (Save) — Excel", "Excel faylini diskka yozish amali",
     ["Yopish", "Topish", "Bekor qilish"], 7),
    ("Save As — Excel", "Excel faylini boshqa nom yoki formatda saqlash",
     ["Faqat ochish", "Faqat o‘chirish", "Faqat chop etish"], 7),
    ("Excel kengaytmasi (.xlsx)", "Microsoft Excel fayllari uchun kengaytma",
     [".docx", ".pptx", ".png"], 7),
    ("Cell reference (havola)", "Boshqa katakka ishora qiluvchi formula qismi",
     ["Faqat matn", "Faqat son", "Faqat rang"], 3),
    ("Tartiblash (Sort)", "Ustun bo‘yicha o‘sish/kamayish tartibida joylashtirish",
     ["Filterlash", "Faqat o‘chirish", "Faqat saqlash"], 8),
    ("Filter", "Kerakli ma'lumotlarni tanlab ko‘rsatish imkoniyati",
     ["Tartiblash", "Faqat saqlash", "Faqat chizmoq"], 8),
    ("AutoSum", "Tugma orqali avtomatik yig‘indi formulasini qo‘yish",
     ["Faqat AVERAGE", "Faqat MAX", "Faqat MIN"], 4),
    ("Fill handle", "Katak burchagidan torttirib formulani nusxalash imkoniyati",
     ["Faqat ranglash", "Faqat o‘chirish", "Faqat saqlash"], 4),
    ("Bosh sahifa (Sheet1)", "Yangi Excel kitobida birinchi varaq nomi",
     ["Brauzer", "Faqat fayl", "Faqat formula"], 1),
    ("Header row (sarlavha qator)", "Jadvalning birinchi qatori — ustun nomlari",
     ["Faqat son", "Faqat papka", "Faqat formula"], 5),
    ("Cell merge (Birlashtirish)", "Bir nechta katakni bitta katakka birlashtirish",
     ["Bo‘lish", "O‘chirish", "Saqlash"], 5),
    ("Wrap text", "Uzun matnni katakda bir nechta qatorga sig‘dirish",
     ["Faqat o‘chirish", "Faqat saqlash", "Faqat ranglash"], 5),
    ("Alignment (Tekislash)", "Katakdagi matn yoki sonni chap/o‘rta/o‘ng tekislash",
     ["Faqat saqlash", "Faqat ranglash", "Faqat formula"], 5),
    ("Boldroq (Bold) — Ctrl+B", "Matnni qalin qilish",
     ["Kursiv", "Tagiga chizish", "O‘chirish"], 5),
    ("Italic (Kursiv) — Ctrl+I", "Matnni qiya yozish",
     ["Qalin qilish", "Tagiga chizish", "O‘chirish"], 5),
]


def _info5_q3_pool() -> list[QItem]:
    pool: list[QItem] = []
    for c, d, w, l in INF_5_Q3_CONCEPTS:
        pool += _conceptual(c, d, w, lesson=l)

    cols = list("ABCDEFGH")

    def t_address():
        c = random.choice(cols); r = random.randint(2, 99)
        return QItem(text=f"Excelda {c} ustun va {r}-satr kesishgan katak manzili qaysi?",
                     answer=f"{c}{r}",
                     wrongs=[f"{r}{c}", f"{c}:{r}", f"{c}-{r}"],
                     difficulty=2, lesson=3)

    def t_sum():
        nums = [random.randint(1, 30) for _ in range(4)]
        return QItem(text=f"Excelda `=SUM({nums[0]},{nums[1]},{nums[2]},{nums[3]})` natijasi nima?",
                     answer=str(sum(nums)),
                     wrongs=[str(max(nums)), str(min(nums)), str(sum(nums) + 1)],
                     difficulty=2, lesson=4)

    def t_avg():
        nums = [random.randint(1, 50) for _ in range(4)]
        avg = sum(nums) / 4
        return QItem(text=f"Excelda `=AVERAGE({nums[0]},{nums[1]},{nums[2]},{nums[3]})` natijasi nima?",
                     answer=f"{avg:g}",
                     wrongs=[str(sum(nums)), str(max(nums)), str(min(nums))],
                     difficulty=2, lesson=4)

    def t_max():
        nums = [random.randint(5, 200) for _ in range(5)]
        return QItem(text=f"Excelda `=MAX({nums[0]},{nums[1]},{nums[2]},{nums[3]},{nums[4]})` natijasi nima?",
                     answer=str(max(nums)),
                     wrongs=[str(min(nums)), str(sum(nums)), str(sum(nums) // 5)],
                     difficulty=2, lesson=4)

    def t_min():
        nums = [random.randint(5, 200) for _ in range(5)]
        return QItem(text=f"Excelda `=MIN({nums[0]},{nums[1]},{nums[2]},{nums[3]},{nums[4]})` natijasi nima?",
                     answer=str(min(nums)),
                     wrongs=[str(max(nums)), str(sum(nums)), str(sum(nums) // 5)],
                     difficulty=2, lesson=4)

    def t_count():
        nums = [random.randint(1, 50) for _ in range(random.randint(3, 6))]
        return QItem(text=f"Excelda `=COUNT({','.join(map(str, nums))})` natijasi nima?",
                     answer=str(len(nums)),
                     wrongs=[str(len(nums) + 1), str(len(nums) - 1), str(sum(nums))],
                     difficulty=2, lesson=4)

    def t_arith_formula():
        a = random.randint(2, 30); b = random.randint(2, 15)
        op = random.choice(["+", "-", "*"])
        ans = a + b if op == "+" else (a - b if op == "-" else a * b)
        return QItem(text=f"Excelda katakka `={a}{op}{b}` formulasi yozildi. Natija qanday bo‘ladi?",
                     answer=str(ans),
                     wrongs=[str(ans + 1), str(ans - 1), str(a)],
                     difficulty=1, lesson=4)

    def t_what_formula_does():
        f = random.choice(["SUM", "AVERAGE", "MAX", "MIN", "COUNT"])
        rng = f"{random.choice(cols[:3])}{random.randint(1, 5)}:{random.choice(cols[:3])}{random.randint(6, 12)}"
        ans_map = {"SUM": "Tanlangan kataklar yig‘indisini",
                   "AVERAGE": "Tanlangan kataklar o‘rtachasini",
                   "MAX": "Eng katta qiymatni",
                   "MIN": "Eng kichik qiymatni",
                   "COUNT": "Sonli kataklar sonini"}
        ans = ans_map[f]
        wrongs = [v for k, v in ans_map.items() if k != f][:3]
        return QItem(text=f"Excelda `={f}({rng})` formulasi nimani hisoblaydi?",
                     answer=ans, wrongs=wrongs, difficulty=2, lesson=4)

    pool += _capped(t_address)
    pool += _capped(t_sum)
    pool += _capped(t_avg)
    pool += _capped(t_max)
    pool += _capped(t_min)
    pool += _capped(t_count)
    pool += _capped(t_arith_formula)
    pool += _capped(t_what_formula_does)

    discrete = [
        QItem("Excelda formulani boshlash uchun qaysi belgi kerak?", "= (teng) belgisi",
              ["+", "-", "*"], 1, 4),
        QItem("Excelda Ctrl+S birikmasi nima qiladi?", "Faylni saqlaydi",
              ["Yopadi", "Yangi hujjat ochadi", "Topadi"], 1, 7),
        QItem("Excelda yangi varaq qo‘shish uchun qaysi tugma bosiladi?",
              "Sheet1 yonidagi `+` (yangi varaq) tugmasi",
              ["Brauzer", "Antivirus", "Calculator"], 2, 1),
        QItem("Bir vaqtda bir nechta yondosh katakni belgilash uchun nima qilamiz?",
              "Sichqonchani bosib turib torttirib tortamiz",
              ["Faqat klaviatura", "Faqat F5", "Hech narsa"], 2, 2),
        QItem("Bir vaqtda yondosh BO‘LMAGAN bir nechta katak tanlash uchun qaysi tugma bosib turiladi?",
              "Ctrl tugmasi", ["Shift", "Alt", "Tab"], 3, 2),
        QItem("Excelda formulani boshqa katakka olib o‘tish uchun nima qilinadi?",
              "Fill handle (katak burchagi) yordamida torttiriladi",
              ["Klaviaturadan qayta yoziladi", "Faqat brauzerda", "Faqat status bardan"], 2, 4),
        QItem("Excelda barcha kataklarni tezda belgilash tugmasi qaysi?", "Ctrl + A",
              ["Ctrl + S", "Ctrl + Z", "Alt + F4"], 2, 2),
        QItem("Katakdagi matn ko‘rinmayapti — sabab nima bo‘lishi mumkin?",
              "Ustun kengligi yetarli emas",
              ["Fayl saqlanmagan", "Internet sekin", "RAM yetishmasligi"], 2, 5),
        QItem("Excelda satr balandligini qanday o‘zgartiramiz?",
              "Satr chegarasini sichqoncha bilan torttiramiz",
              ["Faqat klaviatura yordamida", "Faqat Ctrl+S", "Internet kerak"], 2, 5),
        QItem("Sonni faqat butun ko‘rinishda chiqarish uchun qaysi format kerak?",
              "Number — Decimal places: 0",
              ["Text formati", "Date formati", "Currency"], 3, 5),
        QItem("Pul birligini katakka qo‘shish uchun qaysi format ishlatiladi?",
              "Currency formati",
              ["Number formati", "Date formati", "Text formati"], 3, 5),
        QItem("Sanani katakka qo‘shish uchun qaysi format eng to‘g‘ri?",
              "Date formati", ["Number", "Text", "Currency"], 2, 5),
        QItem("Excelda `=A1+A2` formulasi A1 va A2 kataklardagi qiymatlarni nima qiladi?",
              "Qo‘shadi", ["Ko‘paytiradi", "Bo‘ladi", "Ayiradi"], 1, 4),
        QItem("Excelda `=A1*A2` formulasi nimani hisoblaydi?",
              "A1 va A2 ni ko‘paytirmasini",
              ["Yig‘indisini", "Bo‘linmasini", "Ayirmasini"], 1, 4),
        QItem("Excelda `=A1/B1` formulasi nimani hisoblaydi?",
              "A1 ni B1 ga bo‘lganini",
              ["Yig‘indisini", "Ayirmasini", "Ko‘paytirmasini"], 1, 4),
        QItem("Diagrammani qaysi bo‘limdan qo‘shish mumkin?",
              "Insert (Qo‘shish) tab",
              ["Home", "View", "Formulas"], 2, 6),
        QItem("Excelda formulada B0 katak manzili bormi?",
              "Yo‘q — satr 1 dan boshlanadi",
              ["Ha — bor", "Faqat ba'zi versiyalarda", "Faqat 'B0' bo‘sh joy bo‘ladi"], 3, 3),
        QItem("Excelda katakdagi formulani ko‘rish uchun qayerga qaraymiz?",
              "Formula bar (formula satri)",
              ["Status bar", "Title bar", "Sheet tab"], 2, 4),
        QItem("Excelda yangi qator qo‘shish uchun qaysi amal eng to‘g‘ri?",
              "Satr raqamiga o‘ng tugma → Insert",
              ["Faqat Ctrl+S", "Faqat Brauzerni ochish", "Faqat F1"], 2, 5),
        QItem("Excelda diagramma turi qaysi ma'lumot uchun eng mos: ulushlar?",
              "Pie (doira) chart",
              ["Faqat Bar chart", "Faqat Line chart", "Faqat Scatter"], 2, 6),
    ]
    pool += discrete
    random.shuffle(pool)
    return pool


# ─── INFORMATIKA — 5-sinf 4-chorak ───────────────────────────────────────────
# Mavzu: Internet, brauzer, URL, xavfsizlik (parol, phishing, fayl yuklash).

INF_5_Q4_CONCEPTS = [
    ("Internet", "Dunyo bo‘ylab kompyuterlarni birlashtirgan global tarmoq",
     ["Faqat lokal tarmoq", "Bitta kompyuter ichidagi xotira", "Faqat ofline o‘yin"], 1),
    ("Veb-sahifa (Web page)", "Brauzer orqali ko‘riladigan internetdagi sahifa",
     ["Faqat fayl turi", "Klaviatura tugmasi", "Faqat rasm"], 2),
    ("Veb-sayt (Web site)", "Bir nechta veb-sahifalardan iborat majmua",
     ["Faqat bitta sahifa", "Brauzer", "Antivirus"], 2),
    ("Brauzer", "Veb-sahifalarni ko‘rish uchun maxsus dastur",
     ["Matn muharriri", "Antivirus", "Excel"], 3),
    ("Google Chrome", "Google kompaniyasining mashhur brauzeri",
     ["Faqat antivirus", "Faqat o‘yin", "Excel formati"], 3),
    ("Mozilla Firefox", "Ochiq kodli mashhur brauzer",
     ["Antivirus", "Faqat e-pochta", "Excel formati"], 3),
    ("Microsoft Edge", "Microsoftning brauzeri",
     ["Antivirus", "Faqat o‘yin", "Word hujjati"], 3),
    ("Safari", "Apple kompaniyasining brauzeri",
     ["Microsoft mahsuloti", "Antivirus", "Excel"], 3),
    ("URL", "Veb-sahifaning to‘liq manzili (masalan https://example.com)",
     ["Faqat fayl nomi", "Klaviatura tugmasi", "Operatsion tizim"], 4),
    ("Domen nomi", "URL dagi sayt asosiy nomi (masalan example.com)",
     ["Internet protokoli", "Klaviatura tugmasi", "Brauzer turi"], 4),
    ("HTTP", "Gipertekst uzatish protokoli — ochiq aloqa",
     ["Faqat shifrlangan", "Faqat audio formati", "Faqat fayl turi"], 4),
    ("HTTPS", "Shifrlangan, xavfsiz HTTP — `S` xavfsizlik bilan",
     ["Shifrlanmagan", "Faqat oyna formati", "Faqat audio"], 4),
    ("DNS", "Domen nomini IP manzilga o‘girib beruvchi tizim",
     ["Faqat fayl turi", "Faqat audio", "Klaviatura tugmasi"], 4),
    ("IP manzil", "Tarmoqdagi har bir qurilmaning unikal raqamli manzili",
     ["Faqat fayl nomi", "Klaviatura tugmasi", "Excel formula"], 4),
    ("Wi-Fi", "Simsiz internetga ulanish texnologiyasi",
     ["Faqat simli ulanish", "Faqat printer", "Faqat audio"], 5),
    ("Modem", "Internet signalini kompyuter tushunadigan ko‘rinishga aylantiruvchi qurilma",
     ["Antivirus", "Faqat tugmacha", "Operatsion tizim"], 5),
    ("Router (yo‘riqnoma)", "Tarmoq qurilmalarini birlashtirib internet tarqatuvchi qurilma",
     ["Antivirus", "Audio karta", "Klaviatura"], 5),
    ("Search Engine (qidiruv tizim)", "Internetda ma'lumot izlash uchun mo‘ljallangan tizim (Google, Yandex)",
     ["Antivirus", "Excel", "Faqat brauzer"], 6),
    ("Bookmark (xatcho‘p)", "Brauzerda saytni keyin tezda topish uchun belgilash",
     ["Saytni o‘chirish", "Brauzerni yopish", "Antivirusni yoqish"], 3),
    ("Tab (yorliq)", "Brauzerda bir vaqtda bir nechta sahifa ochish uchun panel",
     ["Faqat saqlash", "Faqat yopish", "Faqat o‘chirish"], 3),
    ("History (tarix)", "Brauzerda oldin tashrif buyurilgan sahifalar ro‘yxati",
     ["Faqat parollar ro‘yxati", "Faqat fayllar ro‘yxati", "Faqat o‘chirilgan fayllar"], 3),
    ("Download (yuklab olish)", "Internetdan fayllarni kompyuterga ko‘chirib olish",
     ["Internetga yuklash", "Faqat o‘chirish", "Faqat saqlash"], 6),
    ("Upload (yuklash)", "Faylni kompyuterdan internetga yuborish",
     ["Internetdan olib kelish", "Faqat o‘chirish", "Faqat ko‘chirish"], 6),
    ("Cookie", "Saytlar saqlaydigan kichik ma'lumot bo‘lakchasi",
     ["Faqat virus", "Faqat antivirus", "Faqat fayl turi"], 7),
    ("Login (kirish)", "Saytga foydalanuvchi sifatida kirish jarayoni",
     ["Faqat parolni o‘chirish", "Faqat saytdan chiqish", "Faqat brauzerni yopish"], 7),
    ("Parol (Password)", "Hisobni himoya qiluvchi maxfiy belgilar ketma-ketligi",
     ["Hammaga ko‘rinadigan ma'lumot", "Faqat ism", "Faqat foydalanuvchi nomi"], 7),
    ("Kuchli parol", "Uzun, harf+son+belgi bo‘lgan murakkab parol",
     ["Faqat 12345", "Faqat ism", "Faqat tug‘ilgan kun"], 7),
    ("Phishing", "Soxta sahifalar orqali parol/yo‘l o‘g‘irlash usuli",
     ["Faqat brauzer", "Faqat fayl saqlash", "Internet tezligi"], 7),
    ("Spam", "Keraksiz, ko‘plab yuborilgan reklama xat-xabarlar",
     ["Faqat foydali xabar", "Antivirus", "Faqat fayl turi"], 7),
    ("Antivirus", "Zararli dasturlardan himoya qiluvchi maxsus dastur",
     ["Faqat brauzer", "Faqat o‘yin", "Faqat fayl turi"], 8),
    ("Virus", "Kompyuterga zarar etkazadigan zararli dastur",
     ["Antivirus", "Faqat brauzer", "Faqat operatsion tizim"], 8),
    ("Firewall (tarmoq devori)", "Notog‘ri kirishlardan himoya qiluvchi vosita",
     ["Antivirus turi", "Klaviatura turi", "Brauzer"], 8),
    ("Captcha", "Inson ekanligini tekshiruvchi kichik test",
     ["Antivirus", "Faqat parol", "Faqat brauzer"], 7),
    ("E-pochta (Email)", "Internet orqali xat yuborish va olish xizmati",
     ["Brauzer", "Antivirus", "Faqat o‘yin"], 6),
    ("@ (et) belgisi", "E-pochta manzilida foydalanuvchi va domenni ajratuvchi belgi",
     ["Faqat URL ichida", "Faqat fayl nomida", "Faqat operator"], 6),
    ("Cloud Storage (bulutli xotira)", "Fayllarni internetda saqlash xizmati",
     ["Faqat lokal disk", "Faqat brauzer", "Faqat antivirus"], 6),
    ("Google Drive", "Googlening bulutli xotira xizmati",
     ["Antivirus", "Brauzer", "Operatsion tizim"], 6),
    ("Two-Factor Authentication (2FA)", "Parolga qo‘shimcha tasdiqlash kodi orqali xavfsizlikni oshirish",
     ["Faqat oddiy parol", "Faqat antivirus", "Faqat captcha"], 7),
    ("HTTPS qulf belgisi", "Brauzerda saytning xavfsiz ekanligini bildiradi",
     ["Faqat reklama", "Faqat fayl turi", "Faqat brauzer logo"], 4),
    ("Incognito (Yashirin) rejim", "Tarixsiz brauzerda ko‘rish rejimi",
     ["Faqat audio rejim", "Faqat parolni saqlash", "Faqat tezroq tarmoq"], 3),
]


def _info5_q4_pool() -> list[QItem]:
    pool: list[QItem] = []
    for c, d, w, l in INF_5_Q4_CONCEPTS:
        pool += _conceptual(c, d, w, lesson=l)

    def t_url_domain():
        domain = random.choice(["school.uz", "example.com", "jahonschool.uz", "edu.uz",
                                "library.uz", "news.uz", "lex.uz"])
        path = random.choice(["/login", "/news", "/profile", "/courses", "/about"])
        proto = random.choice(["http", "https"])
        url = f"{proto}://{domain}{path}"
        return QItem(text=f"Quyidagi URLda domen qismi qaysi?\n\n{url}",
                     answer=domain,
                     wrongs=[proto, path, f"{proto}://{domain}"],
                     difficulty=2, lesson=4)

    def t_url_protocol():
        domain = random.choice(["edu.uz", "uz.edu", "math.uz", "openclass.uz"])
        path = random.choice(["/index", "/me", "/help", "/blog"])
        proto = random.choice(["http", "https"])
        url = f"{proto}://{domain}{path}"
        ans = "Shifrlangan (xavfsiz)" if proto == "https" else "Shifrlanmagan (xavfsizroq emas)"
        wrongs = ["Shifrlangan (xavfsiz)" if proto != "https" else "Shifrlanmagan (xavfsizroq emas)",
                  "Faqat lokal", "Faqat audio"]
        return QItem(text=f"Quyidagi URL qanday turdagi aloqa orqali ishlaydi?\n\n{url}",
                     answer=ans, wrongs=wrongs, difficulty=2, lesson=4)

    def t_password_strength():
        bases = ["Ali", "user", "school", "python", "test", "Asror", "Maktab"]
        base = random.choice(bases)
        styles = [
            f"{base}123",
            f"{base}{random.randint(10, 99)}",
            f"{base.capitalize()}_{random.randint(10, 99)}!",
            f"{base}{random.choice('!@#$')}{random.randint(100, 999)}Aa",
            f"{base.lower()}",
            "12345678",
            f"{base}{random.choice('!@#$%')}A1z9",
        ]
        pwd = random.choice(styles)
        is_strong = (len(pwd) >= 8
                     and any(c.islower() for c in pwd)
                     and any(c.isupper() for c in pwd)
                     and any(c.isdigit() for c in pwd)
                     and any(c in "!@#$%^&*_-+" for c in pwd))
        ans = "Kuchli" if is_strong else "Kuchsiz"
        return QItem(text=f"Parol kuchini baholang: `{pwd}`",
                     answer=ans, wrongs=["Kuchli", "Kuchsiz", "Aniqlab bo‘lmaydi"],
                     difficulty=2, lesson=7)

    def t_phishing_sign():
        cases = [
            ("Saytda HTTPS yo‘q va qulf belgisi ko‘rinmayapti", "Xavfsizlik past — ehtiyot bo‘lish kerak",
             ["Doim xavfsiz", "Internet uzildi", "Antivirus o‘chgan"]),
            ("Sayt domeni 'g00gle.com' (nol bilan)", "Phishing belgisi — soxta sayt",
             ["Haqiqiy Google sayti", "Brauzer xato", "Hech qanday muammo yo‘q"]),
            ("Notanish manbadan 'parolingizni shoshilinch yangilang' degan xat keldi", "Phishing — ehtiyot bo‘lish kerak",
             ["Foydali xat", "Antivirus xabari", "Brauzer xato"]),
            ("Sayt 'paypaI.com' (katta `I` bilan)", "Soxta sayt — phishing",
             ["Haqiqiy PayPal", "Brauzer xato", "Faqat reklama"]),
        ]
        sign, ans, wrongs = random.choice(cases)
        return QItem(text=f"Bu holat nimani anglatadi?\n\nHolat: {sign}",
                     answer=ans, wrongs=list(wrongs), difficulty=3, lesson=7)

    def t_speed_calc():
        size = random.randint(20, 500)  # MB
        speed = random.randint(2, 25)   # MB/s
        ans = size // speed
        return QItem(text=f"{size} MB hajmdagi fayl {speed} MB/s tezlikda taxminan necha sekundda yuklanadi? (butun qism)",
                     answer=str(ans),
                     wrongs=[str(ans + 1), str(ans - 1), str(size + speed)],
                     difficulty=2, lesson=6)

    pool += _capped(t_url_domain)
    pool += _capped(t_url_protocol)
    pool += _capped(t_password_strength)
    pool += _capped(t_phishing_sign)
    pool += _capped(t_speed_calc)

    discrete = [
        QItem("Brauzerda yangi yorliq (tab) ochish uchun qaysi tugmalar birikmasi ishlatiladi?",
              "Ctrl + T", ["Ctrl + S", "Ctrl + N", "Alt + F4"], 2, 3),
        QItem("Brauzerda sahifa yangilash uchun qaysi tugma bosiladi?",
              "F5", ["F1", "Esc", "Tab"], 2, 3),
        QItem("Brauzerda 'Yashirin' (Incognito) rejim nima uchun ishlatiladi?",
              "Tarixni saqlamasdan ko‘rish uchun",
              ["Tezroq internet uchun", "Saytlarni o‘chirish uchun", "Faqat o‘yinlar uchun"], 3, 3),
        QItem("@ belgisi e-pochta manzilida nimani ajratadi?",
              "Foydalanuvchi nomi va domen nomini",
              ["Sahifa va papkani", "Brauzer va saytni", "Disk va papkani"], 2, 6),
        QItem("Internetda xavfsiz parol qanday bo‘lishi kerak?",
              "Uzun (8+) va harf-son-belgi aralash",
              ["Faqat raqam", "Faqat oddiy ism", "Faqat 1234"], 2, 7),
        QItem("Saytdan keyingi safar tezda topish uchun qanday usul mavjud?",
              "Bookmark (xatcho‘p) qilib qo‘yish",
              ["Faqat brauzerni o‘chirish", "Faqat fayl saqlash", "Faqat URL chop etish"], 2, 3),
        QItem("Fayl internetdan kompyuterga ko‘chib olinishi nima deb ataladi?",
              "Download", ["Upload", "Save", "Print"], 2, 6),
        QItem("Faylni kompyuterdan internetga yuborish nima deb ataladi?",
              "Upload", ["Download", "Print", "Save"], 2, 6),
        QItem("HTTPS protokolida 'S' harfi nima ma'noni bildiradi?",
              "Secure (xavfsiz)", ["Standard", "Speed", "System"], 3, 4),
        QItem("Captcha nima uchun ishlatiladi?",
              "Inson ekanligimizni tekshirish uchun",
              ["Faqat reklama", "Faqat parol saqlash", "Faqat virus"], 2, 7),
        QItem("Quyidagilardan qaysi biri eng kuchli parol?",
              "Asr0r_Maktab#2025!",
              ["12345", "asror", "qwerty"], 2, 7),
        QItem("Brauzerda sahifa orqaga qaytish uchun qaysi tugma ishlatiladi?",
              "Brauzerning chap yuqorisidagi 'Back' (←) tugmasi",
              ["Esc", "Ctrl+S", "Tab"], 2, 3),
        QItem("Bulutli xotira (cloud storage) afzalligi nima?",
              "Fayllarni har qanday qurilmadan kira olish",
              ["Faqat lokal saqlash", "Faqat oflayn ishlash", "Faqat virusdan himoya"], 3, 6),
        QItem("Brauzerda biror saytga kirish uchun avval nima yoziladi?",
              "URL — sayt manzili",
              ["Faqat parol", "Faqat foydalanuvchi nomi", "Faqat fayl nomi"], 1, 4),
        QItem("Notanish odamlardan kelgan havolalarga qanday munosabatda bo‘lish kerak?",
              "Bosishdan oldin tekshirib ko‘rish, ehtiyot bo‘lish",
              ["Doim bosish", "Faylni saqlash", "Brauzerni yopish"], 2, 7),
        QItem("Saytga kirish uchun parol va kod ham so‘ralsa, bu qanday himoya?",
              "Ikki bosqichli tasdiqlash (2FA)",
              ["Faqat oddiy parol", "Faqat captcha", "Faqat brauzer"], 3, 7),
        QItem("Cookie nima uchun ishlatiladi?",
              "Sayt foydalanuvchini eslab qolishi uchun (sozlamalar, kirish)",
              ["Faqat virus", "Faqat reklama", "Faqat parol o‘g‘irlash"], 3, 7),
        QItem("Antivirus dasturi qanday ishlaydi?",
              "Fayllarni virus belgilariga tekshirib, zararlanganini bartaraf etadi",
              ["Faqat tezlikni oshiradi", "Faqat brauzerni ochadi", "Faqat parol saqlaydi"], 3, 8),
        QItem("Internetni tarqatuvchi qurilma nima deb ataladi?",
              "Router (yo‘riqnoma)",
              ["Antivirus", "Operatsion tizim", "Klaviatura"], 2, 5),
        QItem("Veb-sahifa ochilmayapti — birinchi navbatda nimani tekshiramiz?",
              "Internet ulanishini",
              ["Faqat parolni", "Faqat fayl nomini", "Faqat ekran o‘lchamini"], 2, 5),
    ]
    pool += discrete
    random.shuffle(pool)
    return pool


# ─── INFORMATIKA — 6-sinf 1-chorak ───────────────────────────────────────────
# Mavzu: Word matn muharriri — formatlash, tugmalar, header/footer.

INF_6_Q1_CONCEPTS = [
    ("Microsoft Word", "Matn yozish va tahrirlash dasturi",
     ["Brauzer", "Antivirus", "Excel"], 1),
    (".docx", "Microsoft Word hujjati uchun kengaytma",
     [".xlsx", ".pptx", ".png"], 1),
    ("Hujjat (Document)", "Word dasturidagi alohida matn fayli",
     ["Faqat rasm", "Brauzer oynasi", "Klaviatura"], 1),
    ("Sahifa (Page)", "Word hujjatining bitta sahifasi",
     ["Faqat ustun", "Faqat satr", "Faqat formula"], 1),
    ("Abzats (Paragraph)", "Bir-biriga bog‘liq jumlalar to‘plami",
     ["Faqat bitta so‘z", "Faqat sarlavha", "Faqat raqam"], 2),
    ("Sarlavha (Heading)", "Bo‘limning bosh nomi (odatda kattaroq shrift)",
     ["Oddiy abzats", "Faqat raqam", "Faqat rasm"], 2),
    ("Shrift (Font)", "Matn belgilarining shakli (Times, Arial va h.k.)",
     ["Faqat rang", "Faqat sahifa o‘lchami", "Faqat fayl turi"], 3),
    ("Shrift o‘lchami", "Matn katta-kichikligini belgilovchi raqam (10, 12, 14...)",
     ["Faqat fayl hajmi", "Faqat rang", "Faqat formula"], 3),
    ("Bold (Qalin) — Ctrl+B", "Matnni qalin qilish",
     ["Kursiv", "Tagiga chizish", "O‘chirish"], 3),
    ("Italic (Kursiv) — Ctrl+I", "Matnni qiya yozish",
     ["Qalin qilish", "Tagiga chizish", "O‘chirish"], 3),
    ("Underline — Ctrl+U", "Matn tagiga chiziq chizish",
     ["Kursiv", "Qalin", "O‘chirish"], 3),
    ("Tekislash chap (Align Left)", "Matnni chap chetga tekislash",
     ["O‘ng tekislash", "Markazlash", "Justify"], 4),
    ("Tekislash o‘rta (Align Center)", "Matnni markazga tekislash",
     ["Chap tekislash", "O‘ng tekislash", "Justify"], 4),
    ("Tekislash o‘ng (Align Right)", "Matnni o‘ng chetga tekislash",
     ["Chap tekislash", "Markazlash", "Justify"], 4),
    ("Justify", "Matnni ikki chetga tekislash (har qatorga teng tarqatish)",
     ["Faqat chap", "Faqat o‘rta", "Faqat o‘ng"], 4),
    ("Header", "Sahifaning yuqori qismidagi takrorlanuvchi qism",
     ["Pastki qism (footer)", "Faqat ramka", "Faqat raqam"], 5),
    ("Footer", "Sahifaning pastki qismidagi takrorlanuvchi qism",
     ["Yuqori qism (header)", "Faqat rasm", "Faqat sarlavha"], 5),
    ("Page Number", "Sahifaga avtomatik raqam qo‘yish funksiyasi",
     ["Faqat header", "Faqat sarlavha", "Faqat ramka"], 5),
    ("Bullet list", "Belgi bilan boshlanadigan ro‘yxat",
     ["Raqamli ro‘yxat", "Sarlavha", "Faqat ramka"], 6),
    ("Numbered list", "Raqam bilan boshlanadigan tartiblangan ro‘yxat",
     ["Belgi bilan ro‘yxat", "Sarlavha", "Faqat ramka"], 6),
    ("Ctrl+C", "Tanlangan matnni nusxalash tugmalar birikmasi",
     ["Joylashtirish", "Qirqish", "Saqlash"], 7),
    ("Ctrl+V", "Bufferdagi matnni joylashtirish tugmalar birikmasi",
     ["Nusxalash", "Qirqish", "Topish"], 7),
    ("Ctrl+X", "Tanlangan matnni qirqib bufferga olish",
     ["Saqlash", "Joylashtirish", "Topish"], 7),
    ("Ctrl+F", "Hujjat ichidan matn qidirish",
     ["Saqlash", "Yopish", "Joylashtirish"], 7),
    ("Ctrl+H", "Topib almashtirish (Find & Replace) oynasini ochish",
     ["Saqlash", "Topish", "Yopish"], 7),
    ("Ctrl+Z", "Oxirgi amalni bekor qilish",
     ["Qaytarish", "Saqlash", "Yopish"], 7),
    ("Ctrl+Y", "Bekor qilingan amalni qaytarish",
     ["Bekor qilish", "Saqlash", "Yopish"], 7),
    ("Ctrl+S", "Hujjatni saqlash",
     ["Yopish", "Yangi", "Topish"], 7),
    ("Ctrl+N", "Yangi hujjat ochish",
     ["Saqlash", "Yopish", "Topish"], 7),
    ("Ctrl+P", "Hujjatni chop etish",
     ["Saqlash", "Yopish", "Topish"], 7),
    ("Ctrl+A", "Hujjatdagi barcha matnni belgilash",
     ["Faqat satrni belgilash", "Saqlash", "Yopish"], 7),
    ("Spell Check (Imloni tekshirish)", "Matndagi imlo xatolarini topib ko‘rsatish",
     ["Faqat rang berish", "Faqat saqlash", "Faqat formula"], 8),
    ("Insert Image (Rasm qo‘shish)", "Hujjatga rasm qo‘shish amali",
     ["Faqat matn", "Faqat sarlavha", "Faqat raqam"], 8),
    ("Insert Table", "Hujjatga jadval qo‘shish",
     ["Faqat rasm", "Faqat ovoz", "Faqat sahifa raqami"], 8),
    ("Page Break", "Sahifani majburiy yangi sahifaga ajratish",
     ["Faqat raqam", "Faqat ramka", "Faqat sarlavha"], 9),
    ("Print Preview", "Chop etishdan oldin qanday ko‘rinishini ko‘rish",
     ["Faqat saqlash", "Faqat yopish", "Faqat ochish"], 8),
    ("Ribbon (lentasimon menyu)", "Word oynasining yuqorigi qismidagi vositalar paneli",
     ["Pastki status satri", "Sahifa raqami", "Faqat ranglar"], 1),
    ("Layout / Page Setup", "Sahifa o‘lchami va chegaralarini sozlash bo‘limi",
     ["Faqat shrift", "Faqat fayl saqlash", "Faqat sarlavha"], 9),
    ("Margin (Hoshiya)", "Sahifaning chetidan matngacha bo‘lgan bo‘sh masofa",
     ["Sarlavha", "Faqat raqam", "Faqat header"], 9),
    ("Orientation (Yo‘nalish)", "Sahifa portret yoki landshaft (gorizontal) ekanligi",
     ["Faqat shrift turi", "Faqat fayl nomi", "Faqat raqam"], 9),
]


def _info6_q1_pool() -> list[QItem]:
    pool: list[QItem] = []
    for c, d, w, l in INF_6_Q1_CONCEPTS:
        pool += _conceptual(c, d, w, lesson=l)

    def t_shortcut():
        cases = [
            ("Tanlangan matnni nusxalash", "Ctrl+C", ["Ctrl+V", "Ctrl+X", "Ctrl+S"]),
            ("Bufferdan joylashtirish", "Ctrl+V", ["Ctrl+C", "Ctrl+X", "Ctrl+S"]),
            ("Matnni qirqib olish", "Ctrl+X", ["Ctrl+V", "Ctrl+C", "Ctrl+S"]),
            ("Hujjatni saqlash", "Ctrl+S", ["Ctrl+P", "Ctrl+N", "Ctrl+Z"]),
            ("Yangi hujjat ochish", "Ctrl+N", ["Ctrl+S", "Ctrl+P", "Ctrl+Z"]),
            ("Chop etish", "Ctrl+P", ["Ctrl+S", "Ctrl+N", "Ctrl+Z"]),
            ("Hujjat ichidan qidirish", "Ctrl+F", ["Ctrl+H", "Ctrl+S", "Ctrl+N"]),
            ("Topib almashtirish (Replace)", "Ctrl+H", ["Ctrl+F", "Ctrl+S", "Ctrl+N"]),
            ("Bekor qilish (undo)", "Ctrl+Z", ["Ctrl+Y", "Ctrl+S", "Ctrl+N"]),
            ("Bekor qilinganni qaytarish (redo)", "Ctrl+Y", ["Ctrl+Z", "Ctrl+S", "Ctrl+N"]),
            ("Barcha matnni tanlash", "Ctrl+A", ["Ctrl+S", "Ctrl+N", "Ctrl+Z"]),
        ]
        c, ans, wrongs = random.choice(cases)
        return QItem(text=f"Wordda '{c}' uchun tugmalar birikmasi qaysi?",
                     answer=ans, wrongs=list(wrongs), difficulty=1, lesson=7)

    def t_format_action():
        cases = [
            ("Matnni qalin qilish", "Bold (Ctrl+B)", ["Italic", "Underline", "Strikethrough"]),
            ("Matnni kursiv qilish", "Italic (Ctrl+I)", ["Bold", "Underline", "Faqat rang"]),
            ("Matn tagiga chiziq", "Underline (Ctrl+U)", ["Bold", "Italic", "Faqat rang"]),
            ("Matnni o‘rtaga tekislash", "Center align (Ctrl+E)", ["Justify", "Right", "Left"]),
            ("Ikkala chetga tekislash", "Justify (Ctrl+J)", ["Center", "Right", "Left"]),
            ("Matnni o‘chirish (orqaga)", "Backspace tugmasi", ["Enter", "Tab", "Caps Lock"]),
        ]
        c, ans, wrongs = random.choice(cases)
        return QItem(text=f"Wordda '{c}' uchun qaysi amal eng to‘g‘ri?",
                     answer=ans, wrongs=list(wrongs), difficulty=1, lesson=4)

    def t_count_pages():
        words = random.randint(150, 1500)
        per_page = random.choice([200, 250, 300])
        pages = max(1, -(-words // per_page))
        return QItem(text=f"Hujjatda {words} ta so‘z va har sahifaga ~{per_page} so‘z sig‘adi. Taxminan necha sahifa kerak?",
                     answer=str(pages),
                     wrongs=[str(pages + 1), str(pages - 1 if pages > 1 else 2), str(per_page)],
                     difficulty=2, lesson=9)

    def t_count_chars():
        s = random.choice(["Salom Dunyo!", "Python — bu dasturlash tili.",
                           "Maktabga borish kerak.", "Kompyuter foydali asbob."])
        return QItem(text=f"Quyidagi matnda nechta belgi (probel bilan) bor?\n\n«{s}»",
                     answer=str(len(s)),
                     wrongs=[str(len(s) - 1), str(len(s) + 1), str(len(s.split()))],
                     difficulty=2, lesson=2)

    def t_count_words():
        s = random.choice([
            "Bugun maktabga keldim",
            "Kompyuter texnologiyalari juda foydali",
            "Word matn muharririda hujjat yaratamiz",
            "Internet kompyuterlarni birlashtirgan tarmoqdir",
            "Ona-Vatanim shirin",
        ])
        return QItem(text=f"Quyidagi matnda nechta so‘z bor?\n\n«{s}»",
                     answer=str(len(s.split())),
                     wrongs=[str(len(s.split()) + 1), str(len(s.split()) - 1), str(len(s))],
                     difficulty=2, lesson=2)

    def t_arith_word_eval():
        # 6-sinf darajasidagi mantiq amali (matn ichidagi son hisoblash emas)
        a = random.randint(2, 30); b = random.randint(2, 9)
        return QItem(text=f"Hujjatda raqamli ro‘yxat 1 dan {a*b} gacha. Agar har raqam alohida qatorga yozilsa, {b} ta raqam {a} ta jamoaga taqsimlasa, har jamoaga nechtadan tushadi?",
                     answer=str(b),
                     wrongs=[str(a), str(b - 1), str(a + b)],
                     difficulty=2, lesson=6)

    pool += _capped(t_shortcut)
    pool += _capped(t_format_action)
    pool += _capped(t_count_pages)
    pool += _capped(t_count_chars)
    pool += _capped(t_count_words)
    pool += _capped(t_arith_word_eval)

    discrete = [
        QItem("Word hujjatini saqlash uchun standart kengaytma qaysi?", ".docx",
              [".xlsx", ".pptx", ".txt"], 1, 1),
        QItem("Wordda yangi qatorga o‘tish uchun qaysi tugma?", "Enter",
              ["Tab", "Esc", "Caps Lock"], 1, 2),
        QItem("Wordda yangi sahifaga majburiy o‘tish uchun nima qilamiz?",
              "Insert → Page Break (yoki Ctrl+Enter)",
              ["Faqat Enter", "Faqat Tab", "Faqat Esc"], 2, 9),
        QItem("Word hujjatida sahifa raqamlarini avtomatik qo‘yish uchun qaysi bo‘lim ishlatiladi?",
              "Insert → Page Number",
              ["Home", "View", "Review"], 2, 5),
        QItem("Imloviy xatoga ega so‘z qaysi rangda chiziladi (standart)?",
              "Qizil to‘lqin chiziq", ["Yashil", "Sariq", "Ko‘k"], 2, 8),
        QItem("Wordda matn rangini o‘zgartirish uchun qaysi bo‘lim?",
              "Home → Font (A bilan rang) tugmasi",
              ["File", "Insert", "View"], 1, 3),
        QItem("Wordda jadval qo‘shish uchun qaysi menyu?",
              "Insert → Table",
              ["Home", "Layout", "Review"], 2, 8),
        QItem("Wordda hujjatni A4 dan A3 ga o‘zgartirish qayerda?",
              "Layout → Size",
              ["Home", "View", "Review"], 2, 9),
        QItem("Wordda Header qo‘shish uchun qaysi menyu?",
              "Insert → Header",
              ["Home", "View", "Review"], 2, 5),
        QItem("Wordda Footer'da odatda qaysi ma'lumot joylashtiriladi?",
              "Sahifa raqami yoki muallif ma'lumoti",
              ["Faqat sarlavha", "Faqat asosiy matn", "Faqat rasm"], 2, 5),
        QItem("Wordda matnni stol turli ranglar bilan ajratish qanday amalga oshiriladi?",
              "Highlight (Marker) asbobi orqali",
              ["Faqat Page Setup", "Faqat Print", "Faqat Save As"], 2, 3),
        QItem("Word hujjatida fonni ko‘rinmas qiluvchi rang qaysi?",
              "Oq (sahifa fon rangi)",
              ["Qora", "Qizil", "Yashil"], 1, 3),
        QItem("Wordda matn shrifti default odatda qaysi?",
              "Calibri (yoki Times New Roman)",
              ["Wingdings", "Symbol", "ASCII"], 2, 3),
        QItem("Word hujjatini PDF formatida saqlash uchun qaysi amal?",
              "File → Save As → PDF",
              ["Faqat Ctrl+S", "Faqat Ctrl+C", "Faqat Ctrl+P"], 2, 1),
        QItem("Bir hujjatda bir nechta shrift turli xil bo‘lishi mumkinmi?",
              "Ha — har bir abzasga o‘zining shriftini berish mumkin",
              ["Yo‘q — faqat bittadan", "Faqat 2 ta", "Faqat keyingi sahifada"], 2, 3),
        QItem("Hujjatda imloviy xatolarni avtomatik to‘g‘rilab beradigan funksiya?",
              "AutoCorrect", ["Find", "Replace", "Save"], 3, 8),
        QItem("Wordda Find&Replace bilan barcha 'kompyuter' so‘zini 'Computer' bilan almashtirish uchun?",
              "Replace All tugmasini bosish",
              ["Faqat Ctrl+S", "Faqat Esc", "Faqat Tab"], 2, 7),
        QItem("Wordda matn tanlamasdan Ctrl+B bosilsa nima sodir bo‘ladi?",
              "Kursor bo‘lgan joydan boshlab keyingi matn qalin yoziladi",
              ["Hech narsa", "Hujjat yopiladi", "Fayl saqlanadi"], 3, 7),
        QItem("Wordda 'Heading 1' uslubi qaysi maqsad uchun?",
              "Asosiy bo‘lim sarlavhasi uchun",
              ["Oddiy matn uchun", "Faqat sahifa raqami", "Faqat ranglar"], 2, 2),
        QItem("Wordda hujjatni boshqalarga yuborish uchun eng qulay format qaysi?",
              ".pdf (qabul qiluvchining qurilmasidan qat'iy nazar)",
              [".docx", ".xlsx", ".png"], 2, 1),
    ]
    pool += discrete
    random.shuffle(pool)
    return pool


# ─── INFORMATIKA — 6-sinf 2-chorak ───────────────────────────────────────────
# Mavzu: Excel kengaytirilgan — sort, filter, $A$1 absolyut, IF, formulalar.

INF_6_Q2_CONCEPTS = [
    ("Excel formulasi", "= bilan boshlanadigan hisob-kitob ifodasi",
     ["Faqat oddiy matn", "Faqat rasm", "Faqat raqam"], 1),
    ("Nisbiy manzil (A1)", "Formulani ko‘chirganda manzil ham siljiydi",
     ["Hech qachon o‘zgarmaydi", "Faqat satr o‘zgaradi", "Faqat ustun o‘zgaradi"], 2),
    ("Absolyut manzil ($A$1)", "Formulani ko‘chirganda manzil o‘zgarmaydi",
     ["Doim siljiydi", "Faqat satr siljiydi", "Faqat ustun siljiydi"], 2),
    ("$A1", "Aralash manzil — ustun qotirilgan, satr nisbiy",
     ["Doim absolyut", "Doim nisbiy", "Faqat satr qotirilgan"], 2),
    ("A$1", "Aralash manzil — satr qotirilgan, ustun nisbiy",
     ["Doim absolyut", "Doim nisbiy", "Faqat ustun qotirilgan"], 2),
    ("=IF(shart;a;b)", "Shart bajarilsa a, aks holda b ni qaytaruvchi formula",
     ["Faqat yig‘indi", "Faqat o‘rtacha", "Faqat eng katta"], 3),
    ("=AND(a;b)", "Ikkala shart ham TRUE bo‘lsa TRUE qaytaradi",
     ["Bittasi yetarli", "Hech qachon TRUE bo‘lmaydi", "Faqat son qaytaradi"], 3),
    ("=OR(a;b)", "Bittasi TRUE bo‘lsa TRUE qaytaradi",
     ["Faqat ikkalasi TRUE", "Hech qachon TRUE", "Faqat matn qaytaradi"], 3),
    ("=NOT(a)", "TRUE/FALSE qiymatini teskariga o‘zgartirish",
     ["Yig‘indi qaytaradi", "Faqat matn", "O‘zgartirmaydi"], 3),
    ("=COUNTIF(diapazon;shart)", "Diapazonda shartni qanoatlantirgan kataklarni sanaydi",
     ["Yig‘indini qaytaradi", "Faqat MAX qaytaradi", "Faqat MIN qaytaradi"], 4),
    ("=SUMIF(diapazon;shart;sumdiap)", "Shartga mos kataklar yig‘indisini qaytaradi",
     ["Faqat sanaydi", "Faqat MAX qaytaradi", "Faqat MIN qaytaradi"], 4),
    ("=AVERAGEIF(...)", "Shartga mos kataklar o‘rtachasi",
     ["Faqat sanaydi", "Faqat yig‘indi", "Faqat MIN"], 4),
    ("Sort A→Z", "Ma'lumotlarni o‘sish tartibida tartiblash",
     ["Faqat o‘chirish", "Faqat saqlash", "Faqat ranglar"], 5),
    ("Sort Z→A", "Ma'lumotlarni kamayish tartibida tartiblash",
     ["Faqat o‘chirish", "Faqat saqlash", "Faqat ranglar"], 5),
    ("Filter (Saralash)", "Kerakli ma'lumotlarni tanlab ko‘rsatish",
     ["Faqat o‘chirish", "Faqat saqlash", "Faqat ranglar"], 6),
    ("Conditional Formatting", "Shartga qarab katak rangini avtomatik o‘zgartirish",
     ["Faqat shrift turi", "Faqat saqlash", "Faqat o‘chirish"], 6),
    ("Pivot Table", "Ma'lumotlarni guruhlab tahlil qiluvchi maxsus jadval",
     ["Oddiy jadval", "Brauzer", "Diagramma turi"], 7),
    ("Chart Wizard", "Diagrammani yaratish bo‘yicha qadam-baqadam ko‘rsatma",
     ["Faqat ranglash", "Faqat saqlash", "Faqat o‘chirish"], 7),
    ("Data Validation", "Katakka faqat ruxsat etilgan qiymat kiritishni cheklovchi vosita",
     ["Faqat ranglash", "Faqat o‘chirish", "Faqat saqlash"], 8),
    ("Freeze Panes", "Aylantirganda ham ustun/sarlavha qator joyida turishi",
     ["Faqat ranglash", "Faqat o‘chirish", "Faqat saqlash"], 8),
    ("Group", "Bir nechta satr/ustunni yig‘ib qisqartirib ko‘rsatish",
     ["Faqat o‘chirish", "Faqat saqlash", "Faqat ranglar"], 8),
    ("Cell merge (birlashtirish)", "Bir nechta katakni bittaga birlashtirish",
     ["Bo‘lish", "O‘chirish", "Saqlash"], 9),
    ("Wrap Text", "Uzun matnni katakda qatorga sig‘dirish",
     ["Faqat saqlash", "Faqat o‘chirish", "Faqat ranglar"], 9),
    ("Hyperlink", "Katakka veb-havola qo‘shish",
     ["Faqat rasm", "Faqat raqam", "Faqat saqlash"], 9),
    ("=CONCATENATE(a;b)", "Ikki matnni birlashtiruvchi formula",
     ["Sonlarni yig‘ish", "Faqat MAX", "Faqat MIN"], 4),
    ("=LEN(matn)", "Matn uzunligini topuvchi formula",
     ["Yig‘indi", "Eng katta", "Eng kichik"], 4),
    ("=UPPER(matn)", "Matnni katta harflarga o‘giruvchi formula",
     ["Kichikka o‘girish", "Faqat sanash", "Faqat yig‘indi"], 4),
    ("=LOWER(matn)", "Matnni kichik harflarga o‘giruvchi formula",
     ["Kattaga o‘girish", "Faqat sanash", "Faqat yig‘indi"], 4),
    ("=ROUND(son;n)", "Sonni n xona aniqlikda yaxlitlovchi formula",
     ["Yig‘indini hisoblash", "Faqat MAX", "Faqat MIN"], 4),
    ("=NOW()", "Hozirgi sana va vaqtni qaytaruvchi formula",
     ["Faqat sana", "Faqat soat", "Faqat o‘zgaruvchi qiymat"], 4),
    ("=TODAY()", "Bugungi sanani qaytaruvchi formula",
     ["Vaqtni ham qaytaradi", "Faqat soat", "Faqat doimiy son"], 4),
    ("=VLOOKUP(...)", "Jadvalda vertikal qidirish formulasi",
     ["Gorizontal qidirish", "Faqat MAX", "Faqat saqlash"], 7),
    ("=HLOOKUP(...)", "Jadvalda gorizontal qidirish formulasi",
     ["Vertikal qidirish", "Faqat MIN", "Faqat saqlash"], 7),
    ("Range A1:B5", "A1 dan B5 gacha bo‘lgan to‘rtburchak diapazon",
     ["Faqat A1", "Faqat B5", "Faqat satr"], 1),
    ("Defined Name", "Diapazonga nom berib, formulalarda ishlatish",
     ["Faqat oddiy katak", "Faqat formula", "Faqat saqlash"], 8),
    ("Print Area", "Faqat tanlangan sohani chop etish belgisi",
     ["Faqat saqlash", "Faqat o‘chirish", "Faqat ranglar"], 9),
    ("Page Layout", "Excel sahifa parametrlari (margins, orientation)",
     ["Faqat formula", "Faqat saqlash", "Faqat o‘chirish"], 9),
    ("Tartiblash 'Smart' funksiya", "Ma'lumotlar tipini o‘zi aniqlab tartiblash",
     ["Faqat ranglash", "Faqat saqlash", "Faqat o‘chirish"], 5),
    ("Filter — Top 10", "Eng katta yoki kichik 10 qiymatni saralash",
     ["Faqat o‘chirish", "Faqat saqlash", "Faqat ranglar"], 6),
    ("Subtotal", "Guruhlangan ma'lumotlar uchun oraliq jami",
     ["Faqat MAX", "Faqat MIN", "Faqat oddiy yig‘indi"], 7),
]


def _info6_q2_pool() -> list[QItem]:
    pool: list[QItem] = []
    for c, d, w, l in INF_6_Q2_CONCEPTS:
        pool += _conceptual(c, d, w, lesson=l)

    def t_if_eval():
        a = random.randint(1, 50); b = random.randint(1, 50)
        cmp = random.choice([">", "<", ">=", "<=", "="])
        if cmp == ">":
            cond = a > b
        elif cmp == "<":
            cond = a < b
        elif cmp == ">=":
            cond = a >= b
        elif cmp == "<=":
            cond = a <= b
        else:
            cond = a == b
        return QItem(text=f"Excelda `=IF({a}{cmp}{b};\"HA\";\"YO‘Q\")` natijasi nima?",
                     answer="HA" if cond else "YO‘Q",
                     wrongs=["HA" if not cond else "YO‘Q", "0", "Xatolik"],
                     difficulty=2, lesson=3)

    def t_countif():
        nums = [random.randint(1, 30) for _ in range(8)]
        thr = random.randint(5, 25)
        cnt = sum(1 for x in nums if x > thr)
        return QItem(text=f"Excelda diapazonda `{nums}` mavjud. `=COUNTIF` bilan `>{thr}` shartga mos kataklar nechta?",
                     answer=str(cnt),
                     wrongs=[str(cnt + 1), str(cnt - 1 if cnt > 0 else 1), str(thr)],
                     difficulty=3, lesson=4)

    def t_sumif():
        nums = [random.randint(1, 30) for _ in range(7)]
        thr = random.randint(5, 25)
        s = sum(x for x in nums if x > thr)
        return QItem(text=f"Excelda diapazonda `{nums}`. `=SUMIF` bilan `>{thr}` shartga mos qiymatlar yig‘indisi nechchi?",
                     answer=str(s),
                     wrongs=[str(s + 1), str(sum(nums)), str(max(nums))],
                     difficulty=3, lesson=4)

    def t_concat():
        a = random.choice(["Ali", "Olim", "Nodira", "Sardor"])
        b = random.choice(["jon", "bek", "qiz", "boy"])
        return QItem(text=f"Excelda `=CONCATENATE(\"{a}\";\"{b}\")` natijasi nima?",
                     answer=f"{a}{b}",
                     wrongs=[f"{b}{a}", a, b],
                     difficulty=2, lesson=4)

    def t_len():
        s = random.choice(["maktab", "Excel formula", "kompyuter savodxonligi", "informatika fani"])
        return QItem(text=f"Excelda `=LEN(\"{s}\")` natijasi nima?",
                     answer=str(len(s)),
                     wrongs=[str(len(s) + 1), str(len(s) - 1), str(len(s.split()))],
                     difficulty=2, lesson=4)

    def t_round():
        n = round(random.uniform(1, 100), 3)
        d = random.choice([0, 1, 2])
        ans = round(n, d)
        return QItem(text=f"Excelda `=ROUND({n};{d})` natijasi nima?",
                     answer=str(ans),
                     wrongs=[str(round(n, d + 1)), str(int(n)), str(round(n, max(0, d - 1)))],
                     difficulty=2, lesson=4)

    def t_abs_address():
        col = random.choice(list("ABCD"))
        row = random.randint(1, 9)
        return QItem(text=f"Formulani ko‘chirsa ham '{col}{row}' o‘zgarmasligi uchun manzilni qanday yozish kerak?",
                     answer=f"${col}${row}",
                     wrongs=[f"{col}{row}", f"{col}${row}", f"${col}{row}"],
                     difficulty=2, lesson=2)

    def t_logic():
        a = random.choice([True, False])
        b = random.choice([True, False])
        op = random.choice(["AND", "OR"])
        ans = (a and b) if op == "AND" else (a or b)
        return QItem(text=f"Excelda `={op}({str(a).upper()};{str(b).upper()})` natijasi nima?",
                     answer=str(ans).upper(),
                     wrongs=[str(not ans).upper(), "0", "Xatolik"],
                     difficulty=3, lesson=3)

    pool += _capped(t_if_eval)
    pool += _capped(t_countif)
    pool += _capped(t_sumif)
    pool += _capped(t_concat)
    pool += _capped(t_len)
    pool += _capped(t_round)
    pool += _capped(t_abs_address)
    pool += _capped(t_logic)

    discrete = [
        QItem("Excelda nisbiy manzil (A1) formulasini past katakka ko‘chirsak nima sodir bo‘ladi?",
              "Manzil A2 ga siljiydi", ["O‘zgarmaydi", "B1 ga o‘tadi", "Xatolik beradi"], 2, 2),
        QItem("Sort qilish uchun avval nima qilish kerak?",
              "Sortlanadigan diapazonni belgilash",
              ["Faqat saqlash", "Faqat formula yozish", "Faqat ranglash"], 2, 5),
        QItem("Filter qo‘yilganda nima sodir bo‘ladi?",
              "Faqat shartga mos satrlar ko‘rinadi, qolganlari yashirinadi",
              ["O‘chirib tashlanadi", "Hech narsa o‘zgarmaydi", "Faqat ranglar o‘zgaradi"], 2, 6),
        QItem("Excelda VLOOKUP qachon ishlatiladi?",
              "Jadval birinchi ustunidan qiymat izlash uchun",
              ["Faqat ranglash uchun", "Faqat saqlash uchun", "Faqat sortlash uchun"], 3, 7),
        QItem("Conditional Formatting nimaga xizmat qiladi?",
              "Shartga qarab katak rangini avtomatik o‘zgartirish",
              ["Faqat saqlash", "Faqat formula", "Faqat o‘chirish"], 2, 6),
        QItem("Excelda jadval birinchi qatorini doim ko‘rinib turishi uchun nima qilamiz?",
              "Freeze Panes — Freeze Top Row",
              ["Faqat saqlash", "Faqat o‘chirish", "Faqat ranglash"], 3, 8),
        QItem("Bir nechta katakni birlashtirib bitta katakka aylantirish uchun?",
              "Merge & Center",
              ["Sort", "Filter", "Print"], 2, 9),
        QItem("Excelda diagramma turini o‘zgartirish uchun?",
              "Diagrammani belgilab → Design → Change Chart Type",
              ["Faqat Save As", "Faqat Print", "Faqat Filter"], 3, 7),
        QItem("Pivot Table qachon foydali?",
              "Katta hajmdagi ma'lumotlarni guruhlab tahlil qilish",
              ["Faqat ranglash uchun", "Faqat saqlash uchun", "Faqat brauzerda"], 3, 7),
        QItem("=SUMIFS va =SUMIF orasidagi farq?",
              "SUMIFS bir nechta shartni qabul qiladi",
              ["Bir xil", "SUMIFS faqat MAX qaytaradi", "SUMIFS faqat matn"], 3, 4),
        QItem("=AVERAGE va =AVERAGEIF orasidagi farq?",
              "AVERAGEIF shartga mos qiymatlar o‘rtachasini hisoblaydi",
              ["Bir xil", "AVERAGEIF faqat matn", "AVERAGEIF faqat MAX"], 3, 4),
        QItem("Excelda satrni o‘chirib tashlash uchun nima qilamiz?",
              "Satr raqamiga o‘ng tugma → Delete",
              ["Faqat Ctrl+Z", "Faqat Ctrl+S", "Faqat Esc"], 1, 5),
        QItem("Excelda data validation nima uchun?",
              "Foydalanuvchi kiritadigan qiymatlarni cheklash uchun",
              ["Faqat ranglash", "Faqat saqlash", "Faqat o‘chirish"], 3, 8),
        QItem("Excelda satr balandligini avtomatik moslash uchun?",
              "Satr chegarasiga ikki marta bosish (auto-fit)",
              ["Faqat Ctrl+S", "Faqat Esc", "Faqat Save As"], 2, 9),
        QItem("Print Area belgilangan bo‘lsa nima sodir bo‘ladi?",
              "Faqat tanlangan diapazon chop etiladi",
              ["Hammasi chop etiladi", "Hech narsa", "Faqat sarlavha"], 2, 9),
        QItem("Hyperlink kataklarni qaysi shaklga olib o‘tadi?",
              "Brauzerda berilgan URL ga",
              ["Faqat boshqa katakka", "Faqat saqlash", "Faqat o‘chirish"], 3, 9),
        QItem("Defined Name qo‘yishdan maqsad?",
              "Diapazonga osongina nom berib, formulalarda ishlatish",
              ["Faqat ranglash", "Faqat saqlash", "Faqat o‘chirish"], 3, 8),
        QItem("Top 10 filtri qaysi qiymatni qaytaradi?",
              "Eng katta yoki kichik 10 ta qiymatni",
              ["Faqat 1 ta", "Faqat ranglar", "Faqat sarlavha"], 2, 6),
        QItem("Diagrammada ulushlarni aks ettirishga eng mosi?",
              "Pie (doira) chart",
              ["Bar chart", "Line chart", "Scatter"], 2, 7),
        QItem("Excelda ma'lumotni gruxlash (Group) qachon foydali?",
              "Bir nechta satr/ustunni yig‘ib qisqartirish kerak bo‘lganda",
              ["Faqat ranglash", "Faqat o‘chirish", "Faqat saqlash"], 3, 8),
    ]
    pool += discrete
    random.shuffle(pool)
    return pool
