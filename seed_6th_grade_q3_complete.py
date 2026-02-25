from app import app
from models import Question, Subject, ControlWork, db
import random

# ----- 6th Grade: Word, Excel, Scratch -----

standard_easy_medium_questions = [
    # Word (Easy/Medium)
    ("Word dasturida matnni 'Ko'chirish' (Cut) va 'Nusxalash' (Copy) amallarining asosiy farqi nimada?", "Cut asl joyidan o'chirib xotiraga oladi, Copy asl nusxani joyida qoldiradi", "Cut ham, Copy ham bir xil ishlaydi", "Copy faqat rasmlar uchun, Cut matnlar uchun ishlaydi", "Farqi yo'q", "A"),
    ("Word dasturida harflarni qanday qilib darajada yozish mumkin (Superscript, masalan x²)?", "Home -> x² tugmasi orqali", "Insert -> Symbol", "Page Layout -> Margins", "View -> Zoom", "A"),
    ("Word hujjatida jadvalning (Table) qatorlarini qanday o'chirish mumkin?", "Qatorni belgilab 'Delete Rows' ni tanlash", "Backspace tugmasini bir marta bosish", "Jadvalni kattalashtirish orqali", "Qatorga oq rang berish", "A"),
    ("Hujjat foniga rasm yoki suv belgisi (Watermark) o'rnatish Wordning qaysi menyusida joylashgan?", "Design (yoki Page Layout)", "Home", "Insert", "References", "A"),
    ("Matndagi bir xil so'zlarni boshqa so'zga yoppasiga almashtirish (Replace) yorlig'i qaysi?", "Ctrl + H", "Ctrl + F", "Ctrl + G", "Ctrl + R", "A"),
    ("Word da sahifa chegaralarini (Margins) o'zgartirish usuli qaysi menyudan bajariladi?", "Layout (Page Layout) -> Margins", "Insert -> Pictures", "View -> Ruler", "Home -> Paragraph", "A"),
    ("Matnni ustunlarga (Columns) bo'lish, masalan gazetalardagidek qilish, qayerdan bajariladi?", "Layout -> Columns", "Insert -> Text Box", "Design -> Page Color", "Home -> Styles", "A"),

    # Excel (Easy/Medium)
    ("Excelda bitta ustunni to'liq belgilash (Select Column) uchun qaysi klavishlar kombinatsiyasi bosiladi?", "Ctrl + Space", "Shift + Space", "Ctrl + A", "Shift + Enter", "A"),
    ("Excel katagidagi yozuvni o'zgartirish (tahrirlash) rejimi qaysi klavish bilan yoqiladi?", "F2", "F1", "F3", "F4", "A"),
    ("Excelda katakchalar birlashtirilib ichiga yozuv markazlashtirilishi qaysi tugma bilan bajariladi?", "Merge & Center", "Wrap Text", "Alignment", "Bold", "A"),
    ("Formula oxiridagi '=SUM(A1:A5)' da ikki nuqta (:) nimani bildiradi?", "A1 dan A5 gacha bo'lgan oraliqdagi barcha kataklarni", "Faqat A1 va A5 kataklarini", "A1 ni A5 ga bo'lishni", "Xatolikni", "A"),
    ("Hujjatda barcha manfiy sonlarni qizil rangda ko'rsatish (shartli formatlash) qayerdan bajariladi?", "Conditional Formatting", "Cell Styles", "Format as Table", "Font Color", "A"),
    ("Excel varaq (Sheet) nomini o'zgartirish qanday amalga oshiriladi?", "Varaq nomiga ikki marta tez bosish (Double click) orqali", "Fayl nomini o'zgartirish orqali", "Delete tugmasini bosish orqali", "Katakni kattalashtirib", "A"),
    ("Katakdagi sonni foiz (%) ko'rinishiga o'tkazish yorlig'i qaysi menyuda?", "Home -> Number", "Insert -> Symbols", "Data -> Filter", "Formulas -> Math", "A"),

    # Scratch (Easy/Medium)
    ("Scratch dasturlash tilida mushukcha (yoki boshqa qahramon) nima deb ataladi?", "Sprayt (Sprite)", "Kostyum (Costume)", "Obyekt (Object)", "Xarakter (Character)", "A"),
    ("Scratch dasturi loyihasining qanday qismlari 'Sahnaga' (Stage) tegishli?", "Faqat orqa fon (Backdrop) va umumiy skriptlar", "Barcha qahramonlar terisi", "Musiqalar papkasi", "Sichqoncha kursorining formasi", "A"),
    ("Qahramonni 10 qadam oldinga yurishini ta'minlovchi blok qanday rangda bo'ladi?", "Ko'k (Motion / Harakat)", "Sariq (Events / Voqealar)", "Siyohrang (Looks / Ko'rinish)", "Yashil (Operators)", "A"),
    ("Scratch dasturida loyihani ishga tushirish (Start) qaysi belgi orqali amalga oshiriladi?", "Yashil bayroqcha (Green Flag)", "Qizil tugma", "Probel (Space)", "Sariq yulduzcha", "A"),
    ("Scratchda bloklarni bir-biriga ulashda qanday xatolik bo'lishi mumkin?", "Bloklarning shakli bir-biriga tushmasa ulanmaydi, xato bermasdan sirpanib ketadi", "Kompyuter qotib qoladi", "Proramma o'chib ketadi", "Hamma bloklar baribir ulanadi", "A"),
    ("Qahramon nimanidir aytishi ('Salom!' deyishi) qaysi bo'lim (toifa) dan olinadi?", "Looks (Ko'rinish)", "Sound (Ovoz)", "Motion (Harakat)", "Sensing (Sezgi)", "A"),
    ("Scratchda qahramonning tashqi ko'rinishini o'zgartirish uchun qaysi menyu kerak?", "Costumes (Kostyumlar)", "Sounds (Ovozlar)", "Code (Kod)", "Variables (O'zgaruvchilar)", "A"),
    ("Sprayt yo'nalishini (Direction) teskariga qilish burilish burchagi qaysi?", "-90 daraja yoki Chap-O'ng aylanish rejimida g'ildirakni burish", "360 daraja", "0 daraja", "90 daraja", "A"),
    ("Scratch doirasidagi tsikl (qaytarilish) bloki 'Forever' qaysi bo'limda joylashgan?", "Control (Boshqaruv)", "Events (Voqealar)", "Motion (Harakat)", "Operators (Amallar)", "A"),
    ("Scratchda yangi spraytni qayerdan chizsa bo'ladi?", "'Paint' (Mo'yqalam) tugmasini bosish orqali", "Internetdan skachat qilib", "Worddan nusxa olib", "Kod yozuvlaridan", "A")
] * 3 # To artificially inflate standard counts for now, plus the unique below

