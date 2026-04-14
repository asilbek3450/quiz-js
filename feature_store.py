from __future__ import annotations

import json
import os
import secrets
from pathlib import Path
from typing import Any

from flask import current_app, g, url_for
from flask_babel import gettext as _
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

FEATURE_STORE_FILENAME = "feature_settings.json"
DEFAULT_GRADE_SETTINGS = {
    "excellent_min": 85,
    "good_min": 70,
    "satisfactory_min": 65,
    "fail_max": 64,
}
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def _feature_store_path() -> Path:
    instance_dir = Path(current_app.instance_path)
    instance_dir.mkdir(parents=True, exist_ok=True)
    store_path = instance_dir / FEATURE_STORE_FILENAME
    if not store_path.exists():
        store_path.write_text(
            json.dumps({"question_images": {}, "subject_grading": {}}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    return store_path


def _normalize_store(payload: Any) -> dict[str, dict[str, Any]]:
    data = payload if isinstance(payload, dict) else {}
    question_images = data.get("question_images")
    subject_grading = data.get("subject_grading")
    return {
        "question_images": question_images if isinstance(question_images, dict) else {},
        "subject_grading": subject_grading if isinstance(subject_grading, dict) else {},
    }


def load_feature_store() -> dict[str, dict[str, Any]]:
    # Request-level cache: faylni bir so'rov davomida bir marta o'qiymiz
    if hasattr(g, '_feature_store'):
        return g._feature_store
    store_path = _feature_store_path()
    try:
        payload = json.loads(store_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        current_app.logger.warning("feature_store o'qishda xato: %s", e)
        payload = {}
    result = _normalize_store(payload)
    g._feature_store = result
    return result


def save_feature_store(payload: dict[str, dict[str, Any]]) -> None:
    store_path = _feature_store_path()
    normalized = _normalize_store(payload)
    temp_path = store_path.with_suffix(".tmp")
    temp_path.write_text(json.dumps(normalized, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temp_path, store_path)
    # Keshni tozalash — saqlangandan keyin yangi qiymat o'qilsin
    if hasattr(g, '_feature_store'):
        del g._feature_store


def get_subject_grade_settings(subject_id: int | None) -> dict[str, int]:
    settings = dict(DEFAULT_GRADE_SETTINGS)
    if not subject_id:
        return settings

    store = load_feature_store()
    raw_settings = store["subject_grading"].get(str(subject_id), {})
    if not isinstance(raw_settings, dict):
        return settings

    for key, default_value in DEFAULT_GRADE_SETTINGS.items():
        if key == "fail_max":
            raw_value = raw_settings.get(key, settings["satisfactory_min"] - 1)
        else:
            raw_value = raw_settings.get(key, default_value)
        try:
            settings[key] = int(raw_value)
        except (TypeError, ValueError):
            settings[key] = default_value

    # validate_grade_settings xato bo'lsa (None emas) — defaults qaytaramiz
    if validate_grade_settings(
        settings["excellent_min"],
        settings["good_min"],
        settings["satisfactory_min"],
        settings["fail_max"],
    ) is not None:
        return dict(DEFAULT_GRADE_SETTINGS)

    return settings


def validate_grade_settings(
    excellent_min: int,
    good_min: int,
    satisfactory_min: int,
    fail_max: int,
) -> str | None:
    values = [excellent_min, good_min, satisfactory_min, fail_max]
    if any(value < 0 or value > 100 for value in values):
        return _("Baho chegaralari 0 dan 100 gacha bo'lishi kerak")
    if not excellent_min > good_min > satisfactory_min:
        return _("Chegaralar kamayish tartibida bo'lishi kerak: A'lo > Yaxshi > Qoniqarli")
    if fail_max >= satisfactory_min:
        return _("Qoniqarsiz chegarasi Qoniqarli chegarasidan past bo'lishi kerak")
    if fail_max != satisfactory_min - 1:
        return _("Qoniqarsiz chegarasi Qoniqarli chegarasidan 1 foiz past bo'lishi kerak")
    return None


def set_subject_grade_settings(
    subject_id: int,
    excellent_min: int,
    good_min: int,
    satisfactory_min: int,
    fail_max: int,
) -> None:
    store = load_feature_store()
    normalized = {
        "excellent_min": int(excellent_min),
        "good_min": int(good_min),
        "satisfactory_min": int(satisfactory_min),
        "fail_max": int(fail_max),
    }

    if normalized == DEFAULT_GRADE_SETTINGS:
        store["subject_grading"].pop(str(subject_id), None)
    else:
        store["subject_grading"][str(subject_id)] = normalized
    save_feature_store(store)


def remove_subject_grade_settings(subject_id: int) -> None:
    store = load_feature_store()
    store["subject_grading"].pop(str(subject_id), None)
    save_feature_store(store)


def get_grade_info(percentage: float, subject_id: int | None = None) -> dict[str, Any]:
    settings = get_subject_grade_settings(subject_id)

    if percentage >= settings["excellent_min"]:
        return {
            "level": "excellent",
            "label": _("A'lo (5)"),
            "short_label": _("A'lo"),
            "progress_class": "bg-success",
            "badge_class": "bg-success",
            "text_class": "grade-excellent",
        }
    if percentage >= settings["good_min"]:
        return {
            "level": "good",
            "label": _("Yaxshi (4)"),
            "short_label": _("Yaxshi"),
            "progress_class": "bg-info",
            "badge_class": "bg-info",
            "text_class": "grade-good",
        }
    if percentage >= settings["satisfactory_min"]:
        return {
            "level": "satisfactory",
            "label": _("Qoniqarli (3)"),
            "short_label": _("Qoniqarli"),
            "progress_class": "bg-warning",
            "badge_class": "bg-warning text-dark",
            "text_class": "grade-satisfactory",
        }
    return {
        "level": "fail",
        "label": _("Qoniqarsiz (2)"),
        "short_label": _("Qoniqarsiz"),
        "progress_class": "bg-danger",
        "badge_class": "bg-danger",
        "text_class": "grade-fail",
    }


def _question_images_map() -> dict[str, str]:
    store = load_feature_store()
    raw = store["question_images"]
    return raw if isinstance(raw, dict) else {}


def get_question_image_relative_path(question_id: int | None) -> str | None:
    if not question_id:
        return None
    path = _question_images_map().get(str(question_id))
    return path if isinstance(path, str) and path.strip() else None


def get_question_image_url(question_id: int | None) -> str | None:
    relative_path = get_question_image_relative_path(question_id)
    if not relative_path:
        return None
    return url_for("static", filename=relative_path)


def set_question_image(question_id: int, relative_path: str) -> None:
    store = load_feature_store()
    store["question_images"][str(question_id)] = relative_path
    save_feature_store(store)


def remove_question_image(question_id: int) -> str | None:
    store = load_feature_store()
    removed = store["question_images"].pop(str(question_id), None)
    save_feature_store(store)
    return removed if isinstance(removed, str) else None


def _validate_image_extension(filename: str) -> str:
    safe_name = secure_filename(filename)
    if "." not in safe_name:
        raise ValueError(_("Rasm fayli formati noto'g'ri"))
    extension = safe_name.rsplit(".", 1)[1].lower()
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValueError(_("Faqat PNG, JPG, JPEG, GIF va WEBP rasm fayllari qabul qilinadi"))
    return extension


def save_question_image_upload(file_storage: FileStorage | None) -> str | None:
    if not file_storage or not file_storage.filename:
        return None

    extension = _validate_image_extension(file_storage.filename)
    upload_dir = Path(current_app.static_folder) / "uploads" / "questions"
    upload_dir.mkdir(parents=True, exist_ok=True)

    filename = f"question_{secrets.token_hex(16)}.{extension}"
    target_path = upload_dir / filename
    file_storage.save(target_path)
    return f"uploads/questions/{filename}"


def delete_question_image_file(relative_path: str | None) -> None:
    if not relative_path:
        return

    static_root = Path(current_app.static_folder).resolve()
    candidate = (static_root / relative_path).resolve()
    try:
        candidate.relative_to(static_root)
    except ValueError:
        return

    if candidate.is_file():
        candidate.unlink()


def attach_question_media(question: Any) -> Any:
    image_path = get_question_image_relative_path(getattr(question, "id", None))
    question.image_path = image_path
    question.image_url = url_for("static", filename=image_path) if image_path else None
    return question
