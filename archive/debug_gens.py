import random
import math
import datetime

# Copy generators here
def gen_function_def():
    # Regular, args, kwargs, default
    mode = random.choice(['simple', 'default', 'args'])
    
    if mode == 'simple':
        a, b = random.randint(1,5), random.randint(1,5)
        code = f"def add(x, y):\n    return x + y\nprint(add({a}, {b}))"
        ans = str(a+b)
        wrongs = [str(a*b), str(a-b), "Error"]
    elif mode == 'default':
        val = random.randint(2,5)
        code = f"def power(x, n=2):\n    return x ** n\nprint(power({val}))"
        ans = str(val**2)
        wrongs = [str(val), str(val*2), "Error"]
    else:
        # args
        nums = random.sample(range(1,5), 3)
        code = f"def total(*args):\n    return sum(args)\nprint(total({', '.join(map(str, nums))}))"
        ans = str(sum(nums))
        wrongs = [str(len(nums)), "Error", "None"]
        
    return code, [ans] + wrongs, ans

def gen_recursion_simple():
    # Factorial or sum
    n = random.randint(3, 5)
    if random.random() > 0.5:
        # Sum 1 to n
        code = f"def s(n):\n    if n == 1: return 1\n    return n + s(n-1)\nprint(s({n}))"
        ans = str(sum(range(1, n+1)))
    else:
        # Factorial
        code = f"def f(n):\n    if n == 1: return 1\n    return n * f(n-1)\nprint(f({n}))"
        ans = str(math.factorial(n))
        
    wrongs = [str(int(ans)-1), str(int(ans)+n), "Error", "Infinite Loop"]
    return code, [ans] + wrongs, ans

def gen_modules():
    mod = random.choice(['math', 'random', 'datetime'])
    if mod == 'math':
        val = random.choice([16, 25, 36, 49])
        code = f"import math\nprint(int(math.sqrt({val})))"
        ans = str(int(math.sqrt(val)))
        wrongs = [str(val//2), str(val), "Error"]
    elif mod == 'random':
        code = f"import random\n# range 1 to 1\nprint(random.randint(1, 1))"
        ans = "1"
        wrongs = ["0", "2", "Error"]
    else:
        # datetime year/month implies knowing current date? 
        # Better: basic object creation or time
        code = "import datetime\nd = datetime.date(2023, 1, 1)\nprint(d.year)"
        ans = "2023"
        wrongs = ["1", "2024", "Error"]
        
    return code, [ans] + wrongs, ans

def test():
    gens = [gen_function_def, gen_recursion_simple, gen_modules]
    for g in gens:
        print(f"Testing {g.__name__}...")
        try:
            c, o, a = g()
            print("Success")
            # print(c)
            # print(o)
        except Exception as e:
            print(f"FAILED {g.__name__}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test()
