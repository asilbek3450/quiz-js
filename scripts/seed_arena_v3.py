import random
import sys, os
import json
import math

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app
from models import db, ArenaProblem

PROBLEMS = []

def add_p(code, title, desc, ifmt, ofmt, const, ex, ht, diff, cat, ans):
    PROBLEMS.append({
        "code": code, "title": title, "description": desc,
        "input_format": ifmt, "output_format": ofmt, "constraints": const,
        "examples": ex, "hidden_tests": ht, "difficulty": diff, "category": cat,
        "correct_answer": ans
    })

# --- Generators ---

def gen_fib():
    def f(n):
        a, b = 0, 1
        for _ in range(n): a, b = b, a+b
        return a
    ht = [{"input": str(i), "output": str(f(i))} for i in range(51)]
    add_p("B001", "Fibonachchi ketma-ketligi", "n-chi Fibonachchi sonini toping.", "n butun soni.", "F(n).", "0 <= n <= 50", [{"input": "5", "output": "5"}], ht, "medium", "Aritmetika", "5")

def gen_prime():
    def is_p(n):
        if n < 2: return False
        for i in range(2, int(n**0.5)+1):
            if n % i == 0: return False
        return True
    ht = [{"input": str(i), "output": "YES" if is_p(i) else "NO"} for i in range(1, 101)]
    add_p("B002", "Tublikka tekshirish", "Son tub bo'lsa YES, aks holda NO chiqaring.", "n soni.", "YES/NO", "1 <= n <= 10^9", [{"input": "7", "output": "YES"}], ht, "easy", "Aritmetika", "YES")

def gen_factorial():
    def fact(n): return 1 if n == 0 else n * fact(n-1)
    ht = [{"input": str(i), "output": str(fact(i))} for i in range(21)]
    add_p("B003", "Faktorial", "n! qiymatini hisoblang.", "n soni.", "n!", "0 <= n <= 20", [{"input": "5", "output": "120"}], ht, "easy", "Aritmetika", "120")

def gen_gcd():
    def gcd(a, b):
        while b: a, b = b, a % b
        return a
    ht = [{"input": f"{i} {i*2+3}", "output": str(gcd(i, i*2+3))} for i in range(1, 51)]
    add_p("B004", "EKUB (Greatest Common Divisor)", "Ikki sonning eng katta umumiy bo'luvchisini toping.", "a va b bitta qatorda.", "EKUB(a, b).", "1 <= a, b <= 10^9", [{"input": "12 18", "output": "6"}], ht, "easy", "Aritmetika", "6")

def gen_lcm():
    def gcd(a, b):
        while b: a, b = b, a % b
        return a
    def lcm(a, b): return abs(a*b) // gcd(a, b)
    ht = [{"input": f"{i} {i+5}", "output": str(lcm(i, i+5))} for i in range(1, 51)]
    add_p("B005", "EKUK (Least Common Multiple)", "Ikki sonning eng kichik umumiy karralisini toping.", "a va b bitta qatorda.", "EKUK(a, b).", "1 <= a, b <= 10^9", [{"input": "4 6", "output": "12"}], ht, "easy", "Aritmetika", "12")

def gen_sum_digits():
    def s(n): return sum(int(d) for d in str(n))
    ht = [{"input": str(i*123), "output": str(s(i*123))} for i in range(1, 60)]
    add_p("B006", "Raqamlar yig'indisi", "Berilgan sonning barcha raqamlari yig'indisini toping.", "n soni.", "Yig'indi.", "1 <= n <= 10^18", [{"input": "123", "output": "6"}], ht, "easy", "Aritmetika", "6")

def gen_reverse_num():
    ht = [{"input": str(i*17), "output": str(i*17)[::-1].lstrip('0') or '0'} for i in range(1, 60)]
    add_p("B007", "Sonni teskarisiga o'girish", "Berilgan sonning raqamlarini teskari tartibda chiqaring.", "n soni.", "Teskari son.", "1 <= n <= 10^18", [{"input": "123", "output": "321"}], ht, "easy", "Aritmetika", "321")

def gen_palindrome_str():
    ht = [{"input": s, "output": "YES" if s == s[::-1] else "NO"} for s in ["radar", "hello", "level", "world", "madam", "python", "a", "bb", "abc", "racecar"]]
    for _ in range(40):
        s = "".join(random.choice("abc") for _ in range(5))
        ht.append({"input": s, "output": "YES" if s == s[::-1] else "NO"})
    add_p("B021", "Palindrom satr", "Berilgan satr palindrom bo'lsa YES, aks holda NO chiqaring.", "Satr.", "YES/NO", "uzunlik <= 1000", [{"input": "radar", "output": "YES"}], ht, "easy", "Satrlar", "YES")

def gen_count_vowels():
    v = "aeiouAEIOU"
    def c(s): return sum(1 for char in s if char in v)
    ht = [{"input": s, "output": str(c(s))} for s in ["hello", "apple", "sky", "education", "AEIOU", "123", ""]]
    for _ in range(43):
        s = "".join(random.choice("abcdefg ") for _ in range(10))
        ht.append({"input": s, "output": str(c(s))})
    add_p("B022", "Unli harflar soni", "Satrdagi unli harflar (a, e, i, o, u) sonini hisoblang.", "Satr.", "Soni.", "uzunlik <= 1000", [{"input": "hello", "output": "2"}], ht, "easy", "Satrlar", "2")

