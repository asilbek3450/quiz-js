import os
import random
from app import create_app
from extensions import db
from models import Subject, Question, ControlWork

app = create_app()

def get_or_create_subject(name):
    subject = Subject.query.filter_by(name=name).first()
    if not subject:
        subject = Subject(name=name, grades='7,8,9')
        db.session.add(subject)
        db.session.commit()
    else:
        grades_list = [g.strip() for g in subject.grades.split(',') if g.strip()]
        for g in ['7', '8', '9']:
            if g not in grades_list:
                grades_list.append(g)
        subject.grades = ','.join(grades_list)
        db.session.commit()
    return subject

def add_questions_to_db(questions_list):
    saved_questions = []
    for q in questions_list:
        exists = Question.query.filter_by(
            subject_id=q.subject_id,
            grade=q.grade,
            quarter=q.quarter,
            question_text=q.question_text
        ).first()
        if not exists:
            db.session.add(q)
            db.session.flush() 
            saved_questions.append(q)
        else:
            saved_questions.append(exists)
    db.session.commit()
    return saved_questions

def create_control_work(subject_id, grade, quarter, title, target_count=100):
    pool = Question.query.filter(
        Question.subject_id == subject_id,
        Question.grade == grade,
        Question.quarter <= quarter
    ).all()
    
    if len(pool) < target_count:
        selected = pool
    else:
        selected = random.sample(pool, target_count)
        
    cw = ControlWork.query.filter_by(subject_id=subject_id, grade=grade, quarter=quarter, title=title).first()
    if not cw:
        cw = ControlWork(
            title=title,
            subject_id=subject_id,
            grade=grade,
            quarter=quarter,
            time_limit=40,
            is_active=True
        )
        db.session.add(cw)
        db.session.flush()
    else:
        cw.questions = []
        db.session.flush()
        
    cw.questions.extend(selected)
    db.session.commit()
    return cw, len(selected)

# -------- 7-SINF --------
def generate_7_q1(subject_id):
    questions = []
    theory = [
        ("Dastur va dasturlash nima?", "Kompyuter bajarishi kerak bo'lgan buyruqlar to'plami", "Kompyuterni yoqish jarayoni", "Monitor va klaviatura", "Faqat o'yin o'ynash uchun vosita"),
        ("Eng mashhur dasturlash tillaridan biri qaysi?", "Python", "Monitor", "Windows", "Protsessor"),
        ("Pythonda ma'lumotni ekranga chiqaruvchi funksiya qaysi?", "print()", "input()", "show()", "display()"),
        ("Pythonda o'zgaruvchilar nima vazifani bajaradi?", "Xotirada ma'lumot saqlaydi", "Ekranga ma'lumot chiqaradi", "Kompyuterni o'chiradi", "Internetga ulanadi"),
        ("Qaysi biri haqiqiy (float) ma'lumot turi hisoblanadi?", "3.14", "42", "'salom'", "True"),
        ("Qaysi biri butun (int) ma'lumot turi hisoblanadi?", "10", "10.5", "'10'", "False"),
        ("Qaysi biri satr (str) ma'lumot turi hisoblanadi?", "'olma'", "25", "25.0", "True")
    ]
    for _ in range(4): # 28
        for q_text, ans, w1, w2, w3 in theory:
            opts = [ans, w1, w2, w3]
            random.shuffle(opts)
            questions.append(Question(subject_id=subject_id, grade=7, quarter=1, question_text=q_text, option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3], correct_answer=['a','b','c','d'][opts.index(ans)]))

    # Math eval (72)
    ops = [('+', '+'), ('-', '-'), ('*', '*'), ('/', '/'), ('//', '//'), ('%', '%'), ('**', '**')]
    for _ in range(72):
        a = random.randint(2, 25)
        b = random.randint(2, 10)
        op_str, op_eval = random.choice(ops)
        if op_eval == '**':
            a, b = random.randint(2, 5), random.randint(2, 3)
        if op_eval in ('/', '//', '%') and b == 0:
            b = 1
            
        expr = f"{a} {op_eval} {b}"
        try:
            ans = eval(expr)
            if op_eval == '/': ans = round(ans, 2)
        except Exception:
            continue
            
        ans_str = str(ans)
        opts = [ans_str, str(ans + random.randint(1,5)), str(ans - random.randint(1,5)), str(ans * 2)]
        opts = list(set([str(o) for o in opts]))
        while len(opts) < 4:
            opts.append(str(ans + random.randint(10,50)))
            opts = list(set(opts))
        random.shuffle(opts)
        q = Question(subject_id=subject_id, grade=7, quarter=1, question_text=f"Python kodining natijasini toping:\n```python\nprint({a} {op_str} {b})\n```", option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3], correct_answer=['a','b','c','d'][opts.index(ans_str)])
        questions.append(q)
    return questions[:100]

