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


# ─── INFORMATIKA — 6-sinf 3-chorak ───────────────────────────────────────────
# Mavzu: Algoritm, blok-sxema, shart, takrorlash (sodda mantiqlar).

INF_6_Q3_CONCEPTS = [
    ("Algoritm", "Aniq maqsadga erishish uchun amallar ketma-ketligi",
     ["Faqat kompyuter qismi", "Faqat fayl turi", "Faqat brauzer"], 1),
    ("Algoritmning xossalari", "Aniqlik, tugallanganlik, ommaviylik, samaradorlik",
     ["Faqat tezlik", "Faqat ranglar", "Faqat fayl nomi"], 1),
    ("Aniqlik xossasi", "Har bir qadam tushunarli va aniq bo‘lishi",
     ["Faqat tezlik", "Faqat ranglar", "Faqat fayl turi"], 1),
    ("Tugallanganlik xossasi", "Algoritm cheklangan qadamdan keyin yakunlanishi",
     ["Cheksiz davom etadi", "Faqat ranglar", "Faqat fayl turi"], 1),
    ("Ommaviylik xossasi", "Bir xil sinfdagi har qanday masalaga qo‘llanishi",
     ["Faqat bitta masala", "Faqat ranglar", "Faqat fayl turi"], 1),
    ("Blok-sxema", "Algoritmning grafik (rasm) ko‘rinishi",
     ["Faqat matn", "Faqat fayl", "Faqat brauzer"], 2),
    ("Boshlanish bloki (oval)", "Blok-sxemaning boshlanish belgisi",
     ["Tugatish", "Shart", "Amal"], 2),
    ("Tugatish bloki (oval)", "Blok-sxemaning yakunlash belgisi",
     ["Boshlanish", "Shart", "Amal"], 2),
    ("Amal bloki (to‘rtburchak)", "Blok-sxemada bajariladigan ish belgisi",
     ["Boshlanish", "Tugatish", "Shart"], 2),
    ("Shart bloki (romb)", "Blok-sxemada tekshiriladigan shart belgisi",
     ["Amal", "Tugatish", "Boshlanish"], 2),
    ("Kirish/Chiqish bloki (parallelogramm)", "Ma'lumot kiritish yoki chiqarish belgisi",
     ["Shart", "Tugatish", "Amal"], 2),
    ("Chiziqli (linear) algoritm", "Amallar ketma-ket bajariladigan algoritm",
     ["Tarmoqlanuvchi", "Takrorlanuvchi", "Faqat ranglar"], 3),
    ("Tarmoqlanuvchi (shartli) algoritm", "Shartga qarab turli yo‘l tanlanadigan algoritm",
     ["Chiziqli", "Faqat takror", "Faqat matn"], 3),
    ("Takrorlanuvchi (siklik) algoritm", "Bir nechta amal qaytariladigan algoritm",
     ["Faqat chiziqli", "Faqat shartli", "Faqat ranglar"], 3),
    ("If (Agar)", "Shart bajarilsa, amalni bajaruvchi shartli operator",
     ["Faqat takror", "Faqat ranglar", "Faqat fayl"], 4),
    ("Else (Aks holda)", "If sharti bajarilmasa, ishlovchi tarmoq",
     ["Faqat shart", "Faqat takror", "Faqat ranglar"], 4),
    ("For (sikl)", "Aniq sondagi qadamlardan iborat takrorlash",
     ["Faqat shart", "Faqat chiziqli", "Faqat ranglar"], 5),
    ("While (sikl)", "Shart bajarilgancha takrorlash",
     ["Faqat for", "Faqat shart", "Faqat ranglar"], 5),
    ("Repeat (takrorlash)", "Berilgan miqdorda yoki shartgacha amalni qaytarish",
     ["Faqat ranglar", "Faqat shart", "Faqat amal"], 5),
    ("Break", "Sikldan oldin chiqib ketish operatori",
     ["Davom etish", "Saqlash", "Yopish"], 5),
    ("Continue", "Sikl ichida joriy iteratsiyani o‘tkazib yuborish",
     ["Sikldan chiqish", "Saqlash", "Faqat ranglar"], 5),
    ("Scratch", "Bolalar uchun blok asosida dasturlash muhiti",
     ["Faqat oddiy matn muharriri", "Faqat brauzer", "Faqat antivirus"], 6),
    ("Sprite (Scratch)", "Scratchdagi harakatlanuvchi obyekt (rasm)",
     ["Faqat fon", "Faqat blok", "Faqat fayl"], 6),
    ("Stage (Sahna)", "Scratchdagi sprite-lar harakat qiluvchi maydon",
     ["Faqat sprite", "Faqat blok", "Faqat fayl"], 6),
    ("Move 10 steps (Scratch)", "Sprite-ni 10 qadam siljitish bloki",
     ["Faqat ranglar", "Faqat ovoz", "Faqat saqlash"], 6),
    ("When green flag clicked", "Yashil bayroq bosilganda dastur ishga tushish bloki",
     ["Faqat saqlash", "Faqat ovoz", "Faqat ranglar"], 6),
    ("Repeat n (Scratch)", "Ichidagi bloklarni n marta takrorlash",
     ["Faqat shart", "Faqat saqlash", "Faqat ranglar"], 6),
    ("If/then (Scratch)", "Shart bajarilsa ichidagi bloklarni bajarish",
     ["Faqat takror", "Faqat saqlash", "Faqat ranglar"], 6),
    ("Forever (Scratch)", "Cheksiz takrorlash bloki",
     ["Faqat n marta", "Faqat shart", "Faqat saqlash"], 6),
    ("Pseudokod", "Algoritmni so‘zlar bilan tasvirlovchi shartli yozuv",
     ["Bevosita kompyuter dasturi", "Faqat blok-sxema", "Faqat rasm"], 7),
    ("Dasturlash tili", "Kompyuterga buyruq berish uchun maxsus til",
     ["Faqat algoritm", "Faqat brauzer", "Faqat antivirus"], 7),
    ("Buyruq", "Bajariladigan bitta amalni bildiruvchi yozuv",
     ["Faqat fayl", "Faqat ranglar", "Faqat saqlash"], 7),
    ("Sintaksis", "Til qoidasi — qanday yozish kerakligi",
     ["Faqat ma'no", "Faqat ranglar", "Faqat fayl"], 7),
    ("Bug (xato)", "Dasturdagi nosozlik yoki noto‘g‘ri ishlash",
     ["Faqat ovoz", "Faqat ranglar", "Faqat fayl"], 7),
    ("Debugging", "Xatolarni topish va to‘g‘rilash jarayoni",
     ["Faqat saqlash", "Faqat ranglar", "Faqat ovoz"], 7),
    ("Variable (o‘zgaruvchi)", "Qiymat saqlash uchun nomlangan joy",
     ["Faqat blok", "Faqat fayl", "Faqat shart"], 8),
    ("Input (kirish)", "Foydalanuvchidan ma'lumot olish",
     ["Chiqish", "Faqat shart", "Faqat saqlash"], 8),
    ("Output (chiqish)", "Foydalanuvchiga ma'lumot ko‘rsatish",
     ["Kirish", "Faqat shart", "Faqat saqlash"], 8),
    ("Logical operator (mantiqiy amal)", "AND/OR/NOT kabi amallar",
     ["Faqat son", "Faqat matn", "Faqat ranglar"], 4),
    ("Modul (mod) amali", "Bo‘lishdan qoldiqni topuvchi amal",
     ["Faqat butun bo‘linmasi", "Faqat ko‘paytirish", "Faqat ayirish"], 8),
]


