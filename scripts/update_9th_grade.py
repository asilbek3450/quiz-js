import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from models import Question, Subject
from deep_translator import GoogleTranslator
import random

def auto_translate(text, target):
    try:
        return GoogleTranslator(source='auto', target=target).translate(text)
    except:
        return text

# Global set to track uniqueness
SEEN_QUESTIONS = set()

def get_or_create_subject():
    subject = Subject.query.filter_by(name='Python').first()
    if not subject:
        subject = Subject(name='Python', name_ru='Питон', name_en='Python', grades='7,8,9')
        db.session.add(subject)
        db.session.commit()
    return subject

def add_question_safe(questions_list, subject_id, grade, quarter, text, opts, correct):
    global SEEN_QUESTIONS
    
    if len(set(opts)) < 4:
        while len(opts) < 4:
            opts.append(f"Variant {len(opts)+1}")
    
    final_opts = list(set(opts))[:4]
    if len(final_opts) < 4:
        return False
    
    if correct not in final_opts:
        final_opts[0] = correct
        
    random.shuffle(final_opts)
    
    try:
        correct_idx = final_opts.index(correct)
    except ValueError:
        return False
        
    correct_char = ['A', 'B', 'C', 'D'][correct_idx]
    
    if text in SEEN_QUESTIONS:
        return False
    SEEN_QUESTIONS.add(text)
    
    q = Question(
        subject_id=subject_id,
        grade=grade,
        quarter=quarter,
        question_text=text,
        option_a=str(final_opts[0]),
        option_b=str(final_opts[1]),
        option_c=str(final_opts[2]),
        option_d=str(final_opts[3]),
        correct_answer=correct_char
    )
    questions_list.append(q)
    return True

# ================= DARS 1: Kirish. 8-sinfni takrorlash =================

def gen_basic_print():
    texts = [
        "Salom Dunyo!",
        "Python dasturlash",
        "9-sinf",
        "Informatika",
        "Hello World"
    ]
    text = random.choice(texts)
    code = f'print("{text}")'
    ans = text
    wrongs = [f"print({text})", f"'{text}'", "Hech narsa", "Xatolik"]
    return code, [ans] + wrongs, ans

def gen_variable_types():
    types = [
        ("x = 5", "int", "butun son"),
        ("y = 3.14", "float", "haqiqiy son"),
        ("name = 'Ali'", "str", "matn"),
        ("is_true = True", "bool", "mantiqiy qiymat"),
        ("lst = [1,2,3]", "list", "ro'yxat")
    ]
    code, py_type, uz_type = random.choice(types)
    if random.random() > 0.5:
        q = f"Quyidagi kodda 'x' o'zgaruvchisi qanday turga ega?\n\n```python\n{code}\n```"
        ans = py_type
        wrongs = ["str", "float", "bool", "list"]
    else:
        q = f"Quyidagi kodda 'y' o'zgaruvchisi qanday turdagi ma'lumot saqlaydi?\n\n```python\n{code}\n```"
        ans = uz_type
        wrongs = ["butun son", "matn", "ro'yxat", "lug'at"]
    return q, [ans] + wrongs, ans

def gen_input_basic():
    num = random.randint(10, 50)
    code = f"age = input('Yoshingiz: ')\nprint('Siz', age, 'yoshdasiz')"
    ans = f"Foydalanuvchi kiritgan matn bilan 'Siz [matn] yoshdasiz' chiqadi"
    wrongs = [
        f"Faqat {num} chiqadi",
        "Xatolik beradi",
        "'Yoshingiz: ' matni chiqadi",
        "Hech narsa chiqmaydi"
    ]
    return code, [ans] + wrongs, ans

def gen_if_statement():
    a = random.randint(1, 20)
    b = random.randint(1, 20)
    operator = random.choice(['>', '<', '==', '!='])
    
    if operator == '>':
        result = a > b
    elif operator == '<':
        result = a < b
    elif operator == '==':
        result = a == b
    else:
        result = a != b
        
    code = f"a = {a}\nb = {b}\nif a {operator} b:\n    print('Ha')\nelse:\n    print('Yo'q')"
    ans = "Ha" if result else "Yo'q"
    wrongs = ["Yo'q", "Ha", "Xatolik", "Hech narsa"]
    return code, [ans] + wrongs, ans

