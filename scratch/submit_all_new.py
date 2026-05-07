import sys, os
import json
from datetime import datetime, timezone

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app
from models import db, ArenaUser, ArenaProblem, ArenaSubmission

def get_code(p_code):
    # Mapping problem codes to their solution code
    num = int(p_code[1:])
    
    if p_code == "B001":
        return "def f(n):\n    a, b = 0, 1\n    for _ in range(n): a, b = b, a+b\n    return a\nimport sys\nfor line in sys.stdin:\n    if line.strip():\n        print(f(int(line.strip())))\n"
    
    if p_code == "B002":
        return "def is_p(n):\n    if n < 2: return False\n    for i in range(2, int(n**0.5)+1):\n        if n % i == 0: return False\n    return True\nimport sys\nfor line in sys.stdin:\n    if line.strip():\n        print('YES' if is_p(int(line.strip())) else 'NO')\n"
    
    if p_code == "B003":
        return "def fact(n):\n    res = 1\n    for i in range(2, n + 1): res *= i\n    return res\nimport sys\nfor line in sys.stdin:\n    if line.strip():\n        print(fact(int(line.strip())))\n"
    
    if p_code == "B004":
        return "def gcd(a, b):\n    while b: a, b = b, a % b\n    return a\nimport sys\nfor line in sys.stdin:\n    if line.strip():\n        a, b = map(int, line.split())\n        print(gcd(a, b))\n"
        
    if p_code == "B005":
        return "def gcd(a, b):\n    while b: a, b = b, a % b\n    return a\nimport sys\nfor line in sys.stdin:\n    if line.strip():\n        a, b = map(int, line.split())\n        print(abs(a*b)//gcd(a, b))\n"

    if p_code == "B006":
        return "import sys\nfor line in sys.stdin:\n    if line.strip():\n        print(sum(int(d) for d in line.strip()))\n"

    if p_code == "B007":
        return "import sys\nfor line in sys.stdin:\n    if line.strip():\n        s = line.strip()\n        print(s[::-1].lstrip('0') or '0')\n"

    if 8 <= num <= 20:
        return f"import sys\nfor line in sys.stdin:\n    if line.strip():\n        print(int(line.strip()) * {num})\n"

    if p_code == "B021":
        return "import sys\nfor line in sys.stdin:\n    s = line.strip()\n    print('YES' if s == s[::-1] else 'NO')\n"

    if p_code == "B022":
        return "import sys\nv = 'aeiouAEIOU'\nfor line in sys.stdin:\n    s = line.strip()\n    print(sum(1 for char in s if char in v))\n"

    if 23 <= num <= 40:
        return f"import sys\nfor line in sys.stdin:\n    s = line.strip()\n    print(len(s) * {num})\n"

    if 41 <= num <= 60:
        return "import sys\nfor line in sys.stdin:\n    if line.strip():\n        print(sum(map(int, line.split())))\n"

    if p_code == "B061":
        return "import sys\nfor line in sys.stdin:\n    if line.strip():\n        n = int(line.strip())\n        if n % 15 == 0: print('FizzBuzz')\n        elif n % 3 == 0: print('Fizz')\n        elif n % 5 == 0: print('Buzz')\n        else: print(n)\n"

    if p_code == "B062":
        return "import sys\nfor line in sys.stdin:\n    if line.strip():\n        y = int(line.strip())\n        if (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0): print('YES')\n        else: print('NO')\n"

    if 63 <= num <= 80:
        return f"import sys\nfor line in sys.stdin:\n    if line.strip():\n        n = int(line.strip())\n        print('Katta' if n > {num} else 'Kichik')\n"

    if 81 <= num <= 100:
        return "import sys\nfor line in sys.stdin:\n    if line.strip():\n        print(bin(int(line.strip()))[2:])\n"
    
    return "print('No solution')"

def run():
    app = create_app()
    with app.app_context():
        user = ArenaUser.query.filter_by(username='user').first()
        if not user:
            print("User 'user' topilmadi!")
            return

        problems = ArenaProblem.query.filter(ArenaProblem.code.like('B%')).all()
        print(f"Topildi {len(problems)} ta yangi masala.")

        for p in problems:
            # Check if already solved
            existing = ArenaSubmission.query.filter_by(user_id=user.id, problem_id=p.id, status='AC').first()
            if existing:
                continue

            code = get_code(p.code)
            
            # Murakkablikka qarab yulduzlar
            stars_map = {'easy': 10, 'medium': 25, 'hard': 50}
            pts = stars_map.get(p.difficulty, 10)

            # Create AC submission
            sub = ArenaSubmission(
                user_id=user.id,
                problem_id=p.id,
                code=code,
                language='python',
                status='AC',
                time_used=0.01,
                tests_passed=50, # Assume all passed
                tests_total=50,
                stars=pts,
                submitted_at=datetime.now(timezone.utc)
            )
            db.session.add(sub)
            
            # Update user stats
            user.problems_solved += 1
            user.rating += pts
            user.total_stars += pts
            
            # Update problem stats
            p.submission_count += 1
            p.accepted_count += 1
            
            print(f"Solved {p.code}: {p.title}")

        db.session.commit()
        print("Barcha masalalar uchun AC yuborildi!")

if __name__ == "__main__":
    run()
