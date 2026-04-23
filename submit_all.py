"""
Barcha 100 masala uchun to'g'ri Python kodi yozib judge orqali yuborish.
"""
import json
from app import app
from models import db, ArenaUser, ArenaProblem, ArenaSubmission
from judge import judge as judge_code

SOLUTIONS = {
"A001": """\
a = int(input())
b = int(input())
print(a + b)
""",
"A002": """\
a = int(input())
b = int(input())
print(a - b)
""",
"A003": """\
a = int(input())
b = int(input())
print(a * b)
""",
"A004": """\
a = int(input())
b = int(input())
print(f"{a / b:.2f}")
""",
"A005": """\
a = int(input())
b = int(input())
print(a // b)
print(a % b)
""",
"A006": """\
n = int(input())
print(n * n)
print(n * n * n)
""",
"A007": """\
a = float(input())
b = float(input())
c = float(input())
print(f"{(a + b + c) / 3:.2f}")
""",
"A008": """\
r = float(input())
print(f"{3.14159265358979 * r * r:.2f}")
""",
"A009": """\
a = float(input())
h = float(input())
print(f"{a * h / 2:.2f}")
""",
"A010": """\
a = int(input())
b = int(input())
print(2 * (a + b))
""",
"A011": """\
n = int(input())
if n > 0:
    print('musbat')
elif n < 0:
    print('manfiy')
else:
    print('nol')
""",
"A012": """\
n = int(input())
print('Juft' if n % 2 == 0 else 'Toq')
""",
"A013": """\
a = int(input())
b = int(input())
print(a if a >= b else b)
""",
"A014": """\
a = int(input())
b = int(input())
c = int(input())
m = a
if b < m:
    m = b
if c < m:
    m = c
print(m)
""",
"A015": """\
n = int(input())
print('Ha' if 10 < n < 100 else "Yo'q")
""",
"A016": """\
a = int(input())
b = int(input())
c = int(input())
if a + b > c and b + c > a and a + c > b:
    print('Ha')
else:
    print("Yo'q")
""",
"A017": """\
y = int(input())
if (y % 4 == 0 and y % 100 != 0) or y % 400 == 0:
    print('Ha')
else:
    print("Yo'q")
""",
"A018": """\
c = input()
if c.isalpha():
    print('Harf')
elif c.isdigit():
    print('Raqam')
else:
    print('Boshqa')
""",
"A019": """\
n = int(input())
if n >= 90:
    print('A')
elif n >= 75:
    print('B')
elif n >= 60:
    print('C')
elif n >= 40:
    print('D')
else:
    print('F')
""",
"A020": """\
n = int(input())
months = ['Yanvar','Fevral','Mart','Aprel','May','Iyun',
          'Iyul','Avgust','Sentabr','Oktabr','Noyabr','Dekabr']
print(months[n - 1])
""",
"A021": """\
n = int(input())
print(' '.join(str(i) for i in range(1, n + 1)))
""",
"A022": """\
n = int(input())
print(n * (n + 1) // 2)
""",
"A023": """\
n = int(input())
result = 1
for i in range(1, n + 1):
    result *= i
print(result)
""",
"A024": """\
n = int(input())
total = 0
for _ in range(n):
    total += int(input())
print(total)
""",
"A025": """\
n = int(input())
nums = list(map(int, input().split()))
m = nums[0]
for x in nums[1:]:
    if x > m:
        m = x
print(m)
""",
"A026": """\
n = int(input())
nums = list(map(int, input().split()))
count = 0
for x in nums:
    if x % 2 == 0:
        count += 1
print(count)
""",
"A027": """\
n = int(input())
count = 0
for i in range(1, n + 1):
    if n % i == 0:
        count += 1
print(count)
""",
"A028": """\
n = int(input())
if n < 2:
    print("Yo'q")
else:
    is_prime = True
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            is_prime = False
            break
    print('Ha' if is_prime else "Yo'q")
""",
"A029": """\
n = input().strip()
print(sum(int(c) for c in n))
""",
"A030": """\
n = input().strip()
print(int(n[::-1]))
""",
"A031": """\
n = input().strip()
print('YES' if n == n[::-1] else 'NO')
""",
"A032": """\
n = int(input())
a, b = 1, 1
for _ in range(n - 1):
    a, b = b, a + b
print(a)
""",
"A033": """\
n = int(input())
if n == 0:
    print(0)
else:
    result = ''
    while n > 0:
        result = str(n % 2) + result
        n //= 2
    print(result)
""",
"A034": """\
a = int(input())
b = int(input())
while b:
    a, b = b, a % b
print(a)
""",
"A035": """\
a = int(input())
b = int(input())
x, y = a, b
while y:
    x, y = y, x % y
print(a * b // x)
""",
"A036": """\
n = int(input())
s = 0.0
for i in range(1, n + 1):
    s += 1 / i
print(f"{s:.4f}")
""",
"A037": """\
a = int(input())
b = int(input())
result = 1
for _ in range(b):
    result *= a
print(result)
""",
"A038": """\
n = int(input())
words = ['nol', 'bir', 'ikki', 'uch', "to'rt", 'besh', 'olti', 'yetti', 'sakkiz', "to'qqiz"]
print(words[n])
""",
"A039": """\
n = int(input())
nums = list(map(int, input().split()))
seen = set()
for x in nums:
    if x in seen:
        print(x)
        break
    seen.add(x)
""",
"A040": """\
n = int(input())
nums = list(map(int, input().split()))
max_len = 1
cur_len = 1
for i in range(1, n):
    if nums[i] > nums[i - 1]:
        cur_len += 1
        if cur_len > max_len:
            max_len = cur_len
    else:
        cur_len = 1
print(max_len)
""",
"A041": """\
n = int(input())
nums = list(map(int, input().split()))
m = nums[0]
for x in nums[1:]:
    if x > m:
        m = x
print(m)
""",
"A042": """\
n = int(input())
nums = list(map(int, input().split()))
result = []
for i in range(n - 1, -1, -1):
    result.append(nums[i])
print(' '.join(map(str, result)))
""",
"A043": """\
n = int(input())
nums = list(map(int, input().split()))
print(sum(1 for x in nums if x % 2 == 0))
""",
"A044": """\
n = int(input())
nums = list(map(int, input().split()))
print(f"{sum(nums) / n:.2f}")
""",
"A045": """\
n = int(input())
nums = list(map(int, input().split()))
for i in range(n):
    for j in range(n - i - 1):
        if nums[j] > nums[j + 1]:
            nums[j], nums[j + 1] = nums[j + 1], nums[j]
print(' '.join(map(str, nums)))
""",
"A046": """\
n = int(input())
nums = list(map(int, input().split()))
k = int(input())
print('Ha' if k in nums else "Yo'q")
""",
"A047": """\
n = int(input())
nums = list(map(int, input().split()))
from collections import Counter
c = Counter(nums)
print(sum(1 for v in c.values() if v >= 2))
""",
"A048": """\
n1 = int(input())
a = list(map(int, input().split()))
n2 = int(input())
b = list(map(int, input().split()))
print(' '.join(map(str, a + b)))
""",
"A049": """\
n = int(input())
nums = list(map(int, input().split()))
print(max(nums) - min(nums))
""",
"A050": """\
line1 = input().split()
n, k = int(line1[0]), int(line1[1])
nums = list(map(int, input().split()))
k = k % n
result = nums[-k:] + nums[:-k] if k else nums[:]
print(' '.join(map(str, result)))
""",
"A051": """\
n = int(input())
nums = list(map(int, input().split()))
print(nums.count(0))
""",
"A052": """\
n = int(input())
nums = list(map(int, input().split()))
pos = sum(1 for x in nums if x > 0)
neg = sum(1 for x in nums if x < 0)
print(pos)
print(neg)
""",
"A053": """\
n = int(input())
nums = list(map(int, input().split()))
print(' '.join(str(x * x) for x in nums))
""",
"A054": """\
n = int(input())
nums = list(map(int, input().split()))
result = [nums[i] for i in range(1, n, 2)]
print(' '.join(map(str, result)))
""",
"A055": """\
n = int(input())
nums = list(map(int, input().split()))
result = [nums[i] + nums[i + 1] for i in range(n - 1)]
print(' '.join(map(str, result)))
""",
"A056": """\
n = int(input())
nums = list(map(int, input().split()))
mid = (n + 1) // 2
print(' '.join(map(str, nums[:mid])))
print(' '.join(map(str, nums[mid:])))
""",
"A057": """\
n = int(input())
nums = list(map(int, input().split()))
max_len = 1
cur_len = 1
for i in range(1, n):
    if nums[i] > nums[i - 1]:
        cur_len += 1
        if cur_len > max_len:
            max_len = cur_len
    else:
        cur_len = 1
print(max_len)
""",
"A058": """\
n = int(input())
nums = list(map(int, input().split()))
i, j = map(int, input().split())
nums[i], nums[j] = nums[j], nums[i]
print(' '.join(map(str, nums)))
""",
"A059": """\
n = int(input())
nums = list(map(int, input().split()))
print(nums[n // 2])
""",
"A060": """\
line1 = input().split()
n, k = int(line1[0]), int(line1[1])
nums = list(map(int, input().split()))
k = k % n
result = nums[k:] + nums[:k]
print(' '.join(map(str, result)))
""",
"A061": """\
s = input()
count = 0
for _ in s:
    count += 1
print(count)
""",
"A062": """\
s = input()
vowels = 'aeiouAEIOU'
print(sum(1 for c in s if c in vowels))
""",
"A063": """\
s = input()
result = ''
for i in range(len(s) - 1, -1, -1):
    result += s[i]
print(result)
""",
"A064": """\
s = input()
filtered = ''.join(c.lower() for c in s if c.isalpha())
print('YES' if filtered == filtered[::-1] else 'NO')
""",
"A065": """\
s = input()
print(len(s.split()))
""",
"A066": """\
s = input()
print(sum(1 for c in s if c.isupper()))
""",
"A067": """\
s = input()
print(sum(1 for c in s if c.isdigit()))
""",
"A068": """\
s = input()
old = input()
new = input()
print(s.replace(old, new))
""",
"A069": """\
s = input()
from collections import Counter
c = Counter(s)
max_count = max(c.values())
candidates = [ch for ch, cnt in c.items() if cnt == max_count]
print(min(candidates))
""",
"A070": """\
s = input()
for word in s.split():
    print(word)
""",
"A071": """\
n = int(input())
words = [input() for _ in range(n)]
print(' '.join(words))
""",
"A072": """\
s = input()
words = s.split()
print(' '.join(reversed(words)))
""",
"A073": """\
s = input()
count = 0
ok = True
for c in s:
    if c == '(':
        count += 1
    else:
        count -= 1
    if count < 0:
        ok = False
        break
print('Ha' if ok and count == 0 else "Yo'q")
""",
"A074": """\
s = input()
from collections import Counter
c = Counter(s)
print(sum(1 for v in c.values() if v >= 2))
""",
"A075": """\
s = input()
words = s.split()
result = words[0]
for w in words[1:]:
    if len(w) > len(result):
        result = w
print(result)
""",
"A076": """\
s = input()
from collections import Counter
c = Counter(s.split())
for w in sorted(c.keys()):
    print(f"{w}: {c[w]}")
""",
"A077": """\
s = input()
print(' '.join(sorted(s.split())))
""",
"A078": """\
s = input()
words = s.split()
print(' '.join(sorted(words, key=lambda w: (len(w), w))))
""",
"A079": """\
s = input()
print(s.upper())
""",
"A080": """\
s = input()
print(s.title())
""",
"A081": """\
n = int(input())
nums = list(map(int, input().split()))
k = int(input())
lo, hi = 0, n - 1
result = -1
while lo <= hi:
    mid = (lo + hi) // 2
    if nums[mid] == k:
        result = mid
        break
    elif nums[mid] < k:
        lo = mid + 1
    else:
        hi = mid - 1
print(result)
""",
"A082": """\
n = int(input())
nums = list(map(int, input().split()))
swaps = 0
for i in range(n):
    for j in range(n - i - 1):
        if nums[j] > nums[j + 1]:
            nums[j], nums[j + 1] = nums[j + 1], nums[j]
            swaps += 1
print(swaps)
print(' '.join(map(str, nums)))
""",
"A083": """\
import sys
sys.setrecursionlimit(100000)
def fact(n):
    if n <= 1:
        return 1
    return n * fact(n - 1)
n = int(input())
print(fact(n))
""",
"A084": """\
import sys
sys.setrecursionlimit(100000)
memo = {}
def fib(n):
    if n in memo:
        return memo[n]
    if n <= 2:
        return 1
    memo[n] = fib(n - 1) + fib(n - 2)
    return memo[n]
n = int(input())
print(fib(n))
""",
"A085": """\
n = int(input())
print(2 ** n - 1)
""",
"A086": """\
n = int(input())
factors = []
d = 2
while d * d <= n:
    while n % d == 0:
        factors.append(d)
        n //= d
    d += 1
if n > 1:
    factors.append(n)
print(' '.join(map(str, factors)))
""",
"A087": """\
n = int(input())
nums = list(map(int, input().split()))
t = int(input())
closest = nums[0]
for x in nums:
    d_x = abs(x - t)
    d_c = abs(closest - t)
    if d_x < d_c or (d_x == d_c and x < closest):
        closest = x
print(closest)
""",
"A088": """\
n = int(input())
nums = list(map(int, input().split()))
unique = sorted(set(nums), reverse=True)
print(unique[0])
print(unique[1])
""",
"A089": """\
n = int(input())
nums = list(map(int, input().split()))
unique = sorted(set(nums))
print(unique[0])
print(unique[1])
""",
"A090": """\
n = int(input())
nums = list(map(int, input().split()))
t = int(input())
count = 0
for i in range(n):
    for j in range(i + 1, n):
        if nums[i] + nums[j] == t:
            count += 1
print(count)
""",
"A091": """\
n, m = map(int, input().split())
mat = [list(map(int, input().split())) for _ in range(n)]
for j in range(m):
    print(' '.join(str(mat[i][j]) for i in range(n)))
""",
"A092": """\
n = int(input())
A = [list(map(int, input().split())) for _ in range(n)]
B = [list(map(int, input().split())) for _ in range(n)]
for i in range(n):
    row = [sum(A[i][k] * B[k][j] for k in range(n)) for j in range(n)]
    print(' '.join(map(str, row)))
""",
"A093": """\
n = int(input())
mat = [list(map(int, input().split())) for _ in range(n)]
if n == 2:
    print(mat[0][0] * mat[1][1] - mat[0][1] * mat[1][0])
else:
    a = mat[0]
    det = (a[0] * (mat[1][1] * mat[2][2] - mat[1][2] * mat[2][1])
           - a[1] * (mat[1][0] * mat[2][2] - mat[1][2] * mat[2][0])
           + a[2] * (mat[1][0] * mat[2][1] - mat[1][1] * mat[2][0]))
    print(det)
""",
"A094": """\
s1 = input()
s2 = input()
m, n = len(s1), len(s2)
dp = [[0] * (n + 1) for _ in range(m + 1)]
for i in range(1, m + 1):
    for j in range(1, n + 1):
        if s1[i - 1] == s2[j - 1]:
            dp[i][j] = dp[i - 1][j - 1] + 1
        else:
            dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
print(dp[m][n])
""",
"A095": """\
n = int(input())
vals = [(1000,'M'),(900,'CM'),(500,'D'),(400,'CD'),(100,'C'),(90,'XC'),
        (50,'L'),(40,'XL'),(10,'X'),(9,'IX'),(5,'V'),(4,'IV'),(1,'I')]
result = ''
for v, s in vals:
    while n >= v:
        result += s
        n -= v
print(result)
""",
"A096": """\
s = input()
vals = {'I':1,'V':5,'X':10,'L':50,'C':100,'D':500,'M':1000}
result = 0
for i in range(len(s)):
    if i + 1 < len(s) and vals[s[i]] < vals[s[i + 1]]:
        result -= vals[s[i]]
    else:
        result += vals[s[i]]
print(result)
""",
"A097": """\
s = input()
result = ''
i = 0
while i < len(s):
    c = s[i]
    count = 1
    while i + count < len(s) and s[i + count] == c:
        count += 1
    result += c + str(count)
    i += count
print(result)
""",
"A098": """\
s = input()
result = ''
i = 0
while i < len(s):
    c = s[i]
    i += 1
    num = ''
    while i < len(s) and s[i].isdigit():
        num += s[i]
        i += 1
    result += c * int(num)
print(result)
""",
"A099": """\
s1 = input().lower()
s2 = input().lower()
from collections import Counter
print('YES' if Counter(s1) == Counter(s2) else 'NO')
""",
"A100": """\
s = input()
stack = []
pairs = {')': '(', ']': '[', '}': '{'}
ok = True
for c in s:
    if c in '([{':
        stack.append(c)
    elif c in ')]}':
        if not stack or stack[-1] != pairs[c]:
            ok = False
            break
        stack.pop()
if stack:
    ok = False
print('Ha' if ok else "Yo'q")
""",
}