def gen_arithmetic_ops():
    a = random.randint(10, 30)
    b = random.randint(2, 10)
    ops = [
        ('+', a + b),
        ('-', a - b),
        ('*', a * b),
        ('/', a / b),
        ('//', a // b),
        ('%', a % b),
        ('**', a ** 2)
    ]
    op, result = random.choice(ops)
    code = f"x = {a}\ny = {b}\nprint(x {op} y)"
    
    if isinstance(result, float):
        result = round(result, 2)
        
    wrongs = [result + random.randint(1,5), result - random.randint(1,5), a, b]
    return code, [result] + wrongs, result

# ================= DARS 2: Shart operatorlari va Sikl operatorlari =================

def gen_if_elif_else():
    score = random.randint(0, 100)
    code = f"ball = {score}\nif ball >= 90:\n    print('A')\nelif ball >= 80:\n    print('B')\nelif ball >= 70:\n    print('C')\nelse:\n    print('D')"
    
    if score >= 90:
        ans = "A"
    elif score >= 80:
        ans = "B"
    elif score >= 70:
        ans = "C"
    else:
        ans = "D"
        
    wrongs = ["A", "B", "C", "D"]
    wrongs.remove(ans)
    return code, [ans] + wrongs, ans

def gen_for_range():
    start = random.randint(0, 5)
    stop = start + random.randint(3, 7)
    step = random.choice([1, 2, 3])
    
    code = f"for i in range({start}, {stop}, {step}):\n    print(i, end=' ')"
    
    result = list(range(start, stop, step))
    ans = " ".join(str(x) for x in result)
    wrongs = [
        " ".join(str(x) for x in range(stop)),
        " ".join(str(x) for x in range(start, stop)),
        " ".join(str(x) for x in range(0, stop, step)),
        "Hech narsa"
    ]
    return code, [ans] + wrongs, ans

def gen_while_loop():
    n = random.randint(3, 8)
    code = f"i = 1\nwhile i <= {n}:\n    print(i)\n    i += 1"
    ans = f"1 dan {n} gacha sonlar (har biri alohida qatorda)"
    wrongs = [
        f"1 dan {n-1} gacha sonlar",
        f"0 dan {n} gacha sonlar",
        f"Cheksiz sikl",
        f"Hech narsa"
    ]
    return code, [ans] + wrongs, ans

def gen_nested_loops():
    n = random.randint(2, 4)
    m = random.randint(2, 4)
    code = f"for i in range({n}):\n    for j in range({m}):\n        print(i, j)"
    
    results = []
    for i in range(n):
        for j in range(m):
            results.append(f"{i} {j}")
    
    ans = "\\n".join(results)
    wrongs = [
        "\\n".join(f"{i} {i}" for i in range(n)),
        "\\n".join(f"{j} {j}" for j in range(m)),
        "\\n".join(f"{i} {j}" for i in range(m) for j in range(n)),
        "Xatolik"
    ]
    return code, [ans] + wrongs, ans

def gen_break_continue():
    code = "for i in range(10):\n    if i == 5:\n        break\n    print(i, end=' ')"
    ans = "0 1 2 3 4"
    wrongs = ["0 1 2 3 4 5", "1 2 3 4 5", "0 1 2 3 4 5 6 7 8 9", "5"]
    return code, [ans] + wrongs, ans

# ================= DARS 3: String va uning metodlari =================

def gen_string_indexing():
    words = ["PYTHON", "DASTURLASH", "INFORMATIKA", "KOMPYUTER", "ALGORITM"]
    word = random.choice(words)
    idx = random.randint(0, len(word)-1)
    code = f"s = '{word}'\nprint(s[{idx}])"
    ans = word[idx]
    wrongs = [word[idx-1] if idx > 0 else word[1], 
              word[idx+1] if idx < len(word)-1 else word[-2],
              str(len(word)), "Xatolik"]
    return code, [ans] + wrongs, ans

def gen_string_slicing():
    words = ["PYTHON", "PROGRAMMING", "COMPUTER", "SCIENCE", "ALGORITHM"]
    word = random.choice(words)
    start = random.randint(0, 2)
    end = random.randint(start+2, len(word))
    step = random.choice([1, 2])
    
    code = f"s = '{word}'\nprint(s[{start}:{end}:{step}])"
    ans = word[start:end:step]
    wrongs = [
        word[start:end],
        word[start+1:end+1] if end < len(word) else word[start:end-1],
        word[::-1],
        "Xatolik"
    ]
    return code, [ans] + wrongs, ans

def gen_string_methods():
    word = random.choice(["python", "PYTHON", "Python", "  python  ", "python rocks"])
    methods = [
        (".upper()", word.upper()),
        (".lower()", word.lower()),
        (".capitalize()", word.capitalize()),
        (".strip()", word.strip()),
        (".replace('o', 'a')", word.replace('o', 'a')),
        (".count('t')", word.count('t')),
        (".find('y')", word.find('y')),
    ]
    
    op_name, op_func = random.choice(methods)
    
    if op_name == '.replace("o", "a")':
        code = f"s = '{word}'\nprint(s.replace('o', 'a'))"
        ans = word.replace('o', 'a')
    elif op_name in ['.count("t")', '.find("y")']:
        char = op_name[-3]
        code = f"s = '{word}'\nprint(s{op_name})"
        ans = str(op_func)
    else:
        code = f"s = '{word}'\nprint(s{op_name})"
        ans = op_func
    
    if isinstance(ans, str):
        ans = f"'{ans}'"
    
    wrongs = [f"'{word}'", f"'{word.upper() if op_name != '.upper()' else word.lower()}'", "None", "Xatolik"]
    return code, [ans] + wrongs, ans

def gen_string_concatenation():
    str1 = random.choice(["Hello", "Python", "Dastur", "Kod"])
    str2 = random.choice(["World", "dasturlash", "yozish", "ishlash"])
    code = f"a = '{str1}'\nb = '{str2}'\nprint(a + ' ' + b)"
    ans = f"{str1} {str2}"
    wrongs = [
        f"{str1}{str2}",
        f"{str2} {str1}",
        f"'{str1}' '{str2}'",
        "Xatolik"
    ]
    return code, [ans] + wrongs, ans

# ================= DARS 4: Ro'yhatlar (list, tuple, set, dict) =================

def gen_list_basic():
    lst = [random.randint(1, 20) for _ in range(5)]
    idx = random.randint(0, len(lst)-1)
    code = f"numbers = {lst}\nprint(numbers[{idx}])"
    ans = lst[idx]
    wrongs = [
        lst[idx-1] if idx > 0 else lst[-1],
        lst[idx+1] if idx < len(lst)-1 else lst[0],
        len(lst),
        "Xatolik"
    ]
    return code, [ans] + wrongs, ans

def gen_list_methods():
    lst = [random.randint(1, 10) for _ in range(4)]
    methods = [
        (".append(99)", lst + [99], "Ro'yxat oxiriga 99 qo'shiladi"),
        (".insert(1, 99)", lst[:1] + [99] + lst[1:], "1-indeksga 99 qo'shiladi"),
        (".pop()", lst[:-1], "Oxirgi element o'chiriladi"),
        (".remove(" + str(lst[1]) + ")", lst[:1] + lst[2:], f"{lst[1]} qiymati o'chiriladi"),
        (".sort()", sorted(lst), "Ro'yxat tartiblanadi")
    ]
    method, result, desc = random.choice(methods)
    code = f"lst = {lst}\nlst{method}\nprint(lst)"
    ans = str(result)
    wrongs = [
        str(lst),
        str(lst[::-1]),
        str([x*2 for x in lst]),
        "Xatolik"
    ]
    return code, [ans] + wrongs, ans

def gen_tuple_basic():
    tup = tuple(random.randint(1, 10) for _ in range(4))
    idx = random.randint(0, len(tup)-1)
    code = f"t = {tup}\nprint(t[{idx}])"
    ans = tup[idx]
    wrongs = [
        tup[idx-1] if idx > 0 else tup[-1],
        str(tup),
        len(tup),
        "Xatolik"
    ]
    return code, [ans] + wrongs, ans

def gen_set_basic():
    numbers = [random.randint(1, 10) for _ in range(6)]
    s = set(numbers)
    code = f"s = {{{', '.join(map(str, numbers))}}}\nprint(len(s))"
    ans = len(s)
    wrongs = [
        len(numbers),
        max(numbers),
        min(numbers),
        "Xatolik"
    ]
    return code, [ans] + wrongs, ans

def gen_dict_basic():
    keys = ['name', 'age', 'city', 'grade']
    values = ['Ali', 15, 'Toshkent', 9]
    key = random.choice(keys)
    idx = keys.index(key)
    code = f"student = {{'name': 'Ali', 'age': 15, 'city': 'Toshkent', 'grade': 9}}\nprint(student['{key}'])"
    ans = values[idx]
    wrongs = [
        values[(idx+1)%len(values)],
        key,
        str(values),
        "Xatolik"
    ]
    return code, [ans] + wrongs, ans

# ================= DARS 5: Ro'yhatlar va ularning metodlari =================

def gen_list_comprehension():
    n = random.randint(3, 7)
    if random.random() > 0.5:
        code = f"squares = [x**2 for x in range({n})]\nprint(squares)"
        ans = str([x**2 for x in range(n)])
    else:
        code = f"evens = [x for x in range({n*2}) if x % 2 == 0]\nprint(evens)"
        ans = str([x for x in range(n*2) if x % 2 == 0])
    
    wrongs = [
        str(list(range(n))),
        str([x*2 for x in range(n)]),
        "[]",
        "Xatolik"
    ]
    return code, [ans] + wrongs, ans

def gen_list_operations():
    lst1 = [random.randint(1, 5) for _ in range(3)]
    lst2 = [random.randint(6, 10) for _ in range(3)]
    operations = [
        (f"{lst1} + {lst2}", lst1 + lst2, "Ro'yxatlarni birlashtirish"),
        (f"{lst1} * 2", lst1 * 2, "Ro'yxatni ikki marta takrorlash"),
        (f"min({lst1})", min(lst1), "Minimum qiymat"),
        (f"max({lst1})", max(lst1), "Maksimum qiymat"),
        (f"sum({lst1})", sum(lst1), "Elementlar yig'indisi")
    ]
    expr, result, _ = random.choice(operations)
    code = f"print({expr})"
    ans = str(result)
    wrongs = [
        str(lst1),
        str(lst2),
        str(sorted(lst1)),
        "Xatolik"
    ]
    return code, [ans] + wrongs, ans

def gen_dict_methods():
    d = {'a': 1, 'b': 2, 'c': 3}
    methods = [
        (".keys()", list(d.keys()), "Kalitlar ro'yxati"),
        (".values()", list(d.values()), "Qiymatlar ro'yxati"),
        (".items()", list(d.items()), "Kalit-qiymat juftliklari"),
        (".get('b', 0)", d.get('b', 0), "'b' kalitining qiymati"),
        (".pop('a')", d.pop('a'), "'a' kaliti va qiymatini o'chirish")
    ]
    method, result, _ = random.choice(methods)
    if method == ".pop('a')":
        code = f"d = {{'a': 1, 'b': 2, 'c': 3}}\nprint(d.pop('a'))\nprint(d)"
        ans = f"1\\n{{'b': 2, 'c': 3}}"
    else:
        code = f"d = {{'a': 1, 'b': 2, 'c': 3}}\nprint(d{method})"
        ans = str(result)
    
    wrongs = [
        str(d),
        "[1, 2, 3]",
        "['a', 'b', 'c']",
        "Xatolik"
    ]
    return code, [ans] + wrongs, ans

# ================= DARS 6: Amaliy mashg'ulot =================

def gen_practical_loop():
    n = random.randint(3, 7)
    if random.random() > 0.5:
        code = f"for i in range(1, {n+1}):\n    print('*' * i)"
        ans = f"1 dan {n} gacha yulduzlar soni ortib boruvchi uchburchak"
    else:
        code = f"total = 0\nfor i in range(1, {n+1}):\n    total += i\nprint(total)"
        ans = f"1 dan {n} gacha sonlar yig'indisi: {sum(range(1, n+1))}"
    
    wrongs = [
        f"1 dan {n} gacha sonlar",
        f"{n} marta yulduz",
        "Xatolik",
        "Hech narsa"
    ]
    return code, [ans] + wrongs, ans

def gen_practical_string():
    word = random.choice(["python", "programming", "computer", "algorithm"])
    code = f"word = '{word}'\nfor letter in word:\n    print(letter.upper(), end=' ')"
    ans = " ".join(letter.upper() for letter in word)
    wrongs = [
        word.upper(),
        " ".join(word),
        " ".join(letter for letter in word),
        "Xatolik"
    ]
    return code, [ans] + wrongs, ans

# ================= DARS 7: Funksiya, list, string metodlari =================

def gen_function_basic():
    a = random.randint(2, 5)
    b = random.randint(6, 10)
    code = f"def multiply(x, y):\n    return x * y\n\nresult = multiply({a}, {b})\nprint(result)"
    ans = a * b
    wrongs = [a + b, a - b, a // b, a ** b]
    return code, [ans] + wrongs, ans

def gen_function_default():
    n = random.randint(3, 7)
    code = f"def greet(name='Mehmon'):\n    return f'Salom, {{name}}!'\n\nprint(greet())\nprint(greet('Ali'))"
    ans = "Salom, Mehmon!\\nSalom, Ali!"
    wrongs = [
        "Salom, Ali!\\nSalom, Mehmon!",
        "Salom, Mehmon!",
        "Salom, Ali!",
        "Xatolik"
    ]
    return code, [ans] + wrongs, ans

def gen_lambda_function():
    nums = [random.randint(1, 5) for _ in range(3)]
    code = f"nums = {nums}\ndouble = list(map(lambda x: x * 2, nums))\nprint(double)"
    ans = str([x*2 for x in nums])
    wrongs = [
        str(nums),
        str([x**2 for x in nums]),
        str([x+2 for x in nums]),
        "Xatolik"
    ]
    return code, [ans] + wrongs, ans

# ================= MAIN GENERATION FUNCTIONS =================

def generate_dars1(subject_id, limit=40):
    questions = []
    generators = [gen_basic_print, gen_variable_types, gen_input_basic, gen_if_statement, gen_arithmetic_ops]
    
    attempts = 0
    while len(questions) < limit and attempts < 500:
        attempts += 1
        gen = random.choice(generators)
        
        if gen == gen_variable_types:
            q_text, opts, ans = gen()
            success = add_question_safe(questions, subject_id, 9, 1, q_text, opts, ans)
        else:
            code, opts, ans = gen()
            q_text = f"Quyidagi kod natijasi nima?\n\n```python\n{code}\n```"
            success = add_question_safe(questions, subject_id, 9, 1, q_text, opts, ans)
            
    return questions

def generate_dars2(subject_id, limit=50):
    questions = []
    generators = [gen_if_elif_else, gen_for_range, gen_while_loop, gen_nested_loops, gen_break_continue]
    
    attempts = 0
    while len(questions) < limit and attempts < 500:
        attempts += 1
        gen = random.choice(generators)
        code, opts, ans = gen()
        q_text = f"Quyidagi kod natijasi nima?\n\n```python\n{code}\n```"
        success = add_question_safe(questions, subject_id, 9, 1, q_text, opts, ans)
        
    return questions

def generate_dars3(subject_id, limit=40):
    questions = []
    generators = [gen_string_indexing, gen_string_slicing, gen_string_methods, gen_string_concatenation]
    
    attempts = 0
    while len(questions) < limit and attempts < 500:
        attempts += 1
        gen = random.choice(generators)
        code, opts, ans = gen()
        q_text = f"Quyidagi kod natijasi nima?\n\n```python\n{code}\n```"
        success = add_question_safe(questions, subject_id, 9, 1, q_text, opts, ans)
        
    return questions

def generate_dars4(subject_id, limit=40):
    questions = []
    generators = [gen_list_basic, gen_list_methods, gen_tuple_basic, gen_set_basic, gen_dict_basic]
    
    attempts = 0
    while len(questions) < limit and attempts < 500:
        attempts += 1
        gen = random.choice(generators)
        code, opts, ans = gen()
        q_text = f"Quyidagi kod natijasi nima?\n\n```python\n{code}\n```"
        success = add_question_safe(questions, subject_id, 9, 1, q_text, opts, ans)
        
    return questions

def generate_dars5(subject_id, limit=40):
    questions = []
    generators = [gen_list_comprehension, gen_list_operations, gen_dict_methods]
    
    attempts = 0
    while len(questions) < limit and attempts < 500:
        attempts += 1
        gen = random.choice(generators)
        code, opts, ans = gen()
        q_text = f"Quyidagi kod natijasi nima?\n\n```python\n{code}\n```"
        success = add_question_safe(questions, subject_id, 9, 1, q_text, opts, ans)
        
    return questions

def generate_dars6(subject_id, limit=10):
    questions = []
    generators = [gen_practical_loop, gen_practical_string]
    
    attempts = 0
    while len(questions) < limit and attempts < 200:
        attempts += 1
        gen = random.choice(generators)
        code, opts, ans = gen()
        q_text = f"Quyidagi kod natijasi nima?\n\n```python\n{code}\n```"
        success = add_question_safe(questions, subject_id, 9, 1, q_text, opts, ans)
        
    return questions

def generate_dars7(subject_id, limit=10):
    questions = []
    generators = [gen_function_basic, gen_function_default, gen_lambda_function]
    
    attempts = 0
    while len(questions) < limit and attempts < 200:
        attempts += 1
        gen = random.choice(generators)
        code, opts, ans = gen()
        q_text = f"Quyidagi kod natijasi nima?\n\n```python\n{code}\n```"
        success = add_question_safe(questions, subject_id, 9, 1, q_text, opts, ans)
        
    return questions

def main():
    app = create_app()
    with app.app_context():
        print("Clearing Grade 9 Quarter 1 questions...")
        Question.query.filter_by(grade=9, quarter=1).delete()
        db.session.commit()
        
        subject = get_or_create_subject()
        all_questions = []
        
        # Generate questions for each lesson
        dars1 = generate_dars1(subject.id, 40)
        print(f"Dars 1 generated: {len(dars1)} questions")
        
        dars2 = generate_dars2(subject.id, 50)
        print(f"Dars 2 generated: {len(dars2)} questions")
        
        dars3 = generate_dars3(subject.id, 40)
        print(f"Dars 3 generated: {len(dars3)} questions")
        
        dars4 = generate_dars4(subject.id, 40)
        print(f"Dars 4 generated: {len(dars4)} questions")
        
        dars5 = generate_dars5(subject.id, 40)
        print(f"Dars 5 generated: {len(dars5)} questions")
        
        dars6 = generate_dars6(subject.id, 10)
        print(f"Dars 6 generated: {len(dars6)} questions")
        
        dars7 = generate_dars7(subject.id, 10)
        print(f"Dars 7 generated: {len(dars7)} questions")
        
        all_questions = dars1 + dars2 + dars3 + dars4 + dars5 + dars6 + dars7
        
        print(f"Total questions: {len(all_questions)}")
        
        # Add translations for each question
        # for q in all_questions: 
            # q.question_text_ru = auto_translate(q.question_text, 'ru')
            # q.question_text_en = auto_translate(q.question_text, 'en')
            # q.option_a_ru = auto_translate(q.option_a, 'ru')
            # q.option_a_en = auto_translate(q.option_a, 'en')
            # q.option_b_ru = auto_translate(q.option_b, 'ru')
            # q.option_b_en = auto_translate(q.option_b, 'en')
            # q.option_c_ru = auto_translate(q.option_c, 'ru')
            # q.option_c_en = auto_translate(q.option_c, 'en')
            # q.option_d_ru = auto_translate(q.option_d, 'ru')
            # q.option_d_en = auto_translate(q.option_d, 'en')
        
        # Save to database
        for q in all_questions:
            db.session.add(q)
        
        db.session.commit()
        print("Database sync complete. 250 questions added for Grade 9 Quarter 1.")

if __name__ == '__main__':
    main()