def generate_7_q2(subject_id):
    questions = []
    theory = [
        ("Satr (string) qanday ifodalanadi?", "Qo'shtirnoq yoki bittalik tirnoq ichida", "Kvadrat qavslar ichida", "Raqamlar orqali", "Jingalak qavslar ichida"),
        ("Satr uzunligini aniqlovchi funksiya qaysi?", "len()", "size()", "count()", "length()"),
        ("Satrdagi belgilarni kichik harflarga o'tqazuvchi metod?", "lower()", "upper()", "title()", "capitalize()"),
        ("Satrdagi belgilarni hammasini katta harflarga o'tqazuvchi metod?", "upper()", "lower()", "title()", "swapcase()"),
        ("Satr boshidagi va oxiridagi bo'sh joylarni kesib oluvchi metod?", "strip()", "trim()", "clear()", "remove()"),
        ("Matnli '15' ni butun songa o'giruvchi funksiya?", "int()", "str()", "float()", "bool()")
    ]
    for _ in range(3): # 18
        for q_text, ans, w1, w2, w3 in theory:
            opts = [ans, w1, w2, w3]
            random.shuffle(opts)
            questions.append(Question(subject_id=subject_id, grade=7, quarter=2, question_text=q_text, option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3], correct_answer=['a','b','c','d'][opts.index(ans)]))

    words = ["Maktab", "Kitob", "Dastur", "Python", "Kompyuter", "Toshkent", "O'zbekiston", "Algoritm"]
    
    # Simple Indexing (41)
    for _ in range(41):
        word = random.choice(words)
        idx = random.randint(0, len(word) - 1)
        ans = word[idx]
        opts = [ans, word[random.randint(0, len(word)-1)], word[-1], word[0]]
        opts = list(set(opts))
        while len(opts) < 4:
            opts.append(random.choice("abcdefghijklmnopqrstuvwxyz"))
            opts = list(set(opts))
        random.shuffle(opts)
        questions.append(Question(subject_id=subject_id, grade=7, quarter=2, question_text=f"Quyidagi dastur natijasini toping:\n```python\nsoz = '{word}'\nprint(soz[{idx}])\n```", option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3], correct_answer=['a','b','c','d'][opts.index(ans)]))

    # Slicing (41)
    for _ in range(41):
        word = random.choice(words)
        start = random.randint(0, len(word)-3)
        end = random.randint(start+2, len(word))
        ans = word[start:end]
        opts = [ans, word[start:end+1], word[start+1:end], word[0:end]]
        opts = list(set(opts))
        while len(opts) < 4:
            opts.append(word[random.randint(0,2):random.randint(3,len(word))])
            opts = list(set(opts))
        random.shuffle(opts)
        questions.append(Question(subject_id=subject_id, grade=7, quarter=2, question_text=f"Ushbu kod nimani ekranga chiqaradi?\n```python\nmatn = '{word}'\nprint(matn[{start}:{end}])\n```", option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3], correct_answer=['a','b','c','d'][opts.index(ans)]))

    return questions[:100]

def generate_7_q3(subject_id):
    questions = []
    theory = [
        ("Shart operatori qaysi kalit so'z bilan boshlanadi?", "if", "for", "while", "else"),
        ("Qaysi operator shart to'g'ri bo'lmaganda bajariladi?", "else", "if", "elif", "then"),
        ("Bir nechta shartlarni ketma-ket tekshirish uchun ishlatiladi:", "elif", "else if", "if else", "then"),
        ("Ma'lumotlar ro'yxatini shakllantirish uchun ishlatiladi:", "List (Ro'yxat)", "Integer (Butun son)", "Float (Kasr son)", "String (Satr)"),
        ("Tsikl ichidan joriy qadamni yakunlab keyingisiga o'tish tushunchasi:", "continue", "break", "pass", "stop"),
        ("Sikldan butunlay chiqib ketish operatori:", "break", "continue", "exit", "quit"),
        ("Ro'yxat ro'yxatlariga qo'shimcha kiritish qaysi metod bilan bajariladi?", "append()", "add()", "insert()", "push()"),
        ("Cheksiz yoki shartga bog'liq holatda takrorlanuvchi tsikl:", "while", "for", "do", "repeat")
    ]
    for _ in range(2): # 16 theory
        for q_text, ans, w1, w2, w3 in theory:
            opts = [ans, w1, w2, w3]
            random.shuffle(opts)
            questions.append(Question(subject_id=subject_id, grade=7, quarter=3, question_text=q_text, option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3], correct_answer=['a','b','c','d'][opts.index(ans)]))
            
    # Conditional logic
    for _ in range(150):
        x = random.randint(1, 100)
        y = random.randint(1, 100)
        if x > y: ans = "Kotta"
        elif x < y: ans = "Kichik"
        else: ans = "Teng"
        code = f"x = {x}\ny = {y}\nif x > y:\n    print('Kotta')\nelif x < y:\n    print('Kichik')\nelse:\n    print('Teng')"
        opts = ["Kotta", "Kichik", "Teng", "Xatolik beradi"]
        random.shuffle(opts)
        questions.append(Question(subject_id=subject_id, grade=7, quarter=3, question_text=f"Quyidagi kod natijasi nima bo'ladi?\n```python\n{code}\n```", option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3], correct_answer=['a','b','c','d'][opts.index(ans)]))

    # Loops logic
    for _ in range(150):
        start = random.randint(1, 10)
        end = random.randint(11, 20)
        ans = str(list(range(start, end)))
        code = f"natija = []\nfor i in range({start}, {end}):\n    natija.append(i)\nprint(natija)"
        opts = [ans, str(list(range(start, end+1))), str(list(range(start+1, end))), str(list(range(start+1, end+1)))]
        opts = list(set(opts))
        while len(opts) < 4:
            opts.append(f"[{random.randint(1,20)}]")
            opts = list(set(opts))
        random.shuffle(opts)
        questions.append(Question(subject_id=subject_id, grade=7, quarter=3, question_text=f"For tsikli natijasini aniqlang:\n```python\n{code}\n```", option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3], correct_answer=['a','b','c','d'][opts.index(ans)]))
        
    unique_q = {}
    for q in questions: unique_q[q.question_text] = q
    return list(unique_q.values())[:100]

