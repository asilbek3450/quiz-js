import random
import math
import datetime
import string
from app import app, db, Question, Subject

# ================= CONFIGURATION =================
GRADES = [7, 8, 9]
QUARTERS = [1, 2, 3, 4]
QUESTIONS_PER_QUARTER = 250
SEEN_QUESTIONS = set()  # To track uniqueness globally

# ================= UTIL FUNCTIONS =================
def random_var_name():
    prefix = random.choice(string.ascii_lowercase)
    suffix = random.choice(['', str(random.randint(1,9))])
    return prefix + suffix

def random_string(length=5):
    letters = string.ascii_uppercase
    return "".join(random.choices(letters, k=length))

def random_word():
    words = ["PYTHON", "CODE", "DATA", "LIST", "DICT", "FUNC", "LOOP", "TEST", "EXAM", "MATH", "LOGIC", "CLASS", "OBJ", "SELF"]
    return random.choice(words) + random_string(2)

def get_or_create_subject():
    subject = Subject.query.filter_by(name='Python').first()
    if not subject:
        subject = Subject(name='Python', name_ru='Python', name_en='Python', grades='7,8,9')
        db.session.add(subject)
        db.session.commit()
    return subject

def add_question(questions_list, subject_id, grade, quarter, text, opts, correct):
    global SEEN_QUESTIONS
    
    # Clean and Validate Options
    opts = [str(o) for o in opts]
    
    # Ensure 4 unique options
    unique_opts = list(set(opts))
    if len(unique_opts) < 4:
        tries = 0
        while len(unique_opts) < 4 and tries < 20:
            # Generate dummy wrong answers if needed
            dummy = str(random.randint(-100, 100)) if tries % 2 == 0 else f"'{random_string(3)}'"
            if dummy not in unique_opts:
                unique_opts.append(dummy)
            tries += 1
            
    final_opts = unique_opts[:4]
    
    # Ensure correct answer is present
    if str(correct) not in final_opts:
        final_opts[0] = str(correct)
    
    random.shuffle(final_opts)
    
    # Determine correct char
    try:
        correct_idx = final_opts.index(str(correct))
        correct_char = ['A', 'B', 'C', 'D'][correct_idx]
    except ValueError:
        return False # Should not happen

    # Check for duplicate questions
    # Using a simplified text key to catch exact duplicates
    # Removing whitespace to be safe
    key = text.replace(" ", "").replace("\n", "")
    if key in SEEN_QUESTIONS:
        return False
    SEEN_QUESTIONS.add(key)

    q = Question(
        subject_id=subject_id,
        grade=grade, 
        quarter=quarter, 
        question_text=text,
        option_a=final_opts[0], 
        option_b=final_opts[1], 
        option_c=final_opts[2], 
        option_d=final_opts[3],
        correct_answer=correct_char
    )
    questions_list.append(q)
    return True

# ================= GRADE 7 GENERATORS =================
# Q1: Intro, Variables, Types
def g7_q1_vars():
    v = random_var_name()
    val = random.randint(1, 100)
    code = f"{v} = {val}\nprint({v})"
    return code, [str(val), str(val+1), f"'{v}'", "Error"], str(val)

def g7_q1_types():
    val = random.choice([
        (random.randint(1,100), 'int'),
        (f"'{random_string()}'", 'str'),
        (round(random.uniform(1,100), 2), 'float')
    ])
    code = f"x = {val[0]}\nprint(type(x))"
    # Note: type output is <class 'int'> etc.
    ans = f"<class '{val[1]}'>"
    wrongs = [f"<class '{t}'>" for t in ['int', 'str', 'float', 'bool'] if t != val[1]]
    return code, [ans] + wrongs, ans

