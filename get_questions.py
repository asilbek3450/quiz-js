from app import app
from models import Question, Subject
from extensions import db

with app.app_context():
    for sub in Subject.query.all():
        print(f"Subject: {sub.name}, Grade: {sub.grade}")
    
    questions = Question.query.filter_by(grade=5, quarter=3).all()
    print(f"\nFound {len(questions)} questions for 5th grade, 3rd quarter:")
    for q in questions[:5]:
        print(f"- {q.text}")
