from flask import Blueprint, render_template, request, redirect, url_for, session, send_from_directory
import os
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

@main_bp.route('/manifest.json')
def manifest():
    return send_from_directory(os.path.join(main_bp.root_path, '..', 'static'), 'manifest.json')

@main_bp.route('/sw.js')
def service_worker():
    return send_from_directory(os.path.join(main_bp.root_path, '..', 'static'), 'sw.js')