def _info6_q3_pool() -> list[QItem]:
    pool: list[QItem] = []
    for c, d, w, l in INF_6_Q3_CONCEPTS:
        pool += _conceptual(c, d, w, lesson=l)

    def t_sum_1_to_n():
        n = random.randint(5, 50)
        return QItem(text=f"1 dan n gacha sonlar yig‘indisini hisoblovchi algoritm bajarildi.\n\nn = {n}\n\nNatija nima?",
                     answer=str(n * (n + 1) // 2),
                     wrongs=[str(n * n), str(n * (n - 1) // 2), str(n + 1)],
                     difficulty=3, lesson=5)

    def t_step_seq():
        start = random.randint(1, 20); step = random.randint(2, 8); k = random.randint(4, 12)
        last = start + step * (k - 1)
        return QItem(text=f"Algoritm: start={start} dan boshlab har safar +{step} oshirib k={k} marta yozildi. Oxirgi qiymat?",
                     answer=str(last),
                     wrongs=[str(last - step), str(start * step), str(start + k)],
                     difficulty=3, lesson=5)

    def t_if_eval():
        a = random.randint(-50, 50); b = random.randint(-50, 50)
        return QItem(text=f"Algoritm:\n```\nIF a > b THEN\n   chiqar 'A katta'\nELIF a == b THEN\n   chiqar 'Teng'\nELSE\n   chiqar 'B katta'\n```\nKirish: a={a}, b={b}\nNatija nima?",
                     answer="A katta" if a > b else ("Teng" if a == b else "B katta"),
                     wrongs=["A katta", "B katta", "Teng"],
                     difficulty=2, lesson=4)

    def t_count_in_range():
        n = random.randint(10, 80); m = random.randint(2, 9)
        return QItem(text=f"Algoritm: 1 dan {n} gacha sonlar ichidan {m} ga karralilarini sanaymiz. Nechta son chiqadi?",
                     answer=str(n // m),
                     wrongs=[str(n // m + 1), str(n - m), str(n + m)],
                     difficulty=3, lesson=8)

    def t_factorial_simple():
        n = random.randint(2, 6)
        f = 1
        for i in range(1, n + 1):
            f *= i
        return QItem(text=f"Algoritm: 1 dan n gacha sonlarni ko‘paytiramiz (faktorial). n={n}. Natija?",
                     answer=str(f),
                     wrongs=[str(f + 1), str(f * 2), str(n * n)],
                     difficulty=3, lesson=5)

    def t_block_shape():
        cases = [
            ("Boshlanish belgisi", "Oval", ["To‘rtburchak", "Romb", "Parallelogramm"]),
            ("Tugatish belgisi", "Oval", ["Romb", "Parallelogramm", "To‘rtburchak"]),
            ("Amal belgisi", "To‘rtburchak", ["Oval", "Romb", "Parallelogramm"]),
            ("Shart belgisi", "Romb", ["To‘rtburchak", "Oval", "Parallelogramm"]),
            ("Kirish/chiqish belgisi", "Parallelogramm", ["Romb", "Oval", "To‘rtburchak"]),
        ]
        c, ans, wrongs = random.choice(cases)
        return QItem(text=f"Blok-sxemada '{c}' qaysi shakl bilan tasvirlanadi?",
                     answer=ans, wrongs=list(wrongs), difficulty=2, lesson=2)

    def t_repeat_eval():
        n = random.randint(3, 8)
        return QItem(text=f"Scratch: `repeat {n}: move 10 steps`. Sprite jami necha qadam yuradi?",
                     answer=str(n * 10),
                     wrongs=[str(n + 10), str(n * 5), str(n)],
                     difficulty=2, lesson=6)

    def t_mod_eval():
        a = random.randint(10, 99); b = random.randint(2, 9)
        return QItem(text=f"`{a} MOD {b}` (qoldiq) natijasi nima?",
                     answer=str(a % b),
                     wrongs=[str(a // b), str(a + b), str(a - b)],
                     difficulty=2, lesson=8)

    def t_division():
        a = random.randint(20, 99); b = random.randint(2, 9)
        return QItem(text=f"`{a} DIV {b}` (butun bo‘linmasi) natijasi nima?",
                     answer=str(a // b),
                     wrongs=[str(a % b), str(a / b), str(a * b)],
                     difficulty=2, lesson=8)

    pool += _capped(t_sum_1_to_n)
    pool += _capped(t_step_seq)
    pool += _capped(t_if_eval)
    pool += _capped(t_count_in_range)
    pool += _capped(t_factorial_simple)
    pool += _capped(t_block_shape)
    pool += _capped(t_repeat_eval)
    pool += _capped(t_mod_eval)
    pool += _capped(t_division)

    discrete = [
        QItem("Algoritmning birinchi xossasi qaysi?", "Aniqlik (har qadam tushunarli)",
              ["Faqat tezlik", "Faqat ranglar", "Faqat fayl"], 1, 1),
        QItem("Algoritm cheksiz davom etadi degan ma'no — bu xato. Qaysi xossasi buzilgan?",
              "Tugallanganlik xossasi",
              ["Aniqlik", "Ommaviylik", "Samaradorlik"], 2, 1),
        QItem("Blok-sxemada strelkalar nimani ko‘rsatadi?",
              "Algoritm qadamlari ketma-ketligini",
              ["Faqat ranglar", "Faqat fayl turini", "Faqat sonni"], 2, 2),
        QItem("Tarmoqlanuvchi algoritmda qanday blok bor bo‘lishi shart?",
              "Shart bloki (romb)",
              ["Faqat amal", "Faqat boshlanish", "Faqat tugatish"], 2, 3),
        QItem("Takrorlanuvchi algoritmda nima muhim?",
              "Sikl chiqish sharti yoki qadamlar soni",
              ["Faqat saqlash", "Faqat ranglar", "Faqat oddiy amal"], 3, 3),
        QItem("Pseudokodda 'IF x > 0' degan ko‘rinish nimani anglatadi?",
              "Agar x noldan katta bo‘lsa",
              ["Doim bajariladi", "Hech qachon bajarilmaydi", "Faqat takror"], 2, 7),
        QItem("Scratchda dastur boshlanishini bildiruvchi blok qaysi?",
              "When green flag clicked",
              ["Stop", "Forever", "If"], 1, 6),
        QItem("Scratchda Sprite-ni boshqarish uchun qaysi tugmalar to‘plami ishlatilishi mumkin?",
              "Klaviatura strelkalari yoki maxsus tugmalar",
              ["Faqat sichqoncha", "Faqat ovoz", "Faqat ranglar"], 2, 6),
        QItem("Algoritmni ishga tushiruvchi shaxs kim?",
              "Foydalanuvchi (yoki kompyuter)",
              ["Faqat dasturchi", "Faqat o‘qituvchi", "Hech kim"], 2, 1),
        QItem("Algoritm va dastur orasidagi farq nima?",
              "Algoritm — g‘oya, dastur — uning kompyuter tilidagi bajariluvchi shakli",
              ["Bir xil", "Algoritm faqat matn", "Dastur faqat blok-sxema"], 3, 7),
        QItem("If-Else bloki qaysi turdagi algoritmga tegishli?",
              "Tarmoqlanuvchi (shartli)",
              ["Faqat chiziqli", "Faqat takror", "Faqat fayl"], 1, 4),
        QItem("Algoritm samaradorligi nima bilan o‘lchanadi?",
              "Bajarilish vaqti va xotira sarfi",
              ["Faqat ranglar", "Faqat fayl hajmi", "Faqat ovoz"], 3, 1),
        QItem("Mantiqiy AND amali qachon TRUE qaytaradi?",
              "Ikkala operand ham TRUE bo‘lganda",
              ["Bittasi TRUE bo‘lsa", "Hech qachon", "Faqat oxirgisi TRUE"], 2, 4),
        QItem("Mantiqiy OR amali qachon TRUE qaytaradi?",
              "Bittasi TRUE bo‘lsa yetarli",
              ["Faqat ikkalasi TRUE", "Hech qachon", "Faqat birinchisi TRUE"], 2, 4),
        QItem("Mantiqiy NOT amali nima qiladi?",
              "TRUE/FALSE ni teskariga o‘zgartiradi",
              ["Yig‘adi", "Ko‘paytiradi", "Hech narsa qilmaydi"], 2, 4),
        QItem("Algoritmlash boshlangich vositasi sifatida qaysi muhit eng mos?",
              "Scratch yoki blok-sxema",
              ["Faqat Word", "Faqat Excel", "Faqat brauzer"], 2, 6),
        QItem("Sikl ichida 'break' bajarilsa nima sodir bo‘ladi?",
              "Sikl darhol to‘xtaydi va undan keyingi qatorga o‘tiladi",
              ["Sikl yangidan boshlanadi", "Hech narsa o‘zgarmaydi", "Dastur to‘xtaydi"], 3, 5),
        QItem("Sikl ichida 'continue' bajarilsa nima sodir bo‘ladi?",
              "Joriy iteratsiya o‘tkazib yuboriladi, keyingisi boshlanadi",
              ["Sikl tugaydi", "Hech narsa o‘zgarmaydi", "Dastur to‘xtaydi"], 3, 5),
        QItem("Algoritmni testlash nima uchun kerak?",
              "Xatolarni topish va to‘g‘rilash uchun",
              ["Faqat ranglash uchun", "Faqat saqlash uchun", "Faqat ovoz uchun"], 2, 7),
        QItem("Bug topib tuzatish jarayoni qanday nomlanadi?",
              "Debugging",
              ["Saqlash", "Yopish", "Tartiblash"], 2, 7),
    ]
    pool += discrete
    random.shuffle(pool)
    return pool


# ─── INFORMATIKA — 6-sinf 4-chorak ───────────────────────────────────────────
# Mavzu: PowerPoint, taqdimot, slayd, transition, animation.

INF_6_Q4_CONCEPTS = [
    ("Microsoft PowerPoint", "Taqdimot (slayd-shou) yaratuvchi dastur",
     ["Brauzer", "Antivirus", "Excel"], 1),
    (".pptx", "PowerPoint taqdimoti uchun kengaytma",
     [".docx", ".xlsx", ".png"], 1),
    ("Slayd (Slide)", "Taqdimotning bitta sahifasi",
     ["Excel kataki", "Word abzasi", "Brauzer"], 1),
    ("Slayd-shou (Slideshow)", "Slaydlarni ekranga ketma-ket ko‘rsatish rejimi",
     ["Faqat saqlash", "Faqat ochish", "Faqat tahrirlash"], 1),
    ("Title slide", "Birinchi (sarlavha) slayd",
     ["Faqat oxirgi", "Faqat o‘rta", "Faqat bo‘sh"], 1),
    ("Layout (slayd shabloni)", "Slayd ichidagi joylashuv shakli (sarlavha+matn, faqat sarlavha va h.k.)",
     ["Faqat ranglar", "Faqat fayl turi", "Faqat shrift"], 2),
    ("Theme (mavzu)", "Slaydlar uchun tayyor dizayn (rang, shrift, fon)",
     ["Faqat fayl turi", "Faqat saqlash", "Faqat sarlavha"], 2),
    ("Transition (o‘tish)", "Slaydlar almashish vaqtidagi vizual effekt",
     ["Faqat ovoz", "Faqat saqlash", "Faqat shrift"], 3),
    ("Animation", "Slayd ichidagi obyekt (matn, rasm) harakat effekti",
     ["Faqat slaydlar almashishi", "Faqat saqlash", "Faqat shrift"], 3),
    ("Animation – Entrance", "Obyekt slaydga kirish animatsiyasi",
     ["Faqat chiqish", "Faqat fokus", "Faqat ranglar"], 3),
    ("Animation – Exit", "Obyekt slayddan chiqish animatsiyasi",
     ["Faqat kirish", "Faqat fokus", "Faqat ranglar"], 3),
    ("Animation – Emphasis", "Obyektga e'tibor qaratish (rangini o‘zgartirish va h.k.)",
     ["Faqat kirish", "Faqat chiqish", "Faqat saqlash"], 3),
    ("Animation Pane", "Animatsiyalarni boshqarish paneli",
     ["Faqat shrift paneli", "Faqat status bar", "Faqat ranglar paneli"], 3),
    ("F5", "Birinchi slayddan boshlab taqdimotni ekranda ishga tushiruvchi tugma",
     ["Saqlash", "Yopish", "Yangi"], 4),
    ("Shift+F5", "Joriy slayddan boshlab slayd-shouni ishga tushirish",
     ["Saqlash", "Yopish", "Yangi"], 4),
    ("Esc", "Slayd-shoudan chiqish tugmasi",
     ["Saqlash", "Yopish", "Yangi"], 4),
    ("Slide Sorter", "Barcha slaydlarni miniatyura ko‘rinishida ko‘rish rejimi",
     ["Faqat tahrirlash", "Faqat saqlash", "Faqat ranglar"], 5),
    ("Notes Pane", "Slayd ostida ma'ruzachi uchun yozuvlar maydoni",
     ["Faqat sarlavha", "Faqat ranglar", "Faqat saqlash"], 5),
    ("Insert Image", "Slaydga rasm qo‘shish",
     ["Faqat matn", "Faqat shrift", "Faqat saqlash"], 6),
    ("Insert Video", "Slaydga video fayl qo‘shish",
     ["Faqat ovoz", "Faqat sarlavha", "Faqat saqlash"], 6),
    ("Insert Audio", "Slaydga ovoz/musiqa qo‘shish",
     ["Faqat sarlavha", "Faqat ranglar", "Faqat saqlash"], 6),
    ("Insert Chart", "Slaydga diagramma qo‘shish",
     ["Faqat ranglar", "Faqat saqlash", "Faqat shrift"], 6),
    ("SmartArt", "Tayyor diagrammalar va sxema shablonlari",
     ["Faqat oddiy matn", "Faqat ranglar", "Faqat saqlash"], 6),
    ("Hyperlink (Slaydda)", "Slaydga havola qo‘shish (boshqa slayd, sayt, fayl)",
     ["Faqat shrift", "Faqat ranglar", "Faqat saqlash"], 6),
    ("Slide Number", "Har bir slaydga avtomatik raqam qo‘yish",
     ["Faqat ranglar", "Faqat saqlash", "Faqat shrift"], 5),
    ("Slide Master", "Barcha slaydlar uchun umumiy shabloni — bir joyda tahrirlash",
     ["Faqat oxirgi slayd", "Faqat birinchi slayd", "Faqat sarlavha"], 7),
    ("Print Layout — Handouts", "Bir varaqda bir nechta slaydni chop etish rejimi",
     ["Faqat slayd-shou", "Faqat saqlash", "Faqat ranglar"], 8),
    ("Save As — PowerPoint", "Taqdimotni boshqa nom yoki formatda saqlash",
     ["Faqat ochish", "Faqat o‘chirish", "Faqat chop etish"], 1),
    (".pdf eksport (PowerPoint)", "Taqdimotni PDF sifatida saqlash",
     ["Faqat .docx", "Faqat .xlsx", "Faqat .png"], 1),
    ("Outline View", "Faqat sarlavha va matn ko‘rinishidagi tahrir rejimi",
     ["Faqat slayd-shou", "Faqat saqlash", "Faqat ranglar"], 5),
    ("Reading View", "Slayd-shou kabi, lekin oyna ichida ko‘rish",
     ["Faqat tahrirlash", "Faqat saqlash", "Faqat ranglar"], 5),
    ("Background", "Slayd fonidagi rang yoki rasm",
     ["Faqat sarlavha", "Faqat ranglar paneli", "Faqat saqlash"], 7),
    ("Color Scheme", "Mavzudagi ranglar to‘plami",
     ["Faqat shrift", "Faqat saqlash", "Faqat sarlavha"], 7),
    ("Font Theme", "Mavzudagi shriftlar to‘plami",
     ["Faqat ranglar", "Faqat saqlash", "Faqat sarlavha"], 7),
    ("Picture Tools — Format", "Rasmni tahrirlash bo‘limi (kesish, ramka va h.k.)",
     ["Faqat saqlash", "Faqat ranglar", "Faqat shrift"], 6),
    ("Crop (PowerPoint)", "Rasmni qisqartirib kesish",
     ["Faqat aylantirish", "Faqat ranglar", "Faqat saqlash"], 6),
    ("Group/Ungroup (Obyektlarni)", "Bir nechta obyektni guruhga birlashtirish/ajratish",
     ["Faqat saqlash", "Faqat o‘chirish", "Faqat ranglar"], 6),
    ("Arrange — Bring to Front", "Obyektni boshqalarning ustiga olib chiqish",
     ["Faqat orqaga", "Faqat saqlash", "Faqat ranglar"], 6),
    ("Arrange — Send to Back", "Obyektni boshqalarning ortiga yuborish",
     ["Faqat oldinga", "Faqat saqlash", "Faqat ranglar"], 6),
    ("Slide Show — Rehearse Timings", "Slaydlarning avtomatik o‘tish vaqtini sinab belgilash",
     ["Faqat saqlash", "Faqat ovoz", "Faqat ranglar"], 4),
]


def _info6_q4_pool() -> list[QItem]:
    pool: list[QItem] = []
    for c, d, w, l in INF_6_Q4_CONCEPTS:
        pool += _conceptual(c, d, w, lesson=l)

    def t_pres_duration():
        slides = random.randint(5, 30); sec = random.randint(3, 12)
        total = slides * sec
        return QItem(text=f"PowerPoint: {slides} ta slayd har biri {sec} sekundda avtomatik almashsa, taqdimot necha sekund davom etadi?",
                     answer=str(total),
                     wrongs=[str(total + sec), str(total - sec), str(slides + sec)],
                     difficulty=2, lesson=4)

    def t_pres_minutes():
        slides = random.randint(8, 25); sec_per_slide = random.choice([15, 30, 45, 60])
        total_sec = slides * sec_per_slide
        minutes = total_sec // 60
        sec_rem = total_sec % 60
        return QItem(text=f"Taqdimot {slides} ta slayddan iborat. Har slaydga ~{sec_per_slide} soniya. Necha minut va sekund davom etadi?",
                     answer=f"{minutes} min {sec_rem} sek",
                     wrongs=[f"{minutes + 1} min {sec_rem} sek",
                             f"{minutes} min {sec_rem + 5} sek",
                             f"{slides} min {sec_rem} sek"],
                     difficulty=3, lesson=4)

    def t_shortcut():
        cases = [
            ("Slayd-shouni boshlash (birinchi slayddan)", "F5",
             ["Shift+F5", "Esc", "Ctrl+S"]),
            ("Slayd-shouni joriy slayddan boshlash", "Shift+F5",
             ["F5", "Esc", "Ctrl+S"]),
            ("Slayd-shoudan chiqish", "Esc",
             ["F5", "Shift+F5", "Tab"]),
            ("Yangi slayd qo‘shish", "Ctrl+M",
             ["Ctrl+S", "Ctrl+N", "F5"]),
            ("Saqlash", "Ctrl+S",
             ["Ctrl+P", "F5", "Esc"]),
            ("Yangi taqdimot ochish", "Ctrl+N",
             ["Ctrl+S", "F5", "Esc"]),
        ]
        c, ans, wrongs = random.choice(cases)
        return QItem(text=f"PowerPointda '{c}' uchun tugma yoki birikma qaysi?",
                     answer=ans, wrongs=list(wrongs), difficulty=1, lesson=4)

    def t_anim_type():
        cases = [
            ("Obyekt slaydga kiradi", "Entrance", ["Exit", "Emphasis", "Motion Path"]),
            ("Obyekt slayddan chiqib ketadi", "Exit", ["Entrance", "Emphasis", "Motion Path"]),
            ("Obyekt rangini o‘zgartirib e'tibor tortadi", "Emphasis",
             ["Entrance", "Exit", "Motion Path"]),
            ("Obyekt belgilangan yo‘ldan harakat qiladi", "Motion Path",
             ["Entrance", "Exit", "Emphasis"]),
        ]
        c, ans, wrongs = random.choice(cases)
        return QItem(text=f"PowerPoint animatsiyasida '{c}' qaysi turga kiradi?",
                     answer=ans, wrongs=list(wrongs), difficulty=2, lesson=3)

    def t_layout_choose():
        cases = [
            ("Faqat sarlavha kerak", "Title Only", ["Blank", "Title and Content", "Two Content"]),
            ("Sarlavha va bitta matn maydoni", "Title and Content",
             ["Title Only", "Blank", "Comparison"]),
            ("Ikki ustun matn", "Two Content", ["Blank", "Title Only", "Section Header"]),
            ("Bo‘sh slayd", "Blank", ["Title Slide", "Two Content", "Comparison"]),
        ]
        c, ans, wrongs = random.choice(cases)
        return QItem(text=f"PowerPoint Layouti: '{c}'. Qaysi shablon mos?",
                     answer=ans, wrongs=list(wrongs), difficulty=2, lesson=2)

    pool += _capped(t_pres_duration)
    pool += _capped(t_pres_minutes)
    pool += _capped(t_shortcut)
    pool += _capped(t_anim_type)
    pool += _capped(t_layout_choose)

    discrete = [
        QItem("PowerPoint hujjatining standart kengaytmasi qaysi?", ".pptx",
              [".docx", ".xlsx", ".png"], 1, 1),
        QItem("Yangi slayd qo‘shish uchun qaysi menyu?", "Home → New Slide",
              ["File → New", "Insert → Image", "Review"], 1, 2),
        QItem("Bir nechta slaydni guruhlab yashirish uchun?", "Section qo‘shish",
              ["Faqat o‘chirish", "Faqat saqlash", "Faqat ranglash"], 3, 5),
        QItem("PowerPointda matnni boshqa shrift bilan yozish uchun?", "Home → Font menyusi",
              ["File → Print", "View → Outline", "Review"], 1, 7),
        QItem("Slaydga rasm qo‘shish uchun qaysi menyu?", "Insert → Pictures",
              ["Home", "View", "Review"], 1, 6),
        QItem("Animation Painter nima qiladi?",
              "Bir obyektdagi animatsiyani boshqa obyektga ko‘chiradi",
              ["Faqat saqlaydi", "Faqat o‘chiradi", "Faqat ranglar"], 3, 3),
        QItem("Slide Master nima uchun ishlatiladi?",
              "Hamma slaydlar uchun umumiy ko‘rinish bir joyda sozlash",
              ["Faqat birinchi slayd uchun", "Faqat sarlavha uchun", "Faqat ranglash"], 3, 7),
        QItem("Taqdimotni PDF formatida saqlash uchun?",
              "File → Save As → PDF",
              ["Faqat Ctrl+S", "Faqat F5", "Faqat Esc"], 2, 1),
        QItem("Slayd ichidagi obyektlarni tartibga solish uchun?",
              "Arrange (Front/Back/Group) menyusi",
              ["Faqat saqlash", "Faqat ranglash", "Faqat sortlash"], 2, 6),
        QItem("Slayd ichida video o‘ynashini istasak qaysi menyu?",
              "Insert → Video",
              ["Insert → Image", "View → Outline", "Review"], 2, 6),
        QItem("Slaydlar avtomatik almashishini qayerdan sozlaymiz?",
              "Transitions → Advance Slide → After (sekund)",
              ["Insert", "Home", "Review"], 3, 3),
        QItem("Slayd-shou paytida sichqonchani bosish nima qiladi (default)?",
              "Keyingi animatsiya yoki slaydga o‘tadi",
              ["Avtomatik to‘xtaydi", "Slaydni o‘chiradi", "Hech narsa qilmaydi"], 2, 4),
        QItem("PowerPointda Notes Pane nima uchun?",
              "Ma'ruzachi uchun shaxsiy yozuvlar — slayd-shouda ko‘rinmaydi",
              ["Slaydda ko‘rinadigan matn", "Faqat saqlash", "Faqat ranglar"], 3, 5),
        QItem("Slaydda matnni katta-kichikligini ko‘rsatish uchun nima ishlatamiz?",
              "Font size va Bold/Italic",
              ["Faqat saqlash", "Faqat F5", "Faqat ranglash"], 1, 7),
        QItem("Bir slayddagi obyektlar tartibida yuqorida turishi uchun?",
              "Bring to Front",
              ["Send to Back", "Group", "Save"], 2, 6),
        QItem("PowerPointda mavzu (Theme) o‘zgartirish nima qiladi?",
              "Slaydlar dizayni (rang, shrift, fon) bir vaqtda o‘zgaradi",
              ["Faqat shriftni o‘zgartiradi", "Faqat ranglar", "Hech narsa"], 2, 2),
        QItem("Multimedia taqdimotda ovoz qo‘shish uchun qaysi menyu?",
              "Insert → Audio",
              ["Home", "View", "Review"], 2, 6),
        QItem("Reader View qachon foydali?",
              "Taqdimotni oyna ichida (to‘liq ekran emas) ko‘rish kerak bo‘lsa",
              ["Faqat saqlash", "Faqat tahrir", "Faqat ranglar"], 3, 5),
        QItem("PowerPointda 'Section Header' layout qaysi maqsadga mos?",
              "Yangi bo‘limni e'lon qilish",
              ["Faqat sarlavha slayd", "Faqat ovoz", "Faqat saqlash"], 2, 2),
        QItem("Hyperlink ni slaydda qaysi obyektga qo‘yish mumkin?",
              "Matn yoki rasmga",
              ["Faqat saqlash", "Faqat ranglash", "Faqat ovoz"], 2, 6),
    ]
    pool += discrete
    random.shuffle(pool)
    return pool


def informatics_pool(grade: int, quarter: int) -> list[QItem]:
    if grade == 5:
        if quarter == 1: return _info5_q1_pool()
        if quarter == 2: return _info5_q2_pool()
        if quarter == 3: return _info5_q3_pool()
        if quarter == 4:
            # Cumulative: Q1 + Q2 + Q3 + Q4
            return _info5_q1_pool() + _info5_q2_pool() + _info5_q3_pool() + _info5_q4_pool()
    if grade == 6:
        if quarter == 1: return _info6_q1_pool()
        if quarter == 2: return _info6_q2_pool()
        if quarter == 3: return _info6_q3_pool()
        if quarter == 4:
            # Cumulative: Q1 + Q2 + Q3 + Q4
            return _info6_q1_pool() + _info6_q2_pool() + _info6_q3_pool() + _info6_q4_pool()
    return []


# ─── PYTHON — 7-sinf 1-chorak ────────────────────────────────────────────────
# Mavzu: Dastur, print, o'zgaruvchilar, turlar (int/float/str), arifmetika.

PY_7_Q1_CONCEPTS = [
    ("Dastur", "Kompyuter bajaradigan buyruqlar ketma-ketligi",
     ["Faqat o‘chirish tugmasi", "Faqat operatsion tizim", "Faqat papka"], 1),
    ("Python", "Soddaligi va kuchli kutubxonalari bilan mashhur dasturlash tili",
     ["Faqat brauzer", "Faqat antivirus", "Excel formula"], 1),
    ("Yuqori darajadagi til", "Inson tushunadigan ko‘rinishga yaqin dasturlash tili",
     ["Faqat mashina kodi", "Faqat assembler", "Faqat blok-sxema"], 1),
    ("Interpretator", "Python kodini bir-bir o‘qib bajaruvchi dastur",
     ["Kodni faylga o‘zgartiruvchi", "Faqat yopuvchi", "Faqat antivirus"], 1),
    ("IDLE / VS Code", "Python kodini yozish va ishga tushirish muhitlari",
     ["Antivirus dasturlari", "Brauzerlar", "Excel formulalari"], 1),
    ("print()", "Python’da ekranga ma'lumot chiqaruvchi funksiya",
     ["input()", "len()", "type()"], 2),
    ("input()", "Foydalanuvchidan klaviatura orqali matn olish funksiyasi",
     ["print()", "type()", "len()"], 2),
    ("# (sharh)", "Kod ichida tushuntirish berish — Python o‘qimaydigan satr",
     ["Faqat dastur kodi", "Faqat o‘zgaruvchi", "Faqat string"], 2),
    ("O‘zgaruvchi (variable)", "Qiymat saqlanadigan nomlangan joy",
     ["Faqat funksiya", "Faqat fayl turi", "Faqat operatsiya"], 3),
    ("Variable name (o‘zgaruvchi nomi)", "Harf yoki _ bilan boshlanadi, son bilan boshlanmaydi",
     ["Faqat son bilan boshlanadi", "Faqat probel ishlatiladi", "Faqat katta harf"], 3),
    ("=' (taxsiyot)", "O‘zgaruvchiga qiymat berish operatori",
     ["Solishtirish ==", "Yig‘indi", "Bo‘lish"], 3),
    ("int", "Butun son turi (-3, 0, 42)",
     ["Kasr son", "Matn", "Mantiqiy"], 4),
    ("float", "Kasrli son turi (3.14, -0.5)",
     ["Faqat butun", "Faqat matn", "Faqat list"], 4),
    ("str", "Matn (string) — qo‘shtirnoq yoki bittirnoq orasidagi belgilar",
     ["Faqat son", "Faqat list", "Faqat None"], 4),
    ("bool", "True yoki False ikkilik mantiqiy tur",
     ["Son turi", "Matn turi", "Faqat None"], 4),
    ("type()", "O‘zgaruvchining turini qaytaruvchi funksiya",
     ["Faqat ko‘chiruvchi", "Faqat yig‘uvchi", "Faqat saqlovchi"], 4),
    ("int() funksiya", "Matn yoki kasr sonni butun songa o‘giruvchi funksiya",
     ["Faqat matnga o‘giradi", "Faqat list", "Faqat None"], 4),
    ("float() funksiya", "Sonni yoki matnni kasr songa o‘giruvchi funksiya",
     ["Faqat butun songa", "Faqat matn", "Faqat list"], 4),
    ("str() funksiya", "Boshqa turdagi qiymatni matnga o‘giruvchi funksiya",
     ["Faqat songa", "Faqat list", "Faqat None"], 4),
    ("Operator +", "Sonlarni qo‘shish, matnlarni biriktirish operatori",
     ["Faqat son", "Faqat ayirish", "Faqat ko‘paytirish"], 5),
    ("Operator -", "Ayirish operatori",
     ["Qo‘shish", "Ko‘paytirish", "Bo‘lish"], 5),
    ("Operator *", "Sonlarni ko‘paytirish; matnni N marta takrorlash",
     ["Faqat qo‘shish", "Faqat bo‘lish", "Faqat ayirish"], 5),
    ("Operator /", "Bo‘lish operatori (kasrli natija)",
     ["Butun bo‘lish", "Modul", "Daraja"], 5),
    ("Operator //", "Butun bo‘linmasi operatori",
     ["Oddiy bo‘lish", "Modul", "Ko‘paytirish"], 5),
    ("Operator %", "Modul (qoldiq) operatori",
     ["Butun bo‘lish", "Ko‘paytirish", "Daraja"], 5),
    ("Operator **", "Daraja olish operatori (a**b = a^b)",
     ["Modul", "Bo‘lish", "Ko‘paytirish"], 5),
    ("PEMDAS / amallar tartibi", "()→**→*,/,//,%→+,-",
     ["Hammasi chapdan o‘ngga", "Faqat + va -", "Faqat **"], 5),
    ("F-string (f\"...\")", "O‘zgaruvchilarni matn ichiga {} bilan qo‘shish usuli",
     ["Faqat sodda matn", "Faqat son", "Faqat list"], 6),
    ("\\n", "Yangi qator (newline) belgisi",
     ["Tab", "Faqat probel", "Faqat nuqta"], 6),
    ("\\t", "Tabulyatsiya belgisi",
     ["Yangi qator", "Faqat probel", "Faqat nuqta"], 6),
    ("Indentation (chekinish)", "Pythonda blok ichidagi qatorlarni 4 probel bilan chekintirish",
     ["Faqat ranglash", "Faqat saqlash", "Faqat sharh"], 1),
    ("Identifier (nom)", "O‘zgaruvchi yoki funksiya uchun belgilangan nom",
     ["Faqat string", "Faqat son", "Faqat None"], 3),
    ("Reserved keyword", "Pythonda zaxiralangan so‘z (if, for, while...) — nom sifatida ishlatib bo‘lmaydi",
     ["Oddiy o‘zgaruvchi", "Faqat funksiya", "Faqat sharh"], 3),
    ("None", "Bo‘sh qiymatni ifodalovchi maxsus turi",
     ["Faqat 0", "Faqat False", "Faqat ''"], 4),
    ("Boolean True/False", "Mantiqiy qiymatlar — birinchi harfi katta",
     ["true/false (kichik)", "Faqat 0/1", "Faqat son"], 4),
    ("int va str qo‘shilmaydi", "Pythonda int + str → TypeError",
     ["Avtomatik o‘giradi", "Hech narsa qilmaydi", "Faqat ogohlantirish"], 4),
    ("Casting (tip o‘girish)", "Bir turdan boshqa turga o‘girish (int(), str(), float())",
     ["Faqat saqlash", "Faqat sharh", "Faqat list"], 4),
    ("end='' (printda)", "print() ning oxiriga belgi qo‘ymaslik parametri",
     ["Faqat saqlash", "Faqat sharh", "Faqat ranglash"], 6),
    ("sep=' ' (printda)", "Bir nechta argumentlar orasidagi ajratuvchi belgini sozlash",
     ["Faqat saqlash", "Faqat ranglash", "Faqat sharh"], 6),
    ("Truthy/Falsy", "0, '', None, [] — Falsy; qolganlari Truthy",
     ["Hammasi True", "Hammasi False", "Faqat int qaraydi"], 4),
]


def _py7_q1_pool() -> list[QItem]:
    pool: list[QItem] = []
    for c, d, w, l in PY_7_Q1_CONCEPTS:
        pool += _conceptual(c, d, w, lesson=l)

    def t_print_int():
        v = random.randint(-99, 999)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nx = {v}\nprint(x)\n```",
                     answer=str(v), wrongs=[str(v + 1), str(v - 1), "Xatolik"],
                     difficulty=1, lesson=3)

    def t_arith_eval():
        a = random.randint(2, 30); b = random.randint(2, 9)
        op = random.choice(["+", "-", "*"])
        ans = a + b if op == "+" else (a - b if op == "-" else a * b)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nprint({a} {op} {b})\n```",
                     answer=str(ans), wrongs=[str(ans + 1), str(ans - 1), str(a)],
                     difficulty=1, lesson=5)

    def t_floor_mod():
        a = random.randint(15, 80); b = random.randint(2, 9)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nprint({a} // {b}, {a} % {b})\n```",
                     answer=f"{a // b} {a % b}",
                     wrongs=[f"{a / b} {a % b}", f"{a % b} {a // b}", "Xatolik"],
                     difficulty=2, lesson=5)

    def t_power():
        a = random.randint(2, 6); b = random.randint(2, 5)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nprint({a} ** {b})\n```",
                     answer=str(a ** b),
                     wrongs=[str(a * b), str(a + b), str(a ** (b - 1))],
                     difficulty=2, lesson=5)

    def t_type():
        cases = [
            ("'salom'", "<class 'str'>", ["<class 'int'>", "<class 'float'>", "<class 'bool'>"]),
            ("42", "<class 'int'>", ["<class 'str'>", "<class 'float'>", "<class 'bool'>"]),
            ("3.14", "<class 'float'>", ["<class 'int'>", "<class 'str'>", "<class 'bool'>"]),
            ("True", "<class 'bool'>", ["<class 'int'>", "<class 'str'>", "<class 'float'>"]),
            ("'123'", "<class 'str'>", ["<class 'int'>", "<class 'float'>", "<class 'bool'>"]),
        ]
        v, ans, wrongs = random.choice(cases)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nx = {v}\nprint(type(x))\n```",
                     answer=ans, wrongs=list(wrongs), difficulty=2, lesson=4)

    def t_str_concat():
        a = random.choice(["Sa", "Pyt", "ma", "ko", "in"])
        b = random.choice(["lom", "hon", "ktab", "mp", "ter"])
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nprint('{a}' + '{b}')\n```",
                     answer=f"{a}{b}",
                     wrongs=[f"{b}{a}", f"{a} {b}", "Xatolik"],
                     difficulty=2, lesson=5)

    def t_str_repeat():
        s = random.choice(["ab", "py", "no", "yo"])
        n = random.randint(2, 5)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nprint('{s}' * {n})\n```",
                     answer=s * n,
                     wrongs=[s, str(n) + s, "Xatolik"],
                     difficulty=2, lesson=5)

    def t_int_str_err():
        a = random.randint(1, 20); b = random.randint(1, 20)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nx = {a}\ny = '{b}'\nprint(x + y)\n```",
                     answer="TypeError (int va str qo‘shilmaydi)",
                     wrongs=[str(a + b), f"{a}{b}", "0"],
                     difficulty=3, lesson=4)

    def t_cast():
        v = random.randint(1, 99)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nprint(int('{v}') + 1)\n```",
                     answer=str(v + 1),
                     wrongs=[str(v), f"{v}1", "Xatolik"],
                     difficulty=2, lesson=4)

    def t_fstring():
        name = random.choice(["Ali", "Olim", "Sardor"])
        age = random.randint(10, 16)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nname = '{name}'\nage = {age}\nprint(f'{{name}}-{{age}}')\n```",
                     answer=f"{name}-{age}",
                     wrongs=[f"{name} {age}", f"{name}+{age}", "Xatolik"],
                     difficulty=2, lesson=6)

    pool += _capped(t_print_int)
    pool += _capped(t_arith_eval)
    pool += _capped(t_floor_mod)
    pool += _capped(t_power)
    pool += _capped(t_type)
    pool += _capped(t_str_concat)
    pool += _capped(t_str_repeat)
    pool += _capped(t_int_str_err)
    pool += _capped(t_cast)
    pool += _capped(t_fstring)

    discrete = [
        QItem("Pythonda ekranga matn chiqarish uchun qaysi funksiya?", "print()",
              ["input()", "echo()", "show()"], 1, 2, ),
        QItem("Pythonda foydalanuvchidan kiritish olish uchun qaysi funksiya?", "input()",
              ["print()", "read()", "type()"], 1, 2),
        QItem("Pythonda sharh (comment) qaysi belgi bilan boshlanadi?", "# (panja)",
              ["//", "/*", ";"], 1, 2),
        QItem("Pythonda 5/2 ifoda natijasi qanday turda bo‘ladi?", "float (2.5)",
              ["int (2)", "str ('2.5')", "bool"], 2, 4),
        QItem("Pythonda 5//2 ifoda natijasi qanday tur va qiymat?", "int va 2",
              ["float va 2.5", "str va '2'", "bool va True"], 2, 5),
        QItem("Pythonda True + 1 ifoda natijasi nima?", "2",
              ["1", "TypeError", "True"], 3, 4),
        QItem("Pythonda 0 ning bool turdagi qiymati nima?", "False",
              ["True", "None", "Xatolik"], 2, 4),
        QItem("Pythonda bo‘sh string '' ning bool qiymati nima?", "False",
              ["True", "None", "Xatolik"], 2, 4),
        QItem("input() funksiya qanday tur qaytaradi?", "str (matn)",
              ["int", "float", "bool"], 2, 2),
        QItem("Pythonda o‘zgaruvchi nomi 1abc bo‘lishi mumkinmi?", "Yo‘q — son bilan boshlanmaydi",
              ["Ha — har qanday nom bo‘ladi", "Faqat _1abc bo‘ladi", "Faqat katta harf bilan"], 2, 3),
        QItem("Pythonda 2**10 nima beradi?", "1024",
              ["20", "100", "Xatolik"], 2, 5),
        QItem("Pythonda type(3.0) natijasi qaysi?", "<class 'float'>",
              ["<class 'int'>", "<class 'str'>", "<class 'bool'>"], 1, 4),
        QItem("Pythonda print('a', 'b') natijasi nima (default sep)?", "a b",
              ["ab", "a,b", "Xatolik"], 2, 6),
        QItem("Pythonda print('a', end='') keyin print('b') chiqarsa natija qanday?",
              "ab (yangi qatorga o‘tmaydi)",
              ["a\\nb", "a b", "Xatolik"], 3, 6),
        QItem("Pythonda x = 5; y = x; x = 10. y ning qiymati nima?", "5",
              ["10", "None", "Xatolik"], 2, 3),
        QItem("Pythonda True va False da harf qanday yoziladi?",
              "Birinchi harf katta (T va F)",
              ["Hamma harf katta", "Hamma harf kichik", "Faqat birinchi kichik"], 2, 4),
        QItem("Pythonda blok ichidagi qatorlar qanday belgilanadi?",
              "Indentatsiya (4 probel chekinish) bilan",
              ["{ } qavslar bilan", ";; nuqta-vergullar bilan", "Faqat sharh"], 3, 1),
        QItem("Pythonda satr oxiriga ; (nuqta-vergul) qo‘yish kerakmi?",
              "Yo‘q — kerak emas",
              ["Ha — har doim", "Faqat shartda", "Faqat funksiyada"], 2, 1),
        QItem("Pythonda 'apple' < 'banana' ifoda natijasi nima?",
              "True (alfavit bo‘yicha)",
              ["False", "Xatolik", "None"], 3, 5),
        QItem("Pythonda 'a' * 0 ifoda natijasi nima?", "''",
              ["a", "Xatolik", "None"], 3, 5),
    ]
    pool += discrete
    random.shuffle(pool)
    return pool


# ─── PYTHON — 7-sinf 2-chorak ────────────────────────────────────────────────
# Mavzu: Stringlar — index, slicing, methods, type errors.

PY_7_Q2_CONCEPTS = [
    ("String (str)", "Tirnoqlar orasidagi belgilar ketma-ketligi",
     ["Faqat son", "Faqat list", "Faqat tuple"], 1),
    ("Index (indeks)", "Stringdagi har belgining tartib raqami (0 dan boshlanadi)",
     ["1 dan boshlanadi", "Faqat manfiy", "Faqat oxirgi"], 2),
    ("Manfiy indeks", "Oxirdan hisoblovchi indeks: -1 oxirgi belgi",
     ["1 dan boshlanadi", "Faqat 0 bo‘ladi", "Hech qachon ishlamaydi"], 2),
    ("len()", "String yoki listning uzunligini topish funksiyasi",
     ["Faqat son qiymati", "Faqat tip", "Faqat indeks"], 1),
    ("Slicing s[a:b]", "a dan b gacha (b kirmaydi) bo‘lakni olish",
     ["Faqat birinchi belgi", "Faqat oxirgi belgi", "Hech qachon ishlamaydi"], 3),
    ("Slicing s[a:b:c]", "a dan b gacha c qadam bilan olish",
     ["Faqat oxirgi", "Hech qachon ishlamaydi", "Faqat butun string"], 3),
    ("s[::-1]", "Stringni teskariga o‘girish",
     ["Faqat o‘zgartirmaydi", "Xatolik beradi", "Faqat oxirgi belgi"], 3),
    (".upper()", "Stringni katta harflarga o‘girish metodi",
     ["Kichikka o‘girish", "Probel olib tashlash", "Faqat sanash"], 4),
    (".lower()", "Stringni kichik harflarga o‘girish",
     ["Kattaga o‘girish", "Probel olib tashlash", "Sanash"], 4),
    (".title()", "Har so‘zning birinchi harfini katta qilish",
     ["Hammasini kichik", "Hammasini katta", "Probel olib tashlash"], 4),
    (".capitalize()", "Faqat birinchi harfni katta, qolganini kichik qilish",
     ["Hammasini katta", "Hammasini kichik", "Faqat probel olib tashlash"], 4),
    (".strip()", "Stringning ikki tomonidagi probelni olib tashlash",
     ["Faqat chap probel", "Faqat o‘ng probel", "Probelni qo‘shadi"], 4),
    (".lstrip()", "Stringning chap tomonidagi probelni olib tashlash",
     ["Faqat o‘ng", "Faqat o‘rtadan", "Probelni qo‘shadi"], 4),
    (".rstrip()", "Stringning o‘ng tomonidagi probelni olib tashlash",
     ["Faqat chap", "Faqat o‘rtadan", "Probelni qo‘shadi"], 4),
    (".replace(a,b)", "String ichidagi a ni b ga almashtirish",
     ["Faqat sanash", "Faqat o‘chirish", "Faqat saqlash"], 4),
    (".find(a)", "String ichidan a ning birinchi indeksini topish (yo‘q bo‘lsa -1)",
     ["Faqat sanash", "Faqat o‘chirish", "Faqat saqlash"], 4),
    (".count(a)", "String ichidagi a ning sonini topish",
     ["Faqat o‘chirish", "Faqat o‘girish", "Faqat saqlash"], 4),
    (".split()", "Stringni probel yoki belgi bo‘yicha listga ajratish",
     ["Faqat o‘girish", "Faqat birikish", "Faqat saqlash"], 4),
    (".split(',')", "Stringni vergul bo‘yicha bo‘lib listga ajratish",
     ["Faqat probel bo‘yicha", "Faqat o‘chirish", "Faqat birikish"], 4),
    (".join(list)", "Listdagi stringlarni ajratuvchi bilan birlashtirish",
     ["Faqat ajratish", "Faqat sanash", "Faqat saqlash"], 4),
    (".startswith(a)", "Stringning a bilan boshlanishini tekshirish (True/False)",
     ["Faqat oxirini tekshirish", "Faqat o‘rtadan", "Faqat saqlash"], 5),
    (".endswith(a)", "Stringning a bilan tugashini tekshirish",
     ["Faqat boshlanishini", "Faqat o‘rtadan", "Faqat saqlash"], 5),
    (".isdigit()", "Stringdagi barcha belgilar raqam ekanligini tekshirish",
     ["Faqat harflarni tekshirish", "Faqat probelni", "Faqat saqlash"], 5),
    (".isalpha()", "Stringdagi barcha belgilar harf ekanligini tekshirish",
     ["Faqat raqamlarni", "Faqat probelni", "Faqat saqlash"], 5),
    (".isalnum()", "Stringdagi belgilar harf yoki raqam ekanligini tekshirish",
     ["Faqat probelni", "Faqat raqamlarni", "Faqat saqlash"], 5),
    ("in operator", "Belgi yoki bo‘lak string ichida bormi (True/False)",
     ["Faqat saqlash", "Faqat o‘chirish", "Faqat o‘girish"], 5),
    ("\"escape \\'\"", "String ichida tirnoq yozish uchun teskari slesh",
     ["Faqat probel", "Faqat oxirgi belgi", "Faqat saqlash"], 6),
    ("Multi-line string \"\"\"...\"\"\"", "Bir necha qatorli stringni yozish usuli",
     ["Faqat bitta qator", "Faqat probel", "Faqat saqlash"], 6),
    ("String + String", "Birlashtirish (concatenation)",
     ["Faqat ko‘paytirish", "Faqat ayirish", "Faqat saqlash"], 5),
    ("String * N", "Stringni N marta takrorlash",
     ["Faqat birikish", "Faqat ajratish", "Faqat saqlash"], 5),
    ("TypeError", "Tipi mos kelmaydigan amal — masalan int + str",
     ["Faqat sintaksis", "Faqat bo‘lish nolga", "Faqat saqlash"], 6),
    ("ValueError", "Qiymat noto‘g‘ri — masalan int('abc')",
     ["Faqat sintaksis", "Faqat tip", "Faqat saqlash"], 6),
    ("IndexError", "Mavjud bo‘lmagan indeksga murojaat",
     ["Faqat tip xatosi", "Faqat sintaksis", "Faqat saqlash"], 6),
    ("Immutable string", "Stringning belgilari o‘zgartirib bo‘lmasligi",
     ["String mutable", "Faqat list mutable", "Faqat saqlash"], 7),
    ("Char access s[i]", "i-indeksdagi belgini olish",
     ["Faqat butun string", "Faqat birinchi", "Faqat oxirgi"], 2),
    ("Negative slicing s[-3:]", "Oxirgi 3 ta belgini olish",
     ["Birinchi 3 ta belgi", "Faqat o‘rtasi", "Faqat oxirgisi"], 3),
    ("s[:n]", "Stringning birinchi n ta belgisini olish",
     ["Oxirgi n ta", "Faqat oxirgi belgi", "Faqat birinchi belgi"], 3),
    ("s[n:]", "n-indeksdan oxirigacha bo‘lakni olish",
     ["Boshidan n gacha", "Faqat n-belgi", "Faqat oxirgi belgi"], 3),
    ("Comparison stringga", "Alfavit (lex) tartibida solishtirish",
     ["Faqat uzunligi bo‘yicha", "Hech qachon", "Faqat raqam bo‘yicha"], 5),
    (".replace 3 argument", ".replace(a,b,c) — eng ko‘pi bilan c marta almashtirish",
     ["Faqat 1 marta", "Faqat 2 marta", "Faqat saqlash"], 4),
]


def _py7_q2_pool() -> list[QItem]:
    pool: list[QItem] = []
    for c, d, w, l in PY_7_Q2_CONCEPTS:
        pool += _conceptual(c, d, w, lesson=l)

    words = ["python", "dasturlash", "Algoritm", "Kompyuter", "JahonSchool", "maktab"]

    def t_index_pos():
        s = random.choice(words)
        i = random.randint(0, len(s) - 1)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\ns = '{s}'\nprint(s[{i}])\n```",
                     answer=s[i],
                     wrongs=[s[0], s[-1], "Xatolik"],
                     difficulty=2, lesson=2)

    def t_index_neg():
        s = random.choice(words)
        i = random.randint(1, min(len(s), 4))
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\ns = '{s}'\nprint(s[-{i}])\n```",
                     answer=s[-i],
                     wrongs=[s[0], s[i - 1], "Xatolik"],
                     difficulty=3, lesson=2)

    def t_slice():
        s = random.choice(words)
        a = random.randint(0, max(0, len(s) - 3))
        b = random.randint(a + 2, len(s))
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\ns = '{s}'\nprint(s[{a}:{b}])\n```",
                     answer=s[a:b],
                     wrongs=[s[a:b - 1], s[a + 1:b], "Xatolik"],
                     difficulty=2, lesson=3)

    def t_slice_step():
        s = random.choice(words)
        a = random.randint(0, max(0, len(s) - 4))
        b = random.randint(a + 3, len(s))
        step = random.choice([2, 3])
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\ns = '{s}'\nprint(s[{a}:{b}:{step}])\n```",
                     answer=s[a:b:step],
                     wrongs=[s[a:b], s[::-1], "Xatolik"],
                     difficulty=3, lesson=3)

    def t_reverse():
        s = random.choice(words)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\ns = '{s}'\nprint(s[::-1])\n```",
                     answer=s[::-1],
                     wrongs=[s, s.upper(), "Xatolik"],
                     difficulty=3, lesson=3)

    def t_methods():
        cases = [
            ("'hello'.upper()", "HELLO", ["hello", "Hello", "Xatolik"]),
            ("'WORLD'.lower()", "world", ["WORLD", "World", "Xatolik"]),
            ("'  hi  '.strip()", "hi", ["  hi  ", "hi  ", "  hi"]),
            ("'python'.title()", "Python", ["PYTHON", "python", "Xatolik"]),
            ("'jahonschool'.capitalize()", "Jahonschool",
             ["jahonschool", "JAHONSCHOOL", "JahonSchool"]),
            ("'aabbcc'.count('a')", "2", ["1", "0", "Xatolik"]),
            ("'apple'.find('p')", "1", ["0", "2", "Xatolik"]),
            ("'apple'.replace('p','b')", "abble", ["apple", "appleb", "Xatolik"]),
        ]
        c, ans, wrongs = random.choice(cases)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nprint({c})\n```",
                     answer=ans, wrongs=list(wrongs), difficulty=2, lesson=4)

    def t_split():
        cases = [
            ("'a,b,c'.split(',')", "['a', 'b', 'c']"),
            ("'1 2 3'.split()", "['1', '2', '3']"),
            ("'x-y-z'.split('-')", "['x', 'y', 'z']"),
        ]
        c, ans = random.choice(cases)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nprint({c})\n```",
                     answer=ans,
                     wrongs=[ans.replace("'", '"'), "['a,b,c']", "Xatolik"],
                     difficulty=2, lesson=4)

    def t_join():
        cases = [
            ("'-'.join(['a','b','c'])", "a-b-c"),
            ("' '.join(['Bir','ikki','uch'])", "Bir ikki uch"),
            ("''.join(['p','y','t'])", "pyt"),
        ]
        c, ans = random.choice(cases)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nprint({c})\n```",
                     answer=ans,
                     wrongs=[ans + "?", "['a','b','c']", "Xatolik"],
                     difficulty=3, lesson=4)

    def t_in_check():
        s = random.choice(["python", "maktab", "kompyuter", "dasturlash"])
        ch = random.choice(list(set(s)) + ["x", "z", "q"])
        ans = "True" if ch in s else "False"
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nprint('{ch}' in '{s}')\n```",
                     answer=ans, wrongs=["True" if ans == "False" else "False",
                                         "0", "Xatolik"],
                     difficulty=2, lesson=5)

    def t_len_str():
        s = random.choice(words)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nprint(len('{s}'))\n```",
                     answer=str(len(s)),
                     wrongs=[str(len(s) + 1), str(len(s) - 1), "Xatolik"],
                     difficulty=1, lesson=1)

    pool += _capped(t_index_pos)
    pool += _capped(t_index_neg)
    pool += _capped(t_slice)
    pool += _capped(t_slice_step)
    pool += _capped(t_reverse)
    pool += _capped(t_methods)
    pool += _capped(t_split)
    pool += _capped(t_join)
    pool += _capped(t_in_check)
    pool += _capped(t_len_str)

    discrete = [
        QItem("Pythonda string mutablemi (o‘zgartirib bo‘ladimi)?",
              "Yo‘q — immutable",
              ["Ha — mutable", "Faqat ba'zi versiyalarda", "Faqat list ichida"], 3, 7),
        QItem("Pythonda string ichidagi belgini index orqali o‘zgartirish mumkinmi?",
              "Yo‘q — immutable",
              ["Ha", "Faqat birinchi belgini", "Faqat oxirgi belgini"], 3, 7),
        QItem("Pythonda 'abc'[3] qaysi xatolikni beradi?", "IndexError",
              ["TypeError", "ValueError", "Hech qanday xatolik"], 2, 6),
        QItem("Pythonda int('python') qaysi xatolikni beradi?", "ValueError",
              ["TypeError", "IndexError", "SyntaxError"], 2, 6),
        QItem("Pythonda 5 + '3' qaysi xatolikni beradi?", "TypeError",
              ["ValueError", "IndexError", "SyntaxError"], 2, 6),
        QItem("Pythonda string ni songa o‘girish uchun?", "int(s) yoki float(s)",
              ["str(s)", ".upper()", ".strip()"], 2, 4),
        QItem("Pythonda 'Hello'.lower() natijasi qaysi turda bo‘ladi?", "str (string)",
              ["int", "list", "bool"], 1, 4),
        QItem("Pythonda 'abc' < 'abd' ifoda natijasi nima?", "True (alifbo bo‘yicha)",
              ["False", "Xatolik", "None"], 3, 5),
        QItem("Pythonda f-string qachon ishlatiladi?",
              "Stringga o‘zgaruvchi qiymatini qo‘shish kerak bo‘lganda",
              ["Faqat sonlar uchun", "Faqat list uchun", "Faqat saqlash uchun"], 2, 6),
        QItem("Pythonda 'a' * -1 ifoda natijasi nima?", "''",
              ["a", "Xatolik", "None"], 3, 5),
        QItem("Pythonda 'abc'.find('z') natijasi nima?", "-1 (yo‘q ekanligi)",
              ["0", "None", "Xatolik"], 3, 4),
        QItem("Pythonda boshqarmasdan probelni olish uchun qaysi metod?",
              ".strip()",
              [".replace()", ".upper()", ".split()"], 1, 4),
        QItem("Pythonda 'abc'.replace('a', '') natijasi nima?", "bc",
              ["abc", "''", "Xatolik"], 2, 4),
        QItem("Pythonda 'a,b,c'.split(',')[1] natijasi nima?", "b",
              ["a", "c", "Xatolik"], 3, 4),
        QItem("Pythonda len('') natijasi nima?", "0",
              ["1", "None", "Xatolik"], 1, 1),
        QItem("Pythonda 'abc'.startswith('a') natijasi nima?", "True",
              ["False", "1", "Xatolik"], 1, 5),
        QItem("Pythonda 'abc'.endswith('z') natijasi nima?", "False",
              ["True", "0", "Xatolik"], 1, 5),
        QItem("Pythonda '123'.isdigit() natijasi nima?", "True",
              ["False", "1", "Xatolik"], 2, 5),
        QItem("Pythonda 'abc1'.isalpha() natijasi nima?", "False",
              ["True", "1", "Xatolik"], 3, 5),
        QItem("Pythonda 'abc123'.isalnum() natijasi nima?", "True",
              ["False", "0", "Xatolik"], 3, 5),
    ]
    pool += discrete
    random.shuffle(pool)
    return pool


# ─── PYTHON — 7-sinf 3-chorak ────────────────────────────────────────────────
# Mavzu: if/elif/else, mantiq, for/while, break/continue, list asoslari.

PY_7_Q3_CONCEPTS = [
    ("if operatori", "Shartni tekshirib, TRUE bo‘lsa kod blokini bajarish",
     ["Faqat takror", "Faqat saqlash", "Faqat o‘zgaruvchi"], 1),
    ("elif", "Bir nechta shartni ketma-ket tekshirish (else if)",
     ["Faqat oxirgi tarmoq", "Faqat takror", "Faqat saqlash"], 1),
    ("else", "Yuqoridagi shartlarning hech biri TRUE bo‘lmasa bajariluvchi blok",
     ["Bosh shart", "Sikl boshlanishi", "Faqat funksiya"], 1),
    ("Comparison ==", "Tenglikni solishtirish operatori",
     ["Qiymat berish", "Faqat ko‘paytirish", "Faqat saqlash"], 2),
    ("Comparison !=", "Teng emaslik operatori",
     ["Tenglik", "Faqat ko‘paytirish", "Faqat saqlash"], 2),
    ("Comparison < <= > >=", "Solishtirish operatorlari",
     ["Faqat tenglik", "Faqat ko‘paytirish", "Faqat saqlash"], 2),
    ("and", "Mantiqiy 'va' — ikkala TRUE bo‘lsa TRUE",
     ["Faqat OR", "Faqat NOT", "Faqat IF"], 3),
    ("or", "Mantiqiy 'yoki' — birortasi TRUE bo‘lsa TRUE",
     ["Faqat AND", "Faqat NOT", "Faqat IF"], 3),
    ("not", "Mantiqiy inkor — TRUE/FALSE ni teskariga o‘giradi",
     ["Faqat AND", "Faqat OR", "Faqat IF"], 3),
    ("in operator (mantiq)", "Element ichida bormi — True/False qaytaradi",
     ["Faqat saqlash", "Faqat ayirish", "Faqat o‘chirish"], 3),
    ("for sikli", "Diapazon yoki kolleksiyadagi har element uchun takrorlash",
     ["Faqat shart", "Faqat saqlash", "Faqat funksiya"], 4),
    ("while sikli", "Shart TRUE bo‘lgancha takrorlash",
     ["Faqat for", "Faqat shart", "Faqat funksiya"], 4),
    ("range(n)", "0 dan n-1 gacha sonlar ketma-ketligi",
     ["1 dan n gacha", "Faqat n", "Faqat 0"], 4),
    ("range(a,b)", "a dan b-1 gacha sonlar",
     ["a dan b gacha (b kirgan)", "Faqat b", "Faqat a"], 4),
    ("range(a,b,c)", "a dan b gacha c qadam bilan",
     ["Faqat birinchi qiymat", "Faqat oxirgi qiymat", "Faqat saqlash"], 4),
    ("break", "Sikldan oldindan chiqib ketish operatori",
     ["Davom etish", "Saqlash", "Yopish"], 5),
    ("continue", "Joriy iteratsiyani o‘tkazib yuborib keyingisiga o‘tish",
     ["Sikldan chiqish", "Saqlash", "Faqat ranglar"], 5),
    ("else (sikl bilan)", "Sikl break siz tugagach bajariluvchi blok",
     ["Faqat shart", "Faqat funksiya", "Faqat saqlash"], 5),
    ("List (ro‘yxat)", "Tartiblangan, o‘zgaruvchan element to‘plami []",
     ["Faqat son", "Faqat string", "Faqat tuple"], 6),
    ("Bo‘sh list []", "Hech qanday element bo‘lmagan list",
     ["[None]", "[0]", "['']"], 6),
    ("List indeks L[i]", "Listdagi i-elementni olish (0 dan boshlanadi)",
     ["1 dan boshlanadi", "Faqat oxirgi", "Faqat birinchi"], 6),
    ("L[-1]", "Listning oxirgi elementi",
     ["Birinchi element", "Xatolik", "Hech narsa"], 6),
    (".append(x)", "List oxiriga element qo‘shish",
     ["Faqat o‘chirish", "Faqat saralash", "Faqat saqlash"], 6),
    (".pop()", "List oxiridan element olib tashlash va qaytarish",
     ["Faqat append", "Faqat saqlash", "Faqat saralash"], 6),
    (".remove(x)", "Listdan birinchi uchragan x ni olib tashlash",
     ["Faqat indeksdan", "Faqat oxirgisini", "Faqat saqlash"], 6),
    ("len(L)", "Listdagi elementlar soni",
     ["Faqat birinchisi", "Faqat oxirgisi", "Faqat saqlash"], 6),
    ("List slicing L[a:b]", "Listdan bo‘lakni kesib olish (yangi list)",
     ["Faqat birinchi", "Faqat oxirgi", "Faqat saqlash"], 6),
    ("sum(L)", "Listdagi sonlar yig‘indisi",
     ["Faqat o‘rtacha", "Faqat MAX", "Faqat MIN"], 7),
    ("max(L)", "Listdagi eng katta qiymat",
     ["Faqat MIN", "Faqat sum", "Faqat saqlash"], 7),
    ("min(L)", "Listdagi eng kichik qiymat",
     ["Faqat MAX", "Faqat sum", "Faqat saqlash"], 7),
    ("List + List", "Ikki listni birlashtirish (yangi list)",
     ["Faqat ko‘paytirish", "Faqat ayirish", "Faqat saqlash"], 6),
    ("List * N", "Listni N marta takrorlash",
     ["Faqat ayirish", "Faqat saqlash", "Faqat o‘chirish"], 6),
    ("List of strings", "Stringlar saqlanadigan list",
     ["Faqat sonlar list", "Faqat list ichida list", "Faqat saqlash"], 6),
    ("Mixed list", "Turli tipdagi qiymatlardan iborat list",
     ["Faqat bir tip", "Faqat son", "Faqat saqlash"], 6),
    ("Mutable list", "Listni o‘zgartirib bo‘ladi (string emas)",
     ["Immutable", "Faqat o‘qish", "Faqat saqlash"], 7),
    ("if x in L", "Element listda bormi tekshirish",
     ["Faqat saqlash", "Faqat o‘chirish", "Faqat ayirish"], 7),
    ("Equal lists ==", "Ikki list element-elementga teng bo‘lsa TRUE",
     ["Doim TRUE", "Doim FALSE", "Faqat uzunligi tekshiriladi"], 7),
    ("Sequential search", "Listni ketma-ket tekshirib elementni qidirish",
     ["Faqat binar", "Faqat saqlash", "Faqat sortlash"], 7),
    ("Counter cnt += 1", "Cnt o‘zgaruvchisini birga oshirish",
     ["1 ga kamaytirish", "Saqlash", "Yopish"], 5),
    ("Accumulator s += x", "S o‘zgaruvchisiga x ni qo‘shib yangilash",
     ["Almashtirish", "Saqlash", "Faqat o‘chirish"], 5),
]


def _py7_q3_pool() -> list[QItem]:
    pool: list[QItem] = []
    for c, d, w, l in PY_7_Q3_CONCEPTS:
        pool += _conceptual(c, d, w, lesson=l)

    def t_if_3way():
        x = random.randint(-30, 30); y = random.randint(-30, 30)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nx = {x}\ny = {y}\nif x > y:\n    print('A')\nelif x == y:\n    print('B')\nelse:\n    print('C')\n```",
                     answer="A" if x > y else ("B" if x == y else "C"),
                     wrongs=["A", "B", "C"], difficulty=2, lesson=1)

    def t_and_or():
        a = random.randint(0, 1); b = random.randint(0, 1)
        bool_a = bool(a); bool_b = bool(b)
        op = random.choice(["and", "or"])
        ans = bool_a and bool_b if op == "and" else bool_a or bool_b
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nprint({bool_a} {op} {bool_b})\n```",
                     answer=str(ans),
                     wrongs=[str(not ans), "None", "Xatolik"],
                     difficulty=2, lesson=3)

    def t_for_sum():
        n = random.randint(5, 20)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\ns = 0\nfor i in range(1, {n + 1}):\n    s += i\nprint(s)\n```",
                     answer=str(sum(range(1, n + 1))),
                     wrongs=[str(n), str(n + 1), "Xatolik"],
                     difficulty=2, lesson=4)

    def t_for_count_even():
        n = random.randint(8, 25)
        cnt = sum(1 for i in range(1, n + 1) if i % 2 == 0)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\ncnt = 0\nfor i in range(1, {n + 1}):\n    if i % 2 == 0:\n        cnt += 1\nprint(cnt)\n```",
                     answer=str(cnt),
                     wrongs=[str(cnt + 1), str(cnt - 1 if cnt > 0 else 1), str(n)],
                     difficulty=2, lesson=4)

    def t_while_dec():
        n = random.randint(5, 15)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nx = {n}\nwhile x > 0:\n    x -= 1\nprint(x)\n```",
                     answer="0",
                     wrongs=[str(n), str(n - 1), "Xatolik"],
                     difficulty=2, lesson=4)

    def t_break_loop():
        n = random.randint(8, 20); stop = random.randint(2, n - 1)
        s = sum(range(stop))
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\ns = 0\nfor i in range({n}):\n    if i == {stop}:\n        break\n    s += i\nprint(s)\n```",
                     answer=str(s),
                     wrongs=[str(s + 1), str(stop), "Xatolik"],
                     difficulty=3, lesson=5)

    def t_continue_loop():
        n = random.randint(6, 15); skip = random.randint(2, n - 1)
        s = sum(i for i in range(n) if i != skip)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\ns = 0\nfor i in range({n}):\n    if i == {skip}:\n        continue\n    s += i\nprint(s)\n```",
                     answer=str(s),
                     wrongs=[str(s + skip), str(skip), "Xatolik"],
                     difficulty=3, lesson=5)

    def t_list_index():
        L = [random.randint(1, 30) for _ in range(5)]
        i = random.randint(-5, 4)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nL = {L}\nprint(L[{i}])\n```",
                     answer=str(L[i]),
                     wrongs=[str(L[0]), str(len(L)), "Xatolik"],
                     difficulty=2, lesson=6)

    def t_list_append():
        L = [random.randint(1, 20) for _ in range(4)]
        v = random.randint(1, 30)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nL = {L}\nL.append({v})\nprint(L)\n```",
                     answer=str(L + [v]),
                     wrongs=[str(L), str([v] + L), "Xatolik"],
                     difficulty=2, lesson=6)

    def t_list_sum():
        L = [random.randint(-5, 30) for _ in range(5)]
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nprint(sum({L}))\n```",
                     answer=str(sum(L)),
                     wrongs=[str(max(L)), str(min(L)), "Xatolik"],
                     difficulty=1, lesson=7)

    def t_list_max():
        L = [random.randint(-30, 30) for _ in range(5)]
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nprint(max({L}))\n```",
                     answer=str(max(L)),
                     wrongs=[str(min(L)), str(sum(L)), "Xatolik"],
                     difficulty=1, lesson=7)

    def t_in_list():
        L = [random.randint(1, 10) for _ in range(5)]
        v = random.randint(1, 15)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nprint({v} in {L})\n```",
                     answer="True" if v in L else "False",
                     wrongs=["True" if v not in L else "False", "0", "Xatolik"],
                     difficulty=2, lesson=7)

    pool += _capped(t_if_3way)
    pool += _capped(t_and_or)
    pool += _capped(t_for_sum)
    pool += _capped(t_for_count_even)
    pool += _capped(t_while_dec)
    pool += _capped(t_break_loop)
    pool += _capped(t_continue_loop)
    pool += _capped(t_list_index)
    pool += _capped(t_list_append)
    pool += _capped(t_list_sum)
    pool += _capped(t_list_max)
    pool += _capped(t_in_list)

    discrete = [
        QItem("Pythonda if-else qaysi turdagi algoritmga taalluqli?",
              "Tarmoqlanuvchi (shartli)",
              ["Chiziqli", "Faqat takror", "Faqat saqlash"], 2, 1),
        QItem("Pythonda for sikli odatda qachon ishlatiladi?",
              "Aniq sondagi takrorlash kerak bo‘lganda",
              ["Faqat shart bo‘lganda", "Faqat ranglash uchun", "Faqat saqlash uchun"], 2, 4),
        QItem("Pythonda while sikli qachon ishlatiladi?",
              "Shart bajarilgancha takrorlash kerak bo‘lganda",
              ["Faqat aniq son", "Faqat saqlash", "Faqat ranglash"], 2, 4),
        QItem("Pythonda range(5) qaysi qiymatlarni qaytaradi?",
              "0,1,2,3,4",
              ["1,2,3,4,5", "0,1,2,3,4,5", "1,2,3,4"], 2, 4),
        QItem("Pythonda range(2, 6) qaysi qiymatlarni qaytaradi?", "2,3,4,5",
              ["2,3,4,5,6", "1,2,3,4,5", "Xatolik"], 2, 4),
        QItem("Pythonda L = [1,2,3] bo‘lsa, len(L) nima qaytaradi?", "3",
              ["2", "4", "Xatolik"], 1, 6),
        QItem("Pythonda L.append(4) nima qiladi (L=[1,2,3])?", "L = [1,2,3,4] bo‘ladi",
              ["L = [4,1,2,3]", "L = [1,2,4]", "Xatolik"], 1, 6),
        QItem("Pythonda L = [1,2,3]; L[3] qaysi xatolikni beradi?", "IndexError",
              ["TypeError", "ValueError", "Hech qanday"], 2, 6),
        QItem("Pythonda 'and' va 'or' farqi nima?",
              "and — ikkalasi TRUE bo‘lsa TRUE; or — bittasi yetarli",
              ["Bir xil", "Faqat or qaytaradi", "Faqat and qaytaradi"], 2, 3),
        QItem("Pythonda 'not True' natijasi nima?", "False",
              ["True", "1", "Xatolik"], 1, 3),
        QItem("Pythonda x = 5 if y > 0 else 0 — bu nima?",
              "Conditional expression (ternary) — qisqa if-else",
              ["Faqat sikl", "Faqat funksiya", "Faqat saqlash"], 3, 1),
        QItem("Pythonda for i in range(0, 10, 2) qaysi qiymatlarni beradi?",
              "0,2,4,6,8",
              ["0,1,2,3,4,5,6,7,8,9", "1,3,5,7,9", "Xatolik"], 2, 4),
        QItem("Pythonda break va continue farqi?",
              "break — sikldan chiqadi; continue — keyingisiga o‘tadi",
              ["Bir xil", "Faqat saqlash", "Faqat ranglash"], 2, 5),
        QItem("Pythonda L = [1,2,3]; L.pop() natijasi nima?", "3 (oxirgi element)",
              ["1", "[]", "Xatolik"], 2, 6),
        QItem("Pythonda L = [1,2,3]; L.remove(2) keyin L nimaga teng?", "[1, 3]",
              ["[1, 2]", "[2, 3]", "[1, 3, 2]"], 2, 6),
        QItem("Pythonda L = [3,1,2]; L.sort() keyin L nimaga teng?", "[1, 2, 3]",
              ["[3, 2, 1]", "[3, 1, 2]", "Xatolik"], 2, 7),
        QItem("Pythonda L = [3,1,2]; sorted(L) qaysi qiymatni qaytaradi?", "[1, 2, 3]",
              ["[3, 2, 1]", "[3, 1, 2]", "Xatolik"], 2, 7),
        QItem("Pythonda for sikli ichida else qachon bajariladi?",
              "Sikl break siz oxirigacha tugaganda",
              ["Doim", "Hech qachon", "Faqat saqlash"], 3, 5),
        QItem("Pythonda L = []; bool(L) natijasi nima?", "False",
              ["True", "1", "Xatolik"], 2, 7),
        QItem("Pythonda 'apple' in ['apple','banana'] natijasi nima?", "True",
              ["False", "1", "Xatolik"], 1, 7),
    ]
    pool += discrete
    random.shuffle(pool)
    return pool


# ─── PYTHON — 7-sinf 4-chorak ────────────────────────────────────────────────
# Mavzu: Aralash takrorlash + amaliy: ATM, sodda qaror qabul qilish.

PY_7_Q4_CONCEPTS = [
    ("Foydalanuvchi interaktivligi", "input()/print() orqali muloqot qilish",
     ["Faqat saqlash", "Faqat ranglash", "Faqat o‘chirish"], 1),
    ("Validatsiya", "Kiritilgan ma'lumotni shartga muvofiqligini tekshirish",
     ["Faqat saqlash", "Faqat o‘chirish", "Faqat ranglash"], 1),
    ("ATM modeli", "Bankomat — balansni yechish va to‘ldirish jarayoni",
     ["Faqat saqlash", "Faqat o‘chirish", "Faqat ranglash"], 1),
    ("Yetarli mablag‘ sharti", "yechish > balans bo‘lsa rad etiladi",
     ["Faqat saqlash", "Doim qabul qilinadi", "Hech qachon ruxsat berilmaydi"], 1),
    ("Komissiya (fee)", "Bank xizmati uchun olinuvchi qo‘shimcha haq",
     ["Faqat saqlash", "Faqat o‘chirish", "Faqat ranglash"], 2),
    ("Min/Max chegara", "Kiritilgan qiymatni minimum va maksimumda cheklash",
     ["Doim cheksiz", "Faqat saqlash", "Faqat o‘chirish"], 2),
    ("PIN tekshiruvi", "Kiritilgan PIN to‘g‘ri-yo‘qligini tekshirish",
     ["Faqat saqlash", "Faqat o‘chirish", "Faqat ranglash"], 2),
    ("Multi-step menyu", "Bir nechta tanlovdan birini bajarish (kirish, yechish, balans)",
     ["Faqat saqlash", "Faqat ranglash", "Faqat o‘chirish"], 3),
    ("Loop bilan menyu", "Foydalanuvchi 'chiqish' tanlamaguncha menyu takrorlanadi",
     ["Faqat bir marta", "Faqat saqlash", "Faqat ranglash"], 3),
    ("Counter (urinishlar)", "Kiritish urinishlari sonini sanab borish",
     ["Faqat saqlash", "Faqat ranglash", "Faqat o‘chirish"], 3),
    ("Continue ishlatish", "Noto‘g‘ri kiritishda iteratsiyani o‘tkazib yuborish",
     ["Faqat break", "Faqat saqlash", "Faqat ranglash"], 4),
    ("Break ishlatish", "Foydalanuvchi 'chiqish' tanlasa sikldan chiqish",
     ["Faqat continue", "Faqat saqlash", "Faqat ranglash"], 4),
    ("Tarmoqlanish — odd/even", "Sonni juft yoki toq aniqlash",
     ["Faqat saqlash", "Faqat ranglash", "Faqat o‘chirish"], 4),
    ("Tarmoqlanish — yosh", "Yosh asosida qarorlar qabul qilish",
     ["Faqat saqlash", "Faqat ranglash", "Faqat o‘chirish"], 4),
    ("Tarmoqlanish — baho", "Baho oraliqlariga qarab xulosa berish",
     ["Faqat saqlash", "Faqat ranglash", "Faqat o‘chirish"], 4),
    ("Comprehension (oddiy)", "Listni qisqa shaklda yaratish",
     ["Faqat oddiy sikl", "Faqat saqlash", "Faqat ranglash"], 5),
    ("Pattern: hisoblagich", "for ichida cnt += 1 — element sanash",
     ["Faqat o‘chirish", "Faqat saqlash", "Faqat ranglash"], 5),
    ("Pattern: yig‘uvchi", "for ichida s += x — yig‘indi to‘plash",
     ["Faqat o‘chirish", "Faqat saqlash", "Faqat ranglash"], 5),
    ("Pattern: max/min topish", "for ichida solishtirib eng katta/kichik topish",
     ["Faqat saqlash", "Faqat ranglash", "Faqat o‘chirish"], 5),
    ("Pattern: shart bo‘yicha sanab", "if shart: cnt += 1",
     ["Faqat saqlash", "Faqat ranglash", "Faqat o‘chirish"], 5),
    ("List comp [x for x in L]", "Listdan element olib yangi list yaratish",
     ["Faqat saqlash", "Faqat o‘chirish", "Faqat ranglash"], 5),
    ("List comp [x*2 for x in L]", "Listdagi har elementni 2 ga ko‘paytirib yangi list yaratish",
     ["Faqat saqlash", "Faqat o‘chirish", "Faqat ranglash"], 5),
    ("List comp [x for x in L if c]", "Shartli list comprehension",
     ["Faqat saqlash", "Faqat o‘chirish", "Faqat ranglash"], 5),
    ("Bracket [] vs () vs {}", "List, tuple, dict/set turlarini ajratuvchi qavslar",
     ["Faqat saqlash", "Hammasi bir xil", "Faqat o‘chirish"], 6),
    ("Tuple", "O‘zgartirib bo‘lmaydigan tartiblangan to‘plam",
     ["Mutable list", "Faqat saqlash", "Faqat ranglash"], 6),
    ("Dict (lug‘at)", "Kalit-qiymat juftliklari to‘plami {k: v}",
     ["Faqat son", "Faqat string", "Faqat list"], 6),
    ("Set (to‘plam)", "Takrorlanmas elementlar to‘plami",
     ["Tartiblangan", "Faqat string", "Faqat son"], 6),
    ("Boolean kasting", "if x: — x truthy bo‘lsa bajariladi",
     ["Faqat saqlash", "Faqat ranglash", "Faqat o‘chirish"], 4),
    ("Random", "Tasodifiy son hosil qiluvchi modul (random)",
     ["Faqat saqlash", "Faqat ranglash", "Faqat o‘chirish"], 7),
    ("random.randint(a,b)", "a dan b gacha (b kirgan) tasodifiy butun son",
     ["a dan b-1 gacha", "Faqat 0 va 1", "Faqat saqlash"], 7),
    ("random.choice(L)", "Listdan tasodifiy element tanlash",
     ["Faqat birinchi element", "Faqat oxirgi", "Faqat saqlash"], 7),
    ("Try-Except (oddiy)", "Xatolarni qo‘lda qayta ishlash bloki",
     ["Faqat saqlash", "Faqat ranglash", "Faqat o‘chirish"], 8),
    ("ValueError ushlash", "int() ga noto‘g‘ri matn berilganda xatoni qayta ishlash",
     ["Faqat saqlash", "Faqat ranglash", "Faqat o‘chirish"], 8),
    ("ZeroDivisionError", "0 ga bo‘lishda yuzaga keladigan xatolik",
     ["Faqat saqlash", "Faqat ranglash", "Faqat o‘chirish"], 8),
    ("Code style — bo‘sh joy", "Operator atrofida probel qo‘yish odob",
     ["Hech qachon kerak emas", "Faqat saqlash", "Faqat ranglash"], 9),
    ("Code style — nom", "Tushunarli o‘zgaruvchi nomlari (snake_case)",
     ["Faqat 1 harf", "Faqat raqamlar", "Faqat saqlash"], 9),
    ("Code style — sharh", "Murakkab joylarda sharh qo‘shish odat",
     ["Sharh kerak emas", "Faqat saqlash", "Faqat ranglash"], 9),
    ("Modular dastur", "Kodni funksiyalarga bo‘lib yozish",
     ["Bir butun bo‘lakka yozish", "Faqat saqlash", "Faqat ranglash"], 9),
    ("Test qilish", "Dasturni turli kirish bilan sinab ko‘rish",
     ["Faqat saqlash", "Faqat ranglash", "Faqat o‘chirish"], 9),
    ("Refactoring", "Kodni qayta yozib tushunarli va samarali qilish",
     ["Faqat saqlash", "Faqat ranglash", "Faqat o‘chirish"], 9),
]


def _py7_q4_pool() -> list[QItem]:
    pool: list[QItem] = []
    for c, d, w, l in PY_7_Q4_CONCEPTS:
        pool += _conceptual(c, d, w, lesson=l)

    def t_atm():
        bal = random.randint(50, 500) * 1000
        wd = random.randint(20, 600) * 1000
        ans = "Yetarli emas" if wd > bal else str(bal - wd)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nbalans = {bal}\nyechish = {wd}\nif yechish > balans:\n    print('Yetarli emas')\nelse:\n    print(balans - yechish)\n```",
                     answer=ans,
                     wrongs=["0", str(bal), str(wd)],
                     difficulty=3, lesson=1)

    def t_atm_fee():
        bal = random.randint(100, 800) * 1000
        wd = random.randint(50, 750) * 1000
        fee = random.choice([0, 1000, 2000, 5000])
        if wd <= 0:
            ans = "Xato"
        elif wd + fee > bal:
            ans = "Rad"
        else:
            ans = str(bal - wd - fee)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nbalans={bal}\nkomissiya={fee}\nyechish={wd}\nif yechish<=0:\n    print('Xato')\nelif yechish+komissiya>balans:\n    print('Rad')\nelse:\n    print(balans-yechish-komissiya)\n```",
                     answer=ans, wrongs=["Rad", "Xato", str(bal)], difficulty=3, lesson=2)

    def t_grade_letter():
        b = random.randint(0, 100)
        ans = "A" if b >= 90 else ("B" if b >= 75 else ("C" if b >= 60 else ("D" if b >= 40 else "F")))
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nb = {b}\nif b >= 90:\n    print('A')\nelif b >= 75:\n    print('B')\nelif b >= 60:\n    print('C')\nelif b >= 40:\n    print('D')\nelse:\n    print('F')\n```",
                     answer=ans, wrongs=["A", "B", "F"], difficulty=2, lesson=4)

    def t_loop_count_mod():
        n = random.randint(20, 80); m = random.randint(2, 9)
        cnt = sum(1 for i in range(n) if i % m == 0)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\ncnt = 0\nfor i in range({n}):\n    if i % {m} == 0:\n        cnt += 1\nprint(cnt)\n```",
                     answer=str(cnt),
                     wrongs=[str(cnt + 1), str(n), str(m)],
                     difficulty=2, lesson=5)

    def t_list_filter():
        L = [random.randint(-5, 30) for _ in range(7)]
        ans = [x for x in L if x > 0]
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nprint([x for x in {L} if x > 0])\n```",
                     answer=str(ans),
                     wrongs=[str(L), "[]", "Xatolik"],
                     difficulty=2, lesson=5)

    def t_list_double():
        L = [random.randint(1, 15) for _ in range(5)]
        ans = [x * 2 for x in L]
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nprint([x*2 for x in {L}])\n```",
                     answer=str(ans),
                     wrongs=[str(L), str([x + 2 for x in L]), "Xatolik"],
                     difficulty=2, lesson=5)

    def t_str_upper_slice():
        s = random.choice(["python", "dastur", "algoritm", "maktab"]) + str(random.randint(1, 99))
        a = random.randint(0, 2); b = random.randint(a + 2, min(len(s), a + 6))
        ans = s[a:b].upper()
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\ns = '{s}'\nprint(s[{a}:{b}].upper())\n```",
                     answer=ans,
                     wrongs=[s.upper(), s[a:b], "Xatolik"],
                     difficulty=2, lesson=5)

    def t_nested_loop():
        n = random.randint(2, 5); m = random.randint(2, 5)
        c = sum(1 for i in range(n) for j in range(m) if (i + j) % 2 == 0)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nc = 0\nfor i in range({n}):\n    for j in range({m}):\n        if (i+j) % 2 == 0:\n            c += 1\nprint(c)\n```",
                     answer=str(c),
                     wrongs=[str(n * m), "0", "Xatolik"],
                     difficulty=3, lesson=5)

    def t_break_continue_combo():
        n = random.randint(8, 20); skip = random.randint(2, 5); stop = random.randint(skip + 1, n - 1)
        s = 0
        for i in range(1, n):
            if i == skip:
                continue
            if i == stop:
                break
            s += i
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\ns = 0\nfor i in range(1, {n}):\n    if i == {skip}:\n        continue\n    if i == {stop}:\n        break\n    s += i\nprint(s)\n```",
                     answer=str(s),
                     wrongs=[str(s + skip), str(stop), "Xatolik"],
                     difficulty=3, lesson=4)

    def t_count_chars():
        s = random.choice(["pythonpython", "kompyuter", "dasturlash", "salomalaykum"])
        ch = random.choice(list(set(s)))
        ans = s.count(ch)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nprint('{s}'.count('{ch}'))\n```",
                     answer=str(ans),
                     wrongs=[str(ans + 1), "0", "Xatolik"],
                     difficulty=2, lesson=5)

    pool += _capped(t_atm)
    pool += _capped(t_atm_fee)
    pool += _capped(t_grade_letter)
    pool += _capped(t_loop_count_mod)
    pool += _capped(t_list_filter)
    pool += _capped(t_list_double)
    pool += _capped(t_str_upper_slice)
    pool += _capped(t_nested_loop)
    pool += _capped(t_break_continue_combo)
    pool += _capped(t_count_chars)

    discrete = [
        QItem("Pythonda input() orqali olingan ma'lumot qaysi turda bo‘ladi?",
              "str (matn)",
              ["int", "float", "list"], 2, 1),
        QItem("Foydalanuvchidan butun son olish uchun nima qilish kerak?",
              "int(input(...))", ["str(input)", ".upper()", "Faqat input"], 2, 1),
        QItem("Foydalanuvchi 'a' deb yozsa va biz int() qilsak nima sodir bo‘ladi?",
              "ValueError",
              ["TypeError", "Hech qanday xatolik", "Faqat 0 qaytaradi"], 2, 8),
        QItem("Try-except qachon foydali?",
              "Xato yuz berishi mumkin bo‘lgan kodni xavfsizlashtirish",
              ["Faqat saqlash", "Faqat sortlash", "Faqat ranglash"], 3, 8),
        QItem("Pythonda 0 ga bo‘lganda qanday xatolik chiqadi?", "ZeroDivisionError",
              ["TypeError", "ValueError", "IndexError"], 2, 8),
        QItem("ATMda balans yetarli bo‘lmasa nima qilish kerak?",
              "Yechishni rad etish va xabar berish",
              ["Faqat sokin yechish", "Faqat saqlash", "Faqat ranglash"], 2, 1),
        QItem("Pythonda L=[1,2,3]; sum(L) natijasi nima?", "6",
              ["3", "1", "Xatolik"], 1, 5),
        QItem("Pythonda max([5,3,9,1]) natijasi nima?", "9",
              ["5", "1", "Xatolik"], 1, 5),
        QItem("Pythonda min([5,3,9,1]) natijasi nima?", "1",
              ["9", "5", "Xatolik"], 1, 5),
        QItem("Pythonda len([1,2,3]) natijasi nima?", "3",
              ["2", "4", "Xatolik"], 1, 5),
        QItem("Pythonda for else qachon bajariladi?",
              "Sikl break siz oxirigacha tugaganda",
              ["Doim", "Hech qachon", "Faqat saqlash"], 3, 4),
        QItem("Pythonda continue va break farqi?",
              "continue — keyingisiga o‘tadi; break — sikldan chiqadi",
              ["Bir xil", "Faqat saqlash", "Faqat ranglash"], 2, 4),
        QItem("Pythonda nested loop nima?",
              "Sikl ichida sikl",
              ["Bitta sikl", "Faqat saqlash", "Faqat ranglash"], 2, 5),
        QItem("Pythonda r=random.randint(1, 6) qanday qiymat qaytaradi?",
              "1 dan 6 gacha (6 ham kirgan) butun son",
              ["1 dan 5 gacha", "Faqat 0", "Faqat 6"], 2, 7),
        QItem("Pythonda r=random.choice(['a','b','c']) qanday qiymat qaytaradi?",
              "'a','b','c' lardan birini",
              ["Faqat 'a'", "Faqat 'c'", "Xatolik"], 2, 7),
        QItem("Pythonda 'pass' nima qiladi?", "Hech narsa qilmaydi (joy egallaydi)",
              ["Sikldan chiqadi", "Saqlaydi", "Yopadi"], 3, 9),
        QItem("Pythonda ESLATMA: indentatsiya muhimmi?",
              "Ha — bloklarni bir xil indent bilan yozish shart",
              ["Yo‘q", "Faqat ba'zan", "Faqat funksiyalarda"], 2, 9),
        QItem("Pythonda yoshga qarab kategoriya: 0-12 'bola', 13-17 'o‘smir', 18+ 'kattalar'. 14 ga qaysi to‘g‘ri?",
              "o‘smir",
              ["bola", "kattalar", "Xatolik"], 2, 4),
        QItem("Pythonda agar son juft bo‘lsa qanday tekshiramiz?", "n % 2 == 0",
              ["n % 2 == 1", "n / 2 == 0", "n // 2 == 0"], 1, 4),
        QItem("Pythonda agar son toq bo‘lsa qanday tekshiramiz?", "n % 2 == 1 (yoki != 0)",
              ["n % 2 == 0", "n / 2 != 0", "n // 2 == 1"], 1, 4),
    ]
    pool += discrete
    random.shuffle(pool)
    return pool


# ─── PYTHON — 8-sinf 1-chorak ────────────────────────────────────────────────
# Mavzu: Takror (7-sinf) + murakkab if/loop, while siklining chuqur ishlatishi.

PY_8_Q1_CONCEPTS = [
    ("Murakkab shart (and/or)", "and va or larni birgalikda ishlatish",
     ["Faqat AND", "Faqat OR", "Faqat NOT"], 1),
    ("Nested if", "Shartlar ichidagi shartlar — chuqur tarmoqlanish",
     ["Faqat bitta if", "Faqat else", "Faqat saqlash"], 1),
    ("Comparison chaining", "a < b < c — bir vaqtda ikkita solishtirish",
     ["Faqat alohida", "Hech qachon", "Faqat saqlash"], 1),
    ("Pythonda is va == farqi", "is — obyekt ayniyligi; == — qiymat tengligi",
     ["Bir xil", "Faqat is ishlaydi", "Faqat == ishlaydi"], 2),
    ("None solishtiruv", "x is None — None bilan solishtirish to‘g‘ri usul",
     ["x == None", "Faqat saqlash", "Faqat ranglash"], 2),
    ("Loop ichidagi loop", "Ichma-ich sikllar — N×M iteratsiya",
     ["Faqat bitta sikl", "Faqat saqlash", "Faqat ranglash"], 3),
    ("while True", "Cheksiz sikl — break orqali tugaydi",
     ["Hech qachon ishlamaydi", "Faqat oddiy if", "Faqat saqlash"], 3),
    ("Loop counter", "Sikldagi iteratsiyalar sonini sanab borish",
     ["Faqat saqlash", "Faqat ranglash", "Faqat o‘chirish"], 3),
    ("Sikl bilan max topish", "for ichida solishtirib, mx ni yangilab borish",
     ["Faqat saqlash", "Faqat ranglash", "Faqat o‘chirish"], 4),
    ("Sikl bilan min topish", "for ichida solishtirib, mn ni yangilab borish",
     ["Faqat saqlash", "Faqat ranglash", "Faqat o‘chirish"], 4),
    ("Sikl bilan sum", "for ichida s += x — yig‘indi to‘plash",
     ["Faqat saqlash", "Faqat ranglash", "Faqat o‘chirish"], 4),
    ("Sikl bilan avg", "for bilan yig‘indini hisoblab, count ga bo‘lish",
     ["Faqat saqlash", "Faqat ranglash", "Faqat o‘chirish"], 4),
    ("Range qadamli", "range(a, b, c) — c qadam bilan",
     ["Faqat 1 qadam", "Faqat 0 qadam", "Faqat saqlash"], 3),
    ("range manfiy qadam", "range(10, 0, -1) — kamayuvchi diapazon",
     ["Hech qachon ishlamaydi", "Faqat 1 ga ortadi", "Faqat saqlash"], 3),
    ("Sikldan oldin/keyin", "Initialize → while/for → cleanup",
     ["Faqat oddiy", "Faqat saqlash", "Faqat ranglash"], 3),
    ("Boolean qaytadan", "while True → ichida shart bilan break",
     ["Hech qachon to‘xtamaydi", "Faqat oddiy", "Faqat saqlash"], 3),
    ("Modul amali %", "Qoldiqni topish — juftlik aniqlash, bo‘luvchanlik",
     ["Faqat butun bo‘linma", "Faqat ko‘paytirish", "Faqat ayirish"], 5),
    ("Bo‘luvchanlik testi", "n % d == 0 bo‘lsa n d ga bo‘linadi",
     ["n / d == 0", "n // d", "Faqat saqlash"], 5),
    ("Ko‘paytma sarflash", "for ichida p *= x — ko‘paytma to‘plash",
     ["Faqat ayirish", "Faqat saqlash", "Faqat ranglash"], 5),
    ("Faktorial sikl orqali", "1 dan n gacha sonlarni ko‘paytirish",
     ["Faqat ayirish", "Faqat saqlash", "Faqat ranglash"], 5),
    ("Toping (search) algoritm", "Sikl orqali listdan element izlash",
     ["Faqat saqlash", "Faqat ranglash", "Faqat o‘chirish"], 6),
    ("Linear search", "Listni ketma-ket tekshirib element topish",
     ["Faqat oxirgi", "Faqat birinchi", "Faqat saqlash"], 6),
    ("Found flag (bool)", "Topildi/topilmadi holatini saqlovchi mantiqiy o‘zgaruvchi",
     ["Faqat son", "Faqat string", "Faqat saqlash"], 6),
    ("Default value", "Topilmasa qaytariladigan boshlang‘ich qiymat",
     ["Faqat saqlash", "Faqat ranglash", "Faqat o‘chirish"], 6),
    ("Iteratsiya bo‘yicha hisob", "Sikl iteratsiyalari sonini sanash",
     ["Faqat saqlash", "Faqat ranglash", "Faqat o‘chirish"], 4),
    ("if-elif-else daraxti", "Bir nechta shartni daraxt ko‘rinishida tekshirish",
     ["Faqat bitta if", "Faqat else", "Faqat saqlash"], 1),
    ("Boolean vs son", "if n: — n != 0 bo‘lsa TRUE",
     ["Faqat bool", "Faqat saqlash", "Faqat ranglash"], 2),
    ("Boolean vs string", "if s: — s != '' bo‘lsa TRUE",
     ["Faqat bool", "Faqat saqlash", "Faqat ranglash"], 2),
    ("Boolean vs list", "if L: — L != [] bo‘lsa TRUE",
     ["Faqat bool", "Faqat saqlash", "Faqat ranglash"], 2),
    ("not in operator", "Element kolleksiyada yo‘qligi tekshirish",
     ["Faqat in", "Faqat saqlash", "Faqat ranglash"], 2),
    ("Operator priority", "and dan oldin not, or dan oldin and",
     ["Hech qanday tartib", "Faqat saqlash", "Faqat ranglash"], 1),
    ("Konvertatsiya zanjiri", "int(input()) — kirishni butun songa o‘girish",
     ["Faqat saqlash", "Faqat ranglash", "Faqat o‘chirish"], 7),
    ("List bilan range", "for x in range(...) — range natijasini iteratsiya qilish",
     ["Faqat saqlash", "Faqat ranglash", "Faqat o‘chirish"], 3),
    ("Pythonic loop", "for x in L — to‘g‘ridan-to‘g‘ri elementlar bo‘yicha",
     ["Faqat indeks bilan", "Faqat saqlash", "Faqat ranglash"], 4),
    ("enumerate(L)", "Indeks va element birgalikda — for i, x in enumerate(L)",
     ["Faqat element", "Faqat indeks", "Faqat saqlash"], 4),
    ("zip(a, b)", "Ikki kolleksiyani parallel iteratsiya qilish",
     ["Faqat birinchi", "Faqat ikkinchi", "Faqat saqlash"], 4),
    ("any()", "Kolleksiyada bittasi TRUE bo‘lsa TRUE qaytaradi",
     ["Hammasi TRUE", "Faqat saqlash", "Faqat ranglash"], 6),
    ("all()", "Kolleksiyaning hammasi TRUE bo‘lsa TRUE qaytaradi",
     ["Bittasi TRUE", "Faqat saqlash", "Faqat ranglash"], 6),
    ("Boolean default", "Bo‘sh kolleksiya uchun any() False, all() True",
     ["Hammasi True", "Hammasi False", "Faqat saqlash"], 6),
    ("Iterating dict", "for k in D — kalitlar bo‘yicha iteratsiya",
     ["Faqat qiymatlar", "Faqat ko‘rsatkich", "Faqat saqlash"], 7),
]


def _py8_q1_pool() -> list[QItem]:
    pool: list[QItem] = []
    for c, d, w, l in PY_8_Q1_CONCEPTS:
        pool += _conceptual(c, d, w, lesson=l)

    def t_chained_compare():
        x = random.randint(0, 30); a = random.randint(0, 15); b = random.randint(15, 30)
        cond = (a < x < b)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nx={x}\nprint({a}<x<{b})\n```",
                     answer=str(cond),
                     wrongs=[str(not cond), "None", "Xatolik"],
                     difficulty=2, lesson=1)

    def t_complex_if():
        x = random.randint(-30, 50); y = random.randint(-30, 50); z = random.randint(-30, 50)
        ans = "A" if (x < y and y <= z) else ("B" if x == z else "C")
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nx={x}\ny={y}\nz={z}\nif x<y and y<=z:\n    print('A')\nelif x==z:\n    print('B')\nelse:\n    print('C')\n```",
                     answer=ans, wrongs=["A", "B", "C"], difficulty=2, lesson=1)

    def t_while_double():
        n = random.randint(20, 200); mul = random.choice([2, 3])
        i = 1
        while i < n:
            i *= mul
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\ni = 1\nwhile i < {n}:\n    i *= {mul}\nprint(i)\n```",
                     answer=str(i),
                     wrongs=[str(n), str(i // mul), "Xatolik"],
                     difficulty=3, lesson=3)

    def t_while_dec_count():
        start = random.randint(20, 100); dec = random.randint(2, 9); limit = random.randint(0, 15)
        i = start; step = 0
        while i > limit:
            i -= dec; step += 1
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\ni = {start}\nstep = 0\nwhile i > {limit}:\n    i -= {dec}\n    step += 1\nprint(step)\n```",
                     answer=str(step),
                     wrongs=[str(step + 1), str(start - limit), "Xatolik"],
                     difficulty=3, lesson=3)

    def t_for_break():
        n = random.randint(10, 30); stop = random.randint(2, n - 1)
        s = sum(range(stop))
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\ns = 0\nfor i in range({n}):\n    if i == {stop}:\n        break\n    s += i\nprint(s)\n```",
                     answer=str(s),
                     wrongs=[str(s + 1), str(stop), "Xatolik"],
                     difficulty=2, lesson=3)

    def t_logical_combo():
        a = random.randint(-20, 30); b = random.randint(-20, 30); c = random.randint(-20, 30)
        ans = (a < 0) or (b > c and c % 2 == 0)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\na={a}\nb={b}\nc={c}\nprint((a<0) or (b>c and c%2==0))\n```",
                     answer=str(ans),
                     wrongs=[str(not ans), "None", "Xatolik"],
                     difficulty=3, lesson=1)

    def t_nested_count():
        n = random.randint(2, 6); m = random.randint(2, 6)
        c = sum(1 for i in range(n) for j in range(m) if i + j > 2)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nc = 0\nfor i in range({n}):\n    for j in range({m}):\n        if i + j > 2:\n            c += 1\nprint(c)\n```",
                     answer=str(c),
                     wrongs=[str(n * m), str(0), "Xatolik"],
                     difficulty=3, lesson=3)

    def t_factorial():
        n = random.randint(2, 6)
        f = 1
        for i in range(1, n + 1):
            f *= i
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\np = 1\nfor i in range(1, {n + 1}):\n    p *= i\nprint(p)\n```",
                     answer=str(f),
                     wrongs=[str(n), str(n * n), "Xatolik"],
                     difficulty=2, lesson=5)

    def t_search_in_list():
        L = [random.randint(1, 30) for _ in range(7)]
        v = random.choice(L + [random.randint(1, 30)])
        ans = "Topildi" if v in L else "Topilmadi"
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nL = {L}\nfound = False\nfor x in L:\n    if x == {v}:\n        found = True\n        break\nprint('Topildi' if found else 'Topilmadi')\n```",
                     answer=ans,
                     wrongs=["Topildi" if ans == "Topilmadi" else "Topilmadi", "False", "Xatolik"],
                     difficulty=3, lesson=6)

    def t_range_step_neg():
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nfor i in range(5, 0, -1):\n    print(i, end=' ')\n```",
                     answer="5 4 3 2 1 ",
                     wrongs=["1 2 3 4 5 ", "5 4 3 2 1 0 ", "Xatolik"],
                     difficulty=3, lesson=3)

    def t_any_all():
        L = [random.choice([0, 1]) for _ in range(5)]
        op = random.choice(["any", "all"])
        ans = any(L) if op == "any" else all(L)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nprint({op}({L}))\n```",
                     answer=str(ans),
                     wrongs=[str(not ans), "None", "Xatolik"],
                     difficulty=2, lesson=6)

    pool += _capped(t_chained_compare)
    pool += _capped(t_complex_if)
    pool += _capped(t_while_double)
    pool += _capped(t_while_dec_count)
    pool += _capped(t_for_break)
    pool += _capped(t_logical_combo)
    pool += _capped(t_nested_count)
    pool += _capped(t_factorial)
    pool += _capped(t_search_in_list)
    pool += _capped(t_range_step_neg)
    pool += _capped(t_any_all)

    discrete = [
        QItem("Pythonda 'is' va '==' farqi nima?",
              "is — obyekt ayniyligi; == — qiymat tengligi",
              ["Bir xil", "Faqat is", "Faqat =="], 3, 2),
        QItem("Pythonda x is None to‘g‘rimi?",
              "Ha — None bilan solishtirish uchun afzal usul",
              ["Yo‘q — x == None to‘g‘ri", "Hech qachon ishlatib bo‘lmaydi", "Faqat son uchun"], 3, 2),
        QItem("Pythonda x = []; if x: degan shart qaysi natijani beradi?",
              "False — bo‘sh list falsy",
              ["True", "Xatolik", "None"], 2, 2),
        QItem("Pythonda not (a or b) qaysi ifodaga teng?",
              "(not a) and (not b) — De Morgan qonuni",
              ["a or b", "a and b", "Xatolik"], 3, 1),
        QItem("Pythonda while True ichida break qachon kerak?",
              "Sikl tugashi uchun shart bajarilganda",
              ["Hech qachon", "Faqat saqlash", "Faqat ranglash"], 3, 3),
        QItem("Pythonda for sikli ichida else qachon bajariladi?",
              "Sikl break siz tugaganda",
              ["Doim", "Hech qachon", "Faqat saqlash"], 3, 3),
        QItem("Pythonda enumerate(['a','b']) nima qaytaradi?",
              "[(0,'a'),(1,'b')] kabi indeks-qiymat juftliklarini",
              ["Faqat indekslarni", "Faqat qiymatlarni", "Xatolik"], 3, 4),
        QItem("Pythonda zip([1,2],[3,4]) nima qaytaradi?",
              "[(1,3),(2,4)] juftliklarni",
              ["[1,2,3,4]", "Faqat birinchi list", "Xatolik"], 3, 4),
        QItem("Pythonda any([0, 0, 1]) natijasi nima?", "True",
              ["False", "0", "Xatolik"], 2, 6),
        QItem("Pythonda all([1, 1, 0]) natijasi nima?", "False",
              ["True", "0", "Xatolik"], 2, 6),
        QItem("Pythonda a < b < c qanday bajariladi?",
              "(a < b) and (b < c) shaklida — comparison chain",
              ["Faqat (a<b)", "Faqat (b<c)", "Xatolik"], 3, 1),
        QItem("Pythonda 'else' ham 'elif' ham bo‘lmasa, kod qanday ishlaydi?",
              "Faqat shart TRUE bo‘lsa bajariladi",
              ["Doim bajariladi", "Hech qachon", "Xatolik"], 2, 1),
        QItem("Pythonda nested (ichma-ich) sikllar samaradorlik jihatidan qanday?",
              "Iteratsiya soni N×M ga ortadi — sekinroq",
              ["Tezroq ishlaydi", "Bir xil", "Hech ta'sir qilmaydi"], 3, 3),
        QItem("Pythonda for i, x in enumerate(L): qachon foydali?",
              "Indeks va elementni birga ishlatishda",
              ["Faqat indeks kerak bo‘lganda", "Faqat element kerak bo‘lganda", "Hech qachon"], 3, 4),
        QItem("Pythonda while sikli boshlanmasdan bajarilmasligi mumkinmi?",
              "Ha — agar shart boshidanoq False bo‘lsa",
              ["Yo‘q — kamida bir marta", "Faqat for da", "Hech qachon"], 3, 3),
        QItem("Pythonda 5 % 2 natijasi nima?", "1",
              ["2", "0", "Xatolik"], 1, 5),
        QItem("Pythonda 10 % 3 natijasi nima?", "1",
              ["3", "0", "Xatolik"], 1, 5),
        QItem("Pythonda 100 // 7 natijasi nima?", "14",
              ["7", "2", "Xatolik"], 1, 5),
        QItem("Pythonda 0 ga bo‘lganda 0 / 0 nima beradi?",
              "ZeroDivisionError",
              ["0", "1", "None"], 2, 3),
        QItem("Pythonda for x in 'abc': qaysi tartibda iteratsiya bo‘ladi?",
              "a, b, c — har belgi alohida",
              ["Faqat butun string", "Teskari tartibda", "Xatolik"], 2, 4),
    ]
    pool += discrete
    random.shuffle(pool)
    return pool


