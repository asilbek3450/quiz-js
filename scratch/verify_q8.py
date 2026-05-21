import sys
import os
import random

sys.path.insert(0, '/Users/asilbek/Desktop/AI-Projects/quiz-js')
os.environ.setdefault('FLASK_ENV', 'development')

from app import create_app
from models import db, Question

def main():
    app = create_app()
    with app.app_context():
        # Get all 8th grade 4th quarter questions
        questions = Question.query.filter_by(grade=8, quarter=4).all()
        print(f"Total Grade 8 Q4 questions in database: {len(questions)}")

        # Keywords for out-of-syllabus (complex) topics
        out_of_syllabus_keywords = [
            "open(", ".read(", "readline", "file", "fayl",
            "try:", "except ", "finally:", "error", "xatolik", "exception",
            "stack", "lifo", "queue", "navbat", "fifo", "stek", "steyk",
            "pop(", "extend(", "zip(", "enumerate(", "is va =="
        ]

        found_bad = []
        for q in questions:
            text = (q.question_text or "").lower()
            if any(kw in text for kw in out_of_syllabus_keywords):
                found_bad.append(q)

        print(f"\n--- Database Syllabus Compliance Check ---")
        if found_bad:
            print(f"WARNING: Found {len(found_bad)} non-compliant questions:")
            for q in found_bad[:5]:
                print(f"  ID {q.id}: {q.question_text[:80]}...")
        else:
            print("SUCCESS: 0 out-of-syllabus questions found. The database is 100% compliant!")

        # Print some random samples of the new questions we added
        new_samples = [q for q in questions if "hisobla(5)" in q.question_text or "daraja(3, 3)" in q.question_text or "any([0" in q.question_text]
        print(f"\n--- Sample of Brand New Core Q4 Questions Added ---")
        for q in new_samples[:3]:
            print(f"\n[ID {q.id}] Difficulty: {q.difficulty}")
            print(q.question_text)
            print(f"  A) {q.option_a} | B) {q.option_b} | C) {q.option_c} | D) {q.option_d}")
            print(f"  Correct Answer: {q.correct_answer}")

        # Print a sample of cloned questions from Q1/Q2
        cloned_samples = [q for q in questions if q.id not in [x.id for x in found_bad] and "hisobla(5)" not in q.question_text and "daraja(3, 3)" not in q.question_text and "any([0" not in q.question_text]
        random.seed(123)
        random.shuffle(cloned_samples)
        print(f"\n--- Sample of Basic/Fundamental Python Questions (Taught in Q1/Q2) ---")
        for q in cloned_samples[:3]:
            print(f"\n[ID {q.id}] Difficulty: {q.difficulty}")
            print(q.question_text[:120])
            print(f"  A) {q.option_a} | B) {q.option_b} | C) {q.option_c} | D) {q.option_d}")
            print(f"  Correct Answer: {q.correct_answer}")

if __name__ == '__main__':
    main()
