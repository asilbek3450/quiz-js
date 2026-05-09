"""
Arena uchun 100 ta sifatli LeetCode-easy uslubidagi masala.
Har bir masala unikal — real algoritm/data struktura tushunchasiga asoslangan.
B001-B100 kodlarida saqlanadi.
"""
import sys, os, json, random, math
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app
from models import db, ArenaProblem

random.seed(42)
PROBLEMS = []


def add(code, title, desc, ifmt, ofmt, const, examples, hidden, diff, cat, ans):
    PROBLEMS.append({
        "code": code, "title": title, "description": desc,
        "input_format": ifmt, "output_format": ofmt, "constraints": const,
        "examples": examples, "hidden_tests": hidden,
        "difficulty": diff, "category": cat, "correct_answer": ans,
    })


def gen_tests(generator, solve, n=15):
    """Generate n hidden tests using a generator function and solver."""
    tests = []
    for _ in range(n):
        inp = generator()
        out = solve(inp)
        tests.append({"input": inp, "output": out})
    return tests


# ═══════════════════════════════════════════════════════════════════════════
# MASSIVLAR (15 ta)
# ═══════════════════════════════════════════════════════════════════════════

# B001: Two Sum (LC#1) — find two indices in array that sum to target
def p_b001():
    def solve(inp):
        lines = inp.strip().split('\n')
        nums = list(map(int, lines[0].split()))
        t = int(lines[1])
        seen = {}
        for i, x in enumerate(nums):
            if t - x in seen:
                return f"{seen[t-x]} {i}"
            seen[x] = i
        return "-1"

    examples = [
        {"input": "2 7 11 15\n9", "output": "0 1", "explanation": "nums[0]+nums[1]=2+7=9"},
        {"input": "3 2 4\n6", "output": "1 2", "explanation": "nums[1]+nums[2]=2+4=6"},
    ]
    hidden = []
    for _ in range(55):
        n = random.randint(2, 15)
        nums = [random.randint(-50, 50) for _ in range(n)]
        # ensure a valid pair exists
        i, j = random.sample(range(n), 2)
        target = nums[i] + nums[j]
        inp = f"{' '.join(map(str, nums))}\n{target}"
        hidden.append({"input": inp, "output": solve(inp)})
    add("B001", "Ikkita son yig'indisi (Two Sum)",
        "Massiv va target son berilgan. Massivdan target ga teng yig'indi beruvchi ikkita son indekslarini toping (0-indeksli, eng kichik chap indeks).",
        "Birinchi qatorda massiv (probel bilan), ikkinchi qatorda target.",
        "Bitta qatorda ikki indeks (probel bilan).",
        "2 ≤ n ≤ 100, |a[i]| ≤ 10^9. Yagona yechim mavjud.",
        examples, hidden, "easy", "Massivlar", "0 1")

# B002: Maximum Subarray (LC#53)
def p_b002():
    def solve(inp):
        nums = list(map(int, inp.strip().split()))
        cur = best = nums[0]
        for x in nums[1:]:
            cur = max(x, cur + x)
            best = max(best, cur)
        return str(best)
    examples = [
        {"input": "-2 1 -3 4 -1 2 1 -5 4", "output": "6", "explanation": "[4,-1,2,1] yig'indi=6"},
        {"input": "1", "output": "1", "explanation": "Yagona element"},
        {"input": "5 4 -1 7 8", "output": "23", "explanation": "Hammasini olish"},
    ]
    hidden = []
    for _ in range(55):
        n = random.randint(1, 30)
        nums = [random.randint(-100, 100) for _ in range(n)]
        inp = ' '.join(map(str, nums))
        hidden.append({"input": inp, "output": solve(inp)})
    add("B002", "Maksimal qism-massiv yig'indisi (Maximum Subarray)",
        "QISM-MASSIV (subarray) — massivning QO'SHNI (yonma-yon turgan) bir nechta elementlaridan tashkil topgan ketma-ketlik. Masalan [1,2,3,4] dan [2,3] qism-massiv, lekin [1,3] EMAS (qo'shni emas).\n\n"
        "Vazifa: BARCHA mumkin bo'lgan qism-massivlar ichidan eng KATTA yig'indiga ega bo'lganini topib, shu yig'indini chiqaring.\n\n"
        "Misol: [-2,1,-3,4,-1,2,1,-5,4] → eng yaxshi qism-massiv [4,-1,2,1] → yig'indi = 6.\n\n"
        "KADANE ALGORITMI (O(n) — eng tezi):\n"
        "  cur = best = nums[0]\n"
        "  Har keyingi x uchun:\n"
        "    cur = max(x, cur + x)        ← yo joriy elementni o'zi bilan boshlash, yo eski zanjirga qo'shish\n"
        "    best = max(best, cur)        ← shu paytgacha topilgan eng yaxshi yig'indi\n\n"
        "Sezgi: cur — \"shu indeksda tugaydigan eng yaxshi qism-massiv yig'indisi\". Agar oldingi cur manfiy bo'lsa, uni tashlab yangidan boshlash foydaliroq.",
        "Bir qatorda massiv (probel bilan).",
        "Bitta son — maksimal yig'indi.",
        "1 ≤ n ≤ 1000, |a[i]| ≤ 10^4",
        examples, hidden, "easy", "Massivlar", "6")

# B003: Best Time to Buy and Sell Stock (LC#121)
def p_b003():
    def solve(inp):
        prices = list(map(int, inp.strip().split()))
        mn = prices[0]; best = 0
        for p in prices[1:]:
            best = max(best, p - mn)
            mn = min(mn, p)
        return str(best)
    examples = [
        {"input": "7 1 5 3 6 4", "output": "5", "explanation": "1 da olib 6 da sotish: foyda=5"},
        {"input": "7 6 4 3 1", "output": "0", "explanation": "Foyda yo'q"},
    ]
    hidden = []
    for _ in range(55):
        n = random.randint(2, 30)
        prices = [random.randint(0, 200) for _ in range(n)]
        inp = ' '.join(map(str, prices))
        hidden.append({"input": inp, "output": solve(inp)})
    add("B003", "Aksiyadan eng yaxshi foyda (Best Time to Buy/Sell Stock)",
        "Kunlik aksiya narxlari massivi berilgan. Bir marta sotib olib, keyinroq sotib olinadigan eng katta foyda. Foyda bo'lmasa 0.",
        "Bir qatorda narxlar.", "Bitta son — eng katta foyda.",
        "1 ≤ n ≤ 10^4, 0 ≤ price ≤ 10^4",
        examples, hidden, "easy", "Massivlar", "5")

# B004: Contains Duplicate (LC#217)
def p_b004():
    def solve(inp):
        nums = inp.strip().split()
        return "true" if len(set(nums)) < len(nums) else "false"
    examples = [
        {"input": "1 2 3 1", "output": "true"},
        {"input": "1 2 3 4", "output": "false"},
    ]
    hidden = []
    for _ in range(55):
        n = random.randint(1, 20)
        nums = [random.randint(1, 15) for _ in range(n)]
        inp = ' '.join(map(str, nums))
        hidden.append({"input": inp, "output": solve(inp)})
    add("B004", "Takrorlanuvchi son borligini tekshirish (Contains Duplicate)",
        "Massivda kamida bitta takrorlanuvchi son bo'lsa true, aks holda false chiqaring.",
        "Bir qatorda massiv.", "true yoki false.",
        "1 ≤ n ≤ 10^5",
        examples, hidden, "easy", "Massivlar", "true")

# B005: Single Number (LC#136)
def p_b005():
    def solve(inp):
        nums = list(map(int, inp.strip().split()))
        r = 0
        for x in nums: r ^= x
        return str(r)
    examples = [
        {"input": "2 2 1", "output": "1", "explanation": "1 yagona"},
        {"input": "4 1 2 1 2", "output": "4"},
    ]
    hidden = []
    for _ in range(55):
        k = random.randint(1, 10)
        nums = [random.randint(1, 100) for _ in range(k)]
        unique = random.randint(101, 200)
        all_nums = nums + nums + [unique]
        random.shuffle(all_nums)
        inp = ' '.join(map(str, all_nums))
        hidden.append({"input": inp, "output": solve(inp)})
    add("B005", "Yagona son (Single Number)",
        "Massivdagi BARCHA sonlar AYNAN 2 martadan uchraydi, faqat BITTA son bor — u 1 marta uchraydi. Shu yagona sonni toping.\n\n"
        "Maslahat (XOR usuli): XOR (^) — ikkilik amal. Qoidalari:\n"
        "  • x XOR x = 0  (bir xil sonlarning XOR'i — 0)\n"
        "  • x XOR 0 = x  (0 bilan XOR — sonni o'zgartirmaydi)\n"
        "  • XOR — kommutativ va assotsiativ (tartib muhim emas)\n"
        "Demak, butun massivni XOR qilsak, juftliklar bir-birini yo'qotadi va faqat yagona son qoladi.\n"
        "Misol: [4,1,2,1,2] → 4^1^2^1^2 = 4^(1^1)^(2^2) = 4^0^0 = 4.",
        "Bir qatorda massiv.", "Yagona son.",
        "1 ≤ n < 3·10^4, har element [-3·10^4, 3·10^4]",
        examples, hidden, "easy", "Massivlar", "1")

# B006: Move Zeroes (LC#283)
def p_b006():
    def solve(inp):
        nums = list(map(int, inp.strip().split()))
        non_zero = [x for x in nums if x != 0]
        zeros = [0] * (len(nums) - len(non_zero))
        return ' '.join(map(str, non_zero + zeros))
    examples = [
        {"input": "0 1 0 3 12", "output": "1 3 12 0 0"},
        {"input": "0", "output": "0"},
    ]
    hidden = []
    for _ in range(55):
        n = random.randint(1, 15)
        nums = [random.randint(0, 5) for _ in range(n)]
        inp = ' '.join(map(str, nums))
        hidden.append({"input": inp, "output": solve(inp)})
    add("B006", "Nollarni oxiriga ko'chirish (Move Zeroes)",
        "Massivdagi barcha nollarni oxiriga ko'chiring. Nol bo'lmagan elementlar tartibi saqlanadi.",
        "Bir qatorda massiv.", "Bir qatorda yangi massiv.",
        "1 ≤ n ≤ 10^4",
        examples, hidden, "easy", "Massivlar", "1 3 12 0 0")

