# ==========================================
# AI English Conversation Partner — v13 (Ultimate Stable & UI Enforced)
# الميزات:
# 1) AI Memory & Profile
# 2) Vocabulary Notebook
# 3) Real-time Evaluation
# 4) Voice-Only Call Mode
# 5) Granular Settings
# تم الإصلاح الشامل لمشاكل دورة حياة Streamlit، وتصحيح انهيار ذاكرة Gemini، وفرض تنسيق الواجهة.
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
from string import Template

import streamlit as st
import streamlit.components.v1 as components
import edge_tts
from google import genai
from google.genai import types

# ==========================================
# 0. إعداد قاعدة البيانات المحلية (SQLite)
# ==========================================
DB_DIR = os.path.join(tempfile.gettempdir(), "ai_english_elite")
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "elite_partner.db")

# تم التعديل: إضافة timeout=10 لمنع خطأ Database is locked عند العمل على مسارات Streamlit المتعددة
def init_db():
    try:
        with sqlite3.connect(DB_PATH, timeout=10) as conn:
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
        print(f"Database Initialization Error: {e}")

init_db()

def set_profile(key: str, val: str):
    try:
        with sqlite3.connect(DB_PATH, timeout=10) as conn:
            c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO user_profile (key, value) VALUES (?, ?)", (key, val))
            conn.commit()
    except Exception as e:
        print(f"DB Error (set_profile): {e}")

def get_profile(key: str, default: str = "") -> str:
    try:
        with sqlite3.connect(DB_PATH, timeout=10) as conn:
            c = conn.cursor()
            c.execute("SELECT value FROM user_profile WHERE key = ?", (key,))
            row = c.fetchone()
            return row[0] if row else default
    except Exception as e:
        print(f"DB Error (get_profile): {e}")
        return default

def update_stat(key: str, amount: int = 1):
    try:
        with sqlite3.connect(DB_PATH, timeout=10) as conn:
            c = conn.cursor()
            c.execute("INSERT OR IGNORE INTO user_stats (key, value) VALUES (?, 0)", (key,))
            c.execute("UPDATE user_stats SET value = value + ? WHERE key = ?", (amount, key))
            conn.commit()
    except Exception as e:
        print(f"DB Error (update_stat): {e}")

def get_stat(key: str) -> int:
    try:
        with sqlite3.connect(DB_PATH, timeout=10) as conn:
            c = conn.cursor()
            c.execute("SELECT value FROM user_stats WHERE key = ?", (key,))
            row = c.fetchone()
            return row[0] if row else 0
    except Exception as e:
        print(f"DB Error (get_stat): {e}")
        return 0

if "session_audio_dir" not in st.session_state:
    st.session_state.session_audio_dir = os.path.join(DB_DIR, uuid.uuid4().hex)
    os.makedirs(st.session_state.session_audio_dir, exist_ok=True)

AUDIO_DIR = st.session_state.session_audio_dir

# ==========================================
# 1. إعدادات الصفحة والتصميم (UI & CSS)
# ==========================================
st.set_page_config(page_title="Elite English Partner", page_icon="🎓", layout="wide")

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
        "topics (hobbies, food, daily life, movies, weekend plans, etc.). Keep the tone relaxed "
        "and friendly, ask natural follow-up questions, and let the conversation flow the way "
        "real friends talk."
    ),
    "Supermarket Customer (Work Practice)": (
        "Roleplay as a customer at a supermarket while the user practices being the cashier or "
        "employee. Ask about prices, product locations, and availability, and make small talk "
        "typical of a supermarket checkout interaction. Occasionally raise realistic situations "
        "(a discount code, a missing item, asking for a bag) for the user to handle."
    ),
    "Grammar & Translation Coach": (
        "Act as a supportive but precise grammar and Arabic-English translation coach. Help the "
        "user translate sentences accurately, explain grammar rules clearly with examples, and "
        "correct mistakes with a brief explanation of the rule behind each correction."
    ),
    "Speaking Placement Test (10+ Questions)": (
        "Conduct a structured spoken English placement test. Ask at least 10-15 questions of "
        "gradually increasing difficulty, covering different tenses and topics, to assess the "
        "user's CEFR level. Keep questions short and clear, one at a time. After the test is "
        "complete, give an estimated CEFR level (A1-C2) with a short justification."
    ),
}

