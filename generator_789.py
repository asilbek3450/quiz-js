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
        # ensure grades cover 7,8,9
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
        # Check if identical question already exists to prevent pure duplicates
        exists = Question.query.filter_by(
            subject_id=q.subject_id,
            grade=q.grade,
            quarter=q.quarter,
            question_text=q.question_text
        ).first()
        if not exists:
            db.session.add(q)
            db.session.flush() # flush to get an ID
            saved_questions.append(q)
        else:
            saved_questions.append(exists)
    db.session.commit()
    return saved_questions

def create_control_work(subject_id, grade, quarter, title, target_count=100):
    """
    Creates or re-rolls a Control Work for a specific grade and quarter, 
    pulling questions cumulatively up to that quarter.
    """
    # 1. Fetch available pool
    pool = Question.query.filter(
        Question.subject_id == subject_id,
        Question.grade == grade,
        Question.quarter <= quarter
    ).all()
    
    if scarcely := len(pool) < target_count:
        print(f"[{title}] WARNING: Pool only has {len(pool)} questions, targeting {target_count}. Using what's available.")
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
        cw.questions = [] # Clear existing mapping
        db.session.flush()
        
    cw.questions.extend(selected)
    db.session.commit()
    return cw, len(selected)

def generate_math_eval(subject_id, grade, quarter, num_questions=100):
    questions = []
    ops = [('+', '+'), ('-', '-'), ('*', '*'), ('/', '/'), ('//', '//'), ('%', '%'), ('**', '**')]
    for _ in range(num_questions):
        a = random.randint(2, 25)
        b = random.randint(2, 10) if random.choice([True, False]) else random.randint(2, 20)
        op_str, op_eval = random.choice(ops)
        
        # Keep ** exponents small
        if op_eval == '**':
            b = random.randint(2, 3)
            a = random.randint(2, 6)
            
        expr = f"{a} {op_eval} {b}"
        try:
            ans = eval(expr)
            if op_eval == '/':
                ans = round(ans, 2)
        except Exception:
            continue
            
        wrong1 = ans + random.randint(1, 5)
        wrong2 = ans - random.randint(1, 5)
        wrong3 = ans * 2
        
        opts = [str(ans), str(wrong1), str(wrong2), str(wrong3)]
        opts = list(set(opts))
        while len(opts) < 4:
            opts.append(str(ans + random.randint(10, 50)))
            opts = list(set(opts))
            
        random.shuffle(opts)
        
        q = Question(
            subject_id=subject_id,
            grade=grade,
            quarter=quarter,
            question_text=f"Python dasturida ushbu ifodaning natijasi nima bo'ladi?\n```python\nprint({a} {op_str} {b})\n```",
            option_a=opts[0],
            option_b=opts[1],
            option_c=opts[2],
            option_d=opts[3],
            correct_answer=['a', 'b', 'c', 'd'][opts.index(str(ans))]
        )
        questions.append(q)
    return questions

def generate_7_q1(subject_id):
    questions = []
    theory = [
        ("Dastur nima?", "Kompyuter uchun yozilgan buyruqlar ketma-ketligi", "Monitor", "Protsessor", "Axborot tashuvchi vosita"),
        ("Python dasturlash tilining asoschisi kim?", "Guido van Rossum", "Bill Gates", "Steve Jobs", "Mark Zuckerberg"),
        ("Pythonda ekranga ma'lumot chiqarish funksiyasi qaysi?", "print()", "output()", "show()", "display()"),
        ("Pythonda butun sonlar qaysi turga mansub?", "int", "float", "str", "bool"),
        ("Pythonda haqiqiy (kasr) sonlar qaysi turga mansub?", "float", "int", "str", "bool"),
        ("Pythonda matnli ma'lumotlar qaysi turga mansub?", "str", "int", "float", "bool"),
        ("O'zgaruvchi nima?", "Kompyuter xotirasida ma'lumot saqlash uchun ajratilgan joy", "Kompyuterning qattiq diski", "Ekranga chiqaruvchi funksiya", "Dasturlash tili turi"),
        ("Python qanday til hisoblanadi?", "Yuqori darajali dasturlash tili", "Quyi darajali dasturlash tili", "Matn muharriri", "Operatsion tizim")
    ]
    for _ in range(6): # theory clones -> 48
        for q_text, ans, w1, w2, w3 in theory:
            opts = [ans, w1, w2, w3]
            random.shuffle(opts)
            q = Question(
                subject_id=subject_id, grade=7, quarter=1,
                question_text=q_text,
                option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3],
                correct_answer=['a', 'b', 'c', 'd'][opts.index(ans)]
            )
            questions.append(q)
            
    # Add math evals
    questions.extend(generate_math_eval(subject_id, 7, 1, 80)) # 80 math evals
    return questions

