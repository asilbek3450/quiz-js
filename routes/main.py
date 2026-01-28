from flask import Blueprint, render_template, request, redirect, url_for, session
from flask_babel import gettext as _
from extensions import db
from models import Subject

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@main_bp.route('/set_language/<lang>')
def set_language(lang):
    if lang in ['uz', 'ru', 'en']:
        session['lang'] = lang
    return redirect(request.referrer or url_for('main.index'))