# تم التعديل: فرض التنسيقات باستخدام data-testid واستهداف الجذور لإجبار Streamlit على التغيير البصري.
st.markdown(
    """
    <style>
        /* إخفاء الزوائد الافتراضية لستريم ليت لتنظيف الواجهة */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* فرض ألوان وتنسيقات لحاويات المحادثة (الفقاعات) */
        div[data-testid="stChatMessage"] {
            background-color: var(--secondary-background-color) !important;
            border-radius: 16px !important;
            padding: 1.5rem !important;
            margin-bottom: 1rem !important;
            border: 1px solid rgba(14, 165, 233, 0.2) !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.02) !important;
        }

        /* فرض تأثيرات حركية على جميع الأزرار */
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
        
        /* تجميل حقول الإدخال */
        div[data-baseweb="input"] > div, div[data-baseweb="textarea"] > div {
            border-radius: 10px !important;
        }
        
        /* البطاقة الترحيبية */
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
        
        /* البادجات (العلامات) */
        .badge {
            display: inline-flex; align-items: center; gap: 6px;
            padding: 6px 14px; border-radius: 10px; font-size: 0.85rem; font-weight: 600;
            background-color: rgba(14, 165, 233, 0.15); 
            color: #0ea5e9; 
            border: 1px solid rgba(14, 165, 233, 0.3);
        }
        
        /* بطاقة التقييم */
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
        
        /* العناوين الجانبية */
        .side-heading {
            font-size: 0.85rem; font-weight: 700; text-transform: uppercase;
            opacity: 0.7; margin: 24px 0 10px 0;
            border-bottom: 2px solid rgba(128, 128, 128, 0.1);
            padding-bottom: 6px;
        }
        
        /* صفوف المفردات */
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
# 2. الشريط الجانبي: الإعدادات والتحكم
# ==========================================
st.sidebar.title("🎓 Elite English")
st.sidebar.caption("بيئة تعليمية هادئة وذكية")

with st.sidebar.expander("🔑 إعدادات API (اضغط للفتح)", expanded=not bool(os.environ.get("GEMINI_API_KEY"))):
    env_key = os.environ.get("GEMINI_API_KEY", "")
    use_different_key = False
    if env_key:
        st.success("مفتاح النظام مفعل.")
        use_different_key = st.checkbox("إدخال مفتاح مختلف")

    if env_key and not use_different_key:
        api_key = env_key
    else:
        api_key = st.text_input("Gemini API Key:", type="password")
        
    model_name = st.text_input("Gemini Model:", value=DEFAULT_MODEL)

st.sidebar.markdown('<div class="side-heading">💬 بيئة المحادثة</div>', unsafe_allow_html=True)
scenario = st.sidebar.selectbox(
    "اختر السيناريو (Scenario):",
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
    ["تصحيح جميع الأخطاء بدقة", "الأخطاء الكبيرة فقط (لتشجيع الطلاقة)", "بدون تصحيح (محادثة حرة تماماً)"],
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
voice_only_mode = st.sidebar.toggle("🎙️ وضع المكالمة الصوتية", value=False, help="يخفي لوحة المفاتيح لتعتمد كلياً على التحدث بالمايكرفون.")

st.sidebar.markdown('<div class="side-heading">⚙️ خيارات الجلسة</div>', unsafe_allow_html=True)
if st.sidebar.button("🔄 بدء جلسة جديدة", use_container_width=True):
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()

# ==========================================
# 3. محول الصوتيات (Edge TTS) ومشغل Waveform
# ==========================================
# تم التعديل: عزل تام لمنطق الـ Asyncio داخل خيط (Thread) منفصل لضمان عدم تعليق الواجهة أبداً تحت أي ظرف.
def speak(text: str, voice: str) -> str:
    out_path = os.path.join(AUDIO_DIR, f"tts_{int(time.time() * 1000)}.mp3")
    def run_async():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        communicate = edge_tts.Communicate(text, voice)
        loop.run_until_complete(communicate.save(out_path))
        loop.close()
    
    t = threading.Thread(target=run_async)
    t.start()
    t.join()
    return out_path

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
  .vp-wave { position: relative; width: ${wave_width}px; height: 26px; cursor: pointer; }
  .vp-bars-bg, .vp-bars-fixed { position: absolute; top: 0; left: 0; width: ${wave_width}px; height: 100%; display: flex; align-items: center; gap: 3px; }
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
    with open(audio_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    heights = _wave_bar_heights(os.path.basename(audio_path))
    bars_html = "".join(f'<span style="height:{h}px"></span>' for h in heights)
    html = _VOICE_PLAYER_TEMPLATE.substitute(wave_width=220, bars=bars_html, autoplay_attr="autoplay" if autoplay else "", b64=b64)
    components.html(html, height=55, scrolling=False)

# ==========================================
# 4. بناء تبويبات المنصة الاحترافية (Tabs)
# ==========================================
tab_chat, tab_vocab, tab_profile = st.tabs([
    "💬 قاعة المحادثة", 
    "📓 دفتر المفردات (Vocab)", 
    "🧠 الملف الشخصي والإحصائيات"
])

# ------------------------------------------
# التبويب 3: الملف الشخصي والإحصائيات
# ------------------------------------------
with tab_profile:
    st.subheader("الملف الشخصي وذاكرة الذكاء الاصطناعي")
    st.caption("يستخدم الذكاء الاصطناعي هذه المعلومات لتخصيص الحوار وتوجيهه لمستواك وأهدافك.")

    col_prof1, col_prof2 = st.columns([2, 1])
    
    with col_prof1:
        with st.form("profile_form"):
            p_name = st.text_input("اسمك الكريم:", value=get_profile("name", ""))
            level_options = ["A1 (مبتدئ)", "A2 (مبتدئ متقدم)", "B1 (متوسط)", "B2 (متوسط متقدم)", "C1 (متقدم)", "C2 (محترف)"]
            saved_level = get_profile("level", "B1 (متوسط)")
            p_level = st.selectbox(
                "مستواك في الإنجليزية:",
                level_options,
                index=level_options.index(saved_level) if saved_level in level_options else 2,
            )
            p_goals = st.text_input("هدف التعلم (مثال: التحضير لـ IELTS، العمل، محادثة عامة):", value=get_profile("goals", ""))
            p_notes = st.text_area("ملاحظات خاصة لمعلمك الذكي (مثال: التركيز على نطق الكلمات، القواعد...):", value=get_profile("notes", ""))
            
            if st.form_submit_button("💾 حفظ البيانات وتحديث الذاكرة"):
                set_profile("name", p_name)
                set_profile("level", p_level)
                set_profile("goals", p_goals)
                set_profile("notes", p_notes)
                st.success("✅ تم تحديث بياناتك بنجاح! سيتم تطبيقها في المحادثة القادمة.")
    
    with col_prof2:
        st.markdown("### 📊 إحصائيات الأداء")
        st.info(f"**💬 إجمالي الرسائل:** {get_stat('total_messages')}")
        st.info(f"**📓 كلمات الدفتر المحفوظة:** {get_stat('total_vocab_saved')}")
        st.info(f"**📚 كلمات متفاعل معها:** {get_stat('total_words')}")

# ------------------------------------------
# التبويب 2: دفتر المفردات (Vocabulary Notebook)
# ------------------------------------------
with tab_vocab:
    st.subheader("دفتر المفردات الذكي")
    
    with st.expander("➕ إضافة كلمة جديدة يدوياً"):
        with st.form("add_vocab"):
            col_v1, col_v2 = st.columns(2)
            new_word = col_v1.text_input("الكلمة أو التعبير (English):")
            new_type = col_v2.selectbox("التصنيف:", ["Verb (فعل)", "Noun (اسم)", "Phrase (تعبير)", "Adjective (صفة)", "Other"])
            new_meaning = st.text_input("المعنى بالعربية:")
            new_example = st.text_input("مثال إنجليزي (اختياري):")
            if st.form_submit_button("حفظ الكلمة"):
                if new_word:
                    try:
                        with sqlite3.connect(DB_PATH, timeout=10) as conn:
                            c = conn.cursor()
                            c.execute("INSERT OR REPLACE INTO vocab_notebook (word, word_type, meaning_ar, example, status) VALUES (?, ?, ?, ?, ?)",
                                      (new_word.strip(), new_type, new_meaning.strip(), new_example.strip(), "Needs Review"))
                            conn.commit()
                        st.success(f"تم الحفظ: {new_word}")
                        update_stat("total_vocab_saved", 1)
                    except Exception as e:
                        st.error(f"حدث خطأ: {e}")
                else:
                    st.warning("يرجى كتابة الكلمة أولاً.")

    try:
        with sqlite3.connect(DB_PATH, timeout=10) as conn:
            c = conn.cursor()
            c.execute("SELECT id, word, word_type, meaning_ar, example, status FROM vocab_notebook ORDER BY id DESC")
            vocab_rows = c.fetchall()

        if vocab_rows:
            search_q = st.text_input("🔍 ابحث في مفرداتك...", "")
            filtered = [r for r in vocab_rows if search_q.lower() in r[1].lower() or search_q in r[3]]
            
            st.caption(f"عدد الكلمات المحفوظة: {len(vocab_rows)}")
            
            for row in filtered:
                r_id, r_word, r_type, r_meaning, r_example, r_status = row
                st.markdown(f"""
                <div class="vocab-row">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <strong style="font-size:1.25rem; color:#0ea5e9;">{r_word}</strong> 
                            <span style="opacity:0.6; font-size:0.9rem; margin-left:6px;">({r_type})</span><br>
                            <span style="font-weight:600; font-size:1.05rem;">{r_meaning}</span>
                            {f'<br><i style="opacity:0.8; font-size:0.95rem; margin-top:6px; display:inline-block;">"{r_example}"</i>' if r_example else ''}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                status_color = "🟢 محفوظة (Learned)" if r_status == "Learned" else "🟠 تحتاج مراجعة"
                col_btn1, col_btn2 = st.columns([1, 4])
                if col_btn1.button("تغيير الحالة", key=f"v_toggle_{r_id}", help="التبديل بين محفوظة وتحتاج مراجعة"):
                    new_st = "Learned" if r_status == "Needs Review" else "Needs Review"
                    with sqlite3.connect(DB_PATH, timeout=10) as conn:
                        c = conn.cursor()
                        c.execute("UPDATE vocab_notebook SET status = ? WHERE id = ?", (new_st, r_id))
                        conn.commit()
                    st.rerun()
                col_btn2.markdown(f"<div style='margin-top:6px; font-size:0.95rem; font-weight:600;'>الحالة: {status_color}</div>", unsafe_allow_html=True)
        else:
            st.info("لم تقم بإضافة أي كلمات بعد.")
    except Exception as e:
        st.error(f"خطأ في عرض المفردات: {e}")

# ------------------------------------------
# التبويب 1: غرفة المحادثة الذكية (Main Chat Room)
# ------------------------------------------
with tab_chat:
    mem_name = get_profile("name", "الطالب")
    mem_level = get_profile("level", "B1")
    mem_goals = get_profile("goals", "محادثة عامة وتحسين الطلاقة")
    mem_notes = get_profile("notes", "")

    SYSTEM_PROMPT = f"""
    You are an elite English conversation partner and coach.
    User Profile:
    - Name: {mem_name}
    - CEFR Level: {mem_level}
    - Goals: {mem_goals}
    - Notes/Weaknesses: {mem_notes}
    - Correction Strictness: {strictness}

    Scenario Instruction: {PROMPTS.get(scenario, PROMPTS['Casual Friend (Everyday Chat)'])}
    
    IMPORTANT RULES:
    1. Tailor your language difficulty to the user's level ({mem_level}).
    2. Respect the correction strictness: {strictness}.
    3. At the end of every response, you MUST provide a short evaluation block for the user's previous message in this exact format:
       [EVAL|Grammar:X/10|Vocab:X/10|Natural:X/10|Fluency:X/10|Correction: short polite tip if any]
    """

    if not api_key:
        st.warning("👈 يرجى إدخال مفتاح Gemini API Key في الشريط الجانبي لبدء المحادثة.")
        st.stop()

    # تم التعديل: دالة مساعدة لضمان مزامنة محادثات الواجهة مع تاريخ محادثة Gemini في حال تم حذف رسالة (لمنع خطأ 400 Bad Request).
    def sync_gemini_history(client_instance):
        history_parts = []
        for m in st.session_state.messages:
            # Gemini expects 'user' or 'model' roles explicitly in history.
            role = "user" if m["role"] == "user" else "model" 
            history_parts.append(
                types.Content(role=role, parts=[types.Part.from_text(text=m["content"])])
            )
        st.session_state.chat_session = client_instance.chats.create(
            model=model_name,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT, temperature=0.7),
            history=history_parts
        )

    try:
        client = genai.Client(api_key=api_key)
        config_signature = (scenario, model_name, strictness, mem_name, mem_level, mem_goals, mem_notes)
        if "chat_session" not in st.session_state or st.session_state.get("current_config") != config_signature:
            st.session_state.messages = []
            sync_gemini_history(client)
            st.session_state.current_config = config_signature
            st.session_state.test_question_count = 0
            st.session_state.last_played_audio = None
            st.session_state.audio_input_key = 0

            if scenario == "Speaking Placement Test (10+ Questions)":
                welcome_msg = f"Welcome {mem_name} to the English Speaking Placement Test. Let's begin! Question 1: Could you introduce yourself and tell me a bit about your daily routine?"
                st.session_state.messages.append({"role": "assistant", "content": welcome_msg, "audio": speak(welcome_msg, voice_id)})
                sync_gemini_history(client)
                update_stat("total_messages", 1)
    except Exception as e:
        st.error(f"⚠️ خطأ في الاتصال بالخادم (تأكد من صحة المفتاح أو الاتصال): `{e}`")
        st.stop()

    st.markdown(f"""
        <div class="hero-card">
            <div class="hero-title">أهلاً بك، {mem_name or 'صديقي'}!</div>
            <div class="hero-sub">المستوى: {mem_level} | الهدف: {mem_goals}</div>
            <div>
                <span class="badge">{SCENARIO_ICONS.get(scenario, '💬')} {scenario.split(' (')[0]}</span>
                <span class="badge" style="background-color:rgba(139, 92, 246, 0.1); color:#8b5cf6; border-color:rgba(139, 92, 246, 0.2);">🔊 {voice_label.split(' — ')[0]}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if scenario == "Speaking Placement Test (10+ Questions)":
        answered = st.session_state.get("test_question_count", 0)
        pct = min(answered / 10, 1.0)
        st.progress(pct, text=f"📝 الأسئلة المجابة: {answered} من أصل 10+")

    # تم التعديل: إيقاف عملية st.rerun() الخاطئة التي كانت تسبب اختفاء المحتوى وتمزيق الواجهة عند إرسال رسالة.
    # الآن يتم استرجاع وعرض الرسائل السابقة أولاً لتسلسل سليم.
    messages = st.session_state.messages
    if not messages:
        st.info("ابدأ التحدث بالأسفل لبدء المحادثة الصوتية أو النصية!")

    last_index = len(messages) - 1
    for i, msg in enumerate(messages):
        avatar = "🤖" if msg["role"] == "assistant" else "🧑"
        with st.chat_message(msg["role"], avatar=avatar):
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
                        <div style="margin-top:8px; font-weight:600; opacity:0.9;"><b>التصحيح:</b> {ev.get('Correction','عمل ممتاز!')}</div>
                    </div>
                """, unsafe_allow_html=True)

            st.write(msg["content"])
            
            audio_path = msg.get("audio")
            if audio_path and os.path.exists(audio_path):
                is_fresh = (i == last_index) and (audio_path != st.session_state.get("last_played_audio"))
                render_voice_player(audio_path, autoplay_audio and is_fresh)
                if is_fresh:
                    st.session_state.last_played_audio = audio_path

            if st.button("🗑️", key=f"del_{i}", help="حذف هذه الرسالة"):
                # تم التعديل: عند الحذف، نحذف الرسالة ونقوم بمزامنة الذاكرة مع Gemini لمنع انهيار API.
                st.session_state.messages.pop(i)
                sync_gemini_history(client)
                st.rerun()

    st.markdown("<br><hr style='opacity:0.2;'>", unsafe_allow_html=True)
    
    if voice_only_mode:
        st.success("🎙️ وضع المكالمة الصوتية مفعل. يمكنك استخدام زر المايكرفون للتحدث بشكل مباشر.")

    if "audio_input_key" not in st.session_state:
        st.session_state.audio_input_key = 0

    audio_value = st.audio_input("سجل رسالتك الصوتية:", key=f"audio_recorder_{st.session_state.audio_input_key}")
    typed = None if voice_only_mode else st.chat_input("أو اكتب رسالتك النصية هنا...")

    # تم التعديل: جمع عمليات الإدخال لمنع التداخل والتعامل مع الإرسال بأسلوب Streamlit الصحيح والسلس
    user_input_text = None

    if audio_value is not None:
        audio_bytes = audio_value.getvalue()
        audio_id = hashlib.sha256(audio_bytes).hexdigest()
        if st.session_state.get("last_audio_id") != audio_id:
            st.session_state.last_audio_id = audio_id
            with st.spinner("🎧 جاري معالجة الصوت..."):
                try:
                    transcript = client.models.generate_content(
                        model=model_name,
                        contents=[types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav"), "Transcribe exactly what is said in this audio. Output ONLY the transcription."],
                    )
                    user_input_text = transcript.text.strip()
                except Exception as e:
                    st.error(f"⚠️ حدث خطأ في التعرف على الصوت: {e}")
            st.session_state.audio_input_key += 1
    elif typed:
        user_input_text = typed

    # معالجة الإدخال الحي ورسم الرسالة فوراً دون استدعاء st.rerun() المسبب للوميض
    if user_input_text:
        st.session_state.messages.append({"role": "user", "content": user_input_text})
        update_stat("total_messages", 1)
        update_stat("total_words", len(user_input_text.split()))

        if scenario == "Speaking Placement Test (10+ Questions)":
            st.session_state.test_question_count = st.session_state.get("test_question_count", 0) + 1

        with st.chat_message("user", avatar="🧑"):
            st.write(user_input_text)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("المعلم يكتب الرد..."):
                try:
                    response = st.session_state.chat_session.send_message(user_input_text)
                    full_reply = response.text
                except Exception as e:
                    st.error(f"⚠️ تعذر الحصول على رد من الذكاء الاصطناعي: {e}")
                    st.session_state.messages.pop() # التراجع عن رسالة المستخدم في حال فشل الرد
                    st.stop()

            eval_data = None
            display_reply = full_reply
            eval_match = re.search(r"\[EVAL\s*\|(.*?)\]", full_reply, re.DOTALL | re.IGNORECASE)
            if eval_match:
                eval_str = eval_match.group(1).replace('\n', '')
                display_reply = full_reply.replace(eval_match.group(0), "").strip()
                eval_parts = {}
                for item in eval_str.split("|"):
                    if ":" in item:
                        k, v = item.split(":", 1)
                        eval_parts[k.strip()] = v.strip()
                eval_data = eval_parts

            if eval_data:
                st.markdown(f"""
                    <div class="eval-card">
                        <div class="eval-scores">
                            <span class="eval-score-item">Grammar: {eval_data.get('Grammar','-')}</span>
                            <span class="eval-score-item">Vocab: {eval_data.get('Vocab','-')}</span>
                            <span class="eval-score-item">Natural: {eval_data.get('Natural','-')}</span>
                            <span class="eval-score-item">Fluency: {eval_data.get('Fluency','-')}</span>
                        </div>
                        <div style="margin-top:8px; font-weight:600; opacity:0.9;"><b>التصحيح:</b> {eval_data.get('Correction','لا يوجد ملاحظات، عمل ممتاز!')}</div>
                    </div>
                """, unsafe_allow_html=True)

            st.write(display_reply)

            audio_path = None
            try:
                audio_path = speak(display_reply, voice_id)
                render_voice_player(audio_path, autoplay_audio)
                st.session_state.last_played_audio = audio_path
            except Exception as e:
                print(f"TTS Error: {e}")

        # حفظ رد המعلم في الذاكرة المحلية
        st.session_state.messages.append({
            "role": "assistant", 
            "content": display_reply, 
            "audio": audio_path, 
            "eval": eval_data
        })
        update_stat("total_messages", 1)
        update_stat("total_words", len(display_reply.split()))
