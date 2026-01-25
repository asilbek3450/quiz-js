import random
from app import app, db, Question, Subject

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
    if len(opts) < 4: return False

    final_opts = opts[:4]
    random.shuffle(final_opts)
    
    try:
        correct_idx = final_opts.index(correct)
    except ValueError:
        return False
        
    correct_char = ['A', 'B', 'C', 'D'][correct_idx]
    unique_key = f"{grade}-{quarter}-{text}"
    
    if unique_key in SEEN_QUESTIONS: return False
        
    SEEN_QUESTIONS.add(unique_key)
    
    q = Question(
        subject_id=subject_id, grade=grade, quarter=quarter, question_text=text,
        option_a=final_opts[0], option_b=final_opts[1], option_c=final_opts[2], option_d=final_opts[3],
        correct_answer=correct_char
    )
    questions_list.append(q)
    return True

def generate_variations(concept, definition, wrong_options):
    """
    Generates a list of (question_text, [options], correct_answer) tuples.
    """
    variations = []
    
    # Template Set 1: Direct Definition
    q_templates = [
        f"{concept} nima?",
        f"{concept} - bu ...",
        f"{concept}ning vazifasi nima?",
        f"Kompyuterda {concept} nima uchun ishlatiladi?",
        f"\"{concept}\" tushunchasining ma'nosi nima?",
        f"Quyidagilardan qaysi biri {concept} hisoblanadi?",
        f"{concept} nima vazifani bajaradi?",
        f"{concept} haqida to'g'ri fikrni toping.",
    ]
    
    for t in q_templates:
        variations.append((t, [definition] + wrong_options, definition))
        
    # Template Set 2: Reverse Definition
    def_clean = definition.lower().replace(" - bu", "").strip()
    r_templates = [
        f"{definition} - bu qaysi qurilma?",
        f"{definition} nima deb ataladi?",
        f"\"{definition}\" ta'rifi qaysi atamaga tegishli?",
        f"Qaysi qurilma {def_clean}?",
        f"Nima {def_clean}?",
        f"{def_clean} vazifasini nima bajaradi?",
    ]
    
    for t in r_templates:
        variations.append((t, [concept] + wrong_options, concept))
        
    return variations

# ================= 5th GRADE =================

def generate_5th_grade_q1(subject_id):
    questions = []
    grade, quarter = 5, 1
    
    parts = [
        ('Monitor', 'Ma\'lumotni ekranda tasvirlaydi', ['Klaviatura', 'Sichqoncha', 'Printer']),
        ('Klaviatura', 'Ma\'lumot kiritish qurilmasi', ['Monitor', 'Printer', 'Kolonka']),
        ('Sichqoncha', 'Grafik interfeysni boshqarish', ['Klaviatura', 'Skaner', 'Mikrofon']),
        ('Printer', 'Qog\'ozga chop etish', ['Skaner', 'Monitor', 'Modem']),
        ('Skaner', 'Rasmni kompyuterga kiritish', ['Printer', 'Plotter', 'Klaviatura']),
        ('Mikrofon', 'Ovoz yozish qurilmasi', ['Kolonka', 'Quloqchin', 'Kamera']),
        ('Veb-kamera', 'Video tasvirga olish', ['Ovoz', 'Matn', 'Fayl']),
        ('Kolonka', 'Ovoz chiqarish qurilmasi', ['Mikrofon', 'Sichqoncha', 'Klaviatura']),
        ('Sistema bloki', 'Kompyuterning asosiy qismi', ['Monitor', 'Ekran', 'Sim']),
        ('Protsessor', 'Ma\'lumotlarni qayta ishlash', ['Xotira', 'Disk', 'Ekran']),
        ('HDD', 'Ma\'lumotlarni doimiy saqlash', ['RAM', 'ROM', 'Flash']),
        ('RAM', 'Vaqtinchalik xotira', ['HDD', 'SSD', 'Disk']),
        ('Enter', 'Buyruqni tasdiqlash', ['Bekor qilish', 'O\'chirish', 'Chiqish']),
        ('Space', 'Bo\'sh joy qoldirish', ['Yozish', 'O\'chirish', 'Saqlash']),
    ]
    
    pool = []
    for p in parts:
        pool.extend(generate_variations(p[0], p[1], p[2]))
        
    random.shuffle(pool)
    for q in pool:
        if len(questions) >= 200: break
        add_question_safe(questions, subject_id, grade, quarter, q[0], q[1], q[2])
        
    return questions

