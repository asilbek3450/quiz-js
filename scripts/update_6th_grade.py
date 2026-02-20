import sys
import os
import random
from datetime import datetime

# Adjust path to import app and models
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import Question, Subject

# Global set to track uniqueness
SEEN_QUESTIONS = set()

def get_or_create_subject():
    subject = Subject.query.filter_by(name='Informatika').first()
    if not subject:
        subject = Subject(name='Informatika', name_ru='Информатика', name_en='Computer Science', grades='5,6,7,8,9,10,11')
        db.session.add(subject)
        db.session.commit()
    return subject

def add_question_safe(questions_list, subject_id, grade, quarter, text, opts, correct):
    global SEEN_QUESTIONS
    
    # Ensure 4 unique options
    unique_opts = list(set(opts))
    if len(unique_opts) < 4:
        while len(unique_opts) < 4:
            dummy = f"Variant {len(unique_opts) + 1}"
            if dummy not in unique_opts:
                unique_opts.append(dummy)
    
    final_opts = unique_opts[:4]
    if correct not in final_opts:
        final_opts[0] = correct
        
    random.shuffle(final_opts)
    
    try:
        correct_idx = final_opts.index(correct)
        correct_char = ['A', 'B', 'C', 'D'][correct_idx]
    except ValueError:
        return False
        
    if text in SEEN_QUESTIONS:
        return False
    SEEN_QUESTIONS.add(text)
    
    q = Question(
        subject_id=subject_id,
        grade=grade,
        quarter=quarter,
        question_text=text,
        option_a=str(final_opts[0]),
        option_b=str(final_opts[1]),
        option_c=str(final_opts[2]),
        option_d=str(final_opts[3]),
        correct_answer=correct_char
    )
    questions_list.append(q)
    return True

def generate_variations(concept, definition, wrong_options):
    variations = []
    q_templates = [
        f"{concept} nima?",
        f"{concept} - bu ...",
        f"{concept} qaysi vazifani bajaradi?",
        f"Kompyuterda {concept} nima uchun ishlatiladi?",
        f"\"{concept}\" tushunchasining ma'nosi nima?",
        f"Quyidagilardan qaysi biri {concept} hisoblanadi?",
        f"{concept} haqida to'g'ri fikrni toping.",
        f"{concept} buyrug'ining vazifasi qanday?",
        f"Qaysi holatda {concept} ishlatiladi?",
        f"{concept} nima vazifa uchun mo'ljallangan?",
    ]
    for t in q_templates:
        variations.append((t, [definition] + wrong_options, definition))
    
    r_templates = [
        f"{definition} - bu qaysi buyruq yoki qurilma?",
        f"{definition} nima deb ataladi?",
        f"\"{definition}\" ta'rifi qaysi atamaga tegishli?",
        f"Qaysi buyruq {definition.lower()}?",
        f"Hujjatda {definition.lower()} nima orqali bajariladi?",
        f"Dasturda {definition.lower()} uchun nima ishlatiladi?",
    ]
    for t in r_templates:
        variations.append((t, [concept] + wrong_options, concept))
        
    return variations

# ================= QUARTER 1: MS Word (Complex) =================

def get_q1_pool():
    items = [
        ("Ctrl+X", "Matnni qirqib olish va buferga saqlash", ["Nusxalash", "Joylashtirish", "O'chirish"]),
        ("Ctrl+C", "Matn nusxasini buferga saqlash", ["Qirqish", "Joylashtirish", "Saqlash"]),
        ("Ctrl+V", "Buferdagi matnni kursor turgan joyga qo'shish", ["Nusxalash", "Qirqish", "Bekor qilish"]),
        ("Ctrl+Z", "Oxirgi bajarilgan amalni bekor qilish", ["Qaytarish", "Saqlash", "Yopish"]),
        ("Ctrl+S", "Hujjatdagi o'zgarishlarni xotiraga saqlash", ["Chop etis", "Ochish", "Yopish"]),
        ("Header", "Har bir sahifaning yuqori qismidagi takrorlanuvchi sarlavha", ["Footer", "Footnote", "Page Number"]),
        ("Footer", "Har bir sahifaning pastki qismidagi takrorlanuvchi sarlavha", ["Header", "Page Number", "Rasm"]),
        ("Portrait", "Sahifaning vertikal (tik) holatda joylashishi", ["Landscape", "Square", "Circle"]),
        ("Landscape", "Sahifaning gorizontal (yotiq) holatda joylashishi", ["Portrait", "Vertical", "Column"]),
        ("Ctrl+A", "Hujjatdagi barcha obyektlarni belgilash", ["Nusxalash", "Saqlash", "Qirqish"]),
        ("Find", "Hujjat ichidan kerakli so'z yoki iborani qidirish", ["Replace", "Delete", "Save"]),
        ("Replace", "Qidirilgan so'zni boshqa so'z bilan almashtirish", ["Find", "Format", "Copy"]),
        ("Page Number", "Har bir sahifaga tartib raqami qo'yish", ["Date", "Time", "Header"]),
        ("Font Size", "Matn belgilarining o'lchamini o'zgartirish", ["Color", "Style", "Alignment"]),
    ]
    pool = []
    for concept, definition, wrongs in items:
        pool.extend(generate_variations(concept, definition, wrongs))
    
    # Combined complex ones
    pool.append(("Ctrl+X va Ctrl+V ketma-ketligi nima uchun ishlatiladi?", "Matnni ko'chirish (bir joydan boshqa joyga)", ["Nusxalash", "O'chirish", "Formatlash", "Saqlash"]))
    pool.append(("Ctrl+C va Ctrl+V ketma-ketligi nima uchun ishlatiladi?", "Matn nusxasini yaratish", ["Matnni ko'chirish", "O'chirish", "Saqlash", "Yopish"]))
    
    return pool

