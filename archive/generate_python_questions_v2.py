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

# ================= GRADE 8 SPECIFIC GENERATORS =================

def gen_list_methods():
    lst = [random.randint(1, 20) for _ in range(4)]
    method = random.choice(['append', 'insert', 'remove', 'sort', 'reverse', 'pop'])
    
    if method == 'append':
        val = random.randint(21, 50)
        code = f"lst = {lst}\nlst.append({val})\nprint(lst[-1])"
        ans = str(val)
        wrongs = [str(lst[-1]), str(val-1), "None", "Error"]
    elif method == 'insert':
        idx = random.randint(0, len(lst)-1)
        val = random.randint(21, 50)
        code = f"lst = {lst}\nlst.insert({idx}, {val})\nprint(lst[{idx}])"
        ans = str(val)
        wrongs = [str(lst[idx]), str(val+1), "None", "Error"]
    elif method == 'remove':
        val = random.choice(lst)
        # Ensure only one occurrence for unambiguous removal or handle duplicates logic (remove removes first)
        # For simplicity, let's just use unique list
        lst = random.sample(range(1, 100), 5)
        val = lst[2]
        code = f"lst = {lst}\nlst.remove({val})\nprint({val} in lst)"
        ans = "False"
        wrongs = ["True", "None", "Error"]
    elif method == 'sort':
        lst = random.sample(range(1, 100), 5)
        code = f"lst = {lst}\nlst.sort()\nprint(lst[0])"
        ans = str(min(lst))
        wrongs = [str(max(lst)), str(lst[0]), "None", "Error"]
    elif method == 'reverse':
        lst = random.sample(range(1, 10), 4)
        code = f"lst = {lst}\nlst.reverse()\nprint(lst[0])"
        ans = str(lst[-1])
        wrongs = [str(lst[0]), "None", "Error"]
    else: # pop
        code = f"lst = {lst}\nlst.pop()\nprint(len(lst))"
        ans = str(len(lst)-1)
        wrongs = [str(len(lst)), str(lst[-1]), "None"]
        
    return code, [ans] + wrongs, ans

def gen_tuple_ops():
    tup = tuple(random.sample(range(1, 20), 4))
    op = random.choice(['index', 'slice', 'immutability'])
    
    if op == 'index':
        idx = random.randint(0, 3)
        code = f"t = {tup}\nprint(t[{idx}])"
        ans = str(tup[idx])
        wrongs = [str(tup[(idx+1)%4]), "Error", "None"]
    elif op == 'slice':
        code = f"t = {tup}\nprint(t[1:3])"
        ans = str(tup[1:3])
        wrongs = [str(tup[1:4]), str(list(tup[1:3])), "Error"]
    else:
        # Immutability
        code = f"t = {tup}\nt[0] = 100\nprint(t[0])"
        ans = "TypeError" # catching the error text? Or generally "Error"
        # Since options usually simple strings, let's say "Error" is the intended answer for school level
        # But let's be technically precise if possible. "TypeError" or "Xatolik"
        ans = "Error"
        wrongs = ["100", str(tup[0]), "None"]
        
    return code, [ans] + wrongs, ans

def gen_dict_methods():
    d = {'a': 1, 'b': 2, 'c': 3}
    method = random.choice(['keys', 'values', 'items', 'get', 'update'])
    
    if method == 'keys':
        code = f"d = {d}\nprint(list(d.keys()))"
        ans = str(list(d.keys()))
        wrongs = [str(list(d.values())), str(d), "Error"]
    elif method == 'values':
        code = f"d = {d}\nprint(list(d.values()))"
        ans = str(list(d.values()))
        wrongs = [str(list(d.keys())), "Error", "[1, 2]"]
    elif method == 'get':
        k = 'b'
        code = f"d = {d}\nprint(d.get('{k}', 0))"
        ans = str(d.get(k))
        wrongs = [str(d.get('a')), "0", "None"]
    elif method == 'update':
        code = f"d = {{'a': 1}}\nd.update({{'b': 2}})\nprint(len(d))"
        ans = "2"
        wrongs = ["1", "Error", "None"]
    else:
        code = f"d = {{'a': 1}}\nprint(d.items())"
        ans = "dict_items([('a', 1)])"
        wrongs = ["[('a', 1)]", "{'a': 1}", "Error"]
        
    return code, [ans] + wrongs, ans

def gen_function_def():
    # Regular, args, kwargs, default
    mode = random.choice(['simple', 'default', 'args'])
    
    if mode == 'simple':
        a, b = random.randint(1,100), random.randint(1,100)
        func_name = random.choice(['add', 'calc', 'sum_nums', 'func'])
        code = f"def {func_name}(x, y):\n    return x + y\nprint({func_name}({a}, {b}))"
        ans = str(a+b)
        wrongs = [str(a*b), str(a-b), "Error", "None", str(a+b+1)]
    elif mode == 'default':
        val = random.randint(2, 10)
        default_pow = random.randint(2, 3)
        func_name = random.choice(['power', 'kvadrat', 'daraja'])
        code = f"def {func_name}(x, n={default_pow}):\n    return x ** n\nprint({func_name}({val}))"
        ans = str(val**default_pow)
        wrongs = [str(val), str(val*2), "Error", str(val**(default_pow+1))]
    else:
        # args
        # range should be larger
        nums = random.sample(range(1, 20), 3)
        func_name = random.choice(['total', 'yigindi', 'all_sum'])
        code = f"def {func_name}(*args):\n    return sum(args)\nprint({func_name}({', '.join(map(str, nums))}))"
        ans = str(sum(nums))
        wrongs = [str(len(nums)), "Error", "None", str(sum(nums)+1)]
        
    return code, [ans] + wrongs, ans