def generate_7_q2(subject_id):
    questions = []
    theory = [
        ("Satr (str) nima?", "Belgilar ketma-ketligi", "Faqat raqamlardan iborat", "Butun sonlar", "Mantiqiy ifoda"),
        ("Satrning o'ziga xos uzunligini aniqlovchi funksiya qaysi?", "len()", "size()", "count()", "length()"),
        ("Satrdagi belgilarni kichik harflarga o'tkazuvchi metod qaysi?", "lower()", "upper()", "title()", "capitalize()"),
        ("Satrdagi belgilarni katta harflarga o'tkazuvchi metod qaysi?", "upper()", "lower()", "title()", "capitalize()"),
        ("Satr boshidagi va oxiridagi bo'sh joylarni olib tashlovchi metod qaysi?", "strip()", "trim()", "clear()", "remove()"),
        ("Matnli (str) o'zgaruvchini butun songa (int) aylantirish funksiyasi qaysi?", "int()", "str()", "float()", "bool()"),
    ]
    for _ in range(6): # 36 theory
        for q_text, ans, w1, w2, w3 in theory:
            opts = [ans, w1, w2, w3]
            random.shuffle(opts)
            q = Question(
                subject_id=subject_id, grade=7, quarter=2, question_text=q_text,
                option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3],
                correct_answer=['a', 'b', 'c', 'd'][opts.index(ans)]
            )
            questions.append(q)
            
    # Slicing questions
    words = ["Maktab", "Kitob", "Dastur", "Python", "Kompyuter", "Informatika", "Toshkent", "O'zbekiston"]
    for _ in range(50): # 50 specific index
        word = random.choice(words)
        idx = random.randint(0, len(word) - 1)
        ans = word[idx]
        opts = [ans, word[random.randint(0, len(word)-1)], word[-1], word[0]]
        opts = list(set(opts))
        while len(opts) < 4:
            opts.append(random.choice("abcdefghijklmnopqrstuvwxyz"))
            opts = list(set(opts))
        random.shuffle(opts)
        q = Question(
            subject_id=subject_id, grade=7, quarter=2,
            question_text=f"Natijani toping:\n```python\nword = '{word}'\nprint(word[{idx}])\n```",
            option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3],
            correct_answer=['a', 'b', 'c', 'd'][opts.index(ans)]
        )
        questions.append(q)
        
    for _ in range(50): # 50 slicing ranges
        word = random.choice(words)
        start = random.randint(0, len(word)-3)
        end = random.randint(start+1, len(word))
        ans = word[start:end]
        opts = [ans, word[start:end+1], word[start+1:end], word[0:end]]
        opts = list(set(opts))
        while len(opts) < 4:
            opts.append(word[random.randint(0,2):random.randint(3,len(word))])
            opts = list(set(opts))
            
        random.shuffle(opts)
        q = Question(
            subject_id=subject_id, grade=7, quarter=2,
            question_text=f"Natijani toping:\n```python\ns = '{word}'\nprint(s[{start}:{end}])\n```",
            option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3],
            correct_answer=['a', 'b', 'c', 'd'][opts.index(ans)]
        )
        questions.append(q)
        
    return questions