# ================= QUARTER 2: MS Excel (Logic) =================

def get_q2_pool():
    items = [
        ("SUM", "Belgilangan kataklardagi sonlar yig'indisini hisoblash", ["O'rtacha", "Maksimum", "Sanoq"]),
        ("AVERAGE", "Belgilangan kataklardagi sonlarning o'rtacha qiymatini topish", ["Yig'indi", "Minimum", "Maksimum"]),
        ("MAX", "Tanlangan sohadagi eng katta sonni aniqlash", ["MIN", "COUNT", "SUM"]),
        ("MIN", "Tanlangan sohadagi eng kichik sonni aniqlash", ["MAX", "SUM", "AVERAGE"]),
        ("COUNT", "Faqat sonli qiymatga ega kataklar sonini sanash", ["SUM", "MAX", "Average"]),
        ("COUNTA", "Bo'sh bo'lmagan (har qanday ma'lumotli) kataklar sonini aniqlash", ["COUNT", "SUM", "MIN"]),
        ("$A$1", "Absolyut (q'atiy) katak manzili", ["Nisbiy manzil", "Xato manzil", "Matn"]),
        ("Excel", "Elektron jadvallar bilan ishlash dasturi", ["Matn muharriri", "Taqdimot dasturi", "Brauzer"]),
        ("Column", "Lotin harflari bilan belgilanadigan ustun", ["Row", "Cell", "Sheet"]),
        ("Row", "Raqamlar bilan belgilanadigan qator", ["Column", "Cell", "Sheet"]),
        ("Cell", "Ustun va qator kesishmasidagi elektron jadval birligi", ["Row", "Column", "Sheet"]),
        ("Sheet", "Excel hujjatidagi alohida ishchi varaq", ["Workbook", "Cell", "Row"]),
        ("Workbook", "Bir yoki bir nechta varaqdan iborat Excel fayli", ["Sheet", "Document", "Presentation"]),
        ("AutoSum", "Tanlangan kataklar yig'indisini tezda hisoblash tugmasi", ["Average", "Max", "Min"]),
        ("Sort", "Ma'lumotlarni alifbo yoki raqam tartibida joylashtirish", ["Filter", "Sum", "Average"]),
        ("Filter", "Kerakli ma'lumotlarni saralab olish imkoniyati", ["Sort", "Max", "Count"]),
    ]
    pool = []
    for concept, definition, wrongs in items:
        pool.extend(generate_variations(concept, definition, wrongs))
    
    return pool

# ================= QUARTER 3: Scratch (Flow) =================

def get_q3_pool():
    items = [
        ("Motion", "Spritning harakatini boshqaruvchi ko'k rangli bloklar", ["Sound", "Looks", "Control"]),
        ("Looks", "Sprit ko'rinishi va rangini o'zgartiruvchi binafsha bloklar", ["Motion", "Events", "Sensing"]),
        ("Events", "Dasturni ishga tushiruvchi (Yashil bayroqcha) sariq bloklar", ["Control", "Operators", "Sound"]),
        ("Control", "Sikllar va shartlarni (if, repeat) boshqaruvchi olovrang bloklar", ["Events", "Looks", "Motion"]),
        ("Sprit", "Scratch loyihasidagi asosiy obyekt (qahramon)", ["Fon", "Sahna", "Ovoz"]),
        ("Stage", "Dastur natijasi namoyish etiladigan sahna", ["Costume", "Script", "Variable"]),
        ("X o'qi", "Spritning gorizontal (chap-o'ng) joylashuvini belgilaydi", ["Y o'qi", "Z o'qi", "Rang"]),
        ("Y o'qi", "Spritning vertikal (tepa-past) joylashuvini belgilaydi", ["X o'qi", "Z o'qi", "Hajm"]),
        ("Costume", "Spritning tashqi ko'rinishi yoki libosi", ["Background", "Sound", "Variable"]),
        ("Backdrop", "Scratch sahnasining orqa foni", ["Costume", "Sprit", "Script"]),
        ("Variable", "Ma'lumotlarni saqlash uchun ishlatiladigan o'zgaruvchi", ["Operator", "List", "Sensing"]),
        ("Operator", "Matematik va mantiqiy amallarni bajaruvchi yashil bloklar", ["Sensing", "Control", "Looks"]),
        ("Sensing", "Spritning boshqa obyektlarga tegishi yoki rangini sezuvchi bloklar", ["Motion", "Looks", "Sound"]),
        ("Pen", "Sprit harakatlanganda chiziq chizuvchi asbob", ["Brush", "Eraser", "Select"]),
    ]
    pool = []
    for concept, definition, wrongs in items:
        pool.extend(generate_variations(concept, definition, wrongs))
    
    return pool

