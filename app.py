# ==========================================
# AI English Conversation Partner — v13 FIXED
# ==========================================

import os
import re
import time
import uuid
import hashlib
import tempfile
import asyncio
import base64
import random
import sqlite3
import threading
import shutil
from string import Template
from datetime import datetime, timedelta

import streamlit as st
import streamlit.components.v1 as components
import edge_tts
from google import genai
from google.genai import types

# ==========================================
# 0. إعداد قاعدة البيانات المحلية
# ==========================================
DB_DIR = os.path.join(tempfile.gettempdir(), "ai_english_elite")
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "elite_partner.db")

def init_db():
    """Initialize database with proper error handling"""
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
                            status TEXT
                        )''')
            c.execute('''CREATE TABLE IF NOT EXISTS saved_sessions (
                            id TEXT PRIMARY KEY,
                            title TEXT,
                            scenario TEXT,
                            created_at TEXT,
                            messages_json TEXT
                        )''')
            c.execute('''CREATE TABLE IF NOT EXISTS user_stats (
                            key TEXT PRIMARY KEY,
                            value INTEGER
                        )''')
            conn.commit()
    except Exception as e:
        st.error(f"❌ Database Initialization Error: {e}")
        raise

init_db()

def set_profile(key: str, val: str):
    """Set profile value with error handling"""
    try:
        with sqlite3.connect(DB_PATH, timeout=15) as conn:
            c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO user_profile (key, value) VALUES (?, ?)", 
                      (key, str(val)))
            conn.commit()
    except Exception as e:
        print(f"⚠️ DB Error (set_profile): {e}")

def get_profile(key: str, default: str = "") -> str:
    """Get profile value with error handling"""
    try:
        with sqlite3.connect(DB_PATH, timeout=15) as conn:
            c = conn.cursor()
            c.execute("SELECT value FROM user_profile WHERE key = ?", (key,))
            row = c.fetchone()
            return row[0] if row else default
    except Exception as e:
        print(f"⚠️ DB Error (get_profile): {e}")
        return default

def update_stat(key: str, amount: int = 1):
    """Update statistics"""
    try:
        with sqlite3.connect(DB_PATH, timeout=15) as conn:
            c = conn.cursor()
            c.execute("INSERT OR IGNORE INTO user_stats (key, value) VALUES (?, 0)", (key,))
            c.execute("UPDATE user_stats SET value = value + ? WHERE key = ?", (amount, key))
            conn.commit()
    except Exception as e:
        print(f"⚠️ DB Error (update_stat): {e}")

def get_stat(key: str) -> int:
    """Get statistics"""
    try:
        with sqlite3.connect(DB_PATH, timeout=15) as conn:
            c = conn.cursor()
            c.execute("SELECT value FROM user_stats WHERE key = ?", (key,))
            row = c.fetchone()
            return row[0] if row else 0
    except Exception as e:
        print(f"⚠️ DB Error (get_stat): {e}")
        return 0

# ✅ إصلاح 1: تنظيف الملفات الصوتية القديمة
def cleanup_old_audio_files(days=7):
    """حذف الملفات الصوتية الأقدم من عدد محدد من الأيام"""
    try:
        cutoff_time = time.time() - (days * 24 * 3600)
        for root, dirs, files in os.walk(DB_DIR):
            for f in files:
                if f.endswith('.mp3'):
                    fpath = os.path.join(root, f)
                    if os.path.getmtime(fpath) < cutoff_time:
                        os.remove(fpath)
    except Exception as e:
        print(f"⚠️ Cleanup error: {e}")

cleanup_old_audio_files()

# Session state initialization
if "session_audio_dir" not in st.session_state:
    st.session_state.session_audio_dir = os.path.join(DB_DIR, uuid.uuid4().hex)
    os.makedirs(st.session_state.session_audio_dir, exist_ok=True)

AUDIO_DIR = st.session_state.session_audio_dir

# ==========================================
# 1. إعدادات الصفحة والتصميم
# ==========================================
st.set_page_config(
    page_title="Elite English Partner",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

DEFAULT_MODEL = "gemini-2.5-flash"

SCENARIO_ICONS = {
    "Casual Friend (Everyday Chat)": "☕",
    "Supermarket Customer (Work Practice)": "🛒",
    "Grammar & Translation Coach": "📘",
    "Speaking Placement Test (10+ Questions)": "📝",
}

PROMPTS = {
    "Casual Friend (Everyday Chat)": (
        "Act as a warm, casual native English-speaking friend. Talk naturally about everyday "
        "topics. Keep the tone relaxed and friendly, ask natural follow-up questions, and let "
        "the conversation flow naturally."
    ),
    "Supermarket Customer (Work Practice)": (
        "Roleplay as a customer at a supermarket while the user practices being the employee. "
        "Ask about prices, product locations, and availability, and make small talk typical of "
        "a supermarket checkout interaction."
    ),
    "Grammar & Translation Coach": (
        "Act as a supportive grammar and Arabic-English translation coach. Help the user "
        "translate sentences accurately, explain grammar rules clearly with examples, and "
        "correct mistakes with a brief explanation."
    ),
    "Speaking Placement Test (10+ Questions)": (
        "Conduct a structured English placement test. Ask 10-15 questions of gradually "
        "increasing difficulty. After completion, give an estimated CEFR level (A1-C2)."
    ),
}

st.markdown(
    """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        div[data-testid="stChatMessage"] {
            background-color: var(--secondary-background-color) !important;
            border-radius: 16px !important;
            padding: 1.5rem !important;
            margin-bottom: 1rem !important;
            border: 1px solid rgba(14, 165, 233, 0.2) !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.02) !important;
        }

        div[data-testid="stButton"] > button {
            border-radius: 10px !important;
            transition: all 0.3s ease !important;
            border: 1px solid rgba(14, 165, 233, 0.4) !important;
        }
        div[data-testid="stButton"] > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 12px rgba(14, 165, 233, 0.2) !important;
            border-color: #0ea5e9 !important;
        }
        
        .hero-card {
            background: linear-gradient(135deg, rgba(14,165,233,0.08) 0%, rgba(139,92,246,0.08) 100%);
            border-left: 6px solid #0ea5e9;
            border-radius: 14px; 
            padding: 24px; 
            margin-bottom: 24px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        }
        .hero-title { font-size: 1.7rem; font-weight: 800; margin-bottom: 8px; }
        .hero-sub { font-size: 1rem; opacity: 0.8; margin-bottom: 16px; }
        
        .badge {
            display: inline-flex; align-items: center; gap: 6px;
            padding: 6px 14px; border-radius: 10px; font-size: 0.85rem; font-weight: 600;
            background-color: rgba(14, 165, 233, 0.15); 
            color: #0ea5e9; 
            border: 1px solid rgba(14, 165, 233, 0.3);
        }
        
        .eval-card {
            background-color: rgba(0, 0, 0, 0.03);
            border: 1px solid rgba(128, 128, 128, 0.2);
            border-radius: 12px; 
            padding: 16px; 
            margin-top: 10px;
            margin-bottom: 14px;
            font-size: 0.95rem;
        }
        .eval-scores { 
            display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 10px; 
        }
        .eval-score-item {
            background-color: rgba(14, 165, 233, 0.1);
            color: #0ea5e9;
            padding: 6px 12px;
            border-radius: 8px;
            font-size: 0.85rem;
            font-weight: 700;
            border: 1px solid rgba(14, 165, 233, 0.2);
        }
        
        .side-heading {
            font-size: 0.85rem; font-weight: 700; text-transform: uppercase;
            opacity: 0.7; margin: 24px 0 10px 0;
            border-bottom: 2px solid rgba(128, 128, 128, 0.1);
            padding-bottom: 6px;
        }
        
        .vocab-row {
            background-color: var(--secondary-background-color);
            border: 1px solid rgba(128, 128, 128, 0.15);
            border-radius: 12px;
            padding: 18px;
            margin-bottom: 14px;
            transition: all 0.3s ease;
        }
        .vocab-row:hover {
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
            transform: translateY(-3px);
            border-color: rgba(14, 165, 233, 0.4);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================================
# 2. الشريط الجانبي: الإعدادات
# ==========================================
st.sidebar.title("🎓 Elite English")
st.sidebar.caption("بيئة تعليمية هادئة وذكية")

# ✅ إصلاح 2: التحقق من API Key بشكل صحيح
with st.sidebar.expander("🔑 إعدادات API (اضغط للفتح)", expanded=not bool(os.environ.get("GEMINI_API_KEY"))):
    env_key = os.environ.get("GEMINI_API_KEY", "")
    use_different_key = False
    if env_key:
        st.success("✅ مفتاح النظام مفعل.")
        use_different_key = st.checkbox("إدخال مفتاح مختلف")

    if env_key and not use_different_key:
        api_key = env_key
    else:
        api_key = st.text_input("Gemini API Key:", type="password", key="api_key_input")
        if not api_key:
            st.warning("⚠️ يرجى إدخال API Key لمتابعة")
        
    model_name = st.text_input("Gemini Model:", value=DEFAULT_MODEL, key="model_input")

st.sidebar.markdown('<div class="side-heading">💬 بيئة المحادثة</div>', unsafe_allow_html=True)
scenario = st.sidebar.selectbox(
    "اختر السيناريو:",
    [
        "Casual Friend (Everyday Chat)",
        "Supermarket Customer (Work Practice)",
        "Grammar & Translation Coach",
        "Speaking Placement Test (10+ Questions)",
    ],
    format_func=lambda s: f"{SCENARIO_ICONS.get(s, '💬')} {s}",
)

strictness = st.sidebar.selectbox(
    "مستوى تصحيح الأخطاء:",
    ["تصحيح جميع الأخطاء بدقة", "الأخطاء الكبيرة فقط (لتشجيع الطلاقة)", "بدون تصحيح"],
)

st.sidebar.markdown('<div class="side-heading">🔊 الصوت والتحدث</div>', unsafe_allow_html=True)
voice_label = st.sidebar.selectbox(
    "اختر المعلم الصوتي:",
    ["Aria — US Female", "Guy — US Male", "Sonia — UK Female", "Ryan — UK Male"],
)
VOICE_MAP = {
    "Aria — US Female": "en-US-AriaNeural",
    "Guy — US Male": "en-US-GuyNeural",
    "Sonia — UK Female": "en-GB-SoniaNeural",
    "Ryan — UK Male": "en-GB-RyanNeural",
}
voice_id = VOICE_MAP[voice_label]

autoplay_audio = st.sidebar.checkbox("🔊 التشغيل التلقائي للصوت", value=True)
voice_only_mode = st.sidebar.toggle("🎙️ وضع المكالمة الصوتية", value=False)

st.sidebar.markdown('<div class="side-heading">⚙️ خيارات الجلسة</div>', unsafe_allow_html=True)
if st.sidebar.button("🔄 بدء جلسة جديدة", use_container_width=True):
    for k in list(st.session_state.keys()):
        if k != "session_audio_dir":
            del st.session_state[k]
    st.rerun()

# ==========================================
# 3. معالج الصوت (Text-to-Speech)
# ==========================================
# ✅ إصلاح 3: تحسين دالة speak() مع معالجة أفضل للأخطاء
def speak(text: str, voice: str) -> str:
    """Generate speech with proper async handling"""
    out_path = os.path.join(AUDIO_DIR, f"tts_{uuid.uuid4().hex}.mp3")
    
    def run_async():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            communicate = edge_tts.Communicate(text, voice)
            loop.run_until_complete(communicate.save(out_path))
            loop.close()
        except Exception as e:
            print(f"❌ TTS Error: {e}")
            raise
    
    try:
        t = threading.Thread(target=run_async, daemon=True)
        t.start()
        t.join(timeout=30)  # ✅ إصلاح: إضافة timeout
        
        if not os.path.exists(out_path):
            raise Exception("Audio file was not created")
        
        return out_path
    except Exception as e:
        print(f"❌ Speech generation failed: {e}")
        return None

_VOICE_PLAYER_TEMPLATE = Template("""
<!DOCTYPE html>
<html>
<head>
<style>
  html, body { margin:0; padding:2px 0 0 0; background: transparent; font-family: sans-serif; }
  .vp-wrap {
    display: inline-flex; align-items: center; gap: 12px;
    background-color: rgba(128, 128, 128, 0.08);
    border: 1px solid rgba(128, 128, 128, 0.2); border-radius: 30px; padding: 6px 14px 6px 6px;
  }
  .vp-btn {
    width: 34px; height: 34px; border-radius: 50%; border: none; cursor: pointer;
    background-color: #0ea5e9; color: #fff; font-size: 13px;
    display: flex; align-items: center; justify-content: center;
    transition: all 0.2s;
  }
  .vp-btn:hover { background-color: #0284c7; transform: scale(1.05); }
  .vp-wave { position: relative; width: $${wave_width}px; height: 26px; cursor: pointer; }
  .vp-bars-bg, .vp-bars-fixed { position: absolute; top: 0; left: 0; width: $${wave_width}px; height: 100%; display: flex; align-items: center; gap: 3px; }
  .vp-bars-bg span { display: block; width: 3px; border-radius: 2px; background: rgba(128, 128, 128, 0.3); }
  .vp-bars-fixed span { display: block; width: 3px; border-radius: 2px; background-color: #0ea5e9; }
  .vp-clip { position: absolute; top: 0; left: 0; height: 100%; width: 0px; overflow: hidden; }
  .vp-time { font-size: 12px; font-weight: 700; opacity: 0.7; min-width: 36px; text-align: right; }
</style>
</head>
<body>
  <div class="vp-wrap" id="wrap">
    <button class="vp-btn" id="btn">&#9658;</button>
    <div class="vp-wave" id="wave">
      <div class="vp-bars-bg">${bars}</div>
      <div class="vp-clip" id="clip"><div class="vp-bars-fixed">${bars}</div></div>
    </div>
    <span class="vp-time" id="timeLabel">0:00</span>
    <audio id="aud" preload="auto" ${autoplay_attr} src="data:audio/mpeg;base64,${b64}"></audio>
  </div>
<script>
  var audio = document.getElementById('aud');
  var btn = document.getElementById('btn');
  var wave = document.getElementById('wave');
  var clip = document.getElementById('clip');
  var timeLabel = document.getElementById('timeLabel');
  var WAVE_WIDTH = ${wave_width};

  function fmt(s) {
    if (!isFinite(s) || s < 0) return '0:00';
    s = Math.round(s);
    var m = Math.floor(s / 60), r = s % 60;
    return m + ':' + (r < 10 ? '0' : '') + r;
  }
  audio.addEventListener('loadedmetadata', function () { timeLabel.textContent = fmt(audio.duration); });
  audio.addEventListener('play', function () { btn.innerHTML = '&#10074;&#10074;'; });
  audio.addEventListener('pause', function () { btn.innerHTML = '&#9658;'; });
  audio.addEventListener('ended', function () { btn.innerHTML = '&#9658;'; clip.style.width = '0px'; });
  audio.addEventListener('timeupdate', function () {
    if (audio.duration) {
      clip.style.width = ((audio.currentTime / audio.duration) * WAVE_WIDTH) + 'px';
      timeLabel.textContent = fmt(audio.currentTime);
    }
  });
  btn.addEventListener('click', function () { if (audio.paused) audio.play(); else audio.pause(); });
  wave.addEventListener('click', function (e) {
    var rect = wave.getBoundingClientRect();
    var frac = Math.min(Math.max((e.clientX - rect.left) / rect.width, 0), 1);
    if (isFinite(audio.duration)) audio.currentTime = frac * audio.duration;
  });
  if (audio.autoplay) audio.play().catch(function(){});
</script>
</body>
</html>
""")

def _wave_bar_heights(seed_key: str, bars: int = 40):
    rng = random.Random(seed_key)
    return [rng.randint(6, 22) for _ in range(bars)]

def render_voice_player(audio_path: str, autoplay: bool):
    """Render voice player with proper error handling"""
    try:
        if not os.path.exists(audio_path):
            st.warning("⚠️ الملف الصوتي غير متوفر")
            return
            
        with open(audio_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        
        heights = _wave_bar_heights(os.path.basename(audio_path))
        bars_html = "".join(f'<span style="height:{h}px"></span>' for h in heights)
        html = _VOICE_PLAYER_TEMPLATE.substitute(
            wave_width=220,
            bars=bars_html,
            autoplay_attr="autoplay" if autoplay else "",
            b64=b64
        )
        components.html(html, height=55, scrolling=False)
    except Exception as e:
        print(f"❌ Voice player error: {e}")
        st.warning(f"⚠️ خطأ في تشغيل الصوت: {e}")

# ==========================================
# 4. التبويبات الرئيسية
# ==========================================
tab_chat, tab_vocab, tab_profile = st.tabs([
    "💬 قاعة المحادثة", 
    "📓 دفتر المفردات", 
    "🧠 الملف الشخصي"
])

# ------------------------------------------
# التبويب 3: الملف الشخصي
# ------------------------------------------
with tab_profile:
    st.subheader("الملف الشخصي وذاكرة الذكاء الاصطناعي")
    st.caption("يستخدم الذكاء الاصطناعي هذه المعلومات لتخصيص المحادثة")

    col_prof1, col_prof2 = st.columns([2, 1])
    
    with col_prof1:
        with st.form("profile_form"):
            p_name = st.text_input("اسمك الكريم:", value=get_profile("name", ""))
            level_options = ["A1 (مبتدئ)", "A2 (مبتدئ متقدم)", "B1 (متوسط)", 
                           "B2 (متوسط متقدم)", "C1 (متقدم)", "C2 (محترف)"]
            saved_level = get_profile("level", "B1 (متوسط)")
            p_level = st.selectbox(
                "مستواك في الإنجليزية:",
                level_options,
                index=level_options.index(saved_level) if saved_level in level_options else 2,
            )
            p_goals = st.text_input(
                "هدف التعلم:",
                value=get_profile("goals", "")
            )
            p_notes = st.text_area(
                "ملاحظات خاصة:",
                value=get_profile("notes", "")
            )
            
            if st.form_submit_button("💾 حفظ البيانات"):
                set_profile("name", p_name)
                set_profile("level", p_level)
                set_profile("goals", p_goals)
                set_profile("notes", p_notes)
                st.success("✅ تم تحديث البيانات بنجاح!")
    
    with col_prof2:
        st.markdown("### 📊 الإحصائيات")
        st.metric("💬 الرسائل", get_stat('total_messages'))
        st.metric("📓 المفردات المحفوظة", get_stat('total_vocab_saved'))
        st.metric("📚 الكلمات", get_stat('total_words'))

# ------------------------------------------
# التبويب 2: المفردات
# ------------------------------------------
with tab_vocab:
    st.subheader("دفتر المفردات الذكي")
    
    with st.expander("➕ إضافة كلمة جديدة"):
        with st.form("add_vocab"):
            col_v1, col_v2 = st.columns(2)
            new_word = col_v1.text_input("الكلمة (English):")
            new_type = col_v2.selectbox("التصنيف:", 
                ["Verb (فعل)", "Noun (اسم)", "Phrase (تعبير)", "Adjective (صفة)", "Other"])
            new_meaning = st.text_input("المعنى (العربية):")
            new_example = st.text_input("مثال (اختياري):")
            
            if st.form_submit_button("💾 حفظ"):
                if new_word and new_meaning:
                    try:
                        with sqlite3.connect(DB_PATH, timeout=15) as conn:
                            c = conn.cursor()
                            c.execute(
                                "INSERT OR REPLACE INTO vocab_notebook (word, word_type, meaning_ar, example, status) VALUES (?, ?, ?, ?, ?)",
                                (new_word.strip(), new_type, new_meaning.strip(), new_example.strip(), "Needs Review")
                            )
                            conn.commit()
                        st.success(f"✅ تم حفظ: {new_word}")
                        update_stat("total_vocab_saved", 1)
                    except Exception as e:
                        st.error(f"❌ خطأ: {e}")
                else:
                    st.warning("⚠️ أدخل الكلمة والمعنى")

    try:
        with sqlite3.connect(DB_PATH, timeout=15) as conn:
            c = conn.cursor()
            c.execute("SELECT id, word, word_type, meaning_ar, example, status FROM vocab_notebook ORDER BY id DESC")
            vocab_rows = c.fetchall()

        if vocab_rows:
            search_q = st.text_input("🔍 ابحث في المفردات...")
            filtered = [r for r in vocab_rows 
                       if search_q.lower() in r[1].lower() or search_q.lower() in r[3].lower()]
            
            st.caption(f"📊 {len(vocab_rows)} كلمات محفوظة")
            
            for row in filtered:
                r_id, r_word, r_type, r_meaning, r_example, r_status = row
                st.markdown(f"""
                <div class="vocab-row">
                    <strong style="font-size:1.2rem; color:#0ea5e9;">{r_word}</strong>
                    <span style="opacity:0.6; margin-left:8px;">({r_type})</span><br>
                    <span style="font-weight:600; margin-top:4px; display:block;">{r_meaning}</span>
                    {f'<i style="opacity:0.8; margin-top:6px; display:block;">"{r_example}"</i>' if r_example else ''}
                </div>
                """, unsafe_allow_html=True)
                
                col_btn1, col_btn2 = st.columns([1, 4])
                if col_btn1.button("🔄", key=f"v_toggle_{r_id}", help="تغيير الحالة"):
                    new_st = "Learned" if r_status == "Needs Review" else "Needs Review"
                    try:
                        with sqlite3.connect(DB_PATH, timeout=15) as conn:
                            c = conn.cursor()
                            c.execute("UPDATE vocab_notebook SET status = ? WHERE id = ?", 
                                     (new_st, r_id))
                            conn.commit()
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ خطأ: {e}")
                
                status_text = "✅ محفوظة" if r_status == "Learned" else "⏳ قيد المراجعة"
                col_btn2.markdown(f"<div style='margin-top:6px;'>{status_text}</div>", 
                                 unsafe_allow_html=True)
        else:
            st.info("لم تقم بحفظ أي كلمات بعد")
    except Exception as e:
        st.error(f"❌ خطأ في عرض المفردات: {e}")

# ------------------------------------------
# التبويب 1: المحادثة (Main Chat)
# ------------------------------------------
with tab_chat:
    # ✅ إصلاح 4: التحقق من API Key قبل بدء المحادثة
    if not api_key or not api_key.strip():
        st.warning("👈 يرجى إدخال Gemini API Key في الشريط الجانبي")
        st.stop()

    mem_name = get_profile("name", "الطالب")
    mem_level = get_profile("level", "B1")
    mem_goals = get_profile("goals", "محادثة عامة")
    mem_notes = get_profile("notes", "")

    SYSTEM_PROMPT = f"""
You are an elite English conversation partner.
User: {mem_name} | Level: {mem_level} | Goals: {mem_goals}
Special Notes: {mem_notes}
Correction Mode: {strictness}

Scenario: {PROMPTS.get(scenario, PROMPTS['Casual Friend (Everyday Chat)'])}

IMPORTANT:
1. Tailor language to {mem_level}
2. Follow strictness: {strictness}
3. End with: [EVAL|Grammar:X/10|Vocab:X/10|Natural:X/10|Fluency:X/10|Correction: brief tip]
"""

    def sync_gemini_history(client_instance, messages):
        """Sync messages with Gemini"""
        try:
            history_parts = []
            for m in messages:
                role = "user" if m["role"] == "user" else "model"
                history_parts.append(
                    types.Content(role=role, parts=[types.Part.from_text(text=m["content"])])
                )
            st.session_state.chat_session = client_instance.chats.create(
                model=model_name,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.7
                ),
                history=history_parts
            )
        except Exception as e:
            st.error(f"❌ خطأ في مزامنة المحادثة: {e}")
            raise

    try:
        client = genai.Client(api_key=api_key)
        config_signature = (scenario, model_name, strictness, mem_name, mem_level)
        
        if "chat_session" not in st.session_state or st.session_state.get("current_config") != config_signature:
            st.session_state.messages = []
            sync_gemini_history(client, [])
            st.session_state.current_config = config_signature
            st.session_state.test_question_count = 0
            st.session_state.last_audio_id = None

            # Welcome message for placement test
            if scenario == "Speaking Placement Test (10+ Questions)":
                welcome_msg = f"Welcome {mem_name}! Let's begin the placement test. Question 1: Please introduce yourself and tell me about your daily routine."
                audio_path = speak(welcome_msg, voice_id)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": welcome_msg,
                    "audio": audio_path
                })
                sync_gemini_history(client, st.session_state.messages)
                update_stat("total_messages", 1)
    except Exception as e:
        st.error(f"❌ خطأ في الاتصال: {e}")
        st.stop()

    st.markdown(f"""
        <div class="hero-card">
            <div class="hero-title">مرحباً {mem_name or 'بك'}! 👋</div>
            <div class="hero-sub">{mem_level} • {mem_goals}</div>
            <div>
                <span class="badge">{SCENARIO_ICONS.get(scenario)} {scenario.split('(')[0]}</span>
                <span class="badge" style="background-color:rgba(139, 92, 246, 0.1); color:#8b5cf6; border-color:rgba(139, 92, 246, 0.2);">🔊 {voice_label.split('—')[0]}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if scenario == "Speaking Placement Test (10+ Questions)":
        answered = st.session_state.get("test_question_count", 0)
        st.progress(min(answered / 10, 1.0), text=f"السؤال {answered} من 10+")

    # Display messages
    if st.session_state.messages:
        for i, msg in enumerate(st.session_state.messages):
            with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "🧑"):
                if msg.get("eval"):
                    ev = msg["eval"]
                    st.markdown(f"""
                    <div class="eval-card">
                        <div class="eval-scores">
                            <span class="eval-score-item">Grammar: {ev.get('Grammar','-')}</span>
                            <span class="eval-score-item">Vocab: {ev.get('Vocab','-')}</span>
                            <span class="eval-score-item">Natural: {ev.get('Natural','-')}</span>
                            <span class="eval-score-item">Fluency: {ev.get('Fluency','-')}</span>
                        </div>
                        <div style="margin-top:8px;"><b>التصحيح:</b> {ev.get('Correction','')}</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.write(msg["content"])
                
                audio_path = msg.get("audio")
                if audio_path:
                    render_voice_player(audio_path, autoplay_audio)

                if st.button("🗑️", key=f"del_{i}", help="حذف"):
                    st.session_state.messages.pop(i)
                    sync_gemini_history(client, st.session_state.messages)
                    st.rerun()
    else:
        st.info("💬 ابدأ المحادثة أدناه!")

    st.markdown("<hr>", unsafe_allow_html=True)

    # ✅ إصلاح 5: معالجة الإدخال الصوتي والنصي بشكل أفضل
    col_audio, col_text = st.columns([1, 2]) if not voice_only_mode else (st.columns([1, 0])[0], None)
    
    with col_audio:
        audio_value = st.audio_input("🎤 سجل صوتياً:")
    
    typed = None
    if col_text and not voice_only_mode:
        with col_text:
            typed = st.chat_input("📝 أو اكتب رسالتك...")

    user_input_text = None

    # ✅ إصلاح 6: معالجة الصوت مع تجنب المشاكل
    if audio_value is not None and len(audio_value.getvalue()) > 0:
        audio_bytes = audio_value.getvalue()
        audio_id = hashlib.sha256(audio_bytes).hexdigest()
        
        if st.session_state.get("last_audio_id") != audio_id:
            st.session_state.last_audio_id = audio_id
            
            with st.spinner("🎧 جاري التعرف على الصوت..."):
                try:
                    transcript = client.models.generate_content(
                        model=model_name,
                        contents=[
                            types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav"),
                            "Transcribe exactly what is said. Output ONLY the transcription."
                        ],
                    )
                    user_input_text = transcript.text.strip() if transcript.text else None
                except Exception as e:
                    st.error(f"❌ خطأ في التعرف: {e}")
    
    elif typed:
        user_input_text = typed

    # Send message
    if user_input_text:
        st.session_state.messages.append({"role": "user", "content": user_input_text})
        update_stat("total_messages", 1)
        update_stat("total_words", len(user_input_text.split()))

        if scenario == "Speaking Placement Test (10+ Questions)":
            st.session_state.test_question_count += 1

        with st.chat_message("user", avatar="🧑"):
            st.write(user_input_text)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("المعلم يرد..."):
                try:
                    response = st.session_state.chat_session.send_message(user_input_text)
                    full_reply = response.text
                except Exception as e:
                    st.error(f"❌ خطأ: {e}")
                    st.session_state.messages.pop()
                    st.stop()

            # Parse evaluation
            eval_data = None
            display_reply = full_reply
            eval_match = re.search(r"\[EVAL\s*\|(.*?)\]", full_reply, re.DOTALL | re.IGNORECASE)
            
            if eval_match:
                eval_str = eval_match.group(1).replace('\n', '')
                display_reply = full_reply.replace(eval_match.group(0), "").strip()
                
                for item in eval_str.split("|"):
                    if ":" in item:
                        if eval_data is None:
                            eval_data = {}
                        k, v = item.split(":", 1)
                        eval_data[k.strip()] = v.strip()

            # Display evaluation
            if eval_data:
                st.markdown(f"""
                <div class="eval-card">
                    <div class="eval-scores">
                        <span class="eval-score-item">Grammar: {eval_data.get('Grammar','-')}</span>
                        <span class="eval-score-item">Vocab: {eval_data.get('Vocab','-')}</span>
                        <span class="eval-score-item">Natural: {eval_data.get('Natural','-')}</span>
                        <span class="eval-score-item">Fluency: {eval_data.get('Fluency','-')}</span>
                    </div>
                    <div style="margin-top:8px;"><b>التصحيح:</b> {eval_data.get('Correction','')}</div>
                </div>
                """, unsafe_allow_html=True)

            st.write(display_reply)

            # Generate speech
            audio_path = None
            try:
                audio_path = speak(display_reply, voice_id)
                if audio_path:
                    render_voice_player(audio_path, autoplay_audio)
            except Exception as e:
                st.warning(f"⚠️ خطأ في توليد الصوت: {e}")

            # Save assistant message
            st.session_state.messages.append({
                "role": "assistant",
                "content": display_reply,
                "audio": audio_path,
                "eval": eval_data
            })
            update_stat("total_messages", 1)
            update_stat("total_words", len(display_reply.split()))