def generate_7_q3(subject_id):
    questions = []
    theory = [
        ("Python'da shart operatori qaysi so'z bilan boshlanadi?", "if", "for", "while", "else"),
        ("Shart bajarilmaganda ishlashi uchun qaysi kalit so'z ishlatiladi?", "else", "if", "elif", "then"),
        ("Bir nechta shartlarni ketma-ket tekshirish uchun qaysi kalit so'z ishlatiladi?", "elif", "else if", "if else", "then"),
        ("Ro'yxat (list) elementlari qanday qavslar ichida yoziladi?", "[ ]", "( )", "{ }", "< >"),
        ("Takrorlanuvchi jarayonlarni yaratish uchun nima ishlatiladi?", "Sikllar (loops)", "Shartlar", "O'zgaruvchilar", "Modullar"),
        ("Ma'lum marta takrorlanishi aniq bo'lgan sikl qaysi?", "for", "while", "if", "def"),
        ("Ro'yxatga yangi element qo'shish uchun qaysi metod ishlatiladi?", "append()", "add()", "insert()", "push()"),
        ("Tsiklni to'xtatish uchun qaysi operator ishlatiladi?", "break", "continue", "stop", "exit"),
        ("Tsiklning joriy qadamini o'tkazib yuborish uchun qaysi operator ishlatiladi?", "continue", "break", "pass", "skip"),
        ("While sikli qachon to'xtaydi?", "Shart noto'g'ri (False) bo'lganda", "Shart to'g'ri (True) bo'lganda", "Hech qachon", "Dastur ishga tushganda")
    ]
    for _ in range(2): # 20 theory
        for q_text, ans, w1, w2, w3 in theory:
            opts = [ans, w1, w2, w3]
            random.shuffle(opts)
            q = Question(
                subject_id=subject_id, grade=7, quarter=3, question_text=q_text,
                option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3],
                correct_answer=['a', 'b', 'c', 'd'][opts.index(ans)]
            )
            questions.append(q)
            
    # Conditional code snippets (30 questions)
    for _ in range(30):
        a = random.randint(5, 50)
        b = random.randint(5, 50)
        if a > b:
            ans = "A katta"
        elif a < b:
            ans = "B katta"
        else:
            ans = "Teng"
            
        code = f"a = {a}\nb = {b}\nif a > b:\n    print('A katta')\nelif a < b:\n    print('B katta')\nelse:\n    print('Teng')"
        opts = ["A katta", "B katta", "Teng", "Xatolik beradi"]
        random.shuffle(opts)
        q = Question(
            subject_id=subject_id, grade=7, quarter=3,
            question_text=f"Quyidagi dastur natijasi nima bo'ladi?\n```python\n{code}\n```",
            option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3],
            correct_answer=['a', 'b', 'c', 'd'][opts.index(ans)]
        )
        questions.append(q)

    # loop questions (50 questions)
    for _ in range(50):
        start = random.randint(1, 10)
        end = random.randint(11, 20)
        ans = str(list(range(start, end)))
        code = f"natija = []\nfor i in range({start}, {end}):\n    natija.append(i)\nprint(natija)"
        opts = [ans, str(list(range(start, end+1))), str(list(range(start+1, end))), str(list(range(start+1, end+1)))]
        opts = list(set(opts))
        while len(opts) < 4:
            opts.append(f"[{random.randint(1,10)}]")
            opts = list(set(opts))
            
        random.shuffle(opts)
        q = Question(
            subject_id=subject_id, grade=7, quarter=3,
            question_text=f"Dastur nima natija chiqaradi?\n```python\n{code}\n```",
            option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3],
            correct_answer=['a', 'b', 'c', 'd'][opts.index(ans)]
        )
        questions.append(q)
        
    return questions

def generate_7_q4(subject_id):
    # Specialized Q4 questions expanding on the entirety
    questions = []
    
    for _ in range(60):
        n = random.randint(3, 10)
        ans = str(sum(range(n)))
        code = f"s = 0\ni = 0\nwhile i < {n}:\n    s += i\n    i += 1\nprint(s)"
        wrong1 = str(sum(range(n+1)))
        wrong2 = str(sum(range(n-1)))
        wrong3 = str(sum(range(n)) + 2)
        opts = [ans, wrong1, wrong2, wrong3]
        opts = list(set(opts))
        while len(opts) < 4:
            opts.append(str(random.randint(10,50)))
            opts = list(set(opts))
        random.shuffle(opts)
        q = Question(
            subject_id=subject_id, grade=7, quarter=4,
            question_text=f"Natijani toping (while tsikli bilan ishlash):\n```python\n{code}\n```",
            option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3],
            correct_answer=['a', 'b', 'c', 'd'][opts.index(ans)]
        )
        questions.append(q)
        
    for _ in range(40):
        # Mix string methods
        method = random.choice([('upper', str.upper), ('lower', str.lower)])
        basestr = random.choice(["O'ZBEK", "dastur", "pyThOn", "iNFoRmAtika"])
        ans = method[1](basestr)
        code = f"x = '{basestr}'\nprint(x.{method[0]}())"
        
        opts = [ans, basestr, basestr.capitalize(), method[1](basestr + " ")]
        opts = list(set(opts))
        while len(opts) < 4:
            opts.append("Xatolik bo'ladi")
            opts = list(set(opts))
        random.shuffle(opts)
        q = Question(
            subject_id=subject_id, grade=7, quarter=4,
            question_text=f"Kod natijasi qanday bo'ladi?\n```python\n{code}\n```",
            option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3],
            correct_answer=['a', 'b', 'c', 'd'][opts.index(ans)]
        )
        questions.append(q)
        
    return questions

