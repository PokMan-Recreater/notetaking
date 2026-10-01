"""Vercel serverless entrypoint.

Vercel's Python runtime looks for a WSGI application named `app` at a
supported entrypoint file. This file re-exports the Flask app from `src.main`
so Vercel can load it (and route every request to it).
"""
from src.main import app  # noqa: F401