# ================= QUARTER 4: PowerPoint & Internet =================

def get_q4_pool():
    items = [
        ("PowerPoint", "Taqdimotlar yaratish uchun mo'ljallangan dastur", ["Excel", "Word", "Paint"]),
        ("Slide", "Taqdimotning alohida bir varag'i (sahifasi)", ["Document", "Cell", "Page"]),
        ("F5", "Taqdimotni birinchi slayddan boshlab namoyish etish", ["Shift+F5", "Esc", "Ctrl+S"]),
        ("Transition", "Slaydlar almashayotganda sodir bo'ladigan effekt", ["Animation", "Design", "Layout"]),
        ("Animation", "Slayd ichidagi obyektlar uchun beriladigan effekt", ["Transition", "Theme", "Format"]),
        ("URL", "Internetdagi veb-sahifaning yagona manzili", ["Login", "Parol", "Username"]),
        ("Browser", "Veb-saytlarni ko'rish uchun maxsus dastur", ["Search Engine", "Website", "Server"]),
        ("HTTPS", "Xavfsiz va shifrlangan ma'lumot almashish protokoli", ["HTTP", "URL", "WWW"]),
        ("Search Engine", "Internetdan kerakli ma'lumotlarni qidirish sayti", ["Browser", "Email", "Social Network"]),
        ("Hyperlink", "Boshqa sahifa yoki hujjatga yo'naltiruvchi faol bog'lama", ["Image", "Video", "Audio"]),
        ("Transition", "Slaydlar almashish vaqtidagi vizual effekt", ["Animation", "Theme", "Layout"]),
        ("Design", "Taqdimotning tashqi ko'rinishini belgilovchi tayyor andozalar", ["Insert", "Review", "View"]),
        ("Slide Show", "Taqdimotni to'liq ekranda namoyish qilish rejimi", ["Edit Mode", "Outline View", "Notes"]),
        ("IP Address", "Internetga ulangan har bir qurilmaning betakror raqamli manzili", ["URL", "Domain", "Login"]),
        ("Domain Name", "Veb-saytning harfli va oson eslab qolinadigan nomi", ["IP", "Password", "Username"]),
        ("Protocol", "Internetda ma'lumot almashish tartib va qoidalari", ["Browser", "Site", "File"]),
    ]
    pool = []
    for concept, definition, wrongs in items:
        pool.extend(generate_variations(concept, definition, wrongs))
    
    return pool

# ================= MAIN LOGIC =================

def main():
    with app.app_context():
        print("Starting 6th grade questions upgrade...")
        subject = get_or_create_subject()
        
        # Target counts based on previous analysis
        targets = {1: 200, 2: 200, 3: 200, 4: 196}
        
        # Clean existing 6th grade questions
        print("Cleaning old 6th grade questions...")
        Question.query.filter_by(grade=6, subject_id=subject.id).delete()
        db.session.commit()
        
        quarter_pools = {
            1: get_q1_pool,
            2: get_q2_pool,
            3: get_q3_pool,
            4: get_q4_pool
        }
        
        all_new = []
        for quarter, target in targets.items():
            print(f"Generating for Quarter {quarter} (Target: {target})...")
            q_list = []
            pool = quarter_pools[quarter]()
            random.shuffle(pool)
            
            # Fill from pool
            for text, opts, ans in pool:
                if len(q_list) >= target: break
                add_question_safe(q_list, subject.id, 6, quarter, text, opts, ans)
            
            # If pool is not enough, add random variations or combinations
            attempts = 0
            while len(q_list) < target and attempts < 2000:
                attempts += 1
                text, opts, ans = random.choice(pool)
                # Ensure uniqueness by finding a non-duplicate template variant
                add_question_safe(q_list, subject.id, 6, quarter, text, opts, ans)
            
            print(f"  Generated {len(q_list)} questions.")
            all_new.extend(q_list)
            
        print(f"Total questions to save: {len(all_new)}")
        
        # Bulk save
        chunk_size = 200
        for i in range(0, len(all_new), chunk_size):
            db.session.bulk_save_objects(all_new[i:i+chunk_size])
            db.session.commit()
            print(f"  Saved chunk {i}-{i+chunk_size}")

        print("Finished upgrading 6th grade questions.")

if __name__ == '__main__':
    main()