def generate_7_q4(subject_id):
    questions = []
    # Mix from previous + general review (100)
    for _ in range(50):
        n = random.randint(3, 10)
        ans = str(sum(range(n)))
        code = f"s = 0\ni = 0\nwhile i < {n}:\n    s += i\n    i += 1\nprint(s)"
        opts = [ans, str(sum(range(n+1))), str(sum(range(n-1))), str(sum(range(n)) + 2)]
        opts = list(set(opts))
        while len(opts) < 4:
            opts.append(str(random.randint(10,50)))
            opts = list(set(opts))
        random.shuffle(opts)
        questions.append(Question(subject_id=subject_id, grade=7, quarter=4, question_text=f"While tsikli yordamida ishlangan kod natijasi (umumiy yig'indi):\n```python\n{code}\n```", option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3], correct_answer=['a','b','c','d'][opts.index(ans)]))
        
    for _ in range(50):
        method = random.choice([('upper', str.upper), ('lower', str.lower), ('capitalize', str.capitalize)])
        basestr = random.choice(["O'zBek", "daStUr", "pyThOn", "inFormaTika"])
        ans = method[1](basestr)
        code = f"x = '{basestr}'\nprint(x.{method[0]}())"
        opts = [ans, basestr, basestr.lower(), basestr.upper()]
        opts = list(set(opts))
        while len(opts) < 4:
            opts.append("Xatolik bo'ladi")
            opts = list(set(opts))
        random.shuffle(opts)
        questions.append(Question(subject_id=subject_id, grade=7, quarter=4, question_text=f"Kod natijasi qanday bo'ladi?\n```python\n{code}\n```", option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3], correct_answer=['a','b','c','d'][opts.index(ans)]))

    return questions[:100]

# -------- 8-SINF --------
def generate_8_q1(subject_id):
    questions = []
    theory = [
        ("7-sinf takrori: if, elif, else bloklari nimani bildiradi?", "Shartli tekshirish vositalari", "Aylanib o'tish operatorlari", "Malumot turlari", "Tizim funksiyalari"),
        ("while va for tsiklining asosiy farqi nimada?", "for odatda takrorlanishlar soni ma'lum bo'lganda, while esa noma'lum bo'lganda shart bilan ishlatiladi", "Hec qanday farqi yo'q", "for faqat harflar uchun, while sonlar uchun ishlaydi", "while tezroq ishlaydi"),
        ("Sikl ishini tugatmasdan navbatdagi qadamga o'tkazib yuboruvchi so'z?", "continue", "break", "pass", "skip")
    ]
    for _ in range(25): # 25 theory (using random.choice to bulk scale theory duplicates if needed, but best if we just add unique logic)
        q_text, ans, w1, w2, w3 = random.choice(theory)
        opts = [ans, w1, w2, w3]
        random.shuffle(opts)
        questions.append(Question(subject_id=subject_id, grade=8, quarter=1, question_text=q_text, option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3], correct_answer=['a','b','c','d'][opts.index(ans)]))

    # Complex conditions & loops
    for _ in range(80):
        x = random.randint(1, 100)
        y = random.randint(1, 100)
        ans = "True" if x < 50 or y > 50 else "False"
        code = f"x = {x}\ny = {y}\nif x < 50 or y > 50:\n    print('True')\nelse:\n    print('False')"
        opts = ["True", "False", "None", "Error"]
        random.shuffle(opts)
        questions.append(Question(subject_id=subject_id, grade=8, quarter=1, question_text=f"Mantiqiy ifodalar bilan ishlash:\n```python\n{code}\n```", option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3], correct_answer=['a','b','c','d'][opts.index(ans)]))

    for _ in range(80):
        start = random.randint(1, 20)
        stop = random.randint(25, 50)
        step = random.randint(2, 6)
        ans = str(list(range(start, stop, step)))
        code = f"natija = []\nfor i in range({start}, {stop}, {step}):\n    natija.append(i)\nprint(natija)"
        opts = [ans, str(list(range(start, stop, step+1))), str(list(range(start+1, stop, step))), str(list(range(start, stop+step, step)))]
        opts = list(set(opts))
        while len(opts) < 4:
            opts.append(f"[{random.randint(1,20)}]")
            opts = list(set(opts))
        random.shuffle(opts)
        questions.append(Question(subject_id=subject_id, grade=8, quarter=1, question_text=f"Quyidagi kod natijasi nima?\n```python\n{code}\n```", option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3], correct_answer=['a','b','c','d'][opts.index(ans)]))

    # deduplicate early to check
    unique_q = {}
    for q in questions:
        unique_q[q.question_text] = q
    return list(unique_q.values())[:100]