# B007: Missing Number (LC#268)
def p_b007():
    def solve(inp):
        nums = list(map(int, inp.strip().split()))
        n = len(nums)
        return str(n*(n+1)//2 - sum(nums))
    examples = [
        {"input": "3 0 1", "output": "2", "explanation": "0..3 dan 2 yo'q"},
        {"input": "0 1", "output": "2"},
    ]
    hidden = []
    for _ in range(55):
        n = random.randint(2, 30)
        miss = random.randint(0, n)
        nums = [i for i in range(n+1) if i != miss]
        random.shuffle(nums)
        inp = ' '.join(map(str, nums))
        hidden.append({"input": inp, "output": solve(inp)})
    add("B007", "Yo'qolgan son (Missing Number)",
        "n ta turli son 0..n oraliqdan berilgan. Yo'qolgan sonni toping.",
        "Bir qatorda n ta son.", "Yo'qolgan son.",
        "1 ≤ n ≤ 10^4",
        examples, hidden, "easy", "Massivlar", "2")

# B008: Find All Numbers Disappeared (LC#448)
def p_b008():
    def solve(inp):
        nums = list(map(int, inp.strip().split()))
        n = len(nums)
        s = set(nums)
        miss = [str(i) for i in range(1, n+1) if i not in s]
        return ' '.join(miss) if miss else ""
    examples = [
        {"input": "4 3 2 7 8 2 3 1", "output": "5 6"},
        {"input": "1 1", "output": "2"},
    ]
    hidden = []
    for _ in range(55):
        n = random.randint(2, 20)
        nums = [random.randint(1, n) for _ in range(n)]
        inp = ' '.join(map(str, nums))
        hidden.append({"input": inp, "output": solve(inp)})
    add("B008", "Yo'qolgan barcha sonlar (Find All Disappeared)",
        "1 dan n gacha bo'lgan sonlarning n tasi berilgan (takrorlanishi mumkin). Massivda bo'lmagan sonlarni o'sish tartibida chiqaring.",
        "Bir qatorda n ta son.", "Yo'qolgan sonlar (probel bilan).",
        "1 ≤ n ≤ 10^4, 1 ≤ a[i] ≤ n",
        examples, hidden, "easy", "Massivlar", "5 6")

# B009: Max Consecutive Ones (LC#485)
def p_b009():
    def solve(inp):
        nums = list(map(int, inp.strip().split()))
        cur = best = 0
        for x in nums:
            cur = cur + 1 if x == 1 else 0
            best = max(best, cur)
        return str(best)
    examples = [
        {"input": "1 1 0 1 1 1", "output": "3"},
        {"input": "1 0 1 1 0 1", "output": "2"},
    ]
    hidden = []
    for _ in range(55):
        n = random.randint(1, 30)
        nums = [random.randint(0, 1) for _ in range(n)]
        inp = ' '.join(map(str, nums))
        hidden.append({"input": inp, "output": solve(inp)})
    add("B009", "Ketma-ket eng ko'p 1 lar (Max Consecutive Ones)",
        "Faqat 0 va 1 dan iborat massivda eng uzun ketma-ket 1 lar zanjiri uzunligini toping.",
        "Bir qatorda 0/1 lar.", "Eng katta uzunlik.",
        "1 ≤ n ≤ 10^5",
        examples, hidden, "easy", "Massivlar", "3")

# B010: Sort Array By Parity (LC#905)
def p_b010():
    def solve(inp):
        nums = list(map(int, inp.strip().split()))
        even = [x for x in nums if x % 2 == 0]
        odd = [x for x in nums if x % 2 != 0]
        return ' '.join(map(str, even + odd))
    examples = [
        {"input": "3 1 2 4", "output": "2 4 3 1"},
    ]
    hidden = []
    for _ in range(55):
        n = random.randint(1, 20)
        nums = [random.randint(0, 100) for _ in range(n)]
        inp = ' '.join(map(str, nums))
        hidden.append({"input": inp, "output": solve(inp)})
    add("B010", "Juftlik bo'yicha saralash (Sort Array By Parity)",
        "Massivda avval barcha juft sonlar (kelish tartibida), keyin barcha toq sonlar (kelish tartibida) keladi tarzda chiqaring.",
        "Bir qatorda massiv.", "Yangi massiv (probel bilan).",
        "1 ≤ n ≤ 10^4",
        examples, hidden, "easy", "Massivlar", "2 4 3 1")

# B011: Squares of Sorted Array (LC#977)
def p_b011():
    def solve(inp):
        nums = list(map(int, inp.strip().split()))
        return ' '.join(map(str, sorted(x*x for x in nums)))
    examples = [
        {"input": "-4 -1 0 3 10", "output": "0 1 9 16 100"},
    ]
    hidden = []
    for _ in range(55):
        n = random.randint(1, 20)
        nums = sorted(random.randint(-30, 30) for _ in range(n))
        inp = ' '.join(map(str, nums))
        hidden.append({"input": inp, "output": solve(inp)})
    add("B011", "Saralangan massiv kvadratlari (Squares of Sorted Array)",
        "O'sib boruvchi tartibda saralangan butun sonlar massivi berilgan. Har sonning kvadratidan o'sish tartibida saralangan massivni chiqaring.",
        "Saralangan massiv.", "Saralangan kvadratlar.",
        "1 ≤ n ≤ 10^4, |a[i]| ≤ 10^4",
        examples, hidden, "easy", "Massivlar", "0 1 9 16 100")

# B012: Running Sum (LC#1480)
def p_b012():
    def solve(inp):
        nums = list(map(int, inp.strip().split()))
        out = []
        s = 0
        for x in nums:
            s += x
            out.append(s)
        return ' '.join(map(str, out))
    examples = [
        {"input": "1 2 3 4", "output": "1 3 6 10"},
    ]
    hidden = []
    for _ in range(55):
        n = random.randint(1, 20)
        nums = [random.randint(-50, 50) for _ in range(n)]
        inp = ' '.join(map(str, nums))
        hidden.append({"input": inp, "output": solve(inp)})
    add("B012", "Yugurib boruvchi yig'indi (Running Sum)",
        "Massivning prefiks yig'indilarini chiqaring: result[i] = nums[0]+...+nums[i].",
        "Bir qatorda massiv.", "Bir qatorda prefiks yig'indilar.",
        "1 ≤ n ≤ 10^3",
        examples, hidden, "easy", "Massivlar", "1 3 6 10")

# B013: Build Array from Permutation (LC#1920)
def p_b013():
    def solve(inp):
        nums = list(map(int, inp.strip().split()))
        return ' '.join(str(nums[nums[i]]) for i in range(len(nums)))
    examples = [
        {"input": "0 2 1 5 3 4", "output": "0 1 2 4 5 3"},
    ]
    hidden = []
    for _ in range(55):
        n = random.randint(1, 15)
        perm = list(range(n))
        random.shuffle(perm)
        inp = ' '.join(map(str, perm))
        hidden.append({"input": inp, "output": solve(inp)})
    add("B013", "Permutatsiyadan massiv qurish (Build Array from Permutation)",
        "PERMUTATSIYA — 0 dan n−1 gacha bo'lgan barcha sonlarning BIROR TARTIBDA joylashishi (har son aniq 1 marta uchraydi).\n"
        "  Misol: n=4 uchun [2,0,3,1], [0,1,2,3], [3,2,1,0] — barchasi permutatsiya.\n"
        "  EMAS: [0,1,1,2] (1 ikki marta), [0,1,4,2] (n-1=3 dan katta son bor).\n\n"
        "Vazifa: Berilgan nums permutatsiyasidan formula bo'yicha yangi massiv tuzing:\n"
        "    ans[i] = nums[ nums[i] ]    (nums[i] ni indeks sifatida ishlatib, qaytadan nums dan o'qing)\n\n"
        "Misol: nums = [0,2,1,5,3,4]\n"
        "  i=0: nums[0]=0 → nums[0]=0      → ans[0]=0\n"
        "  i=1: nums[1]=2 → nums[2]=1      → ans[1]=1\n"
        "  i=2: nums[2]=1 → nums[1]=2      → ans[2]=2\n"
        "  i=3: nums[3]=5 → nums[5]=4      → ans[3]=4\n"
        "  i=4: nums[4]=3 → nums[3]=5      → ans[4]=5\n"
        "  i=5: nums[5]=4 → nums[4]=3      → ans[5]=3\n"
        "  Javob: 0 1 2 4 5 3.",
        "Bir qatorda permutatsiya.", "Bir qatorda natija massivi.",
        "1 ≤ n ≤ 1000, 0 ≤ nums[i] < n",
        examples, hidden, "easy", "Massivlar", "0 1 2 4 5 3")

# B014: Concatenation of Array (LC#1929)
def p_b014():
    def solve(inp):
        nums = inp.strip().split()
        return ' '.join(nums + nums)
    examples = [
        {"input": "1 2 1", "output": "1 2 1 1 2 1"},
    ]
    hidden = []
    for _ in range(55):
        n = random.randint(1, 15)
        nums = [random.randint(1, 100) for _ in range(n)]
        inp = ' '.join(map(str, nums))
        hidden.append({"input": inp, "output": solve(inp)})
    add("B014", "Massivni o'ziga qo'shish (Concatenation of Array)",
        "Massivni o'ziga ulang: ans = nums + nums (uzunligi 2n bo'lgan).",
        "Bir qatorda massiv.", "Birlashgan massiv.",
        "1 ≤ n ≤ 1000",
        examples, hidden, "easy", "Massivlar", "1 2 1 1 2 1")

# B015: Plus One (LC#66) — increment digit array
def p_b015():
    def solve(inp):
        digits = list(map(int, inp.strip().split()))
        n = int(''.join(map(str, digits))) + 1
        return ' '.join(str(n))
    examples = [
        {"input": "1 2 3", "output": "1 2 4", "explanation": "123+1=124"},
        {"input": "9 9", "output": "1 0 0"},
    ]
    hidden = []
    for _ in range(55):
        n = random.randint(1, 8)
        digits = [random.randint(0, 9) for _ in range(n)]
        if digits[0] == 0 and len(digits) > 1: digits[0] = random.randint(1, 9)
        inp = ' '.join(map(str, digits))
        hidden.append({"input": inp, "output": solve(inp)})
    add("B015", "Bir qo'shish (Plus One)",
        "Raqamlardan iborat massiv katta sonni ifodalaydi. Songa 1 qo'shib, natijani raqamlar massivi sifatida chiqaring.",
        "Bir qatorda raqamlar.", "Bir qatorda yangi raqamlar.",
        "1 ≤ n ≤ 100, oxirgi raqam emas faqat",
        examples, hidden, "easy", "Massivlar", "1 2 4")


# ═══════════════════════════════════════════════════════════════════════════
# SATRLAR (15 ta)
# ═══════════════════════════════════════════════════════════════════════════

# B016: Reverse String (LC#344)
def p_b016():
    def solve(inp):
        return inp.strip()[::-1]
    examples = [{"input": "hello", "output": "olleh"}, {"input": "Hannah", "output": "hannaH"}]
    hidden = []
    for _ in range(55):
        s = ''.join(random.choices('abcdefghij', k=random.randint(1, 15)))
        hidden.append({"input": s, "output": solve(s)})
    add("B016", "Satrni teskari qilish (Reverse String)",
        "Satrni teskari tartibda chiqaring.",
        "Bir qatorda satr.", "Teskari satr.",
        "1 ≤ uzunlik ≤ 10^5",
        examples, hidden, "easy", "Satrlar", "olleh")

# B017: Valid Anagram (LC#242)
def p_b017():
    def solve(inp):
        a, b = inp.strip().split('\n')
        return "true" if sorted(a) == sorted(b) else "false"
    examples = [
        {"input": "anagram\nnagaram", "output": "true"},
        {"input": "rat\ncar", "output": "false"},
    ]
    hidden = []
    for _ in range(55):
        s1 = ''.join(random.choices('abcdef', k=random.randint(2, 10)))
        if random.random() < 0.5:
            s2 = ''.join(random.sample(s1, len(s1)))
        else:
            s2 = ''.join(random.choices('abcdef', k=len(s1)))
        inp = f"{s1}\n{s2}"
        hidden.append({"input": inp, "output": solve(inp)})
    add("B017", "Anagramma tekshirish (Valid Anagram)",
        "ANAGRAMMA — bir so'zning HARFLARINI BOSHQA TARTIBDA joylashtirib hosil qilingan boshqa so'z. Ya'ni:\n"
        "  • har ikkala so'zda ayni HARFLAR uchraydi,\n"
        "  • har harf TURGAN MIQDORDA ham TENG (a 3 marta bo'lsa — ikkalasida ham 3 marta),\n"
        "  • faqat tartibi farq qilishi mumkin.\n\n"
        "Misollar:\n"
        "  'anagram' va 'nagaram' → true. (a:3, n:1, g:1, r:1, m:1 — ikkalasida ham bir xil)\n"
        "  'rat' va 'car' → false. (r,a,t  ≠  c,a,r — 't' va 'c' farq qiladi)\n"
        "  'aab' va 'abb' → false. (a soni: 2 vs 1)\n\n"
        "USULLAR:\n"
        "  1) sorted(s1) == sorted(s2)  — eng qisqasi.\n"
        "  2) Counter(s1) == Counter(s2)  — har harfni sanab tenglashtirish (tezroq, O(n)).",
        "Birinchi qatorda s1, ikkinchi qatorda s2.", "true yoki false.",
        "1 ≤ uzunliklar ≤ 5·10^4, faqat kichik lotin harflari",
        examples, hidden, "easy", "Satrlar", "true")

# B018: First Unique Character (LC#387)
def p_b018():
    def solve(inp):
        s = inp.strip()
        from collections import Counter
        c = Counter(s)
        for i, ch in enumerate(s):
            if c[ch] == 1:
                return str(i)
        return "-1"
    examples = [
        {"input": "leetcode", "output": "0", "explanation": "'l' yagona"},
        {"input": "loveleetcode", "output": "2"},
        {"input": "aabb", "output": "-1"},
    ]
    hidden = []
    for _ in range(55):
        s = ''.join(random.choices('abcde', k=random.randint(1, 12)))
        hidden.append({"input": s, "output": solve(s)})
    add("B018", "Birinchi noyob harf (First Unique Character)",
        "Satrda faqat bir marta uchraydigan birinchi harf indeksini toping. Bunday harf yo'q bo'lsa -1 chiqaring.",
        "Bir qatorda satr.", "Indeks yoki -1.",
        "1 ≤ uzunlik ≤ 10^5, kichik lotin harflari",
        examples, hidden, "easy", "Satrlar", "0")

# B019: Valid Palindrome (LC#125, simplified)
def p_b019():
    def solve(inp):
        s = ''.join(c.lower() for c in inp.strip() if c.isalnum())
        return "true" if s == s[::-1] else "false"
    examples = [
        {"input": "A man a plan a canal Panama", "output": "true"},
        {"input": "race a car", "output": "false"},
    ]
    hidden = []
    samples = ["abba", "abc", "Was it a car or a cat I saw", "No lemon no melon", "hello", "deed", "abba1abba"]
    for s in samples:
        hidden.append({"input": s, "output": solve(s)})
    for _ in range(55):
        s = ''.join(random.choices('abc ABC', k=random.randint(1, 15)))
        hidden.append({"input": s, "output": solve(s)})
    add("B019", "Yaroqli palindrom (Valid Palindrome)",
        "PALINDROM — chapdan va o'ngdan o'qilganda bir xil bo'lgan so'z yoki gap (masalan: 'kiyik', 'alla').\n\n"
        "Vazifa: Berilgan satr yaroqli palindrom ekanligini tekshiring.\n"
        "Bunda QOIDALAR quyidagicha:\n"
        "  1) Faqat harf va raqamlar (alphanumeric) hisobga olinadi. Boshqa barcha belgilar (probel, vergul va h.k.) tashlab yuboriladi.\n"
        "  2) Katta-kichik harflar farq qilmaydi (ya'ni 'A' va 'a' bir xil deb olinadi).\n\n"
        "Misol: 'A man, a plan, a canal: Panama'\n"
        "Tozalanadi: 'amanaplanacanalpanama' → Palindrom! (true).",
        "Bir qatorda satr.", "true yoki false.",
        "1 ≤ uzunlik ≤ 2·10^5",
        examples, hidden, "easy", "Satrlar", "true")

# B020: Reverse Words in a String III (LC#557)
def p_b020():
    def solve(inp):
        return ' '.join(w[::-1] for w in inp.strip().split(' '))
    examples = [
        {"input": "Let's take LeetCode contest", "output": "s'teL ekat edoCteeL tsetnoc"},
    ]
    hidden = []
    samples = ["hello world", "abc def", "a b c", "single"]
    for s in samples:
        hidden.append({"input": s, "output": solve(s)})
    for _ in range(55):
        words = [''.join(random.choices('abcde', k=random.randint(1,5))) for _ in range(random.randint(1, 4))]
        s = ' '.join(words)
        hidden.append({"input": s, "output": solve(s)})
    add("B020", "Har so'zni teskari qilish (Reverse Words III)",
        "Satrdagi har bir so'zni teskari yozing. So'zlar tartibi va probellar saqlanadi.",
        "Bir qatorda satr.", "Yangi satr.",
        "1 ≤ uzunlik ≤ 5·10^4",
        examples, hidden, "easy", "Satrlar", "s'teL ekat edoCteeL tsetnoc")

# B021: Length of Last Word (LC#58)
def p_b021():
    def solve(inp):
        words = inp.strip().split()
        return str(len(words[-1])) if words else "0"
    examples = [
        {"input": "Hello World", "output": "5"},
        {"input": "   fly me   to   the moon  ", "output": "4"},
    ]
    hidden = []
    samples = ["a", "ab cd", "hello   world  ", "single", "  end"]
    for s in samples:
        hidden.append({"input": s, "output": solve(s)})
    for _ in range(55):
        words = [''.join(random.choices('abcdef', k=random.randint(1,7))) for _ in range(random.randint(1,5))]
        s = ' '.join(words) + (' ' * random.randint(0,3))
        hidden.append({"input": s, "output": solve(s)})
    add("B021", "Oxirgi so'z uzunligi (Length of Last Word)",
        "Satrdagi oxirgi so'z uzunligini chiqaring (probel bilan ajratilgan so'zlar).",
        "Bir qatorda satr.", "Oxirgi so'z uzunligi.",
        "1 ≤ uzunlik ≤ 10^4",
        examples, hidden, "easy", "Satrlar", "5")

# B022: Detect Capital (LC#520)
def p_b022():
    def solve(inp):
        w = inp.strip()
        return "true" if (w.isupper() or w.islower() or (w[0].isupper() and w[1:].islower())) else "false"
    examples = [
        {"input": "USA", "output": "true"},
        {"input": "FlaG", "output": "false"},
        {"input": "Google", "output": "true"},
        {"input": "leetcode", "output": "true"},
    ]
    hidden = []
    samples = ["A", "Aaa", "AAA", "aaa", "AaA", "USA", "abc", "ABc"]
    for s in samples:
        hidden.append({"input": s, "output": solve(s)})
    for _ in range(55):
        s = ''.join(random.choices('abcABC', k=random.randint(1, 8)))
        hidden.append({"input": s, "output": solve(s)})
    add("B022", "Bosh harflarni aniqlash (Detect Capital)",
        "So'z to'g'ri yozilgan bo'lsa true chiqaring: barcha harflar katta yoki barchasi kichik yoki faqat birinchi harf katta.",
        "Bir qatorda so'z.", "true yoki false.",
        "1 ≤ uzunlik ≤ 100, faqat lotin harflari",
        examples, hidden, "easy", "Satrlar", "true")

# B023: Find the Difference (LC#389)
def p_b023():
    def solve(inp):
        parts = inp.split('\n', 1)
        s = parts[0]
        t = parts[1].rstrip('\n') if len(parts) > 1 else ''
        r = 0
        for c in s+t: r ^= ord(c)
        return chr(r)
    examples = [
        {"input": "abcd\nabcde", "output": "e"},
        {"input": "\ny", "output": "y"},
    ]
    hidden = []
    for _ in range(55):
        s = ''.join(random.choices('abcdefg', k=random.randint(1, 10)))
        extra = random.choice('abcdefghij')
        t = list(s) + [extra]
        random.shuffle(t)
        inp = f"{s}\n{''.join(t)}"
        hidden.append({"input": inp, "output": solve(inp)})
    add("B023", "Qo'shilgan harf (Find the Difference)",
        "t satri s satri harflari + 1 qo'shimcha tasodifiy harfdan tashkil topgan. Qo'shilgan harfni toping.",
        "Birinchi qatorda s, ikkinchi qatorda t.", "Qo'shilgan harf.",
        "0 ≤ |s| ≤ 1000, |t| = |s|+1",
        examples, hidden, "easy", "Satrlar", "e")

# B024: To Lower Case (LC#709)
def p_b024():
    def solve(inp):
        return inp.lower().rstrip('\n')
    examples = [
        {"input": "Hello", "output": "hello"},
        {"input": "LOVELY", "output": "lovely"},
    ]
    hidden = []
    for _ in range(55):
        s = ''.join(random.choices('abcdABCD123!', k=random.randint(1, 10)))
        hidden.append({"input": s, "output": solve(s)})
    add("B024", "Kichik harflarga aylantirish (To Lower Case)",
        "Satrning barcha katta harflarini kichik harflarga aylantiring (boshqa belgilar o'zgarmasligi kerak).",
        "Bir qatorda satr.", "Kichik harfli satr.",
        "1 ≤ uzunlik ≤ 100",
        examples, hidden, "easy", "Satrlar", "hello")

# B025: Repeated Substring Pattern (LC#459)
def p_b025():
    def solve(inp):
        s = inp.strip()
        return "true" if s in (s+s)[1:-1] else "false"
    examples = [
        {"input": "abab", "output": "true"},
        {"input": "aba", "output": "false"},
        {"input": "abcabcabcabc", "output": "true"},
    ]
    hidden = []
    samples = ["a", "aa", "abcabc", "abcabcabc", "abcd", "ababab", "xyz"]
    for s in samples:
        hidden.append({"input": s, "output": solve(s)})
    for _ in range(55):
        if random.random() < 0.5:
            base = ''.join(random.choices('abc', k=random.randint(1,3)))
            s = base * random.randint(2, 4)
        else:
            s = ''.join(random.choices('abcd', k=random.randint(1, 8)))
        hidden.append({"input": s, "output": solve(s)})
    add("B025", "Takrorlanuvchi qism-satr (Repeated Substring Pattern)",
        "Berilgan satr qandaydir kichikroq qism-satrning bir necha marta (kamida 2 marta) takrorlanishidan hosil bo'lganmi yoki yo'q, shuni toping.\n\n"
        "Misollar:\n"
        "  • 'abab' → true (chunki 'ab' qism-satri 2 marta takrorlangan).\n"
        "  • 'aba' → false (hech qanday qism o'zini takrorlab buni hosil qilolmaydi).\n"
        "  • 'abcabcabcabc' → true ('abc' 4 marta yoki 'abcabc' 2 marta).\n\n"
        "Qiziqarli yechim (hiyla): Agar satr s takrorlanuvchi bo'lsa, s+s satrining bosh va oxirgi harflarini olib tashlasak, uning ichidan baribir original s topiladi!",
        "Bir qatorda satr.", "true yoki false.",
        "1 ≤ uzunlik ≤ 10^4",
        examples, hidden, "easy", "Satrlar", "true")

# B026: Roman to Integer (LC#13)
def p_b026():
    def solve(inp):
        s = inp.strip()
        v = {'I':1,'V':5,'X':10,'L':50,'C':100,'D':500,'M':1000}
        total = 0
        for i, c in enumerate(s):
            if i+1 < len(s) and v[c] < v[s[i+1]]:
                total -= v[c]
            else:
                total += v[c]
        return str(total)
    examples = [
        {"input": "III", "output": "3"},
        {"input": "IV", "output": "4"},
        {"input": "IX", "output": "9"},
        {"input": "LVIII", "output": "58"},
        {"input": "MCMXCIV", "output": "1994"},
    ]
    hidden = []
    samples = ["I", "II", "III", "IV", "V", "VI", "IX", "X", "XL", "L", "XC", "C", "CD", "D", "CM", "M", "MMXXIV", "DCCC"]
    for s in samples:
        hidden.append({"input": s, "output": solve(s)})
    def to_roman(n):
        v = [(1000,"M"),(900,"CM"),(500,"D"),(400,"CD"),(100,"C"),(90,"XC"),(50,"L"),(40,"XL"),(10,"X"),(9,"IX"),(5,"V"),(4,"IV"),(1,"I")]
        r = ""
        for val, sym in v:
            while n >= val: r += sym; n -= val
        return r
    for _ in range(50):
        n = random.randint(1, 3999)
        s = to_roman(n)
        hidden.append({"input": s, "output": solve(s)})
    add("B026", "Rim raqamidan butun songa (Roman to Integer)",
        "Rim raqami — qadimgi Rim sanoq tizimi. Har harfning qiymati bor:\n"
        "  I=1, V=5, X=10, L=50, C=100, D=500, M=1000.\n\n"
        "ASOSIY QOIDA: Belgilar odatda chapdan o'ngga QO'SHILADI. Masalan, VI = 5+1 = 6, LX = 50+10 = 60.\n\n"
        "ISTISNO (ayirish qoidasi): Agar kichik qiymatli belgi katta qiymatli belgidan OLDIN kelsa — u AYIRILADI:\n"
        "  • IV = 5−1 = 4  (V dan oldingi I — ayirildi)\n"
        "  • IX = 10−1 = 9\n"
        "  • XL = 50−10 = 40,  XC = 100−10 = 90\n"
        "  • CD = 500−100 = 400,  CM = 1000−100 = 900\n\n"
        "Misol: MCMXCIV = M(1000) + CM(900) + XC(90) + IV(4) = 1994.\n"
        "Algoritm: har bir belgini tekshiring — agar undan keyingi belgi KATTA bo'lsa, joriy belgini ayiring; aks holda qo'shing.",
        "Bir qatorda rim raqami.", "Butun son.",
        "1 ≤ uzunlik ≤ 15, qiymat 1..3999",
        examples, hidden, "easy", "Satrlar", "3")

# B027: Longest Common Prefix (LC#14)
def p_b027():
    def solve(inp):
        words = inp.strip().split()
        if not words: return ""
        pref = words[0]
        for w in words[1:]:
            while not w.startswith(pref):
                pref = pref[:-1]
                if not pref: return ""
        return pref if pref else " "
    examples = [
        {"input": "flower flow flight", "output": "fl"},
        {"input": "dog racecar car", "output": " ", "explanation": "Umumiy prefiks yo'q"},
    ]
    hidden = []
    samples = ["abc abd abe", "a a a", "abc def", "interspecies interstellar interstate", "x", "ab"]
    for s in samples:
        hidden.append({"input": s, "output": solve(s)})
    for _ in range(55):
        prefix = ''.join(random.choices('abc', k=random.randint(0, 4)))
        words = [prefix + ''.join(random.choices('def', k=random.randint(0, 4))) for _ in range(random.randint(1, 4))]
        s = ' '.join(words)
        hidden.append({"input": s, "output": solve(s)})
    add("B027", "Eng uzun umumiy prefiks (Longest Common Prefix)",
        "Bir nechta so'zlarning eng uzun umumiy boshlang'ich qismini chiqaring. Yo'q bo'lsa probel chiqaring.",
        "Bir qatorda probel bilan ajratilgan so'zlar.", "Umumiy prefiks.",
        "1 ≤ so'zlar soni ≤ 200",
        examples, hidden, "easy", "Satrlar", "fl")

# B028: Reverse Vowels of a String (LC#345)
def p_b028():
    def solve(inp):
        s = list(inp.strip())
        v = "aeiouAEIOU"
        idx = [i for i, c in enumerate(s) if c in v]
        chars = [s[i] for i in idx]
        chars.reverse()
        for i, j in enumerate(idx):
            s[j] = chars[i]
        return ''.join(s)
    examples = [
        {"input": "hello", "output": "holle"},
        {"input": "leetcode", "output": "leotcede"},
    ]
    hidden = []
    samples = ["aA", "ab", "race", "AEIOUaeiou"]
    for s in samples:
        hidden.append({"input": s, "output": solve(s)})
    for _ in range(55):
        s = ''.join(random.choices('abcdeiou', k=random.randint(1, 12)))
        hidden.append({"input": s, "output": solve(s)})
    add("B028", "Unli harflarni teskari qilish (Reverse Vowels)",
        "Satrdagi unli harflar (aeiouAEIOU) o'rinlarini teskari almashtiring. Boshqa harflar joyida qolsin.",
        "Bir qatorda satr.", "Yangi satr.",
        "1 ≤ uzunlik ≤ 3·10^5",
        examples, hidden, "easy", "Satrlar", "holle")

# B029: Add Strings (LC#415)
def p_b029():
    def solve(inp):
        a, b = inp.strip().split('\n')
        return str(int(a) + int(b))
    examples = [
        {"input": "11\n123", "output": "134"},
        {"input": "456\n77", "output": "533"},
    ]
    hidden = []
    for _ in range(55):
        a = random.randint(0, 10**12)
        b = random.randint(0, 10**12)
        inp = f"{a}\n{b}"
        hidden.append({"input": inp, "output": solve(inp)})
    add("B029", "Satr ko'rinishidagi sonlarni qo'shish (Add Strings)",
        "Ikki musbat butun son satr sifatida berilgan. Yig'indini satr sifatida chiqaring.",
        "Birinchi qatorda son1, ikkinchi qatorda son2.", "Yig'indi.",
        "1 ≤ |son| ≤ 10^4, manfiy emas",
        examples, hidden, "easy", "Satrlar", "134")

# B030: strStr — Find Index of First Occurrence (LC#28)
def p_b030():
    def solve(inp):
        h, n = inp.strip().split('\n')
        return str(h.find(n))
    examples = [
        {"input": "sadbutsad\nsad", "output": "0"},
        {"input": "leetcode\nleeto", "output": "-1"},
    ]
    hidden = []
    for _ in range(55):
        n = ''.join(random.choices('abc', k=random.randint(1, 4)))
        h = ''.join(random.choices('abc', k=random.randint(1, 12)))
        if random.random() < 0.5:
            pos = random.randint(0, max(0, len(h)-len(n)))
            h = h[:pos] + n + h[pos:]
        inp = f"{h}\n{n}"
        hidden.append({"input": inp, "output": solve(inp)})
    add("B030", "Birinchi qism-satr indeksi (strStr / Find Index)",
        "Haystack satrida needle qism-satrining birinchi indeksi. Topilmasa -1.",
        "Birinchi qatorda haystack, ikkinchi qatorda needle.", "Indeks yoki -1.",
        "1 ≤ uzunlik ≤ 10^4",
        examples, hidden, "easy", "Satrlar", "0")


# ═══════════════════════════════════════════════════════════════════════════
# MATEMATIKA (15 ta)
# ═══════════════════════════════════════════════════════════════════════════

# B031: Reverse Integer (LC#7, simplified to non-negative)
def p_b031():
    def solve(inp):
        n = int(inp.strip())
        sign = -1 if n < 0 else 1
        r = int(str(abs(n))[::-1]) * sign
        if r < -2**31 or r > 2**31-1: return "0"
        return str(r)
    examples = [
        {"input": "123", "output": "321"},
        {"input": "-123", "output": "-321"},
        {"input": "120", "output": "21"},
    ]
    hidden = []
    samples = ["0", "1", "10", "100", "1534236469", "-2147483648"]
    for s in samples:
        hidden.append({"input": s, "output": solve(s)})
    for _ in range(55):
        n = random.randint(-100000, 100000)
        s = str(n)
        hidden.append({"input": s, "output": solve(s)})
    add("B031", "Sonni teskari qilish (Reverse Integer)",
        "Berilgan butun sonning raqamlarini teskari yozib chiqaring. Natija int32 chegarasidan chiqsa 0 chiqaring.",
        "Bir butun son.", "Teskari son.",
        "-2^31 ≤ n ≤ 2^31-1",
        examples, hidden, "easy", "Arifmetika", "321")

# B032: Palindrome Number (LC#9)
def p_b032():
    def solve(inp):
        n = inp.strip()
        return "true" if (not n.startswith('-') and n == n[::-1]) else "false"
    examples = [
        {"input": "121", "output": "true"},
        {"input": "-121", "output": "false"},
        {"input": "10", "output": "false"},
    ]
    hidden = []
    samples = ["0", "1", "11", "123", "1221", "12321", "-1", "100"]
    for s in samples:
        hidden.append({"input": s, "output": solve(s)})
    for _ in range(55):
        n = random.randint(-1000, 10000)
        s = str(n)
        hidden.append({"input": s, "output": solve(s)})
    add("B032", "Palindrom son (Palindrome Number)",
        "Berilgan butun son n palindrom ekanligini tekshiring (chapdan va o'ngdan bir xil o'qiladimi?).\n\n"
        "Eslatmalar:\n"
        "  • Manfiy sonlar HECH QACHON palindrom bo'lmaydi. Masalan: -121 teskarisiga 121- bo'lib qoladi (false).\n"
        "  • Oxiri 0 bilan tugaydigan sonlar (0 dan tashqari) palindrom bo'lolmaydi (masalan 10 → 01 emas).\n\n"
        "Misol: 121 → true, chunki u teskarisiga ham 121.",
        "Bir butun son.", "true yoki false.",
        "-2^31 ≤ n ≤ 2^31-1",
        examples, hidden, "easy", "Arifmetika", "true")

# B033: Sqrt(x) (LC#69) — integer square root
def p_b033():
    def solve(inp):
        n = int(inp.strip())
        return str(int(math.isqrt(n)))
    examples = [
        {"input": "4", "output": "2"},
        {"input": "8", "output": "2", "explanation": "sqrt(8)≈2.82, butun qism = 2"},
        {"input": "0", "output": "0"},
    ]
    hidden = []
    samples = [0, 1, 2, 3, 4, 9, 15, 16, 17, 100, 1000, 100000, 2**30, 2**31-1]
    for n in samples:
        hidden.append({"input": str(n), "output": solve(str(n))})
    for _ in range(50):
        n = random.randint(0, 2**30)
        hidden.append({"input": str(n), "output": solve(str(n))})
    add("B033", "Butun ildiz (Sqrt(x))",
        "Manfiy bo'lmagan butun sonning kvadrat ildizini butun qism sifatida chiqaring.",
        "Bir son n.", "floor(sqrt(n)).",
        "0 ≤ n ≤ 2^31-1",
        examples, hidden, "easy", "Arifmetika", "2")

# B034: Climbing Stairs (LC#70)
def p_b034():
    def solve(inp):
        n = int(inp.strip())
        a, b = 1, 1
        for _ in range(n): a, b = b, a+b
        return str(a)
    examples = [
        {"input": "2", "output": "2"},
        {"input": "3", "output": "3"},
        {"input": "5", "output": "8"},
    ]
    hidden = []
    for n in range(1, 56):
        hidden.append({"input": str(n), "output": solve(str(n))})
    add("B034", "Zinapoyaga chiqish (Climbing Stairs)",
        "n ta pog'onadan iborat zinapoya bor. Siz har safar yo 1 ta pog'ona, yoki 2 ta pog'ona yuqoriga ko'tarila olasiz.\n\n"
        "Vazifa: Eng yuqoriga chiqishning jami necha xil usuli borligini toping.\n\n"
        "Dinamik dasturlash (Fibonachchi) yondashuvi:\n"
        "n-chi pog'onaga chiqish usullari soni: (n-1)-pog'onaga chiqish usullari va (n-2)-pog'onaga chiqish usullari yig'indisiga teng.\n"
        "Chunki (n-1) dan 1 qadam bilan, (n-2) dan esa 2 qadam bilan n-pog'onaga chiqish mumkin.\n"
        "  • 1-pog'onaga: 1 usul (1)\n"
        "  • 2-pog'onaga: 2 usul (1+1, 2)\n"
        "  • 3-pog'onaga: 1+2 = 3 usul (1+1+1, 1+2, 2+1)\n"
        "  • 4-pog'onaga: 2+3 = 5 usul va hokazo.",
        "Bir butun son n.", "Usul soni.",
        "1 ≤ n ≤ 45",
        examples, hidden, "easy", "Dinamik dasturlash", "2")

# B035: Power of Two (LC#231)
def p_b035():
    def solve(inp):
        n = int(inp.strip())
        return "true" if n > 0 and (n & (n-1)) == 0 else "false"
    examples = [
        {"input": "1", "output": "true"},
        {"input": "16", "output": "true"},
        {"input": "3", "output": "false"},
    ]
    hidden = []
    samples = [0, 1, 2, 3, 4, 5, 8, 16, 1024, 1023, -1, 1<<30, (1<<30)-1]
    for n in samples:
        hidden.append({"input": str(n), "output": solve(str(n))})
    for _ in range(50):
        if random.random() < 0.4:
            n = 1 << random.randint(0, 30)
        else:
            n = random.randint(-100, 1<<20)
        hidden.append({"input": str(n), "output": solve(str(n))})
    add("B035", "Ikkining darajasi (Power of Two)",
        "Berilgan n soni 2 ning biror butun darajasiga (2^x) tengmi?\n"
        "Ya'ni u 1, 2, 4, 8, 16, 32... qatoriga kiradimi?\n\n"
        "Bitwise (Bit amallari) hiylasi (O(1) yechim):\n"
        "Ikkining darajasi bo'lgan sonning ikkilik sanoq sistemasidagi ko'rinishida FAQAT bitta 1 bo'ladi (masalan, 8 = 1000₂).\n"
        "Shuning uchun, agar son 2 ning darajasi bo'lsa:\n"
        "    n & (n - 1) == 0  bo'ladi!\n\n"
        "Misol uchun n=8 (1000). n-1 = 7 (0111).\n"
        "1000 & 0111 = 0000 (0) → Demak, 8 bu 2 ning darajasi.",
        "Bir butun son n.", "true yoki false.",
        "-2^31 ≤ n ≤ 2^31-1",
        examples, hidden, "easy", "Bit amallari", "true")

# B036: Power of Three (LC#326)
def p_b036():
    def solve(inp):
        n = int(inp.strip())
        if n < 1: return "false"
        while n % 3 == 0:
            n //= 3
        return "true" if n == 1 else "false"
    examples = [
        {"input": "27", "output": "true"},
        {"input": "9", "output": "true"},
        {"input": "10", "output": "false"},
    ]
    hidden = []
    samples = [0, 1, 2, 3, 9, 27, 81, 243, 1162261467, 45, 100]
    for n in samples:
        hidden.append({"input": str(n), "output": solve(str(n))})
    for _ in range(50):
        if random.random() < 0.4:
            n = 3 ** random.randint(0, 19)
        else:
            n = random.randint(-100, 10**6)
        hidden.append({"input": str(n), "output": solve(str(n))})
    add("B036", "Uchning darajasi (Power of Three)",
        "n soni 3 ning biror darajasiga teng bo'lsa true (1, 3, 9, 27, ...).",
        "Bir butun son n.", "true yoki false.",
        "-2^31 ≤ n ≤ 2^31-1",
        examples, hidden, "easy", "Arifmetika", "true")

# B037: Add Digits (LC#258)
def p_b037():
    def solve(inp):
        n = int(inp.strip())
        while n >= 10:
            n = sum(int(d) for d in str(n))
        return str(n)
    examples = [
        {"input": "38", "output": "2", "explanation": "3+8=11, 1+1=2"},
        {"input": "0", "output": "0"},
    ]
    hidden = []
    for _ in range(55):
        n = random.randint(0, 10**9)
        hidden.append({"input": str(n), "output": solve(str(n))})
    add("B037", "Raqamlar yig'indisi (Add Digits / Digital Root)",
        "Berilgan sonning barcha raqamlarini qo'shing. Agar yig'indi 10 dan katta bo'lsa, yana raqamlarini qo'shing. "
        "Bu jarayonni bitta xonali son qolgunicha davom ettiring.\n\n"
        "Misol: 38\n"
        "  1) 3 + 8 = 11\n"
        "  2) 1 + 1 = 2 (javob: 2).\n\n"
        "Matematik qonuniyat (Digital Root):\n"
        "Sonning raqamlar yig'indisini topish aslida sonning 9 ga bo'lingandagi qoldig'iga (n % 9) bog'liq:\n"
        "  • Agar n = 0 bo'lsa, javob 0.\n"
        "  • Agar n % 9 == 0 bo'lsa (va n > 0), javob 9.\n"
        "  • Boshqa holatlarda javob n % 9.",
        "Bir butun son n.", "Bitta raqam.",
        "0 ≤ n ≤ 2^31-1",
        examples, hidden, "easy", "Arifmetika", "2")

# B038: Happy Number (LC#202)
def p_b038():
    def solve(inp):
        n = int(inp.strip())
        seen = set()
        while n != 1 and n not in seen:
            seen.add(n)
            n = sum(int(d)**2 for d in str(n))
        return "true" if n == 1 else "false"
    examples = [
        {"input": "19", "output": "true"},
        {"input": "2", "output": "false"},
    ]
    hidden = []
    for n in [1, 7, 10, 13, 19, 23, 28, 4, 16, 20, 100, 99, 1000]:
        hidden.append({"input": str(n), "output": solve(str(n))})
    for _ in range(50):
        n = random.randint(1, 10**6)
        hidden.append({"input": str(n), "output": solve(str(n))})
    add("B038", "Baxtli son (Happy Number)",
        "Jarayon: sonning HAR BIR raqamining KVADRATINI hisoblang va ularni qo'shing. Yangi songa nisbatan amalni TAKRORLANG.\n\n"
        "Misol: 19 ni tekshiramiz:\n"
        "  19 → 1² + 9² = 1 + 81 = 82\n"
        "  82 → 8² + 2² = 64 + 4 = 68\n"
        "  68 → 6² + 8² = 36 + 64 = 100\n"
        "  100 → 1² + 0² + 0² = 1 ← TO'XTAYDI ✅ → 19 baxtli (true)\n\n"
        "Misol (baxtsiz): 2 → 4 → 16 → 37 → 58 → 89 → 145 → 42 → 20 → 4 ← oldin uchragan! Sikl boshlandi → false.\n\n"
        "MUHIM: Agar 1 ga kelmasa, jarayon doim siklga (oldin uchragan songa) qaytadi. Shuning uchun ko'rilgan sonlarni 'set' (to'plam) da saqlab, qayta uchraganini sezsangiz — false; 1 ga yetsangiz — true.",
        "Bir butun son n.", "true (baxtli) yoki false.",
        "1 ≤ n ≤ 2^31-1",
        examples, hidden, "easy", "Arifmetika", "true")

# B039: Count Primes (LC#204)
def p_b039():
    def solve(inp):
        n = int(inp.strip())
        if n < 2: return "0"
        is_p = [True]*(n)
        is_p[0]=is_p[1]=False
        for i in range(2, int(n**0.5)+1):
            if is_p[i]:
                for j in range(i*i, n, i):
                    is_p[j] = False
        return str(sum(is_p))
    examples = [
        {"input": "10", "output": "4", "explanation": "2,3,5,7"},
        {"input": "0", "output": "0"},
        {"input": "1", "output": "0"},
    ]
    hidden = []
    for n in [0, 1, 2, 3, 5, 10, 20, 100, 500, 1000, 5000, 10000]:
        hidden.append({"input": str(n), "output": solve(str(n))})
    for _ in range(50):
        n = random.randint(0, 50000)
        hidden.append({"input": str(n), "output": solve(str(n))})
    add("B039", "Tub sonlar soni (Count Primes)",
        "TUB SON — 1 va o'zidan boshqa hech qanday songa bo'linmaydigan, 1 dan katta natural son. Masalan: 2, 3, 5, 7, 11, 13, 17, ...\n"
        "(1 — tub emas, 4=2·2 — tub emas, 9=3·3 — tub emas).\n\n"
        "Vazifa: n dan QAT'IY KICHIK (n ning o'zi kirmaydi) tub sonlar sonini hisoblang. Masalan n=10 → 2,3,5,7 → 4 ta.\n\n"
        "Tezkor usul — ERATOSFEN ELAGI:\n"
        "  1) 0..n-1 uchun is_prime[i]=true massivi ochib oling, 0 va 1 ni false qiling.\n"
        "  2) i=2 dan boshlab: agar is_prime[i] bo'lsa, uning barcha karralarini (i*i, i*i+i, i*i+2i, ...) false qiling.\n"
        "  3) Oxirida is_prime'da true bo'lganlarni sanang.\n"
        "Bu O(n·log·log·n) tezlikda ishlaydi.",
        "Bir musbat butun son n.", "Tublar soni.",
        "0 ≤ n ≤ 5·10^6",
        examples, hidden, "easy", "Arifmetika", "4")

# B040: Excel Sheet Column Number (LC#171)
def p_b040():
    def solve(inp):
        s = inp.strip()
        r = 0
        for c in s:
            r = r*26 + (ord(c)-ord('A')+1)
        return str(r)
    examples = [
        {"input": "A", "output": "1"},
        {"input": "AB", "output": "28"},
        {"input": "ZY", "output": "701"},
    ]
    hidden = []
    samples = ["A", "B", "Z", "AA", "AZ", "BA", "ZZ", "AAA", "AMJ", "FXSHRXW"]
    for s in samples:
        hidden.append({"input": s, "output": solve(s)})
    for _ in range(55):
        s = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=random.randint(1,7)))
        hidden.append({"input": s, "output": solve(s)})
    add("B040", "Excel ustun raqami (Excel Sheet Column Number)",
        "Excel ustunining harfli nomini berilganida, unga mos keladigan ustun raqamini qaytaring.\n\n"
        "Masalan, Excelda ustunlar shunday raqamlanadi:\n"
        "  A -> 1\n  B -> 2\n  ... \n  Z -> 26\n"
        "  AA -> 27\n  AB -> 28\n"
        "  ZY -> 701\n\n"
        "Bu 26 lik sanoq sistemasiga juda o'xshaydi. Har bir harf orqasidan yangi harf qo'shilsa, avvalgi qiymat 26 ga ko'payadi va yangi harfning qiymati (1 dan 26 gacha) qo'shiladi.",
        "Bir qatorda Excel ustun.", "Son raqami.",
        "1 ≤ uzunlik ≤ 7, faqat katta lotin harflari",
        examples, hidden, "easy", "Arifmetika", "1")

