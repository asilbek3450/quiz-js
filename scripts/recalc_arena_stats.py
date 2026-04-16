"""
Barcha Arena foydalanuvchilari uchun problems_solved va rating ni
haqiqiy AC submissionlar asosida qayta hisoblaydi.

Ishlatish:
    python scripts/recalc_arena_stats.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from extensions import db
from models import ArenaUser, ArenaProblem, ArenaSubmission

DIFF_PTS = {'easy': 10, 'medium': 25, 'hard': 50}

with app.app_context():
    users = ArenaUser.query.all()
    print(f"Jami {len(users)} ta foydalanuvchi topildi.\n")

    for user in users:
        # Har bir foydalanuvchining birinchi AC submissionlarini topamiz
        ac_subs = (
            db.session.query(ArenaSubmission.problem_id)
            .filter_by(user_id=user.id, status='AC')
            .distinct()
            .all()
        )
        solved_ids = [row[0] for row in ac_subs]
        problems_solved = len(solved_ids)

        # Har bir hal qilingan masalaning qiyinligiga qarab reyting hisoblash
        rating = 0
        for pid in solved_ids:
            problem = ArenaProblem.query.get(pid)
            if problem:
                rating += DIFF_PTS.get(problem.difficulty, 10)

        old_solved = user.problems_solved
        old_rating = user.rating

        user.problems_solved = problems_solved
        user.rating = rating

        print(
            f"  {user.username:<20} | "
            f"hal qildi: {old_solved} → {problems_solved} | "
            f"reyting: {old_rating} → {rating}"
        )

    db.session.commit()
    print("\nBarcha statistikalar yangilandi!")