def generate_5th_grade_q2(subject_id):
    questions = []
    grade, quarter = 5, 2
    
    items = [
        ('Qalam', 'Erkin chiziq chizish', ['O\'chirish', 'Bo\'yash', 'Kattalashtirish']),
        ('O\'chirg\'ich', 'Tasvirni o\'chirish', ['Chizish', 'Saqlash', 'Nusxalash']),
        ('Mo\'yqalam', 'Bo\'yoq bilan chizish', ['Matn yozish', 'O\'lcham olish', 'Kesish']),
        ('Fill (To\'ldirish)', 'Yopiq sohani bo\'yash', ['Chiziq chizish', 'O\'chirish', 'Tanlash']),
        ('Matn (Text)', 'Rasmga yozuv kiritish', ['Chizish', 'Ranglash', 'O\'chirish']),
        ('Lupa', 'Tasvirni yaqinlashtirish', ['Uzoqlashtirish', 'Kesish', 'Aylantirish']),
        ('Pipetka', 'Rang namunasini olish', ['Rang berish', 'O\'chirish', 'Chizish']),
        ('JPG', 'Siqilgan rasm formati', ['Matn', 'Video', 'Musiqa']),
        ('PNG', 'Shaffof fonli rasm', ['Ovoz', 'Hujjat', 'Video']),
        ('BMP', 'Siqilmagan rasm formati', ['Internet', 'Dastur', 'Virus']),
        ('Select', 'Tasvir qismini belgilash', ['O\'chirish', 'Chizish', 'Bo\'yash']),
        ('Resize', 'O\'lchamni o\'zgartirish', ['Ranglash', 'Saqlash', 'Ochish']),
        ('Rotate', 'Tasvirni aylantirish', ['Kesish', 'Nusxalash', 'Yozish']),
        ('Brush', 'Mo\'yqalam turi', ['Qalam', 'O\'chirg\'ich', 'Lupa']),
        ('Airbrush', 'Bo\'yoq purkash', ['Chiziq chizish', 'Katak chizish', 'Yozish']),
    ]
    
    pool = []
    for item in items:
        pool.extend(generate_variations(item[0], item[1], item[2]))
        
    random.shuffle(pool)
    for q in pool:
        if len(questions) >= 200: break
        add_question_safe(questions, subject_id, grade, quarter, q[0], q[1], q[2])
    
    return questions

def generate_5th_grade_q3(subject_id):
    questions = []
    grade, quarter = 5, 3
    # Already 200 via math generation
    letters = list("ABCDEFGH")
    for _ in range(500):
        if len(questions) >= 200: break
        c = random.choice(letters)
        r = random.randint(1, 99)
        q_text = random.choice([
            f"Excel: {c} ustun va {r} qator kesishmasi?",
            f"Katak manzili: {c}-ustun, {r}-qator.",
            f"Qaysi biri to'g'ri manzil: {c} va {r}?",
            f"{c} va {r} kesishgan katak?"
        ])
        ans = f"{c}{r}"
        opts = [ans, f"{r}{c}", f"{c}:{r}", f"{r}-{c}"]
        add_question_safe(questions, subject_id, grade, quarter, q_text, opts, ans)
    return questions

def generate_5th_grade_q4(subject_id):
    questions = []
    grade, quarter = 5, 4
    
    items = [
        ('Brauzer', 'Veb-saytlarni ko\'rish dasturi', ['Matn muharriri', 'O\'yin', 'Antivirus']),
        ('Google Chrome', 'Eng mashhur brauzerlardan biri', ['Operatsion tizim', 'Virus', 'Sayt']),
        ('Sayt', 'Internetdagi ma\'lumotlar sahifasi', ['Kompyuter qismi', 'Disk', 'Fayl']),
        ('Login', 'Foydalanuvchi ismi', ['Parol', 'Sayt', 'Kompyuter']),
        ('Parol', 'Maxfiy kirish so\'zi', ['Login', 'Ism', 'Manzil']),
        ('Spam', 'Keraksiz reklama xabarlari', ['Muhim xat', 'Virus', 'Dastur']),
        ('Email', 'Elektron pochta', ['Elektron kitob', 'Elektron hukumat', 'Elektron to\'lov']),
        ('Username', 'Foydalanuvchi nomi', ['Parol', 'IP manzil', 'Domen']),
        ('Download', 'Faylni internetdan olish', ['Internetga yuklash', 'O\'chirish', 'Saqlash']),
        ('Upload', 'Faylni internetga yuklash', ['Internetdan olish', 'O\'qish', 'Yozish']),
        ('Wi-Fi', 'Simsiz internet tarmog\'i', ['Simli tarmoq', 'Bluetooth', 'Mobil aloqa']),
        ('Router', 'Internet tarqatuvchi qurilma', ['Printer', 'Monitor', 'Skaner']),
        ('Modem', 'Internetga ulovchi qurilma', ['Klaviatura', 'Sichqoncha', 'Mikrofon']),
        ('Server', 'Katta hajmli ma\'lumotlar saqlovchi kompyuter', ['Oddiy kompyuter', 'Telefon', 'Planshet']),
        ('Klient', 'Serverdan ma\'lumot oluvchi kompyuter', ['Server', 'Provayder', 'Sayt']),
    ]
    
    pool = []
    for item in items:
        pool.extend(generate_variations(item[0], item[1], item[2]))
        
    random.shuffle(pool)
    for q in pool:
        if len(questions) >= 200: break
        add_question_safe(questions, subject_id, grade, quarter, q[0], q[1], q[2])
    return questions

