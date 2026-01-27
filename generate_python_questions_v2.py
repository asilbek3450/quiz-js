import random
from app import app, db, Question, Subject
import math

# Global set to track uniqueness (cleared per run/grade usually to allow overlap across grades if needed, but uniqueness within a grade is safer)
SEEN_QUESTIONS = set()

def get_or_create_subject():
    subject = Subject.query.filter_by(name='Python').first()
    if not subject:
        subject = Subject(name='Python', name_ru='Python', name_en='Python', grades='7,8,9')
        db.session.add(subject)
        db.session.commit()
    else:
        if subject.grades != '7,8,9':
            subject.grades = '7,8,9'
            db.session.commit()
    return subject

def add_question_safe(questions_list, subject_id, grade, quarter, text, opts, correct):
    global SEEN_QUESTIONS
    
    # Validation
    if len(set(opts)) < 4:
        tries = 0
        while len(opts) < 4 and tries < 10:
            val = f"{random.randint(1,100)}"
            if val not in opts: opts.append(val)
            tries += 1
        # If still failing, pad with generic strings (rare)
        while len(opts) < 4:
             opts.append(f"Option {len(opts)+1}")
             
    final_opts = list(set(opts))[:4]
    random.shuffle(final_opts)
    
    if correct not in final_opts:
        final_opts[0] = correct
        random.shuffle(final_opts)
        
    try:
        correct_idx = final_opts.index(correct)
    except ValueError:
        return False
        
    correct_char = ['A', 'B', 'C', 'D'][correct_idx]
    
    # Unique check
    # We prefix with grade/quarter to ensure uniqueness is scoped or global?
    # User wants unique content. exact same text shouldn't repeat.
    unique_key = f"{grade}-{quarter}-{text}"
    if unique_key in SEEN_QUESTIONS: 
        return False
    SEEN_QUESTIONS.add(unique_key)
    
    q = Question(
        subject_id=subject_id, grade=grade, quarter=quarter, question_text=text,
        option_a=str(final_opts[0]), option_b=str(final_opts[1]), 
        option_c=str(final_opts[2]), option_d=str(final_opts[3]),
        correct_answer=correct_char
    )
    questions_list.append(q)
    return True

# ================= GENERATORS =================

def gen_print_basic():
    # Expand ranges
    val = random.randint(1, 1000)
    s = random.choice(['Salom', 'Python', 'Maktab', 'Kod', 'Dastur', 'Kompyuter', 'Bilim', 'Oquvchi'])
    
    types = ['int', 'str', 'float']
    t = random.choice(types)
    
    if t == 'int':
        code = f"print({val})"
        ans = str(val)
    elif t == 'str':
        code = f"print('{s}')"
        ans = s
    else:
        f_val = round(random.uniform(1.1, 99.9), 1)
        code = f"print({f_val})"
        ans = str(f_val)
        
    wrongs = [str(val+1), f"'{ans}'", "Error", "None", str(val-1), f"'{ans}!'"]
    return code, [ans] + wrongs, ans