def generate_8_q1(subject_id):
    questions = []
    theory = [
        ("if, elif va else nima uchun ishlatiladi?", "Shartlarni tekshirish uchun", "Sikl yaratish uchun", "Ma'lumot kiritish uchun", "Funksiya e'lon qilish uchun"),
        ("Sikllarda qadamni belgilash uchun `range` funksiyasi qanday yoziladi?", "range(start, stop, step)", "range(step, start, stop)", "range(stop, start, step)", "range(start, step, stop)"),
        ("Takrorlanishlar soni nom\'alum bo\'lganda qaysi sikl qulay?", "while", "for", "if", "switch"),
        ("Qaysi operator faqat to'g'ri (True) qiymat qaytganda bajariladi?", "if", "else", "break", "continue"),
        ("`input()` funksiyasi qanday turdagi qiymat qaytaradi?", "str", "int", "float", "bool")
    ]
    for _ in range(8): #  40 theory
        for q_text, ans, w1, w2, w3 in theory:
            opts = [ans, w1, w2, w3]
            random.shuffle(opts)
            q = Question(
                subject_id=subject_id, grade=8, quarter=1, question_text=q_text,
                option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3],
                correct_answer=['a', 'b', 'c', 'd'][opts.index(ans)]
            )
            questions.append(q)
            
    # Some logic questions
    for _ in range(80):
        start = random.randint(1, 10)
        stop = random.randint(15, 25)
        step = random.randint(2, 5)
        ans = str(list(range(start, stop, step)))
        code = f"natija = []\nfor i in range({start}, {stop}, {step}):\n    natija.append(i)\nprint(natija)"
        opts = [ans, str(list(range(start, stop, step+1))), str(list(range(start+1, stop, step))), str(list(range(start, stop+step, step)))]
        opts = list(set(opts))
        while len(opts) < 4:
            opts.append(f"[{random.randint(1,10)}]")
            opts = list(set(opts))
        random.shuffle(opts)
        q = Question(
            subject_id=subject_id, grade=8, quarter=1,
            question_text=f"Quyidagi kod natijasi nima?\n```python\n{code}\n```",
            option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3],
            correct_answer=['a', 'b', 'c', 'd'][opts.index(ans)]
        )
        questions.append(q)
        
    return questions

def generate_8_q2(subject_id):
    questions = []
    theory = [
        ("List va Tuple o'rtasidagi asosiy farq nima?", "List o'zgaruvchan (mutable), Tuple o'zgarmas (immutable)", "List o'zgarmas, Tuple o'zgaruvchan", "Hech qanday farqi yo'q", "List qavslarsiz yoziladi"),
        ("Lug'at (dictionary) qaysi qavslar ichida yoziladi?", "{}", "[]", "()", "<>"),
        ("Ro'yxat (list) ohiriga element qo'shuvchi metod qaysi?", "append()", "add()", "insert()", "extend()"),
        ("Listdan berilgan elementni o'chiruvchi metod qaysi?", "remove()", "pop()", "delete()", "clear()"),
        ("Listdagi elementlarni o'sish tartibida saralovchi metod qaysi?", "sort()", "order()", "sorted()", "arrange()"),
        ("Kortej (Tuple) qanday qavslar ichida yoziladi?", "()", "[]", "{}", "<>"),
        ("Dictionary da malumotlar qanday tuzilishda saqlanadi?", "Kalit va Qiymat (Key: Value)", "Faqat qiymatlar", "Indekslangan ro'yxat", "To'plam"),
        ("Listni teskari o'girish metodi qaysi?", "reverse()", "inverse()", "flip()", "back()")
    ]
    for _ in range(6): # 48
        for q_text, ans, w1, w2, w3 in theory:
            opts = [ans, w1, w2, w3]
            random.shuffle(opts)
            q = Question(
                subject_id=subject_id, grade=8, quarter=2, question_text=q_text,
                option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3],
                correct_answer=['a', 'b', 'c', 'd'][opts.index(ans)]
            )
            questions.append(q)
            
    # List and Dict questions
    for _ in range(40):
        lst = [random.randint(1, 15) for i in range(4)]
        elem = random.randint(16, 25)
        ans = str(lst + [elem])
        code = f"nums = {lst}\nnums.append({elem})\nprint(nums)"
        opts = [ans, str([elem] + lst), str(lst), "Xatolik bo'ladi"]
        random.shuffle(opts)
        q = Question(
            subject_id=subject_id, grade=8, quarter=2,
            question_text=f"Dastur natijasini toping (List):\n```python\n{code}\n```",
            option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3],
            correct_answer=['a', 'b', 'c', 'd'][opts.index(ans)]
        )
        questions.append(q)
        
    for _ in range(50):
        keys = ['name', 'age', 'job', 'city', 'country']
        k1, k2 = random.sample(keys, 2)
        v1, v2 = random.randint(1, 40), random.randint(41, 100)
        ans = str(v2)
        code = f"data = {{'{k1}': {v1}, '{k2}': {v2}}}\nprint(data['{k2}'])"
        opts = [ans, str(v1), f"'{k2}'", "KeyError: Topilmadi"]
        random.shuffle(opts)
        q = Question(
            subject_id=subject_id, grade=8, quarter=2,
            question_text=f"Dastur nimani ekranga chiqaradi (Dictionary)?\n```python\n{code}\n```",
            option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3],
            correct_answer=['a', 'b', 'c', 'd'][opts.index(ans)]
        )
        questions.append(q)
        
    return questions

