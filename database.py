# ==========================================
# database.py — قاعدة البيانات المحلية (SQLite) وكل عمليات القراءة/الكتابة
# ==========================================
import os
import tempfile
import sqlite3
from datetime import datetime

DB_DIR = os.path.join(tempfile.gettempdir(), "ai_english_elite")
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "elite_partner.db")


def init_db():
    # // تم التعديل: إضافة timeout و WAL mode لضمان عدم قفل قاعدة البيانات (Database is locked)
    try:
        with sqlite3.connect(DB_PATH, timeout=15) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS user_profile (
                            key TEXT PRIMARY KEY,
                            value TEXT
                        )''')
            c.execute('''CREATE TABLE IF NOT EXISTS vocab_notebook (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            word TEXT UNIQUE,
                            word_type TEXT,
                            meaning_ar TEXT,
                            example TEXT,
                            status TEXT,
                            created_at TEXT
                        )''')
            c.execute('''CREATE TABLE IF NOT EXISTS user_stats (
                            key TEXT PRIMARY KEY,
                            value INTEGER
                        )''')
            # // جديد v10: سجل الأخطاء المتكررة
            c.execute('''CREATE TABLE IF NOT EXISTS mistakes_log (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            wrong_text TEXT,
                            correct_text TEXT,
                            explanation TEXT,
                            created_at TEXT
                        )''')
            # // جديد v10: سجل تقييمات كل رسالة (لبناء لوحة التحليل)
            c.execute('''CREATE TABLE IF NOT EXISTS eval_log (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            grammar INTEGER,
                            vocab INTEGER,
                            natural INTEGER,
                            fluency INTEGER,
                            cefr TEXT,
                            created_at TEXT
                        )''')
            # // جديد v10: جلسات المحادثة (لتبويب السجل)
            c.execute('''CREATE TABLE IF NOT EXISTS conversation_sessions (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            scenario TEXT,
                            title TEXT,
                            created_at TEXT
                        )''')
            c.execute('''CREATE TABLE IF NOT EXISTS conversation_messages (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            session_id INTEGER,
                            role TEXT,
                            content TEXT,
                            created_at TEXT
                        )''')
            conn.commit()
        # // ترقية جدول قديم: إضافة created_at لدفتر مفردات موجود من نسخة سابقة
        try:
            with sqlite3.connect(DB_PATH, timeout=10) as conn:
                conn.execute("ALTER TABLE vocab_notebook ADD COLUMN created_at TEXT")
                conn.commit()
        except Exception:
            pass  # العمود موجود مسبقاً
    except Exception as e:
        print(f"DB Init Error: {e}")


def set_profile(key: str, val: str):
    try:
        with sqlite3.connect(DB_PATH, timeout=10) as conn:
            c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO user_profile (key, value) VALUES (?, ?)", (key, str(val)))
            conn.commit()
    except Exception:
        pass


def get_profile(key: str, default: str = "") -> str:
    try:
        with sqlite3.connect(DB_PATH, timeout=10) as conn:
            c = conn.cursor()
            c.execute("SELECT value FROM user_profile WHERE key = ?", (key,))
            row = c.fetchone()
            return row[0] if row else default
    except Exception:
        return default


def update_stat(key: str, amount: int = 1):
    try:
        with sqlite3.connect(DB_PATH, timeout=10) as conn:
            c = conn.cursor()
            c.execute("INSERT OR IGNORE INTO user_stats (key, value) VALUES (?, 0)", (key,))
            c.execute("UPDATE user_stats SET value = value + ? WHERE key = ?", (amount, key))
            conn.commit()
    except Exception:
        pass


def get_stat(key: str) -> int:
    try:
        with sqlite3.connect(DB_PATH, timeout=10) as conn:
            c = conn.cursor()
            c.execute("SELECT value FROM user_stats WHERE key = ?", (key,))
            row = c.fetchone()
            return row[0] if row else 0
    except Exception:
        return 0


# ------------------------------------------
# جديد v10: مساعدات الأخطاء / التقييم / الجلسات / المراجعة الذكية
# ------------------------------------------
def log_mistake(wrong: str, correct: str, explanation: str):
    if not wrong or wrong.strip().lower() in ("none", "n/a", "-"):
        return
    try:
        with sqlite3.connect(DB_PATH, timeout=10) as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO mistakes_log (wrong_text, correct_text, explanation, created_at) VALUES (?, ?, ?, ?)",
                (wrong.strip(), correct.strip(), explanation.strip(), datetime.now().isoformat()),
            )
            conn.commit()
    except Exception:
        pass


def log_eval(eval_data: dict, cefr: str):
    def num(x):
        try:
            return int(str(x).split("/")[0].strip())
        except Exception:
            return None

    try:
        with sqlite3.connect(DB_PATH, timeout=10) as conn:
            c = conn.cursor()
            c.execute(
                """INSERT INTO eval_log (grammar, vocab, natural, fluency, cefr, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    num(eval_data.get("Grammar")),
                    num(eval_data.get("Vocab")),
                    num(eval_data.get("Natural")),
                    num(eval_data.get("Fluency")),
                    cefr,
                    datetime.now().isoformat(),
                ),
            )
            conn.commit()
    except Exception:
        pass


def create_session(scenario: str, title: str = None) -> int:
    try:
        with sqlite3.connect(DB_PATH, timeout=10) as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO conversation_sessions (scenario, title, created_at) VALUES (?, ?, ?)",
                (scenario, title or scenario, datetime.now().isoformat()),
            )
            conn.commit()
            return c.lastrowid
    except Exception:
        return None


def log_message_to_session(session_id, role: str, content: str):
    if not session_id or not content:
        return
    try:
        with sqlite3.connect(DB_PATH, timeout=10) as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO conversation_messages (session_id, role, content, created_at) VALUES (?, ?, ?, ?)",
                (session_id, role, content, datetime.now().isoformat()),
            )
            conn.commit()
    except Exception:
        pass


def get_all_sessions():
    try:
        with sqlite3.connect(DB_PATH, timeout=10) as conn:
            c = conn.cursor()
            c.execute("SELECT id, scenario, title, created_at FROM conversation_sessions ORDER BY created_at DESC")
            return c.fetchall()
    except Exception:
        return []


def load_session_messages(session_id):
    try:
        with sqlite3.connect(DB_PATH, timeout=10) as conn:
            c = conn.cursor()
            c.execute(
                "SELECT role, content FROM conversation_messages WHERE session_id = ? ORDER BY id ASC",
                (session_id,),
            )
            rows = c.fetchall()
            return [{"role": r, "content": ct, "audio": None, "eval": None} for r, ct in rows]
    except Exception:
        return []


def group_sessions_by_date(sessions):
    now = datetime.now()
    groups = {"📌 اليوم": [], "📅 أمس": [], "🗓️ هذا الأسبوع": [], "🗓️ هذا الشهر": [], "📦 أقدم": []}
    for sid, scenario_name, title, created in sessions:
        try:
            dt = datetime.fromisoformat(created)
        except Exception:
            continue
        diff_days = (now.date() - dt.date()).days
        if diff_days <= 0:
            groups["📌 اليوم"].append((sid, scenario_name, title, created))
        elif diff_days == 1:
            groups["📅 أمس"].append((sid, scenario_name, title, created))
        elif diff_days <= 7:
            groups["🗓️ هذا الأسبوع"].append((sid, scenario_name, title, created))
        elif diff_days <= 30:
            groups["🗓️ هذا الشهر"].append((sid, scenario_name, title, created))
        else:
            groups["📦 أقدم"].append((sid, scenario_name, title, created))
    return groups


def get_due_reviews():
    """مراجعة ذكية مبسطة: نعرض كلمات أُضيفت قبل 1 / 7 / 30 يوم بالضبط (نموذج تكرار متباعد مبسّط)."""
    now = datetime.now()
    buckets = {"🔔 تعلمتها أمس": [], "🔔 من الأسبوع الماضي": [], "🔔 من الشهر الماضي": []}
    try:
        with sqlite3.connect(DB_PATH, timeout=10) as conn:
            c = conn.cursor()
            c.execute("SELECT word, created_at FROM vocab_notebook WHERE created_at IS NOT NULL")
            rows = c.fetchall()
        for word, created in rows:
            try:
                dt = datetime.fromisoformat(created)
            except Exception:
                continue
            diff_days = (now.date() - dt.date()).days
            if diff_days == 1:
                buckets["🔔 تعلمتها أمس"].append(word)
            elif diff_days == 7:
                buckets["🔔 من الأسبوع الماضي"].append(word)
            elif diff_days == 30:
                buckets["🔔 من الشهر الماضي"].append(word)
    except Exception:
        pass
    return buckets


def save_vocab_quick(nw: dict):
    try:
        with sqlite3.connect(DB_PATH, timeout=10) as conn:
            c = conn.cursor()
            c.execute(
                """INSERT OR REPLACE INTO vocab_notebook
                   (word, word_type, meaning_ar, example, status, created_at) VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    nw["word"].strip(),
                    nw.get("type", "Phrase"),
                    nw.get("meaning", ""),
                    nw.get("example", ""),
                    "Needs Review",
                    datetime.now().isoformat(),
                ),
            )
            conn.commit()
        update_stat("total_vocab_words", 1)
    except Exception:
        pass
