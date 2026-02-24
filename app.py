from flask import Flask, session
from datetime import timedelta
from extensions import db, babel
from routes.main import main_bp
from routes.admin import admin_bp
from routes.student import student_bp
import markdown
from models import Admin, Subject, Question

def create_app():
    app = Flask(__name__, template_folder="templates")
    app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_platform.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)

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
        
        # Check and migrate Subject table
        columns = [c['name'] for c in inspector.get_columns('subject')]
        if 'is_protected' not in columns:
            print("Migrating database: Adding is_protected to Subject table...")
            with db.engine.connect() as conn:
                conn.execute(db.text("ALTER TABLE subject ADD COLUMN is_protected BOOLEAN DEFAULT 0"))
                conn.commit()

        # Check and migrate TestResult table
        test_result_columns = [c['name'] for c in inspector.get_columns('test_result')]
        if 'control_work_id' not in test_result_columns:
            print("Migrating database: Adding control_work_id to TestResult table...")
            with db.engine.connect() as conn:
                conn.execute(db.text("ALTER TABLE test_result ADD COLUMN control_work_id INTEGER REFERENCES control_work(id)"))
                conn.commit()

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
                full_name='Administrator'
            )
            db.session.add(admin)
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