def generate_8_q2(subject_id):
    questions = []
    theory = [
        ("List va Tuple ning eng muhim farqi?", "List o'zgaruvchan (mutable), Tuple o'zgarmas (immutable)", "List o'zgarmas, Tuple o'zgaruvchan", "Hech farqi yo'q", "List faqat son qabul qiladi"),
        ("List qavslarini ko'rsating", "[]", "()", "{}", "<>"),
        ("Tuple qavslarini ko'rsating", "()", "[]", "{}", "<>"),
        ("Dictionary da malumot qanday tuzilmada bo'ladi?", "Key: Value (Kalit: Qiymat)", "Faqat bir xil malumot", "Ketma-ket matn", "Ro'yhat shaklida"),
        ("Lug'atda (Dictionary) malumotlar qanday qavs ichida elon qilinadi?", "{}", "[]", "()", "||")
    ]
    for _ in range(25): # 20
        q_text, ans, w1, w2, w3 = random.choice(theory)
        opts = [ans, w1, w2, w3]
        random.shuffle(opts)
        questions.append(Question(subject_id=subject_id, grade=8, quarter=2, question_text=q_text, option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3], correct_answer=['a','b','c','d'][opts.index(ans)]))

    # Lists
    for _ in range(150):
        lst = [random.randint(1, 15) for _ in range(4)]
        elem = random.randint(16, 25)
        ans = str(lst + [elem])
        code = f"sonlar = {lst}\nsonlar.append({elem})\nprint(sonlar)"
        opts = [ans, str([elem] + lst), str(lst), "Xatolik bo'ladi"]
        random.shuffle(opts)
        questions.append(Question(subject_id=subject_id, grade=8, quarter=2, question_text=f"List ustida append amali natijasi:\n```python\n{code}\n```", option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3], correct_answer=['a','b','c','d'][opts.index(ans)]))
        
    # Dicts
    for _ in range(150):
        keys = ['ism', 'yosh', 'sinf', 'maktab']
        k1, k2 = random.sample(keys, 2)
        v1, v2 = random.randint(10, 30), random.randint(31, 99)
        ans = str(v2)
        code = f"data = {{'{k1}': {v1}, '{k2}': {v2}}}\nprint(data['{k2}'])"
        opts = [ans, str(v1), f"'{k2}'", "KeyError"]
        random.shuffle(opts)
        questions.append(Question(subject_id=subject_id, grade=8, quarter=2, question_text=f"Dictionary dan qiymat olish yoradami natijani toping:\n```python\n{code}\n```", option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3], correct_answer=['a','b','c','d'][opts.index(ans)]))

    unique_q = {}
    for q in questions: unique_q[q.question_text] = q
    return list(unique_q.values())[:100]

def generate_8_q3(subject_id):
    questions = []
    theory = [
        ("Funksiya qaysi kalit so'z orqali e'lon qilinadi?", "def", "func", "function", "lambda"),
        ("Funksiya qiymat qaytarishi uchun so'z?", "return", "print", "get", "put"),
        ("Istalgan miqdordagi oddiy argumentlarni qabul kilish belgisi?", "*args", "**kwargs", "args[]", "[]"),
        ("Istalgan miqdordagi kalit-qiymatli argumentlarni qabul qilish belgisi?", "**kwargs", "*args", "kwargs[]", "{}"),
        ("Python f-string qanday e'lon qilinadi?", "f'Malumot {o\'zgaruvchi}'", "f(Malumot)", "'Malumot' + o'zgaruvchi", "str(Malumot)")
    ]
    for _ in range(25): # 25 theory
        q_text, ans, w1, w2, w3 = random.choice(theory)
        opts = [ans, w1, w2, w3]
        random.shuffle(opts)
        questions.append(Question(subject_id=subject_id, grade=8, quarter=3, question_text=q_text, option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3], correct_answer=['a','b','c','d'][opts.index(ans)]))
            
    # Functions
    for _ in range(150):
        f_type = random.choice(['yigindi', 'kattasi', 'juftmi'])
        if f_type == 'yigindi':
            a, b = random.randint(5, 50), random.randint(15, 60)
            ans = str(a + b)
            code = f"def yigindi(x, y):\n    return x + y\n\nprint(yigindi({a}, {b}))"
            opts = [ans, str(a*b), str(b-a), "Xato"]
        elif f_type == 'kattasi':
            a, b = random.randint(10, 99), random.randint(10, 99)
            while a == b: b = random.randint(10, 99)
            ans = str(max(a, b))
            code = f"def kattasi(a, b):\n    if a > b:\n        return a\n    return b\n\nprint(kattasi({a}, {b}))"
            opts = [ans, str(min(a,b)), str(a+b), "Hech qaysi"]
        else:
            n = random.randint(10, 99)
            ans = str(n % 2 == 0)
            code = f"def juftmi(n):\n    return n % 2 == 0\n\nprint(juftmi({n}))"
            opts = ["True", "False", "None", "Error"]
            
        opts = list(set(opts))
        while len(opts) < 4:
            opts.append(f"{random.randint(10, 150)}")
            opts = list(set(opts))
        random.shuffle(opts)
        questions.append(Question(subject_id=subject_id, grade=8, quarter=3, question_text=f"Funksiyaga murojaat qilingandagi natijani toping:\n```python\n{code}\n```", option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3], correct_answer=['a','b','c','d'][opts.index(str(ans))]))

    # Comprehensions
    for _ in range(150):
        c_type = random.choice(['kavadrat', 'juft', 'len'])
        if c_type == 'kavadrat':
            n = random.randint(2, 5)
            ans = str([i*i for i in range(1, n+1)])
            code = f"sonlar = [i*i for i in range(1, {n+1})]\nprint(sonlar)"
            opts = [ans, str([i*i for i in range(0, n)]), str([i*2 for i in range(1, n+1)]), "Xato"]
        elif c_type == 'juft':
            n = random.randint(6, 12)
            ans = str([i for i in range(1, n) if i%2==0])
            code = f"sonlar = [i for i in range(1, {n}) if i % 2 == 0]\nprint(sonlar)"
            opts = [ans, str([i for i in range(1, n) if i%2!=0]), str([i*2 for i in range(1, n)]), "Bo'sh list"]
        else:
            words = random.sample(["olma", "banan", "gilos", "behi", "anor"], 3)
            ans = str([len(w) for w in words])
            code = f"mevalar = {words}\nuzunlik = [len(m) for m in mevalar]\nprint(uzunlik)"
            opts = [ans, str([len(w)+1 for w in words]), "Error", "None"]
            
        opts = list(set(opts))
        while len(opts) < 4:
            opts.append(f"[{random.randint(1,10)}]")
            opts = list(set(opts))
        random.shuffle(opts)
        questions.append(Question(subject_id=subject_id, grade=8, quarter=3, question_text=f"List comprehension (generatsiya) natijasini toping:\n```python\n{code}\n```", option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3], correct_answer=['a','b','c','d'][opts.index(str(ans))]))

    unique_q = {}
    for q in questions: unique_q[q.question_text] = q
    return list(unique_q.values())[:100]

