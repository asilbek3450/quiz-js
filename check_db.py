from app import app
from models import Subject, Question

with app.app_context():
    subjects = Subject.query.all()
    print("Subjects:")
    for s in subjects:
        print(f"ID: {s.id}, Name: {s.name}, Grades: {s.grades}")
    
    questions_5_3 = Question.query.filter_by(grade=5, quarter=3).all()
    print(f"\nTotal questions for 5th grade, 3rd quarter: {len(questions_5_3)}")
    if questions_5_3:
        for q in questions_5_3[:3]:
            print(f"- [ID: {q.id}, Diff: {q.difficulty}] {q.question_text}")
            print(f"  A: {q.option_a}, B: {q.option_b}, C: {q.option_c}, D: {q.option_d} -> {q.correct_answer}")
            print("-" * 20)
