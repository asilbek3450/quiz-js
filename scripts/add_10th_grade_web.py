import sys
import os
import random
import json

# Add parent directory to path to import app and models
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from models import Question, Subject

# TRACKING
SEEN_QUESTIONS = set()

def get_or_create_subject(name, grades):
    subject = Subject.query.filter_by(name=name).first()
    if not subject:
        subject = Subject(name=name, name_ru=name, name_en=name, grades=grades)
        db.session.add(subject)
        db.session.commit()
    return subject

def add_question_safe(questions_list, subject_id, grade, quarter, q_text, opts, ans):
    global SEEN_QUESTIONS
    if q_text in SEEN_QUESTIONS:
        return False
    
    # Shuffle options
    final_opts = list(set(opts))
    if len(final_opts) < 4:
        # Pad with dummy wrong answers if needed
        dummies = ["Brauzerni yopish", "Xatolikni ko'rsatish", "Rangni o'chirish", "Hamma javob to'g'ri"]
        for d in dummies:
            if d not in final_opts:
                final_opts.append(d)
                if len(final_opts) == 4: break
    
    final_opts = final_opts[:4]
    random.shuffle(final_opts)
    
    if ans not in final_opts:
        # Ensure answer is included
        final_opts[0] = ans
        random.shuffle(final_opts)
    
    correct_char = ['A', 'B', 'C', 'D'][final_opts.index(ans)]
    
    q = Question(
        subject_id=subject_id,
        grade=grade,
        quarter=quarter,
        question_text=q_text,
        option_a=str(final_opts[0]),
        option_b=str(final_opts[1]),
        option_c=str(final_opts[2]),
        option_d=str(final_opts[3]),
        correct_answer=correct_char
    )
    questions_list.append(q)
    SEEN_QUESTIONS.add(q_text)
    return True

# --- HTML DATA ---
HTML_POOLS = {
    1: [
        ("<h1>-<h6>", "Sarlavhalar (Header)"), ("<p>", "Paragraf"), ("<br>", "Qatorga tushish"),
        ("<hr>", "Gorizontal chiziq"), ("<b>", "Qalin matn"), ("<i>", "Kursiv matn"),
        ("<u>", "Tagiga chizilgan matn"), ("<strong>", "Muhim qalin matn"), ("<em>", "Urg'uli matn"),
        ("<ul>", "Tartibsiz ro'yxat"), ("<ol>", "Tartibli ro'yxat"), ("<li>", "Ro'yxat elementi"),
        ("<html>", "Hujjatning asosi"), ("<head>", "Meta-ma'lumotlar qismi"), ("<body>", "Asosiy mazmun qismi"),
        ("<title>", "Veb-sahifa nomi"), ("<!-- -->", "Izoh (Comment)"), ("<address>", "Aloqa ma'lumotlari"),
        ("<blockquote>", "Boshqa manbadan iqtibos"), ("<cite>", "Asar nomi"), ("<code>", "Dastur kodi matni"),
        ("<pre>", "Formatlangan matn"), ("<sub>", "Pastki indeks"), ("<sup>", "Yuqori indeks")
    ],
    2: [
        ("<a>", "Havola yaratish"), ("href", "Havola manzili"), ("target='_blank'", "Yangi oynada ochish"),
        ("<img>", "Rasm joylashtirish"), ("src", "Manba (URL)"), ("alt", "Muqobil matn"),
        ("width", "Kenglik"), ("height", "Balandlik"), ("<table>", "Jadval"), 
        ("<tr>", "Jadval qatori"), ("<td>", "Jadval katagi"), ("<th>", "Sarlavha katagi"),
        ("<thead>", "Jadval tepasi"), ("<tbody>", "Jadval tanasi"), ("<tfoot>", "Jadval pasti"),
        ("<caption", "Jadval nomi"), ("colspan", "Ustunlarni birlashtirish"), ("rowspan", "Qatorlarni birlashtirish")
    ],
    3: [
        ("<form>", "Ma'lumot yig'ish formasi"), ("<input>", "Kiritish maydoni"), ("type='text'", "Matnli maydon"),
        ("type='password'", "Parol maydoni"), ("type='checkbox'", "Bayroqcha (ko'p tanlov)"), 
        ("type='radio'", "Radio tugma (yakka tanlov)"), ("type='submit'", "Yuborish tugmasi"),
        ("<label>", "Element nomi"), ("<select>", "Ochiluvchi ro'yxat"), ("<option>", "Ro'yxat varianti"),
        ("<textarea>", "Ko'p qatorli matn"), ("placeholder", "Maslahat matni"), ("name", "Element nomi (serverga)"),
        ("value", "Element qiymati"), ("required", "Majburiy maydon"), ("readonly", "Faqat o'qish uchun")
    ],
    4: [
        ("<video>", "Video qo'yish"), ("<audio>", "Audio qo'yish"), ("<source>", "Media manbasi"),
        ("controls", "Boshqaruv tugmalari"), ("autoplay", "Avtomatik ijro"), ("loop", "Takroriy ijro"),
        ("<iframe>", "Ichki oyna"), ("<nav>", "Navigatsiya"), ("<header>", "Yuqori qism"),
        ("<footer>", "Pastki qism"), ("<section>", "Bo'lim"), ("<article>", "Maqola"),
        ("<aside>", "Yon qism"), ("<meta>", "Metadata (SEO uchun)"), ("charset='UTF-8'", "Belgilar kodi")
    ]
}

