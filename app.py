from flask import Flask, Response, session
from flask import send_from_directory
from datetime import date, timedelta
from extensions import db, babel
from routes.main import main_bp
from routes.admin import admin_bp
from routes.student import student_bp
import markdown
from models import Admin, Subject, Question, TestResult, ControlWork, Feedback

def create_app():
    app = Flask(__name__, template_folder="templates")
    app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_platform.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)
    # Public base URL for sitemap/OG tags (PythonAnywhere domain)
    app.config.setdefault("PUBLIC_BASE_URL", "https://jahonschool.pythonanywhere.com")

    db.init_app(app)
    
    def get_locale():
        if 'lang' in session:
            return session['lang']
        return 'uz'

    babel.init_app(app, locale_selector=get_locale)

    @app.context_processor
    def inject_conf_var():
        return dict(get_locale=get_locale)

    @app.template_filter('markdown')
    def markdown_filter(text):
        if not text:
            return ""
        return markdown.markdown(text, extensions=['fenced_code'])

    # Register Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(student_bp)
    
    
    @app.route('/google123456789.html')
    def google_verification():
        return send_from_directory('.', 'google123456789.html')

    @app.get("/robots.txt")
    def robots_txt():
        base = app.config.get("PUBLIC_BASE_URL", "").rstrip("/")
        body = "\n".join([
            "User-agent: *",
            "Allow: /",
            f"Sitemap: {base}/sitemap.xml",
            "",
        ])
        return Response(body, content_type="text/plain; charset=utf-8")

    @app.get("/sitemap.xml")
    def sitemap_xml():
        base = app.config.get("PUBLIC_BASE_URL", "").rstrip("/")

        today = date.today().isoformat()
        urls = [
            {"path": "/", "changefreq": "daily", "priority": "1.0"},
            {"path": "/about", "changefreq": "monthly", "priority": "0.7"},
            {"path": "/contact", "changefreq": "yearly", "priority": "0.5"},
            {"path": "/services", "changefreq": "monthly", "priority": "0.7"},
            {"path": "/blog", "changefreq": "weekly", "priority": "0.8"},
        ]

        urls_xml = "\n".join([
            "\n".join([
                "  <url>",
                f"    <loc>{base}{u['path']}</loc>",
                f"    <lastmod>{today}</lastmod>",
                f"    <changefreq>{u['changefreq']}</changefreq>",
                f"    <priority>{u['priority']}</priority>",
                "  </url>",
            ])
            for u in urls
        ])
        xml = "\n".join([
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
            urls_xml,
            "</urlset>",
            "",
        ])
        return Response(xml, content_type="application/xml; charset=utf-8")

    with app.app_context():
        # Create tables if not exist (includes new column for Subject)
        # Note: SQLAlchemy bind does not auto-migrate existing tables usually unless drop_all is called or using migration tool.
        # SQLite adds column automatically? No.
        # We might need to manually add column or handle migration.
        # For simplicity in this environment:
        # Check if Subject table has is_protected column. If not, add it via raw SQL.
        
        db.create_all()
        
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        
        # Check and migrate Admin table
        admin_columns = [c['name'] for c in inspector.get_columns('admin')]
        if 'role' not in admin_columns:
            print("Migrating database: Adding role to Admin table...")
            with db.engine.connect() as conn:
                conn.execute(db.text("ALTER TABLE admin ADD COLUMN role VARCHAR(20) DEFAULT 'admin'"))
                conn.commit()
        if 'phone_number' not in admin_columns:
            print("Migrating database: Adding phone_number to Admin table...")
            with db.engine.connect() as conn:
                conn.execute(db.text("ALTER TABLE admin ADD COLUMN phone_number VARCHAR(20)"))
                conn.commit()
        if 'email' not in admin_columns:
            print("Migrating database: Adding email to Admin table...")
            with db.engine.connect() as conn:
                conn.execute(db.text("ALTER TABLE admin ADD COLUMN email VARCHAR(100)"))
                conn.commit()

        # Check and migrate Subject table
        columns = [c['name'] for c in inspector.get_columns('subject')]
        if 'is_protected' not in columns:
            print("Migrating database: Adding is_protected to Subject table...")
            with db.engine.connect() as conn:
                conn.execute(db.text("ALTER TABLE subject ADD COLUMN is_protected BOOLEAN DEFAULT 0"))
                conn.commit()
        if 'question_count' not in columns:
            print("Migrating database: Adding question_count to Subject table...")
            with db.engine.connect() as conn:
                conn.execute(db.text("ALTER TABLE subject ADD COLUMN question_count INTEGER DEFAULT 20"))
                conn.commit()
        if 'time_limit' not in columns:
            print("Migrating database: Adding time_limit to Subject table...")
            with db.engine.connect() as conn:
                conn.execute(db.text("ALTER TABLE subject ADD COLUMN time_limit INTEGER DEFAULT 30"))
                conn.commit()
        if 'show_results' not in columns:
            print("Migrating database: Adding show_results to Subject table...")
            with db.engine.connect() as conn:
                conn.execute(db.text("ALTER TABLE subject ADD COLUMN show_results BOOLEAN DEFAULT 1"))
                conn.commit()
        if 'is_visible' not in columns:
            print("Migrating database: Adding is_visible to Subject table...")
            with db.engine.connect() as conn:
                conn.execute(db.text("ALTER TABLE subject ADD COLUMN is_visible BOOLEAN DEFAULT 1"))
                conn.commit()

        # Check and migrate TestResult table
        test_result_columns = [c['name'] for c in inspector.get_columns('test_result')]
        if 'control_work_id' not in test_result_columns:
            print("Migrating database: Adding control_work_id to TestResult table...")
            with db.engine.connect() as conn:
                conn.execute(db.text("ALTER TABLE test_result ADD COLUMN control_work_id INTEGER REFERENCES control_work(id)"))
                conn.commit()

        # Check and migrate Feedback table
        feedback_columns = [c['name'] for c in inspector.get_columns('feedback')]
        sender_added = False
        text_added = False
        if 'admin_response' not in feedback_columns:
            print("Migrating database: Adding admin_response to Feedback table...")
            with db.engine.connect() as conn:
                conn.execute(db.text("ALTER TABLE feedback ADD COLUMN admin_response TEXT"))
                conn.commit()
        if 'is_read' not in feedback_columns:
            print("Migrating database: Adding is_read to Feedback table...")
            with db.engine.connect() as conn:
                conn.execute(db.text("ALTER TABLE feedback ADD COLUMN is_read BOOLEAN DEFAULT 0"))
                conn.commit()
        if 'responded_at' not in feedback_columns:
            print("Migrating database: Adding responded_at to Feedback table...")
            with db.engine.connect() as conn:
                conn.execute(db.text("ALTER TABLE feedback ADD COLUMN responded_at DATETIME"))
                conn.commit()
        if 'sender' not in feedback_columns:
            print("Migrating database: Adding sender to Feedback table...")
            with db.engine.connect() as conn:
                conn.execute(db.text("ALTER TABLE feedback ADD COLUMN sender VARCHAR(10) DEFAULT 'student'"))
                conn.commit()
            sender_added = True
        if 'text' not in feedback_columns:
            print("Migrating database: Adding text to Feedback table...")
            with db.engine.connect() as conn:
                conn.execute(db.text("ALTER TABLE feedback ADD COLUMN text TEXT"))
                conn.commit()
            text_added = True

        # Backfill to new chat-style format (idempotent-ish)
        if sender_added or text_added:
            try:
                # 1) Ensure existing rows have sender/text
                db.session.execute(db.text(
                    "UPDATE feedback SET sender='student' WHERE sender IS NULL OR sender=''"
                ))
                db.session.execute(db.text(
                    "UPDATE feedback SET text=message WHERE text IS NULL"
                ))
                db.session.commit()

                # 2) Convert legacy admin_response into separate admin messages
                rows = db.session.execute(db.text(
                    "SELECT id, user_uuid, admin_response, responded_at, created_at "
                    "FROM feedback "
                    "WHERE admin_response IS NOT NULL AND TRIM(admin_response) <> ''"
                )).mappings().all()

                for r in rows:
                    # Avoid duplicating if this exact response already exists as an admin message
                    exists = db.session.execute(db.text(
                        "SELECT 1 FROM feedback "
                        "WHERE user_uuid=:user_uuid AND sender='admin' AND text=:text LIMIT 1"
                    ), {"user_uuid": r["user_uuid"], "text": r["admin_response"]}).first()
                    if exists:
                        continue

                    # Insert an admin message row
                    db.session.execute(db.text(
                        "INSERT INTO feedback (user_uuid, message, admin_response, sender, text, is_read, created_at, responded_at) "
                        "VALUES (:user_uuid, '', NULL, 'admin', :text, 1, :created_at, NULL)"
                    ), {
                        "user_uuid": r["user_uuid"],
                        "text": r["admin_response"],
                        "created_at": r["responded_at"] or r["created_at"],
                    })

                # Optional: clear legacy admin_response so UI doesn’t double-render
                db.session.execute(db.text(
                    "UPDATE feedback SET admin_response=NULL WHERE admin_response IS NOT NULL"
                ))
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Feedback migration warning: {e}")

        # Check and migrate Question table (difficulty/lesson for balanced tests)
        question_columns = [c['name'] for c in inspector.get_columns('question')]
        if 'difficulty' not in question_columns:
            print("Migrating database: Adding difficulty to Question table...")
            with db.engine.connect() as conn:
                conn.execute(db.text("ALTER TABLE question ADD COLUMN difficulty INTEGER DEFAULT 2"))
                conn.commit()
        if 'lesson' not in question_columns:
            print("Migrating database: Adding lesson to Question table...")
            with db.engine.connect() as conn:
                conn.execute(db.text("ALTER TABLE question ADD COLUMN lesson INTEGER"))
                conn.commit()

        # Init default admin/subjects if empty
        if not Admin.query.first():
            from werkzeug.security import generate_password_hash
            admin = Admin(
                username='asilbek',
                password_hash=generate_password_hash('jahonschool'),
                full_name='Administrator',
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()

        # If there is no admin with role='admin', promote the first admin user
        if not Admin.query.filter_by(role='admin').first():
            first_admin = Admin.query.first()
            if first_admin:
                first_admin.role = 'admin'
                db.session.commit()

        if not Subject.query.first():
            informatika = Subject(name='Informatika', grades='5,6', is_protected=True)
            python = Subject(name='Python', grades='7,8,9', is_protected=True)
            db.session.add(informatika)
            db.session.add(python)
            db.session.commit()

    return app

app = create_app()

if __name__ == '__main__':
    # Port 5000 is occupied by ControlCenter (AirPlay Receiver) on macOS Monterey+
    # Using 5001 to avoid conflict
    import os
    port = int(os.environ.get("PORT", 5050))
    app.run(host='0.0.0.0', port=port, debug=True)
