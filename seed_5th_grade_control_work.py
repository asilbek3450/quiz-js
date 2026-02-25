from app import app
from models import Question, Subject, ControlWork, db
import random

situational_questions = [
    # 1-5 MS Word Logical/Situational
    ("Aziza do'stiga xat yozayotib, o'z ismini juda chiroyli va qalin (yaqqol ko'rinib turadigan) qilib yozmoqchi. U buning uchun matnni belgilab qaysi tugmani bosishi kerak?", "Bold (B)", "Italic (I)", "Underline (U)", "Strikethrough (ab)", "A"),
    ("Sarvar ingliz tili darsiga matn tayyorlamoqda. U matn ichidagi hamma so'zlarni o'yin uchun qizil rangga bo'yamoqchi. U Wordning qaysi joyidan rangni o'zgartiradi?", "Font Color (Harf rangi)", "Highlight (Fonga rang berish)", "Page Color (Sahifa rangi)", "WordArt", "A"),
    ("Ali ertak yozayotib noto'g'ri so'z yozib yubordi va xatosini endi ko'rdi. U shu xato so'zni o'chirib, o'rniga boshqasini yozishdan oldin oxirgi amalini bekor qilmoqchi. Qaysi tezkor yorliq unga yordam beradi?", "Ctrl + Z", "Ctrl + C", "Ctrl + Y", "Ctrl + S", "A"),
    ("Dildora yozgan matni juda chiroyli chiqdi va endi uni qog'ozda ko'rmoqchi (chop etmoqchi). U Word dasturiga qanday buyruq beradi?", "Print (Ctrl+P)", "Save (Ctrl+S)", "Open (Ctrl+O)", "Copy (Ctrl+C)", "A"),
    ("O'qituvchi o'quvchilarga maqola yozishni topshirdi va sarlavhani aynan o'rtaga joylashtirishni so'radi. Doston sarlavhani o'rtaga keltirish uchun klaviaturadan qaysi yorliqni bosa qolgani ma'qul?", "Ctrl + E", "Ctrl + L", "Ctrl + R", "Ctrl + J", "A"),

    # 6-10 Excel Logical/Situational
    ("Sinfingizdagi 5 ta o'quvchining baholarini Excelda tez qo'shmoqchisiz (Yig'indi). Qaysi tugma sizga eng tez yordam beradi?", "AutoSum (Avtosumma)", "Sort (Saralash)", "Filter (Filtr)", "Find (Qidirish)", "A"),
    ("Malika Excel jadvalida butun sinfning bo'yi uzunligini yozib chiqdi. Endi u bolalar orasidan bo'yi eng baland (eng katta qiymat) o'quvchini qidirish o'rniga qaysi formuladan foydalangani yaxshi?", "=MAX()", "=MIN()", "=SUM()", "=AVERAGE()", "A"),
    ("Hasan do'konga borib sotib olgan narsalarining narxini Excelga kiritmoqda. U narxlarni yozgan ustunning kengligi yetmay, ichidagi sonlar '#' belgisiga aylanib qoldi. Buni qanday to'g'rilaydi?", "Ustunni chegarasidan ushlab kattalashtiradi", "Harflar o'lchamini kichiklashtirmaydi, kompyuterni o'chirib yoqadi", "Hujjatni qaytadan yaratadi", "Matnni qizil rangga bo'yaydi", "A"),
    ("Oybek ukasining yoshlarini (4 va 6) qatorlarga yozib qo'ydi. Shu ikkita sonning o'rtachasini (AVERAGE) qanday formulada topadi?", "=AVERAGE(A1:A2)", "=SUM(A1:A2)", "=MAX(A1:A2)", "=MIN(A1:A2)", "A"),
    ("Zilola jadvaldagi 10 ta o'rtoqlarining ismini alifbo tartibida (A dan Z gacha) taxlamoqchi. Buning uchun u qanday usuldan foydalanishi kerak?", "Sort (Saralash)", "Format Painter (Format nusxalash)", "Find (Qidirish)", "Replace (Almashtirish)", "A"),

    # 11-15 General Workarounds & Shortcuts Logical
    ("Kompyuterda qiziqarli rasm ko'rib qoldingiz va uni Wordga olmoqchisiz. Buning uchun qaysi ikkita ketma-ket yorliqdan foydalanasiz? (Nusxa olish va Joylash)", "Ctrl + C va Ctrl + V", "Ctrl + X va Ctrl + V", "Ctrl + Z va Ctrl + C", "Ctrl + S va Ctrl + P", "A"),
    ("Nodir uyga vazifasini qilib bo'ldi, lekin hojatxonaga chiqib kelmoqchi. Akasi kompyuterni titganini xohlamaydi. U ishini saqlab, kompyuterni tezda qulflashi uchun nima bosadi?", "Win + L", "Win + D", "Alt + F4", "Win + E", "A"),
    ("Madina kompyuterda ko'p oyna ochib yubordi. Onasi xonaga kirayotganda, barcha oynalarni yashirib darhol ish stolini (Desktop) ko'rsatmoqchi. U klaviaturadan nimani bosadi?", "Win + D", "Alt + Tab", "Ctrl + Esc", "Win + R", "A"),
    ("Internetda ma’lumot o‘qiyapsiz, lekin u xato ko‘rinyapti. Sahifani qayta yuklash (yangilash) uchun qaysi tezkor klavish yordam beradi?", "F5", "F1", "F2", "F4", "A"),
    ("Jasur papka ichidagi 'Yangi hujjat' degan faylning nomini o'zgaritmoqchi. Faylni o'ng tugma bilan bosib 'Rename' qilish o'rniga qaysi tugmani bosa qolsa tezroq bo'ladi?", "F2", "F5", "F1", "F12", "A"),

    # 16-20 Logical Flow / Scenarios
    ("Iroda 10 betlik matnni yozib bo'ldi. Endi u hujjat ichidan o'zining ismini tezda topmoqchi. Matnni boshdan oxirigacha o'qib chiqish o'rniga qaysi menyudan foydalansa bo'ladi?", "Find (Qidirish)", "Replace (Almashtirish)", "Select All (Hammasini belgilash)", "Translate (Tarjima)", "A"),
    ("Shavkat bitta faylni Papkaga qo'yganini unutib qo'ydi, endi butun kompyuterdan qidirishi kerak. Bunga eng to'g'ri bo'lgan Word vositasi qaysi?", "Kompyuter qidiruv tizimidan foydalanish (Win + S)", "Hoshimlarga Word orqali yozib jo'natish", "Yangi kompyuter sotib olish", "Fayllarni birma bir titish", "A"),
    ("Zuhra onasini rasmiga matn yozmoqchi. U rasmning o'rtasiga matn joylashtiradigan maxsus shakl chizib (masalan to'rtburchak qilib) uning orqasini oq rangsiz qilish siri nimada?", "Shape Fill -> No Fill", "Outline -> No Outline", "Text Color -> White", "Shadow -> None", "A"),
    ("Azizjon MS Word dasturini ochganda qatorlar oralig'i (Line spacing) juda katta ekanini sezdi. Matn bir-biriga yaqin va chiroyli bo'lishi uchun intervallarni qanday qisqartiradi?", "Line and Paragraph Spacing tugmasi orqali (1.0 yoki 1.15)", "Harflar o'lchamini kattalashtiradi", "Shriftlarni Arial'dan Calibri'ga o'zgartiradi", "Format Painter qiladi", "A"),
    ("Temur qog'ozni printerda gorizontal (keng) shaklda chiqarmoqchi, chunki chizgan jadvali keng joy olyapti. U qog'oz holatini (Orientation) qanday targa o'zgartirishi kerak?", "Landscape (Albom shakli)", "Portrait (Kitob shakli)", "A4 hajmidan A5 hajmigacha", "Margins -> Narrow", "A")
]