# ─── PYTHON — 8-sinf 2-chorak ────────────────────────────────────────────────
# Mavzu: List metodlari, tuple, dict, amaliy.

PY_8_Q2_CONCEPTS = [
    ("List (chuqurroq)", "Tartiblangan, mutable elementlar to‘plami []",
     ["Tuple", "Set", "Dict"], 1),
    (".append(x)", "List oxiriga element qo‘shish",
     ["Faqat o‘chirish", "Faqat saralash", "Faqat saqlash"], 1),
    (".extend(L)", "Listga boshqa kolleksiya elementlarini qo‘shish",
     ["Faqat bitta element", "Faqat o‘chirish", "Faqat saqlash"], 1),
    (".insert(i, x)", "i-indeksga x ni qo‘yish",
     ["Faqat oxirga", "Faqat boshiga", "Faqat saqlash"], 1),
    (".pop()", "Oxirgi elementni olib tashlash va qaytarish",
     ["Faqat birinchini", "Faqat saqlash", "Faqat ranglash"], 1),
    (".pop(i)", "i-indeksdagi elementni olib tashlash va qaytarish",
     ["Faqat oxirgini", "Faqat saqlash", "Faqat ranglash"], 1),
    (".remove(x)", "Birinchi uchragan x ni listdan o‘chirish",
     ["Faqat indeks bilan", "Faqat oxirgini", "Faqat saqlash"], 1),
    (".sort()", "Listni o‘rnida tartiblash",
     ["Faqat saqlash", "Faqat ranglash", "Faqat o‘chirish"], 2),
    ("sorted(L)", "Yangi tartiblangan list qaytarish",
     ["O‘zini o‘zgartiradi", "Faqat saqlash", "Faqat ranglash"], 2),
    (".reverse()", "Listni teskari tartibga keltirish",
     ["Faqat saqlash", "Faqat ranglash", "Faqat o‘chirish"], 2),
    ("L.sort(reverse=True)", "Kamayish tartibida tartiblash",
     ["O‘sish tartibida", "Faqat saqlash", "Faqat ranglash"], 2),
    (".index(x)", "x elementning birinchi indeksini qaytarish",
     ["Faqat oxirgi indeksini", "Faqat saqlash", "Faqat ranglash"], 1),
    (".count(x)", "x elementning sonini qaytarish",
     ["Faqat saqlash", "Faqat ranglash", "Faqat o‘chirish"], 1),
    (".clear()", "Listdagi barcha elementlarni o‘chirish",
     ["Faqat birinchini", "Faqat oxirgini", "Faqat saqlash"], 1),
    (".copy()", "Listning sayoz nusxasini qaytarish",
     ["Faqat o‘rnida o‘zgartirish", "Faqat saqlash", "Faqat ranglash"], 1),
    ("Tuple", "O‘zgartirib bo‘lmaydigan tartiblangan to‘plam ()",
     ["Mutable list", "Set", "Dict"], 3),
    ("Bo‘sh tuple ()", "Hech qanday element bo‘lmagan tuple",
     ["[]", "{}", "None"], 3),
    ("Bir elementli tuple (x,)", "Vergul majburiy",
     ["(x)", "(x,)", "[x]"], 3),
    ("Tuple unpacking", "a, b = (1, 2) — qiymatlarni alohida o‘zgaruvchilarga yoyish",
     ["Faqat birinchi qiymat", "Faqat saqlash", "Faqat ranglash"], 3),
    ("Tuple immutable", "Tuple elementlarini o‘zgartirib bo‘lmaydi",
     ["Tuple mutable", "Faqat ba'zi", "Faqat saqlash"], 3),
    ("Dict (lug‘at)", "Kalit-qiymat juftliklari to‘plami {k: v}",
     ["Faqat list", "Faqat tuple", "Faqat set"], 4),
    ("Bo‘sh dict {}", "Hech qanday juftlik yo‘q",
     ["()", "[]", "None"], 4),
    ("d[key]", "Kalit bo‘yicha qiymatni olish (kalit yo‘q bo‘lsa KeyError)",
     ["Faqat indeks", "Faqat oxirgi", "Faqat saqlash"], 4),
    ("d.get(key, default)", "Kalit bo‘yicha qiymatni xavfsiz olish (yo‘q bo‘lsa default)",
     ["Faqat KeyError", "Faqat saqlash", "Faqat ranglash"], 4),
    ("d.keys()", "Lug‘atdagi barcha kalitlar",
     ["Faqat qiymatlar", "Faqat juftliklar", "Faqat saqlash"], 4),
    ("d.values()", "Lug‘atdagi barcha qiymatlar",
     ["Faqat kalitlar", "Faqat juftliklar", "Faqat saqlash"], 4),
    ("d.items()", "Lug‘atdagi (kalit, qiymat) juftliklari",
     ["Faqat kalitlar", "Faqat qiymatlar", "Faqat saqlash"], 4),
    ("Kalit yangilash d[k]=v", "Mavjud kalit qiymatini yangilash",
     ["Faqat saqlash", "Faqat o‘chirish", "Faqat ranglash"], 4),
    ("del d[k]", "Lug‘atdan kalitni o‘chirish",
     ["Faqat saqlash", "Faqat ranglash", "Faqat qo‘shish"], 4),
    ("k in d", "Kalit lug‘atda bormi (True/False)",
     ["Faqat qiymat", "Faqat saqlash", "Faqat ranglash"], 4),
    ("Set (to‘plam) {1,2,3}", "Takrorlanmas elementlar — tartibsiz",
     ["Tartiblangan", "Faqat son", "Faqat saqlash"], 5),
    ("Bo‘sh set: set()", "Bo‘sh to‘plam — {} bo‘sh dict bo‘ladi",
     ["{}", "()", "[]"], 5),
    (".add(x) — set", "Setga element qo‘shish",
     ["Faqat o‘chirish", "Faqat saqlash", "Faqat ranglash"], 5),
    (".discard(x) — set", "Setdan elementni xavfsiz olib tashlash",
     ["Faqat KeyError", "Faqat saqlash", "Faqat ranglash"], 5),
    ("Set union: a | b", "Ikki to‘plamni birlashtirish",
     ["Faqat kesishma", "Faqat ayirma", "Faqat saqlash"], 5),
    ("Set intersection: a & b", "Ikki to‘plamning kesishmasi",
     ["Faqat birlashma", "Faqat ayirma", "Faqat saqlash"], 5),
    ("Set difference: a - b", "Ikki to‘plamning ayirmasi",
     ["Faqat kesishma", "Faqat birlashma", "Faqat saqlash"], 5),
    ("List vs Tuple vs Set", "List — tartibli&mutable; tuple — immutable; set — takrorlanmas&tartibsiz",
     ["Hammasi bir xil", "Faqat list ishlaydi", "Faqat saqlash"], 6),
    ("Listni setga: set(L)", "Listni unikal qiymatlar setiga aylantirish",
     ["Faqat saqlash", "Faqat ranglash", "Faqat o‘chirish"], 6),
    ("Setni listga: list(s)", "Setni listga o‘girish (tartib o‘zgarib qolishi mumkin)",
     ["Faqat saqlash", "Faqat ranglash", "Faqat o‘chirish"], 6),
]


