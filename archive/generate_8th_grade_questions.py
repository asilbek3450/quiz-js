import random
from app import app, db, Question, Subject
import math

# Global set to track uniqueness
SEEN_QUESTIONS = set()

def get_or_create_subject():
    subject = Subject.query.filter_by(name='Python').first()
    if not subject:
        subject = Subject(name='Python', name_ru='Python', name_en='Python', grades='7,8,9')
        db.session.add(subject)
        db.session.commit()
    return subject

def add_question_safe(questions_list, subject_id, grade, quarter, text, opts, correct):
    global SEEN_QUESTIONS
    
    # Ensure options are unique
    if len(set(opts)) < 4:
        # Pad with placeholders if needed, though templates should generate unique opts
        while len(opts) < 4:
            opts.append(f"Option {len(opts)+1}")
    
    final_opts = list(set(opts))[:4] # Take 4 unique
    if len(final_opts) < 4: return False 
    
    if correct not in final_opts:
        # Ensure correct is in options (it might have been cut off if logic was weak)
        final_opts[0] = correct
        
    random.shuffle(final_opts)
    
    try:
        correct_idx = final_opts.index(correct)
    except ValueError:
        return False
        
    correct_char = ['A', 'B', 'C', 'D'][correct_idx]
    
    # Simpler uniqueness check: just the text content
    if text in SEEN_QUESTIONS: return False
    SEEN_QUESTIONS.add(text)
    
    q = Question(
        subject_id=subject_id, grade=grade, quarter=quarter, question_text=text,
        option_a=str(final_opts[0]), option_b=str(final_opts[1]), 
        option_c=str(final_opts[2]), option_d=str(final_opts[3]),
        correct_answer=correct_char
    )
    questions_list.append(q)
    return True

# ================= HELPER GENERATORS =================