def create_control_work():
    with app.app_context():
        # Get Informatica subject
        subject = Subject.query.filter_by(name="Informatika").first()
        if not subject:
            print("Informatika fani topilmadi.")
            return
            
        subject_id = subject.id
        
        # Checking if control work for grade 5 Q 3 already exists
        cw = ControlWork.query.filter_by(grade=5, quarter=3).first()
        if cw:
            print(f"5-sinf 3-chorak uchun '{cw.title}' nomli nazorat ishi allaqachon mavjud. Uni o'chiryapman...")
            db.session.delete(cw)
            db.session.commit()
            
        print("Yangi vaziyatli/mantiqiy savollar kiritilmoqda...")
        added_questions = []
        for data in situational_questions:
            q_text, a, b, c, d, correct = data
            
            # Shuffling options
            options = [(a, "A"), (b, "B"), (c, "C"), (d, "D")]
            random.shuffle(options)
            
            new_opt_a = options[0][0]
            new_opt_b = options[1][0]
            new_opt_c = options[2][0]
            new_opt_d = options[3][0]
            
            real_correct = ""
            for i, opt in enumerate(options):
                if opt[1] == correct:
                    real_correct = ["A", "B", "C", "D"][i]
                    break
                    
            question = Question(
                subject_id=subject_id,
                grade=5,
                quarter=3,
                difficulty=2, # Medium mapping for situational
                question_text=q_text,
                option_a=new_opt_a,
                option_b=new_opt_b,
                option_c=new_opt_c,
                option_d=new_opt_d,
                correct_answer=real_correct,
                lesson=None
            )
            db.session.add(question)
            added_questions.append(question)
            
        db.session.commit()
        print(f"{len(added_questions)} ta savol bazaga yuklandi.")
        
        # Create control work
        new_cw = ControlWork(
            title="5-sinf Informatika 3-chorak Nazorat ishi",
            subject_id=subject_id,
            grade=5,
            quarter=3,
            time_limit=45,
            is_active=True
        )
        
        # Link questions to the control work
        for q in added_questions:
            new_cw.questions.append(q)
            
        db.session.add(new_cw)
        db.session.commit()
        print("Muvaffaqiyatli! Mantiqiy savollardan iborat Nazorat of ishi yaratildi va savollar unga ulandi.")

if __name__ == "__main__":
    create_control_work()