def generate_8_q3(subject_id):
    questions = []
    theory = [
        ("Funksiya yaratish uchun qaysi kalit so'z ishlatiladi?", "def", "func", "function", "create"),
        ("Funksiya natija qaytarishi uchun qaysi so'z ishlatiladi?", "return", "output", "print", "yield"),
        ("Qanday qilib istalgancha o'zgaruvchi (arguments) qabul qiluvchi funksiya yaratiladi?", "*args", "&args", "$args", "args[]"),
        ("Qanday qilib istalgancha kalit-qiymatli o'zgaruvchilar qabul qiluvchi funksiya yaratiladi?", "**kwargs", "&&kwargs", "*kwargs", "kwargs()"),
        ("Satrni ma'lum bir belgi bo'yicha ajratib listga o'zlashtiruvchi metod qaysi?", "split()", "join()", "break()", "slice()"),
        ("Listdagi matnlarni biriktirib bitta satrga aylantiruvchi metod qaysi?", "join()", "concat()", "merge()", "split()"),
        ("f-string yordamida o'zgaruvchini matn ichida qanday ishlatamiz?", "f'Matn {o\'zgaruvchi}'", "f'Matn + o\'zgaruvchi'", "'Matn' + o'zgaruvchi", "f'Matn (o\'zgaruvchi)'")
    ]
    for _ in range(3): # 21 theory
        for q_text, ans, w1, w2, w3 in theory:
            opts = [ans, w1, w2, w3]
            random.shuffle(opts)
            q = Question(
                subject_id=subject_id, grade=8, quarter=3, question_text=q_text,
                option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3],
                correct_answer=['a', 'b', 'c', 'd'][opts.index(ans)]
            )
            questions.append(q)
            
    # Function tracing questions (39)
    for _ in range(39):
        a = random.randint(5, 50)
        b = random.randint(15, 60)
        ans = str(a + b)
        code = f"def qushish(x, y):\n    return x + y\n\nprint(qushish({a}, {b}))"
        opts = [ans, str(a*b), str(b-a), "Xatolik"]
        random.shuffle(opts)
        q = Question(
            subject_id=subject_id, grade=8, quarter=3,
            question_text=f"Funksiya natijasi qanday bo'ladi?\n```python\n{code}\n```",
            option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3],
            correct_answer=['a', 'b', 'c', 'd'][opts.index(ans)]
        )
        questions.append(q)
        
    # Comprehensions (40)
    for _ in range(40):
        n = random.randint(2, 6)
        ans = str([i*i for i in range(1, n+1)])
        code = f"sonlar = [i*i for i in range(1, {n+1})]\nprint(sonlar)"
        opts = [ans, str([i*i for i in range(0, n)]), str([i for i in range(1, n+1)]), str([i*2 for i in range(1, n+1)])]
        opts = list(set(opts))
        while len(opts) < 4:
            opts.append(f"[{random.randint(1,10)}]")
            opts = list(set(opts))
        random.shuffle(opts)
        q = Question(
            subject_id=subject_id, grade=8, quarter=3,
            question_text=f"List comprehension natijasini toping:\n```python\n{code}\n```",
            option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3],
            correct_answer=['a', 'b', 'c', 'd'][opts.index(ans)]
        )
        questions.append(q)

    return questions

