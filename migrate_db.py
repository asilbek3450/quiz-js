
import sqlite3
from deep_translator import GoogleTranslator
import time

DB_PATH = 'instance/test_platform.db'

def translate_text(text, target_lang):
    if not text:
        return ""
    try:
        # Retry logic
        for _ in range(3):
            try:
                translated = GoogleTranslator(source='auto', target=target_lang).translate(text)
                return translated
            except Exception as e:
                time.sleep(1)
        return text # Fallback to original
    except Exception as e:
        print(f"Translation failed for '{text}': {e}")
        return text

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Add columns to Subject table
    print("Migrating Subject table...")
    try:
        cursor.execute("ALTER TABLE subject ADD COLUMN name_ru TEXT")
        cursor.execute("ALTER TABLE subject ADD COLUMN name_en TEXT")
    except sqlite3.OperationalError:
        print("Subject columns already exist.")

    # 2. Add columns to Question table
    print("Migrating Question table...")
    columns_to_add = [
        'question_text_ru', 'question_text_en',
        'option_a_ru', 'option_a_en',
        'option_b_ru', 'option_b_en',
        'option_c_ru', 'option_c_en',
        'option_d_ru', 'option_d_en'
    ]
    
    for col in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE question ADD COLUMN {col} TEXT")
        except sqlite3.OperationalError:
            print(f"Column {col} already exists.")

    conn.commit()

    # 3. Backfill translations
    print("Backfilling Subject translations...")
    cursor.execute("SELECT id, name FROM subject")
    subjects = cursor.fetchall()
    
    for subject_id, name in subjects:
        name_ru = translate_text(name, 'ru')
        name_en = translate_text(name, 'en')
        cursor.execute("UPDATE subject SET name_ru = ?, name_en = ? WHERE id = ?", (name_ru, name_en, subject_id))
        print(f"Updated Subject {subject_id}: {name} -> RU: {name_ru}, EN: {name_en}")
    
    conn.commit()

    print("Backfilling Question translations (this may take a while)...")
    cursor.execute("SELECT id, question_text, option_a, option_b, option_c, option_d FROM question")
    questions = cursor.fetchall()

    for q in questions:
        q_id, text, a, b, c, d = q
        
        # RU
        text_ru = translate_text(text, 'ru')
        a_ru = translate_text(a, 'ru')
        b_ru = translate_text(b, 'ru')
        c_ru = translate_text(c, 'ru')
        d_ru = translate_text(d, 'ru')

        # EN
        text_en = translate_text(text, 'en')
        a_en = translate_text(a, 'en')
        b_en = translate_text(b, 'en')
        c_en = translate_text(c, 'en')
        d_en = translate_text(d, 'en')

        cursor.execute("""
            UPDATE question 
            SET question_text_ru = ?, question_text_en = ?,
                option_a_ru = ?, option_a_en = ?,
                option_b_ru = ?, option_b_en = ?,
                option_c_ru = ?, option_c_en = ?,
                option_d_ru = ?, option_d_en = ?
            WHERE id = ?
        """, (text_ru, text_en, a_ru, a_en, b_ru, b_en, c_ru, c_en, d_ru, d_en, q_id))
        print(f"Updated Question {q_id}")

    conn.commit()
    conn.close()
    print("Migration completed successfully!")

if __name__ == '__main__':
    migrate()