def diff_stars(difficulty):
    return {'easy': 10, 'medium': 25, 'hard': 50}.get(difficulty, 10)


def run_submission(user, problem, code, language='python'):
    try:
        examples = json.loads(problem.examples or '[]')
    except Exception:
        examples = []

    try:
        hidden_raw = json.loads(problem.hidden_tests or '[]')
    except Exception:
        hidden_raw = []

    example_tests = [{'input': ex.get('input', ''), 'output': ex.get('output', '')}
                     for ex in examples if ex.get('output', '').strip()]

    hidden_tests = [{'input': t.get('input', ''), 'output': t.get('output', '')}
                    for t in hidden_raw if t.get('output', '').strip()]

    if not hidden_tests and (problem.correct_answer or '').strip():
        hidden_tests = [{'input': '', 'output': problem.correct_answer.strip()}]

    all_tests = example_tests + hidden_tests
    if not all_tests:
        return None

    time_limit = float(problem.time_limit or 5)
    final_verdict = 'AC'
    final_output  = ''
    final_error   = ''
    final_time    = 0.0
    passed_count  = 0
    total_count   = len(all_tests)

    for t in all_tests:
        result = judge_code(code, language, t['input'], t['output'], time_limit)
        final_time = max(final_time, result.get('time', 0))
        if result['verdict'] == 'AC':
            passed_count += 1
        else:
            if final_verdict == 'AC':
                final_verdict = result['verdict']
                final_output  = result.get('output', '')
                final_error   = result.get('error', '')
            if result['verdict'] in ('TLE', 'CE'):
                break

    pts = diff_stars(problem.difficulty) if final_verdict == 'AC' else 0

    already_ac = (ArenaSubmission.query
                  .filter_by(user_id=user.id, problem_id=problem.id, status='AC')
                  .first())

    sub = ArenaSubmission(
        user_id=user.id,
        problem_id=problem.id,
        code=code,
        language=language,
        answer=final_output[:2000],
        status=final_verdict,
        time_used=round(final_time, 3),
        error_msg=final_error[:1000],
        tests_passed=passed_count,
        tests_total=total_count,
        stars=pts,
    )
    db.session.add(sub)

    problem.submission_count += 1
    if final_verdict == 'AC':
        problem.accepted_count += 1

    if final_verdict == 'AC' and not already_ac:
        user.problems_solved += 1
        user.rating      += pts
        user.total_stars += pts

    db.session.commit()
    return final_verdict, passed_count, total_count


