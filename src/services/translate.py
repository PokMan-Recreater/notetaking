"""English -> {Traditional Chinese, Simplified Chinese, Korean, Japanese} service.

Uses the free `deep-translator` package (no API key required).
It tries Google Translate first (supports longer text) and falls back to
MyMemory if Google is temporarily rate-limited or unavailable.
"""
import os
import time

from deep_translator import GoogleTranslator, MyMemoryTranslator

# Supported target languages (and the display names used by the UI).
LANGUAGES = {
    "zh-TW": "Traditional Chinese",
    "zh-CN": "Simplified Chinese",
    "ko": "Korean",
    "ja": "Japanese",
}

SOURCE_LANG = "en"
DEFAULT_TARGET = "zh-TW"

# Google Translate accepts the same codes as above.
GOOGLE_TARGET_CODES = {
    "zh-TW": "zh-TW",
    "zh-CN": "zh-CN",
    "ko": "ko",
    "ja": "ja",
}

# MyMemory requires region-qualified codes for some languages (and en-GB
# for the English source). See deep_translator.constants.MY_MEMORY_LANGUAGES_TO_CODES.
MYMEMORY_SOURCE_CODE = "en-GB"
MYMEMORY_TARGET_CODES = {
    "zh-TW": "zh-TW",
    "zh-CN": "zh-CN",
    "ko": "ko-KR",
    "ja": "ja-JP",
}

# Providing an email raises MyMemory's free daily limit from 5,000 to 50,000
# characters. Override via the MYMEMORY_EMAIL environment variable if desired.
MYMEMORY_EMAIL = os.environ.get("MYMEMORY_EMAIL", "notetaker@example.com")

# Google Translate accepts up to ~5000 chars per request via deep-translator.
_GOOGLE_MAX_CHARS = 4000
# MyMemory (free) accepts up to 500 chars per request.
_MYMEMORY_MAX_CHARS = 450
# Number of retries for transient failures (rate limits, timeouts, etc.).
_RETRIES = 3
_RETRY_DELAY = 1.5


def _split_text(text: str, max_chars: int):
    """Split text into chunks that each stay under max_chars, on word boundaries."""
    chunks = []
    for line in text.split("\n"):
        if not line.strip():
            chunks.append(line)
            continue
        while len(line) > max_chars:
            cut = line.rfind(" ", 0, max_chars)
            if cut == -1:
                cut = max_chars
            chunks.append(line[:cut])
            line = line[cut:].lstrip()
        chunks.append(line)
    return chunks


def _retry(fn, *args):
    """Call fn(*args), retrying on exception up to _RETRIES times."""
    last_exc = None
    for attempt in range(_RETRIES + 1):
        try:
            return fn(*args)
        except Exception as e:  # noqa: BLE001 - we raise at the end
            last_exc = e
            if attempt < _RETRIES:
                time.sleep(_RETRY_DELAY * (attempt + 1))
    raise last_exc


def _translate_google(text: str, target: str) -> str:
    translator = GoogleTranslator(
        source=SOURCE_LANG, target=GOOGLE_TARGET_CODES[target]
    )
    if len(text) <= _GOOGLE_MAX_CHARS:
        return translator.translate(text)
    translated = [
        translator.translate(chunk) for chunk in _split_text(text, _GOOGLE_MAX_CHARS)
    ]
    return "".join(translated)


def _translate_mymemory(text: str, target: str) -> str:
    translator = MyMemoryTranslator(
        source=MYMEMORY_SOURCE_CODE,
        target=MYMEMORY_TARGET_CODES[target],
        email=MYMEMORY_EMAIL,
    )
    if len(text) <= _MYMEMORY_MAX_CHARS:
        return translator.translate(text)
    parts = []
    for chunk in _split_text(text, _MYMEMORY_MAX_CHARS):
        parts.append(translator.translate(chunk) if chunk.strip() else chunk)
    return "".join(parts)


def translate_text(text: str, target: str = DEFAULT_TARGET) -> str:
    """Translate English text to the requested target language.

    `target` must be one of the keys in LANGUAGES. Returns the original text
    unchanged when it is empty/whitespace so the caller can skip the round-trip.
    """
    if target not in LANGUAGES:
        raise ValueError(f"Unsupported target language: {target}")

    text = (text or "").strip()
    if not text:
        return text

    # Try Google once (it supports longer text and is fast when available).
    try:
        return _translate_google(text, target)
    except Exception:
        # Fall back to MyMemory, retrying transient failures (rate limits,
        # timeouts, etc.) to improve reliability.
        try:
            return _retry(_translate_mymemory, text, target)
        except Exception:
            raise


# Backward-compatible alias kept for existing callers/tests.
def translate_en_to_zh_tw(text: str) -> str:
    return translate_text(text, "zh-TW")