standard_hard_questions = [
    # Word (Hard)
    ("Wordda uzun hujjat ichidagi ma'lum bir sarlavhaga tezkor havola (Cross-reference / Bookmark) qanday qilinadi?", "Insert -> Bookmark, keyin Hyperlink yoki Cross-reference orqali joylanadi", "Sahifa raqamini qizilga bo'yash orqali", "Faqat Mundarija (TOC) qilib qo'yish shart", "Wordda havola yaratib bo'lmaydi", "A"),
    ("Hujjatdagi ba'zi sahifalarni yotqizilgan (Landscape), qolganini tik (Portrait) ko'rinishida bitta fayl ichida saqlash mumkinmi?", "Ha, 'Section Break' (Bo'lim tanaffusi) orqali", "Yo'q, buning uchun alohida 2 ta fayl qilish kerak", "Ha, agar sahifa oxiriga cheksiz probel tashlansa", "Ha, faqat rasm qilib PDF ga otib", "A"),
    ("Faylni formatlanishi saqlanib turishi uchun matn shriftlarini (Embed fonts) to'g'ridan-to'g'ri hujjatning ichiga tikish parametrlari qayerda?", "File -> Options -> Save -> Embed fonts in the file", "Insert -> Symbol -> Embed", "Home -> Font", "Layout -> Text direction", "A"),

    # Excel (Hard)
    ("Keltirilgan '=IF(AND(A1>5, B1<10), 1, 0)' formulasi qachon 1 (True) natijasini beradi?", "Agar A1 5 dan katta VA B1 10 dan kichik bo'lsa (ikkisi ham bajarilganda)", "Agar A1 5 dan katta YOuKI B1 10 dan kichik bo'lsa", "Agar A1 faqat 5 ga teng bo'lsa", "Agar ikkisi ham teng bo'lsa", "A"),
    ("Excel Pivot Table (Yig'ma jadval) yaratishdan asosiy maqsad nima?", "Katta hajmdagi chalkash ma'lumotlarni turkumlash, saralash va tezkor analitik xulosalar yasash", "Faqat kataklarni chiroyli formatlash", "Kataklarga grafik chizish", "Jadval ustunlarini teskari o'girib qo'yish", "A"),
    ("'$B$3' o'zgarmas (absolyut) manzili qutilarni nusxalaganda 'C4' katagiga tushsa qanday o'zgaradi?", "U umuman o'zgarmaydi, '$B$3' ligicha qoladi", "U '$C$4' ga o'zgaradi", "U xatoga('#REF') aylanadi", "Faqat soni o'zgaradi '$B$4'", "A"),
    ("Matnlar uzunligini hisoblovchi 'LEN' funksiyasiga probellar (bo'sh joy) kiritiladimi?", "Ha, probel va tinish belgilari ham belgi sifatida sanaladi", "Yo'q, faqat harflar sanaladi", "Yo'q, faqat raqamlar sanaladi", "Probel xato ('ERROR') beradi", "A"),

    # Scratch (Hard)
    ("Scratchda 'X' va 'Y' koordinatalar o'qi bo'yicha markaz (sahnaning qoqo'rtasi) koordinatalari qanday?", "X: 0, Y: 0", "X: 240, Y: 180", "X: 100, Y: 100", "X: -240, Y: -180", "A"),
    ("Agar sprayt devorga tegib qaytishi kerak bo'lsa, qaysi blok to'g'ri keladi?", "If on edge, bounce (Agar chekkada bo'lsang, qayt)", "Point in direction 90", "Go to random position", "Move 10 steps", "A"),
    ("Scratchda mantiqiy 'OR' (Yoki) operatori qachon rost ('True') bo'ladi?", "Berilgan shartlarning bittasi bajarilsa kifoya", "Barcha shartlar birdaniga bajarilishi shart", "Hech qaysi shart bajarilmasa", "Faqat sonlar kiritilganda", "A"),
    ("Scratchda tasodifiy sonlarni generatsiya qilish (tanlash) vazifasi qaysi blokda amalga oshadi?", "Pick random () to () (Operators bo'limi)", "Set variable to ()", "Change variable by ()", "Move () steps", "A"),
    ("Tizimdagi timer(vaqt o'lchagich) ni qanday qilib noldan boshlash mumkin?", "Sensing -> 'Reset timer' bloki orqali", "Tizimni restart qilib", "Green Flag (Yashil bayroq) ni bosish orqali umuman bo'lmaydi", "Costumes qismidan", "A")
] * 2 # Increase pool artificially