def _py8_q2_pool() -> list[QItem]:
    pool: list[QItem] = []
    for c, d, w, l in PY_8_Q2_CONCEPTS:
        pool += _conceptual(c, d, w, lesson=l)

    def t_list_append():
        L = [random.randint(1, 20) for _ in range(4)]
        v = random.randint(20, 50)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nL = {L}\nL.append({v})\nL.sort()\nprint(L[-1])\n```",
                     answer=str(max(L + [v])),
                     wrongs=[str(min(L + [v])), str(v), "Xatolik"],
                     difficulty=2, lesson=2)

    def t_list_extend():
        L1 = [random.randint(1, 10) for _ in range(3)]
        L2 = [random.randint(1, 10) for _ in range(2)]
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nL = {L1}\nL.extend({L2})\nprint(L)\n```",
                     answer=str(L1 + L2),
                     wrongs=[str(L1 + [L2]), str(L2 + L1), "Xatolik"],
                     difficulty=2, lesson=1)

    def t_list_remove():
        L = [random.randint(1, 10) for _ in range(5)]
        v = random.choice(L)
        ans = list(L); ans.remove(v)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nL = {L}\nL.remove({v})\nprint(L)\n```",
                     answer=str(ans),
                     wrongs=[str(L), str(L[1:]), "Xatolik"],
                     difficulty=2, lesson=1)

    def t_list_pop():
        L = [random.randint(1, 30) for _ in range(5)]
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nL = {L}\nx = L.pop()\nprint(x, L)\n```",
                     answer=f"{L[-1]} {L[:-1]}",
                     wrongs=[f"{L[0]} {L[1:]}", str(L), "Xatolik"],
                     difficulty=3, lesson=1)

    def t_list_sort():
        L = random.sample(range(1, 50), 5)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nL = {L}\nL.sort()\nprint(L)\n```",
                     answer=str(sorted(L)),
                     wrongs=[str(L), str(sorted(L, reverse=True)), "Xatolik"],
                     difficulty=2, lesson=2)

    def t_tuple_slice():
        t = tuple(random.randint(1, 30) for _ in range(5))
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nt = {t}\nprint(t[1:4])\n```",
                     answer=str(t[1:4]),
                     wrongs=[str(t), str(t[:3]), "Xatolik"],
                     difficulty=2, lesson=3)

    def t_tuple_unpack():
        a = random.randint(1, 50); b = random.randint(1, 50); c = random.randint(1, 50)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nx, y, z = ({a}, {b}, {c})\nprint(y)\n```",
                     answer=str(b),
                     wrongs=[str(a), str(c), "Xatolik"],
                     difficulty=2, lesson=3)

    def t_dict_get():
        keys = ["ism", "yosh", "sinf", "shahar"]
        k = random.choice(keys)
        v = random.randint(10, 30)
        d = {k: v, random.choice([x for x in keys if x != k]): random.randint(10, 30)}
        miss = random.choice([x for x in keys if x not in d])
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nd = {d}\nprint(d.get('{miss}', 0))\n```",
                     answer="0",
                     wrongs=[str(v), "None", "Xatolik"],
                     difficulty=2, lesson=4)

    def t_dict_in():
        d = {"a": 1, "b": 2, "c": 3}
        k = random.choice(["a", "b", "c", "d", "e"])
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nd = {d}\nprint('{k}' in d)\n```",
                     answer=str(k in d),
                     wrongs=[str(k not in d), str(d.get(k, 0)), "Xatolik"],
                     difficulty=2, lesson=4)

    def t_set_unique():
        L = [random.randint(1, 5) for _ in range(8)]
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nprint(len(set({L})))\n```",
                     answer=str(len(set(L))),
                     wrongs=[str(len(L)), str(min(L)), "Xatolik"],
                     difficulty=2, lesson=5)

    def t_set_union():
        a = set(random.sample(range(1, 8), 3))
        b = set(random.sample(range(1, 8), 3))
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\na = {a}\nb = {b}\nprint(sorted(a | b))\n```",
                     answer=str(sorted(a | b)),
                     wrongs=[str(sorted(a & b)), str(sorted(a - b)), "Xatolik"],
                     difficulty=3, lesson=5)

    def t_set_intersection():
        a = set(random.sample(range(1, 8), 4))
        b = set(random.sample(range(1, 8), 4))
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\na = {a}\nb = {b}\nprint(sorted(a & b))\n```",
                     answer=str(sorted(a & b)),
                     wrongs=[str(sorted(a | b)), str(sorted(a - b)), "Xatolik"],
                     difficulty=3, lesson=5)

    pool += _capped(t_list_append)
    pool += _capped(t_list_extend)
    pool += _capped(t_list_remove)
    pool += _capped(t_list_pop)
    pool += _capped(t_list_sort)
    pool += _capped(t_tuple_slice)
    pool += _capped(t_tuple_unpack)
    pool += _capped(t_dict_get)
    pool += _capped(t_dict_in)
    pool += _capped(t_set_unique)
    pool += _capped(t_set_union)
    pool += _capped(t_set_intersection)

    discrete = [
        QItem("Pythonda L=[1,2,3]; L.append([4,5]) keyin L nimaga teng?",
              "[1, 2, 3, [4, 5]]",
              ["[1, 2, 3, 4, 5]", "[1, 2, 3]", "Xatolik"], 3, 1),
        QItem("Pythonda L=[1,2,3]; L.extend([4,5]) keyin L nimaga teng?",
              "[1, 2, 3, 4, 5]",
              ["[1, 2, 3, [4, 5]]", "[4, 5, 1, 2, 3]", "Xatolik"], 2, 1),
        QItem("Pythonda L=[1,2,3]; L.insert(0, 0) keyin L nimaga teng?",
              "[0, 1, 2, 3]",
              ["[1, 2, 3, 0]", "[1, 2, 3]", "Xatolik"], 2, 1),
        QItem("Pythonda L=[3,1,2]; sorted(L) qaysi qiymatni qaytaradi?", "[1, 2, 3]",
              ["[3, 2, 1]", "[3, 1, 2]", "Xatolik"], 1, 2),
        QItem("Pythonda t=(1,2,3); t[0]=10 nima qaytaradi?",
              "TypeError — tuple immutable",
              ["[10, 2, 3]", "(10, 2, 3)", "Hech qanday xatolik"], 3, 3),
        QItem("Pythonda t=(1,) — bu nima?",
              "Bir elementli tuple (vergul muhim)",
              ["Oddiy son", "Xatolik", "Bo‘sh tuple"], 3, 3),
        QItem("Pythonda d={1:'a', 2:'b'}; d[1] nima qaytaradi?", "'a'",
              ["1", "'b'", "Xatolik"], 1, 4),
        QItem("Pythonda d={'a':1}; d['b'] nima xato beradi?", "KeyError",
              ["IndexError", "ValueError", "TypeError"], 2, 4),
        QItem("Pythonda d={'a':1, 'b':2}; len(d) natijasi nima?", "2",
              ["1", "3", "Xatolik"], 1, 4),
        QItem("Pythonda d.update({'a':5}) — d={'a':1} bo‘lsa keyin nimaga teng?",
              "{'a': 5}",
              ["{'a': 1}", "{'a': 1, 'a': 5}", "Xatolik"], 2, 4),
        QItem("Pythonda set([1,1,2,2,3]) natijasi nima?", "{1, 2, 3}",
              ["[1,1,2,2,3]", "[1,2,3]", "Xatolik"], 2, 5),
        QItem("Pythonda {1,2,3} & {2,3,4} natijasi nima?", "{2, 3}",
              ["{1, 4}", "{1, 2, 3, 4}", "Xatolik"], 2, 5),
        QItem("Pythonda {1,2,3} | {3,4} natijasi nima?", "{1, 2, 3, 4}",
              ["{3}", "{1, 2}", "Xatolik"], 2, 5),
        QItem("Pythonda L=[1,2,3]; L.copy() bilan L o‘zgarishi mumkinmi?",
              "Yo‘q — copy() yangi list yaratadi",
              ["Ha — bir xil obyekt", "Faqat ba'zi versiyalarda", "Xatolik"], 3, 1),
        QItem("Pythonda dict tartiblanganmi (Python 3.7+)?",
              "Ha — qo‘shilish tartibi saqlanadi",
              ["Yo‘q — tartib yo‘q", "Faqat alphabet tartibida", "Faqat saqlash"], 3, 4),
        QItem("Pythonda set ichida list saqlash mumkinmi?",
              "Yo‘q — list mutable, hashable emas",
              ["Ha", "Faqat birinchi", "Faqat saqlash"], 3, 5),
        QItem("Pythonda set ichida tuple saqlash mumkinmi?",
              "Ha — tuple immutable, hashable",
              ["Yo‘q", "Faqat ba'zi turdagi", "Hech qachon"], 3, 5),
        QItem("Pythonda L = [1,2,3]; L[1:] nima qaytaradi?", "[2, 3]",
              ["[1]", "[1, 2]", "Xatolik"], 1, 1),
        QItem("Pythonda L = [1,2,3,4]; L[::2] natijasi nima?", "[1, 3]",
              ["[2, 4]", "[1, 2, 3, 4]", "Xatolik"], 2, 1),
        QItem("Pythonda d = {'a':1, 'b':2}; for k in d: print(k) nimani chiqaradi?",
              "Lug‘at kalitlarini",
              ["Faqat qiymatlarni", "Faqat juftliklarni", "Xatolik"], 2, 4),
    ]
    pool += discrete
    random.shuffle(pool)
    return pool


