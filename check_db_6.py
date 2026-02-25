from app import app
from models import Subject, Question, ControlWork

with app.app_context():
    questions_6_3 = Question.query.filter_by(grade=6, quarter=3).all()
    print(f"\nTotal questions for 6th grade, 3rd quarter: {len(questions_6_3)}")
    cw_6 = ControlWork.query.filter_by(grade=6, quarter=3).first()
    if cw_6:
        print(f"Control work exists for 6th grade Q3. Question count: {len(cw_6.questions)}")
    else:
        print("No control work found for 6th grade Q3.")
