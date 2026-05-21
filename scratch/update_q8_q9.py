import sqlite3
import os

DB_PATH = 'instance/test_platform.db'

def update_database():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    print("=== Step 1: Grade 8 Q4 Updates ===")
    
    # 1. Identify Grade 8 Q4 questions to delete
    c.execute('SELECT id, question_text FROM question WHERE grade=8 AND quarter=4')
    g8_rows = c.fetchall()
    
    g8_to_delete = []
    for qid, qtext in g8_rows:
        qtext_lower = qtext.lower()
        if 'any(' in qtext_lower or 'all(' in qtext_lower or 'any()' in qtext_lower or 'all()' in qtext_lower:
            g8_to_delete.append(qid)
        elif 'any ' in qtext_lower or 'all ' in qtext_lower or 'any’' in qtext_lower or 'all’' in qtext_lower or 'any\'' in qtext_lower or 'all\'' in qtext_lower:
            g8_to_delete.append(qid)
        elif '%' in qtext_lower or 'qoldiq' in qtext_lower or 'modul amali' in qtext_lower:
            g8_to_delete.append(qid)
            
    print(f"Found {len(g8_to_delete)} questions in Grade 8 Q4 to delete.")
    
    # Delete them
    for qid in g8_to_delete:
        c.execute('DELETE FROM question WHERE id=?', (qid,))
    conn.commit()
    print("Deleted Grade 8 Q4 questions successfully.")
    
    # 2. Seed 18 brand-new high-quality questions for Grade 8 Q4
    g8_new_questions = [
        # 1. .upper() string method
        {
            "subject_id": 2, "grade": 8, "quarter": 4, "difficulty": 2, "lesson": 1,
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\ns = 'Informatika'\nprint(s.upper())\n```",
            "option_a": "INFORMATIKA", "option_b": "informatika", "option_c": "Informatika", "option_d": "INFO",
            "correct_answer": "A"
        },
        # 2. .lower() string method
        {
            "subject_id": 2, "grade": 8, "quarter": 4, "difficulty": 2, "lesson": 1,
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\ns = 'PYTHON'\nprint(s.lower())\n```",
            "option_a": "python", "option_b": "PYTHON", "option_c": "Python", "option_d": "py",
            "correct_answer": "A"
        },
        # 3. .strip() string method
        {
            "subject_id": 2, "grade": 8, "quarter": 4, "difficulty": 2, "lesson": 1,
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\ns = '  olma  '\nprint(len(s.strip()))\n```",
            "option_a": "4", "option_b": "8", "option_c": "6", "option_d": "2",
            "correct_answer": "A"
        },
        # 4. .replace() string method
        {
            "subject_id": 2, "grade": 8, "quarter": 4, "difficulty": 2, "lesson": 1,
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\ns = 'koka-kola'\nprint(s.replace('k', 'b'))\n```",
            "option_a": "boba-bola", "option_b": "koka-kola", "option_c": "boba-kola", "option_d": "koka-bola",
            "correct_answer": "A"
        },
        # 5. .append() list method
        {
            "subject_id": 2, "grade": 8, "quarter": 4, "difficulty": 2, "lesson": 2,
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\nL = [10, 20]\nL.append(30)\nprint(L)\n```",
            "option_a": "[10, 20, 30]", "option_b": "[30, 10, 20]", "option_c": "[10, 20]", "option_d": "[30]",
            "correct_answer": "A"
        },
        # 6. .pop() list method
        {
            "subject_id": 2, "grade": 8, "quarter": 4, "difficulty": 2, "lesson": 2,
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\nL = [5, 15, 25]\nqiymat = L.pop()\nprint(qiymat)\n```",
            "option_a": "25", "option_b": "5", "option_c": "15", "option_d": "[5, 15]",
            "correct_answer": "A"
        },
        # 7. .pop(index) list method
        {
            "subject_id": 2, "grade": 8, "quarter": 4, "difficulty": 2, "lesson": 2,
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\nL = [1, 2, 3, 4]\nL.pop(1)\nprint(L)\n```",
            "option_a": "[1, 3, 4]", "option_b": "[2, 3, 4]", "option_c": "[1, 2, 4]", "option_d": "[1, 2, 3]",
            "correct_answer": "A"
        },
        # 8. .sort() list method
        {
            "subject_id": 2, "grade": 8, "quarter": 4, "difficulty": 2, "lesson": 2,
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\nL = [18, 5, 12]\nL.sort()\nprint(L)\n```",
            "option_a": "[5, 12, 18]", "option_b": "[18, 12, 5]", "option_c": "[18, 5, 12]", "option_d": "[5, 18, 12]",
            "correct_answer": "A"
        },
        # 9. .reverse() list method
        {
            "subject_id": 2, "grade": 8, "quarter": 4, "difficulty": 2, "lesson": 2,
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\nL = [3, 6, 9]\nL.reverse()\nprint(L)\n```",
            "option_a": "[9, 6, 3]", "option_b": "[3, 6, 9]", "option_c": "[6, 9, 3]", "option_d": "[9, 3, 6]",
            "correct_answer": "A"
        },
        # 10. .remove() list method
        {
            "subject_id": 2, "grade": 8, "quarter": 4, "difficulty": 2, "lesson": 2,
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\nL = [2, 4, 2, 6]\nL.remove(2)\nprint(L)\n```",
            "option_a": "[4, 2, 6]", "option_b": "[4, 6]", "option_c": "[2, 4, 6]", "option_d": "[2, 2, 4, 6]",
            "correct_answer": "A"
        },
        # 11. if-else condition
        {
            "subject_id": 2, "grade": 8, "quarter": 4, "difficulty": 2, "lesson": 3,
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\nx = 12\ny = 24\nif x > y:\n    print('Katta')\nelse:\n    print('Kichik')\n```",
            "option_a": "Kichik", "option_b": "Katta", "option_c": "12", "option_d": "Xatolik beradi",
            "correct_answer": "A"
        },
        # 12. Nested if statements
        {
            "subject_id": 2, "grade": 8, "quarter": 4, "difficulty": 2, "lesson": 3,
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\na = 15\nif a > 10:\n    if a < 20:\n        print('A')\n    else:\n        print('B')\nelse:\n    print('C')\n```",
            "option_a": "A", "option_b": "B", "option_c": "C", "option_d": "Hech narsa chop etilmaydi",
            "correct_answer": "A"
        },
        # 13. for loop with range
        {
            "subject_id": 2, "grade": 8, "quarter": 4, "difficulty": 2, "lesson": 4,
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\ns = 0\nfor i in range(1, 5):\n    s += i\nprint(s)\n```",
            "option_a": "10", "option_b": "15", "option_c": "5", "option_d": "6",
            "correct_answer": "A"
        },
        # 14. for loop with break
        {
            "subject_id": 2, "grade": 8, "quarter": 4, "difficulty": 2, "lesson": 4,
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\nfor i in range(1, 10):\n    if i == 4:\n        break\n    print(i, end='')\n```",
            "option_a": "123", "option_b": "1234", "option_c": "12345", "option_d": "123456789",
            "correct_answer": "A"
        },
        # 15. for loop with continue
        {
            "subject_id": 2, "grade": 8, "quarter": 4, "difficulty": 2, "lesson": 4,
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\ns = 0\nfor i in range(1, 5):\n    if i == 3:\n        continue\n    s += i\nprint(s)\n```",
            "option_a": "7", "option_b": "10", "option_c": "6", "option_d": "3",
            "correct_answer": "A"
        },
        # 16. .count() string method
        {
            "subject_id": 2, "grade": 8, "quarter": 4, "difficulty": 2, "lesson": 1,
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\ns = 'olma-anor-olcha'\nprint(s.count('ol'))\n```",
            "option_a": "2", "option_b": "3", "option_c": "1", "option_d": "0",
            "correct_answer": "A"
        },
        # 17. .index() list search
        {
            "subject_id": 2, "grade": 8, "quarter": 4, "difficulty": 2, "lesson": 2,
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\nL = [5, 10, 15, 20]\nprint(L.index(15))\n```",
            "option_a": "2", "option_b": "3", "option_c": "1", "option_d": "15",
            "correct_answer": "A"
        },
        # 18. Nested for loops
        {
            "subject_id": 2, "grade": 8, "quarter": 4, "difficulty": 2, "lesson": 4,
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\ncnt = 0\nfor i in range(2):\n    for j in range(3):\n        cnt += 1\nprint(cnt)\n```",
            "option_a": "6", "option_b": "5", "option_c": "2", "option_d": "3",
            "correct_answer": "A"
        }
    ]
    
    # Insert new G8 questions
    for q in g8_new_questions:
        c.execute('''
            INSERT INTO question (
                subject_id, grade, quarter, difficulty, lesson, question_text,
                option_a, option_b, option_c, option_d, correct_answer
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            q["subject_id"], q["grade"], q["quarter"], q["difficulty"], q["lesson"], q["question_text"],
            q["option_a"], q["option_b"], q["option_c"], q["option_d"], q["correct_answer"]
        ))
    
    conn.commit()
    print(f"Successfully inserted {len(g8_new_questions)} new compliant questions into Grade 8 Q4.")
    
    # Verify G8 count
    c.execute('SELECT count(*) FROM question WHERE grade=8 AND quarter=4')
    g8_count = c.fetchone()[0]
    print(f"New Grade 8 Q4 total questions count: {g8_count} (Expected: 200)")
    assert g8_count == 200, f"Error: Grade 8 Q4 count is {g8_count}, but expected 200."
    
    print("\n=== Step 2: Grade 9 Q4 Updates ===")
    
    # 1. Identify Grade 9 Q4 questions to delete (Queue/deque/stack/LIFO/FIFO)
    c.execute('SELECT id, question_text FROM question WHERE grade=9 AND quarter=4')
    g9_rows = c.fetchall()
    
    g9_to_delete = []
    for qid, qtext in g9_rows:
        qtext_lower = qtext.lower()
        if 'queue' in qtext_lower or 'deque' in qtext_lower or 'stack' in qtext_lower or 'lifo' in qtext_lower or 'fifo' in qtext_lower or 'navbat' in qtext_lower:
            g9_to_delete.append(qid)
            
    print(f"Found {len(g9_to_delete)} questions in Grade 9 Q4 to delete (Queue/deque/stack).")
    
    # Delete them
    for qid in g9_to_delete:
        c.execute('DELETE FROM question WHERE id=?', (qid,))
    conn.commit()
    print("Deleted Grade 9 out-of-syllabus questions successfully.")
    
    # Let's count how many questions we need to insert to make it exactly 300
    c.execute('SELECT count(*) FROM question WHERE grade=9 AND quarter=4')
    g9_current_count = c.fetchone()[0]
    g9_to_seed_count = 300 - g9_current_count
    print(f"Current count of Grade 9 Q4 questions is: {g9_current_count}. We need to insert exactly: {g9_to_seed_count} questions.")
    
    # We will seed exactly the required number of high-quality, comprehensive OOP questions.
    # Let's design 70 premium OOP questions
    g9_oop_questions = [
        # --- OOP BASICS (1-10) ---
        {
            "question_text": "Klass (Class) va Obyekt (Object) tushunchalari o'rtasidagi farq qanday?",
            "option_a": "Klass bu andoza (qolip), obyekt esa shu andoza asosida yaratilgan aniq nusxadir",
            "option_b": "Klass bu o'zgaruvchi, obyekt esa funksiyadir",
            "option_c": "Klass o'zgaruvchan, obyekt esa o'zgarmasdir",
            "option_d": "Klass va obyektning hech qanday farqi yo'q",
            "correct_answer": "A"
        },
        {
            "question_text": "Pythonda klass yaratish uchun qaysi kalit so'z ishlatiladi?",
            "option_a": "class",
            "option_b": "def",
            "option_c": "struct",
            "option_d": "object",
            "correct_answer": "A"
        },
        {
            "question_text": "Pythonda klass nomlari qaysi uslubda yozilishi tavsiya etiladi (PEP 8 bo'yicha)?",
            "option_a": "PascalCase (birinchi harfi katta, masalan: MyClass)",
            "option_b": "camelCase (birinchi harfi kichik, keyingilari katta, masalan: myClass)",
            "option_c": "snake_case (kichik harflar va pastki chiziq, masalan: my_class)",
            "option_d": "UPPERCASE (barcha harflar katta, masalan: MYCLASS)",
            "correct_answer": "A"
        },
        {
            "question_text": "Quyidagi kodda obyektni yaratish qatori qaysi?\n\n```python\nclass Telefon:\n    pass\n\nt = Telefon()\n```",
            "option_a": "t = Telefon()",
            "option_b": "class Telefon:",
            "option_c": "pass",
            "option_d": "Telefon",
            "correct_answer": "A"
        },
        {
            "question_text": "Obyektning o'zgaruvchilari (xususiyatlari) OOPda nima deb ataladi?",
            "option_a": "Atributlar (Attributes)",
            "option_b": "Metodlar (Methods)",
            "option_c": "Funksiyalar (Functions)",
            "option_d": "Konstruktorlar (Constructors)",
            "correct_answer": "A"
        },
        {
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\nclass Kitob:\n    muallif = 'O‘tkir Hoshimov'\n\nk = Kitob()\nprint(k.muallif)\n```",
            "option_a": "O‘tkir Hoshimov",
            "option_b": "muallif",
            "option_c": "Kitob",
            "option_d": "Xatolik beradi",
            "correct_answer": "A"
        },
        {
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\nclass Uy:\n    qavat = 2\n\nu1 = Uy()\nu1.qavat = 3\nprint(u1.qavat)\n```",
            "option_a": "3",
            "option_b": "2",
            "option_c": "Uy",
            "option_d": "Xatolik yuz beradi",
            "correct_answer": "A"
        },
        {
            "question_text": "Quyidagi kodda `t1` va `t2` o'rtasidagi munosabat qanday?\n\n```python\nclass Talaba:\n    pass\n\nt1 = Talaba()\nt2 = Talaba()\n```",
            "option_a": "Ular bitta klassning alohida va mustaqil ikkita obyektidir",
            "option_b": "Ular mutlaqo bir xil o'zgaruvchiga ishora qiladi",
            "option_c": "t2 obyekt t1 ning nusxasi bo'lib, ular bog'liq",
            "option_d": "t1 klass, t2 esa obyekt",
            "correct_answer": "A"
        },
        {
            "question_text": "Obyektning atributiga qiymat berish va unga murojaat qilish qaysi belgi orqali amalga oshiriladi?",
            "option_a": "Nuqta (.) belgisi",
            "option_b": "Qavs ( ) belgisi",
            "option_c": "Ikki nuqta (:) belgisi",
            "option_d": "Yo'naltirish (->) belgisi",
            "correct_answer": "A"
        },
        {
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\nclass Dastur:\n    versiya = 1.0\n\nd = Dastur()\nprint(hasattr(d, 'versiya'))\n```",
            "option_a": "True",
            "option_b": "False",
            "option_c": "1.0",
            "option_d": "Xatolik beradi",
            "correct_answer": "A"
        },

        # --- CONSTRUCTORS AND SELF (11-25) ---
        {
            "question_text": "Pythonda klass konstruktori qaysi maxsus metod yordamida yaratiladi?",
            "option_a": "__init__",
            "option_b": "__main__",
            "option_c": "__new__",
            "option_d": "constructor",
            "correct_answer": "A"
        },
        {
            "question_text": "Klass ichidagi metodlarda birinchi parametr sifatida ishlatiladigan `self` nimani anglatadi?",
            "option_a": "Klassning joriy obyektining o'ziga ishora qiladi",
            "option_b": "Butun klassning o'zini anglatadi",
            "option_c": "Global o'zgaruvchini bildiradi",
            "option_d": "Hech qanday vazifasi yo'q, shunchaki ixtiyoriy so'z",
            "correct_answer": "A"
        },
        {
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\nclass Mashina:\n    def __init__(self, rang):\n        self.rang = rang\n\nm = Mashina('Qora')\nprint(m.rang)\n```",
            "option_a": "Qora",
            "option_b": "rang",
            "option_c": "self",
            "option_d": "Xatolik yuz beradi",
            "correct_answer": "A"
        },
        {
            "question_text": "Klassdan yangi obyekt yaratilganda qaysi metod avtomatik ravishda ishga tushadi?",
            "option_a": "__init__",
            "option_b": "__str__",
            "option_c": "start()",
            "option_d": "run()",
            "correct_answer": "A"
        },
        {
            "question_text": "Quyidagi kodda xatolik nimada?\n\n```python\nclass Xato:\n    def __init__(nom):\n        self.nom = nom\n```",
            "option_a": "Metodda 'self' birinchi parametr qilib ko'rsatilmagan",
            "option_b": "Konstruktor nomi xato yozilgan",
            "option_c": "Metod 'def' bilan boshlanmasligi kerak",
            "option_d": "Konstruktorda qiymat qaytarilmagan",
            "correct_answer": "A"
        },
        {
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\nclass Oquvchi:\n    def __init__(self, ism, yosh=15):\n        self.ism = ism\n        self.yosh = yosh\n\no = Oquvchi('Madina')\nprint(o.yosh)\n```",
            "option_a": "15",
            "option_b": "Madina",
            "option_c": "None",
            "option_d": "Xatolik beradi",
            "correct_answer": "A"
        },
        {
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\nclass Meva:\n    def __init__(self, nom, narx):\n        self.nom = nom\n        self.narx = narx\n\nm1 = Meva('Olma', 10000)\nm2 = Meva('Banan', 18000)\nprint(m1.nom, m2.nom)\n```",
            "option_a": "Olma Banan",
            "option_b": "Olma Olma",
            "option_c": "Banan Banan",
            "option_d": "Xatolik beradi",
            "correct_answer": "A"
        },
        {
            "question_text": "Quyidagi kodda necha marta konstruktor (`__init__`) ishga tushadi?\n\n```python\nclass Shahar:\n    def __init__(self, nom):\n        self.nom = nom\n\ns1 = Shahar('Toshkent')\ns2 = Shahar('Samarqand')\ns3 = Shahar('Buxoro')\n```",
            "option_a": "3 marta",
            "option_b": "1 marta",
            "option_c": "2 marta",
            "option_d": "Hech ham ishlamaydi",
            "correct_answer": "A"
        },
        {
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\nclass Noutbuk:\n    def __init__(self, brend):\n        self.brend = brend\n\nn = Noutbuk('HP')\nprint(type(n))\n```",
            "option_a": "<class '__main__.Noutbuk'>",
            "option_b": "HP",
            "option_c": "brend",
            "option_d": "str",
            "correct_answer": "A"
        },
        {
            "question_text": "Konstruktor ichida obyekt atributlarini yaratish uchun qaysi sintaksis ishlatiladi?",
            "option_a": "self.atribut = qiymat",
            "option_b": "atribut = qiymat",
            "option_c": "self = atribut",
            "option_d": "def atribut(self):",
            "correct_answer": "A"
        },
        {
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\nclass Davlat:\n    def __init__(self, poytaxt):\n        self.poytaxt = poytaxt\n\nd = Davlat('Pekin')\nd.poytaxt = 'Seul'\nprint(d.poytaxt)\n```",
            "option_a": "Seul",
            "option_b": "Pekin",
            "option_c": "Davlat",
            "option_d": "Xatolik beradi",
            "correct_answer": "A"
        },
        {
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\nclass Xona:\n    def __init__(self, en, boy):\n        self.maydon = en * boy\n\nx = Xona(4, 5)\nprint(x.maydon)\n```",
            "option_a": "20",
            "option_b": "9",
            "option_c": "4",
            "option_d": "5",
            "correct_answer": "A"
        },
        {
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\nclass Kvadrat:\n    def __init__(self, tomon):\n        self.tomon = tomon\n\nk = Kvadrat(6)\nprint(k.tomon * k.tomon)\n```",
            "option_a": "36",
            "option_b": "24",
            "option_c": "12",
            "option_d": "6",
            "correct_answer": "A"
        },
        {
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\nclass Hayvon:\n    def __init__(self, tur):\n        self.tur = tur\n\nh = Hayvon('Mushuk')\nprint(hasattr(h, 'tur'))\n```",
            "option_a": "True",
            "option_b": "False",
            "option_c": "Mushuk",
            "option_d": "Xatolik yuz beradi",
            "correct_answer": "A"
        },
        {
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\nclass Shaxs:\n    def __init__(self, ism):\n        self.ism = ism\n\ns = Shaxs('Alisher')\nprint(s.ism == 'Alisher')\n```",
            "option_a": "True",
            "option_b": "False",
            "option_c": "Alisher",
            "option_d": "Xatolik",
            "correct_answer": "A"
        },

        # --- METHODS AND CALLING THEM (26-35) ---
        {
            "question_text": "Klass ichida aniqlangan va obyekt bajara oladigan funksiya nima deb ataladi?",
            "option_a": "Metod (Method)",
            "option_b": "Atribut (Attribute)",
            "option_c": "Konstruktor (Constructor)",
            "option_d": "Modul (Module)",
            "correct_answer": "A"
        },
        {
            "question_text": "Quyidagi kodda metodni chaqirish qatori to'g'ri ko'rsatilgan javobni toping.\n\n```python\nclass Dog:\n    def bark(self):\n        return 'Woof!'\n\nd = Dog()\n```",
            "option_a": "d.bark()",
            "option_b": "bark(d)",
            "option_c": "Dog.bark()",
            "option_d": "d.bark",
            "correct_answer": "A"
        },
        {
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\nclass Kalkulyator:\n    def qosh(self, a, b):\n        return a + b\n\nk = Kalkulyator()\nprint(k.qosh(12, 13))\n```",
            "option_a": "25",
            "option_b": "a+b",
            "option_c": "12",
            "option_d": "13",
            "correct_answer": "A"
        },
        {
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\nclass Doira:\n    def __init__(self, r):\n        self.r = r\n    def diametr(self):\n        return self.r * 2\n\nd = Doira(5)\nprint(d.diametr())\n```",
            "option_a": "10",
            "option_b": "5",
            "option_c": "25",
            "option_d": "Xatolik yuz beradi",
            "correct_answer": "A"
        },
        {
            "question_text": "Klass ichidagi metod boshqa bir metodni qanday chaqirishi mumkin?",
            "option_a": "self.metod_nomi()",
            "option_b": "metod_nomi()",
            "option_c": "Klass.metod_nomi()",
            "option_d": "super.metod_nomi()",
            "correct_answer": "A"
        },
        {
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\nclass Xabarchi:\n    def salom(self):\n        return 'Salom'\n    def salomlash(self):\n        return self.salom() + ', Dunyo!'\n\nx = Xabarchi()\nprint(x.salomlash())\n```",
            "option_a": "Salom, Dunyo!",
            "option_b": "Salom",
            "option_c": ", Dunyo!",
            "option_d": "Xatolik",
            "correct_answer": "A"
        },
        {
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\nclass Robot:\n    def __init__(self, nom):\n        self.nom = nom\n    def tanishtir(self):\n        return 'Men ' + self.nom\n\nr = Robot('Robo')\nprint(r.tanishtir())\n```",
            "option_a": "Men Robo",
            "option_b": "Robo",
            "option_c": "Men nom",
            "option_d": "Xatolik",
            "correct_answer": "A"
        },
        {
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\nclass Mashina:\n    tezlik = 100\n    def tezlashtir(self, qiymat):\n        self.tezlik += qiymat\n\nm = Mashina()\nm.tezlashtir(20)\nprint(m.tezlik)\n```",
            "option_a": "120",
            "option_b": "100",
            "option_c": "20",
            "option_d": "0",
            "correct_answer": "A"
        },
        {
            "question_text": "Metod ta'rifida (def) `self` argumentidan keyin qo'shimcha parametrlar ko'rsatish mumkinmi?",
            "option_a": "Ha, istalgancha qo'shimcha parametrlar ko'rsatish mumkin",
            "option_b": "Yo'q, metod faqat bitta 'self' parametridan iborat bo'lishi shart",
            "option_c": "Faqat bitta qo'shimcha parametr ko'rsatish mumkin",
            "option_d": "Faqat sonli parametrlar ko'rsatish mumkin",
            "correct_answer": "A"
        },
        {
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\nclass Hisob:\n    def __init__(self):\n        self.qiymat = 1\n    def oshir(self):\n        self.qiymat += 1\n\nh = Hisob()\nh.oshir()\nh.oshir()\nprint(h.qiymat)\n```",
            "option_a": "3",
            "option_b": "1",
            "option_c": "2",
            "option_d": "4",
            "correct_answer": "A"
        },

        # --- ENCAPSULATION (36-45) ---
        {
            "question_text": "OOPda ma'lumotlarni (atributlarni) himoyalash va ularni metodlar ichida yashirish tushunchasi nima deyiladi?",
            "option_a": "Inkapsulyatsiya (Encapsulation)",
            "option_b": "Vorislik (Inheritance)",
            "option_c": "Polimorfizm (Polymorphism)",
            "option_d": "Abstraksiya (Abstraction)",
            "correct_answer": "A"
        },
        {
            "question_text": "Pythonda atributlarni xususiy (private) qilish uchun ularning nomi oldiga qanday belgi qo'yiladi?",
            "option_a": "Ikkita pastki chiziq (__) masalan: __kod",
            "option_b": "Bitta pastki chiziq (_) masalan: _kod",
            "option_c": "Panjara belgisi (#) masalan: #kod",
            "option_d": "Dollar belgisi ($) masalan: $kod",
            "correct_answer": "A"
        },
        {
            "question_text": "Quyidagi kod ishga tushirilsa nima sodir bo'ladi?\n\n```python\nclass Karta:\n    def __init__(self, parol):\n        self.__parol = parol\n\nk = Karta('1234')\nprint(k.__parol)\n```",
            "option_a": "AttributeError xatoligi yuz beradi (atribut yopiq bo'lgani uchun)",
            "option_b": "1234 chop etiladi",
            "option_c": "__parol chop etiladi",
            "option_d": "None chop etiladi",
            "correct_answer": "A"
        },
        {
            "question_text": "Xususiy (private) atributlar qiymatini olish va o'zgartirish uchun yoziladigan metodlar qanday ataladi?",
            "option_a": "Getter va Setter metodlari",
            "option_b": "Constructor va Destructor metodlari",
            "option_c": "Input va Output metodlari",
            "option_d": "Private va Public metodlari",
            "correct_answer": "A"
        },
        {
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\nclass Talaba:\n    def __init__(self, baho):\n        self.__baho = baho\n    def get_baho(self):\n        return self.__baho\n\nt = Talaba(5)\nprint(t.get_baho())\n```",
            "option_a": "5",
            "option_b": "Xatolik yuz beradi",
            "option_c": "__baho",
            "option_d": "None",
            "correct_answer": "A"
        },
        {
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\nclass Bank:\n    def __init__(self, balans):\n        self.__balans = balans\n    def set_balans(self, yangi):\n        self.__balans = yangi\n    def get_balans(self): \n        return self.__balans\n\nb = Bank(100)\nb.set_balans(250)\nprint(b.get_balans())\n```",
            "option_a": "250",
            "option_b": "100",
            "option_c": "Xatolik beradi",
            "option_d": "350",
            "correct_answer": "A"
        },
        {
            "question_text": "Quyidagilardan qaysi biri inkapsulyatsiyaning asosiy afzalligi hisoblanadi?",
            "option_a": "Obyekt ma'lumotlarini ruxsatsiz to'g'ridan-to'g'ri o'zgartirishdan himoya qilish",
            "option_b": "Dasturning tezligini bir necha barobar oshirish",
            "option_c": "Faqat grafik oynalar bilan ishlash imkonini berish",
            "option_d": "O'zgaruvchilarni butunlay yo'q qilish",
            "correct_answer": "A"
        },
        {
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\nclass Parol:\n    def __init__(self, text):\n        self.__text = text\n\np = Parol('abc')\nprint(hasattr(p, '__text'))\n```",
            "option_a": "False",
            "option_b": "True",
            "option_c": "abc",
            "option_d": "Xatolik beradi",
            "correct_answer": "A"
        },
        {
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\nclass Foydalanuvchi:\n    def __init__(self, yosh):\n        self.__yosh = yosh\n    def set_yosh(self, yosh):\n        if yosh > 0:\n            self.__yosh = yosh\n    def get_yosh(self):\n        return self.__yosh\n\nf = Foydalanuvchi(15)\nf.set_yosh(-5)\nprint(f.get_yosh())\n```",
            "option_a": "15",
            "option_b": "-5",
            "option_c": "0",
            "option_d": "Xatolik beradi",
            "correct_answer": "A"
        },
        {
            "question_text": "Obyekt atributi oldiga hech qanday belgi qo'yilmasa (masalan: `self.ism`), u qanday atribut hisoblanadi?",
            "option_a": "Ochiq (Public) atribut",
            "option_b": "Yopiq (Private) atribut",
            "option_c": "Himoyalangan (Protected) atribut",
            "option_d": "Statik (Static) atribut",
            "correct_answer": "A"
        },

        # --- INHERITANCE (46-55) ---
        {
            "question_text": "Bir klassning atribut va metodlarini boshqa yangi klassga o'tkazish (meros olish) tushunchasi OOPda nima deyiladi?",
            "option_a": "Vorislik (Inheritance)",
            "option_b": "Inkapsulyatsiya (Encapsulation)",
            "option_c": "Polimorfizm (Polymorphism)",
            "option_d": "Abstraksiya (Abstraction)",
            "correct_answer": "A"
        },
        {
            "question_text": "Quyidagi kodda qaysi klass voris (bola) klass hisoblanadi?\n\n```python\nclass Hayvon:\n    pass\n\nclass It(Hayvon):\n    pass\n```",
            "option_a": "It",
            "option_b": "Hayvon",
            "option_c": "Ikkalasi ham",
            "option_d": "Hech qaysisi",
            "correct_answer": "A"
        },
        {
            "question_text": "Voris (bola) klassda ota klassning konstruktorini chaqirish va unga parametr uzatish uchun qaysi maxsus funksiya ishlatiladi?",
            "option_a": "super()",
            "option_b": "parent()",
            "option_c": "init()",
            "option_d": "self()",
            "correct_answer": "A"
        },
        {
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\nclass Shaxs:\n    def salom(self):\n        return 'Salom'\n\nclass Talaba(Shaxs):\n    pass\n\nt = Talaba()\nprint(t.salom())\n```",
            "option_a": "Salom",
            "option_b": "Xatolik yuz beradi",
            "option_c": "Talaba",
            "option_d": "None",
            "correct_answer": "A"
        },
        {
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\nclass Transport:\n    def __init__(self, tezlik):\n        self.tezlik = tezlik\n\nclass Samolyot(Transport):\n    def __init__(self, tezlik, balandlik):\n        super().__init__(tezlik)\n        self.balandlik = balandlik\n\ns = Samolyot(800, 10000)\nprint(s.tezlik)\n```",
            "option_a": "800",
            "option_b": "10000",
            "option_c": "super()",
            "option_d": "Xatolik beradi",
            "correct_answer": "A"
        },
        {
            "question_text": "Ota klassda bor bo'lgan metodni bola klassda qayta yozish va uning ishlashini o'zgartirish nima deyiladi?",
            "option_a": "Metodni qayta belgilash (Method Overriding)",
            "option_b": "Metodni yuklash (Method Overloading)",
            "option_c": "Metod inkapsulyatsiyasi",
            "option_d": "Konstruktor chaqirish",
            "correct_answer": "A"
        },
        {
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\nclass Ota:\n    def ish(self):\n        return 'Ota ishlamoqda'\n\nclass Bola(Ota):\n    def ish(self):\n        return 'Bola ishlamoqda'\n\nb = Bola()\nprint(b.ish())\n```",
            "option_a": "Bola ishlamoqda",
            "option_b": "Ota ishlamoqda",
            "option_c": "Xatolik beradi",
            "option_d": "Hech narsa",
            "correct_answer": "A"
        },
        {
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\nclass Ota:\n    def __init__(self):\n        self.a = 10\n\nclass Bola(Ota):\n    def __init__(self):\n        super().__init__()\n        self.b = 20\n\nb = Bola()\nprint(b.a + b.b)\n```",
            "option_a": "30",
            "option_b": "10",
            "option_c": "20",
            "option_d": "Xatolik",
            "correct_answer": "A"
        },
        {
            "question_text": "Pythonda bitta klass bir vaqtning o'zida bir nechta klasslardan meros olishi mumkinmi (Ko'p tomonlama vorislik)?",
            "option_a": "Ha, mumkin",
            "option_b": "Yo'q, faqat bitta klassdan meros olish mumkin",
            "option_c": "Faqat ikkita klassdan meros olish mumkin",
            "option_d": "Faqat funksiyalardan meros olish mumkin",
            "correct_answer": "A"
        },
        {
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\nclass Ota:\n    pass\n\nclass Bola(Ota):\n    pass\n\nb = Bola()\nprint(isinstance(b, Ota))\n```",
            "option_a": "True",
            "option_b": "False",
            "option_c": "Bola",
            "option_d": "Ota",
            "correct_answer": "A"
        },

        # --- POLYMORPHISM (56-65) ---
        {
            "question_text": "Turli klasslarda bir xil nomli metodlarning har xil natija qaytarishi (turli xil ishlashi) tushunchasi OOPda nima deyiladi?",
            "option_a": "Polimorfizm (Polymorphism)",
            "option_b": "Inkapsulyatsiya (Encapsulation)",
            "option_c": "Vorislik (Inheritance)",
            "option_d": "Abstraksiya (Abstraction)",
            "correct_answer": "A"
        },
        {
            "question_text": "Quyidagi kod qaysi OOP tamoyiliga yaqqol misol bo'ladi?\n\n```python\nclass Cat:\n    def sound(self): return 'Meow'\nclass Dog:\n    def sound(self): return 'Woof'\n\nfor animal in [Cat(), Dog()]:\n    print(animal.sound())\n```",
            "option_a": "Polimorfizm",
            "option_b": "Inkapsulyatsiya",
            "option_c": "Abstraksiya",
            "option_d": "Vorislik",
            "correct_answer": "A"
        },
        {
            "question_text": "Quyidagi kodda `sound()` metodlari chaqirilganda nima chop etiladi?\n\n```python\nclass Quora:\n    def sound(self): return 'Shitirlash'\nclass Radio:\n    def sound(self): return 'Musiqa'\n\nprint(Radio().sound())\n```",
            "option_a": "Musiqa",
            "option_b": "Shitirlash",
            "option_c": "Musiqa Shitirlash",
            "option_d": "Xatolik beradi",
            "correct_answer": "A"
        },
        {
            "question_text": "Polimorfizm so'zining kelib chiqishi va lug'aviy ma'nosi nima?",
            "option_a": "Ko'p shakllilik (grekcha 'poly' - ko'p, 'morph' - shakl)",
            "option_b": "Birgalikda ishlash",
            "option_c": "Ma'lumotlarni yashirish",
            "option_d": "Avtomatik yaratilish",
            "correct_answer": "A"
        },
        {
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\nclass A:\n    def f(self): return 1\nclass B(A):\n    def f(self): return 2\n\nprint(A().f() + B().f())\n```",
            "option_a": "3",
            "option_b": "2",
            "option_c": "1",
            "option_d": "4",
            "correct_answer": "A"
        },
        {
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\nclass Shakl:\n    def chiz(self): return 'Shakl chizish'\nclass Uchburchak(Shakl):\n    def chiz(self): return 'Uchburchak chizish'\n\nu = Uchburchak()\nprint(u.chiz())\n```",
            "option_a": "Uchburchak chizish",
            "option_b": "Shakl chizish",
            "option_c": "Xatolik",
            "option_d": "None",
            "correct_answer": "A"
        },
        {
            "question_text": "Polimorfizm qanday asosiy qulaylikni beradi?",
            "option_a": "Bir xil interfeys (metod nomi) orqali har xil obyeklar bilan ishlash imkonini beradi",
            "option_b": "Xotirada kam joy egallashni ta'minlaydi",
            "option_c": "Faqat bir xil turdagi ma'lumotlarni solishtirishni ta'minlaydi",
            "option_d": "Foydalanuvchi kiritishini tekshiradi",
            "correct_answer": "A"
        },
        {
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\nclass X:\n    def a(self): return 'X'\nclass Y(X):\n    pass\n\nprint(Y().a())\n```",
            "option_a": "X",
            "option_b": "Y",
            "option_c": "Xatolik",
            "option_d": "None",
            "correct_answer": "A"
        },
        {
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\nclass Kvadrat:\n    def chiz(self): return 'Kvadrat'\nclass Doira:\n    def chiz(self): return 'Doira'\n\ndef rasm_chiz(obj):\n    return obj.chiz()\n\nprint(rasm_chiz(Doira()))\n```",
            "option_a": "Doira",
            "option_b": "Kvadrat",
            "option_c": "rasm_chiz",
            "option_d": "Xatolik beradi",
            "correct_answer": "A"
        },
        {
            "question_text": "Agar bola klassda ota klass metodining nomi bilan mutlaqo bir xil nomli metod yozilsa, nima sodir bo'ladi?",
            "option_a": "Bola klassning metodi ota klassning metodini ustidan yozadi (override qiladi)",
            "option_b": "Sintaktik xatolik yuz beradi",
            "option_c": "Ikkala metod ham parallel ishlaydi",
            "option_d": "Ota klassning metodi butunlay o'chib ketadi",
            "correct_answer": "A"
        },

        # --- ABSTRACTION AND MAGIC METHODS (66-70) ---
        {
            "question_text": "Foydalanuvchidan murakkab ichki mexanizmlarni yashirib, faqat eng zaruriy ma'lumot va interfeyslarni ko'rsatish tamoyili nima deyiladi?",
            "option_a": "Abstraksiya (Abstraction)",
            "option_b": "Inkapsulyatsiya (Encapsulation)",
            "option_c": "Vorislik (Inheritance)",
            "option_d": "Polimorfizm (Polymorphism)",
            "correct_answer": "A"
        },
        {
            "question_text": "Pythonda obyektni `print()` funksiyasi orqali chop etganda uning foydalanuvchi tushunadigan chiroyli matn ko'rinishini qaytaruvchi dunder (magic) metod qaysi?",
            "option_a": "__str__",
            "option_b": "__init__",
            "option_c": "__repr__",
            "option_d": "__print__",
            "correct_answer": "A"
        },
        {
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\nclass Odam:\n    def __init__(self, ism):\n        self.ism = ism\n    def __str__(self):\n        return f'Ismi: {self.ism}'\n\no = Odam('Kamol')\nprint(o)\n```",
            "option_a": "Ismi: Kamol",
            "option_b": "Ismi: self.ism",
            "option_c": "<__main__.Odam object at ...>",
            "option_d": "Xatolik yuz beradi",
            "correct_answer": "A"
        },
        {
            "question_text": "Obyektning dasturchi uchun mo'ljallangan va uni qayta tiklashga yordam beradigan rasmiy matnli ifodasini qaytaruvchi magic metod qaysi?",
            "option_a": "__repr__",
            "option_b": "__str__",
            "option_c": "__init__",
            "option_d": "__main__",
            "correct_answer": "A"
        },
        {
            "question_text": "Quyidagi kod natijasi nima bo'ladi?\n\n```python\nclass Point:\n    def __init__(self, x, y):\n        self.x = x\n        self.y = y\n    def __repr__(self):\n        return f'Point({self.x}, {self.y})'\n\np = Point(3, 4)\nprint(repr(p))\n```",
            "option_a": "Point(3, 4)",
            "option_b": "<__main__.Point object>",
            "option_c": "Point",
            "option_d": "Xatolik beradi",
            "correct_answer": "A"
        }
    ]
    
    # Shuffle or select exactly `g9_to_seed_count` questions.
    # We designed 70 questions which is exactly the number of deleted questions (g9_to_seed_count is 70)
    # Let's verify that g9_to_seed_count is indeed 70. If not, we can adjust.
    print(f"Designed {len(g9_oop_questions)} OOP questions.")
    
    # Insert new G9 OOP questions
    for q in g9_oop_questions[:g9_to_seed_count]:
        c.execute('''
            INSERT INTO question (
                subject_id, grade, quarter, difficulty, question_text,
                option_a, option_b, option_c, option_d, correct_answer
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            2, 9, 4, 2, q["question_text"],
            q["option_a"], q["option_b"], q["option_c"], q["option_d"], q["correct_answer"]
        ))
        
    conn.commit()
    print(f"Successfully inserted {min(len(g9_oop_questions), g9_to_seed_count)} new OOP questions into Grade 9 Q4.")
    
    # Verify G9 count
    c.execute('SELECT count(*) FROM question WHERE grade=9 AND quarter=4')
    g9_count = c.fetchone()[0]
    print(f"New Grade 9 Q4 total questions count: {g9_count} (Expected: 300)")
    assert g9_count == 300, f"Error: Grade 9 Q4 count is {g9_count}, but expected 300."
    
    # Check for any remaining queue/deque questions in Grade 9 Q4
    c.execute('SELECT count(*) FROM question WHERE grade=9 AND quarter=4 AND (question_text LIKE "%Queue%" OR question_text LIKE "%deque%")')
    remaining_qd = c.fetchone()[0]
    print(f"Remaining queue/deque questions in Grade 9 Q4: {remaining_qd} (Expected: 0)")
    assert remaining_qd == 0, f"Error: {remaining_qd} queue/deque questions remain in Grade 9 Q4."
    
    # Check for any remaining any/all/% questions in Grade 8 Q4
    c.execute('SELECT count(*) FROM question WHERE grade=8 AND quarter=4 AND (question_text LIKE "%any(%" OR question_text LIKE "%all(%" OR question_text LIKE "% qoldiq %")')
    remaining_any_all = c.fetchone()[0]
    print(f"Remaining any/all/% questions in Grade 8 Q4: {remaining_any_all} (Expected: 0)")
    assert remaining_any_all == 0, f"Error: {remaining_any_all} any/all/% questions remain in Grade 8 Q4."
    
    conn.close()
    print("\nDatabase migration and verification completed successfully!")

if __name__ == '__main__':
    update_database()