# ─── PYTHON — 8-sinf 3-chorak ────────────────────────────────────────────────
# Mavzu: Funksiyalar (def), parametrlar, return, scope.

PY_8_Q3_CONCEPTS = [
    ("Funksiya (Function)", "Ma'lum bir vazifani bajaruvchi nomlangan kod bloki",
     ["Faqat o‘zgaruvchi", "Faqat shart", "Faqat sikl"], 1),
    ("def kalit so‘zi", "Funksiya ta'riflashni boshlovchi buyruq",
     ["print", "return", "if"], 1),
    ("Parametr (Argument)", "Funksiyaga tashqaridan uzatiladigan ma'lumot",
     ["Funksiya nomi", "Natija", "Faqat son"], 2),
    ("return kalit so‘zi", "Funksiya natijasini qaytarish uchun ishlatiladi",
     ["print", "input", "def"], 1),
    ("Lokal o‘zgaruvchi", "Faqat funksiya ichida ko‘rinadigan o‘zgaruvchi",
     ["Global o‘zgaruvchi", "Faqat raqam", "Dastur nomi"], 2),
    ("Global o‘zgaruvchi", "Butun dastur davomida ko‘rinadigan o‘zgaruvchi",
     ["Lokal o‘zgaruvchi", "Faqat bitta funksiyada", "Hech qayerda"], 2),
    ("Default parametr", "Agar argument berilmasa, ishlatiladigan boshlang‘ich qiymat",
     ["Majburiy parametr", "Natija", "Xatolik"], 3),
    ("Lambda (anonim) funksiya", "Bir qatorda yoziladigan nomsiz funksiya",
     ["Katta funksiya", "Faqat loop", "Faqat shart"], 3),
    ("Docstring", "Funksiya nima qilishini tushuntiruvchi matn ('''...''')",
     ["Faqat sharh #", "Faqat o‘zgaruvchi", "Faqat return"], 2),
    ("Scope (ko‘rinish sohasi)", "O‘zgaruvchi qayerda mavjudligini belgilovchi qoida",
     ["Faqat ranglash", "Faqat saqlash", "Faqat o‘chirish"], 2),
]