# ================= 6th GRADE =================

def generate_6th_grade_q1(subject_id):
    questions = []
    grade, quarter = 6, 1
    
    items = [
        ('Ctrl+C', 'Nusxalash', ['Qirqish', 'Joylashtirish', 'Saqlash']),
        ('Ctrl+V', 'Joylashtirish', ['Nusxalash', 'O\'chirish', 'Chop etish']),
        ('Ctrl+X', 'Qirqib olish', ['Nusxalash', 'Saqlash', 'Formatlash']),
        ('Ctrl+Z', 'Amalni bekor qilish', ['Saqlash', 'Qaytarish', 'Yopish']),
        ('Ctrl+S', 'Hujjatni saqlash', ['Ochish', 'Yopish', 'Chop etish']),
        ('Ctrl+A', 'Hammasini belgilash', ['Bontasini belgilash', 'O\'chirish', 'Qirqish']),
        ('Ctrl+B', 'Qalin shrift', ['Og\'ma', 'Tagiga chizish', 'Kichik']),
        ('Ctrl+I', 'Og\'ma shrift', ['Qalin', 'Oddiy', 'Rangsiz']),
        ('Ctrl+U', 'Tagiga chizilgan', ['Usti chizilgan', 'Qalin', 'Og\'ma']),
        ('Header', 'Sahifa yuqori sarlavhasi', ['Pastki sarlavha', 'Matn', 'Rasm']),
        ('Footer', 'Sahifa pastki sarlavhasi', ['Yuqori sarlavha', 'Jadval', 'Hoshiya']),
        ('Page Number', 'Sahifa raqami', ['Sarlavha', 'Sana', 'Vaqt']),
        ('Landscape', 'Yotiq (Albumniy) joylashish', ['Tik (Knijniy)', 'Kvadrat', 'Aylana']),
        ('Portrait', 'Tik (Knijniy) joylashish', ['Yotiq (Albumniy)', 'Kvadrat', 'Uchburchak']),
        ('Find', 'Matn qidirish', ['Almashtirish', 'O\'chirish', 'Saqlash']),
        ('Replace', 'Matnni almashtirish', ['Qidirish', 'O\'chirish', 'Nusxalash']),
    ]
    
    pool = []
    for item in items:
        pool.extend(generate_variations(item[0], item[1], item[2]))
        
    random.shuffle(pool)
    for q in pool:
        if len(questions) >= 200: break
        add_question_safe(questions, subject_id, grade, quarter, q[0], q[1], q[2])
    return questions

def generate_6th_grade_q2(subject_id):
    questions = []
    grade, quarter = 6, 2
    # Already 200 via math generation
    funcs = ["SUM", "AVERAGE", "MAX", "MIN", "COUNT"]
    for _ in range(500):
        if len(questions) >= 200: break
        f = random.choice(funcs)
        r = f"{random.choice('ABC')}{random.randint(1,5)}:{random.choice('ABC')}{random.randint(6,10)}"
        q_text = random.choice([
            f"={f}({r}) formulasi nima hisoblaydi?",
            f"Qaysi formula {f} funksiyasini bajaradi?",
            f"Excel: ={f}({r}) natijasi nima bo'ladi?",
        ])
        ans_map = {"SUM": "Yig'indi", "AVERAGE": "O'rtacha", "MAX": "Maksimum", "MIN": "Minimum", "COUNT": "Sanoq"}
        ans = ans_map[f]
        opts = [ans, "Ayirma", "Ko'paytma", "Foiz"] 
        add_question_safe(questions, subject_id, grade, quarter, q_text, opts, ans)
    return questions

