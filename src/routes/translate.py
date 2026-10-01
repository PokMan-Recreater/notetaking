from flask import Blueprint, jsonify, request

from src.services.translate import LANGUAGES, DEFAULT_TARGET, translate_text

translate_bp = Blueprint("translate", __name__)


@translate_bp.route("/translate", methods=["POST"])
def translate():
    """Translate English text(s) to the requested language.

    Accepts a JSON body with any of:
      - "title": text to translate
      - "content": text to translate
      - "target": one of "zh-TW", "zh-CN", "ko", "ja" (defaults to "zh-TW")

    Returns the translated values under the same "title"/"content" keys.
    """
    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({"error": "No data provided"}), 400

    target = data.get("target", DEFAULT_TARGET)
    if target not in LANGUAGES:
        return jsonify(
            {"error": f"Unsupported target language. Choose one of {sorted(LANGUAGES)}"}
        ), 400

    try:
        result = {}
        if "title" in data:
            result["title"] = translate_text(data.get("title") or "", target)
        if "content" in data:
            result["content"] = translate_text(data.get("content") or "", target)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Translation failed: {e}"}), 502

