from flask import Blueprint, render_template, request, redirect, url_for, session, send_from_directory
import os
from flask_babel import gettext as _
from extensions import db
from models import Subject

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@main_bp.get("/about")
def about():
    return render_template("page.html", page_title="About", h1=_("Platforma haqida"),
                           seo_description=_("Informatika va zamonaviy texnologiyalar bo'yicha test platformasi haqida ma'lumot."))

@main_bp.get("/contact")
def contact():
    return render_template("page.html", page_title="Contact", h1=_("Aloqa"),
                           seo_description=_("Bog'lanish uchun aloqa sahifasi. Taklif va savollaringizni yuboring."))

@main_bp.get("/services")
def services():
    return render_template("page.html", page_title="Services", h1=_("Xizmatlar"),
                           seo_description=_("Platforma xizmatlari: testlar, nazorat ishlari va natijalar tahlili."))

@main_bp.get("/blog")
def blog():
    return render_template("page.html", page_title="Blog", h1=_("Blog"),
                           seo_description=_("Ta'lim, informatika va dasturlash bo'yicha maqolalar va yangiliklar."))

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
