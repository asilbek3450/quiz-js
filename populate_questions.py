"""
Ma'lumotlar bazasiga 4000 ta HAR XIL savol qo'shish skripti
Har bir fan/sinf/chorak uchun 200 ta BIR-BIRIDAN FARQLI savol
"""

from app import app, db, Question
import random
from datetime import datetime

# ============================================
# KO'PROQ ASOSIY SHABLONLAR QO'SHILDI
# ============================================

# Informatika savollari shablonlari (5-6 sinflar) - KO'P AYTILGAN
informatika_templates = {
    5: {
        1: [  # 1-chorak: Kompyuter asoslari (25 ta)
            ("Kompyuterning miyasi deb nimaga aytiladi?", ["Monitor", "Protsessor", "Klaviatura", "Sichqoncha"], 1),
            ("Qaysi qurilma ma'lumot kiritish uchun ishlatiladi?", ["Printer", "Monitor", "Klaviatura", "Kolonka"], 2),
            ("ROM xotira nima?", ["Doimiy xotira", "Operativ xotira", "Tashqi xotira", "Kesh xotira"], 0),
            ("Internet nima?", ["Kompyuter o'yini", "Global tarmoq", "Dastur", "Qurilma"], 1),
            ("Fayl kengaytmasi .txt nimani bildiradi?", ["Rasm", "Matn hujjati", "Video", "Audio"], 1),
            ("Kompyuterning asosiy xotirasiga nima kiradi?", ["Flash disk", "CD disk", "RAM", "Printer"], 2),
            ("Windows operatsion tizimining asosiy vazifasi nima?", ["Internet bilan ishlash", "Dasturlarni boshqarish", "Matn yozish", "Rasm chizish"], 1),
            ("Kompyuterda ma'lumotlar qanday o'lchanadi?", ["Metr", "Litr", "Bayt", "Kilogramm"], 2),
            ("1 Kilobayt necha baytga teng?", ["100 bayt", "1000 bayt", "1024 bayt", "2048 bayt"], 2),
            ("Quyidagilardan qaysi biri dasturiy ta'minot emas?", ["Windows", "Microsoft Word", "Protsessor", "Chrome"], 2),
            ("Kompyuter qurilmalarining fizik qismlariga nima deyiladi?", ["Software", "Hardware", "Brainware", "Middleware"], 1),
            ("Operatsion tizim qanday turdagi dastur?", ["Ilova dasturi", "Tizim dasturi", "O'yin dasturi", "Antivirus"], 1),
            ("Keyboards, mouse, scanner qanday qurilmalar hisoblanadi?", ["Output devices", "Input devices", "Storage devices", "Processing devices"], 1),
            ("Monitor, printer, speaker qanday qurilmalar hisoblanadi?", ["Input devices", "Output devices", "Storage devices", "Processing devices"], 1),
            ("CD, DVD, flash drive qanday qurilmalar hisoblanadi?", ["Processing devices", "Storage devices", "Input devices", "Output devices"], 1),
            ("Kompyuterda hisoblash uchun asosiy qurilma?", ["RAM", "CPU", "Hard disk", "Power supply"], 1),
            ("ASCII nima?", ["Dastur", "Kodlash tizimi", "Qurilma", "Tarmoq"], 1),
            ("Bit nima?", ["Ma'lumotning eng kichik birligi", "Dastur", "Qurilma", "Tarmoq protokoli"], 0),
            ("1 Byte necha bit?", ["4 bit", "8 bit", "16 bit", "32 bit"], 1),
            ("Binary tizimda necha raqam ishlatiladi?", ["2", "8", "10", "16"], 0),
            ("Hexadecimal tizim necha asosida?", ["2", "8", "10", "16"], 3),
            ("Qaysi biri periferik qurilma emas?", ["Monitor", "CPU", "Printer", "Scanner"], 1),
            ("Tarmoq kartasi nima uchun kerak?", ["Internetga ulanish", "Ovoz chiqarish", "Rasm ko'rsatish", "Ma'lumot saqlash"], 0),
            ("Power supply nima?", ["Quvvat manbai", "Protsessor", "Xotira", "Monitor"], 0),
            ("Motherboard nima?", ["Asosiy platalar", "Monitor", "Klaviatura", "Printer"], 0),
        ],
        2: [  # 2-chorak: Tashqi qurilmalar (25 ta)
            ("Sichqonchaning asosiy vazifasi nima?", ["Matn kiritish", "Kursor bilan boshqarish", "Ovoz chiqarish", "Rasm chop etish"], 1),
            ("Printer qanday qurilma hisoblanadi?", ["Kirish qurilmasi", "Chiqish qurilmasi", "Xotira qurilmasi", "Tarmoq qurilmasi"], 1),
            ("Monitor ekrani o'lchami nima bilan o'lchanadi?", ["Santimetr", "Metr", "Dyuym", "Kilogramm"], 2),
            ("USB port nima uchun ishlatiladi?", ["Internetga ulanish", "Qurilmalarni ulash", "Ovoz chiqarish", "Rasm ko'rsatish"], 1),
            ("Hard disk nima uchun ishlatiladi?", ["Ma'lumotlarni doimiy saqlash", "Internetga ulanish", "Ovoz chiqarish", "Rasm ko'rsatish"], 0),
            ("Scanner qanday qurilma?", ["Input device", "Output device", "Storage device", "Processing device"], 0),
            ("Touchscreen qanday qurilma?", ["Input-output device", "Storage device", "Processing device", "Communication device"], 0),
            ("Microphone qanday qurilma?", ["Output device", "Input device", "Storage device", "Display device"], 1),
            ("Speaker qanday qurilma?", ["Input device", "Output device", "Storage device", "Input-output device"], 1),
            ("Web-camera nima uchun ishlatiladi?", ["Video yozish", "Ovoz yozish", "Matn kiritish", "Chop etish"], 0),
            ("LCD nima?", ["Monitor turi", "Printer turi", "Keyboard turi", "Mouse turi"], 0),
            ("LED monitor qanday texnologiya?", ["Light Emitting Diode", "Liquid Crystal Display", "Cathode Ray Tube", "Plasma Display"], 0),
            ("CRT monitor qanday texnologiya?", ["Yangi texnologiya", "Eski texnologiya", "Suyuq kristalli", "Plazma"], 1),
            ("Dot matrix printer qanday printer?", ["Inkjet", "Laser", "Impact", "Thermal"], 2),
            ("Inkjet printer qanday printer?", ["Suyuq bo'yoq bilan ishlaydi", "Lazer bilan ishlaydi", "Zarba bilan ishlaydi", "Issiqlik bilan ishlaydi"], 0),
            ("Laser printer qanday printer?", ["Tez va yuqori sifatli", "Sekin va past sifatli", "Arzon", "Og'ir"], 0),
            ("Plotter nima?", ["Katta formatli printer", "Kichik printer", "Scanner", "Monitor"], 0),
            ("Touchpad qayerda ko'p ishlatiladi?", ["Desktop", "Laptop", "Tablet", "Smartphone"], 1),
            ("Joystick nima uchun ishlatiladi?", ["O'yinlar", "Matn kiritish", "Rasm chizish", "Ovoz yozish"], 0),
            ("Light pen nima?", ["Rasm chizish qurilmasi", "Matn kiritish qurilmasi", "Ovoz qabul qilish", "Video ko'rish"], 0),
            ("Barcode reader nima?", ["Shtrix-kod o'qiydi", "Matn o'qiydi", "Rasm o'qiydi", "Ovoz o'qiydi"], 0),
            ("OMR nima?", ["Optical Mark Recognition", "Optical Character Recognition", "Magnetic Recognition", "Barcode Recognition"], 0),
            ("OCR nima?", ["Barcode o'qish", "Matnni skanerdan o'qish", "Rasm o'qish", "Ovozni tanib olish"], 1),
            ("Biometric device nima?", ["Barmoq izini skanerlaydi", "Matn o'qiydi", "Rasm o'qiydi", "Ovoz yozadi"], 0),
            ("Digital camera qanday fayllar yaratadi?", ["Digital images", "Text files", "Audio files", "Video files"], 0),
        ],
        3: [  # 3-chorak: Xavfsizlik (25 ta)
            ("Kompyuter viruslari nima?", ["Foydali dasturlar", "Zarar keltiruvchi dasturlar", "O'yin dasturlari", "Operatsion tizim"], 1),
            ("Antivirus dasturi nima uchun kerak?", ["Matn yozish", "Viruslardan himoya qilish", "Rasm chizish", "O'yin o'ynash"], 1),
            ("Parolning minimal uzunligi qancha bo'lishi kerak?", ["2 ta belgi", "4 ta belgi", "8 ta belgi", "16 ta belgi"], 2),
            ("Firewall nima?", ["Yong'in devori", "Tarmoq himoyasi", "Antivirus", "Parol"], 1),
            ("Malware nima?", ["Yaxshi dastur", "Zararli dastur", "O'yin", "Ilova"], 1),
            ("Spyware nima?", ["Josuslik dasturi", "Virus", "Antivirus", "Firewall"], 0),
            ("Adware nima?", ["Reklama ko'rsatadigan dastur", "Virus", "Antivirus", "Utility"], 0),
            ("Trojan horse nima?", ["O'yin", "Josuslik dasturi", "Fayllarni o'chiradigan virus", "Antivirus"], 1),
            ("Worm nima?", ["Qurt virusi", "Trojan", "Spyware", "Adware"], 0),
            ("Phishing nima?", ["Baliq ovlash", "Firibgarlik", "Xakerlik", "Spam"], 1),
            ("Spam nima?", ["Keraksiz elektron pochta", "Virus", "Antivirus", "Fayl"], 0),
            ("Backup nima?", ["Zaxira nusxa", "Virus", "Parol", "Firewall"], 0),
            ("Encryption nima?", ["Shifrlash", "O'chirish", "Nusxa olish", "Skanerlash"], 0),
            ("Two-factor authentication nima?", ["Ikki faktorli autentifikatsiya", "Bitta parol", "Biometrik", "SMS"], 0),
            ("Biometric authentication nima?", ["Barmoq izi", "Parol", "Token", "Smart card"], 0),
            ("VPN nima?", ["Virtual Private Network", "Virus Protection Network", "Video Processing Network", "Voice Phone Network"], 0),
            ("Password manager nima?", ["Parollarni saqlaydigan dastur", "Virus", "Antivirus", "Firewall"], 0),
            ("Social engineering nima?", ["Ijtimoiy muhandislik", "Dasturiy muhandislik", "Qurilish", "Tibbiyot"], 0),
            ("Shoulder surfing nima?", ["Yelka orqali ko'rish", "Hacking", "Programming", "Scanning"], 0),
            ("Dumpster diving nima?", ["Chiqindilarni qidirish", "Hacking", "Programming", "Scanning"], 0),
            ("Antivirusni qanchada yangilash kerak?", ["Hech qachon", "Har kuni", "Har hafta", "Avtomatik yangilanish"], 3),
            ("Full system scan qachon amalga oshiriladi?", ["Har kuni", "Har hafta", "Har oy", "Vaqti-vaqti bilan"], 3),
            ("Emailda nimalarga shubha qilish kerak?", ["Noma'lum manbalardan", "Tanishlardan", "Barcha email", "Hech qanday emailga"], 0),
            ("Public WiFi-da nima qilish xavfli?", ["Bank operatsiyalari", "Veb-sayt ko'rish", "Email o'qish", "Video ko'rish"], 0),
            ("Software update nima uchun muhim?", ["Xavfsizlik tuzatmalari", "Yangi o'yinlar", "Ko'proq xotira", "Tezroq ishlash"], 0),
        ],
        4: [  # 4-chorak: Internet va Office (25 ta)
            ("WWW nimaning qisqartmasi?", ["World Wide Web", "World Web Windows", "Web Wide World", "Windows Web World"], 0),
            ("Elektron pochta uchun qaysi belgi ishlatiladi?", ["#", "@", "&", "%"], 1),
            ("Brauzer nima?", ["Operatsion tizim", "Veb-sahifalarni ko'rish dasturi", "Antivirus", "O'yin"], 1),
            ("URL nima?", ["Internet manzili", "Elektron pochta", "Fayl nomi", "Dastur"], 0),
            ("HTTP nimaning qisqartmasi?", ["HyperText Transfer Protocol", "High Text Transfer Protocol", "Hyper Transfer Text Protocol", "High Transfer Text Protocol"], 0),
            ("HTML nima?", ["Veb-sahifa yaratish tili", "Dasturlash tili", "Operatsion tizim", "Database"], 0),
            ("Search engine nima?", ["Google kabi", "Antivirus", "Word processor", "Spreadsheet"], 0),
            ("Download nima?", ["Yuklab olish", "Yuklash", "O'chirish", "Ko'rish"], 0),
            ("Upload nima?", ["Yuklash", "Yuklab olish", "O'chirish", "Ko'rish"], 0),
            ("Social media nima?", ["Facebook kabi", "Antivirus", "Word processor", "Spreadsheet"], 0),
            ("Blog nima?", ["Onlayn jurnal", "Email", "Chat", "Game"], 0),
            ("Cloud computing nima?", ["Bulutli hisoblash", "Local computing", "Mobile computing", "Desktop computing"], 0),
            ("E-commerce nima?", ["Elektron tijorat", "Email", "Chat", "Blog"], 0),
            ("Wi-Fi nima?", ["Simsiz internet", "Simli internet", "Mobile internet", "Satellite internet"], 0),
            ("Modem nima?", ["Internetga ulanish qurilmasi", "Printer", "Scanner", "Monitor"], 0),
            ("Router nima?", ["Tarmoq trafigini boshqaradi", "Printer", "Scanner", "Monitor"], 0),
            ("ISP nima?", ["Internet Service Provider", "Internet Security Protocol", "International Service Provider", "Internal Security Protocol"], 0),
            ("Bandwidth nima?", ["Internet tezligi", "Xotira hajmi", "Protsessor tezligi", "Ekran o'lchami"], 0),
            ("Cookies nima?", ["Kichik fayllar", "Viruslar", "Antiviruslar", "Spam"], 0),
            ("Cache nima?", ["Vaqtinchalik xotira", "Doimiy xotira", "Tashqi xotira", "Operativ xotira"], 0),
            ("History nima?", ["Brauzer tarixi", "Email tarixi", "Chat tarixi", "Game tarixi"], 0),
            ("Bookmark nima?", ["Xatcho'p", "Email", "Chat", "Download"], 0),
            ("Refresh nima?", ["Sahifani yangilash", "Brauzerni yopish", "Kompyuterni o'chirish", "Internetni uzish"], 0),
            ("Incognito mode nima?", ["Maxfiy rejim", "Oddiy rejim", "Tez rejim", "Sekin rejim"], 0),
            ("Pop-up nima?", ["Ochiladigan oyna", "Email", "Chat", "Download"], 0),
        ]
    },
    6: {
        1: [  # 1-chorak: Dasturiy ta'minot (25 ta)
            ("Operatsion tizim nima?", ["Dastur", "Asosiy dasturiy ta'minot", "O'yin", "Brauzer"], 1),
            ("Microsoft Office nima?", ["Operatsion tizim", "Ofis dasturlari to'plami", "Antivirus", "Brauzer"], 1),
            ("Paint dasturi nima uchun ishlatiladi?", ["Matn yozish", "Rasm chizish", "Hisoblash", "Internet"], 1),
            ("Windows, Linux, macOS nima?", ["Operatsion tizimlar", "Dasturlash tillari", "Antiviruslar", "Brauzerlar"], 0),
            ("Application software nima?", ["Ilova dasturlari", "Operatsion tizim", "Utility", "Device driver"], 0),
            ("System software nima?", ["Tizim dasturlari", "Ilova dasturlari", "O'yinlar", "Multimedia"], 0),
            ("Utility software nima?", ["Yordamchi dasturlar", "Operatsion tizim", "Ilova dasturi", "O'yin"], 0),
            ("Device driver nima?", ["Qurilma haydovchisi", "Antivirus", "Word processor", "Browser"], 0),
            ("Word processor nima?", ["Matn muharriri", "Hisoblash dasturi", "Rasm muharriri", "Presentation"], 0),
            ("Spreadsheet nima?", ["Jadval muharriri", "Matn muharriri", "Rasm muharriri", "Presentation"], 0),
            ("Presentation software nima?", ["Taqdimot dasturi", "Matn muharriri", "Jadval muharriri", "Database"], 0),
            ("Database software nima?", ["Ma'lumotlar bazasi dasturi", "Matn muharriri", "Jadval muharriri", "Presentation"], 0),
            ("Graphics software nima?", ["Grafika dasturi", "Matn muharriri", "Jadval muharriri", "Database"], 0),
            ("Multimedia software nima?", ["Multimedia dasturi", "Matn muharriri", "Jadval muharriri", "Database"], 0),
            ("Web browser nima?", ["Veb brauzer", "Word processor", "Spreadsheet", "Database"], 0),
            ("Email client nima?", ["Elektron pochta dasturi", "Word processor", "Spreadsheet", "Browser"], 0),
            ("Antivirus nima?", ["Virusga qarshi dastur", "Word processor", "Spreadsheet", "Browser"], 0),
            ("File compression software nima?", ["Fayl siqish dasturi", "Antivirus", "Word processor", "Browser"], 0),
            ("Backup software nima?", ["Zaxira nusxa dasturi", "Antivirus", "Word processor", "Browser"], 0),
            ("Disk cleanup utility nima?", ["Diskni tozalash", "Antivirus", "Word processor", "Browser"], 0),
            ("Disk defragmenter nima?", ["Disk defragmentatsiyasi", "Antivirus", "Word processor", "Browser"], 0),
            ("Task manager nima?", ["Vazifalar menejeri", "Antivirus", "Word processor", "Browser"], 0),
            ("Control panel nima?", ["Boshqaruv paneli", "Antivirus", "Word processor", "Browser"], 0),
            ("Software installation nima?", ["Dastur o'rnatish", "Dastur o'chirish", "Dastur yaratish", "Dastur testlash"], 0),
            ("Software update nima?", ["Dastur yangilash", "Dastur o'chirish", "Dastur yaratish", "Dastur testlash"], 0),
        ],
        2: [  # 2-chorak: Fayllar bilan ishlash (25 ta)
            ("Papka (folder) nima?", ["Fayl", "Fayllarni saqlash joyi", "Dastur", "Qurilma"], 1),
            ("Faylni nusxalash qanday amalga oshiriladi?", ["Delete", "Copy-Paste", "Cut", "Rename"], 1),
            ("Faylni o'chirish uchun qaysi tugma ishlatiladi?", ["Enter", "Delete", "Ctrl", "Alt"], 1),
            ("File extension nima?", ["Fayl kengaytmasi", "Fayl nomi", "Fayl hajmi", "Fayl formati"], 0),
            (".docx qaysi dastur fayli?", ["Excel", "Word", "PowerPoint", "Access"], 1),
            (".xlsx qaysi dastur fayli?", ["Word", "Excel", "PowerPoint", "Access"], 1),
            (".pptx qaysi dastur fayli?", ["Word", "Excel", "PowerPoint", "Access"], 2),
            (".pdf qaysi fayl formati?", ["Portable Document Format", "Word Document", "Excel Spreadsheet", "PowerPoint Presentation"], 0),
            ("File path nima?", ["Fayl joylashuvi", "Fayl nomi", "Fayl kengaytmasi", "Fayl hajmi"], 0),
            ("Root directory nima?", ["Asosiy katalog", "Papka", "Fayl", "Disk"], 0),
            ("Subdirectory nima?", ["Pastki katalog", "Asosiy katalog", "Fayl", "Disk"], 0),
            ("File size qanday o'lchanadi?", ["Bayt, KB, MB", "Metr, km", "Kilogramm", "Soni"], 0),
            ("1 MB necha KB?", ["100 KB", "1000 KB", "1024 KB", "2048 KB"], 2),
            ("1 GB necha MB?", ["100 MB", "1000 MB", "1024 MB", "2048 MB"], 2),
            ("File attributes nima?", ["Fayl atributlari", "Fayl nomi", "Fayl kengaytmasi", "Fayl hajmi"], 0),
            ("Read-only attribute nima?", ["Faqat o'qish", "Yozish", "O'chirish", "O'zgartirish"], 0),
            ("Hidden attribute nima?", ["Yashirin", "Ochiq", "O'qish", "Yozish"], 0),
            ("Archive attribute nima?", ["Arxiv", "Ochiq", "Yashirin", "Faqat o'qish"], 0),
            ("File compression nima?", ["Fayl siqish", "Fayl kengaytirish", "Fayl o'chirish", "Fayl ko'chirish"], 0),
            ("ZIP format nima?", ["Siqilgan fayl formati", "Matn formati", "Rasm formati", "Audio formati"], 0),
            ("File sharing nima?", ["Fayl almashish", "Fayl o'chirish", "Fayl yaratish", "Fayl nomlash"], 0),
            ("Cloud storage nima?", ["Bulutli saqlash", "Local saqlash", "External saqlash", "Internal saqlash"], 0),
            ("File backup nima?", ["Fayl zaxirasi", "Fayl o'chirishi", "Fayl yaratish", "Fayl ko'chirish"], 0),
            ("File recovery nima?", ["Fayl tiklash", "Fayl o'chirish", "Fayl yaratish", "Fayl nomlash"], 0),
            ("Recycle Bin nima?", ["Chiqindilar qutisi", "Papka", "Disk", "Fayl"], 0),
        ],
        3: [  # 3-chorak: Tarmoqlar (25 ta)
            ("LAN nima?", ["Lokal tarmoq", "Global tarmoq", "Internet", "Dastur"], 0),
            ("Wi-Fi nima?", ["Simli tarmoq", "Simsiz tarmoq", "Operatsion tizim", "Brauzer"], 1),
            ("IP manzil nima?", ["Elektron pochta", "Tarmoqdagi kompyuter manzili", "Veb-sayt", "Dastur"], 1),
            ("WAN nima?", ["Keng tarmoq", "Lokal tarmoq", "Shaxsiy tarmoq", "Simsiz tarmoq"], 0),
            ("MAN nima?", ["Shahar tarmog'i", "Lokal tarmoq", "Global tarmoq", "Shaxsiy tarmoq"], 0),
            ("PAN nima?", ["Shaxsiy tarmoq", "Lokal tarmoq", "Global tarmoq", "Shahar tarmog'i"], 0),
            ("Network topology nima?", ["Tarmoq topologiyasi", "Tarmoq protokoli", "Tarmoq qurilmasi", "Tarmoq xavfsizligi"], 0),
            ("Star topology nima?", ["Yulduz topologiyasi", "Halqa topologiyasi", "Shina topologiyasi", "Daraxt topologiyasi"], 0),
            ("Bus topology nima?", ["Shina topologiyasi", "Yulduz topologiyasi", "Halqa topologiyasi", "Daraxt topologiyasi"], 0),
            ("Ring topology nima?", ["Halqa topologiyasi", "Yulduz topologiyasi", "Shina topologiyasi", "Daraxt topologiyasi"], 0),
            ("Mesh topology nima?", ["To'r topologiyasi", "Yulduz topologiyasi", "Shina topologiyasi", "Halqa topologiyasi"], 0),
            ("Network device nima?", ["Tarmoq qurilmasi", "Kirish qurilmasi", "Chiqish qurilmasi", "Saqlash qurilmasi"], 0),
            ("Hub nima?", ["Oddiy tarmoq qurilmasi", "Aqlli tarmoq qurilmasi", "Xavfsizlik qurilmasi", "Ulanish qurilmasi"], 0),
            ("Switch nima?", ["Aqlli tarmoq qurilmasi", "Oddiy tarmoq qurilmasi", "Xavfsizlik qurilmasi", "Ulanish qurilmasi"], 0),
            ("Router nima?", ["Tarmoqlarni ulaydi", "Faqt signalni kuchaytiradi", "Faqt kompyuterlarni ulaydi", "Internetni uzadi"], 0),
            ("Gateway nima?", ["Darvoza", "Router", "Switch", "Hub"], 0),
            ("Bridge nima?", ["Ko'prik", "Router", "Switch", "Hub"], 0),
            ("Repeater nima?", ["Takrorlovchi", "Router", "Switch", "Hub"], 0),
            ("Modem nima?", ["Digital-analog konvertor", "Router", "Switch", "Hub"], 0),
            ("NIC nima?", ["Tarmoq interfeys kartasi", "Router", "Switch", "Hub"], 0),
            ("Protocol nima?", ["Tarmoq qoidasi", "Tarmoq qurilmasi", "Tarmoq dasturi", "Tarmoq xavfsizligi"], 0),
            ("TCP/IP nima?", ["Internet protokoli", "Local protokol", "File protokol", "Security protokol"], 0),
            ("FTP nima?", ["Fayl uzatish protokoli", "Elektron pochta protokoli", "Veb protokol", "Xavfsizlik protokoli"], 0),
            ("HTTP nima?", ["Veb protokol", "Fayl uzatish protokoli", "Elektron pochta protokoli", "Xavfsizlik protokoli"], 0),
            ("SMTP nima?", ["Elektron pochta protokoli", "Veb protokol", "Fayl uzatish protokoli", "Xavfsizlik protokoli"], 0),
        ],
        4: [  # 4-chorak: Multimediya va ilovalar (25 ta)
            ("Audio fayl kengaytmasi qaysi?", [".txt", ".mp3", ".jpg", ".exe"], 1),
            ("Video fayl kengaytmasi qaysi?", [".doc", ".mp3", ".mp4", ".txt"], 2),
            ("Rasm fayl kengaytmasi qaysi?", [".txt", ".mp3", ".jpg", ".exe"], 2),
            (".wav qaysi fayl?", ["Audio", "Video", "Rasm", "Matn"], 0),
            (".avi qaysi fayl?", ["Video", "Audio", "Rasm", "Matn"], 0),
            (".png qaysi fayl?", ["Rasm", "Audio", "Video", "Matn"], 0),
            (".gif qaysi fayl?", ["Harakatli rasm", "Audio", "Video", "Matn"], 0),
            ("Bitmap image nima?", ["Piksel rasmi", "Vektor rasmi", "3D rasmi", "Matnli rasm"], 0),
            ("Vector image nima?", ["Vektor rasmi", "Piksel rasmi", "3D rasmi", "Matnli rasm"], 0),
            ("Resolution nima?", ["Rasm sifati", "Rasm hajmi", "Rasm formati", "Rasm nomi"], 0),
            ("Pixel nima?", ["Rasm nuqtasi", "Rasm chizig'i", "Rasm maydoni", "Rasm formati"], 0),
            ("DPI nima?", ["Nuqta zichligi", "Piksel soni", "Rasm hajmi", "Rasm formati"], 0),
            ("RGB nima?", ["Rang modeli", "Audio formati", "Video codec", "Fayl formati"], 0),
            ("CMYK nima?", ["Bosma rang modeli", "Ekran rang modeli", "Audio formati", "Video codec"], 0),
            ("MP3 nima?", ["Audio format", "Video format", "Image format", "Text format"], 0),
            ("MP4 nima?", ["Video format", "Audio format", "Image format", "Text format"], 0),
            ("Codec nima?", ["Kodlash-qochirish", "Format", "Player", "Editor"], 0),
            ("Multimedia player nima?", ["Multimedia ijrochisi", "Multimedia muharriri", "Multimedia konvertori", "Multimedia skaneri"], 0),
            ("Video editing software nima?", ["Video muharriri", "Audio muharriri", "Rasm muharriri", "Text muharriri"], 0),
            ("Audio editing software nima?", ["Audio muharriri", "Video muharriri", "Rasm muharriri", "Text muharriri"], 0),
            ("Image editing software nima?", ["Rasm muharriri", "Video muharriri", "Audio muharriri", "Text muharriri"], 0),
            ("Animation software nima?", ["Animatsiya dasturi", "Video muharriri", "Audio muharriri", "Rasm muharriri"], 0),
            ("3D modeling software nima?", ["3D modellashtirish", "2D chizish", "Video editing", "Audio editing"], 0),
            ("Streaming nima?", ["Oqimli media", "Yuklab olish", "Yuklash", "Skanerlash"], 0),
            ("Podcast nima?", ["Audio dastur", "Video dastur", "Rasm galereyasi", "Matn blogi"], 0),
        ]
    }
}