# --- CSS DATA ---
CSS_POOLS = {
    1: [
        ("color", "Matn rangi"), ("background-color", "Fon rangi"), ("font-size", "Shrift o'lchami"),
        ("font-family", "Shrift turi"), ("text-align", "Matnni tekislash"), ("font-weight", "Shrift qalinligi"),
        ("selector", "CSS qoidasi tanlovchisi"), (".", "Klass selektori (.class)"), ("#", "ID selektori (#id)"),
        ("line-height", "Qatorlar orasi masofasi"), ("text-transform", "Harflar katta-kichikligi"),
        ("background-image", "Fon rasmi"), ("text-decoration", "Matn bezagi (ostiga chizish)"),
        ("inline CSS", "style atributi orqali"), ("internal CSS", "<style> tegi orqali"),
        ("external CSS", ".css fayl orqali")
    ],
    2: [
        ("padding", "Ichki bo'shliq"), ("margin", "Tashqi bo'shliq"), ("border", "Chegara"),
        ("width", "Kenglik"), ("height", "Balandlik"), ("box-sizing", "Box modelini hisoblash usuli"),
        ("border-radius", "Burchaklarni yumaloqlash"), ("border-style", "Chegara turi (solid, dashed)"),
        ("margin-left: auto", "Elementni o'ngga surish (markazlash uchun)"), ("list-style", "Ro'yxat uslubi"),
        ("outline", "Element tashqi chegarasi"), ("cursor", "Sichqoncha ko'rinishi"),
        ("display: inline", "Yonma-yon joylashish"), ("display: block", "Qatorni to'liq egallash")
    ],
    3: [
        ("position: relative", "O'z joyiga nisbatan"), ("position: absolute", "Ota elementga nisbatan"),
        ("position: fixed", "Ekran oynasiga nisbatan"), ("position: sticky", "Yopishqoq holat"),
        ("z-index", "Qatlamlar tartibi"), ("overflow", "Mazmun ortib ketishi (scroll)"),
        ("float", "Elementni yon tomonga surish"), ("clear", "Float ta'sirini bekor qilish"),
        ("display: none", "Elementni mutlaqo yashirish"), ("visibility: hidden", "Yashirish (joyi saqlanadi)"),
        ("opacity", "Shaffoflik darajasi"), ("vertical-align", "Vertikal tekislash")
    ],
    4: [
        ("display: flex", "Flexbox konteyneri"), ("flex-direction", "Yo'nalish (row/column)"),
        ("justify-content", "Asosiy o'q tekislashi"), ("align-items", "Kesishgan o'q tekislashi"),
        ("display: grid", "To'rli (Grid) joylashuv"), ("grid-template-columns", "Ustunlar o'lchami"),
        ("@media", "Media so'rovlar (Responsive)"), ("transition", "Silliq o'tish effekti"),
        ("animation", "Harakatli animatsiyalar"), ("@keyframes", "Animatsiya bosqichlari"),
        ("box-shadow", "Ko'lka berish"), ("--var", "CSS o'zgaruvchisi"), ("calc()", "Hisob-kitob qilish")
    ]
}

