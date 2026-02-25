from app import app
from models import Question, Subject, db
import random

easy_medium_questions = [
    # Word (Easy/Medium)
    ("MS Word qanday dasturlar sirasiga kiradi?", "Matn muharriri", "Jadval muharriri", "Grafik muharriri", "Operatsion tizim", "A"),
    ("MS Word hujjatining kengaytmasi nima?", ".docx", ".xlsx", ".pptx", ".txt", "A"),
    ("Matnni qalin (bold) qilish uchun qaysi tugmalar majmuasi bosiladi?", "Ctrl + B", "Ctrl + I", "Ctrl + U", "Ctrl + C", "A"),
    ("Matnni nusxalash usuli qaysi?", "Ctrl + C", "Ctrl + X", "Ctrl + V", "Ctrl + Z", "A"),
    ("Nusxa olingan matnni joylashtirish (paste) uchun qaysi tugma bosiladi?", "Ctrl + V", "Ctrl + P", "Ctrl + X", "Ctrl + C", "A"),
    ("Matnni og'ma (italic) qilish tugmasi qaysi?", "Ctrl + I", "Ctrl + B", "Ctrl + U", "Ctrl + S", "A"),
    ("Faylni saqlash uchun qaysi yorliq bosiladi?", "Ctrl + S", "Ctrl + O", "Ctrl + N", "Ctrl + P", "A"),
    ("Hujjatni chop etish (print) qaysi komanda orqali bajariladi?", "Ctrl + P", "Ctrl + C", "Ctrl + V", "Ctrl + S", "A"),
    ("Yangi Word hujjatini ochish yorlig'i qaysi?", "Ctrl + N", "Ctrl + M", "Ctrl + O", "Ctrl + W", "A"),
    ("Hujjat ichidan so'z qidirish qaysi tugma bilan bajariladi?", "Ctrl + F", "Ctrl + H", "Ctrl + G", "Ctrl + D", "A"),
    ("Oxirgi amalni bekor qilish (Undo) qaysi klavish orqali bajariladi?", "Ctrl + Z", "Ctrl + Y", "Ctrl + X", "Ctrl + C", "A"),
    ("MS Word da sahifa parametrlari qaysi menyuda joylashgan?", "Page Layout (Layout)", "Home", "Insert", "View", "A"),
    ("Jadval qo'shish qaysi menyudan amalga oshiriladi?", "Insert -> Table", "Home -> Table", "Design -> Table", "View -> Table", "A"),
    ("Matnni o'rta (Center) tekislaydigan klaviatura yorlig'i qaysi?", "Ctrl + E", "Ctrl + L", "Ctrl + R", "Ctrl + J", "A"),
    ("Matnni ikki tomondan to'liq tekislash (Justify) qaysi klaviatura yorlig'i bilan bajariladi?", "Ctrl + J", "Ctrl + F", "Ctrl + H", "Ctrl + T", "A"),
    ("Rasm qo'shish qaysi menyu orqali qilinadi?", "Insert -> Pictures", "Home -> Pictures", "Layout -> Pictures", "Design -> Pictures", "A"),

    # Excel (Easy/Medium)
    ("MS Excel qanday dasturlar sirasiga kiradi?", "Jadval muharriri", "Matn muharriri", "Taqdimot yaratuvchi", "Ma'lumotlar bazasi", "A"),
    ("Excel faylining kengaytmasi nima?", ".xlsx", ".docx", ".pdf", ".txt", "A"),
    ("Excelda ustunlar nima bilan belgilanadi?", "Lotin harflari (A, B, C...)", "Arab raqamlari (1, 2, 3...)", "Rim raqamlari", "Simvollar", "A"),
    ("Excelda qatorlar nima bilan belgilanadi?", "Raqamlar bilan", "Harflar bilan", "Ranglar bilan", "Shakllar bilan", "A"),
    ("Excel katagi nima deb ataladi?", "Qator va ustun kesishgan joy", "Faqat qator", "Faqat ustun", "Sahifa nomi", "A"),
    ("Excelda formula qaysi belgi bilan boshlanadi?", "= (tenglik)", "+ (qo'shish)", "* (ko'paytirish)", "/ (bo'lish)", "A"),
    ("Yig'indini hisoblash formulasi qaysi?", "SUM", "AVERAGE", "MIN", "MAX", "A"),
    ("Eng katta qiymatni topuvchi funksiya?", "MAX", "MIN", "SUM", "COUNT", "A"),
    ("Eng kichik qiymatni topuvchi funksiya?", "MIN", "MAX", "SUM", "COUNT", "A"),
    ("O'rtacha qiymatni hisoblovchi funksiya qaysi?", "AVERAGE", "SUM", "COUNT", "IF", "A"),
    ("Hujjatdagi barcha narsani belgilash (Select All) klaviatura yorlig'i:", "Ctrl + A", "Ctrl + S", "Ctrl + D", "Ctrl + F", "A"),

    # Shortcuts (Easy/Medium)
    ("Kompyuterni qulflash uchun qaysi klaviatura yorlig'idan foydalaniladi?", "Win + L", "Win + D", "Win + E", "Win + R", "A"),
    ("Ochilgan barcha oynalarni yashirib, ish stolini ko'rsatish (Show Desktop) klaviatura yorlig'i?", "Win + D", "Win + M", "Win + L", "Win + Tab", "A"),
    ("Tizimning 'Task Manager' (Vazifalar dispetcheri) ni ochish yorlig'i qaysi?", "Ctrl + Shift + Esc", "Ctrl + Alt + Del", "Alt + F4", "Win + X", "A"),
    ("Joriy oynani yopish klaviatura yorlig'i qaysi?", "Alt + F4", "Ctrl + W", "Win + D", "Alt + Tab", "A"),
    ("Faylni qayta nomlash (Rename) uchun qaysi tugma bosiladi?", "F2", "F3", "F4", "F5", "A"),
    ("Sahifani yoki oynani yangilash (Refresh) uchun qaysi klavish bosiladi?", "F5", "F2", "F1", "F12", "A"),
    ("'Saqlash' (Save As) darchasini ochish uchun Word'da qaysi klavish bosiladi?", "F12", "F1", "F2", "F10", "A"),
    ("Qidiruv oynasini ochish (Brauzerda va fayllarda) yorlig'i qaysi?", "Ctrl + F", "Ctrl + S", "Ctrl + O", "Ctrl + E", "A"),
    ("Yordam (Help) oynasini chaqirish tugmasi qaysi?", "F1", "F2", "F3", "F4", "A"),
    ("Hujjatning eng boshiga tez qaytish klaviatura yorlig'i?", "Ctrl + Home", "Ctrl + End", "Home", "Page Up", "A"),
    ("Hujjatning eng oxiriga tushish klaviatura yorlig'i?", "Ctrl + End", "Ctrl + Home", "End", "Page Down", "A"),
    ("Dasturlar orasida tezgina o'tish (Switch) qaysi klaviatr orqali qilinadi?", "Alt + Tab", "Ctrl + Tab", "Win + Tab", "Shift + Tab", "A"),
    ("Bitta so'zni to'liq belgilash (tanlash) uchun nima qilinadi?", "So'z ustiga ikki marta tez bosiladi (Double click)", "Sichqonchani bir marta bosish", "Ctrl ni bosib turish", "O'ng tugmani bosish", "A"),
    ("To'liq bitta abzasni belgilash uchun sichqoncha bilan nima qilinadi?", "Abzas ustiga uch marta tez bosiladi", "Ikki marta bosiladi", "Bir marta bosiladi", "Ctrl bilan bosiladi", "A"),
    ("So'zni qirqib olish (Cut) komandasi bilan o'chirish o'rtasidagi asosiy farq?", "Cut qilingan narsa xotirada saqlanadi va qayta qo'yish mumkin", "Har ikkisi bir xil", "Cut faylni butunlay yo'q qiladi", "Cut faqat rasmlar uchun ishlaydi", "A"),
    ("Word-da chiziq tortish (Underline) klaviatura kombinatsiyasi?", "Ctrl + U", "Ctrl + I", "Ctrl + B", "Ctrl + C", "A"),
    ("Excelda katakchani tahrirlash (Edit cell) uchun qaysi tugma bosiladi?", "F2", "F1", "F3", "F4", "A"),
    ("Excelda butun ustunni belgilash uchun qanday klaviatura yorlig'i ishlatiladi?", "Ctrl + Space", "Shift + Space", "Ctrl + A", "Ctrl + Enter", "A"),
    ("Excelda butun qatorni belgilash uchun qanday klaviatura yorlig'i ishlatiladi?", "Shift + Space", "Ctrl + Space", "Ctrl + A", "Shift + Enter", "A"),
    ("Yangi ishchi varaq (New Sheet) Excelda qanday qo'shiladi?", "Shift + F11", "Ctrl + N", "Alt + Shift + F1", "F12", "A"),
    ("Wordda belgilangan matnni bosh harflar bilan yozishga o'tkazish (Change Case) uchun qaysi tugmalar ishlatiladi?", "Shift + F3", "Ctrl + Shift + A", "Caps Lock", "Alt + F3", "A"),
    ("Windowsda barcha ochiq dasturlarni ko'rish yorlig'i?", "Win + Tab", "Alt + Tab", "Ctrl + Esc", "Shift + Tab", "A"),
    ("Faylni to'liq (qutiga tushmasdan) o'chirib tashlash yorlig'i qaysi?", "Shift + Delete", "Delete", "Ctrl + Delete", "Alt + Delete", "A"),
    ("MS Word da nusxalash amali qaysi menyuda joylashgan?", "Home", "Insert", "Page Layout", "View", "A"),
    ("Bir hujjatdan ikkinchi hujjatga o'tish yorlig'i:", "Alt + Tab", "Shift + Tab", "Ctrl + Tab", "Win + Tab", "A"),
    ("Excel katagi qanday ko'rinishga ega bo'ladi?", "To'rtburchak", "Dumaloq", "Uchburchak", "Ko'pburchak", "A"),
    ("Wordda matn o'lchamini kattalashtirish yorlig'i?", "Ctrl + ]", "Ctrl + [", "Ctrl + +", "Ctrl + -", "A"),
    ("MS Word da jadvallar bilan ishlash uchun qaysi menyu kerak?", "Design va Layout", "Home", "Review", "View", "A"),
    ("Excelda matnni o'ngga tekislash qaysi menyudan bajariladi?", "Home", "Insert", "Data", "View", "A"),
    ("Kompyuter klaviaturasida 'Space' nima vazifani bajaradi?", "Bo'sh joy tashlash", "O'chirish", "Saqlash", "Tasdiqlash", "A"),
    ("'Enter' tugmasi qanday vazifada ishlatiladi?", "Tasdiqlash/Yangi qatorga o'tish", "Bekor qilish", "O'chirish", "Nusxalash", "A"),
    ("Kompyuterdan o'chirilgan fayllar qayerga tushadi?", "Savat (Recycle Bin)", "Xotira", "Monitorga", "Bulutli tizimga", "A")
] # 50 questions exactly