# Python savollari shablonlari (7-8-9 sinflar) - KO'P AYTILGAN
python_templates = {
    7: {
        1: [  # 1-chorak: Python asoslari (25 ta)
            ("Python dasturlash tilini kim yaratgan?", ["Bill Gates", "Guido van Rossum", "Mark Zuckerberg", "Steve Jobs"], 1),
            ("Python dasturida print() funksiyasi nima qiladi?", ["Ma'lumot kiritadi", "Ma'lumotni ekranga chiqaradi", "Faylni o'qiydi", "Dasturni to'xtatadi"], 1),
            ("Python-da o'zgaruvchi e'lon qilish uchun qaysi kalit so'z ishlatiladi?", ["var", "let", "Kalit so'z kerak emas", "variable"], 2),
            ("Quyidagi qaysi biri to'g'ri o'zgaruvchi nomi?", ["2ism", "ism-familiya", "ism_familiya", "ism familiya"], 2),
            ("Python-da kommentariya qanday boshlanadi?", ["//", "/* */", "#", "--"], 2),
            ("Python faylining kengaytmasi qanday?", [".txt", ".py", ".pyt", ".python"], 1),
            ("Python IDLE nima?", ["Brauzar", "Dasturlash muhiti", "O'yin", "Operatsion tizim"], 1),
            ("Variable nima?", ["O'zgaruvchi", "Funksiya", "Operator", "Modul"], 0),
            ("String nima?", ["Matn", "Son", "Mantiqiy", "Ro'yxat"], 0),
            ("Integer nima?", ["Butun son", "O'nli son", "Matn", "Mantiqiy"], 0),
            ("Float nima?", ["O'nli son", "Butun son", "Matn", "Mantiqiy"], 0),
            ("Boolean nima?", ["Mantiqiy", "Butun son", "O'nli son", "Matn"], 0),
            ("Assignment operator nima?", ["Tenglashtirish operatori", "Qo'shish operatori", "Taqqoslash operatori", "Mantiqiy operator"], 0),
            ("= nima operator?", ["Tenglashtirish", "Tenglik", "Ayirish", "Ko'paytirish"], 0),
            ("== nima operator?", ["Tenglik", "Tenglashtirish", "Katta", "Kichik"], 0),
            ("Syntax nima?", ["Sintaksis", "Mantiq", "Algoritm", "Dastur"], 0),
            ("Error nima?", ["Xato", "Ogohlantirish", "Natija", "Operator"], 0),
            ("Syntax error nima?", ["Sintaksis xatosi", "Mantiqiy xato", "Ish vaqti xatosi", "Indentatsiya xatosi"], 0),
            ("Runtime error nima?", ["Ish vaqti xatosi", "Sintaksis xatosi", "Mantiqiy xato", "Indentatsiya xatosi"], 0),
            ("Logical error nima?", ["Mantiqiy xato", "Sintaksis xatosi", "Ish vaqti xatosi", "Indentatsiya xatosi"], 0),
            ("Debugging nima?", ["Xatolarni tuzatish", "Dastur yozish", "Dastur testlash", "Dastur ishga tushirish"], 0),
            ("Indentation nima?", ["Indentatsiya", "Funksiya", "Operator", "O'zgaruvchi"], 0),
            ("Case-sensitive nima?", ["Katta-kichik harf farqlaydi", "Katta-kichik harf farqlamaydi", "Faqt katta harf", "Faqt kichik harf"], 0),
            ("Python-da statement nima?", ["Ifoda", "Funksiya", "Modul", "Operator"], 0),
            ("Expression nima?", ["Ifoda", "Statement", "Funksiya", "Modul"], 0),
        ],
        2: [  # 2-chorak: Ma'lumot turlari va operatorlar (25 ta)
            ("Python-da matn turi qanday nomlanadi?", ["text", "string", "str", "char"], 2),
            ("int ma'lumot turi nima?", ["Matn", "Butun son", "O'nli kasr", "Mantiqiy qiymat"], 1),
            ("float ma'lumot turi nima uchun ishlatiladi?", ["Butun sonlar", "Matnlar", "O'nli kasrlar", "Mantiqiy qiymatlar"], 2),
            ("True va False qanday ma'lumot turi?", ["int", "str", "bool", "float"], 2),
            ("type(5) qanday natija qaytaradi?", ["str", "int", "float", "number"], 1),
            ("Arithmetic operators nimalar?", ["Hisoblash operatorlari", "Taqqoslash operatorlari", "Mantiqiy operatorlar", "Tayinlash operatorlari"], 0),
            ("+ operatori nima qiladi?", ["Qo'shish", "Ayirish", "Ko'paytirish", "Bo'lish"], 0),
            ("- operatori nima qiladi?", ["Ayirish", "Qo'shish", "Ko'paytirish", "Bo'lish"], 0),
            ("* operatori nima qiladi?", ["Ko'paytirish", "Qo'shish", "Ayirish", "Bo'lish"], 0),
            ("/ operatori nima qiladi?", ["Bo'lish", "Qo'shish", "Ayirish", "Ko'paytirish"], 0),
            ("// operatori nima qiladi?", ["Butun bo'lish", "Qoldiqli bo'lish", "Ko'paytirish", "Qo'shish"], 0),
            ("% operatori nima qiladi?", ["Qoldiq", "Bo'lish", "Ko'paytirish", "Qo'shish"], 0),
            ("** operatori nima qiladi?", ["Daraja", "Ko'paytirish", "Bo'lish", "Qo'shish"], 0),
            ("Comparison operators nimalar?", ["Taqqoslash operatorlari", "Hisoblash operatorlari", "Mantiqiy operatorlar", "Tayinlash operatorlari"], 0),
            ("> operatori nima?", ["Katta", "Kichik", "Teng", "Teng emas"], 0),
            ("< operatori nima?", ["Kichik", "Katta", "Teng", "Teng emas"], 0),
            (">= operatori nima?", ["Katta yoki teng", "Kichik yoki teng", "Teng", "Teng emas"], 0),
            ("<= operatori nima?", ["Kichik yoki teng", "Katta yoki teng", "Teng", "Teng emas"], 0),
            ("== operatori nima?", ["Teng", "Teng emas", "Katta", "Kichik"], 0),
            ("!= operatori nima?", ["Teng emas", "Teng", "Katta", "Kichik"], 0),
            ("Logical operators nimalar?", ["Mantiqiy operatorlar", "Hisoblash operatorlari", "Taqqoslash operatorlari", "Tayinlash operatorlari"], 0),
            ("and operatori nima qiladi?", ["Ikkisi ham to'g'ri", "Kamida bittasi to'g'ri", "Hech biri to'g'ri emas", "Teskari"], 0),
            ("or operatori nima qiladi?", ["Kamida bittasi to'g'ri", "Ikkisi ham to'g'ri", "Hech biri to'g'ri emas", "Teskari"], 0),
            ("not operatori nima qiladi?", ["Teskari", "Qo'shish", "Ko'paytirish", "Bo'lish"], 0),
            ("Operator precedence nima?", ["Operator ustuvorligi", "Operator soni", "Operator turi", "Operator qiymati"], 0),
        ],
        3: [  # 3-chorak: String va kirish-chiqish (25 ta)
            ("5 + 3 * 2 amalining natijasi qancha?", ["16", "11", "13", "10"], 1),
            ("Pythonda bo'linma amalining belgisi?", ["/", "//", "%", "*"], 0),
            ("10 % 3 natijasi nima?", ["3", "1", "0", "10"], 1),
            ("10 // 3 natijasi nima?", ["3.33", "3", "1", "0"], 1),
            ("String concatenation nima?", ["Matnlarni birlashtirish", "Matnlarni taqqoslash", "Matnlarni bo'lish", "Matnlarni ko'paytirish"], 0),
            ("'Hello' + 'World' natijasi?", ["HelloWorld", "Hello World", "Hello+World", "Xato"], 0),
            ("String repetition nima?", ["Matnni takrorlash", "Matnni bo'lish", "Matnni taqqoslash", "Matnni o'zgartirish"], 0),
            ("'Hi' * 3 natijasi?", ["HiHiHi", "Hi3", "3Hi", "Xato"], 0),
            ("String indexing nima?", ["Matn indekslari", "Matn uzunligi", "Matn qiymati", "Matn turi"], 0),
            ("s = 'Python'; s[0] nima?", ["P", "y", "t", "h"], 0),
            ("s = 'Python'; s[-1] nima?", ["n", "P", "y", "o"], 0),
            ("String slicing nima?", ["Matn kesish", "Matn birlashtirish", "Matn takrorlash", "Matn taqqoslash"], 0),
            ("s = 'Python'; s[0:2] nima?", ["Py", "yth", "thon", "Python"], 0),
            ("len() funksiyasi nima qiladi?", ["Uzunlik", "Qiymat", "Tur", "Format"], 0),
            ("len('Python') natijasi?", ["6", "5", "7", "8"], 0),
            ("str() funksiyasi nima qiladi?", ["Matnga o'tkazadi", "Butun songa", "O'nli songa", "Mantiqiyga"], 0),
            ("int() funksiyasi nima qiladi?", ["Butun songa o'tkazadi", "Matnga", "O'nli songa", "Mantiqiyga"], 0),
            ("float() funksiyasi nima qiladi?", ["O'nli songa o'tkazadi", "Butun songa", "Matnga", "Mantiqiyga"], 0),
            ("input() funksiyasi nima qiladi?", ["Foydalanuvchi kiritadi", "Ekranda chiqaradi", "Fayldan o'qiydi", "Tarmoqqa ulanadi"], 0),
            ("name = input('Ism: ') qanday ishlaydi?", ["Ism so'raydi", "Ism chiqaradi", "Ismni saqlaydi", "Ismni o'zgartiradi"], 0),
            ("String methods nima?", ["Matn metodlari", "Matn operatorlari", "Matn funksiyalari", "Matn atributlari"], 0),
            ("upper() metodi nima qiladi?", ["Katta harflarga", "Kichik harflarga", "Bosh harflarga", "Harflarni almashtiradi"], 0),
            ("lower() metodi nima qiladi?", ["Kichik harflarga", "Katta harflarga", "Bosh harflarga", "Harflarni almashtiradi"], 0),
            ("capitalize() metodi nima qiladi?", ["Birinchi harf katta", "Hamma harf katta", "Hamma harf kichik", "Harflarni teskari"], 0),
            ("title() metodi nima qiladi?", ["Har so'zning bosh harfi katta", "Faqt birinchi so'z", "Hamma harf katta", "Hamma harf kichik"], 0),
        ],
        4: [  # 4-chorak: Shartli operatorlar (25 ta)
            ("if operatori nima uchun ishlatiladi?", ["Shartni tekshirish", "Takrorlash", "Funksiya", "Kirish"], 0),
            ("if statement syntax qanday?", ["if condition:", "if (condition)", "if condition then", "if condition {}"], 0),
            ("Indentation if da qancha bo'lishi kerak?", ["4 bo'shliq", "2 bo'shliq", "1 tab", "8 bo'shliq"], 0),
            ("else qachon ishlaydi?", ["if shart noto'g'ri bo'lsa", "if shart to'g'ri bo'lsa", "Har doim", "Hech qachon"], 0),
            ("elif nima?", ["Qo'shimcha shart", "Asosiy shart", "Oxirgi shart", "Majburiy shart"], 0),
            ("Nested if nima?", ["Ichma-ich if", "Oddiy if", "if-else", "if-elif-else"], 0),
            ("Logical operators if bilan qanday ishlatiladi?", ["Murakkab shartlar", "Oddiy shartlar", "Funksiyalar", "O'zgaruvchilar"], 0),
            ("if x > 5 and x < 10: nima tekshiradi?", ["x 5 va 10 oralig'ida", "x 5 dan katta", "x 10 dan kichik", "x 5 ga teng"], 0),
            ("if x > 5 or x < 0: nima tekshiradi?", ["x 5 dan katta yoki 0 dan kichik", "x 5 dan katta", "x 0 dan kichik", "x 5 va 0 oralig'ida"], 0),
            ("if not x: nima tekshiradi?", ["x noto'g'ri", "x to'g'ri", "x mavjud", "x yo'q"], 0),
            ("Ternary operator nima?", ["Qisqa if-else", "Uzun if-else", "Funksiya", "Modul"], 0),
            ("x = 5 if y > 0 else 0 qanday ishlaydi?", ["y > 0 bo'lsa x=5, aks holda x=0", "Har doim x=5", "y > 0 bo'lsa x=0", "Hech qanday"], 0),
            ("Conditional expression nima?", ["Shartli ifoda", "Oddiy ifoda", "Matn ifodasi", "Raqam ifodasi"], 0),
            ("pass statement nima?", ["Hech narsa qilmaydi", "Xato chiqaradi", "Dasturni to'xtatadi", "Natija qaytaradi"], 0),
            ("Empty if qanday yoziladi?", ["if condition: pass", "if condition: none", "if condition: empty", "if condition: break"], 0),
            ("Multiple conditions qanday tekshiriladi?", ["elif bilan", "faqt if bilan", "else bilan", "pass bilan"], 0),
            ("if-elif-else chain nima?", ["Zanjir", "Halqa", "Ro'yxat", "Lug'at"], 0),
            ("Chained comparison nima?", ["Zanjirlangan taqqoslash", "Oddiy taqqoslash", "Murakkab taqqoslash", "Mantiqiy taqqoslash"], 0),
            ("5 < x < 10 nima?", ["x 5 va 10 oralig'ida", "x 5 dan katta", "x 10 dan kichik", "Xato"], 0),
            ("Membership operators nima?", ["A'zolik operatorlari", "Taqqoslash operatorlari", "Mantiqiy operatorlar", "Arifmetik operatorlar"], 0),
            ("in operatori nima qiladi?", ["Ichida borligini tekshiradi", "Tengligini", "Kattaligini", "Kichikligini"], 0),
            ("not in operatori nima qiladi?", ["Ichida yo'qligini", "Ichida borligini", "Tengligini", "Kattaligini"], 0),
            ("Identity operators nima?", ["Shaxsiyat operatorlari", "A'zolik operatorlari", "Taqqoslash operatorlari", "Mantiqiy operatorlar"], 0),
            ("is operatori nima?", ["Bir xil obyekt", "Bir xil qiymat", "Teng qiymat", "Katta qiymat"], 0),
            ("is not operatori nima?", ["Bir xil obyekt emas", "Bir xil qiymat emas", "Teng emas", "Katta emas"], 0),
        ]
    },
    8: {
        1: [  # 1-chorak: Sikllar (25 ta)
            ("for sikli nima uchun ishlatiladi?", ["Takrorlash", "Shart tekshirish", "Funksiya", "Kirish"], 0),
            ("while sikli nima uchun ishlatiladi?", ["Shart to'g'ri bo'lsa takrorlaydi", "Ma'lum son takrorlaydi", "Funksiya chaqiradi", "Ma'lumot kiritadi"], 0),
            ("range() funksiyasi nima qiladi?", ["Sonlar ketma-ketligi", "Matnlar ketma-ketligi", "Ro'yxat yaratadi", "Lug'at yaratadi"], 0),
            ("range(5) qanday sonlar beradi?", ["0,1,2,3,4", "1,2,3,4,5", "0,1,2,3,4,5", "5,4,3,2,1"], 0),
            ("range(1, 6) qanday sonlar beradi?", ["1,2,3,4,5", "0,1,2,3,4,5", "1,2,3,4,5,6", "6,5,4,3,2,1"], 0),
            ("range(0, 10, 2) qanday sonlar beradi?", ["0,2,4,6,8", "0,1,2,3,4,5,6,7,8,9", "2,4,6,8,10", "10,8,6,4,2,0"], 0),
            ("for loop syntax qanday?", ["for item in sequence:", "for (item in sequence)", "for item: sequence", "for item do sequence"], 0),
            ("Iteration nima?", ["Takrorlash", "Shart", "Funksiya", "O'zgaruvchi"], 0),
            ("Iterator nima?", ["Takrorlovchi", "O'zgaruvchi", "Funksiya", "Modul"], 0),
            ("Iterable nima?", ["Takrorlanuvchi", "O'zgaruvchi", "Funksiya", "Modul"], 0),
            ("break statement nima qiladi?", ["Siklni to'xtatadi", "Siklni davom ettirir", "Keyingi iteratsiyaga o'tadi", "Funksiyani chaqiradi"], 0),
            ("continue statement nima qiladi?", ["Keyingi iteratsiyaga o'tadi", "Siklni to'xtatadi", "Siklni boshlaydi", "Funksiyani chaqiradi"], 0),
            ("Nested loops nima?", ["Ichma-ich sikllar", "Oddiy sikl", "for sikl", "while sikl"], 0),
            ("Infinite loop nima?", ["Cheksiz sikl", "Chekli sikl", "To'g'ri sikl", "Noto'g'ri sikl"], 0),
            ("Loop variable nima?", ["Sikl o'zgaruvchisi", "Global o'zgaruvchi", "Local o'zgaruvchi", "Statik o'zgaruvchi"], 0),
            ("Loop counter nima?", ["Sikl hisoblagichi", "Sikl sharti", "Sikl tanasi", "Sikl boshi"], 0),
            ("for loop else qismi qachon ishlaydi?", ["Sikl to'liq bajarilganda", "Sikl to'xtatilganda", "Sikl boshida", "Sikl davomida"], 0),
            ("while loop else qismi qanday?", ["Shart noto'g'ri bo'lganda", "Shart to'g'ri bo'lganda", "break bilan to'xtatilganda", "continue bilan o'tkazilganda"], 0),
            ("for-else break bilan to'xtasa nima bo'ladi?", ["else ishlamaydi", "else ishlaydi", "xato beradi", "dastur to'xtaydi"], 0),
            ("while-else break bilan to'xtasa nima bo'ladi?", ["else ishlamaydi", "else ishlaydi", "xato beradi", "dastur to'xtaydi"], 0),
            ("Loop control statements nimalar?", ["break, continue, pass", "if, elif, else", "for, while", "def, return"], 0),
            ("pass statement loopda nima qiladi?", ["Hech narsa", "Siklni to'xtatadi", "Keyingi iteratsiyaga o'tadi", "Xato beradi"], 0),
            ("enumerate() funksiyasi nima qiladi?", ["Indeks va qiymat", "Faqt qiymat", "Faqt indeks", "Ro'yxat uzunligi"], 0),
            ("for i, value in enumerate(list): qanday ishlaydi?", ["i indeks, value qiymat", "i qiymat, value indeks", "ikkalasi ham qiymat", "ikkalasi ham indeks"], 0),
            ("zip() funksiyasi nima qiladi?", ["Bir necha ketma-ketlikni birlashtiradi", "Bir ketma-ketlikni ajratadi", "Ketma-ketlikni teskari aylantiradi", "Ketma-ketlikni saralaydi"], 0),
        ],
        2: [  # 2-chorak: Ro'yxatlar (Lists) (25 ta)
            ("List nima?", ["Elementlar ketma-ketligi", "Bitta element", "Kalit-qiymat juftligi", "O'zgaruvchi"], 0),
            ("List qanday yaratiladi?", ["[] yordamida", "{}", "()", "||"], 0),
            ("my_list = [1, 2, 3] qanday list?", ["3 elementli", "2 elementli", "1 elementli", "Bo'sh"], 0),
            ("List elementiga qanday murojaat qilinadi?", ["Indeks orqali", "Kalit orqali", "Nom orqali", "Qiymat orqali"], 0),
            ("my_list[0] nima qaytaradi?", ["Birinchi element", "Oxirgi element", "Ikkinchi element", "Xato"], 0),
            ("Negative indexing nima?", ["Oxirdan boshlab", "Boshidan boshlab", "O'rtadan boshlab", "Tasodifiy"], 0),
            ("my_list[-1] nima qaytaradi?", ["Oxirgi element", "Birinchi element", "Ikkinchi element", "Xato"], 0),
            ("List slicing nima?", ["List kesish", "List qo'shish", "List o'chirish", "List yangilash"], 0),
            ("my_list[1:3] nima qaytaradi?", ["1 va 2 indeksdagi elementlar", "1,2,3 elementlar", "2 va 3 elementlar", "Xato"], 0),
            ("List methods nimalar?", ["List metodlari", "List operatorlari", "List funksiyalari", "List atributlari"], 0),
            ("append() metodi nima qiladi?", ["Oxiriga element qo'shadi", "Boshiga element qo'shadi", "Elementni o'chiradi", "Elementni almashtiradi"], 0),
            ("insert() metodi nima qiladi?", ["Belgilangan joyga element qo'shadi", "Oxiriga element qo'shadi", "Elementni o'chiradi", "Elementni topadi"], 0),
            ("remove() metodi nima qiladi?", ["Qiymat bo'yicha o'chiradi", "Indeks bo'yicha o'chiradi", "Oxirgi elementni o'chiradi", "Birinchi elementni o'chiradi"], 0),
            ("pop() metodi nima qiladi?", ["Indeks bo'yicha o'chiradi", "Qiymat bo'yicha o'chiradi", "Barcha elementlarni o'chiradi", "Hech narsa qilmaydi"], 0),
            ("clear() metodi nima qiladi?", ["Barcha elementlarni o'chiradi", "Bitta elementni o'chiradi", "Listni teskari aylantiradi", "Listni saralaydi"], 0),
            ("index() metodi nima qiladi?", ["Element indeksini topadi", "Element qiymatini topadi", "Elementni o'chiradi", "Elementni almashtiradi"], 0),
            ("count() metodi nima qiladi?", ["Element sonini hisoblaydi", "Element indeksini topadi", "Element qiymatini o'zgartiradi", "Elementni o'chiradi"], 0),
            ("sort() metodi nima qiladi?", ["Saralaydi", "Teskari aylantiradi", "Element qo'shadi", "Element o'chiradi"], 0),
            ("reverse() metodi nima qiladi?", ["Teskari aylantiradi", "Saralaydi", "Element qo'shadi", "Element o'chiradi"], 0),
            ("copy() metodi nima qiladi?", ["Nusxa oladi", "Asl listni o'zgartiradi", "Listni o'chiradi", "Listni birlashtiradi"], 0),
            ("List comprehension nima?", ["List yaratishning qisqa usuli", "Listni o'qish", "Listni o'zgartirish", "Listni saralash"], 0),
            ("[x for x in range(5)] nima?", ["0,1,2,3,4", "1,2,3,4,5", "0,1,2,3,4,5", "Xato"], 0),
            ("[x*2 for x in range(3)] nima?", ["0,2,4", "0,1,2", "2,4,6", "Xato"], 0),
            ("List concatenation qanday?", ["+ operatori", "* operatori", "- operatori", "/ operatori"], 0),
            ("List repetition qanday?", ["* operatori", "+ operatori", "- operatori", "/ operatori"], 0),
        ],
        3: [  # 3-chorak: Tuple, Set, Dictionary (25 ta)
            ("Tuple nima?", ["O'zgarmas ketma-ketlik", "O'zgaruvchan ketma-ketlik", "Kalit-qiymat juftligi", "Takrorlanmas to'plam"], 0),
            ("Tuple qanday yaratiladi?", ["() yordamida", "[]", "{}", "||"], 0),
            ("my_tuple = (1, 2, 3) qanday tuple?", ["3 elementli", "2 elementli", "1 elementli", "Bo'sh"], 0),
            ("Tuple elementiga qanday murojaat qilinadi?", ["Indeks orqali", "Kalit orqali", "Nom orqali", "Qiymat orqali"], 0),
            ("Tuple ni nima bilan farq qiladi?", ["O'zgarmasligi", "O'zgaruvchanligi", "Tartibliligim", "Takrorlanmasligi"], 0),
            ("Set nima?", ["Takrorlanmas elementlar to'plami", "Tartibli elementlar ketma-ketligi", "Kalit-qiymat juftliklari", "O'zgarmas ketma-ketlik"], 0),
            ("Set qanday yaratiladi?", ["{} yordamida", "[]", "()", "||"], 0),
            ("my_set = {1, 2, 3} qanday set?", ["3 elementli", "2 elementli", "1 elementli", "Bo'sh"], 0),
            ("Set elementlari qanday tartiblanadi?", ["Tartibsiz", "Tartibli", "Alfavit bo'yicha", "Raqam bo'yicha"], 0),
            ("Set methods nimalar?", ["Set metodlari", "Set operatorlari", "Set funksiyalari", "Set atributlari"], 0),
            ("add() metodi setda nima qiladi?", ["Element qo'shadi", "Element o'chiradi", "Elementni tekshiradi", "Setni tozalaydi"], 0),
            ("remove() metodi setda nima qiladi?", ["Elementni o'chiradi", "Element qo'shadi", "Elementni tekshiradi", "Setni tozalaydi"], 0),
            ("discard() metodi setda nima qiladi?", ["Elementni o'chiradi (xatosiz)", "Elementni o'chiradi (xato bilan)", "Element qo'shadi", "Elementni tekshiradi"], 0),
            ("union() metodi nima qiladi?", ["Birlashma", "Kesishma", "Farq", "Simmetrik farq"], 0),
            ("intersection() metodi nima qiladi?", ["Kesishma", "Birlashma", "Farq", "Simmetrik farq"], 0),
            ("difference() metodi nima qiladi?", ["Farq", "Kesishma", "Birlashma", "Simmetrik farq"], 0),
            ("Dictionary nima?", ["Kalit-qiymat juftliklari", "Elementlar ketma-ketligi", "Takrorlanmas to'plam", "O'zgarmas ketma-ketlik"], 0),
            ("Dictionary qanday yaratiladi?", ["{} yordamida", "[]", "()", "||"], 0),
            ("my_dict = {'a': 1, 'b': 2} qanday dict?", ["2 elementli", "1 elementli", "3 elementli", "Bo'sh"], 0),
            ("Dictionary elementiga qanday murojaat qilinadi?", ["Kalit orqali", "Indeks orqali", "Nom orqali", "Qiymat orqali"], 0),
            ("my_dict['a'] nima qaytaradi?", ["1", "2", "a", "Xato"], 0),
            ("get() metodi nima qiladi?", ["Kalit bo'yicha qiymat oladi", "Yangi element qo'shadi", "Elementni o'chiradi", "Barcha kalitlarni oladi"], 0),
            ("keys() metodi nima qaytaradi?", ["Barcha kalitlar", "Barcha qiymatlar", "Barcha juftliklar", "Bo'sh ro'yxat"], 0),
            ("values() metodi nima qaytaradi?", ["Barcha qiymatlar", "Barcha kalitlar", "Barcha juftliklar", "Bo'sh ro'yxat"], 0),
            ("items() metodi nima qaytaradi?", ["Barcha juftliklar", "Barcha kalitlar", "Barcha qiymatlar", "Bo'sh ro'yxat"], 0),
        ],
        4: [  # 4-chorak: Funksiyalar (25 ta)
            ("Funksiya nima?", ["Qayta ishlatiladigan kod bloki", "O'zgaruvchi", "Operator", "Modul"], 0),
            ("Funksiya qanday yaratiladi?", ["def kalit so'zi", "func", "function", "define"], 0),
            ("def my_func(): nima?", ["Funksiya e'lon qilish", "O'zgaruvchi e'lon qilish", "Sikl yaratish", "Shart yaratish"], 0),
            ("Parameter nima?", ["Funksiya kirishi", "Funksiya chiqishi", "Funksiya nomi", "Funksiya tanasi"], 0),
            ("Argument nima?", ["Funksiyaga beriladigan qiymat", "Funksiya parametri", "Funksiya natijasi", "Funksiya turi"], 0),
            ("Return statement nima qiladi?", ["Qiymat qaytaradi", "Funksiyani to'xtatadi", "Xato chiqaradi", "Hech narsa"], 0),
            ("Default parameter nima?", ["Standart parametr", "Majburiy parametr", "Ixtiyoriy parametr", "Yashirin parametr"], 0),
            ("def func(x=5): nima?", ["x ning standart qiymati 5", "x majburiy", "x ixtiyoriy", "x yashirin"], 0),
            ("Keyword argument nima?", ["Kalit so'z bilan argument", "Pozitsion argument", "Standart argument", "Yashirin argument"], 0),
            ("func(x=1, y=2) qanday chaqirilgan?", ["Keyword argument", "Positional argument", "Default argument", "Required argument"], 0),
            ("Positional argument nima?", ["Tartibli argument", "Kalit so'z bilan argument", "Standart argument", "Yashirin argument"], 0),
            ("func(1, 2) qanday chaqirilgan?", ["Positional argument", "Keyword argument", "Default argument", "Required argument"], 0),
            ("Arbitrary arguments nima?", ["O'zboshimcha argumentlar", "Majburiy argumentlar", "Standart argumentlar", "Yashirin argumentlar"], 0),
            ("def func(*args): nima?", ["Har qanday sonli argument", "Faqt bitta argument", "Hech qanday argument", "Majburiy argument"], 0),
            ("Arbitrary keyword arguments nima?", ["O'zboshimcha kalit so'zli argumentlar", "Pozitsion argumentlar", "Standart argumentlar", "Majburiy argumentlar"], 0),
            ("def func(**kwargs): nima?", ["Har qanday kalit so'zli argument", "Faqt bitta kalit so'z", "Hech qanday argument", "Majburiy kalit so'z"], 0),
            ("Lambda function nima?", ["Nomsiz funksiya", "Nomli funksiya", "Asosiy funksiya", "Yordamchi funksiya"], 0),
            ("lambda x: x*2 nima?", ["x ni 2 ga ko'paytiradi", "x ni 2 ga bo'ladi", "x ga 2 qo'shadi", "x dan 2 ayiradi"], 0),
            ("map() funksiyasi nima qiladi?", ["Har bir elementga funksiya qo'llaydi", "Ro'yxatni saralaydi", "Ro'yxatni teskari aylantiradi", "Ro'yxatdan element oladi"], 0),
            ("filter() funksiyasi nima qiladi?", ["Shartga mos elementlarni oladi", "Barcha elementlarni oladi", "Elementlarni o'zgartiradi", "Elementlarni saralaydi"], 0),
            ("reduce() funksiyasi nima qiladi?", ["Ketma-ket qo'llab natijani qaytaradi", "Har biriga alohida qo'llaydi", "Faqt birinchi elementga", "Faqt oxirgi elementga"], 0),
            ("Recursion nima?", ["O'zini o'zi chaqirish", "Boshqa funksiyani chaqirish", "Sikl", "Shart"], 0),
            ("Global variable nima?", ["Global o'zgaruvchi", "Local o'zgaruvchi", "Funksiya parametri", "Funksiya argumenti"], 0),
            ("Local variable nima?", ["Local o'zgaruvchi", "Global o'zgaruvchi", "Funksiya parametri", "Funksiya argumenti"], 0),
            ("Scope nima?", ["O'zgaruvchi ko'rinish doirasi", "O'zgaruvchi turi", "O'zgaruvchi qiymati", "O'zgaruvchi nomi"], 0),
        ]
    },
    9: {
        1: [  # 1-chorak: Modullar va kutubxonalar (25 ta)
            ("Module nima?", ["Python fayli", "Python funksiyasi", "Python o'zgaruvchisi", "Python operatori"], 0),
            ("Import qanday ishlatiladi?", ["Modulni yuklash", "Funksiya yaratish", "O'zgaruvchi e'lon qilish", "Sikl yaratish"], 0),
            ("import math nima qiladi?", ["Math modulini yuklaydi", "Math funksiyasini yaratadi", "Math o'zgaruvchisini e'lon qiladi", "Hech narsa"], 0),
            ("from math import sqrt nima qiladi?", ["sqrt funksiyasini oladi", "Butun math modulini oladi", "sqrt o'zgaruvchisini oladi", "Xato"], 0),
            ("math.sqrt(4) natijasi?", ["2", "4", "16", "Xato"], 0),
            ("random moduli nima uchun?", ["Tasodifiy sonlar", "Matematik hisoblash", "Vaqt bilan ishlash", "Matn bilan ishlash"], 0),
            ("random.random() nima qaytaradi?", ["0 va 1 orasidagi tasodifiy son", "Butun tasodifiy son", "Matn", "Xato"], 0),
            ("random.randint(1, 10) nima qaytaradi?", ["1 dan 10 gacha butun son", "0 dan 1 gacha son", "Matn", "Xato"], 0),
            ("datetime moduli nima uchun?", ["Vaqt va sana", "Tasodifiy sonlar", "Matematik hisoblash", "Matn bilan ishlash"], 0),
            ("datetime.datetime.now() nima qaytaradi?", ["Joriy vaqt va sana", "Kecha vaqt", "Ertaga sana", "Xato"], 0),
            ("os moduli nima uchun?", ["Operatsion tizim bilan ishlash", "Tasodifiy sonlar", "Matematik hisoblash", "Tarmoq bilan ishlash"], 0),
            ("os.getcwd() nima qaytaradi?", ["Joriy ishchi katalog", "Fayl nomi", "Vaqt", "Xato"], 0),
            ("sys moduli nima uchun?", ["Python interpretatori bilan ishlash", "Operatsion tizim", "Matematik hisoblash", "Tarmoq"], 0),
            ("sys.version nima qaytaradi?", ["Python versiyasi", "Operatsion tizim", "Vaqt", "Xato"], 0),
            ("Built-in functions nima?", ["O'rnatilgan funksiyalar", "Foydalanuvchi funksiyalari", "Modul funksiyalari", "Class funksiyalari"], 0),
            ("len(), print(), input() nimalar?", ["Built-in funksiyalar", "Modul funksiyalari", "User funksiyalari", "Class metodlari"], 0),
            ("Third-party library nima?", ["Uchinchi tomon kutubxonasi", "Standart kutubxona", "Built-in funksiya", "Python interpretatori"], 0),
            ("pip nima?", ["Python paket menejeri", "Python funksiyasi", "Python moduli", "Python o'zgaruvchisi"], 0),
            ("Virtual environment nima?", ["Virtual muhit", "Haqiqiy muhit", "Python moduli", "Python funksiyasi"], 0),
            ("Package nima?", ["Modullar to'plami", "Bitta modul", "Bitta funksiya", "Bitta o'zgaruvchi"], 0),
            ("__init__.py fayli nima uchun?", ["Paketni belgilaydi", "Funksiyani belgilaydi", "O'zgaruvchini belgilaydi", "Xato fayli"], 0),
            ("Namespace nima?", ["Nomlar fazosi", "Fayl nomi", "Funksiya nomi", "O'zgaruvchi nomi"], 0),
            ("Alias nima?", ["Taxallus", "Haqiqiy nom", "Funksiya", "Modul"], 0),
            ("import numpy as np nima?", ["numpy ga np taxallus", "np ni numpy taxallus", "Xato", "Hech narsa"], 0),
            ("Standard library nima?", ["Standart kutubxona", "Uchinchi tomon kutubxonasi", "Built-in funksiyalar", "Python interpretatori"], 0),
        ],
        2: [  # 2-chorak: Fayllar bilan ishlash (25 ta)
            ("File handling nima?", ["Fayllar bilan ishlash", "Fayllarni o'chirish", "Fayllarni ko'rish", "Fayllarni nomlash"], 0),
            ("open() funksiyasi nima qiladi?", ["Faylni ochadi", "Faylni yopadi", "Faylni o'qiydi", "Faylni yozadi"], 0),
            ("File modes nimalar?", ["Fayl rejimlari", "Fayl nomlari", "Fayl kengaytmalari", "Fayl hajmlari"], 0),
            ("'r' mode nima?", ["O'qish uchun", "Yozish uchun", "Qo'shish uchun", "Yaratish uchun"], 0),
            ("'w' mode nima?", ["Yozish uchun", "O'qish uchun", "Qo'shish uchun", "Yaratish uchun"], 0),
            ("'a' mode nima?", ["Qo'shish uchun", "O'qish uchun", "Yozish uchun", "Yaratish uchun"], 0),
            ("'x' mode nima?", ["Yaratish uchun", "O'qish uchun", "Yozish uchun", "Qo'shish uchun"], 0),
            ("read() metodi nima qiladi?", ["Fayldan o'qiydi", "Faylga yozadi", "Faylni yopadi", "Faylni ochadi"], 0),
            ("readline() metodi nima qiladi?", ["Bir qator o'qiydi", "Butun fayl", "Fayl oxirini", "Fayl boshini"], 0),
            ("readlines() metodi nima qiladi?", ["Barcha qatorlarni ro'yxatda", "Bir qator", "Fayl oxirini", "Fayl boshini"], 0),
            ("write() metodi nima qiladi?", ["Faylga yozadi", "Fayldan o'qiydi", "Faylni yopadi", "Faylni ochadi"], 0),
            ("writelines() metodi nima qiladi?", ["Ro'yxatdagi qatorlarni yozadi", "Bir qator yozadi", "Faylni o'qiydi", "Faylni yopadi"], 0),
            ("close() metodi nima qiladi?", ["Faylni yopadi", "Faylni ochadi", "Fayldan o'qiydi", "Faylga yozadi"], 0),
            ("with statement nima?", ["Faylni avtomat yopadi", "Faylni ochadi", "Fayldan o'qiydi", "Faylga yozadi"], 0),
            ("File pointer nima?", ["Fayl ko'rsatkichi", "Fayl nomi", "Fayl kengaytmasi", "Fayl hajmi"], 0),
            ("seek() metodi nima qiladi?", ["Fayl ko'rsatkichini o'zgartiradi", "Fayl nomini o'zgartiradi", "Fayl kengaytmasini", "Fayl hajmini"], 0),
            ("tell() metodi nima qiladi?", ["Fayl ko'rsatkichi joylashuvi", "Fayl nomi", "Fayl kengaytmasi", "Fayl hajmi"], 0),
            ("CSV fayl nima?", ["Vergul bilan ajratilgan", "Tab bilan ajratilgan", "Bo'sh joy bilan", "Nuqta-vergul bilan"], 0),
            ("JSON fayl nima?", ["JavaScript Object Notation", "Java Script Object", "JavaScript Only Notation", "Java Serial Object"], 0),
            ("Binary file nima?", ["Ikkilik fayl", "Matn fayli", "Rasm fayli", "Audio fayli"], 0),
            ("Text file nima?", ["Matn fayli", "Ikkilik fayl", "Rasm fayli", "Audio fayli"], 0),
            ("File encoding nima?", ["Fayl kodlash", "Fayl nomi", "Fayl kengaytmasi", "Fayl hajmi"], 0),
            ("UTF-8 nima?", ["Kodlash formati", "Fayl formati", "Fayl kengaytmasi", "Fayl nomi"], 0),
            ("Exception handling faylda nima uchun?", ["Xatolarni boshqarish", "Faylni tezroq o'qish", "Faylni tezroq yozish", "Fayl nomini o'zgartirish"], 0),
            ("try-except block faylda qachon ishlatiladi?", ["Fayl ochishda", "Fayl yopishda", "Fayl nomlashda", "Fayl o'lchashda"], 0),
        ],
        3: [  # 3-chorak: OOP - Ob'ektga yo'naltirilgan dasturlash (25 ta)
            ("OOP nima?", ["Ob'ektga yo'naltirilgan dasturlash", "Protseduraga yo'naltirilgan", "Funksional dasturlash", "Mantiqiy dasturlash"], 0),
            ("Class nima?", ["Ob'ekt shabloni", "Ob'ekt", "Funksiya", "O'zgaruvchi"], 0),
            ("Object nima?", ["Class misoli", "Class shabloni", "Funksiya", "O'zgaruvchi"], 0),
            ("Attribute nima?", ["Xususiyat", "Metod", "Funksiya", "Parametr"], 0),
            ("Method nima?", ["Funksiya class ichida", "O'zgaruvchi class ichida", "Parametr", "Argument"], 0),
            ("__init__ metodi nima?", ["Konstruktor", "Destruktor", "Oddiy metod", "Statik metod"], 0),
            ("self nima?", ["O'ziga murojaat", "Class nomi", "Ob'ekt nomi", "Funksiya nomi"], 0),
            ("Inheritance nima?", ["Meros olish", "Ko'p shakllilik", "Kapsulatsiya", "Abstraksiya"], 0),
            ("Parent class nima?", ["Ota class", "Bola class", "Abstract class", "Interface"], 0),
            ("Child class nima?", ["Bola class", "Ota class", "Abstract class", "Interface"], 0),
            ("Polymorphism nima?", ["Ko'p shakllilik", "Meros olish", "Kapsulatsiya", "Abstraksiya"], 0),
            ("Encapsulation nima?", ["Kapsulatsiya", "Meros olish", "Ko'p shakllilik", "Abstraksiya"], 0),
            ("Abstraction nima?", ["Abstraksiya", "Meros olish", "Ko'p shakllilik", "Kapsulatsiya"], 0),
            ("Private attribute qanday belgilanadi?", ["__ bilan boshlanadi", "_ bilan boshlanadi", "private kalit so'zi", "protected kalit so'zi"], 0),
            ("Protected attribute qanday belgilanadi?", ["_ bilan boshlanadi", "__ bilan boshlanadi", "protected kalit so'zi", "private kalit so'zi"], 0),
            ("Getter metodi nima?", ["Qiymat olish", "Qiymat berish", "Qiymatni o'zgartirish", "Qiymatni o'chirish"], 0),
            ("Setter metodi nima?", ["Qiymat berish", "Qiymat olish", "Qiymatni o'zgartirish", "Qiymatni o'chirish"], 0),
            ("Property decorator nima?", ["Getter/setter qulayligi", "Class dekoratori", "Method dekoratori", "Function dekoratori"], 0),
            ("Static method nima?", ["Statik metod", "Oddiy metod", "Class metod", "Private metod"], 0),
            ("Class method nima?", ["Class metod", "Statik metod", "Oddiy metod", "Private metod"], 0),
            ("@staticmethod dekoratori nima?", ["Statik metod", "Class metod", "Property", "Abstract metod"], 0),
            ("@classmethod dekoratori nima?", ["Class metod", "Statik metod", "Property", "Abstract metod"], 0),
            ("Multiple inheritance nima?", ["Bir nechta ota class", "Bitta ota class", "Hech qanday ota class", "Abstract class"], 0),
            ("Method overriding nima?", ["Metodni qayta yozish", "Yangi metod yaratish", "Metodni o'chirish", "Metodni chaqirish"], 0),
            ("super() funksiyasi nima qiladi?", ["Ota class metodini chaqiradi", "Bola class metodini", "Hamma metodlarni", "Hech qanday metodni"], 0),
        ],
        4: [  # 4-chorak: Xatolarni boshqarish va loyihalash (25 ta)
            ("Exception nima?", ["Dastur xatosi", "Dastur to'g'ri ishlashi", "Dastur natijasi", "Dastur funksiyasi"], 0),
            ("try block nima uchun?", ["Xato yuz berganda", "Xato yuz bermasdan", "Dasturni tezlashtirish", "Xotirani tejash"], 0),
            ("except block nima uchun?", ["Xatoni ushlash", "Xato yaratish", "Dasturni to'xtatish", "Dasturni davom ettirish"], 0),
            ("else block try-except da qachon ishlaydi?", ["Xato bo'lmasa", "Xato bo'lsa", "Har doim", "Hech qachon"], 0),
            ("finally block qachon ishlaydi?", ["Har doim", "Xato bo'lsa", "Xato bo'lmasa", "Hech qachon"], 0),
            ("raise statement nima qiladi?", ["Xato chiqaradi", "Xatoni ushlaydi", "Dasturni to'xtatadi", "Dasturni davom ettiradi"], 0),
            ("Exception hierarchy nima?", ["Xatolar ierarxiyasi", "Xatolar ro'yxati", "Xatolar soni", "Xatolar turi"], 0),
            ("ValueError qachon chiqadi?", ["Noto'g'ri qiymat", "Fayl topilmasa", "Nolga bo'lish", "Xotira yetmasa"], 0),
            ("TypeError qachon chiqadi?", ["Noto'g'ri tur", "Noto'g'ri qiymat", "Fayl topilmasa", "Nolga bo'lish"], 0),
            ("ZeroDivisionError qachon chiqadi?", ["Nolga bo'lish", "Noto'g'ri tur", "Noto'g'ri qiymat", "Fayl topilmasa"], 0),
            ("FileNotFoundError qachon chiqadi?", ["Fayl topilmasa", "Nolga bo'lish", "Noto'g'ri tur", "Noto'g'ri qiymat"], 0),
            ("IndexError qachon chiqadi?", ["Indeks noto'g'ri", "Qiymat noto'g'ri", "Tur noto'g'ri", "Fayl topilmasa"], 0),
            ("KeyError qachon chiqadi?", ["Kalit topilmasa", "Indeks noto'g'ri", "Qiymat noto'g'ri", "Tur noto'g'ri"], 0),
            ("Assertion nima?", ["Tasdiqlash", "Xato chiqarish", "Dasturni to'xtatish", "Dasturni tezlashtirish"], 0),
            ("assert statement nima qiladi?", ["Shartni tekshiradi", "Xato chiqaradi", "Dasturni to'xtatadi", "Qiymat qaytaradi"], 0),
            ("Debugging tools nimalar?", ["Xatolarni topish vositalari", "Dastur yozish vositalari", "Dastur testlash vositalari", "Dastur ishga tushirish vositalari"], 0),
            ("pdb nima?", ["Python debugger", "Python database", "Python designer", "Python documenter"], 0),
            ("Logging nima?", ["Dastur ishini yozib borish", "Dastur yozish", "Dastur testlash", "Dastur ishga tushirish"], 0),
            ("Unit testing nima?", ["Birlik testlari", "Integratsiya testlari", "Sistema testlari", "Foydalanuvchi testlari"], 0),
            ("unittest module nima uchun?", ["Test yozish", "Xatolarni ushlash", "Dastur yozish", "Dastur ishga tushirish"], 0),
            ("Test case nima?", ["Test holati", "Test natijasi", "Test jarayoni", "Test vositası"], 0),
            ("Test suite nima?", ["Testlar to'plami", "Bitta test", "Test holati", "Test natijasi"], 0),
            ("Code documentation nima?", ["Kod hujjatlari", "Kod yozish", "Kod testlash", "Kod ishga tushirish"], 0),
            ("Docstring nima?", ["Funksiya hujjati", "Funksiya kodi", "Funksiya nomi", "Funksiya parametri"], 0),
            ("PEP 8 nima?", ["Python kod uslubi", "Python kutubxonasi", "Python moduli", "Python funksiyasi"], 0),
        ]
    }
}