def gen_fizzbuzz():
    def fb(n):
        if n % 15 == 0: return "FizzBuzz"
        if n % 3 == 0: return "Fizz"
        if n % 5 == 0: return "Buzz"
        return str(n)
    ht = [{"input": str(i), "output": fb(i)} for i in range(1, 101)]
    add_p("B061", "FizzBuzz", "Son 3 ga bo'linsa Fizz, 5 ga bo'linsa Buzz, har ikkisiga bo'linsa FizzBuzz chiqaring.", "n soni.", "Natija.", "1 <= n <= 1000", [{"input": "3", "output": "Fizz"}, {"input": "5", "output": "Buzz"}], ht, "easy", "Mantiq", "Fizz")

def gen_leap_year():
    def is_l(y): return "YES" if (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0) else "NO"
    ht = [{"input": str(y), "output": is_l(y)} for y in range(1900, 2101)]
    add_p("B062", "Kabisa yili", "Berilgan yil kabisa yili bo'lsa YES, aks holda NO chiqaring.", "Yil.", "YES/NO", "1 <= yil <= 3000", [{"input": "2000", "output": "YES"}, {"input": "2021", "output": "NO"}], ht, "easy", "Mantiq", "YES")

# Helper to generate generic problems quickly
def gen_generic(code, title, desc, func, test_inputs, cat="Algoritm", diff="medium"):
    ht = [{"input": str(i), "output": str(func(i))} for i in test_inputs]
    add_p(code, title, desc, "Kirish ma'lumotlari.", "Natija.", "Cheklovlar.", [{"input": str(test_inputs[0]), "output": str(func(test_inputs[0]))}], ht, diff, cat, str(func(test_inputs[0])))

# Adding 100 problems by repeating logic or creating variants
def fill_100():
    gen_fib()
    gen_prime()
    gen_factorial()
    gen_gcd()
    gen_lcm()
    gen_sum_digits()
    gen_reverse_num()
    # Math 8-20
    for i in range(8, 21):
        gen_generic(f"B{i:03}", f"Aritmetika Masalasi #{i}", f"Sonni {i} ga ko'paytirib natijani chiqaring.", lambda x, i=i: int(x)*i, [j for j in range(50)], "Aritmetika", "easy")
    
    gen_palindrome_str()
    gen_count_vowels()
    # Strings 23-40
    for i in range(23, 41):
        gen_generic(f"B{i:03}", f"Satr Masalasi #{i}", f"Satr uzunligini {i} ga ko'paytirib chiqaring.", lambda x, i=i: len(str(x))*i, ["hello", "python", "world"*i, "a"*i], "Satrlar", "easy")
    
    # Arrays 41-60
    for i in range(41, 61):
        def arr_sum(s): return sum(int(x) for x in s.split())
        ht = [{"input": " ".join(str(random.randint(1, 100)) for _ in range(10)), "output": ""} for _ in range(50)]
        for h in ht: h["output"] = str(arr_sum(h["input"]))
        add_p(f"B{i:03}", f"Massiv Masalasi #{i}", "Berilgan sonlar yig'indisini toping.", "Bo'shliq bilan ajratilgan sonlar.", "Yig'indi.", "N <= 100", [{"input": "1 2 3", "output": "6"}], ht, "easy", "Massivlar", "6")

    gen_fizzbuzz()
    gen_leap_year()
    # Logic 63-80
    for i in range(63, 81):
        gen_generic(f"B{i:03}", f"Mantiq Masalasi #{i}", f"Agar son {i} dan katta bo'lsa 'Katta', aks holda 'Kichik' chiqaring.", lambda x, i=i: "Katta" if int(x) > i else "Kichik", [j for j in range(i-25, i+25)], "Mantiq", "easy")

    # Algorithms 81-100
    for i in range(81, 101):
        gen_generic(f"B{i:03}", f"Algoritm Masalasi #{i}", f"Sonni ikkilik sanoq sistemasida chiqaring.", lambda x: bin(int(x))[2:], [j for j in range(50)], "Algoritmlar", "medium")

fill_100()

def run():
    app = create_app()
    with app.app_context():
        added = 0
        updated = 0
        for p_data in PROBLEMS:
            examples_json = json.dumps(p_data.get("examples", []), ensure_ascii=False)
            hidden_json = json.dumps(p_data.get("hidden_tests", []), ensure_ascii=False)
            existing = ArenaProblem.query.filter_by(code=p_data["code"]).first()
            if existing:
                existing.title = p_data["title"]
                existing.description = p_data["description"]
                existing.input_format = p_data.get("input_format", "")
                existing.output_format = p_data.get("output_format", "")
                existing.constraints = p_data.get("constraints", "")
                existing.examples = examples_json
                existing.hidden_tests = hidden_json
                existing.difficulty = p_data["difficulty"]
                existing.category = p_data["category"]
                existing.correct_answer = p_data["correct_answer"]
                updated += 1
            else:
                prob = ArenaProblem(
                    code=p_data["code"], title=p_data["title"], description=p_data["description"],
                    input_format=p_data.get("input_format", ""), output_format=p_data.get("output_format", ""),
                    constraints=p_data.get("constraints", ""), examples=examples_json, hidden_tests=hidden_json,
                    difficulty=p_data["difficulty"], category=p_data["category"], correct_answer=p_data["correct_answer"],
                    is_active=True
                )
                db.session.add(prob)
                added += 1
        db.session.commit()
        print(f"Bajarildi! Qo'shildi: {added}, Yangilandi: {updated}, Jami: {len(PROBLEMS)}")

if __name__ == "__main__":
    run()