# Q2: Arithmetic
def g7_q2_arithmetic():
    a = random.randint(5, 50)
    b = random.randint(2, 8)
    ops = [
        ('//', a//b), ('%', a%b), ('**', a**2 if a < 12 else a+b) 
    ]
    # For power, keep it small to avoid huge numbers
    if a < 12: ops.append(('**', a**2))
    
    # Pick one
    op_sym, res = random.choice(ops)
    if op_sym == '**':
        code = f"a = {a}\nprint(a ** 2)"
        res = a**2
    else:
        code = f"a = {a}\nb = {b}\nprint(a {op_sym} b)"
        
    ans = str(res)
    wrongs = [str(res+1), str(res-1), str(res*2), str(0)]
    return code, [ans] + wrongs, ans

def g7_q2_priority():
    a, b, c = random.randint(2,5), random.randint(2,5), random.randint(2,5)
    code = f"print({a} + {b} * {c})"
    ans = str(a + b * c)
    wrong = str((a+b) * c)
    return code, [ans, wrong, str(a*b+c), str(a+b+c)], ans

# Q3: Strings
def g7_q3_concat():
    s1 = random_string(random.randint(3, 6))
    s2 = random_string(random.randint(3, 6))
    sep = random.choice([' ', '-', '', '_'])
    if sep:
        code = f"a = '{s1}'\nb = '{s2}'\nprint(a + '{sep}' + b)"
        ans = f"'{s1}{sep}{s2}'"
    else:
        code = f"a = '{s1}'\nb = '{s2}'\nprint(a + b)"
        ans = f"'{s1}{s2}'"
    return code, [ans, f"'{s1} {s2}'", f"'{s2}{s1}'", "Error"], ans

def g7_q3_indexing():
    word = random_string(random.randint(6, 12))
    idx = random.randint(0, len(word)-1)
    neg_idx = random.randint(1, len(word)) * -1
    
    if random.choice([True, False]):
        code = f"s = '{word}'\nprint(s[{idx}])"
        ans = f"'{word[idx]}'"
        wrongs = [f"'{word[i]}'" for i in range(len(word)) if i != idx]
    else:
        code = f"s = '{word}'\nprint(s[{neg_idx}])"
        ans = f"'{word[neg_idx]}'"
        wrongs = [f"'{word[i]}'" for i in range(len(word))]
        
    random.shuffle(wrongs)
    return code, [ans] + wrongs[:3], ans

# Q4: Math & Logic
def g7_q4_logic():
    a = random.randint(1, 100)
    b = random.randint(1, 100)
    op = random.choice(['>', '<', '==', '!='])
    
    code = f"print({a} {op} {b})"
    if op == '>': res = a > b
    elif op == '<': res = a < b
    elif op == '==': res = a == b
    else: res = a != b
    
    return code, ["True", "False", "Error", "None"], str(res)

# ================= GRADE 8 GENERATORS =================
# Q1: Conditionals
def g8_q1_if():
    val = random.randint(1, 50)
    limit = random.randint(20, 40)
    code = f"x = {val}\nif x > {limit}:\n    print('A')\nelse:\n    print('B')"
    ans = "'A'" if val > limit else "'B'"
    return code, ["'A'", "'B'", "Error", "None"], ans

def g8_q1_bool_logic():
    x = random.choice([True, False])
    y = random.choice([True, False])
    op = random.choice(['and', 'or'])
    code = f"x = {x}\ny = {y}\nprint(x {op} y)"
    res = (x and y) if op == 'and' else (x or y)
    return code, ["True", "False", "Error", "None"], str(res)

# Q2: For loops
def g8_q2_range():
    start = random.randint(0, 50)
    end = start + random.randint(10, 50)
    step = random.randint(1, 5)
    code = f"s = 0\nfor i in range({start}, {end}, {step}):\n    s += 1\nprint(s)"
    count = len(range(start, end, step))
    return code, [str(count), str(count+1), str(end), str(start)], str(count)

def g8_q2_loop_val():
    target = random.randint(10, 100)
    v = random_var_name()
    code = f"{v} = 0\nfor i in range({target}):\n    {v} = i\nprint({v})"
    return code, [str(target-1), str(target), "0", "None"], str(target-1)

# Q3: Lists
def g8_q3_list_access():
    lst = [random.randint(10, 99) for _ in range(4)]
    idx = random.randint(-4, 3)
    code = f"L = {lst}\nprint(L[{idx}])"
    ans = str(lst[idx])
    wrongs = [str(n) for n in lst if n != lst[idx]]
    while len(wrongs) < 3: wrongs.append(str(random.randint(10,99)))
    return code, [ans] + wrongs, ans

def g8_q3_list_slice():
    lst = list(range(1, 10))
    start = random.randint(0, 3)
    end = random.randint(5, 8)
    code = f"L = {lst}\nprint(L[{start}:{end}])"
    ans = str(lst[start:end])
    wrong1 = str(lst[start:end+1])
    wrong2 = str(lst[start+1:end])
    return code, [ans, wrong1, wrong2, "Error"], ans

# Q4: While
def g8_q4_while():
    i_start = random.randint(1, 50)
    limit = i_start + random.randint(5, 20)
    code = f"i = {i_start}\nwhile i < {limit}:\n    i += 1\nprint(i)"
    return code, [str(limit), str(limit-1), str(limit+1), "Infinite Loop"], str(limit)

def g8_q4_break():
    limit = random.randint(10, 50)
    stop = random.randint(2, limit-2)
    code = f"for i in range({limit}):\n    if i == {stop}:\n        break\nprint(i)"
    return code, [str(stop), str(stop-1), str(limit), "Error"], str(stop)

# ================= GRADE 9 GENERATORS =================
# Q1: Dicts
def g9_q1_dict_get():
    d = {'a': 1, 'b': 2, 'c': 3}
    k = random.choice(['a', 'b'])
    code = f"d = {d}\nprint(d['{k}'])"
    ans = str(d[k])
    return code, ["1", "2", "3", "KeyError"], ans

def g9_q1_set_len():
    lst = [1, 2, 2, 3, 3, 3, 4]
    random.shuffle(lst)
    code = f"nums = {lst}\nprint(len(set(nums)))"
    ans = "4"
    return code, ["4", "7", "3", "Error"], ans

# Q2: Functions
def g9_q2_simple_func():
    m = random.randint(2, 20)
    fname = random.choice(['calc', 'do_it', 'compute', 'f', 'g'])
    arg = random.choice([10, 20, 5, 2])
    code = f"def {fname}(x):\n    return x * {m}\nprint({fname}({arg}))"
    ans = str(arg * m)
    return code, [ans, str(arg+m), str(arg), "Error"], ans

def g9_q2_default_args():
    val = random.randint(2, 10)
    exp = random.randint(2, 4)
    fname = random.choice(['power', 'proc', 'op'])
    code = f"def {fname}(base, exp={exp}):\n    return base ** exp\nprint({fname}({val}))"
    ans = str(val**exp)
    return code, [ans, str(val), str(val*2), "Error"], ans

# Q3: Methods exceptions
def g9_q3_str_methods():
    w = random_string(random.randint(5, 10))
    # Mix case
    w = "".join(c.upper() if i%2==0 else c.lower() for i,c in enumerate(w))
    
    method = random.choice(['lower', 'upper', 'swapcase', 'capitalize'])
    code = f"s = '{w}'\nprint(s.{method}())"
    
    if method == 'lower': ans = f"'{w.lower()}'"
    elif method == 'upper': ans = f"'{w.upper()}'"
    elif method == 'swapcase': ans = f"'{w.swapcase()}'"
    else: ans = f"'{w.capitalize()}'"

    return code, [ans, f"'{w}'", "Error", "None"], ans

def g9_q3_try_except():
    v1 = random.randint(1,100)
    err = random.choice(['ZeroDivisionError', 'ValueError', 'TypeError'])
    caught = random.choice([True, False])
    
    if caught:
        code = f"try:\n    x = 1 / 0\nexcept {err}:\n    print('A')\nexcept ZeroDivisionError:\n    print('B')"
        ans = "'B'" if err != 'ZeroDivisionError' else "'A'"
    else:
        # Generic
        code = f"try:\n    x = int('abc')\nexcept ValueError:\n    print('Caught')\nexcept:\n    print('Other')"
        ans = "'Caught'"
        
    return code, ["'A'", "'B'", "'Caught'", "'Other'"], ans

# Q4: Modules
def g9_q4_math():
    funcs = ['sqrt', 'ceil', 'floor', 'fabs']
    f = random.choice(funcs)
    val = random.randint(10, 100)
    if f == 'sqrt':
        # Make it NOT perfect square usually, cast to int
        code = f"import math\nprint(int(math.sqrt({val})))"
        ans = str(int(math.sqrt(val)))
    else:
        val = round(random.uniform(1.1, 99.9), 2)
        code = f"import math\nprint(math.{f}({val}))"
        if f == 'ceil': ans = str(math.ceil(val))
        elif f == 'floor': ans = str(math.floor(val))
        else: ans = str(math.fabs(val))
        
    return code, [ans, str(val), "Error", "None"], ans

def g9_q4_algo():
    # Simple array sum or max
    lst = [random.randint(1,20) for _ in range(3)]
    op = random.choice(['sum', 'max', 'min'])
    code = f"nums = {lst}\nprint({op}(nums))"
    if op == 'sum': ans = str(sum(lst))
    elif op == 'max': ans = str(max(lst))
    else: ans = str(min(lst))
    return code, [ans, "0", "None", "Error"], ans


# ================= MAIN LOGIC =================

def get_generators(grade, quarter):
    # Mapping curriculum
    if grade == 7:
        if quarter == 1: return [g7_q1_vars, g7_q1_types]
        if quarter == 2: return [g7_q2_arithmetic, g7_q2_priority]
        if quarter == 3: return [g7_q3_concat, g7_q3_indexing]
        if quarter == 4: return [g7_q4_logic]
    elif grade == 8:
        if quarter == 1: return [g8_q1_if, g8_q1_bool_logic]
        if quarter == 2: return [g8_q2_range, g8_q2_loop_val]
        if quarter == 3: return [g8_q3_list_access, g8_q3_list_slice]
        if quarter == 4: return [g8_q4_while, g8_q4_break]
    elif grade == 9:
        if quarter == 1: return [g9_q1_dict_get, g9_q1_set_len]
        if quarter == 2: return [g9_q2_simple_func, g9_q2_default_args]
        if quarter == 3: return [g9_q3_str_methods, g9_q3_try_except]
        if quarter == 4: return [g9_q4_math, g9_q4_algo]
    return []

def main():
    with app.app_context():
        print("Starting comprehensive generation...")
        subject = get_or_create_subject()
        
        # 1. Clean up old questions for these grades (Boshqatdan)
        print("Cleaning old questions for Grades 7, 8, 9...")
        deleted = Question.query.filter(
            Question.subject_id == subject.id,
            Question.grade.in_(GRADES)
        ).delete(synchronize_session=False)
        db.session.commit()
        print(f"Deleted {deleted} old questions.")

        all_new_questions = []

        # 2. Generate new questions
        for grade in GRADES:
            for quarter in QUARTERS:
                print(f"Generating Grade {grade} Quarter {quarter}...")
                generators = get_generators(grade, quarter)
                
                if not generators:
                    # Fallback or mixed revision if no specific generator
                    # (Should not happen with current map, but good safety)
                    print(f"  Warning: No generators for G{grade} Q{quarter}")
                    continue
                    
                q_list = []
                attempts = 0
                max_attempts = QUESTIONS_PER_QUARTER * 10
                
                while len(q_list) < QUESTIONS_PER_QUARTER and attempts < max_attempts:
                    attempts += 1
                    gen_func = random.choice(generators)
                    try:
                        code, opts, ans = gen_func()
                        q_text = f"Quyidagi kod natijasi nima?\n\n```python\n{code}\n```"
                        add_question(q_list, subject.id, grade, quarter, q_text, opts, ans)
                    except Exception as e:
                        # Error in generation logic, skip
                        pass
                
                print(f"  Generated {len(q_list)} unique questions.")
                all_new_questions.extend(q_list)

        # 3. Bulk Save
        print(f"Saving {len(all_new_questions)} questions to database...")
        # Chunked save for SQLite safety
        chunk_size = 500
        for i in range(0, len(all_new_questions), chunk_size):
            db.session.bulk_save_objects(all_new_questions[i:i+chunk_size])
            db.session.commit()
            print(f"  Saved chunk {i}-{i+chunk_size}")

        print("Done! Database updated.")

if __name__ == '__main__':
    main()