def gen_recursion_simple():
    # Factorial or sum
    n = random.randint(3, 8) # Increased range
    func_name = random.choice(['s', 'f', 'rec', 'func'])
    
    if random.random() > 0.5:
        # Sum 1 to n
        code = f"def {func_name}(n):\n    if n == 1: return 1\n    return n + {func_name}(n-1)\nprint({func_name}({n}))"
        ans = str(sum(range(1, n+1)))
    else:
        # Factorial
        code = f"def {func_name}(n):\n    if n == 1: return 1\n    return n * {func_name}(n-1)\nprint({func_name}({n}))"
        import math
        ans = str(math.factorial(n))
        
    wrongs = [str(int(ans)-1), str(int(ans)+n), "Error", "Infinite Loop", "1"]
    return code, [ans] + wrongs, ans

def gen_modules():
    mod = random.choice(['math', 'random', 'datetime'])
    if mod == 'math':
        # Expand math options
        func = random.choice(['sqrt', 'ceil', 'floor', 'fabs'])
        if func == 'sqrt':
            val = random.choice([16, 25, 36, 49, 64, 81, 100, 121, 144])
            ans = str(int(math.sqrt(val)))
            wrongs = [str(val//2), str(val), "Error"]
        elif func == 'ceil':
            val = random.uniform(1.1, 10.9)
            val = round(val, 2)
            ans = str(math.ceil(val))
            wrongs = [str(int(val)), str(math.floor(val)), "Error"]
        elif func == 'floor':
            val = random.uniform(1.1, 10.9)
            val = round(val, 2)
            ans = str(math.floor(val))
            wrongs = [str(int(val)+1), str(math.ceil(val)), "Error"]
        else: # fabs
            val = random.randint(-20, -1)
            ans = str(int(math.fabs(val)))
            wrongs = [str(val), "Error", "0"]
            
        code = f"import math\nprint(int(math.{func}({val})))" if func != 'sqrt' and func != 'fabs' else f"import math\nprint(int(math.{func}({val})))"
        # Correct output format for float funcs if cast to int
        
    elif mod == 'random':
        a = random.randint(1, 10)
        b = a + random.randint(1, 5)
        # To make it deterministic for "Result?" question, we can't truly use random output unless we mock it or ask for "Range".
        # Or we can ask "Qaysi javob bo'lishi MUMKIN?" (Which answer IS POSSIBLE?)
        # But our system expects one correct answer.
        # Let's switch to `random.seed(x)`?
        # Or simple: "random.randint(5, 5)" -> always 5.
        
        # Strategy: use seed or predictable calls
        seed_val = random.randint(1, 100)
        code = f"import random\nrandom.seed({seed_val})\nprint(random.randint(10, 20))"
        # We can't easily predict this without running it. 
        # Let's stick to concept questions formatted as code? 
        # "print(random.randint(1, 1))" -> 1.
        # "print(random.randrange(10, 11))" -> 10.
        
        val = random.randint(1, 20)
        code = f"import random\n# range {val} to {val}\nprint(random.randint({val}, {val}))"
        ans = str(val)
        wrongs = [str(val+1), "0", "Error"]
        
    else:
        # Datetime
        y = random.randint(2000, 2030)
        m = random.randint(1, 12)
        d = random.randint(1, 28)
        code = f"import datetime\nd = datetime.date({y}, {m}, {d})\nprint(d.year)"
        ans = str(y)
        wrongs = [str(m), str(d), "Error", str(y+1)]
        
    return code, [ans] + wrongs, ans

# ================= ORCHESTRATOR =================

def get_generators_for_grade(grade):
    if grade == 8:
        # Curriculum aligned
        # Q1: List, Tuple, Dict
        pool_q1 = [gen_list_ops, gen_list_methods, gen_tuple_ops, gen_dict_simple, gen_dict_methods]
        
        # Q2: Functions, Recursion, Modules
        pool_q2 = [gen_function_def, gen_recursion_simple, gen_modules]
        
        # Q3 & Q4: Mixed practice (user requested 200/quarter, assuming review or advanced)
        # Let's mix Q1 and Q2 topics plus some logic
        pool_q3 = pool_q1 + pool_q2 + [gen_range_loop]
        pool_q4 = pool_q3 + [gen_bool_logic]
        
        return {1: pool_q1, 2: pool_q2, 3: pool_q3, 4: pool_q4}

    # Keep 7 and 9 as before (or generic)
    pool_basic = [gen_print_basic, gen_arithmetic, gen_type_conversion, gen_formatting, gen_bool_logic, gen_if_simple, gen_range_loop, gen_string_indexing]
    pool_adv = [gen_list_ops, gen_dict_simple, gen_while_basic]
    
    return {
        1: pool_basic,
        2: pool_basic + [gen_range_loop],
        3: pool_adv + pool_basic,
        4: pool_adv + [gen_formatting]
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
