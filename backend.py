import sqlite3
import datetime
import random
import string

DB_PATH = "campus_system.db"

# ====================== DB CONNECTION ======================
def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn, conn.cursor()

# ===================== NOTIF COLUMN FIX ====================
def ensure_notifications_columns():
    conn, cur = get_connection()
    cur.execute("PRAGMA table_info(notifications)")
    cols = [c[1] for c in cur.fetchall()]

    for col, type_ in [
        ("teacher_id", "TEXT"),
        ("subject", "TEXT"),
        ("timestamp", "TEXT")
    ]:
        if col not in cols:
            try:
                cur.execute(f"ALTER TABLE notifications ADD COLUMN {col} {type_}")
            except:
                pass

    conn.commit()
    conn.close()

# ===================== FULL DB SETUP =======================
def setup_database():
    conn, cur = get_connection()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS admin (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL
    )""")

    if not cur.execute("SELECT * FROM admin").fetchone():
        cur.execute("INSERT INTO admin VALUES ('admin','admin123')")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        roll_no TEXT PRIMARY KEY,
        name TEXT,
        course TEXT,
        year INTEGER,
        section TEXT
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS faculty (
        faculty_id TEXT PRIMARY KEY,
        name TEXT,
        subject TEXT
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS login_credentials (
        user_id TEXT PRIMARY KEY,
        password TEXT,
        role TEXT,
        first_login INTEGER
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        roll_no TEXT,
        faculty_id TEXT,
        subject TEXT,
        date TEXT,
        status TEXT
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS marks (
        roll_no TEXT,
        subject TEXT,
        exam_type TEXT,
        marks INTEGER,
        faculty_id TEXT
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        message TEXT,
        posted_by TEXT
    )""")

    conn.commit()
    conn.close()
    ensure_notifications_columns()

# ========================= UTILITIES ========================
def generate_roll_no():
    conn, cur = get_connection()
    n = cur.execute("SELECT COUNT(*) FROM students").fetchone()[0] + 1
    conn.close()
    return f"STU{n:03d}"

def generate_faculty_id():
    conn, cur = get_connection()
    n = cur.execute("SELECT COUNT(*) FROM faculty").fetchone()[0] + 1
    conn.close()
    return f"FAC{n:03d}"

def generate_password(prefix):
    return prefix + ''.join(random.choices(string.ascii_letters + string.digits, k=4))

# =================== LOGIN / PASSWORD =======================
def login_user(uid, pwd):
    conn, cur = get_connection()
    if uid == "admin":
        res = cur.execute("SELECT * FROM admin WHERE username=? AND password=?", (uid, pwd)).fetchone()
        conn.close()
        return ("admin", False) if res else (None, False)

    res = cur.execute(
        "SELECT user_id,password,role,first_login FROM login_credentials WHERE user_id=? AND password=?",
        (uid, pwd)
    ).fetchone()

    conn.close()
    return (res[2], bool(res[3])) if res else (None, False)

def update_password(uid, new_pw):
    conn, cur = get_connection()
    cur.execute("UPDATE login_credentials SET password=?, first_login=0 WHERE user_id=?", (new_pw, uid))
    conn.commit()
    conn.close()

# ===================== NOTIFICATIONS =========================
def post_admin_notification(title, msg):
    conn, cur = get_connection()
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("""
        INSERT INTO notifications (title,message,posted_by,teacher_id,subject,timestamp)
        VALUES (?, ?, 'admin', NULL, NULL, ?)
    """, (title, msg, ts))
    conn.commit()
    conn.close()

def post_teacher_notification(fid, subject, title, msg):
    conn, cur = get_connection()
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("""
        INSERT INTO notifications (title,message,posted_by,teacher_id,subject,timestamp)
        VALUES (?, ?, 'teacher', ?, ?, ?)
    """, (title, msg, fid, subject, ts))
    conn.commit()
    conn.close()

def get_admin_notifications():
    conn, cur = get_connection()
    rows = cur.execute("""
        SELECT title,message,timestamp,posted_by FROM notifications WHERE posted_by='admin'
        ORDER BY timestamp DESC
    """).fetchall()
    conn.close()
    return rows

def get_subject_notifications(sub):
    conn, cur = get_connection()
    rows = cur.execute("""
        SELECT title,message,timestamp,teacher_id FROM notifications
        WHERE posted_by='teacher' AND subject=?
        ORDER BY timestamp DESC
    """, (sub,)).fetchall()
    conn.close()
    return rows

def get_teacher_notifications(fid):
    conn, cur = get_connection()
    rows = cur.execute("""
        SELECT title,message,timestamp,posted_by,teacher_id,subject
        FROM notifications
        WHERE posted_by='admin' OR teacher_id=?
        ORDER BY timestamp DESC
    """, (fid,)).fetchall()
    conn.close()
    return rows
