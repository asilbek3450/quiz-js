from app import app
from models import Question, ControlWork, db
import random

def expand_control_work():
    with app.app_context():
        # Get control work
        cw = ControlWork.query.filter_by(grade=5, quarter=3).first()
        if not cw:
            print("Control Work topilmadi!")
            return
            
        print(f"Hozirgi Nazorat ishi savollari soni: {len(cw.questions)}")
        
        # Get all 5th grade Q3 questions
        all_q3_questions = Question.query.filter_by(grade=5, quarter=3).all()
        
        # Check current questions IDs to avoid duplicates
        existing_ids = set([q.id for q in cw.questions])
        
        # We need to add enough questions to reach 105+
        target_count = 105
        needed = target_count - len(cw.questions)
        
        if needed <= 0:
            print("Savollar yetarli (105 tadan ko'p).")
            return
            
        # Get potential questions to add
        potential_questions = [q for q in all_q3_questions if q.id not in existing_ids]
        
        # If there are fewer available than needed, just take all available
        if len(potential_questions) < needed:
            needed = len(potential_questions)
            
        # Select randomly
        selected_questions = random.sample(potential_questions, needed)
        
        for sq in selected_questions:
            cw.questions.append(sq)
            
        db.session.commit()
        
        print(f"Tanlangan {needed} ta oddiy/murakkab Word/Excel savollari Nazorat ishiga qo'shildi.")
        print(f"ENDI Nazorat ishida jami: {len(cw.questions)} ta savol mavjud (mix of logic and practical questions)")

if __name__ == "__main__":
    expand_control_work()