def generate_8_q4(subject_id):
    questions = []
    
    for _ in range(100):
        val = random.randint(10, 50)
        ans = str(val * 2)
        code = f"def ikkilangan(a):\n    return a * 2\n\nprint(ikkilangan({val}))"
        opts = [ans, str(val), str(val*3), "None"]
        opts = list(set(opts))
        while len(opts) < 4:
            opts.append(str(random.randint(60, 100)))
            opts = list(set(opts))
        random.shuffle(opts)
        q = Question(
            subject_id=subject_id, grade=8, quarter=4,
            question_text=f"Natijani toping:\n```python\n{code}\n```",
            option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3],
            correct_answer=['a', 'b', 'c', 'd'][opts.index(ans)]
        )
        questions.append(q)
    return questions

def generate_9_q1(subject_id):
    questions = []
    theory = [
        ("if-elif-else tuzilmasida nechta 'elif' qatnashishi mumkin?", "Istalgancha", "Faqat 1 ta", "Faqat 2 ta", "elif ishlatilmaydi"),
        ("Sikl ishini butunlay to'xtatuvchi kalit so'z:", "break", "continue", "stop", "exit"),
        ("Matndagi barcha elementlarni ro'yxatga (list) o'tkazish funktsiyasi:", "list()", "array()", "split()", "tuple()"),
        ("Stringdagi belgini indeks bo'yicha o'zgartirib bo'ladimi?", "Yo'q, string xossasi o'zgarmas (immutable)", "Ha, bo'ladi", "Faqat oxirgi belgini", "Faqat raqamlarni"),
        ("Matn (str) elementlarini sanash qaysi metod bilan bajariladi?", "count()", "len()", "size()", "number()")
    ]
    for _ in range(10): # 50 theory
        for q_text, ans, w1, w2, w3 in theory:
            opts = [ans, w1, w2, w3]
            random.shuffle(opts)
            q = Question(
                subject_id=subject_id, grade=9, quarter=1, question_text=q_text,
                option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3],
                correct_answer=['a', 'b', 'c', 'd'][opts.index(ans)]
            )
            questions.append(q)
            
    for _ in range(60):
        word = random.choice(["O'zbekiston", "Toshkent", "Python", "Dasturlash", "Maktab", "Samarqand"])
        char = random.choice(word)
        ans = str(word.count(char))
        code = f"matn = '{word}'\nprint(matn.count('{char}'))"
        opts = [ans, "1", "2", "0"]
        opts = list(set(opts))
        while len(opts) < 4:
            opts.append(str(random.randint(3,10)))
            opts = list(set(opts))
        random.shuffle(opts)
        q = Question(
            subject_id=subject_id, grade=9, quarter=1,
            question_text=f"Dastur nimani chop etadi?\n```python\n{code}\n```",
            option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3],
            correct_answer=['a', 'b', 'c', 'd'][opts.index(ans)]
        )
        questions.append(q)
    return questions

def generate_9_q2(subject_id):
    # Same curriculum practically
    questions = []
    theory = [
        ("Satrdagi ifodalarni almashtiruvchi metod qaysi?", "replace()", "swap()", "change()", "update()"),
        ("Funksiya nima?", "Muayyan vazifani bajaruvchi nomlangan kod bloki", "O'zgaruvchi turi", "Siklning bir qismi", "Malumotlar bazasi"),
        ("Sikl ichidagi break vazifasi nima?", "Sikldan butunlay chiqib ketadi", "Keyingi qadamga o'tadi", "Dasturni to'xtatadi", "Hech narsa"),
    ]
    for _ in range(15): # 45
        for q_text, ans, w1, w2, w3 in theory:
            opts = [ans, w1, w2, w3]
            random.shuffle(opts)
            q = Question(
                subject_id=subject_id, grade=9, quarter=2, question_text=q_text,
                option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3],
                correct_answer=['a', 'b', 'c', 'd'][opts.index(ans)]
            )
            questions.append(q)
            
    for _ in range(60):
        wd = random.choice(["hello", "world", "tester", "python", "developer"])
        old_char = wd[random.randint(0, len(wd)-1)]
        new_char = 'X'
        ans = wd.replace(old_char, new_char)
        code = f"word = '{wd}'\nprint(word.replace('{old_char}', '{new_char}'))"
        opts = [ans, wd, new_char + wd, "Xatolik"]
        opts = list(set(opts))
        while len(opts) < 4:
            opts.append(wd.replace(old_char, 'Y'))
            opts = list(set(opts))
        random.shuffle(opts)
        q = Question(
            subject_id=subject_id, grade=9, quarter=2,
            question_text=f"Natijani toping:\n```python\n{code}\n```",
            option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3],
            correct_answer=['a', 'b', 'c', 'd'][opts.index(ans)]
        )
        questions.append(q)
    return questions

