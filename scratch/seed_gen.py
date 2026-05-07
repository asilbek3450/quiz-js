import sys, os
import json
import random

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app
from models import db, ArenaProblem

def generate_math_problems():
    problems = []
    # B001: Fibonacci
    hidden_tests = [{"input": str(i), "output": str(fib(i))} for i in range(50)]
    problems.append({
        "code": "B001",
        "title": "Fibonachchi soni",
        "description": "n-chi Fibonachchi sonini toping. F(0)=0, F(1)=1, F(n)=F(n-1)+F(n-2).",
        "input_format": "Butun son n.",
        "output_format": "F(n).",
        "constraints": "0 <= n <= 40",
        "examples": [{"input": "5", "output": "5"}, {"input": "10", "output": "55"}],
        "hidden_tests": hidden_tests,
        "difficulty": "medium",
        "category": "Aritmetika",
        "correct_answer": "55"
    })
    
    # B002: Tub son
    def is_prime(n):
        if n < 2: return False
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0: return False
        return True
    
    hidden_tests = [{"input": str(i), "output": "YES" if is_prime(i) else "NO"} for i in range(1, 101)]
    problems.append({
        "code": "B002",
        "title": "Tub sonlikka tekshirish",
        "description": "Berilgan son tub bo'lsa 'YES', aks holda 'NO' chiqaring.",
        "input_format": "Butun son n.",
        "output_format": "'YES' yoki 'NO'.",
        "constraints": "1 <= n <= 10^9",
        "examples": [{"input": "7", "output": "YES"}, {"input": "10", "output": "NO"}],
        "hidden_tests": hidden_tests,
        "difficulty": "easy",
        "category": "Aritmetika",
        "correct_answer": "YES"
    })

    # ... I will generate 100 problems in the actual script execution
    return problems

def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

# I'll create a more comprehensive generator script