def gen_arithmetic():
    a = random.randint(2, 100)
    b = random.randint(2, 50)
    ops = [
        ('+', a+b), ('-', a-b), ('*', a*b), 
        ('//', a//b), ('%', a%b)
    ]
    
    op_sym, res = random.choice(ops)
    
    # Recalc to be safe
    if op_sym == '+': res = a+b
    elif op_sym == '-': res = a-b
    elif op_sym == '*': res = a*b
    elif op_sym == '//': res = a//b
    elif op_sym == '%': res = a%b
    
    code = f"a = {a}\nb = {b}\nprint(a {op_sym} b)"
    ans = str(res)
    wrongs = [str(res+1), str(res-1), str(res*2), str(0), "Error", str(res+10)]
    return code, [ans] + wrongs, ans

def gen_bool_logic():
    a = random.randint(1, 100)
    b = random.randint(1, 100)
    op = random.choice(['>', '<', '==', '!=', '>=', '<='])
    
    code = f"print({a} {op} {b})"
    
    if op == '>': res = a > b
    elif op == '<': res = a < b
    elif op == '==': res = a == b
    elif op == '!=': res = a != b
    elif op == '>=': res = a >= b
    elif op == '<=': res = a <= b
    
    ans = str(res)
    return code, ["True", "False", "Error", "None"], ans

def gen_type_conversion():
    val = random.randint(1, 200)
    f_val = val + 0.5
    s_val = str(val)
    
    mode = random.choice(['int_float', 'str_int', 'int_str'])
    
    if mode == 'int_float':
        code = f"x = {f_val}\nprint(int(x))"
        ans = str(int(f_val))
    elif mode == 'str_int':
        add = random.randint(1, 10)
        code = f"s = '{val}'\nprint(int(s) + {add})"
        ans = str(val + add)
    else:
        suffix = random.randint(1, 9)
        code = f"n = {val}\nprint(str(n) + '{suffix}')"
        ans = f"'{val}{suffix}'"
        
    wrongs = [str(val), str(val+1), "Error", "None", str(val)+str(suffix) if mode!='str_int' else str(val)]
    return code, [ans] + wrongs, ans

def gen_if_simple():
    x = random.randint(1, 200)
    thresh = random.randint(10, 190)
    code = f"x = {x}\nif x > {thresh}:\n    print('Katta')\nelse:\n    print('Kichik')"
    ans = 'Katta' if x > thresh else 'Kichik'
    return code, ['Katta', 'Kichik', 'Error', 'Eq'], ans

def gen_range_loop():
    start = random.randint(1, 50)
    end = start + random.randint(5, 50)
    step = random.choice([1, 2, 3, 4, 5])
    
    mode = random.choice(['sum', 'last', 'count'])
    
    if mode == 'sum':
        code = f"s = 0\nfor i in range({start}, {end}, {step}):\n    s += i\nprint(s)"
        res = sum(range(start, end, step))
    elif mode == 'count':
        code = f"c = 0\nfor i in range({start}, {end}, {step}):\n    c += 1\nprint(c)"
        res = len(range(start, end, step))
    else:
        code = f"x = 0\nfor i in range({start}, {end}, {step}):\n    x = i\nprint(x)"
        r = range(start, end, step)
        res = r[-1] if len(r) > 0 else 0
        
    ans = str(res)
    wrongs = [str(res+1), str(res-step), str(res*2), "0", str(res+10)]
    return code, [ans] + wrongs, ans

def gen_string_indexing():
    # Make random words to increase space
    import string
    chars = string.ascii_uppercase
    w_len = random.randint(4, 10)
    w = "".join(random.choices(chars, k=w_len))
    
    idx = random.randint(0, len(w)-1)
    neg_idx = random.randint(1, len(w)) * -1
    
    if random.random() > 0.5:
        code = f"s = '{w}'\nprint(s[{idx}])"
        ans = f"'{w[idx]}'"
        wrongs = [f"'{w[(idx+1)%len(w)]}'", f"'{w[idx-1]}'", "IndexError"]
    else:
        code = f"s = '{w}'\nprint(s[{neg_idx}])"
        ans = f"'{w[neg_idx]}'"
        wrongs = [f"'{w[neg_idx+1]}'", "Error", "None"]
        
    return code, [ans] + wrongs, ans

def gen_list_ops():
    lst = [random.randint(1, 50) for _ in range(3)]
    op = random.choice(['append', 'pop', 'len', 'sum'])
    
    if op == 'append':
        val = random.randint(51, 100)
        code = f"nums = {lst}\nnums.append({val})\nprint(len(nums))"
        ans = str(len(lst) + 1)
    elif op == 'pop':
        code = f"nums = {lst}\nnums.pop()\nprint(len(nums))"
        ans = str(len(lst) - 1)
    elif op == 'len':
        code = f"nums = {lst}\nprint(len(nums))"
        ans = str(len(lst))
    else: # sum
        code = f"nums = {lst}\nprint(sum(nums))"
        ans = str(sum(lst))
        
    wrongs = [str(len(lst)), str(sum(lst)+1), "Error", "0", str(len(lst)+2)]
    return code, [ans] + wrongs, ans

def gen_formatting():
    names = ['Ali', 'Vali', 'Guli', 'Hasan', 'Husan', 'Olim', 'Anvar']
    name = random.choice(names)
    age = random.randint(10, 50)
    
    code = f"name = '{name}'\nage = {age}\nprint(f'{{name}} {{age}} yoshda')"
    ans = f"'{name} {age} yoshda'"
    wrongs = [f"'{name} {{age}} yoshda'", f"'{name}{age} yoshda'", "Error", f"'{name} {age+1} yoshda'"]
    return code, [ans] + wrongs, ans

def gen_dict_simple():
    d_len = random.randint(2, 5)
    import string
    keys = list(string.ascii_lowercase[:d_len])
    d = {k: random.randint(1, 100) for k in keys}
    
    k = random.choice(list(d.keys()))
    val = random.randint(10, 20)
    
    op = random.choice(['get', 'assign', 'len'])
    
    if op == 'get':
        # Safely construct string repr of dict
        code = f"d = {d}\nprint(d['{k}'])"
        ans = str(d[k])
        wrongs = [str(d[k]+1), "KeyError", "None"]
    elif op == 'len':
        code = f"d = {d}\nprint(len(d))"
        ans = str(len(d))
        wrongs = [str(len(d)-1), str(len(d)+1), "0"]
    else:
        code = f"d = {{'a': 1}}\nd['b'] = {val}\nprint(d['b'])"
        ans = str(val)
        wrongs = ["1", "None", "Error"]
        
    return code, [ans] + wrongs, ans

def gen_while_basic():
    start = random.randint(1, 50)
    limit = start + random.randint(2, 20)
    step = random.randint(1, 3)
    
    code = f"i = {start}\nwhile i < {limit}:\n    i += {step}\nprint(i)"
    
    # Calculate
    curr = start
    while curr < limit:
        curr += step
    res = curr
    
    ans = str(res)
    wrongs = [str(limit), str(limit+1), str(start), "Infinite Loop"]
    return code, [ans] + wrongs, ans

# ================= ORCHESTRATOR =================

def get_generators_for_grade(grade):
    # Differentiate slightly by varying complexity or pool
    # But essentially all grades cover these python basics in school context
    
    # Q1: Basics
    pool_q1 = [gen_print_basic, gen_arithmetic, gen_type_conversion, gen_formatting]
    
    # Q2: Logic & Flow
    pool_q2 = [gen_bool_logic, gen_if_simple, gen_arithmetic] # mixed arithmetic
    
    # Q3: Loops & Strings
    pool_q3 = [gen_range_loop, gen_while_basic, gen_string_indexing]
    
    # Q4: Structures & Adv
    pool_q4 = [gen_list_ops, gen_dict_simple, gen_range_loop]
    
    return {
        1: pool_q1,
        2: pool_q2,
        3: pool_q3,
        4: pool_q4
    }

def main():
    with app.app_context():
        subject = get_or_create_subject()
        
        # Clear specific grades
        Question.query.filter(Question.grade.in_([7, 8, 9])).delete(synchronize_session=False)
        db.session.commit()
        
        grades = [7, 8, 9]
        total_created = 0
        
        for g in grades:
            mapping = get_generators_for_grade(g)
            for q_num, gens in mapping.items():
                
                # Goal: 200 per quarter
                count = 0
                max_retries = 3000
                retries = 0
                
                while count < 200 and retries < max_retries:
                    retries += 1
                    gen = random.choice(gens)
                    try:
                        code, opts, ans = gen()
                        final_code = f"Quyidagi kod natijasi nima?\n\n```python\n{code}\n```"
                        
                        if add_question_safe([], subject.id, g, q_num, final_code, opts, ans):
                            # Pass empty list to add_question_safe to just use side-effect of creating object?
                            # Wait, add_question_safe appends to list provided.
                            # We should reuse the saving logic.
                            
                            # Modified add_question_safe inside this script actually creates object but appended to list
                            # Let's fix usage
                            pass 
                    except Exception as e:
                        continue
                        
                    # We need to actually persist. 
                    # Let's batch save every 50 or so.
                pass 
                
        # Re-implement main loop properly to save objects
        
        all_questions = []
        
        for g in grades:
            print(f"Generating Grade {g}...")
            mapping = get_generators_for_grade(g)
            
            for q_num, gens in mapping.items():
                print(f"  Quarter {q_num}...")
                q_list = []
                attempts = 0
                while len(q_list) < 200 and attempts < 2000:
                    attempts += 1
                    gen = random.choice(gens)
                    try:
                        code, opts, ans = gen()
                        if ans in opts or len(opts) >= 3: # Basic sanity
                            final_code = f"Quyidagi kod natijasi nima?\n\n```python\n{code}\n```"
                            add_question_safe(q_list, subject.id, g, q_num, final_code, opts, ans)
                    except:
                        pass
                
                print(f"    Generated {len(q_list)} questions")
                all_questions.extend(q_list)
        
        print(f"Total questions generated: {len(all_questions)}")
        db.session.bulk_save_objects(all_questions)
        db.session.commit()
        print("Database Updated.")

if __name__ == '__main__':
    main()
