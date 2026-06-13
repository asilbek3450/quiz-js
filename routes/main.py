import os
from pathlib import Path

from flask import (
    Blueprint, abort, current_app, redirect, render_template, request, send_file,
    send_from_directory, session, url_for,
)
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

@main_bp.get("/privacy")
def privacy():
    return render_template("privacy.html")


def _android_apk_path():
    return Path(current_app.root_path) / "android-app" / "app" / "release" / "JS-TEST.apk"


@main_bp.get("/download")
def download_app():
    apk_path = _android_apk_path()
    apk_size_mb = apk_path.stat().st_size / (1024 * 1024) if apk_path.exists() else None
    return render_template("download_app.html", apk_size_mb=apk_size_mb)


@main_bp.get("/download/android-apk")
def download_android_apk():
    apk_path = _android_apk_path()
    if not apk_path.exists():
        abort(404)

    return send_file(
        apk_path,
        mimetype="application/vnd.android.package-archive",
        as_attachment=True,
        download_name="JS-Test.apk",
        max_age=0,
    )

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