def generate_8_q4(subject_id):
    questions = []
    for _ in range(150):
        t = random.choice(['k', 's', 'l'])
        if t == 'k':
            val = random.randint(3, 5)
            ans = "A" * val
            code = f"def kopaytma_str(matn, n):\n    return matn * n\n\nprint(kopaytma_str('A', {val}))"
            opts = [ans, "A" * (val+1), "A" * (val-1), f"A{val}"]
        elif t == 's':
            n = random.randint(4, 8)
            ans = str(sum(range(1, n+1)))
            code = f"def n_gacha_yigindi(n):\n    return sum(range(1, n + 1))\n\nprint(n_gacha_yigindi({n}))"
            opts = [ans, str(sum(range(n))), str(sum(range(1, n+2))), "Xato"]
        else:
            n = random.randint(10, 50)
            ans = str(n * 2)
            code = f"def ikkilangan(a):\n    return a * 2\n\nprint(ikkilangan({n}))"
            opts = [ans, str(n), str(n*3), "None"]
            
        opts = list(set(opts))
        while len(opts) < 4:
            opts.append(str(random.randint(10, 100)))
            opts = list(set(opts))
        random.shuffle(opts)
        questions.append(Question(subject_id=subject_id, grade=8, quarter=4, question_text=f"Funksiya bo'yicha yakuniy takrorlash:\n```python\n{code}\n```", option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3], correct_answer=['a','b','c','d'][opts.index(ans)]))
        
    for _ in range(150):
        t = random.choice(['sum', 'min', 'kwargs'])
        if t == 'sum':
            lst = [random.randint(1, 10), random.randint(11, 20), random.randint(21, 30)]
            ans = str(sum(lst))
            code = f"def summa(*args):\n    return sum(args)\n\nprint(summa({lst[0]}, {lst[1]}, {lst[2]}))"
            opts = [ans, str(lst[0]*lst[1]), str(sum(lst)*2), "Xatolik"]
        elif t == 'min':
            lst = [random.randint(5, 10), random.randint(11, 20), random.randint(1, 4)]
            ans = str(min(lst))
            code = f"def eng_kichigi(*args):\n    return min(args)\n\nprint(eng_kichigi({lst[0]}, {lst[1]}, {lst[2]}))"
            opts = [ans, str(max(lst)), str(sum(lst)), "Error"]
        else:
            ans = "2"
            code = f"def foydalanuvchi(**kwargs):\n    return len(kwargs)\n\nprint(foydalanuvchi(ism='Ali', yosh=15))"
            opts = [ans, "1", "3", "0"]
            
        opts = list(set(opts))
        while len(opts) < 4:
            opts.append(str(random.randint(20, 100)))
            opts = list(set(opts))
        random.shuffle(opts)
        questions.append(Question(subject_id=subject_id, grade=8, quarter=4, question_text=f"Quyidagi args/kwargs metodikasi natijasi qanday:\n```python\n{code}\n```", option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3], correct_answer=['a','b','c','d'][opts.index(ans)]))

    unique_q = {}
    for q in questions: unique_q[q.question_text] = q
    return list(unique_q.values())[:100]