if __name__ == '__main__':
    with app.app_context():
        user = ArenaUser.query.filter_by(username='user').first()
        problems = ArenaProblem.query.filter_by(is_active=True).order_by(ArenaProblem.code).all()

        already_ac_ids = set(
            r[0] for r in
            db.session.query(ArenaSubmission.problem_id)
            .filter_by(user_id=user.id, status='AC').distinct().all()
        )

        ok = 0
        fail = 0
        skip = 0

        for p in problems:
            code = SOLUTIONS.get(p.code)
            if not code:
                print(f"  [{p.code}] Kod topilmadi — o'tkazib yuborildi")
                skip += 1
                continue

            if p.id in already_ac_ids:
                print(f"  [{p.code}] Allaqachon AC — o'tkazib yuborildi")
                skip += 1
                continue

            result = run_submission(user, p, code)
            if result is None:
                print(f"  [{p.code}] Test topilmadi")
                skip += 1
                continue

            verdict, passed, total = result
            if verdict == 'AC':
                print(f"  [{p.code}] AC  {passed}/{total}")
                ok += 1
            else:
                print(f"  [{p.code}] {verdict}  {passed}/{total}")
                fail += 1

        print(f"\nNatija: AC={ok}, WA/TLE={fail}, Skip={skip}")
        print(f"User: solved={user.problems_solved}, rating={user.rating}")