hard_questions = [
    # Word (Hard)
    ("Word dasturida matnni 'Subscript' (pastki indeks, masalan H₂O dagi 2) qilish yorlig'i qaysi?", "Ctrl + = (Tenglik)", "Ctrl + Shift + +", "Ctrl + -", "Alt + =", "A"),
    ("Word dasturida matnni 'Superscript' (yuqori indeks, masalan x²) qilish yorlig'i qaysi?", "Ctrl + Shift + + (Plus)", "Ctrl + = (Tenglik)", "Ctrl + Shift + =", "Alt + +", "A"),
    ("Word da makroslar (Macros) qaysi menyuda joylashgan?", "View yoki Developer", "Insert", "Home", "Page Layout", "A"),
    ("Hujjatda bo'lim tanaffusi (Section Break) tugmasi qaysi menyuda?", "Layout (Page Layout) -> Breaks", "Insert -> Pages", "Design -> Page Background", "References -> Citations", "A"),
    ("Avtomatik mundarija yaratish (Table of Contents) qaysi menyudan qilinadi?", "References", "Insert", "Layout", "Review", "A"),
    ("Hujjatga parol o'rnatish Word da qayerdan qilinadi?", "File -> Info -> Protect Document", "Review -> Restrict Editing", "Insert -> Object", "Design -> Themes", "A"),
    ("Matndagi so'zlar sonini hisoblash (Word Count) klaviatura yorlig'i qaysi?", "Ctrl + Shift + G", "F7", "Ctrl + W", "Alt + W", "A"),
    ("Orfografiya va grammatikani tekshirish (Spelling & Grammar) qaysi tugma bilan chaqiriladi?", "F7", "F5", "F1", "F12", "A"),
    ("Wordda xat jo'natish bosqichi qadamlarini (Mail Merge) qaysi menyu orqali boshqariladi?", "Mailings", "Review", "References", "Insert", "A"),
    ("SmartArt grafiklari Wordning qaysi joyida mavjud?", "Insert -> SmartArt", "Design -> Effects", "Layout -> Borders", "Home -> Styles", "A"),
    ("Word da izoh (Comment) qoldirish klaviatura yorlig'i:", "Ctrl + Alt + M", "Ctrl + Shift + C", "Alt + C", "Ctrl + M", "A"),
    ("Formatlashni nusxalash (Format Painter) qaysi klavish orqali nusxalanadi?", "Ctrl + Shift + C", "Ctrl + C", "Ctrl + Alt + C", "Alt + Shift + C", "A"),
    ("Fayldagi o'zgarishlarni kuzatib borish (Track Changes) klavish yorlig'i qaysi?", "Ctrl + Shift + E", "Ctrl + Alt + T", "Ctrl + T", "Alt + Shift + E", "A"),
    ("Sahifa raqamlarini faqat juft sahifalarda boshqacha qilib qo'yish uchun nima belgilanadi?", "Different Odd & Even Pages", "Different First Page", "Link to Previous", "Show Document Text", "A"),
    ("Wordda formula kiritish (Equation) klavish qaysi?", "Alt + = (Tenglik)", "Ctrl + E", "Shift + =", "Ctrl + Alt + E", "A"),

    # Excel (Hard)
    ("Excelda '=VLOOKUP()' funksiyasi qanday vazifani bajaradi?", "Ma'lumotlar bazasidan berilgan ko'rsatkich bo'yicha qiymatni vertikal qidirish", "Yig'indini hisoblash", "Matnni raqamga o'tkazish", "Gorizontal qidirish amalga oshirish", "A"),
    ("Excelda '$A$1' yozuvi qanday manzil turini bildiradi?", "Absolyut (o'zgarmas) manzil", "Nisbiy (o'zgaruvchi) manzil", "Aralash manzil", "Xato manzil", "A"),
    ("Excelda shartli formatlash (Conditional Formatting) qayerdan topiladi?", "Home -> Styles", "Insert -> Tables", "Data -> Data Tools", "Formulas -> Function Library", "A"),
    ("PivotTable (Yig'ma jadval) qaysi vazifani bajaradi?", "Katta hajmdagi ma'lumotlarni tahlil qilish va guruhlash", "Formatlash va rang berish", "Faylni saqlash", "Grafika chizish", "A"),
    ("Agar formula '=COUNTIF(A1:A10, \">5\")' bo'lsa, bu nima qiladi?", "5 dan katta bo'lgan kataklar sonini hisoblaydi", "A1:A10 dagi hamma katakni hisoblaydi", "5 dan katta qiymatlarni qo'shadi (Yig'indi)", "Faqat 5 ga teng kataklarni qidiradi", "A"),
    ("Faqat ko'rinib turgan kataklarni yig'ish uchuqn qaysi funksiya kerak?", "SUBTOTAL", "SUM", "COUNT", "SUMIF", "A"),
    ("Excelda 'Data Validation' (Ma'lumotlarni tekshirish) orqali nima qilish mumkin?", "Kataklarga kiritilayotgan ma'lumot turiga cheklov qo'yish", "Formulalarni xatosini tuzatish", "Jadval ranglarini o'zgartirish", "Faylga parol o'rnatish", "A"),
    ("Excelda bir xil ustundagi ko'p takrorlangan ma'lumotlarni olib tashlash tugmasi qaysi?", "Data -> Remove Duplicates", "Home -> Find & Select", "Data -> Filter", "Review -> Spelling", "A"),
    ("'#DIV/0!' xatoligi Excelda qachon paydo bo'ladi?", "Nol (0) ga bo'lish amalga oshirilganda", "Matn nolga aylantirilganda", "Manzil topilmaganda", "Katak siqilganda", "A"),
    ("'#REF!' xatoligi nimani anglatadi?", "Mavjud bo'lmagan katakka yoki o'chirilgan katakka ishora qilinganda", "Matn to'g'ri kiritilmagan bo'lsa", "Formula noto'g'ri yozilgan bo'lsa", "Katak turi xato bo'lsa", "A"),
    ("Excelda harf va raqamli ixtiyoriy matnlarni birlashtirish funksiyasi qaysi?", "CONCATENATE yoki & belgisi", "SUM", "TEXT", "LEFT", "A"),
    ("'=IF(A1>10, \"Katta\", \"Kichik\")' formulasi A1=5 bo'lganda qanday natija qaytaradi?", "Kichik", "Katta", "5", "Xato", "A"),
    ("O'zgaruvchi manzil A$1 ko'rinishida bo'lsa, qaysi tomoni o'zgarmas?", "1-qator o'zgarmas, A-ustun o'zgaruvchi", "A-ustun o'zgarmas, 1-qator o'zgaruvchi", "Hammasi o'zgarmas", "Hammasi o'zgaruvchi", "A"),
    ("Excelda bugungi sanani chiqaradigan funksiya qaysi?", "=TODAY()", "=NOW()", "=DATE()", "=DAY()", "A"),
    ("Hozirgi sana va vaqtni baravar chiqaradigan qaysi funksiya?", "=NOW()", "=TODAY()", "=TIME()", "=DATE()", "A"),
    ("Ikkita matnlik kataklarni orasiga bo'shliq qo'shib birlashtirishning to'g'ri usuli qaysi?", "=A1 & \" \" & B1", "=A1 + B1", "=CONCAT(A1,B1)", "=A1:B1", "A"),

    # Shortcuts & Advanced OS Concepts (Hard)
    ("Kompyuterda maxsus belgilar jadvalini (Character Map) qanday ochish mumkin?", "Win + R -> charmap deb yozish", "Win + C", "Alt + Shift + C", "Word orqali yozish", "A"),
    ("Papkalar ichida yashiringan (Hidden) fayllarni ko'rinishga keltirish menyusi qaysi?", "View -> Hidden items", "Home -> Show", "Share -> File extension", "View -> Panes", "A"),
    ("Displeyni bir nechta ekranga ulash (Project ko'rinishi) menyusi yorlig'i qaysi?", "Win + P", "Win + E", "Win + D", "Win + S", "A"),
    ("Tezkor qidiruv menyusi va Windows sozlamalarini qisqa ochish qaysi orqali?", "Win + I", "Win + Q", "Win + R", "Win + W", "A"),
    ("Taskbari (Vazifalar paneli) da turgan dasturlarni tez ochish yorlig'i qaysi?", "Win + (Dastur tartib raqami, masalan Win+1)", "Alt + (Raqam)", "Ctrl + (Raqam)", "Shift + (Raqam)", "A"),
    ("Xotiradagi clipboard (nusxa olinganlar jurnali) oynasini ochish yorlig'i qaysi?", "Win + V", "Ctrl + V", "Alt + V", "Shift + V", "A"),
    ("Brauzerda yopilib ketgan oxirgi oynani (Tab) qaytadan ochish klavish kombinatsiyasi qaysi?", "Ctrl + Shift + T", "Ctrl + T", "Ctrl + H", "Alt + T", "A"),
    ("Ekranning bir qismini rasmga olish (Snipping Tool tezkor yorlig'i) qaysi?", "Win + Shift + S", "Print Screen", "Win + Print Screen", "Alt + Print Screen", "A"),
    ("Kompyuter sistemasiga kirish (Run dialog) ishga tushirish qaysi yorliq?", "Win + R", "Win + E", "Win + S", "Win + F", "A"),
    ("CMD (Buyruqlar satri) da joriy katalogdagi fayllar ro'yxatini ko'rish buyrug'i qaysi?", "dir", "ls", "show", "list", "A"),
    ("Brauzerda kengaytirilgan (Developer) vositalarini ochish yorlig'i?", "F12 yoki Ctrl + Shift + I", "F10", "F5", "Ctrl + D", "A"),
    ("Sayt keshini to'liq bekor qilib sahifani yangilash (Hard Refresh) yorlig'i qaysi?", "Ctrl + F5", "F5", "Ctrl + R", "Shift + F5", "A"),
    ("Barcha ochiq dasturlarni minimallashtirish va xotirada qoldirish yorlig'i?", "Win + M", "Win + D", "Alt + Space", "Win + P", "A"),
    ("Virtual ish stolini (Virtual Desktop) yaratish klavishlar yig'indisi qaysi?", "Win + Ctrl + D", "Win + Tab", "Win + Shift + D", "Win + D", "A"),
    ("Kompyuterda oEmoji Panelni chiqarish klavishi?", "Win + . (Nuqta)", "Win + E", "Win + Space", "Win + Ctrl + E", "A"),

    # Added hard questions
    ("Word da satrlar oralig'ini (Line spacing) 1.5 qilish yorlig'i?", "Ctrl + 5", "Ctrl + 1.5", "Ctrl + 2", "Ctrl + 1", "A"),
    ("Word da satrlar oralig'ini 2 qilish yorlig'i?", "Ctrl + 2", "Ctrl + 1", "Ctrl + 5", "Ctrl + D", "A"),
    ("Excelda kataklarni muzlatish (Freeze Panes) menyusi qayerda joylashgan?", "View", "Home", "Data", "Insert", "A"),
    ("Excel makroslari qaysi dasturlash tili orqali yoziladi?", "VBA - Visual Basic for Applications", "Python", "Java", "C++", "A"),
    ("Word da sahifani albom shakliga (Landscape) o'tkazish qaerdan bajariladi?", "Layout -> Orientation", "Insert -> Pages", "View -> Zoom", "Home -> Styles", "A"),
    ("MS Excel da grafiklar (Charts) qaysi menyu yordamida yaratiladi?", "Insert", "Data", "Home", "Formulas", "A"),
    ("Ekranni ikki qismga bo'lish Windowsda qaysi klavishlar orqali tez bajariladi?", "Win + Chap/O'ng strelkalar", "Win + Up/Down", "Alt + Chap/O'ng", "Ctrl + Shift + Chap/O'ng", "A"),
    ("O'chmas fayllarni Shift+Delete bilsan o'chirilganda ular qayerga tushadi?", "Hech qayerga (butunlay xotiradan o'tadi)", "Recycle bin", "Temp papka", "AppData", "A"),
    ("Word da sahifaning yuqori va pastki qismi nima deb ataladi?", "Header and Footer", "Top and Bottom", "Margin and Padding", "Outline", "A"),
    ("Formula yozilayotganda katak manzilini doimiy (Absolute) qoldirish uchun qaysi klavish ishlatiladi?", "F4", "F2", "F5", "F9", "A"),
    ("Excelda '=LEN(A1)' formulasi nima ish qiladi?", "Katakdagi belgilar sonini sanaydi", "So'zlarni yig'adi", "Raqamlarni qo'shadi", "Bo'sh kataklarni sanaydi", "A"),
    ("Hujjat ichidagi matnni ishorat vositasiga yopishtirish (Paste Special) qaysi klavishlar blan boqlinadigan qoyilari qaysi?", "Ctrl + Alt + V", "Ctrl + Shift + C", "Alt + P", "Ctrl + Space", "A"),
    ("Windows tizimida 'Safe Mode' da yuklash uchun sistema yonayotganda odatda qaysi klavish bosiladi?", "F8", "F1", "F12", "F2", "A"),
    ("Excelda varaqlar (shtitslar) o'rtasida tezkarga o'tish yorlig'i qaysi?", "Ctrl + Page Up/Down", "Alt + Tab", "Shift + Tab", "Ctrl + Shift + Tab", "A"),
    ("Bir turdagi barcha obyektlarni Word da qanday qilib tanlash mumkin?", "Select Text with Similar Formatting", "Select All", "Ctrl + A", "Double Click", "A"),
    ("Brauzer tarixini ochish tezkor yorlig'i qaysi?", "Ctrl + H", "Ctrl + J", "Ctrl + T", "Ctrl + O", "A"),
    ("Brauzerda yuklanganlarni (Downloads) ko'rish yorlig'i qaysi?", "Ctrl + J", "Ctrl + D", "Ctrl + H", "Ctrl + L", "A"),
    ("Formatni tozalash (Clear Formatting) Word da qaysi kombinatsiya bilan qilinadi?", "Ctrl + Spacebar", "Ctrl + Backspace", "Ctrl + Delete", "Alt + C", "A"),
    ("Shaxsiy papkada yashirin ma'lumotlarni qanday qilib yashirish mumkin?", "Attribute 'Hidden' ni tanlash", "Parol qo'yish orqali", "Faylni ismini o'zgartirib", "Hech qanday yo'l bilan", "A")
] # exactly 50 hard questions