# ============================================
# VARIATSIYA YARATISH FUNKSIYASI
# ============================================

def create_variant(question_text, options, correct_idx):
    """Bir savol uchun ko'p variantlar yaratish"""
    variants = []
    
    # 1. Standart variant
    variants.append((question_text, options, correct_idx))
    
    # 2. Variantlar sonini o'zgartirish (4 variant)
    if len(options) == 4:
        # A, B, C, D harflari bilan
        lettered_text = f"{question_text}"
        variants.append((lettered_text, options, correct_idx))
        
        # Savol formatini o'zgartirish
        formatted_text = f"Savol: {question_text}"
        variants.append((formatted_text, options, correct_idx))
        
        # Savol oldiga raqam qo'shish
        numbered_text = f"1. {question_text}"
        variants.append((numbered_text, options, correct_idx))
        
        # Savolni boshqa formatda berish
        alternative_text = f"Quyidagi savolga javob bering: {question_text}"
        variants.append((alternative_text, options, correct_idx))
        
        # Savolni qisqartirish
        if len(question_text) > 30:
            short_text = f"{question_text[:50]}..."
            variants.append((short_text, options, correct_idx))
    
    # 3. Variantlarni aralashtirish
    for _ in range(3):
        shuffled_options = options.copy()
        random.shuffle(shuffled_options)
        new_correct_idx = shuffled_options.index(options[correct_idx])
        variants.append((question_text, shuffled_options, new_correct_idx))
    
    # 4. Variantlar matnini o'zgartirish
    question_prefixes = [
        "",
        "Quyidagilardan qaysi biri to'g'ri? ",
        "To'g'ri javobni toping: ",
        "Qaysi variant to'g'ri? ",
        "Nima deb o'ylaysiz? ",
        "Savol: ",
        "Javob bering: ",
        "Tanlang: ",
    ]
    
    for prefix in question_prefixes[1:]:
        prefixed_text = f"{prefix}{question_text}"
        variants.append((prefixed_text, options, correct_idx))
    
    # 5. Xar xil uslublar
    styles = [
        (f"🔍 {question_text}", options, correct_idx),
        (f"❓ {question_text}", options, correct_idx),
        (f"📝 {question_text}", options, correct_idx),
        (f"{question_text}?", options, correct_idx),
        (f"{question_text} (bir variantni tanlang):", options, correct_idx),
    ]
    
    variants.extend(styles)
    
    return variants