def generate_questions(subject_id, grade, quarter, pool):
    questions_list = []
    
    # 1. Simple Definition Questions (using each item once)
    for tag, desc in pool:
        templates = [
            f"HTML/CSSda {tag} nima vazifani bajaradi?",
            f"Quyidagilardan qaysi biri {desc} uchun ishlatiladi?",
            f"Sahifada {desc}ni amalga oshirish uchun qaysi {('teg' if 'HTML' in str(subject_id) else 'xususiyat')} qo'llaniladi?"
        ]
        q_text = random.choice(templates)
        if "qaysi biri" in q_text:
            ans = tag
            wrongs = [p[0] for p in pool if p[0] != tag]
        else:
            ans = desc
            wrongs = [p[1] for p in pool if p[1] != desc]
        
        add_question_safe(questions_list, subject_id, grade, quarter, q_text, [ans] + random.sample(wrongs, 3), ans)

    # 2. Combined Questions (Picking 2 items)
    attempts = 0
    while len(questions_list) < 100 and attempts < 1000:
        attempts += 1
        item1, item2 = random.sample(pool, 2)
        q_text = f"HTML/CSSda {item1[0]} va {item2[0]} ning to'g'ri vazifalarini ko'rsating."
        ans = f"{item1[1]} va {item2[1]}"
        
        # Wrong answers by mixing
        wrong_pool = [f"{p1[1]} va {p2[1]}" for p1, p2 in [random.sample(pool, 2) for _ in range(3)] if f"{p1[1]} va {p2[1]}" != ans]
        if len(wrong_pool) < 3: continue
        
        add_question_safe(questions_list, subject_id, grade, quarter, q_text, [ans] + wrong_pool, ans)

    # 3. Code Snippet Style
    while len(questions_list) < 100 and attempts < 2000:
        attempts += 1
        item = random.choice(pool)
        if 'HTML' in str(subject_id): # Actually check subject type differently or just allow both
            q_text = f"Ushbu kod parchasida nima sodir bo'ladi?\n\n`{item[0]}`"
        else:
            q_text = f"CSSda `{item[0]}` xususiyati nimani boshqaradi?"
        
        ans = item[1]
        wrongs = random.sample([p[1] for p in pool if p[1] != ans], 3)
        add_question_safe(questions_list, subject_id, grade, quarter, q_text, [ans] + wrongs, ans)

    return questions_list[:100]

def main():
    app = create_app()
    with app.app_context():
        # Clean up existing grade 10 questions to ensure fresh start
        print("Cleaning up existing grade 10 questions...")
        Question.query.filter_by(grade=10).delete()
        db.session.commit()

        # Subjects
        html_subject = get_or_create_subject("HTML", "10")
        css_subject = get_or_create_subject("CSS", "10")
        
        all_new_qs = []
        
        for q in [1, 2, 3, 4]:
            print(f"Generating HTML Q{q}...")
            all_new_qs.extend(generate_questions(html_subject.id, 10, q, HTML_POOLS[q]))
            print(f"Generating CSS Q{q}...")
            all_new_qs.extend(generate_questions(css_subject.id, 10, q, CSS_POOLS[q]))

        print(f"Total Unique Questions generated: {len(all_new_qs)}")
        
        for q in all_new_qs:
            db.session.add(q)
            
        db.session.commit()
        print("Success! 800 UNIQUE questions added for 10th Grade HTML & CSS.")

if __name__ == "__main__":
    main()
