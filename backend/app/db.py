import os, sqlite3, uuid
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
DB_PATH = os.path.join(BASE, "app.db")
os.makedirs(BASE, exist_ok=True)


def now():
    return datetime.now(timezone.utc).isoformat()


def conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    with conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
          id TEXT PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL,
          password_hash TEXT NOT NULL, role TEXT NOT NULL CHECK(role IN ('student','faculty')),
          created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS documents (
          id TEXT PRIMARY KEY, title TEXT NOT NULL, subject TEXT NOT NULL, unit TEXT,
          description TEXT, filename TEXT NOT NULL, stored_path TEXT NOT NULL,
          uploaded_by TEXT NOT NULL, uploaded_by_name TEXT NOT NULL, created_at TEXT NOT NULL,
          FOREIGN KEY(uploaded_by) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS messages (
          id TEXT PRIMARY KEY, document_id TEXT NOT NULL, user_id TEXT NOT NULL,
          role TEXT NOT NULL, content TEXT NOT NULL, created_at TEXT NOT NULL
        );
        """)


def create_user(name, email, password, role):
    uid = str(uuid.uuid4())
    with conn() as c:
        c.execute("INSERT INTO users VALUES (?,?,?,?,?,?)", (uid, name, email.lower().strip(), generate_password_hash(password), role, now()))
    return get_user(uid)


def get_user(uid):
    with conn() as c:
        row = c.execute("SELECT id,name,email,role,created_at FROM users WHERE id=?", (uid,)).fetchone()
    return dict(row) if row else None


def authenticate(email, password):
    with conn() as c:
        row = c.execute("SELECT * FROM users WHERE email=?", (email.lower().strip(),)).fetchone()
    if not row or not check_password_hash(row["password_hash"], password):
        return None
    return {"id": row["id"], "name": row["name"], "email": row["email"], "role": row["role"], "created_at": row["created_at"]}


def add_document(data):
    with conn() as c:
        c.execute("""INSERT INTO documents
          (id,title,subject,unit,description,filename,stored_path,uploaded_by,uploaded_by_name,created_at)
          VALUES (?,?,?,?,?,?,?,?,?,?)""", tuple(data[k] for k in ["id","title","subject","unit","description","filename","stored_path","uploaded_by","uploaded_by_name","created_at"]))
    return get_document(data["id"])


def get_document(doc_id):
    with conn() as c:
        row = c.execute("SELECT * FROM documents WHERE id=?", (doc_id,)).fetchone()
    return dict(row) if row else None


def list_documents():
    with conn() as c:
        rows = c.execute("SELECT * FROM documents ORDER BY created_at DESC").fetchall()
    return [dict(r) for r in rows]


def add_message(document_id, user_id, role, content):
    mid = str(uuid.uuid4())
    with conn() as c:
        c.execute("INSERT INTO messages VALUES (?,?,?,?,?,?)", (mid, document_id, user_id, role, content, now()))


def get_messages(document_id, user_id, limit=30):
    with conn() as c:
        rows = c.execute("SELECT role,content,created_at FROM messages WHERE document_id=? AND user_id=? ORDER BY created_at DESC LIMIT ?", (document_id,user_id,limit)).fetchall()
    return [dict(r) for r in reversed(rows)]