situational_control_work_questions = [
    # Situational Logic (Word)
    ("Anvar o'z yozgan 20 bet kitobida 'Maktab' so'zini ko'p marta xato qilib 'Makdap' deb yozib qo'ygan ekan. Barchasini birdaniga to'g'rilash uchun 20 betni hammasini qarab chiqishi shartmi?", "Yo'q, Ctrl+H bosib 'Replace All' qilsa barchasi avtomatik 'Maktab'ga aylanadi.", "Ha, chunki Wordda birdaniga to'g'rilayotganlarni bilib bo'lmaydi.", "Yo'q, Ctrl+F bosib bitta-bitta qidirib topadi.", "Yo'q, kompyuterni qayta yoqsa tuzalib qoladi.", "A"),
    ("Odina word hujjatiga Internetdan matnni rasm qilib o'rab qo'ydi, endi rasmni orqasidan matn ko'rinib tursin (matn rasm orqasiga yozilsin) deb niyat qildi. Nimani bosishi kerak?", "Wrap Text -> Behind Text", "Wrap Text -> In Front of Text", "Wrap Text -> Top and Bottom", "Align -> Center", "A"),
    ("Farhod wordda matematik misollar yozmoqchi. Unga murakkab kasr chiziqlari, ildizlari kerak. Buni u klaviaturadan yoza olmayapti. U qaysi tugmaga murojaat qilsin?", "Insert -> Equation (Tenglama)", "Insert -> Symbol (Belgilar)", "Insert -> Text Box", "Home -> X2 (Superscript)", "A"),
    ("Malika kurs ishi yozyapti. Har bir sahifa oxirida muallif ismi va bet raqami chiqib turishi kerak. Har bir betga alohida pastga tushib yozib chiqmasligi uchun nima maslahat berasiz?", "Insert -> Footer (Pastki kolontitul) joylashni", "Insert -> Header (Yuqorigi kolontitul)", "Home -> Paragraph", "Pastki sozlami xatosiz Word o'zi qiladi deb kutishni", "A"),
    ("Dilmurod word hujjatida bitta gapni belgilagan holda klaviaturadagi Shift + F3 ni bossa nima hodisa ro'y beradi?", "Belgilangan gapdagi harflar turi (Katta/Kichik harflarga) avtomatik o'zgaradi (Change Case)", "Matn rangi o'zgaradi", "Word oyna yopilib qoladi", "Probellarni yashiradi", "A"),
    
    # Situational Logic (Excel)
    ("Asror ustoz 30 bola qatnashgan olimpiada natijalarini Excelda yig'ishdi. Endi eng kuchli (eng yuqori ball) olgan bolani ro'yxatning eng tepasiga chiqarib qo'ymoqchi. U jadvaldagi ballar degan ustunni qanday holatga o'tkazishi kerak?", "Sort -> Largest to Smallest (Kattadan kichikga saralash)", "Sort -> Smallest to Largest (A dan Z gacha)", "Filter orqali balandni qidirib ranglash", "AutoSum bosish orqali", "A"),
    ("Shahzodbek do'konga olingan mollar jadvallarini yuritmoqda. Ba'zida mahsulotning narxi va sonini ko'paytirmoqchi. Mahsulot soni B2 darchada, narxi esa C2 darchada tursa, Jami miqdorini darchaga qanday formula orqali hisoblatadi?", "=B2*C2", "=B2+C2", "=SUM(B2:C2)", "=B2/C2", "A"),
    ("Mubina excelda qizlarni oq rangda, o'g'il bolalarni esa ko'k rangda ko'rinib turishi uchun alohida jadvalni ranglamoqchi lekin bu juda qiyin. U jins ustuni bo'yicha orqa fonni avtomat qanday o'zgartirishi mumkin?", "Conditional Formatting -> Highlight Cells Rules ('Teng=' bo'lganda) dan orqali", "Home -> Fill Color qilib bitta-bitta bo'yab", "Format as Table (Avto Jadval) dan tasodifiy fonga aylantirib", "Excelda bunday funksiya avtomat mavjud emas", "A"),
    ("Jamshid excel jadvalida oynani pastga skroll qilib o'qiyotganda, yuqoridagi sarlavha qatorlari qochib, ko'rinmay qolyapti va nimani o'qiyotganini yo'qotib qo'yyapti. Sarlavhani bir joyda doim qotirib qo'yish uchun nima maslahat berasiz?", "View -> Freeze Panes (Kataklarni qotirish) funktsiyasini ishlatish", "Home -> Lock Cells qilish", "Jadvalni rasmga aylantirib o'qish", "Oynani kichiklashtirish (Zoom out)", "A"),
    ("Sevara ikkita ustunda A ustunda ism va B ustunda familiya yozilgan ro'yxatga ega. U C ustunga to'liq f.i.sh qilib Ism va Familiyani Excelda formulasiz qanday tez birlashtira oladi?", "Data -> Flash Fill yoki bittasini to'g'rila yozib 'Ctrl + E' bossa", "Data -> Remove Duplicates", "Formulalar shart: `=A1&B1` qilinadi", "Ikkisini bitta matnga yozib ctrl+c ctrl+v qilish kerak", "A"),

    # Situational Logic (Scratch)
    ("Oybekning scratchdagi mushugi (sprayt) devorga yurganda urilib turavermasdan orqaga qaytishi kerak. Lekin u qaytganida boshi bilan teskari tushib qolyapti (tepasi pastda). Buni qanday qilib chap-o'ng bo'lib buriladigan qilish mumkin?", "'Direction' xossasidan -> 'Left/Right' burilish rejimini faollashtirib", "Mushukni o'chirib yangidan yasab orqali", "Moves bloki o'rniga X ni o'zgartirish ulab", "Yashil bayroqchani bosmaslik", "A"),
    ("Shodiyona sprayt klaviatura tugmasi (masalan Space probel) bosilganda sakrashini xohlamoqda. Buning uchun u qaysi sariq rangli Voqealar blokidan boshlashi kerak kodini?", "'When [space] key pressed' blokidan", "'When Green Flag clicked' blokidan", "'Forever' blokidan", "'Wait 1 second' blokidan", "A"),
    ("Jalolning o'yinida ayiq qahramoni tez yugurib ketishi kerak emas, u sekin yuryapman deb ko'rsatishi (oyog'i qimirlashi) uchun kostyumlarni o'zgartirib turishi kerak. Har bir qadam o'rtasiga nima kod qoyishi kerakki o'zgarish sezilsin?", "'Wait 1 seconds' yoki ms qiymat qo'yib kutish blokini", "'Stop all' blokini", "'Turn 15 degrees' blokini", "Oddiy 'Next Costume' qilsa o'zi sekinlaydi", "A"),
    ("Umidaning qahramoni olma terishi kerak. Olmani terganda ball qo'shilib borishi uchun Scratchda nima degan quti kashf qilish kerak?", "Make a Variable (O'zgaruvchi yaratish) - masalan 'Ball' degan", "Make a Block (Blok yaratish)", "Broadcast message", "Yangi Sprite yaratish", "A"),
    ("Rustam mushuk sirtmoq (Labyrinth) o'ynini yozdi. Mushuk devorga (qora rangga) tegsa o'yin boshiga qaytishi kerakligi uchun qaysi sezgi (Sensing) bloki shartga qo'yiladi?", "Touching color [qora] ? (Qora rangga tegdimi?)", "Distance to [devor] ?", "Key [up arrow] pressed?", "Mouse down?", "A")
] * 2  # Pool to get exactly 30 logic questions total in the randomized pool