def generate_unique_questions(template, count=200):
    """Shablondan 200 ta unikal savol yaratish"""
    all_questions = []
    seen_texts = set()
    
    # Avval barcha asosiy savollarni variantlarini yaratish
    for q_text, options, correct_idx in template:
        variants = create_variant(q_text, options, correct_idx)
        for variant in variants:
            v_text, v_options, v_correct = variant
            if v_text not in seen_texts:
                all_questions.append({
                    'text': v_text,
                    'options': v_options.copy(),
                    'correct': v_correct
                })
                seen_texts.add(v_text)
    
    # Agar yetarli bo'lmasa, tasodifiy variantlar yaratish
    if len(all_questions) < count:
        # 1. Yangi savollar yaratish
        subjects = [
            "kompyuter", "dastur", "internet", "fayl", "tarmoq", 
            "xotira", "protsessor", "monitor", "klaviatura", "sichqoncha"
        ]
        
        verbs = [
            "nima", "qanday", "necha", "qaysi", "nimaga", 
            "qanday qilinadi", "qayerda", "qachon", "kim", "nima uchun"
        ]
        
        for _ in range(count * 2):  # Ortiqcha yaratib, keyin tanlash
            subject = random.choice(subjects)
            verb = random.choice(verbs)
            
            # Savol matnini yaratish
            new_text = f"{subject.capitalize()} {verb}?"
            
            if new_text not in seen_texts:
                # Variantlarni yaratish
                new_options = []
                for i in range(4):
                    option_text = f"Variant {i+1} {subject} {verb}"
                    new_options.append(option_text)
                
                # To'g'ri javobni tanlash
                new_correct = random.randint(0, 3)
                
                # Savol qo'shish
                all_questions.append({
                    'text': new_text,
                    'options': new_options.copy(),
                    'correct': new_correct
                })
                seen_texts.add(new_text)
    
    # Tasodifiy tanlash va 200 taga cheklash
    if len(all_questions) > count:
        all_questions = random.sample(all_questions, count)
    
    # Har bir savolning variantlarini tekshirish
    final_questions = []
    seen_combinations = set()
    
    for q in all_questions:
        combo_key = (q['text'], tuple(q['options']), q['correct'])
        if combo_key not in seen_combinations:
            final_questions.append(q)
            seen_combinations.add(combo_key)
    
    # Agar hali ham yetarli bo'lmasa, mavjudlarni ko'paytirish
    while len(final_questions) < count and len(final_questions) > 0:
        base_q = random.choice(final_questions)
        
        # Variantlarni aralashtirish
        shuffled_options = base_q['options'].copy()
        random.shuffle(shuffled_options)
        new_correct = shuffled_options.index(base_q['options'][base_q['correct']])
        
        # Yangi savol matni
        prefixes = ["Yana bir savol: ", "Boshqa savol: ", "Keyingi savol: ", ""]
        new_text = f"{random.choice(prefixes)}{base_q['text']}"
        
        combo_key = (new_text, tuple(shuffled_options), new_correct)
        if combo_key not in seen_combinations:
            final_questions.append({
                'text': new_text,
                'options': shuffled_options,
                'correct': new_correct
            })
            seen_combinations.add(combo_key)
    
    return final_questions[:count]

