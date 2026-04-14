# Flask Quiz Platform

Maktab o'quvchilari uchun ishlab chiqilgan zamonaviy test va baholash platformasi.
O'zbek, Rus va Ingliz tillarini qo'llab-quvvatlaydi. PWA sifatida o'rnatilishi mumkin.

**Live demo:** https://jahonschool.pythonanywhere.com

---

## Mundarija

- [Loyiha haqida](#loyiha-haqida)
- [Texnologiyalar](#texnologiyalar)
- [Loyiha strukturasi](#loyiha-strukturasi)
- [Ma'lumotlar bazasi](#malumotlar-bazasi)
- [Sahifalar va marshrutlar](#sahifalar-va-marshrutlar)
- [Funksiyalar](#funksiyalar)
- [Ishga tushirish](#ishga-tushirish)
- [Admin panel](#admin-panel)
- [Statistika](#statistika)
- [Deployment](#deployment)

---

## Loyiha haqida

Flask asosida qurilgan to'liq xususiyatli test platformasi. Asosan **Jahon maktabi** uchun yaratilgan:

| Fan | Sinflar | Choraklar | Savollar |
|-----|---------|-----------|----------|
| Informatika | 5, 6 | 1–4 | 1 600 ta |
| Python | 7, 8, 9 | 1–4 | 2 400 ta |
| **Jami** | | | **4 000 ta** |

Har bir fan/sinf/chorak uchun **200 ta** savol mavjud.

---

## Texnologiyalar

### Backend
| Kutubxona | Versiya | Maqsad |
|-----------|---------|--------|
| Flask | 3.0.0 | Web framework |
| Flask-SQLAlchemy | 3.1.1 | ORM / database |
| Flask-Babel | 4.0.0 | Ko'p tillilik (i18n) |
| Werkzeug | 3.0.1 | Xavfsizlik, WSGI |
| gspread + google-auth | 6.0.0 | Google Sheets integratsiyasi |
| deep-translator | latest | Savollarni avtomatik tarjima qilish |
| pandas + openpyxl | latest | Excel import/export |
| markdown | latest | Savol matnlarida markdown render |
| gunicorn | latest | Ishlab chiqarish (production) serveri |

### Frontend
- **Bootstrap 5.3.0** — UI framework
- **Font Awesome 6.4.0** — Ikonkalar
- **Chart.js** — Admin dashboard grafiklari
- **Vanilla JS** — Test logikasi, taymer, navigatsiya
- **PWA** — O'rnatiluvchi, oflayn ishlay oladigan ilova

### Ma'lumotlar bazasi
- **SQLite 3** — Lokal fayl bazasi (`instance/test_platform.db`)
- Ishga tushganda avtomatik migratsiya bajariladi (yangi ustunlar qo'shiladi)

---

## Loyiha strukturasi

```
quiz-js/
├── app.py                        # Asosiy Flask ilovasi (factory pattern)
├── models.py                     # SQLAlchemy modellari
├── extensions.py                 # Flask kengaytmalari (SQLAlchemy, Babel)
├── feature_store.py              # Rasm va baholash sozlamalari (JSON-based)
├── requirements.txt              # Python bog'liqliklari
├── babel.cfg                     # i18n konfiguratsiyasi
│
├── routes/
│   ├── main.py                   # Umumiy sahifalar (bosh sahifa, til almashtirish)
│   ├── admin.py                  # O'qituvchi/admin boshqaruvi (~1 332 qator)
│   └── student.py                # O'quvchi test oqimi (~675 qator)
│
├── templates/                    # Jinja2 HTML shablonlar (23 ta fayl)
│   ├── base.html                 # Asosiy shablon (navbar, footer, PWA)
│   ├── index.html                # Bosh sahifa (rol tanlash)
│   ├── page.html                 # Statik sahifalar (about, contact, ...)
│   ├── error.html                # Xato sahifasi
│   ├── admin_login.html          # Admin kirish
│   ├── admin_dashboard.html      # Boshqaruv paneli + grafiklar
│   ├── admin_questions.html      # Savollar ro'yxati
│   ├── admin_question_form.html  # Savol qo'shish/tahrirlash
│   ├── admin_subjects.html       # Fanlar ro'yxati
│   ├── admin_subject_form.html   # Fan sozlamalari
│   ├── admin_control_works.html  # Nazorat ishlari
│   ├── admin_control_work_form.html
│   ├── admin_results.html        # Natijalar ko'rish va export
│   ├── admin_feedbacks.html      # Fikr-mulohaza (chat)
│   ├── admin_profile.html        # Admin profil
│   ├── admin_teachers.html       # O'qituvchilar
│   ├── admin_teacher_add.html
│   ├── student_start.html        # Fan/sinf/chorak tanlash
│   ├── student_control_start.html
│   ├── student_test.html         # Test interfeysi
│   └── student_result.html       # Natija sahifasi
│
├── static/
│   ├── manifest.json             # PWA manifest
│   ├── sw.js                     # Service Worker (kesh, oflayn)
│   ├── img/                      # Logo va rasmlar
│   ├── icons/                    # Favicon, app ikonkalari
│   └── uploads/questions/        # Savollar uchun yuklangan rasmlar
│
├── scripts/
│   └── rebuild_question_bank.py  # 4 000 ta savol generatsiya skripti
│
├── translations/                 # i18n tarjima fayllari (uz, ru, en)
│
└── instance/
    ├── test_platform.db          # SQLite bazasi (~2.7 MB)
    └── feature_settings.json     # Rasm va baholash sozlamalari
```

---

## Ma'lumotlar bazasi

### Admin (O'qituvchi/admin akkauntlar)
| Ustun | Tur | Tavsif |
|-------|-----|--------|
| id | Integer | Asosiy kalit |
| username | String | Login nomi |
| password_hash | String | Shifrlangan parol |
| full_name | String | To'liq ism |
| role | String | `admin` yoki `teacher` |
| phone_number | String | Telefon raqami |
| email | String | Elektron pochta |

### Subject (Fanlar)
| Ustun | Tur | Tavsif |
|-------|-----|--------|
| id | Integer | Asosiy kalit |
| name / name_ru / name_en | String | Ko'p tilli nom |
| grades | String | Sinflar (masalan: `"5,6"`) |
| question_count | Integer | Testdagi savollar soni (standart: 20) |
| time_limit | Integer | Vaqt chegarasi (daqiqada, standart: 30) |
| is_protected | Boolean | Anti-aldash himoyasi |
| show_results | Boolean | Natijalarni ko'rsatish |
| is_visible | Boolean | O'quvchilarga ko'rinadimi |

### Question (Savollar)
| Ustun | Tur | Tavsif |
|-------|-----|--------|
| id | Integer | Asosiy kalit |
| subject_id | FK | Fan |
| grade | Integer | Sinf (5–9) |
| quarter | Integer | Chorak (1–4) |
| difficulty | Integer | Qiyinlik: 1=oson, 2=o'rta, 3=qiyin |
| lesson | Integer | Dars raqami (ixtiyoriy) |
| question_text | Text | Savol matni (o'zbekcha) |
| question_text_ru/en | Text | Tarjimalar |
| option_a/b/c/d | String | 4 ta variant |
| correct_answer | String | To'g'ri javob (A/B/C/D) |

### TestResult (Test natijalari)
| Ustun | Tur | Tavsif |
|-------|-----|--------|
| id | Integer | Asosiy kalit |
| full_name | String | O'quvchi ismi |
| grade | Integer | Sinf |
| class_number | String | Sinf harfi (A, B, ...) |
| quarter | Integer | Chorak |
| subject_id | FK | Fan |
| score | Integer | To'g'ri javoblar soni |
| total_questions | Integer | Jami savollar |
| percentage | Float | Foiz |
| grade_text | String | Baho (A'lo/Yaxshi/Qoniqarli/Qoniqarsiz) |
| test_date | DateTime | Vaqt (Toshkent UTC+5) |
| answers_json | JSON | Har bir savol uchun javob |
| control_work_id | FK | Nazorat ishi (ixtiyoriy) |

### ControlWork (Nazorat ishlari)
- Vaqt chegarali (40+ daqiqa) rasmiy baholash
- Ko'p-ko'p munosabat orqali savollar bilan bog'langan
- `is_active` — faqat faol nazorat ishlarini o'quvchilarga ko'rsatadi

### Feedback (Fikr-mulohaza chati)
- O'quvchi va admin o'rtasidagi chat tizimi
- `user_uuid` — anonim o'quvchi identifikatori
- `sender` — `student` yoki `admin`
- Yangi xabar tushganda o'qilmagan holat ko'rsatiladi

---

## Sahifalar va marshrutlar

### Umumiy sahifalar (`routes/main.py`)
| URL | Metod | Tavsif |
|-----|-------|--------|
| `/` | GET, POST | Bosh sahifa — o'quvchi/o'qituvchi tanlash |
| `/about` | GET | Loyiha haqida |
| `/contact` | GET | Aloqa |
| `/services` | GET | Xizmatlar |
| `/set_language/<lang>` | GET | Tilni o'zgartirish (uz/ru/en) |
| `/manifest.json` | GET | PWA manifest |
| `/sw.js` | GET | Service Worker |
| `/robots.txt` | GET | SEO robots fayli |
| `/sitemap.xml` | GET | Dinamik sitemap |

### O'quvchi marshrutlari (`routes/student.py`)
| URL | Metod | Tavsif |
|-----|-------|--------|
| `/student/start` | GET, POST | Fan, sinf, chorak tanlash + test boshlash |
| `/student/control_start` | GET, POST | Nazorat ishi tanlash |
| `/student/test` | GET | Joriy savolni ko'rsatish |
| `/student/answer` | POST | Javobni saqlash |
| `/student/navigate/<direction>` | GET | Oldingi/keyingi savol |
| `/student/jump/<index>` | GET | Istalgan savolga o'tish |
| `/student/mark_question` | POST | Savolni belgilash/bekor qilish |
| `/student/result` | GET | Natija sahifasi |
| `/student/report_violation` | POST | Anti-aldash: buzilishni qayd etish |
| `/student/verify_unlock` | POST | Blokdan chiqarish so'rovi |
| `/student/feedback` | POST | Fikr yuborish |
| `/student/my_feedbacks/<uuid>` | GET | Chat tarixi (JSON) |

### Admin marshrutlari (`routes/admin.py`)
| URL | Tavsif |
|-----|--------|
| `/admin/login` | Kirish |
| `/admin/dashboard` | Boshqaruv paneli |
| `/admin/questions` | Savollar (filter, qidiruv, sahifalash) |
| `/admin/question/add` | Savol qo'shish + avtomatik tarjima |
| `/admin/question/edit/<id>` | Savolni tahrirlash |
| `/admin/question/delete/<id>` | Savolni o'chirish |
| `/admin/questions/translate_missing` | Tarjima bo'lmagan savollarni toplu tarjima |
| `/admin/import/questions` | Excel/CSV dan import |
| `/admin/download/template` | Excel shablon yuklab olish |
| `/admin/subjects` | Fanlar |
| `/admin/subject/add` | Fan qo'shish + baholash chegaralari |
| `/admin/subject/edit/<id>` | Fan sozlamalarini tahrirlash |
| `/admin/control_works` | Nazorat ishlari |
| `/admin/control_work/add` | Nazorat ishi yaratish |
| `/admin/results` | Natijalar + filter + sortlash |
| `/admin/export/results` | Natijalarni Excel sifatida yuklab olish |
| `/admin/results/delete-by-date` | Sana bo'yicha toplu o'chirish |
| `/admin/feedbacks` | Barcha chat suhbatlari |
| `/admin/feedbacks/<uuid>` | Alohida suhbat |
| `/admin/feedback/respond/<uuid>` | Javob yuborish |
| `/admin/teachers` | O'qituvchilar ro'yxati |
| `/admin/teachers/add` | O'qituvchi akkaunt yaratish |
| `/admin/profile` | O'z profilini tahrirlash |

---

## Funksiyalar

### O'quvchilar uchun
- **Login/parolsiz kirish** — faqat ism va sinf talab etiladi
- **Muvozanatli savol tanlash** — har bir test uchun algoritmik tanlash:
  - 5 ta oldingi chorakdan takrorlash savollari
  - 10 ta o'rta darajali savollar
  - 5 ta qiyin darajali savollar
- **Tasodifiy variant tartibi** — har safar variantlar aralashib chiqadi
- **Test suhbatini davom ettirish** — brauzer yopilsa ham test saqlanadi
- **Taymer** — vaqt tugaganda avtomatik topshiriladi (30 yoki 40+ daqiqa)
- **Ko'rish uchun belgilash** — istalgan savolni "Review" sifatida belgilash
- **Savol navigatsiyasi** — chap panelda barcha savollar ko'rsatiladi (desktop)
- **Progress bar** — bosib o'tilgan savollar foizi
- **Natija va tahlil** — har bir savolga to'g'ri/noto'g'ri javob ko'rsatiladi
- **Anti-aldash tizimi** — tab almashtirish, fullscreendan chiqish qayd etiladi
- **Rasmli savollar** — diagramma va tasvirlarga ega savollar
- **Ko'p tillilik** — O'zbek, Rus, Ingliz
- **PWA** — mobil qurilmaga o'rnatilishi mumkin, oflayn ishlaydi
- **Fikr-mulohaza** — admin bilan to'g'ridan-to'g'ri chat

### Admin/O'qituvchilar uchun
- **Rol tizimi** — `admin` (to'liq huquq) va `teacher` (cheklangan)
- **Savollar CRUD** — qo'shish, ko'rish, tahrirlash, o'chirish
- **Avtomatik tarjima** — savollar O'zbekchadan Ruscha va Inglizchaga tarjima qilinadi
- **Toplu tarjima** — tarjima qilinmagan savollarni bir bosish bilan tarjima qilish
- **Excel/CSV import** — savollarni jadvaldan yuklash
- **Excel eksport** — natijalarni jadvalga yuklab olish
- **Fan sozlamalari** — har bir fan uchun alohida baholash chegaralari
- **Nazorat ishlari** — maxsus tanlangan savollar bilan vaqtli imtihonlar
- **Dashboard grafiklar** — fan bo'yicha statistika (Chart.js)
- **Qiyin savollar tahlili** — oxirgi 500 ta natijadan eng ko'p xato qilingan savollar
- **Sana bo'yicha toplu o'chirish** — eski natijalarni tozalash
- **Rasm yuklash** — har bir savolga rasm biriktirish
- **Savol qidirish va filtrlash** — fan, sinf, chorak, matn bo'yicha
- **O'qituvchi boshqaruvi** — akkaunt qo'shish, parol tiklash
- **Profil tahrirlash** — ism, email, telefon, parol

### Tizim imkoniyatlari
- **Avtomatik migratsiya** — bazaga yangi ustunlar qo'shilganda avtomatik o'zgaradi
- **Toshkent vaqt zonasi** — barcha vaqtlar UTC+5 da saqlanadi
- **Markdown render** — savol matni va variantlarda `kod`, `qalin`, ro'yxat va boshqalar
- **SEO** — `robots.txt`, dinamik `sitemap.xml`, Open Graph meta teglari
- **Xavfsiz fayl yuklash** — path traversal himoyasi bilan

---

## Baholash tizimi

Standart chegaralar (har bir fan uchun alohida sozlanishi mumkin):

| Baho | Belgi | Foiz |
|------|-------|------|
| A'lo | 5 | 85% va yuqori |
| Yaxshi | 4 | 70–84% |
| Qoniqarli | 3 | 65–69% |
| Qoniqarsiz | 2 | 65% dan past |

---

## Ishga tushirish

### 1. Repozitoriyani klonlash
```bash
git clone <repo-url>
cd quiz-js
```

### 2. Virtual muhit yaratish
```bash
python3 -m venv venv
source venv/bin/activate       # Linux/Mac
# venv\Scripts\activate        # Windows
```

### 3. Bog'liqliklarni o'rnatish
```bash
pip install -r requirements.txt
```

### 4. Dasturni ishga tushirish
```bash
python3 app.py
```

### 5. Brauzerda ochish
```
http://localhost:5050
```

Ilova birinchi ishga tushganda avtomatik ravishda:
- Barcha jadvallar yaratiladi
- Mavjud jadvallar migratsiya qilinadi (yangi ustunlar qo'shiladi)
- Standart admin akkaunt yaratiladi
- Standart fanlar (Informatika, Python) qo'shiladi

---

## Admin panel

### Kirish
```
URL:      /admin/login
Login:    asilbek
Parol:    jahonschool
```

> **Muhim:** Ishlab chiqarish (production) muhitida parolni albatta o'zgartiring.

### Admin panel bo'limlari
| Bo'lim | Tavsif |
|--------|--------|
| Dashboard | Umumiy statistika, grafik, so'nggi natijalar |
| Savollar | 4 000 ta savolni boshqarish, qidirish, tahrirlash |
| Fanlar | Fan sozlamalari va baholash chegaralari |
| Nazorat ishlari | Timed imtihonlarni boshqarish |
| Natijalar | O'quvchi natijalarini ko'rish va eksport qilish |
| Fikr-mulohazalar | O'quvchilar bilan chat |
| O'qituvchilar | Akkauntlarni boshqarish |
| Profil | O'z akkaunt sozlamalari |

---

## Statistika

| Ko'rsatkich | Qiymat |
|-------------|--------|
| Jami savollar | 4 000 ta |
| Informatika (5–6 sinf, 4 chorak) | 1 600 ta |
| Python (7–8–9 sinf, 4 chorak) | 2 400 ta |
| Har bir fan/sinf/chorak uchun | 200 ta |
| Standart test uzunligi | 20 savol |
| Standart vaqt | 30 daqiqa |
| Nazorat ishi vaqti | 40+ daqiqa |

---

## Deployment

### PythonAnywhere
Loyiha **https://jahonschool.pythonanywhere.com** da joylashtirilgan.

Sozlashlar:
- WSGI fayl: `app.py` dagi `create_app()` ni ko'rsating
- Media fayl yo'li: `static/uploads/questions/`
- `SECRET_KEY` ni muhit o'zgaruvchisi orqali o'zgartiring

### Muhit o'zgaruvchilari (ixtiyoriy)
```
SECRET_KEY=<xavfsiz-kalit>
```

---

## Loyiha yozuvlari

- Barcha fayllar va shablonlar Python/Flask standartlariga mos
- `feature_store.py` JSON-based konfiguratsiya (SQLite siz)
- `rebuild_question_bank.py` skripti barcha 4 000 ta savolni qayta yaratishi mumkin
- Barcha rasm yo'llari xavfsiz (path traversal himoyalangan)
- Test sessiyasi brauzer yopilganda saqlanadi va davom ettirilishi mumkin