def _py8_q3_pool() -> list[QItem]:
    pool: list[QItem] = []
    for c, d, w, l in PY_8_Q3_CONCEPTS:
        pool += _conceptual(c, d, w, lesson=l)

    def t_func_simple():
        a = random.randint(1, 20); b = random.randint(1, 20)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\ndef f(x, y):\n    return x + y\nprint(f({a}, {b}))\n```",
                     answer=str(a + b), wrongs=[str(a), str(b), "Xatolik"], difficulty=1, lesson=1)

    def t_func_mul():
        a = random.randint(2, 9); b = random.randint(2, 9)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\ndef mul(a, b):\n    return a * b\nprint(mul({a}, {b}))\n```",
                     answer=str(a * b), wrongs=[str(a + b), "0", "Xatolik"], difficulty=1, lesson=1)

    def t_func_scope():
        x = random.randint(1, 100); y = random.randint(1, 100)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nx = {x}\ndef change():\n    x = {y}\nchange()\nprint(x)\n```",
                     answer=str(x), wrongs=[str(y), "None", "Xatolik"], difficulty=3, lesson=2)

    def t_func_default():
        a = random.randint(1, 20)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\ndef salom(nom='Mehmon'):\n    return 'Salom ' + nom\nprint(salom())\n```",
                     answer="Salom Mehmon", wrongs=["Salom", "Salom nom", "Xatolik"], difficulty=2, lesson=3)

    def t_lambda_sum():
        a = random.randint(1, 20); b = random.randint(1, 20)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\ns = lambda x, y: x + y\nprint(s({a}, {b}))\n```",
                     answer=str(a + b), wrongs=[str(a), str(b), "Xatolik"], difficulty=3, lesson=4)

    pool += _capped(t_func_simple)
    pool += _capped(t_func_mul)
    pool += _capped(t_func_scope)
    pool += _capped(t_func_default)
    pool += _capped(t_lambda_sum)

    discrete = [
        QItem("Pythonda funksiya qaysi so‘z bilan boshlanadi?", "def", ["func", "function", "define"], 1, 1),
        QItem("Funksiyadan qiymat qaytarish uchun qaysi so‘z ishlatiladi?", "return", ["print", "get", "give"], 1, 1),
        QItem("Funksiya chaqirilganda unga beriladigan qiymat nima deb ataladi?", "Argument", ["Parametr", "Natija", "O‘zgaruvchi"], 2, 1),
        QItem("Funksiya ta'rifidagi o‘zgaruvchilar nima deb ataladi?", "Parametrlar", ["Argumentlar", "Natijalar", "O‘zgaruvchilar"], 2, 1),
        QItem("Global o‘zgaruvchini funksiya ichida o‘zgartirish uchun qaysi so‘z kerak?", "global", ["local", "nonlocal", "change"], 3, 2),
        QItem("Hech narsa qaytarmaydigan funksiya natijasi nima bo‘ladi?", "None", ["0", "False", "Xatolik"], 2, 1),
    ]
    pool += discrete
    pool += _py8_q3_extra()
    random.shuffle(pool)
    return pool


# ─── PYTHON — 8-sinf 4-chorak ────────────────────────────────────────────────
# Mavzu: Fayllar bilan ishlash (open, read, write), exception (try/except).

PY_8_Q4_CONCEPTS = [
    ("open() funksiyasi", "Faylni ochish uchun ishlatiladi", ["Faylni yopish", "Faylni o‘chirish", "Rasm chizish"], 1),
    ("mode='r'", "Faylni faqat o‘qish uchun ochish rejimi", ["Yozish", "Qo‘shish", "O‘chirish"], 1),
    ("mode='w'", "Faylni yozish uchun ochish (mavjud bo‘lsa ustidan yozadi)", ["O‘qish", "Qo‘shish", "Xatolik"], 1),
    ("mode='a'", "Fayl oxiriga ma'lumot qo‘shish (append) rejimi", ["O‘qish", "Yozish", "O‘chirish"], 1),
    (".read()", "Faylning butun mazmunini o‘qib olish", ["Faqat bir qator", "Faqat bitta belgi", "Yozish"], 2),
    (".readline()", "Fayldan faqat bitta qatorni o‘qish", ["Butun faylni", "Faqat bir so‘zni", "O‘chirish"], 2),
    (".write()", "Faylga ma'lumot yozish", ["O‘qish", "Yopish", "O‘chirish"], 2),
    (".close()", "Faylni yopish — resursni bo‘shatish", ["Oshirish", "O‘chirish", "Saqlash"], 1),
    ("with open(...) as f", "Faylni xavfsiz ochish va avtomatik yopish usuli", ["Faqat o‘qish", "Faqat yozish", "Xavfsiz bo‘lmagan usul"], 3),
    ("FileNotFoundError", "Ochmoqchi bo‘lgan fayl mavjud bo‘lmasa chiqadigan xato", ["ValueError", "TypeError", "IndexError"], 2),
]


def _py8_q4_pool() -> list[QItem]:
    pool: list[QItem] = []
    for c, d, w, l in PY_8_Q4_CONCEPTS:
        pool += _conceptual(c, d, w, lesson=l)

    def t_file_mode():
        modes = [('r', 'O‘qish'), ('w', 'Yozish'), ('a', 'Qo‘shish')]
        m, desc = random.choice(modes)
        return QItem(text=f"Pythonda `open('data.txt', '{m}')` buyrug‘ida '{m}' nimani bildiradi?",
                     answer=desc, wrongs=["O‘chirish", "Aylantirish", "Saqlash"], difficulty=1, lesson=1)

    def t_try_except():
        a = random.randint(1, 10)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\ntry:\n    print({a} / 0)\nexcept ZeroDivisionError:\n    print('Xato')\n```",
                     answer="Xato", wrongs=[str(a), "0", "None"], difficulty=2, lesson=2)

    pool += _capped(t_file_mode)
    pool += _capped(t_try_except)

    discrete = [
        QItem("Faylni yopish nima uchun muhim?", "Resurslarni bo‘shatish va ma'lumot saqlanishini ta'minlash uchun",
              ["Muhim emas", "Faqat rasm uchun", "Faqat virusdan himoya"], 2, 1),
        QItem("with open(...) ishlatishning afzalligi?", "Faylni avtomatik yopadi", ["Tezroq o‘qiydi", "Faqat yozadi", "Hech qanday"], 2, 1),
        QItem("Fayl ichidagi barcha qatorlarni ro‘yxat ko‘rinishida olish uchun?", ".readlines()", [".read()", ".write()", ".pop()"], 3, 1),
    ]
    pool += discrete
    pool += _py8_q4_extra()
    random.shuffle(pool)
    return pool