# B041: Excel Sheet Column Title (LC#168)
def p_b041():
    def solve(inp):
        n = int(inp.strip())
        s = ""
        while n > 0:
            n -= 1
            s = chr(ord('A') + n%26) + s
            n //= 26
        return s
    examples = [
        {"input": "1", "output": "A"},
        {"input": "28", "output": "AB"},
        {"input": "701", "output": "ZY"},
    ]
    hidden = []
    for n in [1, 26, 27, 52, 53, 702, 703, 2147483647]:
        hidden.append({"input": str(n), "output": solve(str(n))})
    for _ in range(55):
        n = random.randint(1, 100000)
        hidden.append({"input": str(n), "output": solve(str(n))})
    add("B041", "Excel ustun nomi (Excel Sheet Column Title)",
        "Musbat butun son berilgan, uni Excel ustuni harfiga aylantiring.\n\n"
        "Masalan:\n"
        "  1 -> A\n  26 -> Z\n  27 -> AA\n\n"
        "Tushuntirish: Bu teskari jarayon (26 lik sistemaga o'tish). Lekin indekslar 0 emas, 1 dan boshlanishi sababli, har qadamda n-1 qilib olinib so'ng 26 ga bo'linadi:\n"
        "  qoldiq = (n - 1) % 26, keyin uni harfga aylantiramiz va javob boshiga qo'shamiz.\n"
        "  n = (n - 1) // 26, shu taxlit n 0 bo'lguncha davom etamiz.",
        "Bir musbat butun son n.", "Excel ustun harfi.",
        "1 ≤ n ≤ 2^31-1",
        examples, hidden, "easy", "Arifmetika", "A")

# B042: Factorial Trailing Zeroes (LC#172)
def p_b042():
    def solve(inp):
        n = int(inp.strip())
        c = 0
        while n > 0:
            n //= 5
            c += n
        return str(c)
    examples = [
        {"input": "5", "output": "1", "explanation": "5!=120 da 1 ta nol"},
        {"input": "10", "output": "2"},
        {"input": "0", "output": "0"},
    ]
    hidden = []
    for n in [0, 1, 4, 5, 25, 125, 100, 1000, 10000]:
        hidden.append({"input": str(n), "output": solve(str(n))})
    for _ in range(50):
        n = random.randint(0, 10000)
        hidden.append({"input": str(n), "output": solve(str(n))})
    add("B042", "Faktorialdagi oxirgi nollar (Factorial Trailing Zeroes)",
        "FAKTORIAL (n!) — 1 dan n gacha bo'lgan barcha natural sonlar ko'paytmasi.\n"
        "  Masalan: 5! = 1·2·3·4·5 = 120,    10! = 3 628 800,    0! = 1 (kelishuv).\n\n"
        "Vazifa: n! sonining OXIRIDA nechta NOL borligini toping (sonning o'zini hisoblamasdan).\n"
        "  120 → 1 ta nol,   3628800 → 2 ta nol.\n\n"
        "MATEMATIK SIR: Oxiridagi har nol bu — ko'paytma ichidagi BIR JUFT (2 va 5) dir, chunki 2·5 = 10. n! da 2 lar 5 lardan ko'p bo'lgani uchun, faqat 5 larni sanash yetadi.\n"
        "  n! ichidagi 5 lar soni = n/5 + n/25 + n/125 + ...  (butun bo'lish)\n"
        "Misol: n=100 → 100/5=20, 20/5=4, 4/5=0 → 24 ta nol.",
        "Bir manfiy bo'lmagan butun son.", "Nollar soni.",
        "0 ≤ n ≤ 10^4",
        examples, hidden, "easy", "Arifmetika", "1")

