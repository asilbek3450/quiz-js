"""
Arena masalalari seed skripti.
Ishlatish: python3 scripts/seed_arena.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app
from models import db, ArenaProblem
import json

PROBLEMS = [
    # ── A001-A010: Kirish/Chiqish va Oddiy Arifmetika ───────────────────────
    {
        "code": "A001",
        "title": "Ikki son yig'indisi",
        "description": (
            "Ikkita butun son berilgan. Ularning yig'indisini toping.\n\n"
            "Dastur yozing va quyidagi kirish uchun natijani toping:\n"
            "a = 47, b = 58"
        ),
        "input_format": "Birinchi qatorda a, ikkinchi qatorda b.",
        "output_format": "Bitta qatorda yig'indi.",
        "constraints": "−10^9 ≤ a, b ≤ 10^9",
        "examples": [
            {"input": "5\n3", "output": "8", "explanation": "5 + 3 = 8"},
            {"input": "47\n58", "output": "105", "explanation": "47 + 58 = 105"},
        ],
        "difficulty": "easy",
        "category": "Arifmetika",
        "correct_answer": "105",
    },
    {
        "code": "A002",
        "title": "Ayirma",
        "description": (
            "a va b butun sonlar berilgan. a − b ni toping.\n\n"
            "Kirish: a = 100, b = 37"
        ),
        "input_format": "Birinchi qatorda a, ikkinchi qatorda b.",
        "output_format": "Bitta qatorda ayirma.",
        "constraints": "−10^9 ≤ a, b ≤ 10^9",
        "examples": [
            {"input": "10\n3", "output": "7", "explanation": "10 − 3 = 7"},
            {"input": "100\n37", "output": "63", "explanation": "100 − 37 = 63"},
        ],
        "difficulty": "easy",
        "category": "Arifmetika",
        "correct_answer": "63",
    },
    {
        "code": "A003",
        "title": "Ko'paytma",
        "description": (
            "a va b butun sonlar berilgan. a × b ni toping.\n\n"
            "Kirish: a = 12, b = 15"
        ),
        "input_format": "Birinchi qatorda a, ikkinchi qatorda b.",
        "output_format": "Bitta qatorda ko'paytma.",
        "constraints": "−10^4 ≤ a, b ≤ 10^4",
        "examples": [
            {"input": "6\n7", "output": "42", "explanation": "6 × 7 = 42"},
            {"input": "12\n15", "output": "180", "explanation": "12 × 15 = 180"},
        ],
        "difficulty": "easy",
        "category": "Arifmetika",
        "correct_answer": "180",
    },
    {
        "code": "A004",
        "title": "Bo'linma (haqiqiy son)",
        "description": (
            "a va b butun sonlar berilgan. a / b haqiqiy bo'linmasini 2 kasrgacha aniqlang.\n\n"
            "Kirish: a = 22, b = 7"
        ),
        "input_format": "Birinchi qatorda a, ikkinchi qatorda b (b ≠ 0).",
        "output_format": "Bitta qatorda, 2 kasrli haqiqiy son.",
        "constraints": "−10^9 ≤ a, b ≤ 10^9, b ≠ 0",
        "examples": [
            {"input": "10\n4", "output": "2.50", "explanation": "10 / 4 = 2.5"},
            {"input": "22\n7", "output": "3.14", "explanation": "22 / 7 ≈ 3.142..."},
        ],
        "difficulty": "easy",
        "category": "Arifmetika",
        "correct_answer": "3.14",
    },
    {
        "code": "A005",
        "title": "Butun bo'linma va qoldiq",
        "description": (
            "a va b butun sonlar berilgan. a // b (butun bo'linma) va a % b (qoldiq) ni toping.\n\n"
            "Kirish: a = 17, b = 5"
        ),
        "input_format": "Birinchi qatorda a, ikkinchi qatorda b (b > 0).",
        "output_format": "Birinchi qatorda a//b, ikkinchi qatorda a%b.",
        "constraints": "0 ≤ a ≤ 10^9, 1 ≤ b ≤ 10^9",
        "examples": [
            {"input": "13\n4", "output": "3\n1", "explanation": "13//4=3, 13%4=1"},
            {"input": "17\n5", "output": "3\n2", "explanation": "17//5=3, 17%5=2"},
        ],
        "difficulty": "easy",
        "category": "Arifmetika",
        "correct_answer": "3\n2",
    },
    {
        "code": "A006",
        "title": "Kvadrat va kub",
        "description": (
            "n butun soni berilgan. n² va n³ ni hisoblang.\n\n"
            "Kirish: n = 7"
        ),
        "input_format": "Bitta qatorda n.",
        "output_format": "Birinchi qatorda n², ikkinchi qatorda n³.",
        "constraints": "1 ≤ n ≤ 1000",
        "examples": [
            {"input": "4", "output": "16\n64", "explanation": "4²=16, 4³=64"},
            {"input": "7", "output": "49\n343", "explanation": "7²=49, 7³=343"},
        ],
        "difficulty": "easy",
        "category": "Arifmetika",
        "correct_answer": "49\n343",
    },
    {
        "code": "A007",
        "title": "O'rta arifmetik",
        "description": (
            "3 ta haqiqiy son berilgan. Ularning o'rta arifmetiğini toping (2 kasrgacha).\n\n"
            "Kirish: a=10, b=20, c=30"
        ),
        "input_format": "Har bir son alohida qatorda.",
        "output_format": "Bitta qatorda o'rta arifmetik (2 kasr).",
        "constraints": "−10^6 ≤ a, b, c ≤ 10^6",
        "examples": [
            {"input": "3\n7\n11", "output": "7.00", "explanation": "(3+7+11)/3 = 7.0"},
            {"input": "10\n20\n30", "output": "20.00", "explanation": "(10+20+30)/3 = 20.0"},
        ],
        "difficulty": "easy",
        "category": "Arifmetika",
        "correct_answer": "20.00",
    },
    {
        "code": "A008",
        "title": "Doira yuzi",
        "description": (
            "Doira radiusi r berilgan. S = π × r² formulasi bo'yicha doira yuzini hisoblang.\n"
            "π = 3.14159265358979 qiymatini ishlating. Natijani 2 kasrgacha yozing.\n\n"
            "Kirish: r = 10"
        ),
        "input_format": "Bitta qatorda r (haqiqiy son).",
        "output_format": "Bitta qatorda doira yuzi (2 kasr).",
        "constraints": "0 < r ≤ 10^4",
        "examples": [
            {"input": "5", "output": "78.54", "explanation": "π × 5² = 78.539..."},
            {"input": "10", "output": "314.16", "explanation": "π × 10² = 314.159..."},
        ],
        "difficulty": "easy",
        "category": "Arifmetika",
        "correct_answer": "314.16",
    },
    {
        "code": "A009",
        "title": "Uchburchak yuzi",
        "description": (
            "Uchburchakning asosi a va balandligi h berilgan. Yuzi S = (a × h) / 2.\n"
            "Natijani 2 kasrgacha yozing.\n\n"
            "Kirish: a=8, h=5"
        ),
        "input_format": "Birinchi qatorda a, ikkinchi qatorda h.",
        "output_format": "Bitta qatorda yuzi (2 kasr).",
        "constraints": "0 < a, h ≤ 10^4",
        "examples": [
            {"input": "6\n4", "output": "12.00", "explanation": "6×4/2 = 12"},
            {"input": "8\n5", "output": "20.00", "explanation": "8×5/2 = 20"},
        ],
        "difficulty": "easy",
        "category": "Arifmetika",
        "correct_answer": "20.00",
    },
    {
        "code": "A010",
        "title": "To'g'ri to'rtburchak perimetri",
        "description": (
            "To'g'ri to'rtburchakning tomonlari a va b berilgan. P = 2 × (a + b).\n\n"
            "Kirish: a=13, b=7"
        ),
        "input_format": "Birinchi qatorda a, ikkinchi qatorda b.",
        "output_format": "Bitta qatorda perimetr.",
        "constraints": "1 ≤ a, b ≤ 10^6",
        "examples": [
            {"input": "5\n3", "output": "16", "explanation": "2×(5+3) = 16"},
            {"input": "13\n7", "output": "40", "explanation": "2×(13+7) = 40"},
        ],
        "difficulty": "easy",
        "category": "Arifmetika",
        "correct_answer": "40",
    },

    # ── A011-A020: Shart operatorlari ────────────────────────────────────────
    {
        "code": "A011",
        "title": "Musbat, manfiy yoki nol",
        "description": (
            "Butun son n berilgan. Agar n > 0 bo'lsa 'musbat', n < 0 bo'lsa 'manfiy', "
            "n == 0 bo'lsa 'nol' chiqaring.\n\n"
            "Kirish: n = -17"
        ),
        "input_format": "Bitta qatorda n.",
        "output_format": "'musbat', 'manfiy' yoki 'nol'.",
        "constraints": "−10^9 ≤ n ≤ 10^9",
        "examples": [
            {"input": "5", "output": "musbat"},
            {"input": "-17", "output": "manfiy"},
            {"input": "0", "output": "nol"},
        ],
        "difficulty": "easy",
        "category": "Shart",
        "correct_answer": "manfiy",
    },
    {
        "code": "A012",
        "title": "Juft yoki toq",
        "description": (
            "Butun son n berilgan. n % 2 asosida 'Juft' yoki 'Toq' chiqaring.\n\n"
            "Kirish: n = 2025"
        ),
        "input_format": "Bitta qatorda n.",
        "output_format": "'Juft' yoki 'Toq'.",
        "constraints": "0 ≤ n ≤ 10^9",
        "examples": [
            {"input": "4", "output": "Juft"},
            {"input": "2025", "output": "Toq"},
        ],
        "difficulty": "easy",
        "category": "Shart",
        "correct_answer": "Toq",
    },
    {
        "code": "A013",
        "title": "Eng katta son (2 ta)",
        "description": (
            "2 ta butun son berilgan. Ulardan eng kattasini chiqaring. "
            "Teng bo'lsa istalganini chiqaring.\n\n"
            "Kirish: a=73, b=58"
        ),
        "input_format": "Birinchi qatorda a, ikkinchi qatorda b.",
        "output_format": "Bitta qatorda eng katta son.",
        "constraints": "−10^9 ≤ a, b ≤ 10^9",
        "examples": [
            {"input": "7\n3", "output": "7"},
            {"input": "73\n58", "output": "73"},
        ],
        "difficulty": "easy",
        "category": "Shart",
        "correct_answer": "73",
    },
    {
        "code": "A014",
        "title": "Eng kichik son (3 ta)",
        "description": (
            "3 ta butun son berilgan. Ulardan eng kichigini chiqaring.\n\n"
            "Kirish: a=45, b=12, c=67"
        ),
        "input_format": "Har bir son alohida qatorda.",
        "output_format": "Bitta qatorda eng kichik son.",
        "constraints": "−10^9 ≤ a, b, c ≤ 10^9",
        "examples": [
            {"input": "5\n2\n8", "output": "2"},
            {"input": "45\n12\n67", "output": "12"},
        ],
        "difficulty": "easy",
        "category": "Shart",
        "correct_answer": "12",
    },
    {
        "code": "A015",
        "title": "10 dan katta va 100 dan kichik",
        "description": (
            "Butun son n berilgan. Agar 10 < n < 100 bo'lsa 'Ha', aks holda 'Yo'q' chiqaring.\n\n"
            "Kirish: n = 55"
        ),
        "input_format": "Bitta qatorda n.",
        "output_format": "'Ha' yoki 'Yo'q'.",
        "constraints": "−10^9 ≤ n ≤ 10^9",
        "examples": [
            {"input": "50", "output": "Ha"},
            {"input": "100", "output": "Yo'q"},
            {"input": "55", "output": "Ha"},
        ],
        "difficulty": "easy",
        "category": "Shart",
        "correct_answer": "Ha",
    },
    {
        "code": "A016",
        "title": "Uchburchak mavjudligi",
        "description": (
            "3 ta tomonning uzunliklari a, b, c berilgan. Agar ular uchburchak hosil qila olsa "
            "'Ha', aks holda 'Yo'q' chiqaring.\n"
            "Shart: har bir tomon qolgan ikki tomonning yig'indisidan kichik bo'lishi kerak.\n\n"
            "Kirish: a=3, b=4, c=5"
        ),
        "input_format": "Har bir tomon alohida qatorda.",
        "output_format": "'Ha' yoki 'Yo'q'.",
        "constraints": "1 ≤ a, b, c ≤ 10^4",
        "examples": [
            {"input": "1\n1\n10", "output": "Yo'q", "explanation": "1+1 < 10"},
            {"input": "3\n4\n5", "output": "Ha", "explanation": "3+4>5, 3+5>4, 4+5>3"},
        ],
        "difficulty": "easy",
        "category": "Shart",
        "correct_answer": "Ha",
    },
    {
        "code": "A017",
        "title": "Kabisa yili",
        "description": (
            "Yil raqami berilgan. Kabisa yili bo'lsa 'Ha', aks holda 'Yo'q' chiqaring.\n"
            "Kabisa yili sharti: (yil % 4 == 0 va yil % 100 != 0) yoki (yil % 400 == 0).\n\n"
            "Kirish: yil = 2024"
        ),
        "input_format": "Bitta qatorda yil.",
        "output_format": "'Ha' yoki 'Yo'q'.",
        "constraints": "1 ≤ yil ≤ 9999",
        "examples": [
            {"input": "2000", "output": "Ha", "explanation": "2000 % 400 == 0"},
            {"input": "1900", "output": "Yo'q", "explanation": "1900 % 100 == 0, lekin 1900 % 400 != 0"},
            {"input": "2024", "output": "Ha", "explanation": "2024 % 4 == 0 va % 100 != 0"},
        ],
        "difficulty": "easy",
        "category": "Shart",
        "correct_answer": "Ha",
    },
    {
        "code": "A018",
        "title": "Harf yoki raqam",
        "description": (
            "Bitta belgi kiritiladi. Agar u harf bo'lsa 'Harf', raqam bo'lsa 'Raqam', "
            "boshqa belgi bo'lsa 'Boshqa' chiqaring.\n\n"
            "Kirish: '7'"
        ),
        "input_format": "Bitta belgi.",
        "output_format": "'Harf', 'Raqam' yoki 'Boshqa'.",
        "constraints": "Kiritilgan belgi bitta ASCII belgi.",
        "examples": [
            {"input": "A", "output": "Harf"},
            {"input": "7", "output": "Raqam"},
            {"input": "!", "output": "Boshqa"},
        ],
        "difficulty": "easy",
        "category": "Shart",
        "correct_answer": "Raqam",
    },
    {
        "code": "A019",
        "title": "Reyting bahosi",
        "description": (
            "0–100 oralig'idagi ball berilgan. Quyidagi qoidaga ko'ra baho bering:\n"
            "90–100 → A, 75–89 → B, 60–74 → C, 40–59 → D, 0–39 → F\n\n"
            "Kirish: ball = 82"
        ),
        "input_format": "Bitta qatorda ball (butun son).",
        "output_format": "Bitta harfli baho.",
        "constraints": "0 ≤ ball ≤ 100",
        "examples": [
            {"input": "95", "output": "A"},
            {"input": "82", "output": "B"},
            {"input": "55", "output": "D"},
        ],
        "difficulty": "easy",
        "category": "Shart",
        "correct_answer": "B",
    },
    {
        "code": "A020",
        "title": "Oy raqami → nomi",
        "description": (
            "1 dan 12 gacha oy raqami berilgan. Oy nomini o'zbek tilida chiqaring.\n\n"
            "Kirish: 9"
        ),
        "input_format": "Bitta qatorda oy raqami (1–12).",
        "output_format": "Oy nomi.",
        "constraints": "1 ≤ oy ≤ 12",
        "examples": [
            {"input": "1", "output": "Yanvar"},
            {"input": "9", "output": "Sentabr"},
            {"input": "12", "output": "Dekabr"},
        ],
        "difficulty": "easy",
        "category": "Shart",
        "correct_answer": "Sentabr",
    },

    # ── A021-A030: Takrorlash (for/while) ────────────────────────────────────
    {
        "code": "A021",
        "title": "1 dan n gacha sonlar",
        "description": (
            "n berilgan. 1 dan n gacha bo'lgan sonlarni bitta qatorda, bo'sh joy bilan ajratib chiqaring.\n\n"
            "Kirish: n = 7"
        ),
        "input_format": "Bitta qatorda n.",
        "output_format": "1 dan n gacha sonlar, bitta qatorda.",
        "constraints": "1 ≤ n ≤ 100",
        "examples": [
            {"input": "5", "output": "1 2 3 4 5"},
            {"input": "7", "output": "1 2 3 4 5 6 7"},
        ],
        "difficulty": "easy",
        "category": "Takrorlash",
        "correct_answer": "1 2 3 4 5 6 7",
    },
    {
        "code": "A022",
        "title": "1 dan n gacha yig'indi",
        "description": (
            "n berilgan. 1 + 2 + 3 + ... + n yig'indisini toping.\n\n"
            "Kirish: n = 100"
        ),
        "input_format": "Bitta qatorda n.",
        "output_format": "Bitta qatorda yig'indi.",
        "constraints": "1 ≤ n ≤ 10^6",
        "examples": [
            {"input": "5", "output": "15"},
            {"input": "100", "output": "5050"},
        ],
        "difficulty": "easy",
        "category": "Takrorlash",
        "correct_answer": "5050",
    },
    {
        "code": "A023",
        "title": "Faktorial",
        "description": (
            "n berilgan. n! = 1 × 2 × 3 × ... × n ni hisoblang.\n\n"
            "Kirish: n = 10"
        ),
        "input_format": "Bitta qatorda n.",
        "output_format": "Bitta qatorda n!",
        "constraints": "0 ≤ n ≤ 20",
        "examples": [
            {"input": "5", "output": "120"},
            {"input": "10", "output": "3628800"},
        ],
        "difficulty": "easy",
        "category": "Takrorlash",
        "correct_answer": "3628800",
    },
    {
        "code": "A024",
        "title": "n ta son yig'indisi",
        "description": (
            "Birinchi qatorda n, keyin n ta son (har biri alohida qatorda) beriladi. "
            "Ularning yig'indisini toping.\n\n"
            "Kirish: n=4, sonlar: 10 20 30 40"
        ),
        "input_format": "Birinchi qatorda n, keyin n ta son.",
        "output_format": "Bitta qatorda yig'indi.",
        "constraints": "1 ≤ n ≤ 10^5, −10^9 ≤ har bir son ≤ 10^9",
        "examples": [
            {"input": "3\n1\n2\n3", "output": "6"},
            {"input": "4\n10\n20\n30\n40", "output": "100"},
        ],
        "difficulty": "easy",
        "category": "Takrorlash",
        "correct_answer": "100",
    },
    {
        "code": "A025",
        "title": "Eng katta son (n ta)",
        "description": (
            "n ta son berilgan. Ulardan eng kattasini toping. max() funksiyasini ishlatmang.\n\n"
            "Kirish: n=6, sonlar: 3 1 4 1 5 9"
        ),
        "input_format": "Birinchi qatorda n, ikkinchi qatorda n ta son (bo'sh joy bilan).",
        "output_format": "Bitta qatorda eng katta son.",
        "constraints": "1 ≤ n ≤ 10^5",
        "examples": [
            {"input": "5\n3 1 4 1 5", "output": "5"},
            {"input": "6\n3 1 4 1 5 9", "output": "9"},
        ],
        "difficulty": "easy",
        "category": "Takrorlash",
        "correct_answer": "9",
    },
    {
        "code": "A026",
        "title": "Juft sonlar soni",
        "description": (
            "n ta son berilgan. Ulardan nechta juft son borligini toping.\n\n"
            "Kirish: n=8, sonlar: 1 2 3 4 5 6 7 8"
        ),
        "input_format": "Birinchi qatorda n, ikkinchi qatorda n ta son.",
        "output_format": "Bitta qatorda juft sonlar soni.",
        "constraints": "1 ≤ n ≤ 10^5",
        "examples": [
            {"input": "5\n1 2 3 4 5", "output": "2"},
            {"input": "8\n1 2 3 4 5 6 7 8", "output": "4"},
        ],
        "difficulty": "easy",
        "category": "Takrorlash",
        "correct_answer": "4",
    },
    {
        "code": "A027",
        "title": "Bo'luvchilar soni",
        "description": (
            "n butun soni berilgan. Uning barcha bo'luvchilarining sonini toping.\n\n"
            "Kirish: n = 36"
        ),
        "input_format": "Bitta qatorda n.",
        "output_format": "Bitta qatorda bo'luvchilar soni.",
        "constraints": "1 ≤ n ≤ 10^6",
        "examples": [
            {"input": "12", "output": "6", "explanation": "1,2,3,4,6,12"},
            {"input": "36", "output": "9", "explanation": "1,2,3,4,6,9,12,18,36"},
        ],
        "difficulty": "easy",
        "category": "Takrorlash",
        "correct_answer": "9",
    },
    {
        "code": "A028",
        "title": "Tub son tekshirish",
        "description": (
            "n butun soni berilgan. Agar tub son bo'lsa 'Ha', aks holda 'Yo'q' chiqaring.\n"
            "Tub son: faqat 1 va o'ziga bo'linadigan son (n > 1).\n\n"
            "Kirish: n = 97"
        ),
        "input_format": "Bitta qatorda n.",
        "output_format": "'Ha' yoki 'Yo'q'.",
        "constraints": "2 ≤ n ≤ 10^7",
        "examples": [
            {"input": "7", "output": "Ha"},
            {"input": "15", "output": "Yo'q"},
            {"input": "97", "output": "Ha"},
        ],
        "difficulty": "easy",
        "category": "Takrorlash",
        "correct_answer": "Ha",
    },
    {
        "code": "A029",
        "title": "Raqamlar yig'indisi",
        "description": (
            "Musbat butun son n berilgan. Uning raqamlarining yig'indisini toping.\n"
            "Masalan: 123 → 1+2+3 = 6\n\n"
            "Kirish: n = 98765"
        ),
        "input_format": "Bitta qatorda n.",
        "output_format": "Bitta qatorda raqamlar yig'indisi.",
        "constraints": "1 ≤ n ≤ 10^18",
        "examples": [
            {"input": "123", "output": "6"},
            {"input": "98765", "output": "35", "explanation": "9+8+7+6+5 = 35"},
        ],
        "difficulty": "easy",
        "category": "Takrorlash",
        "correct_answer": "35",
    },
    {
        "code": "A030",
        "title": "Teskari son",
        "description": (
            "Musbat butun son n berilgan. Uning raqamlarini teskari tartibda yozing.\n"
            "Masalan: 12345 → 54321\n\n"
            "Kirish: n = 987654"
        ),
        "input_format": "Bitta qatorda n.",
        "output_format": "Bitta qatorda teskari son.",
        "constraints": "1 ≤ n ≤ 10^9",
        "examples": [
            {"input": "12345", "output": "54321"},
            {"input": "987654", "output": "456789"},
        ],
        "difficulty": "easy",
        "category": "Takrorlash",
        "correct_answer": "456789",
    },

    # ── A031-A040: Takrorlash (murakkab) ─────────────────────────────────────
    {
        "code": "A031",
        "title": "Palindrom son",
        "description": (
            "Butun son n berilgan. Agar u palindrom bo'lsa 'YES', aks holda 'NO' chiqaring.\n"
            "Palindrom: teskari yozilganda ham asl son bilan teng.\n\n"
            "Kirish: n = 12321"
        ),
        "input_format": "Bitta qatorda n.",
        "output_format": "'YES' yoki 'NO'.",
        "constraints": "1 ≤ n ≤ 10^9",
        "examples": [
            {"input": "121", "output": "YES"},
            {"input": "12321", "output": "YES"},
            {"input": "12345", "output": "NO"},
        ],
        "difficulty": "medium",
        "category": "Takrorlash",
        "correct_answer": "YES",
    },
    {
        "code": "A032",
        "title": "Fibonachchi soni",
        "description": (
            "n berilgan. Fibonachchi ketma-ketligining n-hadini toping.\n"
            "F(1)=1, F(2)=1, F(n)=F(n-1)+F(n-2).\n\n"
            "Kirish: n = 10"
        ),
        "input_format": "Bitta qatorda n.",
        "output_format": "Bitta qatorda F(n).",
        "constraints": "1 ≤ n ≤ 50",
        "examples": [
            {"input": "7", "output": "13", "explanation": "1,1,2,3,5,8,13"},
            {"input": "10", "output": "55", "explanation": "10-had = 55"},
        ],
        "difficulty": "medium",
        "category": "Takrorlash",
        "correct_answer": "55",
    },
    {
        "code": "A033",
        "title": "Ikkilik sanoqqa o'tkazish",
        "description": (
            "Musbat butun son n berilgan. Uni ikkilik (binary) sanoqqa o'tkazing.\n"
            "bin() Python funksiyasini ishlatmang.\n\n"
            "Kirish: n = 42"
        ),
        "input_format": "Bitta qatorda n.",
        "output_format": "Bitta qatorda ikkilik ko'rinish (faqat 0 va 1).",
        "constraints": "1 ≤ n ≤ 10^9",
        "examples": [
            {"input": "10", "output": "1010"},
            {"input": "42", "output": "101010"},
        ],
        "difficulty": "medium",
        "category": "Takrorlash",
        "correct_answer": "101010",
    },
    {
        "code": "A034",
        "title": "EKUB — Eng katta umumiy bo'luvchi",
        "description": (
            "Ikkita musbat butun son a va b berilgan. Ularning EKUB ini toping.\n\n"
            "Kirish: a=48, b=18"
        ),
        "input_format": "Birinchi qatorda a, ikkinchi qatorda b.",
        "output_format": "Bitta qatorda EKUB.",
        "constraints": "1 ≤ a, b ≤ 10^9",
        "examples": [
            {"input": "12\n8", "output": "4"},
            {"input": "48\n18", "output": "6"},
        ],
        "difficulty": "medium",
        "category": "Takrorlash",
        "correct_answer": "6",
    },
    {
        "code": "A035",
        "title": "EKUK — Eng kichik umumiy karrali",
        "description": (
            "Ikkita musbat butun son a va b berilgan. Ularning EKUK ini toping.\n"
            "EKUK(a,b) = a × b / EKUB(a,b)\n\n"
            "Kirish: a=12, b=18"
        ),
        "input_format": "Birinchi qatorda a, ikkinchi qatorda b.",
        "output_format": "Bitta qatorda EKUK.",
        "constraints": "1 ≤ a, b ≤ 10^6",
        "examples": [
            {"input": "4\n6", "output": "12"},
            {"input": "12\n18", "output": "36"},
        ],
        "difficulty": "medium",
        "category": "Takrorlash",
        "correct_answer": "36",
    },
    {
        "code": "A036",
        "title": "Garmonik qator yig'indisi",
        "description": (
            "n berilgan. H = 1 + 1/2 + 1/3 + ... + 1/n yig'indisini 4 kasrgacha toping.\n\n"
            "Kirish: n = 10"
        ),
        "input_format": "Bitta qatorda n.",
        "output_format": "Bitta qatorda yig'indi (4 kasr).",
        "constraints": "1 ≤ n ≤ 10^5",
        "examples": [
            {"input": "4", "output": "2.0833", "explanation": "1+0.5+0.333+0.25 ≈ 2.0833"},
            {"input": "10", "output": "2.9290"},
        ],
        "difficulty": "medium",
        "category": "Takrorlash",
        "correct_answer": "2.9290",
    },
    {
        "code": "A037",
        "title": "Darajaga oshirish",
        "description": (
            "a va b sonlar berilgan. a^b ni hisoblang. ** operatori yoki pow() ishlatmang.\n\n"
            "Kirish: a=3, b=8"
        ),
        "input_format": "Birinchi qatorda a, ikkinchi qatorda b.",
        "output_format": "Bitta qatorda a^b.",
        "constraints": "1 ≤ a ≤ 100, 0 ≤ b ≤ 30",
        "examples": [
            {"input": "2\n10", "output": "1024"},
            {"input": "3\n8", "output": "6561"},
        ],
        "difficulty": "medium",
        "category": "Takrorlash",
        "correct_answer": "6561",
    },
    {
        "code": "A038",
        "title": "Sonni so'z bilan chiqarish",
        "description": (
            "0 dan 9 gacha butun son berilgan. Uni o'zbek tilida so'z bilan chiqaring.\n\n"
            "Kirish: n = 6"
        ),
        "input_format": "Bitta qatorda n (0–9).",
        "output_format": "Sonning o'zbek tilidagi nomi.",
        "constraints": "0 ≤ n ≤ 9",
        "examples": [
            {"input": "0", "output": "nol"},
            {"input": "6", "output": "olti"},
            {"input": "9", "output": "to'qqiz"},
        ],
        "difficulty": "easy",
        "category": "Shart",
        "correct_answer": "olti",
    },
    {
        "code": "A039",
        "title": "Takrorlanuvchi sonni topish",
        "description": (
            "n ta son berilgan (1 dan n-1 gacha, biri ikki marta). Takrorlanuvchi sonni toping.\n\n"
            "Kirish: n=6, sonlar: 1 3 4 2 5 3"
        ),
        "input_format": "Birinchi qatorda n, ikkinchi qatorda n ta son (bo'sh joy bilan).",
        "output_format": "Bitta qatorda takrorlanuvchi son.",
        "constraints": "2 ≤ n ≤ 10^5",
        "examples": [
            {"input": "5\n1 2 3 2 4", "output": "2"},
            {"input": "6\n1 3 4 2 5 3", "output": "3"},
        ],
        "difficulty": "medium",
        "category": "Takrorlash",
        "correct_answer": "3",
    },
    {
        "code": "A040",
        "title": "Eng uzun o'suvchi ketma-ketlik",
        "description": (
            "n ta son berilgan. Eng uzun qo'shni (contiguous) o'suvchi ketma-ketlikning uzunligini toping.\n\n"
            "Kirish: n=8, sonlar: 1 2 3 1 2 3 4 5"
        ),
        "input_format": "Birinchi qatorda n, ikkinchi qatorda n ta son.",
        "output_format": "Bitta qatorda eng uzun o'suvchi ketma-ketlik uzunligi.",
        "constraints": "1 ≤ n ≤ 10^5",
        "examples": [
            {"input": "7\n1 2 3 1 2 6 7", "output": "4", "explanation": "1,2,6,7 → uzunlik 4"},
            {"input": "8\n1 2 3 1 2 3 4 5", "output": "5", "explanation": "1,2,3,4,5 → uzunlik 5"},
        ],
        "difficulty": "medium",
        "category": "Takrorlash",
        "correct_answer": "5",
    },

    # ── A041-A060: Massivlar va ro'yxatlar ───────────────────────────────────
    {
        "code": "A041",
        "title": "Ro'yxatdagi eng katta element",
        "description": (
            "n ta son berilgan. max() funksiyasini ishlatmay eng kattasini toping.\n\n"
            "Kirish: n=7, sonlar: 5 8 1 9 3 7 2"
        ),
        "input_format": "Birinchi qatorda n, ikkinchi qatorda n ta son.",
        "output_format": "Bitta qatorda eng katta element.",
        "constraints": "1 ≤ n ≤ 10^5",
        "examples": [
            {"input": "5\n3 1 4 1 5", "output": "5"},
            {"input": "7\n5 8 1 9 3 7 2", "output": "9"},
        ],
        "difficulty": "medium",
        "category": "Massiv",
        "correct_answer": "9",
    },
    {
        "code": "A042",
        "title": "Ro'yxatni teskari qilish",
        "description": (
            "n ta son berilgan. [::-1] ishlatmay teskari tartibda chiqaring.\n\n"
            "Kirish: n=5, sonlar: 10 20 30 40 50"
        ),
        "input_format": "Birinchi qatorda n, ikkinchi qatorda n ta son.",
        "output_format": "Teskari tartibdagi sonlar (bitta qatorda).",
        "constraints": "1 ≤ n ≤ 10^4",
        "examples": [
            {"input": "4\n1 2 3 4", "output": "4 3 2 1"},
            {"input": "5\n10 20 30 40 50", "output": "50 40 30 20 10"},
        ],
        "difficulty": "medium",
        "category": "Massiv",
        "correct_answer": "50 40 30 20 10",
    },
    {
        "code": "A043",
        "title": "Ro'yxatdagi juft elementlar soni",
        "description": (
            "n ta son berilgan. Juft sonlar sonini toping.\n\n"
            "Kirish: n=8, sonlar: 2 3 4 5 6 7 8 9"
        ),
        "input_format": "Birinchi qatorda n, ikkinchi qatorda n ta son.",
        "output_format": "Bitta qatorda juft elementlar soni.",
        "constraints": "1 ≤ n ≤ 10^5",
        "examples": [
            {"input": "6\n1 2 3 4 5 6", "output": "3"},
            {"input": "8\n2 3 4 5 6 7 8 9", "output": "4"},
        ],
        "difficulty": "medium",
        "category": "Massiv",
        "correct_answer": "4",
    },
    {
        "code": "A044",
        "title": "Ro'yxatdagi o'rtacha qiymat",
        "description": (
            "n ta son berilgan. O'rtacha qiymatini 2 kasrgacha toping.\n\n"
            "Kirish: n=5, sonlar: 10 20 30 40 50"
        ),
        "input_format": "Birinchi qatorda n, ikkinchi qatorda n ta son.",
        "output_format": "O'rtacha qiymat (2 kasr).",
        "constraints": "1 ≤ n ≤ 10^5",
        "examples": [
            {"input": "4\n1 2 3 4", "output": "2.50"},
            {"input": "5\n10 20 30 40 50", "output": "30.00"},
        ],
        "difficulty": "medium",
        "category": "Massiv",
        "correct_answer": "30.00",
    },
    {
        "code": "A045",
        "title": "Ro'yxatni o'sish tartibida saralash",
        "description": (
            "n ta son berilgan. sort() yoki sorted() ishlatmay pufakcha saralash (bubble sort) bilan tartiblang.\n\n"
            "Kirish: n=6, sonlar: 5 3 8 1 9 2"
        ),
        "input_format": "Birinchi qatorda n, ikkinchi qatorda n ta son.",
        "output_format": "Saralangan sonlar (bitta qatorda).",
        "constraints": "1 ≤ n ≤ 1000",
        "examples": [
            {"input": "5\n5 3 1 4 2", "output": "1 2 3 4 5"},
            {"input": "6\n5 3 8 1 9 2", "output": "1 2 3 5 8 9"},
        ],
        "difficulty": "medium",
        "category": "Massiv",
        "correct_answer": "1 2 3 5 8 9",
    },
    {
        "code": "A046",
        "title": "Ro'yxatda qidirish",
        "description": (
            "n ta son va qidirilayotgan k berilgan. Agar k ro'yxatda bo'lsa 'Ha', aks holda 'Yo'q'.\n\n"
            "Kirish: n=5, sonlar: 3 7 1 9 5, k=9"
        ),
        "input_format": "Birinchi qatorda n, ikkinchi qatorda n ta son, uchinchi qatorda k.",
        "output_format": "'Ha' yoki 'Yo'q'.",
        "constraints": "1 ≤ n ≤ 10^5",
        "examples": [
            {"input": "5\n1 2 3 4 5\n3", "output": "Ha"},
            {"input": "5\n3 7 1 9 5\n9", "output": "Ha"},
            {"input": "5\n3 7 1 9 5\n6", "output": "Yo'q"},
        ],
        "difficulty": "medium",
        "category": "Massiv",
        "correct_answer": "Ha",
    },
    {
        "code": "A047",
        "title": "Takrorlanuvchi elementlar soni",
        "description": (
            "n ta son berilgan. 2 yoki undan ko'p marta takrorlangan (noyob bo'lmagan) "
            "elementlar sonini toping.\n\n"
            "Kirish: n=7, sonlar: 1 2 2 3 3 3 4"
        ),
        "input_format": "Birinchi qatorda n, ikkinchi qatorda n ta son.",
        "output_format": "Bitta qatorda takrorlanuvchi elementlar soni.",
        "constraints": "1 ≤ n ≤ 10^5",
        "examples": [
            {"input": "6\n1 2 2 3 3 4", "output": "2", "explanation": "2 va 3 takrorlanadi"},
            {"input": "7\n1 2 2 3 3 3 4", "output": "2"},
        ],
        "difficulty": "medium",
        "category": "Massiv",
        "correct_answer": "2",
    },
    {
        "code": "A048",
        "title": "Ikkita ro'yxat birlashmasi",
        "description": (
            "Ikkita ro'yxat berilgan. Ularni birlashtiriib bitta ro'yxat sifatida chiqaring "
            "(birinchi ro'yxat keyin ikkinchisi).\n\n"
            "Kirish: [1 2 3] va [4 5 6]"
        ),
        "input_format": "Birinchi qatorda n1 va n1 ta son. Ikkinchi qatorda n2 va n2 ta son.",
        "output_format": "Birlashgan ro'yxat (bitta qatorda).",
        "constraints": "1 ≤ n1, n2 ≤ 10^4",
        "examples": [
            {"input": "3\n1 2 3\n3\n4 5 6", "output": "1 2 3 4 5 6"},
            {"input": "2\n10 20\n3\n30 40 50", "output": "10 20 30 40 50"},
        ],
        "difficulty": "easy",
        "category": "Massiv",
        "correct_answer": "1 2 3 4 5 6",
    },
    {
        "code": "A049",
        "title": "Eng katta va eng kichik farq",
        "description": (
            "n ta son berilgan. max − min ni toping.\n\n"
            "Kirish: n=6, sonlar: 4 8 2 15 3 11"
        ),
        "input_format": "Birinchi qatorda n, ikkinchi qatorda n ta son.",
        "output_format": "Bitta qatorda farq.",
        "constraints": "1 ≤ n ≤ 10^5",
        "examples": [
            {"input": "5\n1 3 5 2 8", "output": "7"},
            {"input": "6\n4 8 2 15 3 11", "output": "13"},
        ],
        "difficulty": "medium",
        "category": "Massiv",
        "correct_answer": "13",
    },
    {
        "code": "A050",
        "title": "Ro'yxatni siklik siljitish",
        "description": (
            "n ta son va k berilgan. Ro'yxatni k pozitsiyaga o'ngga siklik siljiting.\n"
            "Masalan: [1,2,3,4,5], k=2 → [4,5,1,2,3]\n\n"
            "Kirish: n=5, k=3, sonlar: 1 2 3 4 5"
        ),
        "input_format": "Birinchi qatorda n va k, ikkinchi qatorda n ta son.",
        "output_format": "Siljitilgan ro'yxat (bitta qatorda).",
        "constraints": "1 ≤ n ≤ 10^4, 0 ≤ k ≤ n",
        "examples": [
            {"input": "5 2\n1 2 3 4 5", "output": "4 5 1 2 3"},
            {"input": "5 3\n1 2 3 4 5", "output": "3 4 5 1 2"},
        ],
        "difficulty": "medium",
        "category": "Massiv",
        "correct_answer": "3 4 5 1 2",
    },
    {
        "code": "A051",
        "title": "Ro'yxatdagi nollar soni",
        "description": (
            "n ta son berilgan. Nollar sonini toping.\n\n"
            "Kirish: n=8, sonlar: 0 1 0 2 0 3 0 4"
        ),
        "input_format": "Birinchi qatorda n, ikkinchi qatorda n ta son.",
        "output_format": "Bitta qatorda nollar soni.",
        "constraints": "1 ≤ n ≤ 10^5",
        "examples": [
            {"input": "6\n0 1 0 2 0 3", "output": "3"},
            {"input": "8\n0 1 0 2 0 3 0 4", "output": "4"},
        ],
        "difficulty": "easy",
        "category": "Massiv",
        "correct_answer": "4",
    },
    {
        "code": "A052",
        "title": "Musbat va manfiy sonlar soni",
        "description": (
            "n ta son berilgan. Musbat va manfiy sonlar sonini toping (nolni inobatga olmang).\n\n"
            "Kirish: n=7, sonlar: 1 -2 3 -4 5 -6 0"
        ),
        "input_format": "Birinchi qatorda n, ikkinchi qatorda n ta son.",
        "output_format": "Birinchi qatorda musbat soni, ikkinchi qatorda manfiy soni.",
        "constraints": "1 ≤ n ≤ 10^5",
        "examples": [
            {"input": "5\n1 -2 3 -4 5", "output": "3\n2"},
            {"input": "7\n1 -2 3 -4 5 -6 0", "output": "3\n3"},
        ],
        "difficulty": "medium",
        "category": "Massiv",
        "correct_answer": "3\n3",
    },
    {
        "code": "A053",
        "title": "Elementlarni kvadratga oshirish",
        "description": (
            "n ta son berilgan. Har birini kvadratga oshirib chiqaring.\n\n"
            "Kirish: n=5, sonlar: 1 2 3 4 5"
        ),
        "input_format": "Birinchi qatorda n, ikkinchi qatorda n ta son.",
        "output_format": "Kvadratlangan sonlar (bitta qatorda).",
        "constraints": "1 ≤ n ≤ 10^4, −100 ≤ har bir son ≤ 100",
        "examples": [
            {"input": "4\n1 2 3 4", "output": "1 4 9 16"},
            {"input": "5\n1 2 3 4 5", "output": "1 4 9 16 25"},
        ],
        "difficulty": "easy",
        "category": "Massiv",
        "correct_answer": "1 4 9 16 25",
    },
    {
        "code": "A054",
        "title": "Toq indeksdagi elementlar",
        "description": (
            "n ta son berilgan. Toq indeksdagi (1, 3, 5, ...) elementlarni chiqaring (0-dan boshlab).\n\n"
            "Kirish: n=6, sonlar: 10 20 30 40 50 60"
        ),
        "input_format": "Birinchi qatorda n, ikkinchi qatorda n ta son.",
        "output_format": "Toq indeksdagi elementlar (bitta qatorda).",
        "constraints": "2 ≤ n ≤ 10^4",
        "examples": [
            {"input": "5\n10 20 30 40 50", "output": "20 40"},
            {"input": "6\n10 20 30 40 50 60", "output": "20 40 60"},
        ],
        "difficulty": "medium",
        "category": "Massiv",
        "correct_answer": "20 40 60",
    },
    {
        "code": "A055",
        "title": "Qo'shni elementlar yig'indisi",
        "description": (
            "n ta son berilgan. Qo'shni juftlarning yig'indisini chiqaring: "
            "a[0]+a[1], a[1]+a[2], ..., a[n-2]+a[n-1].\n\n"
            "Kirish: n=5, sonlar: 1 2 3 4 5"
        ),
        "input_format": "Birinchi qatorda n, ikkinchi qatorda n ta son.",
        "output_format": "Qo'shni yig'indilar (bitta qatorda).",
        "constraints": "2 ≤ n ≤ 10^4",
        "examples": [
            {"input": "4\n1 2 3 4", "output": "3 5 7"},
            {"input": "5\n1 2 3 4 5", "output": "3 5 7 9"},
        ],
        "difficulty": "medium",
        "category": "Massiv",
        "correct_answer": "3 5 7 9",
    },
    {
        "code": "A056",
        "title": "Ro'yxatni ikkiga bo'lish",
        "description": (
            "n ta son berilgan. Ro'yxatni ikki teng qismga bo'lib chiqaring. "
            "n toq bo'lsa, birinchi qism kattaroq bo'lsin.\n\n"
            "Kirish: n=6, sonlar: 1 2 3 4 5 6"
        ),
        "input_format": "Birinchi qatorda n, ikkinchi qatorda n ta son.",
        "output_format": "Birinchi qatorda birinchi yarmi, ikkinchi qatorda ikkinchi yarmi.",
        "constraints": "2 ≤ n ≤ 10^4",
        "examples": [
            {"input": "4\n1 2 3 4", "output": "1 2\n3 4"},
            {"input": "6\n1 2 3 4 5 6", "output": "1 2 3\n4 5 6"},
        ],
        "difficulty": "medium",
        "category": "Massiv",
        "correct_answer": "1 2 3\n4 5 6",
    },
    {
        "code": "A057",
        "title": "Eng uzun o'suvchi qism ro'yxat",
        "description": (
            "n ta son berilgan. Qo'shni (contiguous) elementlardan iborat eng uzun o'suvchi "
            "qism ro'yxatning uzunligini toping.\n\n"
            "Kirish: n=8, sonlar: 1 2 3 1 2 3 4 5"
        ),
        "input_format": "Birinchi qatorda n, ikkinchi qatorda n ta son.",
        "output_format": "Bitta qatorda uzunlik.",
        "constraints": "1 ≤ n ≤ 10^5",
        "examples": [
            {"input": "7\n5 1 2 3 0 7 8", "output": "3", "explanation": "1,2,3 — uzunlik 3"},
            {"input": "8\n1 2 3 1 2 3 4 5", "output": "5", "explanation": "1,2,3,4,5"},
        ],
        "difficulty": "medium",
        "category": "Massiv",
        "correct_answer": "5",
    },
    {
        "code": "A058",
        "title": "Elementlarni o'zaro almashtirish",
        "description": (
            "n ta son va ikkita indeks i, j berilgan. a[i] va a[j] ni almashtirib chiqaring.\n\n"
            "Kirish: n=5, sonlar: 1 2 3 4 5, i=1, j=3"
        ),
        "input_format": "Birinchi qatorda n, ikkinchi qatorda n ta son, uchinchi qatorda i va j.",
        "output_format": "Almashtirilgandan keyingi ro'yxat (bitta qatorda).",
        "constraints": "1 ≤ n ≤ 10^4, 0 ≤ i, j < n",
        "examples": [
            {"input": "5\n1 2 3 4 5\n0 4", "output": "5 2 3 4 1"},
            {"input": "5\n1 2 3 4 5\n1 3", "output": "1 4 3 2 5"},
        ],
        "difficulty": "medium",
        "category": "Massiv",
        "correct_answer": "1 4 3 2 5",
    },
    {
        "code": "A059",
        "title": "Ro'yxatdagi o'rta element",
        "description": (
            "n ta son berilgan (n toq). O'rtadagi elementni chiqaring.\n\n"
            "Kirish: n=7, sonlar: 10 20 30 40 50 60 70"
        ),
        "input_format": "Birinchi qatorda n (toq), ikkinchi qatorda n ta son.",
        "output_format": "Bitta qatorda o'rta element.",
        "constraints": "1 ≤ n ≤ 10^5 (n toq)",
        "examples": [
            {"input": "5\n1 2 3 4 5", "output": "3"},
            {"input": "7\n10 20 30 40 50 60 70", "output": "40"},
        ],
        "difficulty": "easy",
        "category": "Massiv",
        "correct_answer": "40",
    },
    {
        "code": "A060",
        "title": "Ro'yxatni chap siklik siljitish",
        "description": (
            "n ta son va k berilgan. Ro'yxatni k pozitsiyaga chapga siklik siljiting.\n"
            "Masalan: [1,2,3,4,5], k=2 → [3,4,5,1,2]\n\n"
            "Kirish: n=6, k=4, sonlar: 1 2 3 4 5 6"
        ),
        "input_format": "Birinchi qatorda n va k, ikkinchi qatorda n ta son.",
        "output_format": "Siljitilgan ro'yxat (bitta qatorda).",
        "constraints": "1 ≤ n ≤ 10^4, 0 ≤ k ≤ n",
        "examples": [
            {"input": "5 2\n1 2 3 4 5", "output": "3 4 5 1 2"},
            {"input": "6 4\n1 2 3 4 5 6", "output": "5 6 1 2 3 4"},
        ],
        "difficulty": "medium",
        "category": "Massiv",
        "correct_answer": "5 6 1 2 3 4",
    },

    # ── A061-A080: Satrlar ────────────────────────────────────────────────────
    {
        "code": "A061",
        "title": "Satr uzunligi",
        "description": (
            "Satr berilgan. len() funksiyasini ishlatmasdan uzunligini toping.\n\n"
            "Kirish: 'Assalomu alaykum'"
        ),
        "input_format": "Bitta qatorda satr.",
        "output_format": "Bitta qatorda uzunlik.",
        "constraints": "0 ≤ uzunlik ≤ 10^5",
        "examples": [
            {"input": "salom", "output": "5"},
            {"input": "Assalomu alaykum", "output": "16"},
        ],
        "difficulty": "medium",
        "category": "Satr",
        "correct_answer": "16",
    },
    {
        "code": "A062",
        "title": "Satrda unli harflar soni",
        "description": (
            "Satr berilgan. Unda nechta unli harf (a,e,i,o,u — katta-kichik) borligini toping.\n\n"
            "Kirish: 'Programming is fun'"
        ),
        "input_format": "Bitta qatorda satr.",
        "output_format": "Bitta qatorda unli harflar soni.",
        "constraints": "0 ≤ uzunlik ≤ 10^5",
        "examples": [
            {"input": "salom dunyo", "output": "4"},
            {"input": "Programming is fun", "output": "5"},
        ],
        "difficulty": "medium",
        "category": "Satr",
        "correct_answer": "5",
    },
    {
        "code": "A063",
        "title": "Satrni teskari qilish",
        "description": (
            "Satr berilgan. Uni teskari tartibda chiqaring. [::-1] ishlatmang.\n\n"
            "Kirish: 'Python'"
        ),
        "input_format": "Bitta qatorda satr.",
        "output_format": "Bitta qatorda teskari satr.",
        "constraints": "1 ≤ uzunlik ≤ 10^4",
        "examples": [
            {"input": "salom", "output": "molas"},
            {"input": "Python", "output": "nohtyP"},
        ],
        "difficulty": "medium",
        "category": "Satr",
        "correct_answer": "nohtyP",
    },
    {
        "code": "A064",
        "title": "Palindrom satr",
        "description": (
            "Satr berilgan. Agar palindrom bo'lsa 'YES', aks holda 'NO' chiqaring.\n"
            "(Faqat harflarni hisobga oling, katta-kichikka e'tibor bermang.)\n\n"
            "Kirish: 'A man a plan a canal Panama'"
        ),
        "input_format": "Bitta qatorda satr.",
        "output_format": "'YES' yoki 'NO'.",
        "constraints": "1 ≤ uzunlik ≤ 10^4",
        "examples": [
            {"input": "radar", "output": "YES"},
            {"input": "A man a plan a canal Panama", "output": "YES"},
            {"input": "hello", "output": "NO"},
        ],
        "difficulty": "medium",
        "category": "Satr",
        "correct_answer": "YES",
    },
    {
        "code": "A065",
        "title": "Satrda so'zlar soni",
        "description": (
            "Satr berilgan. Unda nechta so'z borligini toping (bo'shliqlar bilan ajratilgan).\n\n"
            "Kirish: 'men kitob o'qiyapman'"
        ),
        "input_format": "Bitta qatorda satr.",
        "output_format": "Bitta qatorda so'zlar soni.",
        "constraints": "1 ≤ uzunlik ≤ 10^4",
        "examples": [
            {"input": "salom dunyo biz", "output": "3"},
            {"input": "men kitob o'qiyapman", "output": "3"},
        ],
        "difficulty": "medium",
        "category": "Satr",
        "correct_answer": "3",
    },
    {
        "code": "A066",
        "title": "Satrda katta harflar soni",
        "description": (
            "Satr berilgan. Unda nechta katta (uppercase) harf borligini toping.\n\n"
            "Kirish: 'Hello World from Python'"
        ),
        "input_format": "Bitta qatorda satr.",
        "output_format": "Bitta qatorda katta harflar soni.",
        "constraints": "1 ≤ uzunlik ≤ 10^5",
        "examples": [
            {"input": "Hello World", "output": "2"},
            {"input": "Hello World from Python", "output": "3"},
        ],
        "difficulty": "medium",
        "category": "Satr",
        "correct_answer": "3",
    },
    {
        "code": "A067",
        "title": "Satrda raqamlar soni",
        "description": (
            "Satr berilgan. Unda nechta raqam (0–9) borligini toping.\n\n"
            "Kirish: 'abc123def456gh7'"
        ),
        "input_format": "Bitta qatorda satr.",
        "output_format": "Bitta qatorda raqamlar soni.",
        "constraints": "1 ≤ uzunlik ≤ 10^5",
        "examples": [
            {"input": "abc123def456", "output": "6"},
            {"input": "abc123def456gh7", "output": "7"},
        ],
        "difficulty": "medium",
        "category": "Satr",
        "correct_answer": "7",
    },
    {
        "code": "A068",
        "title": "Satrda belgi almashtirish",
        "description": (
            "Satr, eski belgi va yangi belgi berilgan. Satrda barcha eski belgini yangi belgi bilan almashtiring.\n\n"
            "Kirish: satr='salom dunyo', eski='o', yangi='a'"
        ),
        "input_format": "Birinchi qatorda satr, ikkinchi qatorda eski belgi, uchinchi qatorda yangi belgi.",
        "output_format": "O'zgartirilgan satr.",
        "constraints": "1 ≤ uzunlik ≤ 10^4",
        "examples": [
            {"input": "salom\na\ne", "output": "selem"},
            {"input": "salom dunyo\no\na", "output": "salam dunya"},
        ],
        "difficulty": "medium",
        "category": "Satr",
        "correct_answer": "salam dunya",
    },
    {
        "code": "A069",
        "title": "Eng ko'p uchragan belgi",
        "description": (
            "Satr berilgan. Eng ko'p uchragan belgini toping. "
            "Bir nechta teng bo'lsa, alfavit tartibidagi birinchisini chiqaring.\n\n"
            "Kirish: 'abracadabra'"
        ),
        "input_format": "Bitta qatorda satr.",
        "output_format": "Bitta belgi.",
        "constraints": "1 ≤ uzunlik ≤ 10^5",
        "examples": [
            {"input": "aababc", "output": "a"},
            {"input": "abracadabra", "output": "a", "explanation": "a 5 marta"},
        ],
        "difficulty": "medium",
        "category": "Satr",
        "correct_answer": "a",
    },
    {
        "code": "A070",
        "title": "Satrda so'zlarni ajratish",
        "description": (
            "Satr berilgan. Har bir so'zni alohida qatorda chiqaring.\n\n"
            "Kirish: 'Python juda qiziqarli'"
        ),
        "input_format": "Bitta qatorda satr.",
        "output_format": "Har bir so'z alohida qatorda.",
        "constraints": "1 ≤ so'zlar soni ≤ 100",
        "examples": [
            {"input": "salom dunyo", "output": "salom\ndunyo"},
            {"input": "Python juda qiziqarli", "output": "Python\njuda\nqiziqarli"},
        ],
        "difficulty": "medium",
        "category": "Satr",
        "correct_answer": "Python\njuda\nqiziqarli",
    },
    {
        "code": "A071",
        "title": "So'zlarni birlashtirish",
        "description": (
            "n ta so'z alohida qatorda berilgan. Ularni bitta satr sifatida chiqaring "
            "(bo'sh joy bilan ajratib).\n\n"
            "Kirish: n=4, so'zlar: Python juda qiziqarli til"
        ),
        "input_format": "Birinchi qatorda n, keyin n ta so'z.",
        "output_format": "Birlashtirilgan satr.",
        "constraints": "1 ≤ n ≤ 100",
        "examples": [
            {"input": "3\nsalom\ndunyo\nbiz", "output": "salom dunyo biz"},
            {"input": "4\nPython\njuda\nqiziqarli\ntil", "output": "Python juda qiziqarli til"},
        ],
        "difficulty": "easy",
        "category": "Satr",
        "correct_answer": "Python juda qiziqarli til",
    },
    {
        "code": "A072",
        "title": "So'zlar tartibini teskari qilish",
        "description": (
            "Satr berilgan. So'zlarni teskari tartibda chiqaring.\n\n"
            "Kirish: 'men dastur yozmoqdaman'"
        ),
        "input_format": "Bitta qatorda satr.",
        "output_format": "So'zlar teskari tartibda.",
        "constraints": "1 ≤ uzunlik ≤ 10^4",
        "examples": [
            {"input": "salom dunyo biz", "output": "biz dunyo salom"},
            {"input": "men dastur yozmoqdaman", "output": "yozmoqdaman dastur men"},
        ],
        "difficulty": "medium",
        "category": "Satr",
        "correct_answer": "yozmoqdaman dastur men",
    },
    {
        "code": "A073",
        "title": "Qavslar muvozanati (oddiy)",
        "description": (
            "Faqat '(' va ')' belgileridan iborat satr berilgan. "
            "Qavslar muvozanatli bo'lsa 'Ha', aks holda 'Yo'q' chiqaring.\n\n"
            "Kirish: '((()))'"
        ),
        "input_format": "Bitta qatorda satr.",
        "output_format": "'Ha' yoki 'Yo'q'.",
        "constraints": "1 ≤ uzunlik ≤ 10^4",
        "examples": [
            {"input": "(())", "output": "Ha"},
            {"input": "((()))", "output": "Ha"},
            {"input": "(()", "output": "Yo'q"},
        ],
        "difficulty": "medium",
        "category": "Satr",
        "correct_answer": "Ha",
    },
    {
        "code": "A074",
        "title": "Takrorlanuvchi belgilar soni",
        "description": (
            "Satr berilgan. 2 yoki undan ko'p marta takrorlangan (noyob bo'lmagan) "
            "turli xil belgilarning sonini toping.\n\n"
            "Kirish: 'aabbccddee'"
        ),
        "input_format": "Bitta qatorda satr.",
        "output_format": "Bitta qatorda son.",
        "constraints": "1 ≤ uzunlik ≤ 10^5",
        "examples": [
            {"input": "aabbcc", "output": "3"},
            {"input": "aabbccddee", "output": "5"},
        ],
        "difficulty": "medium",
        "category": "Satr",
        "correct_answer": "5",
    },
    {
        "code": "A075",
        "title": "Satrda eng uzun so'z",
        "description": (
            "Satr berilgan. Eng uzun so'zni chiqaring. Bir nechta teng bo'lsa, birinchisini.\n\n"
            "Kirish: 'bu satr ichidagi eng uzun soz bormi'"
        ),
        "input_format": "Bitta qatorda satr.",
        "output_format": "Bitta qatorda eng uzun so'z.",
        "constraints": "1 ≤ uzunlik ≤ 10^4",
        "examples": [
            {"input": "salom dunyo biz", "output": "dunyo"},
            {"input": "bu satr ichidagi eng uzun soz bormi", "output": "ichidagi"},
        ],
        "difficulty": "medium",
        "category": "Satr",
        "correct_answer": "ichidagi",
    },
    {
        "code": "A076",
        "title": "So'zlar chastotasi",
        "description": (
            "Satr berilgan. Har bir so'z necha marta uchraganini alfavit tartibida chiqaring.\n\n"
            "Kirish: 'olma nok olma banan nok olma'"
        ),
        "input_format": "Bitta qatorda satr.",
        "output_format": "Har qatorda: 'so'z: son'.",
        "constraints": "1 ≤ uzunlik ≤ 10^4",
        "examples": [
            {"input": "a b a c b a", "output": "a: 3\nb: 2\nc: 1"},
            {"input": "olma nok olma banan nok olma", "output": "banan: 1\nnok: 2\nolma: 3"},
        ],
        "difficulty": "medium",
        "category": "Satr",
        "correct_answer": "banan: 1\nnok: 2\nolma: 3",
    },
    {
        "code": "A077",
        "title": "So'zlarni alfavit tartibida chiqarish",
        "description": (
            "Satr berilgan. So'zlarni alfavit tartibida chiqaring.\n\n"
            "Kirish: 'banan olma gilos anor'"
        ),
        "input_format": "Bitta qatorda satr.",
        "output_format": "Alfavit tartibidagi so'zlar (bitta qatorda).",
        "constraints": "1 ≤ uzunlik ≤ 10^4",
        "examples": [
            {"input": "banan olma gilos", "output": "banan gilos olma"},
            {"input": "banan olma gilos anor", "output": "anor banan gilos olma"},
        ],
        "difficulty": "medium",
        "category": "Satr",
        "correct_answer": "anor banan gilos olma",
    },
    {
        "code": "A078",
        "title": "So'zlarni uzunligi bo'yicha saralash",
        "description": (
            "Satr berilgan. So'zlarni uzunligi bo'yicha o'sish tartibida chiqaring. "
            "Teng uzunlikdagilar alfavit tartibida.\n\n"
            "Kirish: 'Python bu kuchli dasturlash tili'"
        ),
        "input_format": "Bitta qatorda satr.",
        "output_format": "Tartib bo'yicha so'zlar (bitta qatorda).",
        "constraints": "1 ≤ uzunlik ≤ 10^4",
        "examples": [
            {"input": "bu katta kichik sozlar", "output": "bu sozlar katta kichik"},
            {"input": "Python bu kuchli dasturlash tili", "output": "bu tili kuchli Python dasturlash"},
        ],
        "difficulty": "medium",
        "category": "Satr",
        "correct_answer": "bu tili kuchli Python dasturlash",
    },
    {
        "code": "A079",
        "title": "Satrni katta harfga o'tkazish",
        "description": (
            "Satr berilgan. Barcha harflarni katta harfga (uppercase) o'tkazib chiqaring.\n\n"
            "Kirish: 'salom dunyo'"
        ),
        "input_format": "Bitta qatorda satr.",
        "output_format": "Katta harfli satr.",
        "constraints": "1 ≤ uzunlik ≤ 10^5",
        "examples": [
            {"input": "hello world", "output": "HELLO WORLD"},
            {"input": "salom dunyo", "output": "SALOM DUNYO"},
        ],
        "difficulty": "easy",
        "category": "Satr",
        "correct_answer": "SALOM DUNYO",
    },
    {
        "code": "A080",
        "title": "Har bir so'zning bosh harfini katta qilish",
        "description": (
            "Satr berilgan. Har bir so'zning birinchi harfini katta qilib (title case) chiqaring.\n\n"
            "Kirish: 'men python dasturlash tilini o'rganmoqdaman'"
        ),
        "input_format": "Bitta qatorda satr.",
        "output_format": "Title case ko'rinishdagi satr.",
        "constraints": "1 ≤ uzunlik ≤ 10^4",
        "examples": [
            {"input": "salom dunyo", "output": "Salom Dunyo"},
            {"input": "men python o'rganmoqdaman", "output": "Men Python O'rganmoqdaman"},
        ],
        "difficulty": "easy",
        "category": "Satr",
        "correct_answer": "Men Python O'rganmoqdaman",
    },

    # ── A081-A100: Algoritmik masalalar ───────────────────────────────────────
    {
        "code": "A081",
        "title": "Ikkilik qidiruv",
        "description": (
            "Saralangan n ta son va qidirilayotgan k berilgan. "
            "Ikkilik qidiruv (binary search) algoritmi yordamida k ning indeksini toping. "
            "Topilmasa -1 chiqaring.\n\n"
            "Kirish: n=8, sonlar: 1 3 5 7 9 11 13 15, k=9"
        ),
        "input_format": "Birinchi qatorda n, ikkinchi qatorda n ta son, uchinchi qatorda k.",
        "output_format": "Bitta qatorda indeks (0 dan boshlab) yoki -1.",
        "constraints": "1 ≤ n ≤ 10^6",
        "examples": [
            {"input": "7\n1 3 5 7 9 11 13\n7", "output": "3"},
            {"input": "8\n1 3 5 7 9 11 13 15\n9", "output": "4"},
        ],
        "difficulty": "hard",
        "category": "Algoritm",
        "correct_answer": "4",
    },
    {
        "code": "A082",
        "title": "Pufakcha saralash (Bubble Sort)",
        "description": (
            "n ta son berilgan. Pufakcha saralash algoritmini yozib, qancha almashtirish "
            "(swap) amalga oshirilganini va saralangan ro'yxatni chiqaring.\n\n"
            "Kirish: n=6, sonlar: 5 3 8 1 9 2"
        ),
        "input_format": "Birinchi qatorda n, ikkinchi qatorda n ta son.",
        "output_format": "Birinchi qatorda swaplar soni, ikkinchi qatorda saralangan ro'yxat.",
        "constraints": "1 ≤ n ≤ 1000",
        "examples": [
            {"input": "4\n4 3 2 1", "output": "6\n1 2 3 4"},
            {"input": "6\n5 3 8 1 9 2", "output": "8\n1 2 3 5 8 9"},
        ],
        "difficulty": "hard",
        "category": "Algoritm",
        "correct_answer": "8\n1 2 3 5 8 9",
    },
    {
        "code": "A083",
        "title": "Rekursiv faktorial",
        "description": (
            "n berilgan. Rekursiya yordamida n! ni hisoblang.\n\n"
            "Kirish: n = 12"
        ),
        "input_format": "Bitta qatorda n.",
        "output_format": "Bitta qatorda n!",
        "constraints": "0 ≤ n ≤ 20",
        "examples": [
            {"input": "6", "output": "720"},
            {"input": "12", "output": "479001600"},
        ],
        "difficulty": "hard",
        "category": "Algoritm",
        "correct_answer": "479001600",
    },
    {
        "code": "A084",
        "title": "Rekursiv Fibonachchi",
        "description": (
            "n berilgan. Rekursiya yordamida Fibonachchi ketma-ketligining n-hadini toping.\n"
            "F(1)=1, F(2)=1, F(n)=F(n-1)+F(n-2).\n\n"
            "Kirish: n = 12"
        ),
        "input_format": "Bitta qatorda n.",
        "output_format": "Bitta qatorda F(n).",
        "constraints": "1 ≤ n ≤ 35",
        "examples": [
            {"input": "8", "output": "21"},
            {"input": "12", "output": "144"},
        ],
        "difficulty": "hard",
        "category": "Algoritm",
        "correct_answer": "144",
    },
    {
        "code": "A085",
        "title": "Hanoi minorasi",
        "description": (
            "n ta disk bilan Hanoi minorasini hal qilish uchun minimal harakatlar soni: 2^n − 1.\n\n"
            "Kirish: n = 8"
        ),
        "input_format": "Bitta qatorda n.",
        "output_format": "Bitta qatorda minimal harakatlar soni.",
        "constraints": "1 ≤ n ≤ 30",
        "examples": [
            {"input": "3", "output": "7"},
            {"input": "8", "output": "255"},
        ],
        "difficulty": "hard",
        "category": "Algoritm",
        "correct_answer": "255",
    },
    {
        "code": "A086",
        "title": "Tub ko'paytuvchilarga ajratish",
        "description": (
            "n berilgan. Uni tub ko'paytuvchilarga ajratib, o'sish tartibida chiqaring.\n\n"
            "Kirish: n = 360"
        ),
        "input_format": "Bitta qatorda n.",
        "output_format": "Tub ko'paytuvchilar bo'sh joy bilan (o'sish tartibida).",
        "constraints": "2 ≤ n ≤ 10^9",
        "examples": [
            {"input": "12", "output": "2 2 3"},
            {"input": "360", "output": "2 2 2 3 3 5"},
        ],
        "difficulty": "hard",
        "category": "Algoritm",
        "correct_answer": "2 2 2 3 3 5",
    },
    {
        "code": "A087",
        "title": "Eng yaqin sonni topish",
        "description": (
            "Saralangan n ta son va target t berilgan. t ga eng yaqin sonni toping. "
            "Teng masofada bo'lsa kichigini chiqaring.\n\n"
            "Kirish: n=6, sonlar: 1 3 5 7 9 11, t=6"
        ),
        "input_format": "Birinchi qatorda n, ikkinchi qatorda n ta son, uchinchi qatorda t.",
        "output_format": "Bitta qatorda eng yaqin son.",
        "constraints": "1 ≤ n ≤ 10^5",
        "examples": [
            {"input": "5\n1 3 5 7 9\n6", "output": "5"},
            {"input": "6\n1 3 5 7 9 11\n6", "output": "5"},
        ],
        "difficulty": "hard",
        "category": "Algoritm",
        "correct_answer": "5",
    },
    {
        "code": "A088",
        "title": "Ikkinchi eng katta son",
        "description": (
            "n ta son berilgan. Eng katta va ikkinchi eng katta sonni toping "
            "(noyob bo'lmasa ham).\n\n"
            "Kirish: n=7, sonlar: 3 1 4 1 5 9 2"
        ),
        "input_format": "Birinchi qatorda n, ikkinchi qatorda n ta son.",
        "output_format": "Birinchi qatorda eng katta, ikkinchi qatorda ikkinchi eng katta.",
        "constraints": "2 ≤ n ≤ 10^5",
        "examples": [
            {"input": "5\n5 3 8 1 9", "output": "9\n8"},
            {"input": "7\n3 1 4 1 5 9 2", "output": "9\n5"},
        ],
        "difficulty": "hard",
        "category": "Algoritm",
        "correct_answer": "9\n5",
    },
    {
        "code": "A089",
        "title": "Eng kichik ikki son",
        "description": (
            "n ta son berilgan. Eng kichik va ikkinchi eng kichik noyob sonlarni toping.\n\n"
            "Kirish: n=7, sonlar: 3 1 4 1 5 9 2"
        ),
        "input_format": "Birinchi qatorda n, ikkinchi qatorda n ta son.",
        "output_format": "Birinchi qatorda eng kichik, ikkinchi qatorda ikkinchi eng kichik (noyob).",
        "constraints": "2 ≤ n ≤ 10^5",
        "examples": [
            {"input": "5\n5 3 8 1 9", "output": "1\n3"},
            {"input": "7\n3 1 4 1 5 9 2", "output": "1\n2"},
        ],
        "difficulty": "hard",
        "category": "Algoritm",
        "correct_answer": "1\n2",
    },
    {
        "code": "A090",
        "title": "Yig'indisi n ga teng juftliklar",
        "description": (
            "n ta son va target t berilgan. Yig'indisi t ga teng bo'lgan juftliklar sonini toping "
            "(har bir juftlik bir marta hisoblansin, indekslari turlicha bo'lsin).\n\n"
            "Kirish: n=6, sonlar: 1 2 3 4 5 6, t=7"
        ),
        "input_format": "Birinchi qatorda n, ikkinchi qatorda n ta son, uchinchi qatorda t.",
        "output_format": "Bitta qatorda juftliklar soni.",
        "constraints": "2 ≤ n ≤ 10^4",
        "examples": [
            {"input": "5\n1 2 3 4 5\n5", "output": "2", "explanation": "(1,4),(2,3)"},
            {"input": "6\n1 2 3 4 5 6\n7", "output": "3", "explanation": "(1,6),(2,5),(3,4)"},
        ],
        "difficulty": "hard",
        "category": "Algoritm",
        "correct_answer": "3",
    },
    {
        "code": "A091",
        "title": "Matritsa transponirlash",
        "description": (
            "n×m matritsa berilgan. Uning transponigini (m×n) chiqaring.\n\n"
            "Kirish: 3×3 matritsa [[1,2,3],[4,5,6],[7,8,9]]"
        ),
        "input_format": "Birinchi qatorda n va m. Keyin n qatorda m ta son.",
        "output_format": "Transponlangan matritsa.",
        "constraints": "1 ≤ n, m ≤ 100",
        "examples": [
            {"input": "2 3\n1 2 3\n4 5 6", "output": "1 4\n2 5\n3 6"},
            {"input": "3 3\n1 2 3\n4 5 6\n7 8 9", "output": "1 4 7\n2 5 8\n3 6 9"},
        ],
        "difficulty": "hard",
        "category": "Algoritm",
        "correct_answer": "1 4 7\n2 5 8\n3 6 9",
    },
    {
        "code": "A092",
        "title": "Matritsa ko'paytirish",
        "description": (
            "2 ta kvadrat n×n matritsa berilgan. Ularning ko'paytmasini hisoblang.\n\n"
            "Kirish: n=2, A=[[1,2],[3,4]], B=[[5,6],[7,8]]"
        ),
        "input_format": "Birinchi qatorda n. Keyin n qatorda A matritsasi, keyin n qatorda B matritsasi.",
        "output_format": "Ko'paytma matritsa (n×n).",
        "constraints": "1 ≤ n ≤ 50",
        "examples": [
            {"input": "2\n1 2\n3 4\n5 6\n7 8", "output": "19 22\n43 50"},
        ],
        "difficulty": "hard",
        "category": "Algoritm",
        "correct_answer": "19 22\n43 50",
    },
    {
        "code": "A093",
        "title": "Matritsa determinanti",
        "description": (
            "2×2 yoki 3×3 matritsa berilgan. Determinantini hisoblang.\n\n"
            "Kirish: 3×3, [[1,2,3],[4,5,6],[7,8,10]]"
        ),
        "input_format": "Birinchi qatorda n (2 yoki 3). Keyin n qatorda matritsa.",
        "output_format": "Bitta qatorda determinant.",
        "constraints": "n ∈ {2, 3}",
        "examples": [
            {"input": "2\n1 2\n3 4", "output": "-2"},
            {"input": "3\n1 2 3\n4 5 6\n7 8 10", "output": "-3"},
        ],
        "difficulty": "hard",
        "category": "Algoritm",
        "correct_answer": "-3",
    },
    {
        "code": "A094",
        "title": "Eng uzun umumiy qism satr (LCS)",
        "description": (
            "Ikkita satr berilgan. Ularning eng uzun umumiy qism satrining uzunligini toping.\n\n"
            "Kirish: 'ABCBDAB' va 'BDCABA'"
        ),
        "input_format": "Birinchi qatorda birinchi satr, ikkinchi qatorda ikkinchi satr.",
        "output_format": "Bitta qatorda LCS uzunligi.",
        "constraints": "1 ≤ har bir satr uzunligi ≤ 1000",
        "examples": [
            {"input": "AGGTAB\nGXTXAYB", "output": "4", "explanation": "GTAB"},
            {"input": "ABCBDAB\nBDCABA", "output": "4", "explanation": "BCBA yoki BDAB"},
        ],
        "difficulty": "hard",
        "category": "Algoritm",
        "correct_answer": "4",
    },
    {
        "code": "A095",
        "title": "Sonni rim raqamiga o'tkazish",
        "description": (
            "Butun son n berilgan. Uni rim raqamiga o'tkazing.\n\n"
            "Kirish: n = 2024"
        ),
        "input_format": "Bitta qatorda n.",
        "output_format": "Rim raqami.",
        "constraints": "1 ≤ n ≤ 3999",
        "examples": [
            {"input": "14", "output": "XIV"},
            {"input": "2024", "output": "MMXXIV"},
        ],
        "difficulty": "hard",
        "category": "Algoritm",
        "correct_answer": "MMXXIV",
    },
    {
        "code": "A096",
        "title": "Rim raqamini songa o'tkazish",
        "description": (
            "Rim raqami berilgan. Uni oddiy butun songa o'tkazing.\n\n"
            "Kirish: 'MCMXCIX'"
        ),
        "input_format": "Bitta qatorda rim raqami.",
        "output_format": "Bitta qatorda son.",
        "constraints": "Rim raqami 1 dan 3999 gacha.",
        "examples": [
            {"input": "XIV", "output": "14"},
            {"input": "MCMXCIX", "output": "1999"},
        ],
        "difficulty": "hard",
        "category": "Algoritm",
        "correct_answer": "1999",
    },
    {
        "code": "A097",
        "title": "Satrni siqish (Run-Length Encoding)",
        "description": (
            "Satr berilgan. Har bir belgini ketma-ket takrorlanish soni bilan siqing.\n"
            "Masalan: 'aaabbc' → 'a3b2c1'\n\n"
            "Kirish: 'aaabbbbcccd'"
        ),
        "input_format": "Bitta qatorda satr (faqat kichik harflar).",
        "output_format": "Siqilgan satr.",
        "constraints": "1 ≤ uzunlik ≤ 10^4",
        "examples": [
            {"input": "aaabbc", "output": "a3b2c1"},
            {"input": "aaabbbbcccd", "output": "a3b4c3d1"},
        ],
        "difficulty": "hard",
        "category": "Algoritm",
        "correct_answer": "a3b4c3d1",
    },
    {
        "code": "A098",
        "title": "Satrni ochish (Run-Length Decoding)",
        "description": (
            "Siqilgan satr berilgan. Uni asl holiga qaytaring.\n"
            "Masalan: 'a3b2c1' → 'aaabbc'\n\n"
            "Kirish: 'a3b4c3d1'"
        ),
        "input_format": "Bitta qatorda siqilgan satr.",
        "output_format": "Asl satr.",
        "constraints": "1 ≤ uzunlik ≤ 10^4",
        "examples": [
            {"input": "a3b2c1", "output": "aaabbc"},
            {"input": "a3b4c3d1", "output": "aaabbbbcccd"},
        ],
        "difficulty": "hard",
        "category": "Algoritm",
        "correct_answer": "aaabbbbcccd",
    },
    {
        "code": "A099",
        "title": "Anagramma tekshirish",
        "description": (
            "Ikkita satr berilgan. Ular anagrammami (bir xil belgilar, boshqa tartibda)? "
            "Katta-kichiklikka e'tibor bermang.\n\n"
            "Kirish: 'Triangle' va 'Integral'"
        ),
        "input_format": "Birinchi qatorda birinchi satr, ikkinchi qatorda ikkinchi satr.",
        "output_format": "'YES' yoki 'NO'.",
        "constraints": "1 ≤ uzunlik ≤ 10^4",
        "examples": [
            {"input": "listen\nsilent", "output": "YES"},
            {"input": "Triangle\nIntegral", "output": "YES"},
            {"input": "hello\nworld", "output": "NO"},
        ],
        "difficulty": "hard",
        "category": "Algoritm",
        "correct_answer": "YES",
    },
    {
        "code": "A100",
        "title": "Qavslar muvozanati (to'liq)",
        "description": (
            "Satr berilgan (faqat '(', ')', '[', ']', '{', '}' belgileridan iborat). "
            "Stek yordamida qavslar muvozanatli bo'lsa 'Ha', aks holda 'Yo'q' chiqaring.\n\n"
            "Kirish: '([{}])'"
        ),
        "input_format": "Bitta qatorda satr.",
        "output_format": "'Ha' yoki 'Yo'q'.",
        "constraints": "1 ≤ uzunlik ≤ 10^5",
        "examples": [
            {"input": "([{}])", "output": "Ha"},
            {"input": "{[()]}", "output": "Ha"},
            {"input": "([)]", "output": "Yo'q"},
            {"input": "((())", "output": "Yo'q"},
        ],
        "difficulty": "hard",
        "category": "Algoritm",
        "correct_answer": "Ha",
    },
]


def run():
    app = create_app()
    with app.app_context():
        added = 0
        updated = 0
        for p_data in PROBLEMS:
            examples_json = json.dumps(p_data.get("examples", []), ensure_ascii=False)
            existing = ArenaProblem.query.filter_by(code=p_data["code"]).first()
            if existing:
                # Update fields (idempotent)
                existing.title          = p_data["title"]
                existing.description    = p_data["description"]
                existing.input_format   = p_data.get("input_format", "")
                existing.output_format  = p_data.get("output_format", "")
                existing.constraints    = p_data.get("constraints", "")
                existing.examples       = examples_json
                existing.difficulty     = p_data["difficulty"]
                existing.category       = p_data["category"]
                existing.correct_answer = p_data["correct_answer"]
                updated += 1
            else:
                prob = ArenaProblem(
                    code           = p_data["code"],
                    title          = p_data["title"],
                    description    = p_data["description"],
                    input_format   = p_data.get("input_format", ""),
                    output_format  = p_data.get("output_format", ""),
                    constraints    = p_data.get("constraints", ""),
                    examples       = examples_json,
                    difficulty     = p_data["difficulty"],
                    category       = p_data["category"],
                    correct_answer = p_data["correct_answer"],
                    is_active      = True,
                )
                db.session.add(prob)
                added += 1

        db.session.commit()
        print(f"Tayyor! Qo'shildi: {added}, Yangilandi: {updated}, Jami: {len(PROBLEMS)}")


if __name__ == "__main__":
    run()