# -------- 9-SINF --------
def generate_9_q1(subject_id):
    # Q1 and Q2 usually go together regarding syntax review and strings in 9th grade start
    questions = []
    theory = [
        ("Python tiliga xos izoh qaysi belgi bilan yoziladi?", "#", "//", "<!--", "/*"),
        ("Sikl ishini butunlay to'xtatuvchi so'z?", "break", "continue", "stop", "exit"),
        ("If-elif-else bloklarida 'elif' nimani bildiradi?", "Qo'shimcha boshqa shart (else if)", "Oxirgi holat", "Siklning boshlanishi", "Faul holat"),
        ("Matndagi (str) metod: .lower() ni vazifasi nima?", "Barcha harflarni kichik qiladi", "Bosh harfni katta qiladi", "Barcha harflarni katta qiladi", "Bo'sh joylarni o'chiradi")
    ]
    for _ in range(15): # scale theory
        q_text, ans, w1, w2, w3 = random.choice(theory)
        opts = [ans, w1, w2, w3]
        random.shuffle(opts)
        questions.append(Question(subject_id=subject_id, grade=9, quarter=1, question_text=q_text, option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3], correct_answer=['a','b','c','d'][opts.index(ans)]))
            
    for _ in range(150):
        t = random.choice(['count', 'find', 'isupper', 'len'])
        word = random.choice(["O'zbekiston", "Toshkent shahri", "Python Programming", "Algoritm", "Maktab tizimi"])
        
        if t == 'count':
            char = random.choice(word)
            ans = str(word.count(char))
            code = f"matn = '{word}'\nprint(matn.count('{char}'))"
            opts = [ans, str(int(ans)+1), str(int(ans)+2), "0"]
        elif t == 'find':
            char = word[random.randint(1, len(word)-1)]
            ans = str(word.find(char))
            code = f"matn = '{word}'\nprint(matn.find('{char}'))"
            opts = [ans, str(word.rfind(char)+1), "-1", "Error"]
        elif t == 'isupper':
            raw = "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=random.randint(4, 8)))
            is_up = random.choice([True, False])
            w = raw.upper() if is_up else raw
            ans = str(w.isupper())
            code = f"matn = '{w}'\nprint(matn.isupper())"
            opts = [ans, "False" if ans == "True" else "True", "None", "Xatolik"]
        else:
            w = (" " * random.randint(1, 10)) + random.choice(["Salom", "Dunyo", "Test"]) + (" " * random.randint(1, 10))
            ans = str(len(w))
            code = f"matn = '{w}'\nprint(len(matn))"
            opts = [ans, str(len(w.strip())), str(len(w)-2), str(len(w)+random.randint(1,5))]
            
        opts = list(set(opts))
        while len(opts) < 4:
            opts.append(str(random.randint(0, 30)))
            opts = list(set(opts))
        random.shuffle(opts)
        questions.append(Question(subject_id=subject_id, grade=9, quarter=1, question_text=f"Dastur nimani chop etadi (String method)?\n```python\n{code}\n```", option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3], correct_answer=['a','b','c','d'][opts.index(ans)]))
    
    unique_q = {}
    for q in questions: unique_q[q.question_text] = q
    return list(unique_q.values())[:100]

def generate_9_q2(subject_id):
    questions = []
    # Similar to Q1 for 9th grade, expanding strings and replaces
    theory = [
        ("Matn tarkibidan bo'lak almashtirish (replace) metodini topings", "replace()", "swap()", "change()", "update()"),
        ("Satrdagi probellarni chap va o'ngdan olib tashlovchi metod", "strip()", "trim()", "clean()", "cut()"),
        ("Sikl (while) bilan break qanday ishlaydi?", "Tsiklni istalgan joyida majburiy to'xtatadi", "Tsiklni qaytadan boshlaydi", "Tsiklni o'tkazib yuboradi", "Cheksizlikka tushiradi")
    ]
    for _ in range(6): # 18
        for q_text, ans, w1, w2, w3 in theory:
            opts = [ans, w1, w2, w3]
            random.shuffle(opts)
            questions.append(Question(subject_id=subject_id, grade=9, quarter=2, question_text=q_text, option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3], correct_answer=['a','b','c','d'][opts.index(ans)]))
            
    for _ in range(150):
        t = random.choice(['replace', 'strip', 'split'])
        if t == 'replace':
            base = random.choice(["hello", "world", "tester", "python", "developer", "backend", "frontend"])
            wd = base + str(random.randint(10, 999))
            old_char = wd[random.randint(0, len(wd)-1)]
            new_char = random.choice('XYZW')
            ans = wd.replace(old_char, new_char)
            code = f"word = '{wd}'\nprint(word.replace('{old_char}', '{new_char}'))"
            opts = [ans, wd, new_char + wd, "Xatolik"]
        elif t == 'strip':
            b = random.choice(["salom", "python", "dastur", "maktab", "ilm"])
            wd = (" " * random.randint(1, 8)) + b + str(random.randint(10, 99)) + (" " * random.randint(1, 8))
            ans = wd.strip()
            code = f"word = '{wd}'\nprint(word.strip())"
            opts = [ans, wd, wd.replace(" ", ""), "Error"]
        else:
            mevalar = ["olma", "anor", "gilos", "shaftoli", "behi", "nok", "uzum", "anjir", "xurmo"]
            wd = ",".join(random.sample(mevalar, k=random.randint(2, 5)))
            ans = str(wd.split(','))
            code = f"mevalar = '{wd}'\nprint(mevalar.split(','))"
            opts = [ans, str(wd.split('a')), str(wd.strip()), str([wd])]
            
        opts = list(set(opts))
        while len(opts) < 4:
            if t == 'replace':
                opts.append(wd.replace(old_char, random.choice('ABC')))
            elif t == 'strip':
                opts.append(wd + "  ")
            else:
                opts.append(str(wd.split('o')))
            opts = list(set(opts))
        random.shuffle(opts)
        questions.append(Question(subject_id=subject_id, grade=9, quarter=2, question_text=f"Kod natijasini toping:\n```python\n{code}\n```", option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3], correct_answer=['a','b','c','d'][opts.index(ans)]))
        
    unique_q = {}
    for q in questions: unique_q[q.question_text] = q
    return list(unique_q.values())[:100]