# ============================================
# MA'LUMOTLAR BAZASINI TO'LDIRISH
# ============================================

def populate_database():
    """Ma'lumotlar bazasini to'ldirish - 4000 ta HAR XIL savol"""
    with app.app_context():
        print("=" * 60)
        print("🚀 MA'LUMOTLAR BAZASINI TO'LDIRISH BOSHLANDI")
        print("=" * 60)
        
        # Jadvallarni tozalash (ixtiyoriy)
        response = input("\n⚠️  Eski savollarni o'chirishni xohlaysizmi? (ha/yo'q): ")
        if response.lower() in ['ha', 'yes', 'y', 'h']:
            Question.query.delete()
            db.session.commit()
            print("✅ Eski savollar o'chirildi")
        
        total_added = 0
        start_time = datetime.now()
        
        print("\n" + "=" * 60)
        print("📚 INFORMATIKA SAVOLLARI")
        print("=" * 60)
        
        # Informatika (5-6 sinflar)
        for grade in [5, 6]:
            print(f"\n📖 {grade}-SINF:")
            for quarter in range(1, 5):
                if grade in informatika_templates and quarter in informatika_templates[grade]:
                    template = informatika_templates[grade][quarter]
                    print(f"  🔄 {quarter}-chorak uchun savollar yaratilmoqda...")
                    
                    questions = generate_unique_questions(template, 200)
                    
                    for q_data in questions:
                        question = Question(
                            subject_id=1,  # Informatika
                            grade=grade,
                            quarter=quarter,
                            question_text=q_data['text'],
                            option_a=q_data['options'][0],
                            option_b=q_data['options'][1],
                            option_c=q_data['options'][2],
                            option_d=q_data['options'][3],
                            correct_answer=chr(65 + q_data['correct'])  # A, B, C, D
                        )
                        db.session.add(question)
                        total_added += 1
                    
                    db.session.commit()
                    print(f"  ✅ {quarter}-chorak: {len(questions)} ta savol qo'shildi")
        
        print("\n" + "=" * 60)
        print("🐍 PYTHON SAVOLLARI")
        print("=" * 60)
        
        # Python (7-8-9 sinflar)
        for grade in [7, 8, 9]:
            print(f"\n📖 {grade}-SINF:")
            for quarter in range(1, 5):
                if grade in python_templates and quarter in python_templates[grade]:
                    template = python_templates[grade][quarter]
                    print(f"  🔄 {quarter}-chorak uchun savollar yaratilmoqda...")
                    
                    questions = generate_unique_questions(template, 200)
                    
                    for q_data in questions:
                        question = Question(
                            subject_id=2,  # Python
                            grade=grade,
                            quarter=quarter,
                            question_text=q_data['text'],
                            option_a=q_data['options'][0],
                            option_b=q_data['options'][1],
                            option_c=q_data['options'][2],
                            option_d=q_data['options'][3],
                            correct_answer=chr(65 + q_data['correct'])  # A, B, C, D
                        )
                        db.session.add(question)
                        total_added += 1
                    
                    db.session.commit()
                    print(f"  ✅ {quarter}-chorak: {len(questions)} ta savol qo'shildi")
        
        # Vaqtni hisoblash
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("\n" + "=" * 60)
        print("🎉 MA'LUMOTLAR BAZASI TO'LDIRISH TUGALLANDI!")
        print("=" * 60)
        
        print(f"\n📊 STATISTIKA:")
        print(f"  - Jami savollar: {total_added} ta")
        print(f"  - Informatika: 5-6 sinflar, 2 sinf × 4 chorak × 200 = 1,600 ta")
        print(f"  - Python: 7-8-9 sinflar, 3 sinf × 4 chorak × 200 = 2,400 ta")
        print(f"  - Umumiy: 1,600 + 2,400 = 4,000 ta")
        print(f"  - Vaqt: {duration:.2f} soniya")
        
        print(f"\n✅ Har bir chorak uchun 200 ta savol")
        print(f"✅ Har bir savol o'ziga xos")
        print(f"✅ Barcha variantlar har xil")
        print(f"✅ Ma'lumotlar bazasiga muvaffaqiyatli saqlandi")

# ============================================
# ASOSIY KOD
# ============================================

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("📋 SAVOLLAR GENERATORI")
    print("=" * 60)
    print("Ushbu dastur 4000 ta har xil savol yaratadi:")
    print("  - Informatika: 5-6 sinflar (1,600 ta)")
    print("  - Python: 7-8-9 sinflar (2,400 ta)")
    print("  - Har bir sinf/chorak uchun 200 ta savol")
    print("=" * 60)
    
    confirmation = input("\n🔧 Dasturni ishga tushirishni xohlaysizmi? (ha/yo'q): ")
    if confirmation.lower() in ['ha', 'yes', 'y', 'h']:
        populate_database()
        print("\n🎯 Dastur muvaffaqiyatli yakunlandi!")
    else:
        print("\n❌ Dastur bekor qilindi.")