def add_questions():
    with app.app_context():
        # Get Informatica subject
        subject = Subject.query.filter_by(name="Informatika").first()
        if not subject:
            subject = Subject(name="Informatika", grades="5,6")
            db.session.add(subject)
            db.session.commit()
            print("Informatika fani yaratildi.")
            
        subject_id = subject.id
        
        # O'chirish (Deletion of old 300 Qs)
        old_questions = Question.query.filter_by(grade=5, quarter=3).all()
        for q in old_questions:
            db.session.delete(q)
        print(f"{len(old_questions)} ta avvalgi savol o'chirildi.")
        
        # Yangi savollarni qoshish
        added = 0
        for data in easy_medium_questions:
            q_text, a, b, c, d, correct = data
            difficulty = random.choice([1, 2]) # easy or medium
            
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
                difficulty=difficulty,
                question_text=q_text,
                option_a=new_opt_a,
                option_b=new_opt_b,
                option_c=new_opt_c,
                option_d=new_opt_d,
                correct_answer=real_correct,
                lesson=None
            )
            db.session.add(question)
            added += 1
            
        for data in hard_questions:
            q_text, a, b, c, d, correct = data
            difficulty = 3 # difficult
            
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
                difficulty=difficulty,
                question_text=q_text,
                option_a=new_opt_a,
                option_b=new_opt_b,
                option_c=new_opt_c,
                option_d=new_opt_d,
                correct_answer=real_correct,
                lesson=None
            )
            db.session.add(question)
            added += 1
            
        db.session.commit()
        print(f"Barcha savollar ({added}ta) muvaffaqiyatli saqlandi. Word/Excel/Shortcuts!")

if __name__ == "__main__":
    add_questions()