# ─── PYTHON — 9-sinf 1-chorak ────────────────────────────────────────────────
# Mavzu: Modullar (import), Math, Random, Datetime, PIP.

PY_9_Q1_CONCEPTS = [
    ("Modul (Module)", "Python kodini o‘z ichiga olgan alohida .py fayl", ["Faqat rasm", "Faqat rasm", "Faqat apparat"], 1),
    ("import kalit so‘zi", "Boshqa modulni joriy dasturga ulash", ["export", "include", "def"], 1),
    ("math moduli", "Matematik funksiyalar (sqrt, sin, pi) to‘plami", ["Faqat rasm", "Faqat o‘yin", "Faqat matn"], 1),
    ("math.sqrt(x)", "Sonning kvadrat ildizini hisoblash", ["Kvadratga ko‘tarish", "Modul", "Butun qism"], 2),
    ("random moduli", "Tasodifiy sonlar bilan ishlash moduli", ["Faqat matematika", "Faqat sana", "Faqat matn"], 1),
    ("datetime moduli", "Sana va vaqt bilan ishlash moduli", ["Faqat rasm", "Faqat matematika", "Faqat o‘yin"], 1),
    ("PIP", "Python paketlar menejeri — tashqi kutubxonalarni o‘rnatish uchun", ["Operatsion tizim", "Brauzer", "Dastur tili"], 2),
    ("Standard Library", "Python bilan birga keladigan tayyor modullar to‘plami", ["Faqat PIP orqali", "Faqat pullik", "Hech qanday"], 2),
    ("from math import pi", "Moduldan faqat kerakli qismni (pi) import qilish", ["Butun modulni", "Hech narsani", "Xatolik"], 2),
    ("as kalit so‘zi", "Modulga qisqa nom (alias) berish (masalan import math as m)", ["O‘chirish", "Yozish", "Saqlash"], 2),
]


def _py9_q1_pool() -> list[QItem]:
    pool: list[QItem] = []
    for c, d, w, l in PY_9_Q1_CONCEPTS:
        pool += _conceptual(c, d, w, lesson=l)

    def t_math_sqrt():
        a = random.choice([4, 9, 16, 25, 36, 49, 64, 81, 100])
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nimport math\nprint(math.sqrt({a}))\n```",
                     answer=str(float(int(a**0.5))), wrongs=[str(a), str(a*2), "None"], difficulty=2, lesson=1)

    def t_random_range():
        a = random.randint(1, 10); b = random.randint(20, 50)
        return QItem(text=f"Pythonda `random.randint({a}, {b})` qaysi oraliqdagi sonni qaytaradi?",
                     answer=f"{a} dan {b} gacha ({b} ham kiradi)", wrongs=[f"{a} dan {b} gacha ({b} kirmaydi)", "Faqat 0 va 1", "Xatolik"], difficulty=2, lesson=2)

    pool += _capped(t_math_sqrt)
    pool += _capped(t_random_range)

    discrete = [
        QItem("Kutubxonani PIP orqali o‘rnatish buyrug‘i qaysi?", "pip install kutubxona_nomi", ["pip get", "python install", "install"], 2, 1),
        QItem("Hozirgi sana va vaqtni olish uchun?", "datetime.datetime.now()", ["time.now()", "now()", "date()"], 2, 1),
        QItem("math.pi qiymati taxminan nechaga teng?", "3.1415...", ["2.71", "1.41", "0"], 1, 1),
    ]
    pool += discrete
    pool += _py9_q1_extra()
    random.shuffle(pool)
    return pool


# ─── PYTHON — 9-sinf 2-chorak ────────────────────────────────────────────────
# Mavzu: OOP asoslari (Class, Object, Init, Methods).

PY_9_Q2_CONCEPTS = [
    ("OOP", "Obyektga yo‘naltirilgan dasturlash", ["Faqat chiziqli", "Faqat funksional", "Faqat rasm"], 1),
    ("Klass (Class)", "Obyekt yaratish uchun shablon (chizma)", ["Faqat bitta son", "Faqat funksiya", "Faqat rasm"], 1),
    ("Obyekt (Object / Instance)", "Klassdan yaratilgan aniq nusxa", ["Faqat shablon", "Faqat modul", "Faqat o‘zgaruvchi"], 1),
    ("Atribut (Attribute)", "Obyektning xususiyati (masalan rangi, nomi)", ["Harakati", "Natijasi", "Faqat son"], 2),
    ("Metod (Method)", "Klass ichidagi funksiya — obyekt bajara oladigan amal", ["Faqat o‘zgaruvchi", "Faqat shart", "Faqat rasm"], 2),
    ("__init__", "Klassdan yangi obyekt yaratilganda avtomatik ishlovchi metod (konstruktor)", ["O‘chirish metodi", "Natija metodi", "Saqlash"], 3),
    ("self", "Joriy obyektning o‘ziga ishora qiluvchi parametr", ["Global o‘zgaruvchi", "Faqat raqam", "Xatolik"], 3),
    ("Inheritance (Vorislik)", "Bir klass xususiyatlarini boshqa klassga o‘tkazish", ["O‘chirish", "Yopish", "Faqat nusxa"], 3),
    ("Encapsulation", "Ma'lumotlarni himoyalash va yashirish", ["Oshirish", "O‘chirish", "Faqat nusxa"], 3),
    ("Polymorphism", "Bir xil nomli metodning turli klasslarda turlicha ishlashi", ["Faqat bitta ish", "O‘chirish", "Faqat saqlash"], 3),
]


def _py9_q2_pool() -> list[QItem]:
    pool: list[QItem] = []
    for c, d, w, l in PY_9_Q2_CONCEPTS:
        pool += _conceptual(c, d, w, lesson=l)

    def t_class_attr():
        val = random.randint(1, 1000)
        attr = random.choice(["x", "y", "val", "data", "n"])
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nclass Data:\n    {attr} = {val}\nd1 = Data()\nprint(d1.{attr})\n```",
                     answer=str(val), wrongs=[str(val+1), "Data", "None"], difficulty=2, lesson=1)

    pool += _capped(t_class_attr)

    discrete = [
        QItem("Klass qaysi kalit so‘z bilan yaratiladi?", "class", ["def", "object", "init"], 1, 1),
        QItem("__init__ metodi qachon ishlaydi?", "Obyekt yaratilgan paytda", ["Faqat chaqirilganda", "Dastur tugaganda", "Hech qachon"], 2, 3),
        QItem("Obyektning atributiga qanday murojaat qilinadi?", "obyekt.atribut", ["obyekt(atribut)", "obyekt->atribut", "atribut(obyekt)"], 2, 1),
    ]
    pool += discrete
    pool += _py9_q2_extra()
    random.shuffle(pool)
    return pool


