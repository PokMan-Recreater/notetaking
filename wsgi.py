"""Vercel serverless entrypoint.

Vercel's Python runtime looks for a WSGI application named `app` at a
supported entrypoint file. This file re-exports the Flask app from `src.main`
so Vercel can load it (and route every request to it).
"""
import os
import sys

# Ensure the repository root (and thus the `src` package) is importable,
# regardless of how Vercel's runtime invokes this module.
_REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
for _p in (_REPO_ROOT, os.path.join(_REPO_ROOT, "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from src.main import app  # noqa: F401,E402
