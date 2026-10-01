"""Vercel serverless entrypoint.

Vercel's Python runtime auto-detects a Flask instance named `app` in a
root-level `main.py`. This file re-exports the app from `src.main` (after
ensuring `src` is importable) so Vercel serves the application correctly.
"""
import os
import sys

_REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
for _p in (_REPO_ROOT, os.path.join(_REPO_ROOT, "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from src.main import app  # noqa: E402,F401
