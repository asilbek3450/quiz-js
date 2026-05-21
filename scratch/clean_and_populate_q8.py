import sys
import os
import random

sys.path.insert(0, '/Users/asilbek/Desktop/AI-Projects/quiz-js')
os.environ.setdefault('FLASK_ENV', 'development')

from app import create_app
from models import db, Question, Subject

def main():
    app = create_app()
    with app.app_context():
        # 1. Fetch Python subject
        python_sub = Subject.query.filter_by(name='Python').first()
        if not python_sub:
            print("Error: Python subject not found!")
            return
        python_sub_id = python_sub.id

        # 2. Reset (delete all) existing Grade 8 Q4 questions to have a clean, reproducible state
        print("Resetting all existing Grade 8 Q4 questions...")
        db.session.query(Question).filter_by(grade=8, quarter=4).delete()
        db.session.commit()
        print("Existing Grade 8 Q4 questions deleted.")

        # Keywords for out-of-syllabus (complex) topics
        out_of_syllabus_keywords = [
            "open(", ".read(", "readline", "file", "fayl",  # File handling
            "try:", "except ", "finally:", "error", "xatolik", "exception",  # Exception handling
            "stack", "lifo", "queue", "navbat", "fifo", "stek", "steyk",  # Stacks/Queues/LIFO/FIFO
            "pop(", "pop()", "extend(", "zip(", "enumerate(", "is va =="  # Advanced methods
        ]

        # 3. Clone high-quality questions from previous quarters (Q1 & Q2) of Grade 8
        # But filter out any that contain out-of-syllabus keywords!
        prev_questions = Question.query.filter(
            Question.grade == 8,
            Question.quarter.in_([1, 2]),
            Question.subject_id == python_sub_id
        ).all()
        
        print(f"Found {len(prev_questions)} candidate questions from Quarters 1 & 2.")
        
        clean_candidates = []
        for q in prev_questions:
            text = (q.question_text or "").lower()
            if not any(kw in text for kw in out_of_syllabus_keywords):
                clean_candidates.append(q)
                
        print(f"Filtered candidate questions from Quarters 1 & 2 to {len(clean_candidates)} clean syllabus-compliant ones.")
        
        # Shuffle and select up to 150 questions
        random.seed(42)
        random.shuffle(clean_candidates)
        clone_limit = min(150, len(clean_candidates))
        cloned_count = 0

        for q in clean_candidates[:clone_limit]:
            cloned_q = Question(
                subject_id=q.subject_id,
                grade=8,
                quarter=4,
                difficulty=q.difficulty,
                lesson=q.lesson,
                question_text=q.question_text,
                question_text_ru=q.question_text_ru,
                question_text_en=q.question_text_en,
                option_a=q.option_a,
                option_a_ru=q.option_a_ru,
                option_a_en=q.option_a_en,
                option_b=q.option_b,
                option_b_ru=q.option_b_ru,
                option_b_en=q.option_b_en,
                option_c=q.option_c,
                option_c_ru=q.option_c_ru,
                option_c_en=q.option_c_en,
                option_d=q.option_d,
                option_d_ru=q.option_d_ru,
                option_d_en=q.option_d_en,
                correct_answer=q.correct_answer,
                creator_id=q.creator_id
            )
            db.session.add(cloned_q)
            cloned_count += 1
        
        db.session.commit()
        print(f"Successfully cloned {cloned_count} clean questions from Quarters 1 & 2.")

        # 4. Insert 50 brand-new, high-quality, high-standard syllabus questions
        new_questions_data = [
            # --- Funksiyalar (Functions) ---
            {
                "text": "Quyidagi kod bajarilganda ekranga nima chiqadi?\n\n```python\ndef hisobla(x, y=3):\n    return x * y\nprint(hisobla(5) + hisobla(4, 2))\n```",
                "a": "23", "b": "32", "c": "25", "d": "Xatolik yuz beradi", "correct": "A"
            },
            {
                "text": "Quyidagi funksiya chaqirilganda natija nima bo'ladi?\n\n```python\ndef salom(ism):\n    return f'Salom, {ism}!'\nprint(salom('Ali'))\n```",
                "a": "Salom, Ali!", "b": "Salom, ism!", "c": "None", "d": "Xatolik yuz beradi", "correct": "A"
            },
            {
                "text": "Funksiyada `return` kalit so'zining asosiy vazifasi nima?",
                "a": "Funksiya bajarilishini tugatib, natijani chaqirilgan joyga qaytarish",
                "b": "Funksiyani yaratish va e'lon qilish",
                "c": "Ekranga ma'lumotlarni chop etish",
                "d": "O'zgaruvchilarni global darajaga o'tkazish",
                "correct": "A"
            },
            {
                "text": "Quyidagi kod bajarilganda natija nima bo'ladi?\n\n```python\ndef f(a, b):\n    return a - b\nprint(f(b=10, a=25))\n```",
                "a": "15", "b": "-15", "c": "Xatolik yuz beradi", "d": "None", "correct": "A"
            },
            {
                "text": "Pythonda funksiya yaratish uchun qaysi kalit so'z ishlatiladi?",
                "a": "def", "b": "func", "c": "function", "d": "define", "correct": "A"
            },
            {
                "text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\ndef f():\n    pass\nprint(f())\n```",
                "a": "None", "b": "pass", "c": "0", "d": "Xatolik yuz beradi", "correct": "A"
            },
            {
                "text": "Funksiyaga uzatiladigan qiymat nima deb ataladi?",
                "a": "Parametr (Argument)", "b": "O'zgaruvchi", "c": "Modul", "d": "Lug'at", "correct": "A"
            },
            {
                "text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\ndef daraja(asos, ko‘rsatkich=2):\n    return asos ** ko‘rsatkich\nprint(daraja(3, 3) - daraja(4))\n```",
                "a": "11", "b": "23", "c": "9", "d": "Xatolik yuz beradi", "correct": "A"
            },
            # --- Scope (O'zgaruvchilar doirasi) ---
            {
                "text": "Quyidagi kod bajarilganda ekranga nima chiqadi?\n\n```python\nx = 15\ndef f():\n    global x\n    x = 30\nf()\nprint(x)\n```",
                "a": "30", "b": "15", "c": "None", "d": "Xatolik yuz beradi", "correct": "A"
            },
            {
                "text": "Quyidagi kod bajarilganda ekranga nima chiqadi?\n\n```python\nx = 10\ndef f():\n    x = 5\nf()\nprint(x)\n```",
                "a": "10", "b": "5", "c": "None", "d": "Xatolik yuz beradi", "correct": "A"
            },
            {
                "text": "Funksiya ichida yaratilgan va faqat funksiya doirasida ko'rinadigan o'zgaruvchi qanday o'zgaruvchi deyiladi?",
                "a": "Mahalliy (Local) o'zgaruvchi", "b": "Umumiy (Global) o'zgaruvchi", "c": "Tizimli o'zgaruvchi", "d": "Statik o'zgaruvchi", "correct": "A"
            },
            {
                "text": "Funksiya tashqarisida e'lon qilingan va butun dastur doirasida foydalanish mumkin bo'lgan o'zgaruvchi qanday nomlanadi?",
                "a": "Umumiy (Global) o'zgaruvchi", "b": "Mahalliy (Local) o'zgaruvchi", "c": "Himoyalangan o'zgaruvchi", "d": "Maxfiy o'zgaruvchi", "correct": "A"
            },
            {
                "text": "Funksiya ichida global o'zgaruvchini o'zgartirish yoki unga qiymat berish uchun qaysi kalit so'zdan foydalaniladi?",
                "a": "global", "b": "local", "c": "def", "d": "return", "correct": "A"
            },
            {
                "text": "Quyidagi kod bajarilganda ekranga nima chiqadi?\n\n```python\na = 7\ndef f():\n    global a\n    a += 3\nf()\nprint(a)\n```",
                "a": "10", "b": "7", "c": "3", "d": "Xatolik yuz beradi", "correct": "A"
            },
            # --- Rekursiya (Recursion) ---
            {
                "text": "Funksiyaning o'z-o'zini chaqirishi nima deb ataladi?",
                "a": "Rekursiya", "b": "Sikl", "c": "Iteratsiya", "d": "Inkapsulyatsiya", "correct": "A"
            },
            {
                "text": "Rekursiya cheksiz bo'lib qolmasligi va ishlashini to'xtatishi uchun nima bo'lishi shart?",
                "a": "Asosiy holat yoki shart (Base case)", "b": "Global o'zgaruvchi", "c": "for sikli", "d": "Lug'at to'plami", "correct": "A"
            },
            {
                "text": "Quyidagi rekursiv funksiya `f(5)` chaqirilganda nima natija beradi?\n\n```python\ndef f(n):\n    if n <= 1:\n        return 1\n    return n * f(n-1)\n```",
                "a": "120", "b": "24", "c": "720", "d": "15", "correct": "A"
            },
            {
                "text": "Quyidagi rekursiv funksiya `f(4)` chaqirilganda ekranga nima chiqadi?\n\n```python\ndef f(n):\n    if n <= 1:\n        return 1\n    return n + f(n-1)\n```",
                "a": "10", "b": "24", "c": "6", "d": "Xatolik yuz beradi", "correct": "A"
            },
            {
                "text": "Rekursiya asosidagi 'Faktorial' deganda nimani tushunasiz?",
                "a": "1 dan n gacha bo'lgan natural sonlarning ko'paytmasi",
                "b": "1 dan n gacha bo'lgan sonlarning yig'indisi",
                "c": "Sonning kvadrat ildizi",
                "d": "Sonning darajaga oshirilgan qiymati",
                "correct": "A"
            },
            {
                "text": "Cheksiz rekursiya yuz berganda Pythonda qanday xatolik yuzaga keladi?",
                "a": "RecursionError (Maksimal chaqiruv chuqurligidan oshib ketish)",
                "b": "TypeError",
                "c": "ValueError",
                "d": "ZeroDivisionError",
                "correct": "A"
            },
            # --- Lug'atlar (Dictionaries) ---
            {
                "text": "Lug'atlarda (Dictionaries) ma'lumotlar qanday tuzilishda saqlanadi?",
                "a": "Kalit va qiymat (key-value) juftligi ko'rinishida",
                "b": "Faqat takrorlanmas qiymatlar ro'yxati ko'rinishida",
                "c": "Tartiblangan massiv ko'rinishida",
                "d": "Matnli fayl ko'rinishida", "correct": "A"
            },
            {
                "text": "Quyidagi kod bajarilganda ekranga nima chiqadi?\n\n```python\nd = {'olma': 12000, 'anor': 25000}\nprint(d.get('uzum', 10000))\n```",
                "a": "10000", "b": "None", "c": "Xatolik yuz beradi", "d": "12000", "correct": "A"
            },
            {
                "text": "Lug'atdagi barcha kalitlar ro'yxatini olish uchun qaysi metod ishlatiladi?",
                "a": "keys()", "b": "values()", "c": "items()", "d": "get()", "correct": "A"
            },
            {
                "text": "Lug'atdagi barcha qiymatlar ro'yxatini olish uchun qaysi metod ishlatiladi?",
                "a": "values()", "b": "keys()", "c": "items()", "d": "list()", "correct": "A"
            },
            {
                "text": "Lug'atdan ma'lum bir kalit va unga mos qiymatni butunlay o'chirish uchun qaysi buyruq ishlatiladi?",
                "a": "del", "b": "remove", "c": "discard", "d": "clear", "correct": "A"
            },
            {
                "text": "Quyidagi kod bajarilganda ekranga nima chiqadi?\n\n```python\nd = {'a': 1, 'b': 2}\nd['c'] = 3\nprint(len(d))\n```",
                "a": "3", "b": "2", "c": "Xatolik yuz beradi", "d": "None", "correct": "A"
            },
            {
                "text": "Quyidagi kod bajarilganda ekranga nima chiqadi?\n\n```python\nd = {'ism': 'Sardor', 'yosh': 14}\nprint('yosh' in d)\n```",
                "a": "True", "b": "False", "c": "14", "d": "Xatolik yuz beradi", "correct": "A"
            },
            {
                "text": "Lug'at elementlarini kalit-qiymat juftligi holatida olish uchun qaysi metoddan foydalaniladi?",
                "a": "items()", "b": "keys()", "c": "values()", "d": "get()", "correct": "A"
            },
            # --- To'plamlar (Sets) ---
            {
                "text": "Pythonda to'plamlar (Set) uchun qaysi ta'rif eng to'g'ri hisoblanadi?",
                "a": "Takrorlanmas (noyob) va tartibsiz elementlar to'plami",
                "b": "Tartiblangan va o'zgartirib bo'lmaydigan ro'yxat",
                "c": "Kalit va qiymatlardan iborat tuzilma",
                "d": "Faqat sonlardan iborat massiv", "correct": "A"
            },
            {
                "text": "To'plamga (Set) yangi element qo'shish uchun qaysi metod ishlatiladi?",
                "a": "add()", "b": "append()", "c": "insert()", "d": "extend()", "correct": "A"
            },
            {
                "text": "Quyidagi kod bajarilganda ekranga nima chiqadi?\n\n```python\na = {1, 2, 3, 3, 4}\nprint(len(a))\n```",
                "a": "4", "b": "5", "c": "Xatolik yuz beradi", "d": "3", "correct": "A"
            },
            {
                "text": "Ikki to'plamning birlashmasini (hamma elementlarni birlashtirish) qaysi belgi orqali yozish mumkin?",
                "a": "| (Set union)", "b": "& (Set intersection)", "c": "-", "d": "^", "correct": "A"
            },
            {
                "text": "Ikki to'plamning kesishmasini (faqat ikkala to'plamda ham bor elementlarni olish) qaysi operator yordamida aniqlaymiz?",
                "a": "& (Set intersection)", "b": "| (Set union)", "c": "+", "d": "*", "correct": "A"
            },
            {
                "text": "Quyidagi to'plamlar kesishmasining natijasi nima bo'ladi?\n\n```python\na = {10, 20, 30}\nb = {20, 30, 40}\nprint(sorted(a & b))\n```",
                "a": "[20, 30]", "b": "[10, 20, 30, 40]", "c": "[10, 40]", "d": "[]", "correct": "A"
            },
            {
                "text": "Quyidagi kod bajarilganda ekranga nima chiqadi?\n\n```python\na = {1, 2}\nb = {3, 4}\nprint(a.isdisjoint(b))\n```",
                "a": "True", "b": "False", "c": "None", "d": "Xatolik yuz beradi", "correct": "A"
            },
            # --- Mantiqiy amallar (any, all, %, comparisons) ---
            {
                "text": "Pythonda `any()` funksiyasi qanday holatda True qiymatini qaytaradi?",
                "a": "To'plamda kamida bitta element True bo'lsa",
                "b": "To'plamda hamma element True bo'lsa",
                "c": "To'plam bo'sh bo'lganda",
                "d": "Faqat birinchi element True bo'lganda", "correct": "A"
            },
            {
                "text": "Pythonda `all()` funksiyasi qanday holatda True qiymatini qaytaradi?",
                "a": "To'plamdagi barcha elementlar True bo'lsa",
                "b": "To'plamda kamida bitta element True bo'lsa",
                "c": "To'plam faqat bitta elementdan iborat bo'lsa",
                "d": "To'plam bo'sh bo'lganda", "correct": "A"
            },
            {
                "text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\nprint(all([True, 1, 'salom', False]))\n```",
                "a": "False", "b": "True", "c": "None", "d": "Xatolik yuz beradi", "correct": "A"
            },
            {
                "text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\nprint(any([0, '', [], 5]))\n```",
                "a": "True", "b": "False", "c": "None", "d": "Xatolik yuz beradi", "correct": "A"
            },
            {
                "text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\nprint(17 % 5)\n```",
                "a": "2", "b": "3", "c": "1", "d": "Xatolik yuz beradi", "correct": "A"
            },
            {
                "text": "Quyidagi ro'yxatlardan qaysi biri o'zgartirilishi mumkin (mutable)?",
                "a": "List (Ro'yxat)", "b": "Tuple (Kortej)", "c": "String (Satr)", "d": "Set (To'plam)", "correct": "A"
            },
            {
                "text": "Quyidagi ro'yxatlardan qaysi birining elementlarini yaratilgandan keyin mutlaqo o'zgartirib bo'lmaydi (immutable)?",
                "a": "Tuple (Kortej)", "b": "List (Ro'yxat)", "c": "Set (To'plam)", "d": "Lug'at (Dict)", "correct": "A"
            },
            {
                "text": "To'plamdan ma'lum bir elementni o'chirish uchun qaysi metod ishlatiladi?",
                "a": "discard()", "b": "add()", "c": "append()", "d": "pop()", "correct": "A"
            },
            {
                "text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\na = {1, 2}\nb = {1, 2, 3}\nprint(a.issubset(b))\n```",
                "a": "True", "b": "False", "c": "None", "d": "Xatolik yuz beradi", "correct": "A"
            },
            {
                "text": "Quyidagi kod bajarilganda ekranga nima chiqadi?\n\n```python\ns = {10, 20}\ns.clear()\nprint(len(s))\n```",
                "a": "0", "b": "2", "c": "None", "d": "Xatolik yuz beradi", "correct": "A"
            },
            {
                "text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\nprint(sorted(list({1, 3, 2} | {3, 4})))\n```",
                "a": "[1, 2, 3, 4]", "b": "[1, 2, 3, 3, 4]", "c": "[1, 2, 4]", "d": "Xatolik yuz beradi", "correct": "A"
            },
            {
                "text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\nprint(5 in {1, 2, 3, 4})\n```",
                "a": "False", "b": "True", "c": "None", "d": "Xatolik yuz beradi", "correct": "A"
            },
            {
                "text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\ndef is_prime(n):\n    if n < 2: return False\n    for i in range(2, int(n**0.5)+1):\n        if n % i == 0: return False\n    return True\nprint(is_prime(7))\n```",
                "a": "True", "b": "False", "c": "None", "d": "Xatolik yuz beradi", "correct": "A"
            },
            {
                "text": "Lug'atning barcha elementlarini butunlay o'chirib yuboruvchi metod qaysi?",
                "a": "clear()", "b": "pop()", "c": "del", "d": "discard()", "correct": "A"
            },
            {
                "text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\ndef kopaytir(*args):\n    r = 1\n    for x in args: r *= x\n    return r\nprint(kopaytir(2, 3, 4))\n```",
                "a": "24", "b": "9", "c": "12", "d": "Xatolik yuz beradi", "correct": "A"
            }
        ]

        inserted_count = 0
        for q_data in new_questions_data:
            new_q = Question(
                subject_id=python_sub_id,
                grade=8,
                quarter=4,
                difficulty=2,  # Medium
                lesson=1,
                question_text=q_data["text"],
                question_text_ru=q_data["text"], # Simple default
                question_text_en=q_data["text"],
                option_a=q_data["a"],
                option_a_ru=q_data["a"],
                option_a_en=q_data["a"],
                option_b=q_data["b"],
                option_b_ru=q_data["b"],
                option_b_en=q_data["b"],
                option_c=q_data["c"],
                option_c_ru=q_data["c"],
                option_c_en=q_data["c"],
                option_d=q_data["d"],
                option_d_ru=q_data["d"],
                option_d_en=q_data["d"],
                correct_answer=q_data["correct"],
                creator_id=None
            )
            db.session.add(new_q)
            inserted_count += 1
            
        db.session.commit()
        print(f"Successfully inserted {inserted_count} new high-quality questions on core 4th quarter topics.")

        # 5. Output final count
        final_count = Question.query.filter_by(grade=8, quarter=4).count()
        print(f"\nFinal Grade 8 Q4 questions count in database: {final_count}")

if __name__ == '__main__':
    main()