# B043: Number of 1 Bits (LC#191) — Hamming weight
def p_b043():
    def solve(inp):
        n = int(inp.strip())
        return str(bin(n).count('1'))
    examples = [
        {"input": "11", "output": "3", "explanation": "11 = 1011₂"},
        {"input": "128", "output": "1"},
    ]
    hidden = []
    for n in [0, 1, 2, 3, 7, 8, 15, 16, 255, 256, 1023, 4294967295]:
        hidden.append({"input": str(n), "output": solve(str(n))})
    for _ in range(50):
        n = random.randint(0, 2**32 - 1)
        hidden.append({"input": str(n), "output": solve(str(n))})
    add("B043", "Bitlar soni (Number of 1 Bits)",
        "IKKILIK (binary) tasvir — sonni faqat 0 va 1 dan iborat ko'rinishda yozish (kompyuterning ichki sanoq tizimi).\n"
        "  Misol: 5 = 101₂  (chunki 4+1),   11 = 1011₂  (8+2+1),   8 = 1000₂.\n\n"
        "HAMMING OG'IRLIGI (Hamming weight) — sonning ikkilik tasvirida nechta 1 borligi.\n"
        "  Misol: 11 = 1011₂ → 3 ta 1.    255 = 11111111₂ → 8 ta 1.\n\n"
        "Eng oddiy usul: bin(n) ishlatib '1' larni sanash. Bit hiyla: while n: n &= n-1; cnt += 1 (har iteratsiyada eng o'ngdagi 1 ni o'chiradi).",
        "Bir musbat butun son.", "1 lar soni.",
        "0 ≤ n ≤ 2^32-1",
        examples, hidden, "easy", "Bit amallari", "3")

# B044: Hamming Distance (LC#461)
def p_b044():
    def solve(inp):
        a, b = map(int, inp.strip().split())
        return str(bin(a ^ b).count('1'))
    examples = [
        {"input": "1 4", "output": "2"},
        {"input": "3 1", "output": "1"},
    ]
    hidden = []
    for _ in range(55):
        a = random.randint(0, 1<<20)
        b = random.randint(0, 1<<20)
        inp = f"{a} {b}"
        hidden.append({"input": inp, "output": solve(inp)})
    add("B044", "Hamming masofasi (Hamming Distance)",
        "HAMMING MASOFASI — ikkita son ikkilik (binary) ko'rinishda solishtirganda nechta pozitsiyada bitlari FARQ qilishi.\n\n"
        "Misol: 1 va 4:\n"
        "  1 = 0 0 1₂\n"
        "  4 = 1 0 0₂\n"
        "          ↑   ↑\n"
        "  2 ta pozitsiyada farq qilmoqda → masofa = 2.\n\n"
        "Tezkor usul: a XOR b natijasidagi 1 lar sonini sanang. Sababi — XOR aynan farqli bitlarni 1 qilib qo'yadi.\n"
        "  a=1=001, b=4=100, a^b = 101 → 2 ta 1 → javob 2.",
        "Ikki son (probel bilan).", "Hamming masofasi.",
        "0 ≤ a, b ≤ 2^31-1",
        examples, hidden, "easy", "Bit amallari", "2")

# B045: Sum of Two Integers — without + (LC#371) — Python so simply add but conceptual
def p_b045():
    def solve(inp):
        a, b = map(int, inp.strip().split())
        return str(a + b)
    examples = [
        {"input": "1 2", "output": "3"},
        {"input": "-1 1", "output": "0"},
    ]
    hidden = []
    for _ in range(55):
        a = random.randint(-1000, 1000)
        b = random.randint(-1000, 1000)
        inp = f"{a} {b}"
        hidden.append({"input": inp, "output": solve(inp)})
    add("B045", "Ikki sonning yig'indisi (Sum of Two Integers)",
        "+ yoki - operatorlarini ishlatmasdan, a va b sonlarining yig'indisini hisoblang!\n\n"
        "Buni qanday qilish mumkin? Bit amallari (Bitwise operations) yordamida:\n"
        "  1) a ^ b (XOR) — yig'indini xotirada saqlamasdan hisoblaydi (ya'ni 1+0=1, 0+1=1, 0+0=0, lekin 1+1=0 deb oladi).\n"
        "  2) (a & b) << 1 — xotiradagi \"o'tish\" (carry) bitlarini hisoblaydi (faqat ikkisi ham 1 bo'lsa bitta chapga suriladi).\n"
        "Shu ikki natijani yig'indini topmaguncha qayta-qayta bajaramiz.",
        "Ikki son (probel bilan).", "Yig'indi.",
        "-1000 ≤ a, b ≤ 1000",
        examples, hidden, "easy", "Bit amallari", "3")


# ═══════════════════════════════════════════════════════════════════════════
# HASH / SET (10 ta)
# ═══════════════════════════════════════════════════════════════════════════

# B046: Intersection of Two Arrays (LC#349)
def p_b046():
    def solve(inp):
        a, b = inp.strip().split('\n')
        s = sorted(set(a.split()) & set(b.split()), key=int)
        return ' '.join(s) if s else ""
    examples = [
        {"input": "1 2 2 1\n2 2", "output": "2"},
        {"input": "4 9 5\n9 4 9 8 4", "output": "4 9"},
    ]
    hidden = []
    for _ in range(55):
        a = [random.randint(1, 30) for _ in range(random.randint(1, 8))]
        b = [random.randint(1, 30) for _ in range(random.randint(1, 8))]
        inp = f"{' '.join(map(str,a))}\n{' '.join(map(str,b))}"
        hidden.append({"input": inp, "output": solve(inp)})
    add("B046", "Ikki massiv kesishmasi (Intersection of Two Arrays)",
        "Ikki massivning umumiy elementlarini takrorsiz, o'sish tartibida chiqaring.",
        "Birinchi qatorda 1-massiv, ikkinchida 2-massiv.", "Umumiy elementlar.",
        "1 ≤ uzunliklar ≤ 1000",
        examples, hidden, "easy", "Hash", "2")

# B047: Intersection of Two Arrays II (LC#350) — with multiplicity
def p_b047():
    def solve(inp):
        a, b = inp.strip().split('\n')
        from collections import Counter
        ca = Counter(a.split())
        cb = Counter(b.split())
        out = []
        for k in ca:
            if k in cb:
                out.extend([k] * min(ca[k], cb[k]))
        return ' '.join(out)
    examples = [
        {"input": "1 2 2 1\n2 2", "output": "2 2"},
        {"input": "4 9 5\n9 4 9 8 4", "output": "4 9", "explanation": "tartibi 2-massivga mos"},
    ]
    hidden = []
    for _ in range(55):
        a = [str(random.randint(1, 10)) for _ in range(random.randint(1, 8))]
        b = [str(random.randint(1, 10)) for _ in range(random.randint(1, 8))]
        inp = f"{' '.join(a)}\n{' '.join(b)}"
        hidden.append({"input": inp, "output": solve(inp)})
    add("B047", "Kesishma takrorlash bilan (Intersection II)",
        "Ikki massivning umumiy elementlarini chiqaring — har element ikkala massivda uchragancha takrorlanadi.",
        "Birinchi qatorda 1-massiv, ikkinchida 2-massiv.", "Kesishma.",
        "1 ≤ uzunliklar ≤ 1000",
        examples, hidden, "easy", "Hash", "2 2")

# B048: Word Pattern (LC#290)
def p_b048():
    def solve(inp):
        p, s = inp.strip().split('\n')
        words = s.split()
        if len(p) != len(words): return "false"
        return "true" if [p.index(c) for c in p] == [words.index(w) for w in words] else "false"
    examples = [
        {"input": "abba\ndog cat cat dog", "output": "true"},
        {"input": "abba\ndog cat cat fish", "output": "false"},
        {"input": "aaaa\ndog cat cat dog", "output": "false"},
    ]
    hidden = []
    samples = [
        ("abc", "x y z"), ("abba", "a b b a"), ("a", "x"),
        ("ab", "x y x"), ("aaa", "x x x"), ("ab", "x x"),
    ]
    for p, s in samples:
        inp = f"{p}\n{s}"
        hidden.append({"input": inp, "output": solve(inp)})
    for _ in range(55):
        p = ''.join(random.choices('ab', k=random.randint(1, 5)))
        s = ' '.join(random.choices(['x','y'], k=random.randint(1, 5)))
        inp = f"{p}\n{s}"
        hidden.append({"input": inp, "output": solve(inp)})
    add("B048", "So'z andozasi (Word Pattern)",
        "ANDOZA (pattern) — harflar ketma-ketligi (mas: 'abba'). Har bir harf BIR so'zga \"taqdim\" qilinadi.\n\n"
        "Vazifa: Andozadagi harflar ketma-ketligi va berilgan so'zlar ketma-ketligi BIR XIL STRUKTURAGA ega bo'lsa true.\n"
        "  • har harf — DOIM bir xil so'zga aks etishi kerak,\n"
        "  • har so'z — DOIM bir xil harfga aks etishi kerak (bijeksiya / 1-ga-1).\n\n"
        "Misollar:\n"
        "  pattern='abba', so'zlar='dog cat cat dog'  → true  (a↔dog, b↔cat)\n"
        "  pattern='abba', so'zlar='dog cat cat fish' → false (a oxirida 'fish' ga ko'chdi)\n"
        "  pattern='aaaa', so'zlar='dog cat cat dog'  → false (a — bitta so'zga mos kelishi kerak edi, lekin 4 xil so'z bor)\n"
        "  pattern='abba', so'zlar='dog dog dog dog'  → false (a va b ikkalasi ham 'dog' ga ko'chdi — har xil so'zga ko'chishi kerak edi)\n\n"
        "Yondashuv: ikki tomonlama lug'at (harf→so'z va so'z→harf) yoki indeks-to'g'ri-keladimi solishtirish.",
        "Birinchi qatorda pattern, ikkinchida so'zlar.", "true yoki false.",
        "1 ≤ |pattern| ≤ 300",
        examples, hidden, "easy", "Hash", "true")

# B049: Isomorphic Strings (LC#205)
def p_b049():
    def solve(inp):
        s, t = inp.strip().split('\n')
        if len(s) != len(t): return "false"
        return "true" if [s.index(c) for c in s] == [t.index(c) for c in t] else "false"
    examples = [
        {"input": "egg\nadd", "output": "true"},
        {"input": "foo\nbar", "output": "false"},
        {"input": "paper\ntitle", "output": "true"},
    ]
    hidden = []
    for s, t in [("ab", "ba"), ("abc", "abc"), ("aab", "xyz"), ("aab", "xxy")]:
        inp = f"{s}\n{t}"
        hidden.append({"input": inp, "output": solve(inp)})
    for _ in range(55):
        n = random.randint(1, 8)
        s = ''.join(random.choices('abc', k=n))
        t = ''.join(random.choices('xyz', k=n))
        inp = f"{s}\n{t}"
        hidden.append({"input": inp, "output": solve(inp)})
    add("B049", "Izomorf satrlar (Isomorphic Strings)",
        "IZOMORF (isomorphic) — \"bir xil shaklga ega\" degani. Ikki satrning har bir harfini bir-biriga MOS qo'yib chiqsa, ko'rinishi mos tushadigan bo'lsa — ular izomorf.\n\n"
        "QOIDA: Bijeksiya (1-ga-1 to'g'ri keladigan) almashtirish bo'lishi kerak. Ya'ni:\n"
        "  • s ning har bir harfi t da DOIM bir xil harfga ko'chadi,\n"
        "  • IKKI HAR XIL harf bir xil harfga ko'chmaydi.\n\n"
        "Misollar:\n"
        "  s='egg', t='add'  → true.  e↔a, g↔d.  (e doim a, g doim d)\n"
        "  s='foo', t='bar'  → false. f↔b, o↔a, lekin keyingi o ham 'r' bo'lib qoldi (o ikki xil harfga aylandi)\n"
        "  s='paper', t='title' → true. p↔t, a↔i, e↔l, r↔e.\n"
        "  s='ab', t='aa'    → false. a va b ikkalasi ham 'a' ga ko'chdi (har xil harflar bir xil harfga ko'chmasligi kerak)\n\n"
        "Yondashuv: ikki tomonlama lug'at (s→t va t→s) yoki indekslarga aylantirib taqqoslash.",
        "Birinchi qatorda s, ikkinchida t.", "true yoki false.",
        "1 ≤ uzunliklar ≤ 5·10^4",
        examples, hidden, "easy", "Hash", "true")