def generate_6th_grade_q3(subject_id):
    questions = []
    grade, quarter = 6, 3
    
    items = [
        ('Motion (Harakat)', 'Ko\'k rangli bloklar', ['Qizil', 'Sariq', 'Yashil']),
        ('Looks (Ko\'rinish)', 'Binafsha rangli', ['Ko\'k', 'Olovrang', 'Pushti']),
        ('Sound (Ovoz)', 'Pushti rangli bloklar', ['Sariq', 'Yashil', 'Qora']),
        ('Events (Voqea)', 'Sariq rangli bloklar', ['Ko\'k', 'Binafsha', 'Oq']),
        ('Control (Boshqaruv)', 'Olovrang bloklar', ['Yashil', 'Sariq', 'Ko\'k']),
        ('Sensing (Sezish)', 'Ochiq ko\'k rangli', ['Qizil', 'To\'q ko\'k', 'Sariq']),
        ('Operators', 'Yashil rangli', ['Qizil', 'Ko\'k', 'Sariq']),
        ('Variables', 'To\'q olovrang', ['Oq', 'Qora', 'Yashil']),
        ('Algoritm', 'Amallar ketma-ketligi', ['O\'yin', 'Dastur', 'Kompyuter']),
        ('Blok-sxema', 'Algoritmning grafik ko\'rinishi', ['Kod', 'Matn', 'Jadval']),
        ('Costume', 'Sprit ko\'rinishi (libosi)', ['Fon', 'Ovoz', 'Skript']),
        ('Background', 'Sahna foni', ['Sprit', 'Libos', 'Ovoz']),
        ('Green Flag', 'Dasturni ishga tushirish', ['To\'xtatish', 'Saqlash', 'O\'chirish']),
        ('Stop Sign', 'Dasturni to\'xtatish', ['Ishga tushirish', 'Saqlash', 'O\'chirish']),
        ('X va Y', 'Sprit koordinatalari', ['Rang va shakl', 'Ovoz va vaqt', 'Tezlik']),
    ]
    
    pool = []
    for item in items:
        pool.extend(generate_variations(item[0], item[1], item[2]))
    
    random.shuffle(pool)
    for q in pool:
        if len(questions) >= 200: break
        add_question_safe(questions, subject_id, grade, quarter, q[0], q[1], q[2])
    return questions

def generate_6th_grade_q4(subject_id):
    questions = []
    grade, quarter = 6, 4
    
    items = [
        ('URL', 'Veb-sahifa manzili', ['Ism', 'Parol', 'IP']),
        ('Giperhavola', 'Boshqa sahifaga o\'tish yo\'li', ['Rasm', 'Video', 'Musiqa']),
        ('Qidiruv tizimi', 'Ma\'lumot izlash sayti', ['O\'yin sayti', 'Chat', 'Forum']),
        ('Animatsiya', 'Obyektlar harakati', ['Rang', 'Fon', 'Matn']),
        ('Transition', 'Slayd almashish effekti', ['Ovoz', 'Video', 'Rasm']),
        ('Slayd', 'Taqdimot sahifasi', 'Word hujjati', 'Excel varag\'i', 'Rasm fayli'),
        ('PowerPoint', 'Taqdimot yaratish dasturi', 'Matn muharriri', 'Jadval', 'Brauzer'),
        ('F5', 'Namoyishni boshlash', 'Chiqish', 'Saqlash', 'O\'chirish'),
        ('Dizayn', 'Taqdimot bezagi', ['Fayl hajmi', 'Dastur kodi', 'Virus']),
        ('Title Slide', 'Sarlavha slaydi', ['Matnli slayd', 'Rasmli slayd', 'Bo\'sh slayd']),
        ('Content Slide', 'Mazmun slaydi', ['Sarlavha slaydi', 'Yakuniy slayd', 'Bo\'sh slayd']),
        ('Notes', 'Slayd uchun eslatmalar', ['Rasm', 'Video', 'Musiqa']),
        ('Video', 'Slaydga video qo\'shish', ['Matn', 'Rasm', 'Ovoz']),
        ('Audio', 'Slaydga ovoz qo\'shish', ['Matn', 'Rasm', 'Video']),
    ]
    
    pool = []
    for item in items:
        # Check if wrong options are list or single items (fix from before)
        wrongs = item[2] if isinstance(item[2], list) else [item[2], 'A', 'B'] 
        pool.extend(generate_variations(item[0], item[1], wrongs))
        
    random.shuffle(pool)
    for q in pool:
        if len(questions) >= 200: break
        add_question_safe(questions, subject_id, grade, quarter, q[0], q[1], q[2])
    return questions

def main():
    with app.app_context():
        print("Cleaning up...")
        Question.query.filter(Question.grade.in_([5, 6])).delete(synchronize_session=False)
        db.session.commit()
        
        subject = get_or_create_subject()
        all_questions = []
        
        funcs = [
            generate_5th_grade_q1, generate_5th_grade_q2, generate_5th_grade_q3, generate_5th_grade_q4,
            generate_6th_grade_q1, generate_6th_grade_q2, generate_6th_grade_q3, generate_6th_grade_q4
        ]
        
        for f in funcs:
            print(f"Running {f.__name__}...")
            all_questions.extend(f(subject.id))
        
        print(f"Total Unique Questions: {len(all_questions)}")
        
        counts = {}
        for q in all_questions:
            k = f"{q.grade}-{q.quarter}"
            counts[k] = counts.get(k, 0) + 1
        print("Counts:", counts)

        try:
            db.session.bulk_save_objects(all_questions)
            db.session.commit()
            print("Database updated!")
        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")

if __name__ == '__main__':
    main()