def generate_9_q3(subject_id):
    questions = []
    theory = [
        ("To'plam (set) ning o'ziga xos xususiyati nima?", "Elementlar takrorlanmaydi va tartibsiz", "Elementlar tartib bilan joylashadi", "Faqat raqamlardan iborat", "Indeks orqali murojaat qilish mumkin"),
        ("To'plam (set) yaratish qavslari qaysi?", "{}", "[]", "()", "<>"),
        ("Modul nima?", "Qayta ishlatsa bo'ladigan Python fayli (.py)", "O'zgaruvchi turi", "Operator", "Xatolik turi"),
        ("Boshqa modulni joriy faylga chaqirish uchun qaysi so'z ishlatiladi?", "import", "include", "require", "using"),
        ("O'zgaruvchan, lekin takrorlanmaydigan malumot turlari to'plami?", "set", "list", "tuple", "dict"),
        ("Istalgan miqdordagi pozitsion argumentlarni funksiyaga uzatish uchun?", "*args", "**kwargs", "args[]", "params"),
        ("Istalgan miqdordagi kalitli (keyword) argumentlarni funksiyaga uzatish uchun?", "**kwargs", "*args", "kwargs{}", "params")
    ]
    for _ in range(3): # 21 theory
        for q_text, ans, w1, w2, w3 in theory:
            opts = [ans, w1, w2, w3]
            random.shuffle(opts)
            q = Question(
                subject_id=subject_id, grade=9, quarter=3, question_text=q_text,
                option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3],
                correct_answer=['a', 'b', 'c', 'd'][opts.index(ans)]
            )
            questions.append(q)
            
    # Sets and Modules (40)
    for _ in range(40):
        lst = [random.randint(1,8) for _ in range(8)]
        ans = str(len(set(lst)))
        code = f"sonlar = {lst}\nprint(len(set(sonlar)))"
        opts = [ans, str(len(lst)), "1", "0"]
        opts = list(set(opts))
        while len(opts) < 4:
            opts.append(str(random.randint(2,8)))
            opts = list(set(opts))
        random.shuffle(opts)
        q = Question(
            subject_id=subject_id, grade=9, quarter=3,
            question_text=f"Quyidagi kod natijasi nima bo'ladi (Set)?\n```python\n{code}\n```",
            option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3],
            correct_answer=['a', 'b', 'c', 'd'][opts.index(ans)]
        )
        questions.append(q)
        
    # *args questions (39)
    for _ in range(39):
        a, b, c = random.randint(1,15), random.randint(2,15), random.randint(3,15)
        ans = str(a+b+c)
        code = f"def yigindi(*args):\n    return sum(args)\n\nprint(yigindi({a}, {b}, {c}))"
        opts = [ans, str(a*b*c), "TypeError", str(a+b)]
        opts = list(set(opts))
        while len(opts) < 4:
            opts.append(str(random.randint(10, 60)))
            opts = list(set(opts))
        random.shuffle(opts)
        q = Question(
            subject_id=subject_id, grade=9, quarter=3,
            question_text=f"Funksiya natijasini toping (*args):\n```python\n{code}\n```",
            option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3],
            correct_answer=['a', 'b', 'c', 'd'][opts.index(ans)]
        )
        questions.append(q)

    return questions

