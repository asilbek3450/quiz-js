import sys
import os
import json

sys.path.insert(0, '/Users/asilbek/Desktop/AI-Projects/quiz-js')
os.environ.setdefault('FLASK_ENV', 'development')

from app import create_app
from models import db, Question

def main():
    app = create_app()
    with app.app_context():
        # Get all 8th grade 4th quarter questions
        questions = Question.query.filter_by(grade=8, quarter=4).all()
        print(f"Total Grade 8 Q4 questions: {len(questions)}")
        
        # Categorize them by keywords in their text
        categories = {
            "file": ["open(", ".read", "readline", "file", "fayl"],
            "exception": ["try", "except", "finally", "error", "xatolik", "exception"],
            "stack_lifo": ["stack", "lifo", "stek", "steyk", "queue", "navbat", "fifo"],
            "recursion": ["recursion", "rekursiya", "factorial", "faktorial"],
            "dictionary": ["dict", "lug'at", "keys()", "values()", "items()", "get("],
            "set": ["set", "to'plam", "union", "intersection", "add(", "kesishma", "birlashma"],
            "function": ["def ", "return", "funksiya", "parametr", "argument"],
            "scope": ["global", "local", "mahalliy", "umumiy", "scope"],
            "other_list_methods": ["pop(", "pop()", "extend(", "enumerate(", "zip(", "sort("]
        }
        
        counts = {cat: 0 for cat in categories}
        uncategorized = []
        
        for q in questions:
            text = (q.question_text or "").lower()
            matched = False
            for cat, keywords in categories.items():
                if any(kw in text for kw in keywords):
                    counts[cat] += 1
                    matched = True
            if not matched:
                uncategorized.append(q)
                
        print("\nQuestion counts by category/keywords:")
        for cat, count in counts.items():
            print(f"  {cat}: {count}")
            
        print(f"\nTotal uncategorized: {len(uncategorized)}")
        print("\nSome sample uncategorized questions:")
        for q in uncategorized[:10]:
            print(f"  ID {q.id}: {q.question_text[:100]}")

if __name__ == '__main__':
    main()