def generate_9_q3(subject_id):
    questions = []
    theory = [
        ("To'plam (set) ning o'ziga xos xususiyati nima?", "Elementlar takrorlanmaydi va tartibsiz", "Elementlar tartib bilan joylashadi", "Faqat raqamlardan iborat", "Indeks orqali murojaat qilish mumkin"),
        ("Set yaratish uchun qaysi qavslardan foydalaniladi?", "{}", "[]", "()", "<>"),
        ("Python'da Modul nima?", "Qayta ishlatsa bo'ladigan funksiya va klasslarni o'zida jamlagan py fayli", "Faqat matnli obyekt", "Matematik funksiya yig'indisi", "Xatolik ro'yxati"),
        ("Boshqa modulni joriy kodga ulash buyrug'i?", "import", "include", "require", "using"),
        ("Bankomat (ATM) yoki shunga o'xshash mantiqiy jarayonlarda pin tekshirish oson yo'li nimadan iborat?", "if ... == pin:", "for i in pin:", "while True:", "import pin")
    ]
    for _ in range(15): # Scaled theory points
        q_text, ans, w1, w2, w3 = random.choice(theory)
        opts = [ans, w1, w2, w3]
        random.shuffle(opts)
        questions.append(Question(subject_id=subject_id, grade=9, quarter=3, question_text=q_text, option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3], correct_answer=['a','b','c','d'][opts.index(ans)]))

    # set theory logic
    for _ in range(50):
        lst = [random.randint(1,10) for _ in range(8)]
        ans = str(len(set(lst)))
        code = f"sonlar = {lst}\nprint(len(set(sonlar)))"
        opts = [ans, str(len(lst)), str(len(lst)-1), str(len(lst)+1)]
        opts = list(set(opts))
        while len(opts) < 4:
            opts.append(str(random.randint(1,15)))
            opts = list(set(opts))
        random.shuffle(opts)
        questions.append(Question(subject_id=subject_id, grade=9, quarter=3, question_text=f"To'plam (set) orqali yozilgan dastur natijasi nima bo'ladi?\n```python\n{code}\n```", option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3], correct_answer=['a','b','c','d'][opts.index(ans)]))

    # ATM Simulation (deep if logic)
    for _ in range(50):
        balance = random.randint(100, 500) * 1000
        withdrawal = random.randint(50, 600) * 1000
        expected = str(balance - withdrawal) if withdrawal <= balance else "Mablag' yetarli emas"
        code = f"balans = {balance}\nyechish = {withdrawal}\nif yechish <= balans:\n    balans -= yechish\n    print(balans)\nelse:\n    print(\"Mablag' yetarli emas\")"
        opts = [expected, str(balance), str(withdrawal), "0" if expected != "0" else "1"]
        opts = list(set(opts))
        while len(opts) < 4:
            opts.append(str(random.randint(10, 800) * 1000))
            opts = list(set(opts))
        random.shuffle(opts)
        questions.append(Question(subject_id=subject_id, grade=9, quarter=3, question_text=f"Bankomat logikasi:\nEkranga qanday natija chiqadi?\n```python\n{code}\n```", option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3], correct_answer=['a','b','c','d'][opts.index(expected)]))

    # ATM PIN logic (loops and if combination)
    for _ in range(45):
        pin = random.randint(1000, 9999)
        wrong = random.randint(1000, 9999)
        while wrong == pin: wrong = random.randint(1000, 9999)
        ans = "Xato parol"
        code = f"asl_pin = {pin}\nkiritilgan = {wrong}\nfor i in range(3):\n    if kiritilgan == asl_pin:\n        print('Kirish ruxsat etildi')\n        break\n    else:\n        kiritilgan += 1\nelse:\n    print('Xato parol')"
        opts = [ans, "Kirish ruxsat etildi", "Error", "None"]
        random.shuffle(opts)
        questions.append(Question(subject_id=subject_id, grade=9, quarter=3, question_text=f"For tsikli va else blokidan tashkil topgan dastur nimani bosmaga chiqaradi:\n```python\n{code}\n```", option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3], correct_answer=['a','b','c','d'][opts.index(ans)]))
        
    unique_q = {}
    for q in questions: unique_q[q.question_text] = q
    return list(unique_q.values())[:100]