def generate_9_q4(subject_id):
    questions = []
    theory = [
        ("Faylni o'qish uchun qaysi rejimda ochish kerak?", "'r'", "'w'", "'a'", "'x'"),
        ("Faylga yangi ma'lumotni oxiridan qo'shish uchun qaysi rejim ishlatiladi?", "'a'", "'w'", "'r'", "'w+'"),
        ("Faylni avtomatik yopishni kafolatlovchi operator qaysi?", "with", "open", "close", "try"),
        ("OOP kengaytmasi nima?", "Object-Oriented Programming", "Oriented-Object Python", "Object-Outline Protocol", "Out-Of-Place"),
        ("Klassdan yaratilgan yangi nusxa (instansiya) nima deyiladi?", "Obyekt", "Metod", "Modul", "Funksiya"),
        ("Klass ichidagi funksiya nima deb ataladi?", "Metod", "Obyekt", "Xususiyat", "Klass"),
        ("Boshqa klassning xususiyat va metodlarini o'zlashtirish nima deyiladi?", "Meros xorlik (Inheritance)", "Enkapsulyatsiya", "Polimorfizm", "Abstraksiya"),
        ("Klassni initsializatsiya qiluvchi (konstruktor) maxsus metod:", "__init__()", "__main__()", "__start__()", "__class__()")
    ]
    for _ in range(8): # 64
        for q_text, ans, w1, w2, w3 in theory:
            opts = [ans, w1, w2, w3]
            random.shuffle(opts)
            q = Question(
                subject_id=subject_id, grade=9, quarter=4, question_text=q_text,
                option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3],
                correct_answer=['a', 'b', 'c', 'd'][opts.index(ans)]
            )
            questions.append(q)
            
    # OOP tracking
    for _ in range(50):
        name = random.choice(["Ali", "Vali", "Hasan", "Husan", "Sardor", "Rustam"])
        age = random.randint(15, 25)
        ans = f"{name} {age} yoshda"
        code = f"class Oquvchi:\n    def __init__(self, ism, yosh):\n        self.ism = ism\n        self.yosh = yosh\n\n    def malumot(self):\n        return f'{{self.ism}} {{self.yosh}} yoshda'\n\noq = Oquvchi('{name}', {age})\nprint(oq.malumot())"
        
        wrong1 = f"Oquvchi {name} {age}"
        wrong2 = f"{age} yoshda {name}"
        wrong3 = "Xatolik beradi"
        
        opts = [ans, wrong1, wrong2, wrong3]
        opts = list(set(opts))
        while len(opts) < 4:
            opts.append(f"{name}ni ma'lumoti yuq")
            opts = list(set(opts))
        random.shuffle(opts)
        q = Question(
            subject_id=subject_id, grade=9, quarter=4,
            question_text=f"Quyidagi OOP dastur natijasi nima?\n```python\n{code}\n```",
            option_a=opts[0], option_b=opts[1], option_c=opts[2], option_d=opts[3],
            correct_answer=['a', 'b', 'c', 'd'][opts.index(ans)]
        )
        questions.append(q)
            
    return questions


def run_generator():
    print("Starting Data Generator and Control Work Assigner for Grades 7, 8, 9...")
    with app.app_context():
        # Ensure 'Python' subject for this requirement
        subject = get_or_create_subject("Python")
        subj_id = subject.id
        print(f"Subject 'Python' ID: {subj_id}")
        
        # 1. Generate Massive Pool of Questions
        # 7th Grade
        add_questions_to_db(generate_7_q1(subj_id))
        add_questions_to_db(generate_7_q2(subj_id))
        add_questions_to_db(generate_7_q3(subj_id))
        add_questions_to_db(generate_7_q4(subj_id))
        
        # 8th Grade
        add_questions_to_db(generate_8_q1(subj_id))
        add_questions_to_db(generate_8_q2(subj_id))
        add_questions_to_db(generate_8_q3(subj_id))
        add_questions_to_db(generate_8_q4(subj_id))
        
        # 9th Grade
        add_questions_to_db(generate_9_q1(subj_id))
        add_questions_to_db(generate_9_q2(subj_id))
        add_questions_to_db(generate_9_q3(subj_id))
        add_questions_to_db(generate_9_q4(subj_id))
        
        # 2. Assign to Control Works per Grade/Quarter
        print("Creating Control Works mapping (100 questions per exam, cumulative)...")
        for grade in [7, 8, 9]:
            for quarter in [1, 2, 3, 4]:
                title = f"{grade}-sinf {quarter}-chorak Nazorat ishi" # Format: 7-sinf 1-chorak Nazorat ishi
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