# ─── PYTHON — 9-sinf 3-chorak ────────────────────────────────────────────────
# Mavzu: Murakkab algoritmlar, Ma'lumotlar tuzilmasi, Stack/Queue (nazariy).

PY_9_Q3_CONCEPTS = [
    ("Stack", "LIFO (Oxirgi kirgan, birinchi chiqadi) tuzilmasi", ["FIFO", "Faqat rasm", "Faqat o‘yin"], 2),
    ("Queue (Navbat)", "FIFO (Birinchi kirgan, birinchi chiqadi) tuzilmasi", ["LIFO", "Faqat rasm", "Faqat o‘yin"], 2),
    ("Rekursiya", "Funksiyaning o‘zini-o‘zi chaqirishi", ["Faqat sikl", "Faqat shart", "Faqat rasm"], 3),
    ("Base case", "Rekursiya to‘xtashi uchun zarur bo‘lgan shart", ["Cheksiz shart", "Faqat return 0", "Faqat input"], 3),
    ("Algoritm murakkabligi", "Vaqt va xotira sarfi (O(n))", ["Faqat rang", "Faqat o‘lcham", "Faqat narx"], 3),
    ("Binary Search", "Saralangan ro‘yxatda ikkiga bo‘lish orqali izlash", ["Ketma-ket izlash", "Tasodifiy izlash", "Faqat rasm"], 3),
    ("Bubble Sort", "Elementlarni juftlab solishtirib saralash", ["Tezkor saralash", "Tasodifiy", "Hech qanday"], 3),
    ("Big O notation", "Algoritm samaradorligini o‘lchash usuli", ["Faqat o‘yin", "Faqat rasm", "Faqat ovoz"], 3),
]


def _py9_q3_pool() -> list[QItem]:
    pool: list[QItem] = []
    for c, d, w, l in PY_9_Q3_CONCEPTS:
        pool += _conceptual(c, d, w, lesson=l)

    discrete = [
        QItem("Stack tuzilmasi qaysi tamoyilga asoslangan?", "LIFO", ["FIFO", "FILO", "RANDOM"], 2, 1),
        QItem("Queue (navbat) tuzilmasi qaysi tamoyilga asoslangan?", "FIFO", ["LIFO", "FILO", "RANDOM"], 2, 1),
        QItem("Rekursiya qachon to‘xtaydi?", "To‘xtash sharti (base case) bajarilganda", ["Hech qachon", "RAM to‘lganda", "Dastur yopilganda"], 2, 3),
    ]
    pool += discrete
    
    def t_stack_simulate():
        stack = []
        ops = []
        for _ in range(random.randint(3, 5)):
            v = random.randint(1, 50)
            stack.append(v)
            ops.append(f"s.append({v})")
        for _ in range(random.randint(1, 2)):
            if stack:
                stack.pop()
                ops.append("s.pop()")
        ops_str = "\n".join(ops)
        ans = stack[-1] if stack else "None"
        return QItem(text=f"Quyidagi Stack amallaridan so'ng `s[-1]` nimaga teng?\n\n```python\ns = []\n{ops_str}\nprint(s[-1])\n```",
                     answer=str(ans), wrongs=[str(random.randint(1, 50)), "0", "Xatolik"], difficulty=3, lesson=1)
    
    def t_recursion_simple():
        a = random.randint(2, 5)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\ndef f(n):\n    if n <= 1: return 1\n    return n + f(n-1)\nprint(f({a}))\n```",
                     answer=str(sum(range(a + 1))), wrongs=[str(a), "1", "Xatolik"], difficulty=3, lesson=3)

    pool += _capped(t_stack_simulate)
    pool += _capped(t_recursion_simple)
    pool += _py9_q3_extra()
    random.shuffle(pool)
    return pool


# ─── PYTHON — 9-sinf 4-chorak ────────────────────────────────────────────────
# Mavzu: Yakuniy loyiha, GUI (Tkinter basics), Review.

PY_9_Q4_CONCEPTS = [
    ("GUI", "Grafik foydalanuvchi interfeysi (oynalar, tugmalar)", ["Faqat matn", "Faqat ovoz", "Faqat apparat"], 1),
    ("Tkinter", "Python bilan birga keluvchi standart GUI kutubxonasi", ["PyGame", "Django", "Flask"], 2),
    ("Widget (Vidjet)", "Interfeys elementi (tugma, matn maydoni, yorliq)", ["Faqat rasm", "Faqat algoritm", "Faqat kod"], 2),
    ("Button", "Foydalanuvchi bosishi mumkin bo‘lgan tugma", ["Faqat matn", "Faqat rasm", "Faqat oyna"], 1),
    ("Label", "Ekranda matn yoki tasvir ko‘rsatuvchi element", ["Kiritish maydoni", "Tugma", "Sikl"], 2),
    ("Entry", "Foydalanuvchi matn kiritadigan maydon", ["Faqat tugma", "Faqat rasm", "Faqat oyna"], 2),
    ("mainloop()", "GUI oynasini ekranda ushlab turish va voqealarni kutish", ["Oynani yopish", "Rasm chizish", "Saqlash"], 3),
]


def _py9_q4_pool() -> list[QItem]:
    pool: list[QItem] = []
    for c, d, w, l in PY_9_Q4_CONCEPTS:
        pool += _conceptual(c, d, w, lesson=l)

    discrete = [
        QItem("Tkinterda asosiy oynani yaratish buyrug‘i qaysi?", "root = Tk()", ["root = Window()", "root = Main()", "root = Screen()"], 2, 2),
        QItem("GUI nima?", "Grafik interfeys (tugmalar, menyular)", ["Faqat konsol", "Faqat algoritm", "Faqat xotira"], 1, 1),
    ]
    pool += discrete
    random.shuffle(pool)
    return pool


# ─── Dispatchers ─────────────────────────────────────────────────────────────

def python_pool(grade: int, quarter: int) -> list[QItem]:
    if grade == 7:
        if quarter == 1: return _py7_get_q1_pool()
        if quarter == 2: return _py7_q2_pool()
        if quarter == 3: return _py7_q3_pool()
        if quarter == 4:
            # Cumulative: Q1 + Q2 + Q3 + Q4
            return _py7_get_q1_pool() + _py7_q2_pool() + _py7_q3_pool() + _py7_q4_pool()
    if grade == 8:
        if quarter == 1: return _py8_q1_pool()
        if quarter == 2: return _py8_q2_pool()
        if quarter == 3: return _py8_q3_pool()
        if quarter == 4:
            # Cumulative: Q1 + Q2 + Q3 + Q4
            return _py8_q1_pool() + _py8_q2_pool() + _py8_q3_pool() + _py8_q4_pool()
    if grade == 9:
        if quarter == 1: return _py9_q1_pool()
        if quarter == 2: return _py9_get_q2_pool() if '_py9_get_q2_pool' in globals() else _py9_q2_pool()
        if quarter == 3: return _py9_q3_pool()
        if quarter == 4:
            # Cumulative: Q1 + Q2 + Q3 + Q4
            p1 = _py9_q1_pool()
            p2 = _py9_q2_pool()
            p3 = _py9_q3_pool()
            p4 = _py9_q4_pool()
            return p1 + p2 + p3 + p4
    return []

# Fixing previous reference name from user context
def _py7_get_q1_pool():
    # In case it was named differently in the truncated part
    if '_py7_q1_pool' in globals():
        return globals()['_py7_q1_pool']()
    return []


def rebuild_all():
    from app import app
    from extensions import db
    from models import Subject, Question, ControlWork

    with app.app_context():
        print("Starting Database Rebuild...")
        
        # 1. Clear old data for relevant subjects
        target_subjects = ["Informatika", "Python"]
        for sname in target_subjects:
            subject = Subject.query.filter_by(name=sname).first()
            if subject:
                print(f"Clearing old questions for {sname}...")
                # Delete related control work associations first to avoid FK errors
                # Actually SQLAlchemy handles this if configured, but let's be safe
                # Clear control works for this subject too
                cworks = ControlWork.query.filter_by(subject_id=subject.id).all()
                for cw in cworks:
                    cw.questions = [] # Clear association table
                    db.session.delete(cw)
                
                # Delete questions
                Question.query.filter_by(subject_id=subject.id).delete()
                db.session.commit()
            else:
                print(f"Creating subject: {sname}")
                if sname == "Informatika":
                    subject = Subject(name="Informatika", grades="5,6", question_count=20, time_limit=30)
                else:
                    subject = Subject(name="Python", grades="7,8,9", question_count=20, time_limit=30)
                db.session.add(subject)
                db.session.commit()

        # 2. Generate new questions
        configs = [
            ("Informatika", [5, 6]),
            ("Python", [7, 8, 9])
        ]

        for sname, grades in configs:
            subject = Subject.query.filter_by(name=sname).first()
            for grade in grades:
                for quarter in range(1, 5):
                    print(f"Generating for {sname} - {grade}-sinf, {quarter}-chorak...")
                    
                    if sname == "Informatika":
                        pool_items = informatics_pool(grade, quarter)
                    else:
                        pool_items = python_pool(grade, quarter)

                    if not pool_items:
                        print(f"  WARNING: No pool items for {grade}-{quarter}")
                        continue

                    # We need 300 questions.
                    # We will shuffle the pool and take what we can.
                    # If we need more, we call the generators in the pool again if they are dynamic.
                    
                    final_questions = []
                    added_texts = set()
                    
                    # We need 300 questions.
                    # We will repeatedly call the pool generator to get more random variants if needed.
                    count_needed = 300
                    attempts = 0
                    while len(final_questions) < count_needed and attempts < 200:
                        if sname == "Informatika":
                            current_pool = informatics_pool(grade, quarter)
                        else:
                            current_pool = python_pool(grade, quarter)
                            
                        random.shuffle(current_pool)
                        for item in current_pool:
                            if item.text not in added_texts:
                                final_questions.append(item)
                                added_texts.add(item.text)
                            if len(final_questions) >= count_needed:
                                break
                        attempts += 1
                    
                    print(f"  Generated {len(final_questions)} unique questions (Attempts: {attempts}).")
                    
                    # Save questions to DB
                    db_questions = []
                    for i, q in enumerate(final_questions):
                        # Ensure options are shuffled
                        opts = [q.answer] + q.wrongs
                        random.shuffle(opts)
                        
                        correct_idx = opts.index(q.answer)
                        correct_letter = chr(65 + correct_idx) # A, B, C, D
                        
                        db_q = Question(
                            subject_id=subject.id,
                            grade=grade,
                            quarter=quarter,
                            difficulty=q.difficulty,
                            lesson=q.lesson,
                            question_text=q.text,
                            option_a=opts[0],
                            option_b=opts[1],
                            option_c=opts[2],
                            option_d=opts[3] if len(opts) > 3 else "N/A",
                            correct_answer=correct_letter
                        )
                        db.session.add(db_q)
                        db_questions.append(db_q)
                    
                    db.session.commit() # Get IDs

                    # Create Control Work (Top 100)
                    cw_title = f"{grade}-sinf {quarter}-chorak Nazorat ishi"
                    cw = ControlWork(
                        title=cw_title,
                        subject_id=subject.id,
                        grade=grade,
                        quarter=quarter,
                        time_limit=45
                    )
                    # Pick top 100 (best difficulty mix)
                    # Sort by difficulty 3, then 2, then 1
                    db_questions.sort(key=lambda x: x.difficulty, reverse=True)
                    cw.questions = db_questions[:100]
                    db.session.add(cw)
                    db.session.commit()

        print("Rebuild Completed Successfully!")


# ─── EXTRA GENERATORS FOR PYTHON 8-9 ──────────────────────────────────────────

def _py8_q3_extra() -> list[QItem]:
    pool = []
    
    def t_func_area():
        w = random.randint(2, 10); h = random.randint(2, 10)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\ndef area(w, h):\n    return w * h\nprint(area({w}, {h}))\n```",
                     answer=str(w*h), wrongs=[str(w+h), str(w*h+1), "0"], difficulty=2, lesson=1)
                     
    def t_func_unpack():
        a = random.randint(1, 10); b = random.randint(11, 20)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\ndef get_coords():\n    return {a}, {b}\nx, y = get_coords()\nprint(y)\n```",
                     answer=str(b), wrongs=[str(a), f"({a}, {b})", "Xatolik"], difficulty=3, lesson=1)

    def t_recursive_sum():
        n = random.randint(3, 5)
        def s(x): return x + s(x-1) if x > 0 else 0
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\ndef mysum(n):\n    if n == 0: return 0\n    return n + mysum(n-1)\nprint(mysum({n}))\n```",
                     answer=str(s(n)), wrongs=[str(n), "0", "Xatolik"], difficulty=3, lesson=1)

    def t_func_max3():
        a = random.randint(1, 50); b = random.randint(1, 50); c = random.randint(1, 50)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\ndef mx(a, b, c):\n    return max(a, b, c)\nprint(mx({a}, {b}, {c}))\n```",
                     answer=str(max(a, b, c)), wrongs=[str(min(a, b, c)), str(a+b+c), "Xatolik"], difficulty=2, lesson=1)

    def t_func_is_even():
        n = random.randint(1, 100)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\ndef is_even(n):\n    return n % 2 == 0\nprint(is_even({n}))\n```",
                     answer=str(n % 2 == 0), wrongs=[str(not (n % 2 == 0)), "None", "0"], difficulty=2, lesson=2)

    def t_func_str_len():
        s = random.choice(["python", "code", "function", "return", "class"])
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\ndef get_len(s):\n    return len(s)\nprint(get_len('{s}'))\n```",
                     answer=str(len(s)), wrongs=[str(len(s)+1), "0", "None"], difficulty=1, lesson=1)

    def t_func_default_param():
        a = random.randint(1, 10); b = random.randint(1, 10)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\ndef add(a, b={b}):\n    return a + b\nprint(add({a}))\n```",
                     answer=str(a+b), wrongs=[str(a), str(b), "Xatolik"], difficulty=3, lesson=3)

    pool += _capped(t_func_area)
    pool += _capped(t_func_unpack)
    pool += _capped(t_recursive_sum)
    pool += _capped(t_func_max3)
    pool += _capped(t_func_is_even)
    pool += _capped(t_func_str_len)
    pool += _capped(t_func_default_param)
    return pool

def _py8_q4_extra() -> list[QItem]:
    pool = []
    def t_try_multi():
        a = random.randint(1, 10)
        err = random.choice(["ZeroDivisionError", "ValueError", "TypeError"])
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\ntry:\n    x = {a} / 0\nexcept {err}:\n    print('Ushlandi')\nexcept:\n    print('Boshqa')\n```",
                     answer="Ushlandi" if err == "ZeroDivisionError" else "Boshqa", 
                     wrongs=["Ushlandi", "Boshqa", "Xatolik"], difficulty=3, lesson=2)

    def t_try_else():
        a = random.randint(1, 10)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\ntry:\n    x = {a} + 5\nexcept:\n    print('Xato')\nelse:\n    print('Ok')\n```",
                     answer="Ok", wrongs=["Xato", "Ok Xato", "None"], difficulty=3, lesson=2)

    def t_try_finally():
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\ntry:\n    print('A')\nfinally:\n    print('B')\n```",
                     answer="A\nB", wrongs=["A", "B", "Xatolik"], difficulty=3, lesson=2)

    pool += _capped(t_try_multi)
    pool += _capped(t_try_else)
    pool += _capped(t_try_finally)
    return pool

def _py9_q1_extra() -> list[QItem]:
    pool = []
    def t_math_ceil_floor():
        v = random.uniform(2.1, 8.9)
        op = random.choice(["ceil", "floor"])
        import math
        ans = math.ceil(v) if op == "ceil" else math.floor(v)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nimport math\nprint(math.{op}({v:.2f}))\n```",
                     answer=str(ans), wrongs=[str(ans+1), str(ans-1), "0"], difficulty=2, lesson=1)

    def t_random_choice():
        L = [random.randint(1, 100) for _ in range(5)]
        return QItem(text=f"Pythonda `random.choice({L})` nima qiladi?",
                     answer="Ro'yxatdan tasodifiy bitta elementni tanlaydi", 
                     wrongs=["Ro'yxatni aralashtiradi", "Eng katta elementni topadi", "Xatolik beradi"], difficulty=2, lesson=1)

    def t_math_pi_pow():
        a = random.randint(2, 5)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nimport math\nprint(math.pow({a}, 2))\n```",
                     answer=f"{float(a**2)}", wrongs=[str(a*2), str(a+2), "Xatolik"], difficulty=2, lesson=1)

    def t_datetime_year():
        y = random.randint(2000, 2025)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nimport datetime\nd = datetime.date({y}, 5, 12)\nprint(d.year)\n```",
                     answer=str(y), wrongs=["5", "12", "Xatolik"], difficulty=2, lesson=1)

    pool += _capped(t_math_ceil_floor)
    pool += _capped(t_random_choice)
    pool += _capped(t_math_pi_pow)
    pool += _capped(t_datetime_year)
    return pool

def _py9_q2_extra() -> list[QItem]:
    pool = []
    def t_oop_method():
        names = ["Rex", "Barsik", "Simba", "Aktosh", "Olapar", "Momiq", "Qoplon"]
        name = random.choice(names)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nclass Dog:\n    def __init__(self, name):\n        self.name = name\n    def bark(self):\n        return f'I am {{self.name}}'\nd = Dog('{name}')\nprint(d.bark())\n```",
                     answer=f"I am {name}", wrongs=[name, "Dog", "Xatolik"], difficulty=2, lesson=2)

    def t_oop_attr_change():
        v1 = random.randint(1, 100); v2 = random.randint(101, 200)
        attr = random.choice(["val", "score", "level", "x"])
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nclass Player:\n    def __init__(self, {attr}):\n        self.{attr} = {attr}\np = Player({v1})\np.{attr} = {v2}\nprint(p.{attr})\n```",
                     answer=str(v2), wrongs=[str(v1), "0", "Xatolik"], difficulty=2, lesson=1)

    def t_oop_calc():
        a = random.randint(2, 10); b = random.randint(2, 10)
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\nclass Calc:\n    def add(self, x, y): return x + y\nc = Calc()\nprint(c.add({a}, {b}))\n```",
                     answer=str(a+b), wrongs=[str(a*b), str(a), "Xatolik"], difficulty=2, lesson=1)

    pool += _capped(t_oop_method)
    pool += _capped(t_oop_attr_change)
    pool += _capped(t_oop_calc)
    return pool

def _py9_q3_extra() -> list[QItem]:
    pool = []
    def t_stack_ops():
        L = [random.randint(1, 100) for _ in range(3)]
        v = random.randint(101, 200)
        return QItem(text=f"Quyidagi Stack amallari natijasi nima?\n\n```python\nstack = {L}\nstack.append({v})\nstack.pop()\nprint(stack[-1])\n```",
                     answer=str(L[-1]), wrongs=[str(v), str(L[0]), "Xatolik"], difficulty=3, lesson=1)

    def t_queue_ops():
        from collections import deque
        L = [random.randint(1, 100) for _ in range(3)]
        v = random.randint(101, 200)
        return QItem(text=f"Quyidagi Queue (LIFO emas, FIFO) amallari natijasi nima?\n\n```python\nfrom collections import deque\nq = deque({L})\nq.append({v})\nq.popleft()\nprint(list(q)[0])\n```",
                     answer=str(L[1]), wrongs=[str(L[0]), str(v), "Xatolik"], difficulty=3, lesson=1)

    def t_recursion_depth():
        n = random.randint(3, 5)
        def f(x): return x * f(x-1) if x > 1 else 1
        return QItem(text=f"Quyidagi kod natijasi nima?\n\n```python\ndef fact(n):\n    if n <= 1: return 1\n    return n * fact(n-1)\nprint(fact({n}))\n```",
                     answer=str(f(n)), wrongs=[str(n), "1", "Xatolik"], difficulty=3, lesson=3)

    pool += _capped(t_stack_ops)
    pool += _capped(t_queue_ops)
    pool += _capped(t_recursion_depth)
    return pool

def _py9_q4_extra() -> list[QItem]:
    pool = []
    def t_tkinter_root():
        return QItem(text="Tkinterda asosiy oynani yaratish uchun qaysi klass ishlatiladi?",
                     answer="Tk()", wrongs=["Window()", "Main()", "Root()"], difficulty=1, lesson=2)

    def t_tkinter_widget():
        return QItem(text="Tkinterda foydalanuvchi bosishi uchun mo'ljallangan element qaysi?",
                     answer="Button", wrongs=["Label", "Entry", "Frame"], difficulty=1, lesson=2)

    pool += _capped(t_tkinter_root)
    pool += _capped(t_tkinter_widget)
    return pool


if __name__ == "__main__":
    rebuild_all()

