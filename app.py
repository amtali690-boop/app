# ==========================================
# AI English Conversation Partner — v9 (Elite Language Platform)
# الميزات الجديدة كلياً:
# 1) AI Memory & Profile: حفظ ذاكرة المستخدم والاسم والمستوى والأهداف وتكييف ردود AI بناءً عليها.
# 2) Vocabulary Notebook: دفتر مفردات تفاعلي لتصنيف الكلمات وتتبع حالة حفظها (مراجعة/محفوظة).
# 3) Real-time Evaluation: تقييم فورية لكل رسالة (Grammar, Vocab, Naturalness, Fluency) مع تصحيح مختصر.
# 4) Voice-Only Call Mode: واجهة مخصصة لمحاكاة المكالمات الصوتية الحقيقية بسلاسة.
# 5) Granular Settings: إعدادات دقيقة لصرامة التصحيح وأسلوب الحوار حسب رغبتك.
# ==========================================

import os
import re
import time
import uuid
import shutil
import hashlib
import tempfile
import asyncio
import base64
import random
import sqlite3
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

def init_db():
    conn = sqlite3.connect(DB_PATH)
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
    conn.close()

init_db()

def set_profile(key: str, val: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO user_profile (key, value) VALUES (?, ?)", (key, val))
        conn.commit()
        conn.close()
    except Exception:
        pass

def get_profile(key: str, default: str = "") -> str:
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT value FROM user_profile WHERE key = ?", (key,))
        row = c.fetchone()
        conn.close()
        return row[0] if row else default
    except Exception:
        return default

def update_stat(key: str, amount: int = 1):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO user_stats (key, value) VALUES (?, 0)", (key,))
        c.execute("UPDATE user_stats SET value = value + ? WHERE key = ?", (amount, key))
        conn.commit()
        conn.close()
    except Exception:
        pass

def get_stat(key: str) -> int:
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT value FROM user_stats WHERE key = ?", (key,))
        row = c.fetchone()
        conn.close()
        return row[0] if row else 0
    except Exception:
        return 0

# مجلد صوتي مستقل لكل جلسة
if "session_audio_dir" not in st.session_state:
    st.session_state.session_audio_dir = os.path.join(DB_DIR, uuid.uuid4().hex)
    os.makedirs(st.session_state.session_audio_dir, exist_ok=True)

AUDIO_DIR = st.session_state.session_audio_dir

# ==========================================
# 1. إعدادات الصفحة والتصميم (UI & CSS)
# ==========================================
st.set_page_config(page_title="AI English Elite Platform", page_icon="🎙️", layout="wide")

DEFAULT_MODEL = "gemini-flash-latest"

SCENARIO_ICONS = {
    "Casual Friend (Everyday Chat)": "☕",
    "Supermarket Customer (Work Practice)": "🛒",
    "Grammar & Translation Coach": "📘",
    "Speaking Placement Test (10+ Questions)": "📝",
}

# تعليمات كل سيناريو تُرسل للذكاء الاصطناعي ضمن الـ System Prompt
# (كانت هذه القائمة مفقودة بالكامل من الكود الأصلي، وهذا كان سبب توقف التطبيق عن العمل)
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

st.markdown(
    """
    <style>
        .stApp {
            background: radial-gradient(circle at top left, #0f172a 0%, #090d16 55%, #030712 100%);
        }
        .hero-card {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 60%, #090d16 100%);
            border: 1px solid rgba(56, 189, 248, 0.2);
            border-radius: 18px; padding: 20px 26px; margin-bottom: 16px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.4);
        }
        .hero-title { font-size: 1.7rem; font-weight: 800; color: #f8fafc; margin-bottom: 4px; }
        .hero-sub { color: #94a3b8; font-size: 0.92rem; margin-bottom: 12px; }
        .badge {
            display: inline-flex; align-items: center; gap: 6px;
            padding: 5px 12px; border-radius: 999px; font-size: 0.8rem; font-weight: 600;
            background: rgba(56, 189, 248, 0.12); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3);
        }
        .eval-card {
            background: rgba(15, 23, 42, 0.7);
            border: 1px solid rgba(167, 139, 250, 0.25);
            border-radius: 12px; padding: 10px 14px; margin-bottom: 8px;
            font-size: 0.82rem; color: #cbd5e1;
        }
        .eval-scores { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 4px; font-weight: 700; color: #38bdf8; }
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #090d16 0%, #030712 100%);
            border-right: 1px solid rgba(148,163,184,0.1);
        }
        .side-heading {
            font-size: 0.78rem; letter-spacing: 0.08em; text-transform: uppercase;
            color: #64748b; font-weight: 700; margin: 16px 0 6px 0;
        }
        .stButton>button, .stDownloadButton>button { border-radius: 10px; font-weight: 700; }
        .typing-card {
            display: inline-flex; align-items: center; gap: 10px;
            background: rgba(255,255,255,0.04); border: 1px solid rgba(148,163,184,0.12);
            border-radius: 14px; padding: 10px 16px; color: #94a3b8; font-size: 0.88rem; font-weight: 600;
        }
        .typing-dots { display: inline-flex; gap: 4px; }
        .typing-dots span {
            width: 6px; height: 6px; border-radius: 50%;
            background: linear-gradient(135deg, #38bdf8, #a78bfa);
            animation: typing-bounce 1.2s infinite ease-in-out;
        }
        .typing-dots span:nth-child(2) { animation-delay: 0.15s; }
        .typing-dots span:nth-child(3) { animation-delay: 0.3s; }
        @keyframes typing-bounce {
            0%, 60%, 100% { transform: translateY(0); opacity: 0.5; }
            30% { transform: translateY(-5px); opacity: 1; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================================
# 2. الشريط الجانبي: الإعدادات والتحكم
# ==========================================
st.sidebar.markdown("### 🎙️ AI English Elite")
st.sidebar.caption("منصة تدريب لغات متطورة مع ذاكرة ذكية")

st.sidebar.markdown('<div class="side-heading">🔑 API & Setup</div>', unsafe_allow_html=True)
env_key = os.environ.get("GEMINI_API_KEY", "")
use_different_key = False
if env_key:
    st.sidebar.success("✅ مفتاح API جاهز بالبيئة")
    use_different_key = st.sidebar.checkbox("استخدام مفتاح مختلف")

if env_key and not use_different_key:
    api_key = env_key
else:
    api_key = st.sidebar.text_input("Gemini API Key:", type="password")

st.sidebar.markdown('<div class="side-heading">💬 إعدادات المحادثة</div>', unsafe_allow_html=True)
scenario = st.sidebar.selectbox(
    "Choose Scenario:",
    [
        "Casual Friend (Everyday Chat)",
        "Supermarket Customer (Work Practice)",
        "Grammar & Translation Coach",
        "Speaking Placement Test (10+ Questions)",
    ],
    format_func=lambda s: f"{SCENARIO_ICONS.get(s, '💬')}  {s}",
)

voice_label = st.sidebar.selectbox(
    "Voice:",
    ["Aria — US Female", "Guy — US Male", "Sonia — UK Female", "Ryan — UK Male"],
)
VOICE_MAP = {
    "Aria — US Female": "en-US-AriaNeural",
    "Guy — US Male": "en-US-GuyNeural",
    "Sonia — UK Female": "en-GB-SoniaNeural",
    "Ryan — UK Male": "en-GB-RyanNeural",
}
voice_id = VOICE_MAP[voice_label]

autoplay_audio = st.sidebar.checkbox("🔊 Autoplay AI Voice", value=True)
voice_only_mode = st.sidebar.checkbox("🎙️ وضع المكالمة الصوتية (Voice-Only Mode)", value=False, help="إخفاء لوحة المفاتيح والتركيز على التحدث والصوت المباشر")

st.sidebar.markdown('<div class="side-heading">⚡ صرامة التصحيح</div>', unsafe_allow_html=True)
strictness = st.sidebar.selectbox(
    "Correction Level:",
    ["تصحيح جميع الأخطاء بدقة", "الأخطاء الكبيرة فقط (لتشجيع الطلاقة)", "بدون تصحيح (محادثة حرة تماماً)"],
)

with st.sidebar.expander("⚙️ إعدادات متقدمة للموديل"):
    model_name = st.text_input("Gemini Model:", value=DEFAULT_MODEL)

st.sidebar.markdown('<div class="side-heading">🧹 إدارة الجلسة</div>', unsafe_allow_html=True)
if st.sidebar.button("🔄 جلسة جديدة تماماً", use_container_width=True):
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()

# ==========================================
# 3. محول الصوتيات (Edge TTS) ومشغل Waveform
# ==========================================
async def _synthesize(text: str, voice: str, out_path: str):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(out_path)

def speak(text: str, voice: str) -> str:
    out_path = os.path.join(AUDIO_DIR, f"tts_{int(time.time() * 1000)}.mp3")
    asyncio.run(_synthesize(text, voice, out_path))
    return out_path

_VOICE_PLAYER_TEMPLATE = Template("""
<!DOCTYPE html>
<html>
<head>
<style>
  html, body { margin:0; padding:4px 0 0 0; background: transparent; font-family: sans-serif; }
  .vp-wrap {
    display: inline-flex; align-items: center; gap: 12px;
    background: linear-gradient(135deg, rgba(56,189,248,0.14), rgba(167,139,250,0.10));
    border: 1px solid rgba(56,189,248,0.28); border-radius: 999px; padding: 8px 16px 8px 8px;
  }
  .vp-btn {
    width: 34px; height: 34px; border-radius: 50%; border: none; cursor: pointer;
    background: linear-gradient(135deg, #38bdf8, #6366f1); color: #fff; font-size: 13px;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 2px 10px rgba(56,189,248,0.35);
  }
  .vp-wave { position: relative; width: ${wave_width}px; height: 28px; cursor: pointer; }
  .vp-bars-bg, .vp-bars-fixed { position: absolute; top: 0; left: 0; width: ${wave_width}px; height: 100%; display: flex; align-items: center; gap: 2px; }
  .vp-bars-bg span { display: block; width: 3px; border-radius: 2px; background: rgba(148,163,184,0.35); }
  .vp-bars-fixed span { display: block; width: 3px; border-radius: 2px; background: linear-gradient(180deg, #38bdf8, #a78bfa); }
  .vp-clip { position: absolute; top: 0; left: 0; height: 100%; width: 0px; overflow: hidden; }
  .vp-time { font-size: 11px; font-weight: 700; color: #94a3b8; min-width: 34px; text-align: right; }
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

def _wave_bar_heights(seed_key: str, bars: int = 30):
    rng = random.Random(seed_key)
    return [rng.randint(6, 24) for _ in range(bars)]

def render_voice_player(audio_path: str, autoplay: bool):
    with open(audio_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    heights = _wave_bar_heights(os.path.basename(audio_path))
    bars_html = "".join(f'<span style="height:{h}px"></span>' for h in heights)
    html = _VOICE_PLAYER_TEMPLATE.substitute(wave_width=150, bars=bars_html, autoplay_attr="autoplay" if autoplay else "", b64=b64)
    components.html(html, height=60, scrolling=False)

def render_typing_indicator(slot):
    slot.markdown("""
        <div class="typing-card">
            <span>🤖 AI يفكر ويكتب</span>
            <span class="typing-dots"><span></span><span></span><span></span></span>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# 4. بناء تبويبات المنصة الاحترافية (Tabs)
# ==========================================
tab_chat, tab_vocab, tab_memory, tab_stats = st.tabs([
    "💬 غرفة المحادثة", 
    "📓 دفتر المفردات (Vocab Notebook)", 
    "🧠 ذاكرة الذكاء الاصطناعي والملف الشخصي", 
    "📊 الإحصائيات الشاملة"
])

# ------------------------------------------
# تبويب 3: ذاكرة الذكاء الاصطناعي والملف الشخصي (AI Memory)
# ------------------------------------------
with tab_memory:
    st.subheader("🧠 ذاكرة المستخدم والملف الشخصي (AI Memory)")
    st.caption("هذه المعلومات تُرسل تلقائياً للذكاء الاصطناعي لكي يتذكرك دائماً ويوجه الأسئلة بناءً عليها.")

    with st.form("profile_form"):
        p_name = st.text_input("اسمك الكريم:", value=get_profile("name", ""))
        level_options = ["A1 (مبتدئ)", "A2 (مبتدئ متقدم)", "B1 (متوسط)", "B2 (متوسط متقدم)", "C1 (متقدم)", "C2 (محترف)"]
        saved_level = get_profile("level", "B1 (متوسط)")
        p_level = st.selectbox(
            "مستواك في الإنجليزية:",
            level_options,
            index=level_options.index(saved_level) if saved_level in level_options else 2,
        )
        p_goals = st.text_input("هدف التعلم (مثلاً: التحضير لـ IELTS، العمل في السوبرماركت، محادثة عامة):", value=get_profile("goals", ""))
        p_notes = st.text_area("ملاحظات خاصة للـ AI (مثل: نقاط ضعف أقع بها دائماً، تصحيح دقيق...):", value=get_profile("notes", ""))
        
        if st.form_submit_button("💾 حفظ الملف الشخصي وتحديث الذاكرة"):
            set_profile("name", p_name)
            set_profile("level", p_level)
            set_profile("goals", p_goals)
            set_profile("notes", p_notes)
            st.success("✅ تم تحديث ذاكرة الذكاء الاصطناعي بنجاح!")

# ------------------------------------------
# تبويب 2: دفتر المفردات (Vocabulary Notebook)
# ------------------------------------------
with tab_vocab:
    st.subheader("📓 دفتر المفردات الذكي (Vocabulary Notebook)")
    st.caption("احفظ الكلمات الجديدة، صنفها، وراجعها وقت ما تحب.")

    # إضافة كلمة جديدة يدوياً
    with st.expander("➕ إضافة كلمة جديدة لدفتر المفردات"):
        with st.form("add_vocab"):
            col1, col2 = st.columns(2)
            new_word = col1.text_input("الكلمة / التعبير بالإنجليزي:")
            new_type = col2.selectbox("التصنيف:", ["Verb (فعل)", "Noun (اسم)", "Phrase (تعبير)", "Adjective (صفة)"])
            new_meaning = st.text_input("المعنى بالعربي:")
            new_example = st.text_input("مثال إنجليزي:")
            if st.form_submit_button("حفظ الكلمة بالدفتر"):
                if new_word:
                    try:
                        conn = sqlite3.connect(DB_PATH)
                        c = conn.cursor()
                        c.execute("INSERT OR REPLACE INTO vocab_notebook (word, word_type, meaning_ar, example, status) VALUES (?, ?, ?, ?, ?)",
                                  (new_word.strip(), new_type, new_meaning.strip(), new_example.strip(), "Needs Review"))
                        conn.commit()
                        conn.close()
                        st.success(f"تم حفظ الكلمة ({new_word}) بنجاح!")
                        update_stat("total_anki", 1)
                    except Exception as e:
                        st.error(f"خطأ: {e}")
                else:
                    st.warning("يرجى كتابة الكلمة على الأقل.")

    # عرض وجدولة الكلمات المحفوظة
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id, word, word_type, meaning_ar, example, status FROM vocab_notebook ORDER BY id DESC")
        vocab_rows = c.fetchall()
        conn.close()

        if vocab_rows:
            search_q = st.text_input("🔍 ابحث داخل دفتر المفردات:", "")
            filtered = [r for r in vocab_rows if search_q.lower() in r[1].lower() or search_q in r[3]]
            
            st.markdown(f"**إجمالي الكلمات المحفوظة:** {len(vocab_rows)}")
            for row in filtered:
                r_id, r_word, r_type, r_meaning, r_example, r_status = row
                cols = st.columns([3, 2, 2, 1])
                cols[0].markdown(f"**{r_word}** ({r_type})<br><span style='color:#94a3b8;font-size:0.85rem;'>{r_meaning}</span>", unsafe_allow_html=True)
                cols[1].markdown(f"<span style='color:#cbd5e1;font-size:0.85rem;'>Ex: {r_example}</span>", unsafe_allow_html=True)
                
                status_color = "#34d399" if r_status == "Learned" else "#f87171"
                cols[2].markdown(f"<span style='color:{status_color};font-weight:700;'>{r_status}</span>", unsafe_allow_html=True)
                
                if cols[3].button("🔄 تبديل", key=f"toggle_v_{r_id}"):
                    new_st = "Learned" if r_status == "Needs Review" else "Needs Review"
                    conn = sqlite3.connect(DB_PATH)
                    c = conn.cursor()
                    c.execute("UPDATE vocab_notebook SET status = ? WHERE id = ?", (new_st, r_id))
                    conn.commit()
                    conn.close()
                    st.rerun()
        else:
            st.info("دفتر المفردات فارغ حالياً. أضف كلمات يدوياً أو استخرجها من جلسات المحادثة.")
    except Exception:
        pass

# ------------------------------------------
# تبويب 4: الإحصائيات الشاملة
# ------------------------------------------
with tab_stats:
    st.subheader("📊 لوحة إحصائيات التعلم الأداء")
    c1, c2, c3 = st.columns(3)
    c1.metric("💬 إجمالي الرسائل", get_stat("total_messages"))
    c2.metric("📇 بطاقات ومفردات Anki", get_stat("total_anki"))
    c3.metric("📚 كلمات متفاعل معها", get_stat("total_words"))
    st.markdown("---")
    st.info("💡 الاستمرارية هي سر إتقان اللغة الإنجليزية. استمر في التدرب يومياً!")

# ------------------------------------------
# تبويب 1: غرفة المحادثة الذكية (Main Chat Room)
# ------------------------------------------
with tab_chat:
    # جمع معلومات الذاكرة لدمجها مع System Prompt
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
        st.warning("👈 يرجى إدخال مفتاح Gemini API Key في الشريط الجانبي للبدء.")
        st.stop()

    try:
        client = genai.Client(api_key=api_key)
        config_signature = (scenario, model_name, strictness, mem_name, mem_level, mem_goals, mem_notes)
        if "chat_session" not in st.session_state or st.session_state.get("current_config") != config_signature:
            st.session_state.chat_session = client.chats.create(
                model=model_name,
                config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT, temperature=0.7),
            )
            st.session_state.current_config = config_signature
            st.session_state.messages = []
            st.session_state.test_question_count = 0

            if scenario == "Speaking Placement Test (10+ Questions)":
                welcome_msg = f"Welcome {mem_name} to the English Speaking Placement Test. Let's begin! Question 1: Could you introduce yourself and tell me a bit about your daily routine?"
                st.session_state.messages.append({"role": "assistant", "content": welcome_msg, "audio": speak(welcome_msg, voice_id)})
                update_stat("total_messages", 1)
    except Exception as e:
        st.error(f"⚠️ خطأ في الاتصال بالخادم: `{e}`")
        st.stop()

    # رأس الصفحة الترحيبي داخل غرفة المحادثة
    st.markdown(f"""
        <div class="hero-card">
            <div class="hero-title">🎙️ أهلاً بك يا {mem_name or 'صديقي'}!</div>
            <div class="hero-sub">المستوى: {mem_level} | الهدف: {mem_goals}</div>
            <div style="display:flex; gap:10px; flex-wrap:wrap;">
                <span class="badge">{SCENARIO_ICONS.get(scenario, '💬')} {scenario}</span>
                <span class="badge" style="background:rgba(167,139,250,0.12); color:#a78bfa; border-color:rgba(167,139,250,0.3);">🔊 {voice_label}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if scenario == "Speaking Placement Test (10+ Questions)":
        answered = st.session_state.get("test_question_count", 0)
        pct = min(answered / 10, 1.0)
        st.progress(pct, text=f"📝 تم الإجابة على {answered} سؤال من أصل 10-15")

    # معالجة الرسائل
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "audio_input_key" not in st.session_state:
        st.session_state.audio_input_key = 0

    def handle_user_message(text: str):
        st.session_state.messages.append({"role": "user", "content": text})
        update_stat("total_messages", 1)
        update_stat("total_words", len(text.split()))

        if scenario == "Speaking Placement Test (10+ Questions)":
            st.session_state.test_question_count = st.session_state.get("test_question_count", 0) + 1

        with st.chat_message("user", avatar="🧑"):
            st.write(text)

        with st.chat_message("assistant", avatar="🤖"):
            typing_slot = st.empty()
            render_typing_indicator(typing_slot)
            try:
                response = st.session_state.chat_session.send_message(text)
                full_reply = response.text
            except Exception as e:
                typing_slot.empty()
                st.error(f"⚠️ تعذر الحصول على رد: {e}")
                return
            typing_slot.empty()

            # فصل التقييم عن نص الرد الأساسي
            eval_data = None
            display_reply = full_reply
            eval_match = re.search(r"\[EVAL\|(.*?)]", full_reply)
            if eval_match:
                eval_str = eval_match.group(1)
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
                            <span>Grammar: {eval_data.get('Grammar','-')}</span>
                            <span>Vocab: {eval_data.get('Vocab','-')}</span>
                            <span>Natural: {eval_data.get('Natural','-')}</span>
                            <span>Fluency: {eval_data.get('Fluency','-')}</span>
                        </div>
                        <div><b>التصحيح والملحوظة:</b> {eval_data.get('Correction','ممتاز!')}</div>
                    </div>
                """, unsafe_allow_html=True)

            st.write(display_reply)

            audio_path = None
            try:
                audio_path = speak(display_reply, voice_id)
                render_voice_player(audio_path, autoplay_audio)
                st.session_state.last_played_audio = audio_path
            except Exception:
                pass

        st.session_state.messages.append({
            "role": "assistant", 
            "content": display_reply, 
            "audio": audio_path, 
            "eval": eval_data
        })
        update_stat("total_messages", 1)
        update_stat("total_words", len(display_reply.split()))

    # عرض الرسائل السابقة
    messages = st.session_state.messages
    if not messages:
        st.markdown("""
            <div style="text-align:center; padding:30px; border:1px dashed rgba(148,163,184,0.25); border-radius:16px; color:#94a3b8; margin-bottom:12px;">
                <div style="font-size:2rem; margin-bottom:8px;">🎙️</div>
                <b>ابدأ مكالمتك أو محادثتك الآن!</b><br/>تحدث بصوتك أو اكتب بالأسفل.
            </div>
        """, unsafe_allow_html=True)

    last_index = len(messages) - 1
    for i, msg in enumerate(messages):
        avatar = "🤖" if msg["role"] == "assistant" else "🧑"
        with st.chat_message(msg["role"], avatar=avatar):
            if msg.get("eval"):
                ev = msg["eval"]
                st.markdown(f"""
                    <div class="eval-card">
                        <div class="eval-scores">
                            <span>Grammar: {ev.get('Grammar','-')}</span>
                            <span>Vocab: {ev.get('Vocab','-')}</span>
                            <span>Natural: {ev.get('Natural','-')}</span>
                            <span>Fluency: {ev.get('Fluency','-')}</span>
                        </div>
                        <div><b>التصحيح والملحوظة:</b> {ev.get('Correction','ممتاز!')}</div>
                    </div>
                """, unsafe_allow_html=True)

            st.write(msg["content"])
            
            audio_path = msg.get("audio")
            if audio_path and os.path.exists(audio_path):
                is_fresh = (i == last_index) and (audio_path != st.session_state.get("last_played_audio"))
                render_voice_player(audio_path, autoplay_audio and is_fresh)
                if is_fresh:
                    st.session_state.last_played_audio = audio_path

            # أزرار الحذف والتعديل السريع
            c_del, c_edt, _ = st.columns([1, 1, 6])
            if c_del.button("🗑️ حذف", key=f"del_{i}"):
                st.session_state.messages.pop(i)
                st.rerun()

    # قسم الإدخال (صوت أو نص)
    st.markdown("---")
    if voice_only_mode:
        st.info("🎙️ **وضع المكالمة الصوتية مفعل**: تحدث مباشرة عبر المايك واستمع لرد الذكاء الاصطناعي تلقائياً.")

    audio_value = st.audio_input("🎤 سجل صوتك هنا", key=f"audio_recorder_{st.session_state.audio_input_key}")

    if audio_value is not None:
        audio_bytes = audio_value.getvalue()
        audio_id = hashlib.sha256(audio_bytes).hexdigest()
        if st.session_state.get("last_audio_id") != audio_id:
            st.session_state.last_audio_id = audio_id
            with st.spinner("🎧 جاري الاستماع وتحليل الصوت..."):
                try:
                    transcript = client.models.generate_content(
                        model=model_name,
                        contents=[types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav"), "Transcribe exactly what is said in this audio. Output ONLY the transcription."],
                    )
                    spoken_text = transcript.text.strip()
                except Exception as e:
                    spoken_text = None
                    st.error(f"⚠️ خطأ بالتعرف على الصوت: {e}")
            if spoken_text:
                handle_user_message(spoken_text)
            st.session_state.audio_input_key += 1
            st.rerun()

    if not voice_only_mode:
        typed = st.chat_input("...أو اكتب رسالتك هنا")
        if typed:
            handle_user_message(typed)
            st.rerun()

    # استخراج Anki التلقائي من المحادثة
    st.divider()
    if st.button("📇 تصدير مفردات هذه الجلسة إلى دفتر المفردات و Anki", use_container_width=True):
        user_turns = [m for m in st.session_state.messages if m["role"] == "user"]
        if not user_turns:
            st.warning("ابدأ المحادثة أولاً!")
        else:
            with st.spinner("✨ جاري استخراج الكلمات الجديدة وإضافتها لدفتر المفردات..."):
                conversation_text = "\n".join(f"{m['role']}: {m['content']}" for m in st.session_state.messages)
                anki_prompt = f"""Analyze this conversation. Extract 5 useful words or phrases.
Output ONLY plain tab-separated lines in this exact format:
Word[TAB]Arabic Meaning + Example Sentence

Conversation:
{conversation_text}"""
                try:
                    anki_result = client.models.generate_content(
                        model=model_name, contents=anki_prompt, config=types.GenerateContentConfig(temperature=0.3)
                    )
                    anki_text = anki_result.text.strip()
                    
                    # حفظ بالدفتر أيضاً تلقائياً
                    conn = sqlite3.connect(DB_PATH)
                    c = conn.cursor()
                    for line in anki_text.splitlines():
                        if "\t" in line:
                            parts = line.split("\t", 1)
                            w = parts[0].strip()
                            m = parts[1].strip()
                            c.execute("INSERT OR IGNORE INTO vocab_notebook (word, word_type, meaning_ar, example, status) VALUES (?, ?, ?, ?, ?)",
                                      (w, "Phrase", m, "", "Needs Review"))
                    conn.commit()
                    conn.close()

                    st.session_state.anki_cards = anki_text
                    update_stat("total_anki", len(anki_text.splitlines()))
                    st.success("✅ تمت الإضافة لدفتر المفردات وجاهزة للتحميل!")
                except Exception as e:
                    st.error(f"خطأ: {e}")

    if "anki_cards" in st.session_state:
        st.download_button(
            label="⬇️ تحميل ملف Anki (.txt)",
            data=st.session_state.anki_cards,
            file_name=f"anki_elite_{int(time.time())}.txt",
            mime="text/plain",
            use_container_width=True,
        )