def re_seed():
    with app.app_context():
        # Get subjects
        subj = Subject.query.filter_by(name="Informatika").first()
        if not subj:
            subj = Subject(name="Informatika", grades="5,6")
            db.session.add(subj)
            db.session.commit()
            
        subject_id = subj.id
        
        # 1. DELETE EXISTING QUESTIONS AND CW (Clean Slate)
        old_questions = Question.query.filter_by(grade=6, quarter=3).all()
        for q in old_questions:
            db.session.delete(q)
            
        old_cw = ControlWork.query.filter_by(grade=6, quarter=3).first()
        if old_cw:
            db.session.delete(old_cw)
            
        db.session.commit()
        print(f"Old 6th grade Q3 data wiped ({len(old_questions)} questions, old Control Work).")
        
        # 2. SEED ALL QUESTIONS INTO THE DATABASE POOL
        # Prepare mixed pool
        all_new_qs = standard_easy_medium_questions + standard_hard_questions + situational_control_work_questions
        # Make them distinct just in case
        unique_q_texts = set()
        final_questions_to_add = []
        
        for idx, item in enumerate(all_new_qs):
            q_text, a, b, c, d, correct = item
            if q_text in unique_q_texts:
                continue
            unique_q_texts.add(q_text)
            
            # Difficulty mapping
            difficulty = 2 # default Medium
            if item in standard_hard_questions or "Control Work" in getattr(item, 'metadata_desc', ''):
                difficulty = 3
            if item in standard_easy_medium_questions and idx % 2 == 0:
                difficulty = 1 # easy
                
            # determine logic type
            is_logic = (item in situational_control_work_questions)
            if is_logic:
                difficulty = 3
            
            # Shuffling options
            options = [(a, "A"), (b, "B"), (c, "C"), (d, "D")]
            random.shuffle(options)
            real_correct = ""
            for i, opt in enumerate(options):
                if opt[1] == correct:
                    real_correct = ["A", "B", "C", "D"][i]
                    break
                    
            question = Question(
                subject_id=subject_id,
                grade=6,
                quarter=3,
                difficulty=difficulty,
                question_text=q_text,
                option_a=options[0][0],
                option_b=options[1][0],
                option_c=options[2][0],
                option_d=options[3][0],
                correct_answer=real_correct,
            )
            db.session.add(question)
            final_questions_to_add.append((question, is_logic))
            
        db.session.commit()
        print(f"Barcha savollar ({len(final_questions_to_add)} ta noyob savollar) bazaga muvaffaqiyatli saqlandi. Word/Excel/Scratch!")

        # 3. CREATE CONTROL WORK
        new_cw = ControlWork(
            title="6-sinf Informatika 3-chorak Nazorat ishi",
            subject_id=subject_id,
            grade=6,
            quarter=3,
            time_limit=45,
            is_active=True
        )
        db.session.add(new_cw)
        db.session.commit()
        
        # 4. MIX QUESTIONS FOR CONTROL WORK (105+ randomized setup)
        logic_qs = [q[0] for q in final_questions_to_add if q[1] == True]
        standard_qs = [q[0] for q in final_questions_to_add if q[1] == False]
        
        for q in logic_qs:
            new_cw.questions.append(q)
            
        remaining_pool = list(standard_qs)
        random.shuffle(remaining_pool)
        
        needed = 105 - len(logic_qs)
        if needed > len(remaining_pool):
            needed = len(remaining_pool)
            
        for q in remaining_pool[:needed]:
            new_cw.questions.append(q)
            
        db.session.commit()
        print(f"Maxsus Nazorat Ishi muvaffaqiyatli yaratildi (Savollar soni: {len(new_cw.questions)}ta - Random & Logic аралашган).")

if __name__ == "__main__":
    re_seed()