def gen_math_expr_q01():
    # Simple var ops: a=X, b=Y, print(a+b)
    ops = [
        ('+', lambda x,y: x+y), ('-', lambda x,y: x-y), 
        ('*', lambda x,y: x*y), ('//', lambda x,y: x//y), ('%', lambda x,y: x%y)
    ]
    a = random.randint(5, 50)
    b = random.randint(2, 10)
    op_sym, op_func = random.choice(ops)
    
    code = f"a = {a}\nb = {b}\nprint(a {op_sym} b)"
    ans = op_func(a,b)
    
    wrongs = {ans + 1, ans - 1, ans + b, ans * 2, 0, 1}
    wrongs.discard(ans)
    
    return code, [ans] + list(wrongs), ans

def gen_string_slice_q01():
    words = ["PYTHON", "INFORMATIKA", "DASTURLASH", "KOMPYUTER", "MAKTAB", "ISLOM", "KELAJAK"]
    w = random.choice(words)
    start = random.randint(0, 2)
    end = random.randint(3, len(w))
    step = random.choice([1, 1, 2])
    
    if step == 1:
        code = f"s = '{w}'\nprint(s[{start}:{end}])"
        ans = w[start:end]
    else:
        code = f"s = '{w}'\nprint(s[{start}:{end}:{step}])"
        ans = w[start:end:step]
        
    # Wrongs: off by one, empty, full word
    wrongs = [w[start:end+1], w[start+1:end], w, "Error"]
    return code, [f"'{ans}'"] + [f"'{x}'" for x in wrongs], f"'{ans}'"

def gen_if_else_q01():
    x = random.randint(1, 20)
    y = random.randint(1, 20)
    thresh = random.randint(5, 15)
    
    code = f"x = {x}\ny = {y}\nif x + y > {thresh}:\n    print('A')\nelse:\n    print('B')"
    ans = 'A' if (x+y) > thresh else 'B'
    return code, ['A', 'B', 'AB', 'Error'], ans

def gen_list_index_q01():
    lst = [random.randint(1, 20) for _ in range(5)]
    idx = random.randint(-5, 4)
    code = f"nums = {lst}\nprint(nums[{idx}])"
    ans = lst[idx]
    
    wrongs = [lst[(idx+1)%5], lst[(idx-1)%5], random.randint(50,100), "Error"]
    return code, [ans] + wrongs, ans

# ================= QUARTER 2: Functions, Math =================

def gen_func_basic_q02():
    a = random.randint(1, 10)
    b = random.randint(1, 10)
    fname = random.choice(['hisobla', 'func', 'test', 'olchash'])
    
    code = f"def {fname}(x, y):\n    return 2 * x + y\n\nprint({fname}({a}, {b}))"
    ans = 2 * a + b
    wrongs = [2*a - b, a + 2*b, a+b, 0]
    return code, [ans] + wrongs, ans

def gen_math_module_q02():
    funcs = [
        ('ceil', math.ceil, 3.14, 4.9), 
        ('floor', math.floor, 3.99, 5.1),
        ('pow', math.pow, (2,3), (3,2)),
        ('sqrt', math.sqrt, 16, 25),
        ('fabs', math.fabs, -5, -10)
    ]
    name, func, v1, v2 = random.choice(funcs)
    
    val = v1 if random.random() > 0.5 else v2
    if isinstance(val, tuple):
        val_str = f"{val[0]}, {val[1]}"
        ans = func(val[0], val[1])
    else:
        val_str = str(val)
        ans = func(val)
        
    if name == 'pow' or name == 'sqrt' or name == 'fabs':
        ans = int(ans) if ans.is_integer() else ans
        
    code = f"import math\nprint(math.{name}({val_str}))"
    
    wrongs = [ans+1, ans-1, 0, int(ans)+2]
    return code, [ans] + wrongs, ans

def gen_random_q02():
    a = random.randint(1, 5)
    b = random.randint(6, 10)
    code = f"import random\nprint(random.randint({a}, {b}))"
    ans = f"{a} dan {b} gacha ixtiyoriy son (u ham kiradi)"
    wrongs = [
        f"{a} dan {b} gacha (b kirmaydi)",
        f"Faqat {a} yoki {b}",
        f"0 dan {b} gacha son",
        "Error"
    ]
    return code, [ans] + wrongs, ans


# ================= QUARTER 3: String Methods, Try/Except, Lists, Lambda =================

def gen_str_method_q03():
    # Expanded word list
    words = ["APPLE", "Banana", "Cherry", "Date", "Elderberry", "Fig", "Grape", "Python", "Coding", "School", "Student"]
    w = random.choice(words) + str(random.randint(1,99)) # Make input unique
    
    ops = [
        ('upper', lambda s: s.upper()),
        ('lower', lambda s: s.lower()),
        ('swapcase', lambda s: s.swapcase()),
        ('replace', lambda s: s.replace('e', 'X')),
        ('replace', lambda s: s.replace('a', '@')),
        ('count', lambda s: s.lower().count('e')),
        ('find', lambda s: s.find('y')),
    ]
    
    op_name, op_func = random.choice(ops)
    
    if op_name == 'replace':
        c1, c2 = ('e', 'X') if 'e' in w else ('a', '@')
        if c1 == 'a' and 'a' not in w.lower():
             # fallback
             w += 'a'
        code = f"s = '{w}'\nprint(s.replace('{c1}', '{c2}'))"
        ans = w.replace(c1, c2)
    elif op_name == 'count':
        char = random.choice(['e', 'a', 'o', 'n'])
        code = f"s = '{w}'\nprint(s.count('{char}'))"
        ans = w.count(char)
    elif op_name == 'find':
        char = random.choice(['y', 'z', 'P', 'S'])
        code = f"s = '{w}'\nprint(s.find('{char}'))"
        ans = w.find(char)
    else:
        code = f"s = '{w}'\nprint(s.{op_name}())"
        ans = op_func(w)

    val = str(ans)
    if isinstance(ans, str):
        val = f"'{ans}'"
        
    wrongs = [f"'{ans}'[::-1]", "Error", "None", "0", "-1"]
    return code, [val] + wrongs, val

def gen_try_except_q03():
    # Numeric variations for uniqueness
    val1 = random.randint(1, 100)
    val2 = random.randint(1, 100)
    
    scenarios = [
        ('ZeroDivision', f"x = {val1} / 0", "ZeroDivisionError", "ZeroDivisionError"),
        ('Value', f"x = int('abc{val2}')", "ValueError", "ValueError"),
        ('Index', f"L=[{val1}]; print(L[5])", "IndexError", "IndexError"),
        ('Key', f"d={{'a':{val1}}}; print(d['b'])", "KeyError", "KeyError"),
        ('Name', f"print(undefined_variable_{val2})", "NameError", "NameError")
    ]
    
    s_name, s_code, s_err, catch_block = random.choice(scenarios)
    
    # Sometimes catch correct, sometimes catch wrong
    if random.random() > 0.5:
        # Correct catch
        code = f"try:\n    {s_code}\nexcept {s_err}:\n    print('Tutildi')\nexcept:\n    print('Boshqa')"
        ans = "'Tutildi'"
    else:
        # Wrong catch, goes to default or crash?
        # Let's use 'except Exception' or specific incorrect one
        wrong_err = "IndexError" if s_err != "IndexError" else "ValueError"
        code = f"try:\n    {s_code}\nexcept {wrong_err}:\n    print('Xato 1')\nexcept:\n    print('Xato 2')"
        ans = "'Xato 2'"
        
    return code, ["'Tutildi'", "'Xato 1'", "'Xato 2'", "'Boshqa'", "Error"], ans

def gen_set_op_q03():
    # Ensure sets are unique
    base = random.randint(1, 100)
    s1 = {base, base+1, base+2}
    s2 = {base+1, base+2, base+3} 
    op = random.choice(['&', '|', '-', '^'])
    
    if op == '&':
        ans = s1 & s2
    elif op == '|':
        ans = s1 | s2
    elif op == '-':
        ans = s1 - s2
    else:
        ans = s1 ^ s2
        
    code = f"A = {s1}\nB = {s2}\nprint(A {op} B)"
    wrongs = [s1, s2, {base}, set()]
    return code, [str(ans)] + [str(x) for x in wrongs if x != ans], str(ans)

def gen_lambda_map_q03():
    # New generator for Q3 to boost numbers
    start = random.randint(1, 5)
    nums = [start, start+1, start+2]
    factor = random.randint(2, 5)
    
    op_type = random.choice(['map', 'filter'])
    
    if op_type == 'map':
        code = f"nums = {nums}\nres = list(map(lambda x: x*{factor}, nums))\nprint(res)"
        ans = [x*factor for x in nums]
    else:
        # Filter even/odd
        is_even = random.choice([True, False])
        mod_val = 0 if is_even else 1
        code = f"nums = {nums}\nres = list(filter(lambda x: x%2=={mod_val}, nums))\nprint(res)"
        ans = [x for x in nums if x%2==mod_val]
        
    return code, [str(ans), str(nums), str([0,0,0]), "Error"], str(ans)



# ================= QUARTER 4: OOP =================

def gen_class_init_q04():
    cls_name = random.choice(['Car', 'User', 'Book', 'Student'])
    attr = random.choice(['name', 'role', 'title', 'grade'])
    val = random.choice(['"Tesla"', '"Admin"', '"Python"', '8'])
    
    code = f"class {cls_name}:\n    def __init__(self, x):\n        self.{attr} = x\n\nobj = {cls_name}({val})\nprint(obj.{attr})"
    ans = val.replace('"', '')
    wrongs = ["None", f"obj.{attr}", "Error", "self"]
    
    if val.startswith('"'):
        # preserve quotes for display if it's a string in python output? usually print removes quotes
        # But wait, python print(obj.name) where name="Tesla" outputs Tesla without quotes.
        # But our options usually represent the value. Let's keep it simple.
        pass
        
    return code, [ans, f"'{ans}'", "Error", "None"], ans

def gen_inheritance_q04():
    p_val = random.randint(10,50)
    c_val = random.randint(10,50)
    
    code = f"class A:\n    def show(self):\n        return {p_val}\n\nclass B(A):\n    def show(self):\n        return {c_val}\n\nb = B()\nprint(b.show())"
    ans = c_val
    wrongs = [p_val, p_val+c_val, 0, "Error"]
    return code, [ans] + wrongs, ans


# ================= MAIN GENERATORS =================

def generate_q1(subject_id, limit=200):
    questions = []
    generators = [gen_math_expr_q01, gen_string_slice_q01, gen_if_else_q01, gen_list_index_q01]
    
    attempts = 0
    while len(questions) < limit and attempts < 1000:
        attempts += 1
        gen = random.choice(generators)
        code, opts, ans = gen()
        
        q_text = f"Quyidagi kod natijasi nima?\n\n```python\n{code}\n```"
        success = add_question_safe(questions, subject_id, 8, 1, q_text, opts, ans)
        
    return questions

def generate_q2(subject_id, limit=200):
    questions = []
    generators = [gen_func_basic_q02, gen_math_module_q02, gen_random_q02]
    
    attempts = 0
    while len(questions) < limit and attempts < 1000:
        attempts += 1
        gen = random.choice(generators)
        code, opts, ans = gen()
        
        q_text = f"Quyidagi kod natijasi nima?\n\n```python\n{code}\n```"
        add_question_safe(questions, subject_id, 8, 2, q_text, opts, ans)
        
    return questions


def generate_q3(subject_id, limit=200):
    questions = []
    # Added gen_lambda_map_q03
    generators = [gen_str_method_q03, gen_try_except_q03, gen_set_op_q03, gen_lambda_map_q03]
    
    attempts = 0
    while len(questions) < limit and attempts < 1000:
        attempts += 1
        gen = random.choice(generators)
        code, opts, ans = gen()
        
        q_text = f"Quyidagi kod natijasi nima?\n\n```python\n{code}\n```"
        add_question_safe(questions, subject_id, 8, 3, q_text, opts, ans)
        
    return questions

def generate_q4(subject_id, limit=200):
    questions = []
    generators = [gen_class_init_q04, gen_inheritance_q04]
    
    attempts = 0
    while len(questions) < limit and attempts < 1000:
        attempts += 1
        gen = random.choice(generators)
        code, opts, ans = gen()
        
        q_text = f"Quyidagi kod natijasi nima?\n\n```python\n{code}\n```"
        add_question_safe(questions, subject_id, 8, 4, q_text, opts, ans)
        
    return questions


def main():
    ctx = app.app_context()
    ctx.push()
    
    print("Clearing Grade 8 questions...")
    Question.query.filter_by(grade=8).delete()
    db.session.commit()
    
    subject = get_or_create_subject()
    all_questions = []
    
    # Generate 200 for each quarter
    q1 = generate_q1(subject.id, 200)
    print(f"Q1 generated: {len(q1)}")
    
    q2 = generate_q2(subject.id, 200)
    print(f"Q2 generated: {len(q2)}")
    
    q3 = generate_q3(subject.id, 200)
    print(f"Q3 generated: {len(q3)}")
    
    q4 = generate_q4(subject.id, 200)
    print(f"Q4 generated: {len(q4)}")
    
    all_questions = q1 + q2 + q3 + q4
    print(f"Total extracted: {len(all_questions)}")
    
    # Save code questions
    db.session.bulk_save_objects(all_questions)
    
    # ADDITIONALLY: Add some theoretical questions back if we are short or to mix it up?
    # The user asked for "turli kodli misollar" (different code examples).
    # If the generators hit 200 unique each, we are good.
    
    db.session.commit()
    print("Database sync complete.")

if __name__ == '__main__':
    main()
