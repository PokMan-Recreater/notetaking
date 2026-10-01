import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from src.models.user import db
from src.routes.user import user_bp
from src.routes.note import note_bp
from src.routes.translate import translate_bp
from src.models.note import Note

# Load environment variables from a .env file (e.g. DATABASE_URL for Neon).
load_dotenv()

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')

# Enable CORS for all routes
CORS(app)

# register blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(note_bp, url_prefix='/api')
app.register_blueprint(translate_bp, url_prefix='/api')

# Configure the database. When DATABASE_URL is set (e.g. a Neon PostgreSQL
# connection string), use it; otherwise fall back to a local SQLite file.
ROOT_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
DATABASE_URL = os.environ.get('DATABASE_URL', '').strip()
IS_VERCEL = os.environ.get('VERCEL', '') == '1'

if DATABASE_URL:
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
elif IS_VERCEL:
    # Vercel's filesystem is read-only, so SQLite can't be used there.
    # Serve the app anyway; the /api routes will surface a clear error.
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
else:
    DB_PATH = os.path.join(ROOT_DIR, 'database', 'app.db')
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_PATH}"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Create tables, but don't let a database/connection problem crash the whole
# app at import time (which would make every request return 500).
try:
    with app.app_context():
        db.create_all()
except Exception as e:  # noqa: BLE001
    app.logger.error("Database initialization failed: %s", e)


@app.route('/api/health')
def health():
    """Simple health check that also reports database connectivity."""
    try:
        db.session.execute(db.text('SELECT 1'))
        db_ok = True
    except Exception:
        db_ok = False
    return {'status': 'ok', 'database': db_ok, 'database_uri': app.config['SQLALCHEMY_DATABASE_URI'].split('@')[-1]}

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