def generate_9_q4(subject_id):
    questions = []
    theory = [
        ("Faylni o'qish reyimi qaysi kalit bilan ochiladi?", "r (read)", "w (write)", "a (append)", "x (execute)"),
        ("Faylga mavjud qatorlarga ziyon yetkazmasdan oxiridan yangi ma'lumot qo'shish qaysi orqali qilinadi?", "a (append)", "w (write)", "r (read)", "a+ (replace)"),
        ("Faylni ishlash yakunlangach avtomatik yopilishini kafolatlaydigan operator?", "with", "open", "close", "destroy"),
        ("Object-Oriented Programming (Ob'ektga yo'naltirilgan dasturlash) asosi?", "Maxsus andoza (Class)", "Tsikl (Loop)", "Mantiq (If/Else)", "Matematik tahlil"),
        ("Class ichidagi o'zgaruvchilarni va funksiyalarni boshqaruvchi (murojaat qiluvchi) parametr nomi odatda nima ataladi?", "self", "this", "my", "object"),
        ("Klasslardan yengi funksiya va xususiyatlarni osongina o'tkazish nima deyiladi?", "Inheritance (Meros xo'rlik)", "Encapsulation", "Polymorphism", "Abstraction"),
        ("Klassni o'zlashtirgan yangi maxsus ma'lumot qanday ataladi?", "Ob'ekt", "O'zgaruvchi", "Parametr", "Fayl")
    ]
    for _ in range(3): # 21 theory
        for q_text, ans, w1, w2, w3 in theory:
            opts = [ans, w1, w2, w3]
            random.shuffle(opts)
            questions.append(Question(subject_id=subject_id, grade=9, quarter=4, question_text=q_text, option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3], correct_answer=['a','b','c','d'][opts.index(ans)]))

    # OOP
    for _ in range(79):
        name = random.choice(["Gentra", "Cobalt", "Tracker", "Innova"])
        color = random.choice(["Oq", "Qora", "Sariq"])
        ans = f"{color} {name}"
        code = f"class Avto:\n    def __init__(self, rusum, rang):\n        self.rusum = rusum\n        self.rang = rang\n\n    def tasnif(self):\n        return f'{{self.rang}} {{self.rusum}}'\n\nmashina = Avto('{name}', '{color}')\nprint(mashina.tasnif())"
        
        wrong1 = f"Avto {name} {color}"
        wrong2 = f"{name} {color}"
        wrong3 = "Xatolik beradi"
        
        opts = [ans, wrong1, wrong2, wrong3]
        opts = list(set(opts))
        while len(opts) < 4:
            opts.append(f"Hech narsa chiqmaydi")
            opts = list(set(opts))
        random.shuffle(opts)
        questions.append(Question(subject_id=subject_id, grade=9, quarter=4, question_text=f"OOP (Obyektga yo'naltirilgan dasturlash) andozasi asosida yozilgan kod nima natija beradi?\n```python\n{code}\n```", option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3], correct_answer=['a','b','c','d'][opts.index(ans)]))

    return questions[:100]

def run_generator():
    print("Starting Perfect Overhauled Data Generator and Control Work Assigner for Grades 7, 8, 9...")
    with app.app_context():
        # Clean older control works explicitly for 7 8 9 python to avoid duplicates or issues
        # Actually, let's just wipe ALL old questions for Python 7,8,9 in the DB to have a pure fresh perfect DB.
        subject = get_or_create_subject("Python")
        subj_id = subject.id
        
        db.session.execute(db.text("DELETE FROM control_work_questions"))
        cw_count = ControlWork.query.filter_by(subject_id=subj_id).delete()
        q_count = Question.query.filter_by(subject_id=subj_id).delete()
        db.session.commit()
        print(f"Purged {cw_count} old ControlWorks, {q_count} Questions for clean slate.")

        q_list = []
        # Generate exactly 100 for each grade/quarter
        q_list.extend(generate_7_q1(subj_id))
        q_list.extend(generate_7_q2(subj_id))
        q_list.extend(generate_7_q3(subj_id))
        q_list.extend(generate_7_q4(subj_id))
        
        q_list.extend(generate_8_q1(subj_id))
        q_list.extend(generate_8_q2(subj_id))
        q_list.extend(generate_8_q3(subj_id))
        q_list.extend(generate_8_q4(subj_id))
        
        q_list.extend(generate_9_q1(subj_id))
        q_list.extend(generate_9_q2(subj_id))
        q_list.extend(generate_9_q3(subj_id))
        q_list.extend(generate_9_q4(subj_id))

        saved = add_questions_to_db(q_list)
        print(f"Saved {len(saved)} new perfect questions.")
        
        # 2. Assign to Control Works per Grade/Quarter
        print("Creating fresh Control Works mapping (100 questions per exam, cumulative)...")
        for grade in [7, 8, 9]:
            for quarter in [1, 2, 3, 4]:
                title = f"{grade}-sinf {quarter}-chorak Nazorat ishi"
                cw, assigned_count = create_control_work(
                    subject_id=subj_id, 
                    grade=grade, 
                    quarter=quarter, 
                    title=title, 
                    target_count=100
                )
                print(f"[{grade}-Grade Q{quarter}] Created/updated ControlWork '{title}' with {assigned_count} questions.")
                
        print("DONE. Process completed successfully.")

if __name__ == '__main__':
    run_generator()