# B050: Majority Element (LC#169)
def p_b050():
    def solve(inp):
        nums = inp.strip().split()
        from collections import Counter
        c = Counter(nums)
        return c.most_common(1)[0][0]
    examples = [
        {"input": "3 2 3", "output": "3"},
        {"input": "2 2 1 1 1 2 2", "output": "2"},
    ]
    hidden = []
    for _ in range(55):
        n = random.randint(1, 15)
        m = random.randint(0, 9)
        nums = [m] * (n//2 + 1)
        nums.extend(random.randint(0, 9) for _ in range(n - len(nums)))
        random.shuffle(nums)
        inp = ' '.join(map(str, nums))
        hidden.append({"input": inp, "output": solve(inp)})
    add("B050", "Ko'pchilik element (Majority Element)",
        "Massivda n/2 dan ko'p marta uchraydigan element borligi kafolatlangan. Uni toping.",
        "Bir qatorda massiv.", "Ko'pchilik element.",
        "1 ≤ n ≤ 5·10^4",
        examples, hidden, "easy", "Hash", "3")

# B051: Two Sum II — sorted (LC#167)
def p_b051():
    def solve(inp):
        lines = inp.strip().split('\n')
        nums = list(map(int, lines[0].split()))
        t = int(lines[1])
        l, r = 0, len(nums)-1
        while l < r:
            s = nums[l]+nums[r]
            if s == t: return f"{l+1} {r+1}"
            elif s < t: l += 1
            else: r -= 1
        return "-1"
    examples = [
        {"input": "2 7 11 15\n9", "output": "1 2"},
        {"input": "2 3 4\n6", "output": "1 3"},
    ]
    hidden = []
    for _ in range(55):
        n = random.randint(2, 12)
        nums = sorted(random.randint(-50, 50) for _ in range(n))
        i, j = random.sample(range(n), 2)
        target = nums[i]+nums[j]
        inp = f"{' '.join(map(str,nums))}\n{target}"
        hidden.append({"input": inp, "output": solve(inp)})
    add("B051", "Saralangan ikkita son (Two Sum II)",
        "Sizga O'SISH TARTIBIDA saralangan massiv va target soni berilgan.\n"
        "Yig'indisi target ga teng bo'ladigan ikkita sonni toping va ularning 1 dan boshlanuvchi indekslarini qaytaring.\n\n"
        "Eslatma: Qo'shimcha xotira (O(1)) ishlatilishi kerak.\n\n"
        "Ikki ko'rsatkich (Two Pointers) yondashuvi:\n"
        "Chapdan (left=0) va o'ngdan (right=n-1) boshlang.\n"
        "  • Agar nums[left] + nums[right] == target bo'lsa, javob topildi.\n"
        "  • Agar yig'indi target dan KICHIK bo'lsa, kattaroq son kerak -> left ni o'ngga suramiz (left++).\n"
        "  • Agar yig'indi target dan KATTA bo'lsa, kichikroq son kerak -> right ni chapga suramiz (right--).",
        "Birinchi qatorda saralangan massiv, ikkinchida target.", "Ikki indeks.",
        "2 ≤ n ≤ 3·10^4. Yagona yechim mavjud.",
        examples, hidden, "easy", "Ikki ko'rsatkich", "1 2")

# B052: Set Mismatch (LC#645)
def p_b052():
    def solve(inp):
        nums = list(map(int, inp.strip().split()))
        n = len(nums)
        seen = set()
        dup = 0
        for x in nums:
            if x in seen: dup = x
            seen.add(x)
        miss = n*(n+1)//2 - sum(seen)
        return f"{dup} {miss}"
    examples = [
        {"input": "1 2 2 4", "output": "2 3"},
        {"input": "1 1", "output": "1 2"},
    ]
    hidden = []
    for _ in range(55):
        n = random.randint(2, 15)
        nums = list(range(1, n+1))
        miss = nums.pop(random.randint(0, n-1))
        nums.append(random.choice(nums))
        random.shuffle(nums)
        inp = ' '.join(map(str, nums))
        hidden.append({"input": inp, "output": solve(inp)})
    add("B052", "To'plam nomuvofiqligi (Set Mismatch)",
        "1..n sonlardan iborat bo'lishi kerak edi, lekin bittasi takrorlanib, bittasi yo'qolgan. Takrorlangan va yo'qolgan sonni chiqaring.",
        "Bir qatorda n ta son.", "Takrorlangan va yo'qolgan (probel bilan).",
        "2 ≤ n ≤ 10^4",
        examples, hidden, "easy", "Hash", "2 3")

# B053: Number of Good Pairs (LC#1512)
def p_b053():
    def solve(inp):
        nums = inp.strip().split()
        from collections import Counter
        c = Counter(nums)
        return str(sum(v*(v-1)//2 for v in c.values()))
    examples = [
        {"input": "1 2 3 1 1 3", "output": "4"},
        {"input": "1 1 1 1", "output": "6"},
    ]
    hidden = []
    for _ in range(55):
        n = random.randint(1, 15)
        nums = [random.randint(1, 5) for _ in range(n)]
        inp = ' '.join(map(str, nums))
        hidden.append({"input": inp, "output": solve(inp)})
    add("B053", "Yaxshi juftliklar soni (Number of Good Pairs)",
        "Massivda nums[i]==nums[j] va i<j bo'lgan juftliklar sonini chiqaring.",
        "Bir qatorda massiv.", "Juftliklar soni.",
        "1 ≤ n ≤ 100",
        examples, hidden, "easy", "Hash", "4")

# B054: Most Common Word (simplified)
def p_b054():
    def solve(inp):
        from collections import Counter
        words = inp.strip().lower().split()
        c = Counter(words)
        # most common, ties: alphabetically first
        max_count = max(c.values())
        cands = sorted(w for w in c if c[w] == max_count)
        return cands[0]
    examples = [
        {"input": "the quick brown fox jumps over the lazy dog the", "output": "the"},
        {"input": "a b a b c", "output": "a", "explanation": "a va b — alfavit bo'yicha a"},
    ]
    hidden = []
    samples = ["aa bb aa", "x y z", "one two three two one one", "cat dog cat dog"]
    for s in samples:
        hidden.append({"input": s, "output": solve(s)})
    for _ in range(55):
        words = [''.join(random.choices('abc', k=random.randint(1,3))) for _ in range(random.randint(1,8))]
        s = ' '.join(words)
        hidden.append({"input": s, "output": solve(s)})
    add("B054", "Eng ko'p uchraydigan so'z",
        "Satrdagi eng ko'p uchraydigan so'zni chiqaring. Bir nechta bir xil eng ko'pli bo'lsa, alfavit bo'yicha birinchisini.",
        "Bir qatorda matn.", "Eng ko'p so'z (kichik harflarda).",
        "1 ≤ matn uzunligi ≤ 1000",
        examples, hidden, "easy", "Hash", "the")

# B055: Find the Town Judge — simplified to: find unique element that appears in all groups
# Skip — graph problem complex. Replace with: Unique Number of Occurrences (LC#1207)
def p_b055():
    def solve(inp):
        nums = inp.strip().split()
        from collections import Counter
        c = Counter(nums)
        return "true" if len(set(c.values())) == len(c) else "false"
    examples = [
        {"input": "1 2 2 1 1 3", "output": "true", "explanation": "1: 3 marta, 2: 2 marta, 3: 1 marta — barchasi turlicha"},
        {"input": "1 2", "output": "false", "explanation": "ikkalasi ham 1 marta"},
        {"input": "-3 0 1 -3 1 1 1 -3 10 0", "output": "true"},
    ]
    hidden = []
    for _ in range(55):
        n = random.randint(1, 12)
        nums = [random.randint(-3, 3) for _ in range(n)]
        inp = ' '.join(map(str, nums))
        hidden.append({"input": inp, "output": solve(inp)})
    add("B055", "Noyob takrorlanish soni (Unique Number of Occurrences)",
        "Massivda har sonning uchrash soni boshqalardan farqli bo'lsa true.",
        "Bir qatorda massiv.", "true yoki false.",
        "1 ≤ n ≤ 1000",
        examples, hidden, "easy", "Hash", "true")


# ═══════════════════════════════════════════════════════════════════════════
# IKKI KO'RSATKICH (10 ta)
# ═══════════════════════════════════════════════════════════════════════════

# B056: Remove Duplicates from Sorted Array (LC#26) — output count and array
def p_b056():
    def solve(inp):
        nums = list(map(int, inp.strip().split()))
        out = []
        for x in nums:
            if not out or out[-1] != x: out.append(x)
        return f"{len(out)}\n{' '.join(map(str, out))}"
    examples = [
        {"input": "1 1 2", "output": "2\n1 2"},
        {"input": "0 0 1 1 1 2 2 3 3 4", "output": "5\n0 1 2 3 4"},
    ]
    hidden = []
    for _ in range(55):
        n = random.randint(1, 15)
        nums = sorted(random.randint(0, 5) for _ in range(n))
        inp = ' '.join(map(str, nums))
        hidden.append({"input": inp, "output": solve(inp)})
    add("B056", "Saralangan massivdan dublikatlarni o'chirish",
        "Saralangan massivdan takrorlangan elementlarni olib tashlab, faqat noyob o'sish tartibidagi qatorni chiqaring.",
        "Bir qatorda saralangan massiv.", "Birinchi qatorda noyoblar soni, ikkinchida noyoblar massivi.",
        "0 ≤ n ≤ 3·10^4",
        examples, hidden, "easy", "Ikki ko'rsatkich", "2\n1 2")

# B057: Remove Element (LC#27)
def p_b057():
    def solve(inp):
        lines = inp.strip().split('\n')
        nums = list(map(int, lines[0].split()))
        v = int(lines[1])
        out = [x for x in nums if x != v]
        return f"{len(out)}\n{' '.join(map(str, out))}".strip()
    examples = [
        {"input": "3 2 2 3\n3", "output": "2\n2 2"},
        {"input": "0 1 2 2 3 0 4 2\n2", "output": "5\n0 1 3 0 4"},
    ]
    hidden = []
    for _ in range(55):
        n = random.randint(1, 15)
        v = random.randint(0, 5)
        nums = [random.randint(0, 5) for _ in range(n)]
        inp = f"{' '.join(map(str,nums))}\n{v}"
        hidden.append({"input": inp, "output": solve(inp)})
    add("B057", "Elementni o'chirish (Remove Element)",
        "Massivdan berilgan val ga teng barcha elementlarni o'chiring.",
        "Birinchi qatorda massiv, ikkinchida val.", "Birinchi qatorda yangi uzunlik, ikkinchida yangi massiv.",
        "0 ≤ n ≤ 100",
        examples, hidden, "easy", "Ikki ko'rsatkich", "2\n2 2")

# B058: Merge Two Sorted Arrays simplified (LC#88)
def p_b058():
    def solve(inp):
        parts = inp.split('\n', 1)
        a = list(map(int, parts[0].split())) if parts[0].strip() else []
        b = list(map(int, parts[1].split())) if len(parts) > 1 and parts[1].strip() else []
        i = j = 0
        out = []
        while i < len(a) and j < len(b):
            if a[i] <= b[j]: out.append(a[i]); i += 1
            else: out.append(b[j]); j += 1
        out.extend(a[i:]); out.extend(b[j:])
        return ' '.join(map(str, out))
    examples = [
        {"input": "1 2 3\n2 5 6", "output": "1 2 2 3 5 6"},
        {"input": "1\n", "output": "1"},
    ]
    hidden = []
    for _ in range(55):
        a = sorted(random.randint(0, 50) for _ in range(random.randint(0, 8)))
        b = sorted(random.randint(0, 50) for _ in range(random.randint(0, 8)))
        inp = f"{' '.join(map(str,a))}\n{' '.join(map(str,b))}"
        hidden.append({"input": inp, "output": solve(inp)})
    add("B058", "Saralangan ikki massivni birlashtirish (Merge Sorted Arrays)",
        "Ikki saralangan massivni birlashtirib, saralangan natija qaytaring.",
        "Birinchi qatorda 1-massiv, ikkinchida 2-massiv.", "Saralangan birlashma.",
        "0 ≤ uzunliklar ≤ 200",
        examples, hidden, "easy", "Ikki ko'rsatkich", "1 2 2 3 5 6")

# B059: Long Pressed Name (LC#925)
def p_b059():
    def solve(inp):
        name, typed = inp.strip().split('\n')
        i = j = 0
        while i < len(name) and j < len(typed):
            if name[i] == typed[j]:
                i += 1; j += 1
            elif j > 0 and typed[j] == typed[j-1]:
                j += 1
            else:
                return "false"
        while j < len(typed):
            if j > 0 and typed[j] == typed[j-1]: j += 1
            else: return "false"
        return "true" if i == len(name) else "false"
    examples = [
        {"input": "alex\naaleex", "output": "true"},
        {"input": "saeed\nssaaedd", "output": "false"},
    ]
    hidden = []
    for _ in range(55):
        name = ''.join(random.choices('abcd', k=random.randint(2,6)))
        typed = ''.join(c * random.randint(1, 3) for c in name)
        if random.random() < 0.3:
            typed = typed + random.choice('abcd')  # mismatch
        inp = f"{name}\n{typed}"
        hidden.append({"input": inp, "output": solve(inp)})
    add("B059", "Bosib turilgan ism (Long Pressed Name)",
        "name — yozish kerak bo'lgan ism. typed — biror harf uzoq bosib qolinishi natijasida ko'paygan harflar bilan ism. typed name dan to'g'ri kelib chiqishi mumkinmi?",
        "Birinchi qatorda name, ikkinchida typed.", "true yoki false.",
        "1 ≤ uzunlik ≤ 1000, faqat kichik harflar",
        examples, hidden, "easy", "Ikki ko'rsatkich", "true")

# B060: Backspace String Compare (LC#844)
def p_b060():
    def solve(inp):
        s, t = inp.strip().split('\n')
        def proc(x):
            st = []
            for c in x:
                if c == '#':
                    if st: st.pop()
                else: st.append(c)
            return ''.join(st)
        return "true" if proc(s) == proc(t) else "false"
    examples = [
        {"input": "ab#c\nad#c", "output": "true", "explanation": "ikkalasi ham 'ac' ga aylanadi"},
        {"input": "a##c\n#a#c", "output": "true"},
        {"input": "a#c\nb", "output": "false"},
    ]
    hidden = []
    for _ in range(55):
        s = ''.join(random.choices('abcd#', weights=[3,3,3,3,2], k=random.randint(1, 10)))
        t = ''.join(random.choices('abcd#', weights=[3,3,3,3,2], k=random.randint(1, 10)))
        inp = f"{s}\n{t}"
        hidden.append({"input": inp, "output": solve(inp)})
    add("B060", "Backspace solishtirish (Backspace String Compare)",
        "'#' belgisi backspace (oxirgi harfni o'chiradi). Ikki satr backspaceni qo'llagandan keyin teng bo'lsa true.",
        "Birinchi qatorda s, ikkinchida t.", "true yoki false.",
        "1 ≤ uzunliklar ≤ 200",
        examples, hidden, "easy", "Stek", "true")

# B061: Find Pivot Index (LC#724)
def p_b061():
    def solve(inp):
        nums = list(map(int, inp.strip().split()))
        total = sum(nums)
        left = 0
        for i, x in enumerate(nums):
            if left == total - left - x: return str(i)
            left += x
        return "-1"
    examples = [
        {"input": "1 7 3 6 5 6", "output": "3"},
        {"input": "1 2 3", "output": "-1"},
        {"input": "2 1 -1", "output": "0"},
    ]
    hidden = []
    for _ in range(55):
        n = random.randint(1, 12)
        nums = [random.randint(-10, 10) for _ in range(n)]
        inp = ' '.join(map(str, nums))
        hidden.append({"input": inp, "output": solve(inp)})
    add("B061", "Markaziy indeks (Find Pivot Index)",
        "Massivning shunday 'Markaziy' (Pivot) indeksini topingki, undan CHAPDAGI sonlar yig'indisi va O'NGDAGI sonlar yig'indisi TENG bo'lsin.\n"
        "Agar shunday indeks bo'lmasa -1 chiqaring. (Agar u 0-indeks bo'lsa chap tomoni 0 deb olinadi).\n\n"
        "Optimal Yechim (O(N)):\n"
        "  1) Butun massiv yig'indisini (total) hisoblab oling.\n"
        "  2) 'left_sum' degan o'zgaruvchi (boshida 0) olamiz va massiv bo'ylab yuramiz.\n"
        "  3) Har bir qadamda, agar left_sum == total - left_sum - nums[i] bo'lsa, demak i-indeks markaz.\n"
        "  4) Agar topilmasa, left_sum ga joriy sonni qo'shib ketaveramiz.",
        "Bir qatorda massiv.", "Indeks yoki -1.",
        "1 ≤ n ≤ 10^4",
        examples, hidden, "easy", "Massivlar", "3")

# B062: Reverse Only Letters (LC#917)
def p_b062():
    def solve(inp):
        s = list(inp.strip())
        l, r = 0, len(s)-1
        while l < r:
            while l < r and not s[l].isalpha(): l += 1
            while l < r and not s[r].isalpha(): r -= 1
            s[l], s[r] = s[r], s[l]
            l += 1; r -= 1
        return ''.join(s)
    examples = [
        {"input": "ab-cd", "output": "dc-ba"},
        {"input": "a-bC-dEf-ghIj", "output": "j-Ih-gfE-dCba"},
    ]
    hidden = []
    samples = ["a", "ab", "a-b", "1-2-3", "Test1ng-Leet=code-Q!"]
    for s in samples:
        hidden.append({"input": s, "output": solve(s)})
    for _ in range(55):
        chars = list('abcdef!-=12')
        s = ''.join(random.choices(chars, k=random.randint(1, 10)))
        hidden.append({"input": s, "output": solve(s)})
    add("B062", "Faqat harflarni teskari qilish (Reverse Only Letters)",
        "Satrdagi faqat harflarni teskari joylashtiring, harf bo'lmagan belgilar joyida qoladi.",
        "Bir qatorda satr.", "Yangi satr.",
        "1 ≤ uzunlik ≤ 100",
        examples, hidden, "easy", "Ikki ko'rsatkich", "dc-ba")

# B063: Sort Array By Parity II (LC#922)
def p_b063():
    def solve(inp):
        nums = list(map(int, inp.strip().split()))
        ev = [x for x in nums if x%2 == 0]
        od = [x for x in nums if x%2 != 0]
        out = []
        for i in range(len(nums)):
            if i % 2 == 0: out.append(ev.pop(0))
            else: out.append(od.pop(0))
        return ' '.join(map(str, out))
    examples = [
        {"input": "4 2 5 7", "output": "4 5 2 7", "explanation": "indeks juft → juft son, indeks toq → toq son"},
    ]
    hidden = []
    for _ in range(55):
        n = random.randint(2, 20)
        if n % 2: n += 1
        nums = []
        for i in range(n):
            x = random.randint(0, 20)
            if i % 2 == 0:
                while x % 2: x = random.randint(0, 20)
            else:
                while x % 2 == 0: x = random.randint(0, 20)
            nums.append(x)
        random.shuffle(nums)
        inp = ' '.join(map(str, nums))
        hidden.append({"input": inp, "output": solve(inp)})
    add("B063", "Juftlik bo'yicha saralash II (Sort Array By Parity II)",
        "Massivda juft sonlar va toq sonlar teng. Juft indekslarda juft, toq indekslarda toq sonlar joylashsin.",
        "Bir qatorda massiv.", "Yangi massiv.",
        "2 ≤ n ≤ 2·10^4, n juft, juft/toq sonlar teng",
        examples, hidden, "easy", "Ikki ko'rsatkich", "4 5 2 7")

# B064: DI String Match (LC#942) — assign 0..n
def p_b064():
    def solve(inp):
        s = inp.strip()
        n = len(s)
        lo, hi = 0, n
        out = []
        for c in s:
            if c == 'I': out.append(lo); lo += 1
            else: out.append(hi); hi -= 1
        out.append(lo)
        return ' '.join(map(str, out))
    examples = [
        {"input": "IDID", "output": "0 4 1 3 2"},
        {"input": "III", "output": "0 1 2 3"},
        {"input": "DDI", "output": "3 2 0 1"},
    ]
    hidden = []
    for _ in range(55):
        s = ''.join(random.choices('ID', k=random.randint(1, 10)))
        hidden.append({"input": s, "output": solve(s)})
    add("B064", "DI satr mosligi (DI String Match)",
        "n uzunlikdagi 'I' va 'D' harflaridan iborat satr s berilgan. Sizdan 0..n sonlardan iborat (n+1 ta son) PERMUTATSIYA (har son aniq 1 marta uchraydi) tuzish so'raladi, shartlar:\n"
        "  • Agar s[i] == 'I'  →  arr[i] < arr[i+1]   (Increasing — keyingi son katta bo'ladi)\n"
        "  • Agar s[i] == 'D'  →  arr[i] > arr[i+1]   (Decreasing — keyingi son kichik bo'ladi)\n\n"
        "Misol: s = 'IDID' (uzunligi 4) — javob 5 ta sondan iborat:\n"
        "  arr = 0 4 1 3 2  →  0<4 (I✓), 4>1 (D✓), 1<3 (I✓), 3>2 (D✓)  ✅\n\n"
        "OCHKO'ZLIK YONDASHUVI: lo=0, hi=n. 'I' uchragan joyga lo ni qo'yib lo++ qiling; 'D' uchragan joyga hi ni qo'yib hi-- qiling. Oxirida lo (yoki hi) qiymatini qo'shing — bu ishlaydi va doim to'g'ri permutatsiya beradi.",
        "Bir qatorda I/D satri.", "Permutatsiya.",
        "1 ≤ |s| ≤ 10^5",
        examples, hidden, "easy", "Ikki ko'rsatkich", "0 4 1 3 2")

# B065: Valid Mountain Array (LC#941)
def p_b065():
    def solve(inp):
        nums = list(map(int, inp.strip().split()))
        n = len(nums)
        if n < 3: return "false"
        i = 0
        while i+1 < n and nums[i] < nums[i+1]: i += 1
        if i == 0 or i == n-1: return "false"
        while i+1 < n and nums[i] > nums[i+1]: i += 1
        return "true" if i == n-1 else "false"
    examples = [
        {"input": "0 3 2 1", "output": "true"},
        {"input": "3 5 5", "output": "false"},
        {"input": "0 2 3 4 5 2 1 0", "output": "true"},
    ]
    hidden = []
    samples = ["1 2 3", "1 3 2", "2 1", "0 1 2 1 0", "1 2 3 4", "5 4 3 2 1", "1 2 1 2"]
    for s in samples:
        hidden.append({"input": s, "output": solve(s)})
    for _ in range(55):
        n = random.randint(2, 8)
        nums = [random.randint(1, 5) for _ in range(n)]
        inp = ' '.join(map(str, nums))
        hidden.append({"input": inp, "output": solve(inp)})
    add("B065", "Tog' shaklidagi massiv (Valid Mountain Array)",
        "Massiv tog' shaklida bo'lsa (qattiq o'sib, keyin qattiq kamayib boruvchi) true. Cho'qqi chetda bo'lmasligi kerak.",
        "Bir qatorda massiv.", "true yoki false.",
        "3 ≤ n ≤ 10^4",
        examples, hidden, "easy", "Ikki ko'rsatkich", "true")


# ═══════════════════════════════════════════════════════════════════════════
# STEK (5 ta)
# ═══════════════════════════════════════════════════════════════════════════

# B066: Valid Parentheses (LC#20)
def p_b066():
    def solve(inp):
        s = inp.strip()
        st = []
        m = {')':'(',']':'[','}':'{'}
        for c in s:
            if c in '([{': st.append(c)
            else:
                if not st or st[-1] != m.get(c): return "false"
                st.pop()
        return "true" if not st else "false"
    examples = [
        {"input": "()", "output": "true"},
        {"input": "()[]{}", "output": "true"},
        {"input": "(]", "output": "false"},
        {"input": "([)]", "output": "false"},
        {"input": "{[]}", "output": "true"},
    ]
    hidden = []
    samples = ["", "(", ")", "((", "(())", "({[]})", "(((", ")))"]
    for s in samples:
        hidden.append({"input": s if s else "()", "output": solve(s)})
    for _ in range(55):
        s = ''.join(random.choices('()[]{}', k=random.randint(2, 10)))
        hidden.append({"input": s, "output": solve(s)})
    add("B066", "Yaroqli qavslar (Valid Parentheses)",
        "Faqatgina '(', ')', '{', '}', '[' va ']' qavslaridan iborat satr berilgan. "
        "Satrdagi qavslar yaroqli bo'lishi uchun:\n"
        "  1) Ochiq qavslar aynan o'zining turidagi qavs bilan yopilishi kerak.\n"
        "  2) Ochiq qavslar to'g'ri ketma-ketlikda yopilishi kerak.\n\n"
        "Stek (Stack) Yondashuvi:\n"
        "Har safar OCHIQ qavs kelsa, uni stekga joylaymiz. Agar YOPIQ qavs kelsa, stekning eng ustidagisini (oxirgi kiritilganini) olib, turini tekshiramiz.\n"
        "Agar turi to'g'ri kelsa o'chiramiz, xato bo'lsa yoki stek bo'sh bo'lsa → xato!",
        "Bir qatorda qavslar satri.", "true yoki false.",
        "0 ≤ uzunlik ≤ 10^4",
        examples, hidden, "easy", "Stek", "true")

# B067: Baseball Game (LC#682) — score keeping with stack
def p_b067():
    def solve(inp):
        ops = inp.strip().split()
        st = []
        for o in ops:
            if o == 'C': st.pop()
            elif o == 'D': st.append(2*st[-1])
            elif o == '+': st.append(st[-1]+st[-2])
            else: st.append(int(o))
        return str(sum(st))
    examples = [
        {"input": "5 2 C D +", "output": "30", "explanation": "5,2,C,D,+ → [5,10,15], sum=30"},
        {"input": "5 -2 4 C D 9 + +", "output": "27"},
    ]
    hidden = []
    for _ in range(55):
        ops = []
        st_sim = []
        for _ in range(random.randint(1, 8)):
            choices = ['num']
            if st_sim: choices.extend(['C', 'D'])
            if len(st_sim) >= 2: choices.append('+')
            ch = random.choice(choices)
            if ch == 'num':
                v = random.randint(-10, 10)
                ops.append(str(v)); st_sim.append(v)
            elif ch == 'C':
                ops.append('C'); st_sim.pop()
            elif ch == 'D':
                ops.append('D'); st_sim.append(2*st_sim[-1])
            elif ch == '+':
                ops.append('+'); st_sim.append(st_sim[-1]+st_sim[-2])
        inp = ' '.join(ops)
        hidden.append({"input": inp, "output": solve(inp)})
    add("B067", "Beysbol o'yini (Baseball Game)",
        "Beysbol o'yinida ballarni hisoblash sizga ishonib topshirilgan.\n"
        "Buyruqlar:\n"
        "  • Butun son (x): Yangi ball (x) ni ro'yxatga qo'shadi.\n"
        "  • '+': Oxirgi IKKITA ballni qo'shadi va natijani yangi ball sifatida qo'shadi.\n"
        "  • 'D': Oxirgi ballni IKKI MANGAGA (2x) ko'paytirib, yangi ball sifatida qo'shadi.\n"
        "  • 'C': Oxirgi kiritilgan ball XATO bo'lganini bildiradi va uni ro'yxatdan O'CHIRADI.\n\n"
        "Vazifa: Barcha amallarni bajargach, yig'ilgan barcha ballar summasini toping (buning uchun Stek - oxirgi qo'shilganni o'chirish juda qulay).",
        "Bir qatorda buyruqlar.", "Yakuniy yig'indi.",
        "1 ≤ buyruqlar soni ≤ 1000",
        examples, hidden, "easy", "Stek", "30")

# B068: Make The String Great (LC#1544)
def p_b068():
    def solve(inp):
        s = inp.strip()
        st = []
        for c in s:
            if st and st[-1].swapcase() == c: st.pop()
            else: st.append(c)
        return ''.join(st) if st else " "
    examples = [
        {"input": "leEeetcode", "output": "leetcode"},
        {"input": "abBAcC", "output": " ", "explanation": "Bo'shab qoladi"},
        {"input": "s", "output": "s"},
    ]
    hidden = []
    for _ in range(55):
        s = ''.join(random.choices('aAbBcC', k=random.randint(0, 12)))
        hidden.append({"input": s if s else "a", "output": solve(s if s else "a")})
    add("B068", "Satrni go'zal qilish (Make The String Great)",
        "Yon-yondagi bir xil harf turli registrda bo'lsa (a-A) ikkalasini o'chiring. Hech narsa o'chirib bo'lmaguncha takrorlang.",
        "Bir qatorda satr.", "Tozalangan satr (bo'sh bo'lsa probel).",
        "1 ≤ |s| ≤ 100",
        examples, hidden, "easy", "Stek", "leetcode")

# B069: Crawler Log Folder (LC#1598)
def p_b069():
    def solve(inp):
        ops = inp.strip().split()
        d = 0
        for op in ops:
            if op == '../': d = max(0, d-1)
            elif op == './': pass
            else: d += 1
        return str(d)
    examples = [
        {"input": "d1/ d2/ ../ d21/ ./", "output": "2"},
        {"input": "d1/ d2/ ./ d3/ ../ d31/", "output": "3"},
        {"input": "d1/ ../ ../ ../", "output": "0"},
    ]
    hidden = []
    for _ in range(55):
        ops = []
        d = 0
        for _ in range(random.randint(1, 8)):
            ch = random.choice(['enter', 'enter', 'up', 'stay'])
            if ch == 'enter': ops.append(f"d{random.randint(1,9)}/"); d += 1
            elif ch == 'up': ops.append('../'); d = max(0, d-1)
            else: ops.append('./')
        inp = ' '.join(ops)
        hidden.append({"input": inp, "output": solve(inp)})
    add("B069", "Papkalar log (Crawler Log Folder)",
        "Operatsiyalar: '../' (yuqoriga), './' (joyida), 'xxx/' (papka ichiga). Asosiy papkadan qancha pastda ekanligini ayting.",
        "Bir qatorda operatsiyalar.", "Chuqurlik (0+).",
        "1 ≤ operatsiyalar soni ≤ 100",
        examples, hidden, "easy", "Stek", "2")

# B070: Remove Adjacent Duplicates (LC#1047)
def p_b070():
    def solve(inp):
        s = inp.strip()
        st = []
        for c in s:
            if st and st[-1] == c: st.pop()
            else: st.append(c)
        return ''.join(st) if st else " "
    examples = [
        {"input": "abbaca", "output": "ca"},
        {"input": "azxxzy", "output": "ay"},
    ]
    hidden = []
    samples = ["a", "aa", "abba", "abccba", "abcd"]
    for s in samples:
        hidden.append({"input": s, "output": solve(s)})
    for _ in range(55):
        s = ''.join(random.choices('abcd', k=random.randint(1, 12)))
        hidden.append({"input": s, "output": solve(s)})
    add("B070", "Yon-yondagi dublikatlarni o'chirish",
        "Satrda yon-yondagi bir xil harflar bo'lsa juftlikni o'chiring. Hech narsa o'chirib bo'lmaguncha takrorlang.",
        "Bir qatorda satr.", "Tozalangan satr.",
        "1 ≤ |s| ≤ 10^5",
        examples, hidden, "easy", "Stek", "ca")


# ═══════════════════════════════════════════════════════════════════════════
# OCHKO'ZLIK (Greedy) (10 ta)
# ═══════════════════════════════════════════════════════════════════════════

# B071: Lemonade Change (LC#860)
def p_b071():
    def solve(inp):
        bills = list(map(int, inp.strip().split()))
        five = ten = 0
        for b in bills:
            if b == 5: five += 1
            elif b == 10:
                if five == 0: return "false"
                five -= 1; ten += 1
            else:
                if ten and five: ten -= 1; five -= 1
                elif five >= 3: five -= 3
                else: return "false"
        return "true"
    examples = [
        {"input": "5 5 5 10 20", "output": "true"},
        {"input": "5 5 10 10 20", "output": "false"},
    ]
    hidden = []
    for _ in range(55):
        bills = [random.choice([5,10,20]) for _ in range(random.randint(1, 10))]
        inp = ' '.join(map(str, bills))
        hidden.append({"input": inp, "output": solve(inp)})
    add("B071", "Limonad qaytim (Lemonade Change)",
        "Limonad sotuvchisisiz. Har bir limonad 5$ turadi. Xaridorlar navbat bilan kelib sizga 5$, 10$ yoki 20$ kupyura beradi.\n"
        "Sizda boshida hech qanday mayda pul (qaytim) yo'q. Faqat mijozlar bergan pullardan foydalanib qaytim bera olasiz.\n\n"
        "Barcha xaridorlarga TO'G'RI qaytim bera olsangiz true, aks holda false chiqaring.\n\n"
        "Ochko'zlik (Greedy) yondashuvi:\n"
        "  • 5$ kelsa: Qaytim kerak emas, bitta 5$ ko'paydi.\n"
        "  • 10$ kelsa: Bitta 5$ qaytim beramiz (agar bor bo'lsa), 10$ ko'paydi.\n"
        "  • 20$ kelsa: Qaytimga 15$ berish kerak. Eng zo'r usul: bitta 10$ va bitta 5$ berish (chunki 5$ lar keyinroq ham kerak bo'ladi). "
        "Agar 10$ yo'q bo'lsa, uchta 5$ beramiz.",
        "Bir qatorda kupyuralar.", "true yoki false.",
        "1 ≤ n ≤ 10^5",
        examples, hidden, "easy", "Ochko'zlik", "true")

# B072: Assign Cookies (LC#455)
def p_b072():
    def solve(inp):
        lines = inp.strip().split('\n')
        g = sorted(map(int, lines[0].split()))
        s = sorted(map(int, lines[1].split())) if len(lines) > 1 and lines[1] else []
        i = j = 0
        while i < len(g) and j < len(s):
            if s[j] >= g[i]: i += 1
            j += 1
        return str(i)
    examples = [
        {"input": "1 2 3\n1 1", "output": "1"},
        {"input": "1 2\n1 2 3", "output": "2"},
    ]
    hidden = []
    for _ in range(55):
        g = [random.randint(1, 10) for _ in range(random.randint(1, 6))]
        s = [random.randint(1, 10) for _ in range(random.randint(0, 6))]
        inp = f"{' '.join(map(str,g))}\n{' '.join(map(str,s))}"
        hidden.append({"input": inp, "output": solve(inp)})
    add("B072", "Bolalarga pechene tarqatish (Assign Cookies)",
        "Sizda bir nechta pechene va och qolgan bolalar bor. Har bir bolaning 'ochlik darajasi' (g[i]) bor va har bir pechenening 'hajmi' (s[j]) bor.\n\n"
        "Qoida: Agar s[j] >= g[i] bo'lsa, bu bola shu pechenega to'yadi. Har bir bolaga faqat 1 tagacha pechene berish mumkin.\n"
        "Maksimal nechta bolani to'yg'izish mumkin?\n\n"
        "Ochko'zlik (Greedy) Yechimi:\n"
        "Ikkala massivni ham o'sish tartibida saralang.\n"
        "Eng kichik ochlik darajasiga ega boladan boshlab pechenelarni tekshirib boring. Agar joriy pechene bolani to'yg'izolsa (s[j]>=g[i]), "
        "keyingi bolaga (i+1) o'tamiz. Har qanday holatda ham keyingi pechenega (j+1) o'tamiz.",
        "Birinchi qatorda g, ikkinchida s.", "Maksimal qoniqgan bolalar.",
        "1 ≤ |g|, |s| ≤ 3·10^4",
        examples, hidden, "easy", "Ochko'zlik", "1")

# B073: Can Place Flowers (LC#605)
def p_b073():
    def solve(inp):
        lines = inp.strip().split('\n')
        bed = list(map(int, lines[0].split()))
        n = int(lines[1])
        bed = [0] + bed + [0]
        cnt = 0
        i = 1
        while i < len(bed)-1:
            if bed[i] == 0 and bed[i-1] == 0 and bed[i+1] == 0:
                bed[i] = 1; cnt += 1
            i += 1
        return "true" if cnt >= n else "false"
    examples = [
        {"input": "1 0 0 0 1\n1", "output": "true"},
        {"input": "1 0 0 0 1\n2", "output": "false"},
    ]
    hidden = []
    for _ in range(55):
        m = random.randint(1, 10)
        bed = [random.randint(0, 1) for _ in range(m)]
        # ensure no adjacent 1s
        for i in range(1, m):
            if bed[i] == 1 and bed[i-1] == 1: bed[i] = 0
        n = random.randint(0, 5)
        inp = f"{' '.join(map(str,bed))}\n{n}"
        hidden.append({"input": inp, "output": solve(inp)})
    add("B073", "Gul ekish (Can Place Flowers)",
        "Uzoq gulzorda gullar ekilgan (1) yoki bo'sh (0). Qoida: Ikkita gul hech qachon yonma-yon ekilishi mumkin emas.\n\n"
        "Sizga yana n ta gul ekish vazifasi berilgan. Qoidani buzmagan holda shu gullarni ekib bo'ladimi?\n\n"
        "Ochko'zlik (Greedy) Yechimi:\n"
        "Gulzor bo'ylab chapdan o'ngga yuramiz. Agar joriy joy (i) bo'sh bo'lsa (0) va uning CHAP tomoni ham bo'sh (yoki chegara), va O'NG tomoni ham bo'sh (yoki chegara) bo'lsa:\n"
        "O'sha joyga gul ekamiz (0 ni 1 ga aylantiramiz) va n ni 1 taga kamaytiramiz.\n"
        "Oxirida n <= 0 bo'lsa, demak ekib bo'ladi (true).",
        "Birinchi qatorda gulzor, ikkinchida n.", "true yoki false.",
        "1 ≤ |bed| ≤ 10^4",
        examples, hidden, "easy", "Ochko'zlik", "true")

# B074: Minimum Operations to Equal Array Elements (LC#1551, simplified)
def p_b074():
    def solve(inp):
        n = int(inp.strip())
        # arr[i] = 2*i+1, target = n. cost = sum |arr[i] - n| / 2
        if n % 2 == 1:
            return str(((n-1)//2) ** 2 + ((n-1)//2))
        return str((n//2) ** 2)
    # Simplified — just compute brute force for testing
    def solve(inp):
        n = int(inp.strip())
        arr = [2*i+1 for i in range(n)]
        target = sum(arr) // n
        return str(sum(abs(x - target) for x in arr) // 2)
    examples = [
        {"input": "3", "output": "2", "explanation": "[1,3,5] → [3,3,3]: 2 amal"},
        {"input": "6", "output": "9"},
    ]
    hidden = []
    for n in [1, 2, 3, 4, 5, 6, 10, 50, 100, 500, 1000]:
        hidden.append({"input": str(n), "output": solve(str(n))})
    for _ in range(50):
        n = random.randint(1, 5000)
        hidden.append({"input": str(n), "output": solve(str(n))})
    add("B074", "Massiv elementlarini tenglashtirish",
        "n berilgan. Massiv quyidagi formula bo'yicha tuziladi (i=0..n-1):  arr[i] = 2·i + 1.\n"
        "  Misol: n=3 →  arr = [1, 3, 5]    (chunki 2·0+1, 2·1+1, 2·2+1)\n"
        "  Misol: n=6 →  arr = [1, 3, 5, 7, 9, 11]\n\n"
        "AMAL: bir qadamda IXTIYORIY ikkita indeks tanlanadi — biri +1 oshadi, ikkinchisi -1 kamayadi (yig'indi saqlanadi).\n\n"
        "Vazifa: BARCHA elementlarni teng qilish uchun MINIMAL qadamlar sonini chiqaring.\n"
        "  n=3 → [1,3,5] → maqsad [3,3,3]: 1 ni 3 ga ko'tarish uchun 2 qadam (1↔5: 5→4, 1→2; keyin 4→3, 2→3) → 2 qadam.\n\n"
        "Sezgi: o'rta qiymat doim arr ning o'rta sonidir. Chap yarmni o'rta songa ko'tarish uchun zarur \"+1 amallar\" yig'indisi javob bo'ladi (yoki teng formula).",
        "Bir musbat butun son n.", "Minimal qadamlar.",
        "1 ≤ n ≤ 10^4",
        examples, hidden, "easy", "Ochko'zlik", "2")

# B075: Maximum Units on a Truck (LC#1710)
def p_b075():
    def solve(inp):
        lines = inp.strip().split('\n')
        boxes = []
        for ln in lines[:-1]:
            parts = ln.split()
            boxes.append((int(parts[0]), int(parts[1])))
        truck = int(lines[-1])
        boxes.sort(key=lambda x: -x[1])
        total = 0
        for n, u in boxes:
            t = min(n, truck)
            total += t * u
            truck -= t
            if truck == 0: break
        return str(total)
    examples = [
        {"input": "1 3\n2 2\n3 1\n4", "output": "8", "explanation": "1*3 + 2*2 + 1*1 = 8"},
    ]
    hidden = []
    for _ in range(55):
        n = random.randint(1, 5)
        boxes = []
        for _ in range(n):
            boxes.append((random.randint(1, 5), random.randint(1, 10)))
        truck = random.randint(1, 15)
        inp = '\n'.join(f"{a} {b}" for a, b in boxes) + f"\n{truck}"
        hidden.append({"input": inp, "output": solve(inp)})
    add("B075", "Yuk mashinasiga maksimal dona (Maximum Units on a Truck)",
        "Har qutida {dona soni, dona birligi}. Yuk mashina maksimal X qutini qabul qiladi. Maksimal birliklar yig'indisi.",
        "Har qator: dona_soni dona_birligi. Oxirgi qatorda truck_size.", "Maksimal birliklar.",
        "1 ≤ qutilar soni ≤ 1000",
        examples, hidden, "easy", "Ochko'zlik", "8")

# B076: Last Stone Weight (LC#1046)
def p_b076():
    def solve(inp):
        import heapq
        stones = [-x for x in map(int, inp.strip().split())]
        heapq.heapify(stones)
        while len(stones) > 1:
            a = -heapq.heappop(stones)
            b = -heapq.heappop(stones)
            if a != b:
                heapq.heappush(stones, -(a-b))
        return str(-stones[0]) if stones else "0"
    examples = [
        {"input": "2 7 4 1 8 1", "output": "1"},
        {"input": "1", "output": "1"},
    ]
    hidden = []
    for _ in range(55):
        n = random.randint(1, 12)
        stones = [random.randint(1, 30) for _ in range(n)]
        inp = ' '.join(map(str, stones))
        hidden.append({"input": inp, "output": solve(inp)})
    add("B076", "Oxirgi tosh og'irligi (Last Stone Weight)",
        "Sizda har xil og'irlikdagi toshlar bor. Har qadamda eng OG'IR ikkita toshni olasiz va ularni bir-biriga urasiz:\n"
        "  • Agar x == y bo'lsa, ikkala tosh ham parchalanib yo'q bo'ladi.\n"
        "  • Agar x != y bo'lsa (y og'irroq), x yo'qoladi, y ning og'irligi y - x bo'lib qoladi.\n\n"
        "Bu jarayon bitta tosh qolgunicha (yoki umuman qolmaguncha) davom etadi. Oxirida qolgan toshning og'irligini toping (hech nima qolmasa 0).\n\n"
        "Optimal Yechim (Max-Heap / Priority Queue):\n"
        "Toshlarni Max-Heap ma'lumotlar tuzilmasiga saqlash (Python da heapq - manfiy qilib saqlash orqali). "
        "Bu har safar eng katta 2 ta toshni tezda (O(logN)) topish va yangisini qo'shish imkonini beradi.",
        "Bir qatorda toshlar.", "Oxirgi tosh og'irligi (0 yoki +).",
        "1 ≤ n ≤ 30, 1 ≤ tosh ≤ 1000",
        examples, hidden, "easy", "Ochko'zlik", "1")

# B077: Maximum 69 Number (LC#1323)
def p_b077():
    def solve(inp):
        s = inp.strip()
        return str(int(s.replace('6', '9', 1)))
    examples = [
        {"input": "9669", "output": "9969"},
        {"input": "9996", "output": "9999"},
        {"input": "9999", "output": "9999"},
    ]
    hidden = []
    for _ in range(55):
        s = ''.join(random.choices('69', k=random.randint(1, 4)))
        hidden.append({"input": s, "output": solve(s)})
    add("B077", "Maksimal 69 son (Maximum 69 Number)",
        "Faqat 6 va 9 dan iborat son berilgan. Eng ko'pi 1 ta 6 ni 9 ga (yoki 9 ni 6 ga) almashtirib eng katta sonni hosil qiling.",
        "Bir butun son.", "Maksimal son.",
        "1 ≤ uzunlik ≤ 4",
        examples, hidden, "easy", "Ochko'zlik", "9969")

# B078: Robot Return to Origin (LC#657)
def p_b078():
    def solve(inp):
        s = inp.strip()
        x = y = 0
        for c in s:
            if c == 'U': y += 1
            elif c == 'D': y -= 1
            elif c == 'L': x -= 1
            elif c == 'R': x += 1
        return "true" if x == 0 and y == 0 else "false"
    examples = [
        {"input": "UD", "output": "true"},
        {"input": "LL", "output": "false"},
        {"input": "RRDD", "output": "false"},
    ]
    hidden = []
    samples = ["", "UDLR", "UUDDLLRR", "U", "UUDD", "RLRLR"]
    for s in samples:
        if s == "": s = "U"
        hidden.append({"input": s, "output": solve(s)})
    for _ in range(55):
        s = ''.join(random.choices('UDLR', k=random.randint(1, 12)))
        hidden.append({"input": s, "output": solve(s)})
    add("B078", "Robotning boshlang'ich joyga qaytishi (Robot Return to Origin)",
        "Robot UDLR komandalarini ijro etadi. Yakunda boshlang'ich nuqtaga qaytsa true.",
        "Bir qatorda komanda satri.", "true yoki false.",
        "1 ≤ |s| ≤ 10^4",
        examples, hidden, "easy", "Ochko'zlik", "true")

# B079: Greatest Common Divisor of Strings (LC#1071)
def p_b079():
    def solve(inp):
        s, t = inp.strip().split('\n')
        if s + t != t + s: return " "  # no GCD
        from math import gcd
        return s[:gcd(len(s), len(t))]
    examples = [
        {"input": "ABCABC\nABC", "output": "ABC"},
        {"input": "ABABAB\nABAB", "output": "AB"},
        {"input": "LEET\nCODE", "output": " ", "explanation": "Umumiy bo'luvchi yo'q"},
    ]
    hidden = []
    samples = [("ABCDEF", "ABC"), ("ABAB", "ABABABAB"), ("ABCABC", "ABCABCABCABC"), ("AAA", "AA")]
    for s, t in samples:
        inp = f"{s}\n{t}"
        hidden.append({"input": inp, "output": solve(inp)})
    for _ in range(55):
        base = ''.join(random.choices('ABC', k=random.randint(1, 3)))
        s = base * random.randint(1, 4)
        t = base * random.randint(1, 4)
        if random.random() < 0.3:
            t = t + random.choice('XY')
        inp = f"{s}\n{t}"
        hidden.append({"input": inp, "output": solve(inp)})
    add("B079", "Satrlarning EKUB (GCD of Strings)",
        "EKUB (Eng Katta Umumiy Bo'luvchi, ingl. GCD) — ikki sonni qoldiqsiz bo'ladigan eng katta son. Misol: gcd(12,18)=6.\n\n"
        "Bu masalada g'oyani SATRLARGA ko'chirilgan. Satr g — ikkala satr (s va t) ning \"bo'luvchisi\" hisoblanadi, agar:\n"
        "  s = g + g + ... + g  (k1 marta takrorlangan g),\n"
        "  t = g + g + ... + g  (k2 marta takrorlangan g).\n\n"
        "Vazifa: Eng UZUN bunday g satrni topish.\n\n"
        "Misollar:\n"
        "  s='ABCABC', t='ABC'  → g='ABC'  (s = ABC·2, t = ABC·1)\n"
        "  s='ABABAB', t='ABAB' → g='AB'   (s = AB·3, t = AB·2)\n"
        "  s='LEET', t='CODE'   → bo'luvchi yo'q → ' ' (probel)\n\n"
        "TRICK: Bunday g mavjud bo'lishi uchun s+t == t+s shart. Mavjud bo'lsa, g uzunligi = gcd(|s|, |t|), va g = s ning shu uzunlikdagi prefiksi.",
        "Birinchi qatorda s, ikkinchida t.", "EKUB satr yoki probel.",
        "1 ≤ uzunliklar ≤ 1000",
        examples, hidden, "easy", "Ochko'zlik", "ABC")

# B080: Find the Highest Altitude (LC#1732)
def p_b080():
    def solve(inp):
        gain = list(map(int, inp.strip().split()))
        cur = best = 0
        for g in gain:
            cur += g
            best = max(best, cur)
        return str(best)
    examples = [
        {"input": "-5 1 5 0 -7", "output": "1"},
        {"input": "-4 -3 -2 -1 4 3 2", "output": "0"},
    ]
    hidden = []
    for _ in range(55):
        n = random.randint(1, 12)
        gains = [random.randint(-10, 10) for _ in range(n)]
        inp = ' '.join(map(str, gains))
        hidden.append({"input": inp, "output": solve(inp)})
    add("B080", "Eng yuqori balandlik (Find the Highest Altitude)",
        "Velosipedchi dengiz sathidan (0 balandlikdan) sayohatni boshladi. Sizga u o'tgan har bir nuqtalar orasidagi BALANDLIK O'ZGARISHI (gain) massivi berilgan.\n"
        "Masalan: gain = [-5, 1, 5, 0, -7]\n"
        "0-nuqta: 0\n"
        "1-nuqta: 0 + (-5) = -5\n"
        "2-nuqta: -5 + 1 = -4\n"
        "3-nuqta: -4 + 5 = 1\n"
        "4-nuqta: 1 + 0 = 1\n"
        "5-nuqta: 1 + (-7) = -6\n\n"
        "Bu balandliklar ichida eng kattasi 1. Demak sayohatdagi eng yuqori balandlik 1 ga teng.\n"
        "Yechim: Prefiks yig'indisi (Prefix sum) orqali yig'ib borib, eng kattasini eslab qolish kifoya.",
        "Bir qatorda gain massivi.", "Eng yuqori balandlik.",
        "1 ≤ n ≤ 100",
        examples, hidden, "easy", "Massivlar", "1")


# ═══════════════════════════════════════════════════════════════════════════
# QO'SHIMCHA (20 ta) — Mantiq, DP, Algoritm
# ═══════════════════════════════════════════════════════════════════════════

# B081: Fizz Buzz (LC#412)
def p_b081():
    def solve(inp):
        n = int(inp.strip())
        out = []
        for i in range(1, n+1):
            if i % 15 == 0: out.append("FizzBuzz")
            elif i % 3 == 0: out.append("Fizz")
            elif i % 5 == 0: out.append("Buzz")
            else: out.append(str(i))
        return ' '.join(out)
    examples = [
        {"input": "5", "output": "1 2 Fizz 4 Buzz"},
        {"input": "15", "output": "1 2 Fizz 4 Buzz Fizz 7 8 Fizz Buzz 11 Fizz 13 14 FizzBuzz"},
    ]
    hidden = []
    for n in [1, 3, 5, 7, 10, 15, 20, 30, 50]:
        hidden.append({"input": str(n), "output": solve(str(n))})
    for _ in range(50):
        n = random.randint(1, 200)
        hidden.append({"input": str(n), "output": solve(str(n))})
    add("B081", "FizzBuzz",
        "1 dan n gacha: 3 ga bo'linsa Fizz, 5 ga bo'linsa Buzz, 15 ga bo'linsa FizzBuzz, aks holda son.",
        "Bir musbat son n.", "1..n natijalar (probel bilan).",
        "1 ≤ n ≤ 10^4",
        examples, hidden, "easy", "Mantiq", "1 2 Fizz 4 Buzz")

# B082: House Robber (LC#198)
def p_b082():
    def solve(inp):
        nums = list(map(int, inp.strip().split()))
        prev = curr = 0
        for x in nums:
            prev, curr = curr, max(curr, prev + x)
        return str(curr)
    examples = [
        {"input": "1 2 3 1", "output": "4"},
        {"input": "2 7 9 3 1", "output": "12"},
    ]
    hidden = []
    for _ in range(55):
        n = random.randint(1, 12)
        nums = [random.randint(0, 30) for _ in range(n)]
        inp = ' '.join(map(str, nums))
        hidden.append({"input": inp, "output": solve(inp)})
    add("B082", "Uy o'g'risi (House Robber)",
        "Siz professional o'g'risiz va ko'chadagi uylarni tunamoqchisiz. Har bir uyda ma'lum miqdorda pul bor.\n"
        "LEKIN xavfsizlik tizimi shundayki: YONMA-YON joylashgan ikkita uyga tushsangiz, signalizatsiya ishlab ketadi!\n\n"
        "Vazifa: Signalizatsiyani ishga tushirmasdan eng ko'p qancha pul o'g'irlash mumkinligini toping.\n\n"
        "Dinamik dasturlash (Dynamic Programming) yechimi:\n"
        "i-chi uyga kelganda ikkita tanlov bor:\n"
        "  1) Bu uyni o'g'irlash: unda i-1 uyni tashlash kerak, ya'ni i-2 gacha bo'lgan foyda + i-uyning puli.\n"
        "  2) Bu uyni tashlab ketish: unda i-1 gacha bo'lgan foydani o'zini olish.\n"
        "Formula: dp[i] = max(dp[i-1], dp[i-2] + nums[i])\n"
        "Buni faqat oxirgi 2 ta holatni (prev va curr) xotirada saqlab O(1) xotira bilan ishlash ham mumkin.",
        "Bir qatorda uylardagi pul.", "Maksimal pul.",
        "1 ≤ n ≤ 100",
        examples, hidden, "easy", "Dinamik dasturlash", "4")

# B083: Min Cost Climbing Stairs (LC#746)
def p_b083():
    def solve(inp):
        cost = list(map(int, inp.strip().split()))
        n = len(cost)
        a = b = 0
        for i in range(n-1, -1, -1):
            cur = cost[i] + min(a, b)
            b = a; a = cur
        return str(min(a, b))
    examples = [
        {"input": "10 15 20", "output": "15"},
        {"input": "1 100 1 1 1 100 1 1 100 1", "output": "6"},
    ]
    hidden = []
    for _ in range(55):
        n = random.randint(2, 12)
        cost = [random.randint(0, 50) for _ in range(n)]
        inp = ' '.join(map(str, cost))
        hidden.append({"input": inp, "output": solve(inp)})
    add("B083", "Zinapoyaning minimal narxi (Min Cost Climbing Stairs)",
        "Siz zinapoya oldidasiz. Har bir pog'onaga qadam qo'yishning o'ziga xos 'narxi' (cost massivi) bor.\n"
        "Siz 0- yoki 1-pog'onadan boshlashingiz mumkin. Har safar 1 ta yoki 2 ta pog'ona yuqoriga sakrashingiz mumkin.\n"
        "Vazifa: Eng yuqoriga (massiv oxiridan tashqariga) chiqish uchun to'lanadigan MINIMAL narxni toping.\n\n"
        "Dinamik Dasturlash (DP) Yechimi:\n"
        "i-chi pog'onaga chiqishning minimal narxi: cost[i] + min(i-1 dan kelish narxi, i-2 dan kelish narxi).\n"
        "Buni orqadan oldinga (tepadan pastga) hisoblasa ham bo'ladi: a va b o'zgaruvchilar yordamida O(1) xotira bilan ishlasa bo'ladi.",
        "Bir qatorda cost massivi.", "Minimal narx.",
        "2 ≤ n ≤ 1000",
        examples, hidden, "easy", "Dinamik dasturlash", "15")

# B084: Fibonacci (LC#509)
def p_b084():
    def solve(inp):
        n = int(inp.strip())
        a, b = 0, 1
        for _ in range(n): a, b = b, a+b
        return str(a)
    examples = [
        {"input": "2", "output": "1"},
        {"input": "3", "output": "2"},
        {"input": "4", "output": "3"},
    ]
    hidden = []
    for n in range(0, 56):
        hidden.append({"input": str(n), "output": solve(str(n))})
    add("B084", "Fibonachchi soni (Fibonacci Number)",
        "FIBONACHCHI ketma-ketligi — har keyingi son OLDINGI IKKI sonning yig'indisiga teng:\n"
        "  F(0) = 0\n"
        "  F(1) = 1\n"
        "  F(n) = F(n-1) + F(n-2)   (n ≥ 2 uchun)\n\n"
        "Birinchi a'zolar: 0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, ...\n\n"
        "Vazifa: berilgan n uchun F(n) ni topish. Misol: F(4) = F(3)+F(2) = 2+1 = 3.\n\n"
        "Yondashuv: oddiy iteratsiya — ikki o'zgaruvchi (a, b) bilan n marta yangilash. Rekursiya ham mumkin, lekin sekin.",
        "Bir manfiy bo'lmagan son n.", "F(n).",
        "0 ≤ n ≤ 30",
        examples, hidden, "easy", "Dinamik dasturlash", "1")

# B085: Pascal's Triangle Row (LC#119)
def p_b085():
    def solve(inp):
        n = int(inp.strip())
        row = [1]
        for i in range(n):
            row = [a + b for a, b in zip([0] + row, row + [0])]
        return ' '.join(map(str, row))
    examples = [
        {"input": "0", "output": "1"},
        {"input": "3", "output": "1 3 3 1"},
        {"input": "4", "output": "1 4 6 4 1"},
    ]
    hidden = []
    for n in range(0, 56):
        hidden.append({"input": str(n), "output": solve(str(n))})
    add("B085", "Paskal uchburchagi qatori (Pascal's Triangle Row)",
        "PASKAL UCHBURCHAGI — uchburchak shaklidagi sonlar jadvali. Qoidalari:\n"
        "  • har qatorning chetlari — 1\n"
        "  • har bir ichki son = uning ustidagi IKKI qo'shni sonning yig'indisi\n\n"
        "Dastlabki qatorlar (0-indeksli):\n"
        "  Qator 0:        1\n"
        "  Qator 1:       1 1\n"
        "  Qator 2:      1 2 1\n"
        "  Qator 3:     1 3 3 1       (3 = 1+2, yana 3 = 2+1)\n"
        "  Qator 4:    1 4 6 4 1      (4=1+3, 6=3+3, 4=3+1)\n"
        "  Qator 5:   1 5 10 10 5 1\n\n"
        "Vazifa: berilgan n uchun n-qatorni chiqaring (kombinatorikadagi C(n,k) qiymatlari).\n"
        "Yondashuv: 0-qatorni [1] dan boshlab, ketma-ket qatorlarni qurib boring (har keyingi qator — oldingisidan qo'shni juftliklarni qo'shib hosil bo'ladi).",
        "Bir manfiy bo'lmagan son n.", "n-qator (probel bilan).",
        "0 ≤ n ≤ 33",
        examples, hidden, "easy", "Dinamik dasturlash", "1")

# B086: Self Dividing Numbers (LC#728)
def p_b086():
    def solve(inp):
        l, r = map(int, inp.strip().split())
        out = []
        for n in range(l, r+1):
            d = str(n)
            if '0' not in d and all(n % int(c) == 0 for c in d):
                out.append(str(n))
        return ' '.join(out)
    examples = [
        {"input": "1 22", "output": "1 2 3 4 5 6 7 8 9 11 12 15 22"},
    ]
    hidden = []
    for _ in range(55):
        a = random.randint(1, 100)
        b = random.randint(a, a+50)
        inp = f"{a} {b}"
        hidden.append({"input": inp, "output": solve(inp)})
    add("B086", "O'z-o'ziga bo'linadigan sonlar (Self Dividing Numbers)",
        "[l,r] oraliqdagi har bir raqami bilan bo'linadigan sonlarni topib chiqaring (raqamlar 0 dan farqli bo'lsin).",
        "Ikki son l r (probel bilan).", "Sonlar (probel bilan).",
        "1 ≤ l ≤ r ≤ 10^4",
        examples, hidden, "easy", "Mantiq", "1 2 3 4 5 6 7 8 9 11 12 15 22")

# B087: Number Complement (LC#476)
def p_b087():
    def solve(inp):
        n = int(inp.strip())
        m = (1 << n.bit_length()) - 1
        return str(n ^ m)
    examples = [
        {"input": "5", "output": "2", "explanation": "101 → 010"},
        {"input": "1", "output": "0"},
    ]
    hidden = []
    for n in [1, 2, 3, 5, 7, 8, 15, 16, 31, 100, 1000, 10**9]:
        hidden.append({"input": str(n), "output": solve(str(n))})
    for _ in range(50):
        n = random.randint(1, 10**9)
        hidden.append({"input": str(n), "output": solve(str(n))})
    add("B087", "Sonning to'ldiruvchisi (Number Complement)",
        "Sonni IKKILIK (binary) ko'rinishda yozing va har bitni teskari almashtiring (0↔1). Boshlang'ich nollar HISOBGA OLINMAYDI — faqat haqiqiy bitlar.\n\n"
        "Misol: n = 5\n"
        "  5 = 101₂   →   (har bitni invert)   →   010₂ = 2\n"
        "  Demak javob 2.\n\n"
        "Yana misollar:\n"
        "  n=7  → 111   → 000 = 0\n"
        "  n=8  → 1000  → 0111 = 7\n"
        "  n=10 → 1010  → 0101 = 5\n\n"
        "Bit hiyla: m = (1 << uzunlik) - 1  (hammasi 1 bo'lgan maska),  javob = n XOR m.",
        "Bir musbat butun son.", "To'ldiruvchi son.",
        "1 ≤ n < 2^31",
        examples, hidden, "easy", "Bit amallari", "2")

# B088: Binary Number with Alternating Bits (LC#693)
def p_b088():
    def solve(inp):
        n = int(inp.strip())
        b = bin(n)[2:]
        return "true" if all(b[i] != b[i-1] for i in range(1, len(b))) else "false"
    examples = [
        {"input": "5", "output": "true", "explanation": "5 = 101"},
        {"input": "7", "output": "false", "explanation": "7 = 111"},
        {"input": "11", "output": "false"},
    ]
    hidden = []
    for n in [1, 2, 3, 5, 7, 10, 11, 21, 42, 85, 170, 1000]:
        hidden.append({"input": str(n), "output": solve(str(n))})
    for _ in range(50):
        n = random.randint(1, 10**6)
        hidden.append({"input": str(n), "output": solve(str(n))})
    add("B088", "Almashinuvchi bitlar (Alternating Bits)",
        "Berilgan sonning ikkilik sanoq sistemasidagi ko'rinishida 0 va 1 lar doimo galma-gal kelishini tekshiring (yonma-yon ikkita 0 yoki ikkita 1 kelmasin).\n\n"
        "Masalan:\n"
        "  • 5 = 101 (true)\n"
        "  • 7 = 111 (false, uchta 1 yonma-yon)\n"
        "  • 11 = 1011 (false)\n\n"
        "Bit amallari bilan hiyla:\n"
        "Agar n almashtiruvchi bitlardan iborat bo'lsa (1010), uni o'ngga 1 bit sursak (n >> 1 = 0101) va ular XOR (^) qilinsa:\n"
        "1010 ^ 0101 = 1111 (faqat 1 lardan iborat son chiqadi).\n"
        "Bunday sonni x&(x+1) qilsangiz doim 0 chiqadi!",
        "Bir musbat son.", "true yoki false.",
        "1 ≤ n ≤ 2^31-1",
        examples, hidden, "easy", "Bit amallari", "true")

# B089: Power of Four (LC#342)
def p_b089():
    def solve(inp):
        n = int(inp.strip())
        return "true" if n > 0 and (n & (n-1)) == 0 and (n & 0x55555555) != 0 else "false"
    examples = [
        {"input": "16", "output": "true"},
        {"input": "5", "output": "false"},
        {"input": "1", "output": "true"},
    ]
    hidden = []
    samples = [0, 1, 2, 4, 8, 16, 32, 64, 256, 1024, 4096, 1<<30, -1, 5]
    for n in samples:
        hidden.append({"input": str(n), "output": solve(str(n))})
    for _ in range(50):
        if random.random() < 0.3:
            n = 4 ** random.randint(0, 15)
        else:
            n = random.randint(-100, 10**6)
        hidden.append({"input": str(n), "output": solve(str(n))})
    add("B089", "To'rtning darajasi (Power of Four)",
        "Berilgan n soni 4 ning butun darajasiga (4^x) tengmi yoki yo'qmi, shuni tekshiring.\n"
        "Qator: 1, 4, 16, 64, 256...\n\n"
        "Bit amallari (Bitwise) bilan hiyla yechim:\n"
        "  1) Avval son 2 ning darajasi ekanligiga ishonch hosil qilamiz: n > 0 va (n & (n-1)) == 0\n"
        "  2) Agar u 2 ning darajasi bo'lsa, u qachon 4 ning darajasi bo'ladi? Faqat uning yagona '1' biti TOQ pozitsiyada turganda! (Masalan 1 = 1, 4 = 100, 16 = 10000)\n"
        "Buni tekshirish uchun uni maska (0x55555555, ya'ni ...01010101) bilan AND qilamiz. Agar n & 0x55555555 != 0 bo'lsa, u 4 ning darajasi hisoblanadi.",
        "Bir butun son.", "true yoki false.",
        "-2^31 ≤ n ≤ 2^31-1",
        examples, hidden, "easy", "Bit amallari", "true")

# B090: Largest Number At Least Twice of Others (LC#747)
def p_b090():
    def solve(inp):
        nums = list(map(int, inp.strip().split()))
        m = max(nums)
        idx = nums.index(m)
        ok = all(m >= 2*x for x in nums if x != m)
        return str(idx) if ok else "-1"
    examples = [
        {"input": "3 6 1 0", "output": "1"},
        {"input": "1 2 3 4", "output": "-1"},
    ]
    hidden = []
    for _ in range(55):
        n = random.randint(2, 8)
        nums = [random.randint(0, 20) for _ in range(n)]
        inp = ' '.join(map(str, nums))
        hidden.append({"input": inp, "output": solve(inp)})
    add("B090", "Boshqalardan kamida 2 marta katta (Largest 2x Others)",
        "Massivdagi eng katta son qolgan barchasidan kamida 2 marta katta bo'lsa, uning indeksini chiqaring. Aks holda -1.",
        "Bir qatorda massiv.", "Indeks yoki -1.",
        "2 ≤ n ≤ 50",
        examples, hidden, "easy", "Massivlar", "1")

# B091: Distribute Candies (LC#575)
def p_b091():
    def solve(inp):
        nums = inp.strip().split()
        return str(min(len(set(nums)), len(nums)//2))
    examples = [
        {"input": "1 1 2 2 3 3", "output": "3"},
        {"input": "1 1 2 3", "output": "2"},
    ]
    hidden = []
    for _ in range(55):
        n = random.randint(2, 14)
        if n % 2: n += 1
        nums = [random.randint(1, 5) for _ in range(n)]
        inp = ' '.join(map(str, nums))
        hidden.append({"input": inp, "output": solve(inp)})
    add("B091", "Konfetni teng ulashish (Distribute Candies)",
        "Singlim juft soni n ta konfetning yarmini oladi. Maksimal qancha turli xil konfetni ololadi?",
        "Bir qatorda n ta konfet turi (n juft).", "Maksimal turli konfet.",
        "2 ≤ n ≤ 10^4, n juft",
        examples, hidden, "easy", "Hash", "3")

# B092: Find Smallest Letter Greater Than Target (LC#744)
def p_b092():
    def solve(inp):
        lines = inp.strip().split('\n')
        letters = lines[0].split()
        t = lines[1]
        for c in letters:
            if c > t: return c
        return letters[0]
    examples = [
        {"input": "c f j\na", "output": "c"},
        {"input": "c f j\nc", "output": "f"},
        {"input": "c f j\nj", "output": "c"},
    ]
    hidden = []
    for _ in range(55):
        letters = sorted(random.sample('abcdefghij', random.randint(2, 8)))
        t = random.choice('abcdefghijk')
        inp = f"{' '.join(letters)}\n{t}"
        hidden.append({"input": inp, "output": solve(inp)})
    add("B092", "Maqsaddan katta eng kichik harf (Find Smallest Letter Greater Than Target)",
        "Sizga o'sish tartibida saralangan harflar massivi va bitta 'target' harfi berilgan.\n"
        "Massiv ichidan alfabet bo'yicha 'target' dan KATTAROQ bo'lgan eng kichik harfni toping.\n\n"
        "Eslatma (Aylanma xususiyat - Wrap around):\n"
        "Agar massivda 'target' dan katta harf umuman topilmasa, massivning ENG BIRINCHI harfini qaytarishingiz kerak.\n\n"
        "Misol: letters = ['c', 'f', 'j']\n"
        "  • target = 'a' → 'c' ('a' dan katta eng kichik)\n"
        "  • target = 'c' → 'f' ('c' bilan teng bo'lishi yetarli emas, KATTA bo'lishi shart!)\n"
        "  • target = 'j' → 'c' (j dan kattasi yo'q, shuning uchun aylanib birinchisiga qaytadi).",
        "Birinchi qatorda harflar (probel bilan), ikkinchida target.", "Topilgan harf.",
        "2 ≤ |letters| ≤ 10^4",
        examples, hidden, "easy", "Algoritmlar", "c")

# B093: Largest Triangle Area (LC#812)
def p_b093():
    def solve(inp):
        pts = []
        for line in inp.strip().split('\n'):
            x, y = map(int, line.split())
            pts.append((x, y))
        best = 0.0
        for i in range(len(pts)):
            for j in range(i+1, len(pts)):
                for k in range(j+1, len(pts)):
                    x1,y1 = pts[i]; x2,y2 = pts[j]; x3,y3 = pts[k]
                    area = abs(x1*(y2-y3) + x2*(y3-y1) + x3*(y1-y2)) / 2.0
                    best = max(best, area)
        return f"{best:.5f}"
    examples = [
        {"input": "0 0\n0 1\n1 0\n0 2\n2 0", "output": "2.00000"},
    ]
    hidden = []
    for _ in range(55):
        n = random.randint(3, 6)
        pts = []
        seen = set()
        while len(pts) < n:
            x, y = random.randint(0, 10), random.randint(0, 10)
            if (x,y) not in seen:
                seen.add((x,y)); pts.append((x,y))
        inp = '\n'.join(f"{x} {y}" for x, y in pts)
        hidden.append({"input": inp, "output": solve(inp)})
    add("B093", "Eng katta uchburchak yuzi (Largest Triangle Area)",
        "Tekislikda bir nechta nuqtalar berilgan (har bir nuqta x va y koordinatalar bilan). Uchburchak hosil qilish uchun BARCHA mumkin bo'lgan 3 ta nuqtalar to'plamini ko'rib chiqing va eng katta yuzli uchburchakni topib, uning yuzini chiqaring.\n\n"
        "UCHBURCHAK YUZI FORMULASI (koordinatalar bo'yicha — Shoelace / yo'nalishli yuz):\n"
        "  Yuz = | x1·(y2-y3) + x2·(y3-y1) + x3·(y1-y2) | / 2\n"
        "(modul belgisi — manfiy bo'lmaydigan qiymat olish uchun).\n\n"
        "Misol: nuqtalar (0,0), (0,2), (2,0) → Yuz = |0·(2-0) + 0·(0-0) + 2·(0-2)| / 2 = |0+0-4|/2 = 2.\n\n"
        "Yondashuv: 3 ta uyali tsikl (i<j<k), har triplet uchun yuzni hisoblab maksimumini saqlash. n≤50 uchun bu juda tez (50³ ≈ 125 ming amal).\n"
        "Natijani 5 kasr aniqlikda chiqaring (mas: '2.00000').",
        "Har qatorda x y koordinatalari.", "Yuz (5 kasr).",
        "3 ≤ |points| ≤ 50",
        examples, hidden, "easy", "Algoritmlar", "2.00000")

# B094: Range Sum Query — Immutable (LC#303) — simplified
def p_b094():
    def solve(inp):
        lines = inp.strip().split('\n')
        nums = list(map(int, lines[0].split()))
        l, r = map(int, lines[1].split())
        return str(sum(nums[l:r+1]))
    examples = [
        {"input": "-2 0 3 -5 2 -1\n0 2", "output": "1"},
        {"input": "-2 0 3 -5 2 -1\n2 5", "output": "-1"},
    ]
    hidden = []
    for _ in range(55):
        n = random.randint(2, 12)
        nums = [random.randint(-10, 10) for _ in range(n)]
        l = random.randint(0, n-1)
        r = random.randint(l, n-1)
        inp = f"{' '.join(map(str,nums))}\n{l} {r}"
        hidden.append({"input": inp, "output": solve(inp)})
    add("B094", "Diapazon yig'indisi (Range Sum Query)",
        "Sizga sonlar massivi va l, r indekslari beriladi.\n"
        "Massivdagi [l, r] oraliqda yotuvchi barcha elementlar yig'indisini hisoblab chiqaring (ikkala chegara ham kiradi).\n\n"
        "Prefiks Yig'indisi (Prefix Sum) usuli haqida tushuncha:\n"
        "Aslida, agar ko'p marta so'rov berilsa, [l, r] oraliqni har safar qo'shib chiqish o'rniga prefix sum qilingan massiv ishlatiladi:\n"
        "  prefix[i] = nums[0] + ... + nums[i-1]\n"
        "Shunda [l, r] oraliq yig'indisini O(1) vaqtda topish mumkin: sum = prefix[r+1] - prefix[l]\n\n"
        "Bu misolda faqat bir marta so'rov bo'lgani uchun oddiy sikl yordamida ham yechsa bo'ladi.",
        "Birinchi qatorda massiv, ikkinchida l r.", "Yig'indi.",
        "1 ≤ n ≤ 10^4",
        examples, hidden, "easy", "Massivlar", "1")

# B095: Move Pieces to Match (simplified)
# Replace with: Squares of Numbers  — already covered. Use: K Closest to Origin (LC#973)
# Simpler: Sort By Frequency
def p_b095():
    def solve(inp):
        nums = inp.strip().split()
        from collections import Counter
        c = Counter(nums)
        return ' '.join(sorted(nums, key=lambda x: (c[x], -int(x))))
    examples = [
        {"input": "1 1 2 2 2 3", "output": "3 1 1 2 2 2"},
        {"input": "2 3 1 3 2", "output": "1 2 2 3 3"},
    ]
    hidden = []
    for _ in range(55):
        n = random.randint(1, 12)
        nums = [random.randint(1, 5) for _ in range(n)]
        inp = ' '.join(map(str, nums))
        hidden.append({"input": inp, "output": solve(inp)})
    add("B095", "Chastota bo'yicha saralash (Sort by Frequency)",
        "Sonlar massivini ularning uchrash chastotasi (necha marta qatnashgani) bo'yicha O'SISH tartibida saralang.\n\n"
        "Qo'shimcha shart: Agar ikki xil sonning uchrash chastotasi bir xil bo'lsa, u holda KATTA son birinchi yozilsin (ya'ni qiymati bo'yicha kamayish tartibida).\n\n"
        "Misol: [1, 1, 2, 2, 2, 3]\n"
        "Chastotalar: 3(1 marta), 1(2 marta), 2(3 marta).\n"
        "Natija: [3, 1, 1, 2, 2, 2]. (1 ning chastotasi 2, shuning uchun 2 dan oldin yozildi).\n\n"
        "Misol-2: [2, 3, 1, 3, 2]\n"
        "Chastotalar: 1(1), 2(2), 3(2). 2 va 3 bir xil ko'p uchragan (2 marta). Shartga ko'ra qiymati katta bo'lgan 3 oldin keladi!\n"
        "Natija: [1, 3, 3, 2, 2].",
        "Bir qatorda massiv.", "Saralangan massiv.",
        "1 ≤ n ≤ 100",
        examples, hidden, "easy", "Hash", "3 1 1 2 2 2")

# B096: Verifying an Alien Dictionary (LC#953) — simplified
def p_b096():
    def solve(inp):
        lines = inp.strip().split('\n')
        words = lines[0].split()
        order = lines[1]
        idx = {c: i for i, c in enumerate(order)}
        for i in range(len(words)-1):
            a, b = words[i], words[i+1]
            for j in range(min(len(a), len(b))):
                if a[j] != b[j]:
                    if idx[a[j]] > idx[b[j]]: return "false"
                    break
            else:
                if len(a) > len(b): return "false"
        return "true"
    examples = [
        {"input": "hello leetcode\nhlabcdefgijkmnopqrstuvwxyz", "output": "true"},
        {"input": "word world row\nworldabcefghijkmnpqstuvxyz", "output": "false"},
    ]
    hidden = []
    samples = [
        ("apple app\nabcdefghijklmnopqrstuvwxyz", "false"),
        ("abc def\nabcdefghijklmnopqrstuvwxyz", "true"),
        ("a\nabcdefghijklmnopqrstuvwxyz", "true"),
        ("ba ab\nabcdefghijklmnopqrstuvwxyz", "false"),
        ("ba ab\nbacdefghijklmnopqrstuvwxyz", "true"),
    ]
    for inp, _exp in samples:
        hidden.append({"input": inp, "output": solve(inp)})
    for _ in range(55):
        order = list('abcdefghij'); random.shuffle(order); order = ''.join(order) + 'klmnopqrstuvwxyz'
        words = [''.join(random.choices('abcdefghij', k=random.randint(1, 4))) for _ in range(random.randint(2, 4))]
        inp = f"{' '.join(words)}\n{order}"
        hidden.append({"input": inp, "output": solve(inp)})
    add("B096", "Alien tilidagi lug'at tekshirish (Alien Dictionary)",
        "Tasavvur qiling — boshqa sayyoradagi mavjudotlar (\"alien\" lar) ham 26 ta lotin harflaridan foydalanadi, LEKIN ularning alfavit TARTIBI biznikidan boshqacha. Masalan, ularda 'h' harfi 'a' dan oldin kelishi mumkin.\n\n"
        "ALIEN ALFAVITI — 26 ta noyob lotin harfining BIROR TARTIBDA joylashgan satri (permutatsiyasi).\n"
        "  Misol: 'hlabcdefgijkmnopqrstuvwxyz'  →  bu alfavitda 'h' birinchi (indeks 0), 'l' ikkinchi (indeks 1), keyin 'a' uchinchi va h.k.\n\n"
        "LEKSIKOGRAFIK TARTIB (lug'at tartibi) — so'zlarni lug'atdagi singari solishtirish:\n"
        "  • So'zlarning birinchi farq qilgan harfini taqqoslang. Qaysisining harfi alfavitda OLDINroq bo'lsa — o'sha so'z oldin keladi.\n"
        "  • Agar bir so'z ikkinchisining BOSHIga to'la mos kelsa-yu, qisqaroq bo'lsa — qisqaroqi oldin keladi (oddiy alfavit qoidasi: 'app' < 'apple').\n\n"
        "VAZIFA: Berilgan so'zlar ALIEN alfaviti bo'yicha o'sib boruvchi (leksikografik) tartibda bo'lsa — true; aks holda — false.\n\n"
        "Misollar:\n"
        "  words='hello leetcode', alfavit='hlabcdefgijkmnopqrstuvwxyz'\n"
        "    Birinchi farqli harflar: 'h' (hello) vs 'l' (leetcode). Alien alfavitda h(0) < l(1) → tartib to'g'ri → true.\n"
        "  words='word world', alfavit standart 'abcd...xyz'\n"
        "    'word' va 'world' birinchi 3 harfda teng. 4-pozitsiyada 'd' va 'l' — 'd' oldin keladi → 'word' < 'world' → true.\n"
        "  words='apple app', alfavit standart\n"
        "    'apple' va 'app' birinchi 3 harfda teng, lekin 'app' qisqaroq. 'app' oldin kelishi kerak edi → tartib noto'g'ri → false.\n\n"
        "ALGORITM: alfavitda har harfning indeksini lug'atga oling: idx[c] = i. Keyin words[i] va words[i+1] juftligini solishtiring — agar har juft to'g'ri bo'lsa true, biror joyda buzilsa darhol false.",
        "Birinchi qatorda so'zlar (probel bilan), ikkinchida alien alfaviti (26 ta harfdan iborat).", "true yoki false.",
        "1 ≤ |words| ≤ 100",
        examples, hidden, "easy", "Hash", "true")

# B097: Arranging Coins (LC#441)
def p_b097():
    def solve(inp):
        n = int(inp.strip())
        # Find largest k where k(k+1)/2 <= n
        k = int(((1 + 8*n)**0.5 - 1) / 2)
        while k*(k+1)//2 > n: k -= 1
        while (k+1)*(k+2)//2 <= n: k += 1
        return str(k)
    examples = [
        {"input": "5", "output": "2", "explanation": "1+2=3, 1+2+3=6 — 2 to'liq qator"},
        {"input": "8", "output": "3"},
        {"input": "0", "output": "0"},
    ]
    hidden = []
    for n in [0, 1, 2, 3, 5, 6, 7, 8, 10, 15, 100, 10000, 1000000]:
        hidden.append({"input": str(n), "output": solve(str(n))})
    for _ in range(50):
        n = random.randint(0, 10**8)
        hidden.append({"input": str(n), "output": solve(str(n))})
    add("B097", "Tangalarni tartiblash (Arranging Coins)",
        "n ta tanga. Pog'ona qatorga joylash: 1-qatorda 1, 2-qatorda 2, ... To'liq nechta qator hosil bo'lishi mumkin?",
        "Bir manfiy bo'lmagan son n.", "To'liq qatorlar soni.",
        "0 ≤ n ≤ 2^31-1",
        examples, hidden, "easy", "Arifmetika", "2")

# B098: Sqrt Newton (LC#69) variant — Average of Levels in Binary Tree → skip (tree)
# Use: Number of Steps to Reduce a Number to Zero (LC#1342)
def p_b098():
    def solve(inp):
        n = int(inp.strip())
        c = 0
        while n > 0:
            n = n // 2 if n % 2 == 0 else n - 1
            c += 1
        return str(c)
    examples = [
        {"input": "14", "output": "6", "explanation": "14→7→6→3→2→1→0"},
        {"input": "8", "output": "4"},
        {"input": "123", "output": "12"},
    ]
    hidden = []
    for n in [0, 1, 2, 3, 5, 14, 100, 1000, 10**6]:
        hidden.append({"input": str(n), "output": solve(str(n))})
    for _ in range(55):
        n = random.randint(0, 10**6)
        hidden.append({"input": str(n), "output": solve(str(n))})
    add("B098", "Sonni nolga keltirish qadami (Steps to Reduce to Zero)",
        "Sizga manfiy bo'lmagan n soni berilgan. Uni 0 ga tushirish uchun necha qadam kerak?\n\n"
        "Qoidalar:\n"
        "  • Agar son juft bo'lsa, uni 2 ga bo'lasiz.\n"
        "  • Agar son toq bo'lsa, undan 1 ayirasiz.\n\n"
        "Misol: n = 14\n"
        "  1-qadam: 14 juft, 2 ga bo'lamiz = 7\n"
        "  2-qadam: 7 toq, 1 ayiramiz = 6\n"
        "  3-qadam: 6 juft, 2 ga bo'lamiz = 3\n"
        "  4-qadam: 3 toq, 1 ayiramiz = 2\n"
        "  5-qadam: 2 juft, 2 ga bo'lamiz = 1\n"
        "  6-qadam: 1 toq, 1 ayiramiz = 0.\n"
        "Jami 6 qadam.",
        "Bir manfiy bo'lmagan son.", "Qadamlar soni.",
        "0 ≤ n ≤ 10^6",
        examples, hidden, "easy", "Bit amallari", "6")

# B099: Decode XORed Array (LC#1720) — simplified
def p_b099():
    def solve(inp):
        lines = inp.strip().split('\n')
        encoded = list(map(int, lines[0].split()))
        first = int(lines[1])
        out = [first]
        for e in encoded:
            out.append(out[-1] ^ e)
        return ' '.join(map(str, out))
    examples = [
        {"input": "1 2 3\n1", "output": "1 0 2 1"},
        {"input": "6 2 7 3\n4", "output": "4 2 0 7 4"},
    ]
    hidden = []
    for _ in range(55):
        n = random.randint(1, 10)
        first = random.randint(0, 100)
        orig = [first]
        for _ in range(n):
            orig.append(random.randint(0, 100))
        encoded = [orig[i] ^ orig[i+1] for i in range(n)]
        inp = f"{' '.join(map(str,encoded))}\n{first}"
        hidden.append({"input": inp, "output": solve(inp)})
    add("B099", "XOR-shifrlangan massivni decoddash (Decode XORed Array)",
        "XOR amali (^) — ikkilik amal:  bitlar bir xil bo'lsa 0, har xil bo'lsa 1. Asosiy xossasi: a ^ b ^ b = a (bir songa ikki marta XOR qilsangiz, o'sha song qaytib keladi).\n\n"
        "MASALA: kimdir original massiv arr ni shu qoida bilan shifrlagan:\n"
        "    encoded[i] = arr[i] XOR arr[i+1]\n"
        "(ya'ni har keyingi juft elementni XOR qilib, encoded ni hosil qilgan; uzunligi bittaga kam.)\n"
        "Sizga encoded VA arr ning birinchi elementi (arr[0]) berilgan. Original arr ni tiklang.\n\n"
        "TIKLASH USULI: yuqoridagi xossadan:\n"
        "    arr[i+1] = encoded[i] XOR arr[i]\n"
        "Demak arr[0] dan boshlab ketma-ket har keyingisini hisoblang.\n\n"
        "Misol: encoded=[1,2,3], arr[0]=1\n"
        "  arr[1] = encoded[0] ^ arr[0] = 1 ^ 1 = 0\n"
        "  arr[2] = encoded[1] ^ arr[1] = 2 ^ 0 = 2\n"
        "  arr[3] = encoded[2] ^ arr[2] = 3 ^ 2 = 1\n"
        "  Javob: 1 0 2 1.",
        "Birinchi qatorda encoded, ikkinchida arr[0].", "Original massiv.",
        "1 ≤ |encoded| ≤ 10^4",
        examples, hidden, "easy", "Bit amallari", "1 0 2 1")

# B100: Three Consecutive Odds (LC#1550)
def p_b100():
    def solve(inp):
        nums = list(map(int, inp.strip().split()))
        cur = 0
        for x in nums:
            cur = cur+1 if x % 2 != 0 else 0
            if cur >= 3: return "true"
        return "false"
    examples = [
        {"input": "2 6 4 1", "output": "false"},
        {"input": "1 2 34 3 4 5 7 23 12", "output": "true", "explanation": "5 7 23"},
    ]
    hidden = []
    for _ in range(55):
        n = random.randint(3, 15)
        nums = [random.randint(1, 50) for _ in range(n)]
        inp = ' '.join(map(str, nums))
        hidden.append({"input": inp, "output": solve(inp)})
    add("B100", "Uchta ketma-ket toq son (Three Consecutive Odds)",
        "Massivda 3 ta ketma-ket toq son bo'lsa true.",
        "Bir qatorda massiv.", "true yoki false.",
        "1 ≤ n ≤ 1000",
        examples, hidden, "easy", "Massivlar", "false")


# Run all generators
for name in list(globals().keys()):
    if name.startswith('p_b'):
        globals()[name]()


def run():
    app = create_app()
    with app.app_context():
        added = updated = 0
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
