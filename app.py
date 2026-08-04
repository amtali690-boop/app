# ==========================================
# AI English Conversation Partner — v7 (Ultra Pro+) — Reply Fix + Export + Typing + CEFR Badge
# تحديثات v7:
# 1) إصلاح جذر مشكلة "ما بقدر أرد بعد ما يجاوب الـ AI": خانة تسجيل الصوت (audio_input)
#    كانت تحتفظ بالتسجيل القديم بعد إرساله، فتظهر وكأنها "عالقة" ولا تسمح بتسجيل رسالة
#    جديدة بسهولة. الآن تتصفّر تلقائياً بمفتاح جديد بعد كل رسالة صوتية (نجحت أو فشلت)،
#    فتقدر تسجّل فوراً من جديد. صندوق الكتابة النصي أُضيف له إعادة تحميل فورية بعد كل
#    رسالة أيضاً، عشان رد الـ AI يطلع دايماً بمكانه الصحيح فوق المحادثة مباشرة.
# 2) زر جديد بالشريط الجانبي لتصدير/حفظ المحادثة كاملة كملف .txt.
# 3) مؤشر "🤖 AI يكتب..." متحرك (نقاط متحركة) بدل السبينر الافتراضي أثناء انتظار الرد.
# 4) شارة واضحة (Badge) تظهر تلقائياً فوق التقرير النهائي لاختبار تحديد المستوى، توضح
#    مستوى CEFR (A1-C2) بصرياً بدل ما يضيع وسط النص.
#
# إصلاحات وتحسينات v5:
# 1) استبدال موديل Gemini المتوقف (gemini-2.0-flash) بموديل قابل للتعديل من الشريط الجانبي
#    (Google أوقفت دعم gemini-2.0-flash فعلياً في 1 يونيو 2026).
# 2) إصلاح خلل كان يحذف كل ملفات الصوت المؤقتة مع كل رسالة جديدة — الآن لكل جلسة مستخدم
#    مجلد صوت خاص بها، فلا تختفي أصوات المحادثة، ولا تتأثر بجلسات مستخدمين آخرين على نفس الخادم.
# 3) رسائل خطأ الذكاء الاصطناعي لم تعد تُقرأ صوتياً، ولا تُحفظ كرد صحيح، ولا تدخل ضمن استخراج Anki.
# 4) زر "إعادة التشغيل" الآن يمسح أيضاً بطاقات Anki القديمة وعداد الأسئلة ومجلد الصوت.
# 5) مؤشر تقدم مرئي لعدد الأسئلة المُجابة في اختبار تحديد المستوى.
# 6) تحديث use_container_width (متوقف في Streamlit) إلى width="stretch".
# 7) مفتاح API القادم من متغيرات البيئة لم يعد يُعرض كاملاً داخل حقل نصي بالواجهة.
# 8) استخراج Anki أصبح أكثر ثباتاً (يتجاهل أي Markdown زائد في رد النموذج).
#
# تحديثات واجهة (UI Refresh 1) — بدون أي تغيير على المنطق/الصوت/الـ API:
# - تصميم عام أهدأ وأكثر احترافية (خلفية، بطاقات، تدرجات لونية خفيفة).
# - رأس صفحة (Hero header) مع شارة توضح السيناريو الحالي والصوت الحالي.
# - شريط جانبي مقسّم لأقسام واضحة بعناوين وأيقونات وفواصل.
# - فقاعات محادثة مخصصة بمظهر بطاقة، وأفاتار مختلف للمستخدم/الذكاء الاصطناعي.
# - مؤشر تقدّم اختبار المستوى بشكل شريط ملوّن متدرّج مع نسبة مئوية.
#
# تحديثات واجهة (UI Refresh 2) — أيضاً بدون أي تغيير على منطق التوليد الصوتي نفسه:
# - "مشغّل صوت" مخصص بالكامل على شكل رسالة صوتية (Waveform) بدل شريط الصوت الافتراضي للمتصفح:
#   زر تشغيل/إيقاف دائري متدرّج، موجة صوت (Bars) تُلوَّن مع تقدّم التشغيل الفعلي، إمكانية
#   الضغط على أي نقطة من الموجة للقفز إليها مباشرة، وعرض الوقت الحالي/الإجمالي. الملف الصوتي
#   المشغَّل هو نفسه تماماً الناتج من edge_tts دون أي تعديل — فقط طريقة عرضه تغيّرت.
# - بطاقة ترحيبية تظهر فقط قبل أول رسالة لتوجيه المستخدم الجديد.
# - معاينة سريعة لبطاقات Anki المستخرجة (Front/Back) قبل التحميل.
# - تذييل بسيط بالشريط الجانبي يعرض الموديل الحالي وعدد رسائل الجلسة.
#
# التحديثات السابقة (v4):
# 1) اختبار تحديد المستوى يسأل 10 أسئلة كحد أدنى، وقد يمتد لـ 15 سؤال لضمان الدقة.
# 2) تحسين سيناريو القواعد ليركز على الأفعال والأسماء العامة وبناء جمل الترجمة.
# 3) إضافة خيار (Autoplay Toggle) للتحكم بتشغيل الصوت تلقائياً أو يدوياً.
# 4) تحسين استخراج كلمات Anki لتركز على الكلمات التي أخطأ فيها المستخدم.
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
from string import Template

import streamlit as st
import streamlit.components.v1 as components
import edge_tts
from google import genai
from google.genai import types

# ==========================================
# 0. مجلد صوت خاص بكل جلسة + تنظيف الجلسات القديمة المتروكة
# ==========================================
if "session_audio_dir" not in st.session_state:
    st.session_state.session_audio_dir = os.path.join(
        tempfile.gettempdir(), "ai_english_partner", uuid.uuid4().hex
    )
    os.makedirs(st.session_state.session_audio_dir, exist_ok=True)

AUDIO_DIR = st.session_state.session_audio_dir


def cleanup_old_sessions(max_age_hours: int = 3):
    """ينظّف مجلدات صوت الجلسات القديمة/المتروكة فقط.
    لا يلمس مجلد جلستك الحالية إطلاقاً، ولا ملفات مستخدمين آخرين ما زالوا نشطين على نفس الخادم."""
    base_dir = os.path.join(tempfile.gettempdir(), "ai_english_partner")
    if not os.path.isdir(base_dir):
        return
    cutoff = time.time() - max_age_hours * 3600
    for name in os.listdir(base_dir):
        folder = os.path.join(base_dir, name)
        if folder == AUDIO_DIR:
            continue
        try:
            if os.path.isdir(folder) and os.path.getmtime(folder) < cutoff:
                shutil.rmtree(folder, ignore_errors=True)
        except Exception:
            pass


cleanup_old_sessions()

# ==========================================
# 1. إعدادات الصفحة + تنسيقات CSS (شكل فقط — لا تغيير منطقي)
# ==========================================
st.set_page_config(page_title="AI English Partner", page_icon="🎙️", layout="wide")

# قيمة افتراضية "حيّة" تتحدّث تلقائياً مع Google بدل تثبيت اسم موديل قد يُلغى فجأة.
# إذا ظهرت رسالة خطأ تفيد بأن الموديل غير متاح، غيّره من "⚙️ إعدادات متقدمة" بالشريط الجانبي.
DEFAULT_MODEL = "gemini-flash-latest"

SCENARIO_ICONS = {
    "Casual Friend (Everyday Chat)": "☕",
    "Supermarket Customer (Work Practice)": "🛒",
    "Grammar & Translation Coach": "📘",
    "Speaking Placement Test (10+ Questions)": "📝",
}

st.markdown(
    """
    <style>
        .stApp {
            background: radial-gradient(circle at top left, #101820 0%, #0b0f14 55%, #05070a 100%);
        }
        .hero-card {
            background: linear-gradient(135deg, #1f2937 0%, #111827 60%, #0b0f14 100%);
            border: 1px solid rgba(148, 163, 184, 0.15);
            border-radius: 18px;
            padding: 22px 28px;
            margin-bottom: 18px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.35);
        }
        .hero-title {
            font-size: 1.8rem;
            font-weight: 800;
            color: #f8fafc;
            margin-bottom: 4px;
        }
        .hero-sub {
            color: #94a3b8;
            font-size: 0.95rem;
            margin-bottom: 14px;
        }
        .badge-row { display: flex; gap: 10px; flex-wrap: wrap; }
        .badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 14px;
            border-radius: 999px;
            font-size: 0.82rem;
            font-weight: 600;
            background: rgba(56, 189, 248, 0.12);
            color: #38bdf8;
            border: 1px solid rgba(56, 189, 248, 0.3);
        }
        .badge.alt {
            background: rgba(167, 139, 250, 0.12);
            color: #a78bfa;
            border: 1px solid rgba(167, 139, 250, 0.3);
        }
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f172a 0%, #0b1120 100%);
            border-right: 1px solid rgba(148,163,184,0.1);
        }
        .side-heading {
            font-size: 0.78rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #64748b;
            font-weight: 700;
            margin: 18px 0 6px 0;
        }
        div[data-testid="stChatMessage"] {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(148,163,184,0.08);
            border-radius: 14px;
            padding: 4px 6px;
            margin-bottom: 6px;
        }
        div[data-testid="stChatInput"] {
            border-radius: 14px;
        }
        div[data-testid="stAudioInput"] {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(148,163,184,0.12);
            border-radius: 14px;
            padding: 4px 8px;
        }
        .empty-state-card {
            text-align: center;
            padding: 34px 20px;
            border: 1px dashed rgba(148,163,184,0.25);
            border-radius: 16px;
            color: #94a3b8;
            margin-bottom: 12px;
        }
        .empty-state-card b { color: #e2e8f0; }
        .anki-result-card {
            background: rgba(52, 211, 153, 0.06);
            border: 1px solid rgba(52, 211, 153, 0.25);
            border-radius: 14px;
            padding: 16px 18px;
        }
        div[data-testid="stProgress"] > div > div {
            background-image: linear-gradient(90deg, #38bdf8, #a78bfa, #34d399);
        }
        .stButton>button, .stDownloadButton>button {
            border-radius: 10px;
            font-weight: 700;
        }
        .cefr-badge {
            display: flex;
            align-items: center;
            gap: 14px;
            background: linear-gradient(135deg, rgba(56,189,248,0.10), rgba(167,139,250,0.08));
            border: 1px solid rgba(148,163,184,0.25);
            border-radius: 14px;
            padding: 12px 18px;
            margin-bottom: 10px;
        }
        .cefr-badge-level {
            font-size: 1.6rem;
            font-weight: 900;
            line-height: 1;
            min-width: 46px;
            text-align: center;
        }
        .cefr-badge-text { color: #e2e8f0; font-size: 0.85rem; line-height: 1.4; }
        .typing-card {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(148,163,184,0.12);
            border-radius: 14px;
            padding: 10px 16px;
            color: #94a3b8;
            font-size: 0.88rem;
            font-weight: 600;
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


def build_transcript(messages: list, scenario_name: str) -> str:
    """يحوّل قائمة الرسائل لنص عادي جاهز للتحميل كملف .txt."""
    lines = [
        "AI English Conversation Partner — نسخة المحادثة",
        f"السيناريو: {scenario_name}",
        f"التاريخ: {time.strftime('%Y-%m-%d %H:%M')}",
        "-" * 40,
        "",
    ]
    for m in messages:
        speaker = "أنت" if m["role"] == "user" else "AI"
        lines.append(f"{speaker}: {m['content']}")
        lines.append("")
    return "\n".join(lines)

# ==========================================
# 2. الشريط الجانبي: الإعدادات والتحكم
# ==========================================
st.sidebar.markdown("### 🎙️ AI English Partner")
st.sidebar.caption("إعداداتك الشخصية للمحادثة والصوت")

st.sidebar.markdown('<div class="side-heading">🔑 API</div>', unsafe_allow_html=True)

env_key = os.environ.get("GEMINI_API_KEY", "")
use_different_key = False
if env_key:
    st.sidebar.success("✅ تم العثور على مفتاح API في متغيرات البيئة")
    use_different_key = st.sidebar.checkbox("استخدام مفتاح مختلف")

if env_key and not use_different_key:
    api_key = env_key
else:
    api_key = st.sidebar.text_input(
        "Gemini API Key:",
        type="password",
        help="مفتاح مجاني من aistudio.google.com",
    )

st.sidebar.markdown('<div class="side-heading">💬 السيناريو</div>', unsafe_allow_html=True)
scenario = st.sidebar.selectbox(
    "Choose Conversation Scenario:",
    [
        "Casual Friend (Everyday Chat)",
        "Supermarket Customer (Work Practice)",
        "Grammar & Translation Coach",
        "Speaking Placement Test (10+ Questions)",
    ],
    format_func=lambda s: f"{SCENARIO_ICONS.get(s, '💬')}  {s}",
)

st.sidebar.markdown('<div class="side-heading">🔊 الصوت</div>', unsafe_allow_html=True)
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

# زر التحكم بالتشغيل التلقائي للصوت
autoplay_audio = st.sidebar.checkbox("🔊 Autoplay AI Voice", value=True)

st.sidebar.markdown('<div class="side-heading">⚙️ متقدم</div>', unsafe_allow_html=True)
with st.sidebar.expander("⚙️ إعدادات متقدمة"):
    model_name = st.text_input(
        "Gemini Model:",
        value=DEFAULT_MODEL,
        help=(
            "غيّر هذا فقط إذا ظهرت رسالة خطأ تفيد بأن الموديل غير متاح — "
            "Google تُلغي موديلات Gemini القديمة بشكل متكرر."
        ),
    )

PROMPTS = {
    "Casual Friend (Everyday Chat)": (
        "Act like a close friend having an easygoing conversation. Ask open-ended "
        "questions about daily life. Speak ONLY in English. Keep answers short and natural."
    ),
    "Supermarket Customer (Work Practice)": (
        "Act like an English-speaking customer in a supermarket asking for items, "
        "prices, or recommendations. Be polite, natural, and stick strictly to English."
    ),
    "Grammar & Translation Coach": (
        "Act like a supportive English tutor. Focus heavily on improving the user's grasp of general verbs and nouns, "
        "and help them build strong sentence structures useful for translation. "
        "If they make a mistake, gently correct it in 1 short sentence before continuing the conversation naturally in English."
    ),
    "Speaking Placement Test (10+ Questions)": (
        "You are a strict but fair English language examiner conducting a CEFR Speaking Placement Test. "
        "CRITICAL RULES: "
        "1. You MUST ask AT LEAST 10 questions. If you need more data to accurately evaluate the user, you may ask up to 15 questions. "
        "2. Do NOT provide the final evaluation before asking a minimum of 10 questions. "
        "3. Ask ONLY ONE question at a time and wait for the user's response. "
        "4. Start with basic topics and progressively increase the complexity of grammar and vocabulary. "
        "5. Preface each question with its number (e.g., 'Question 3: ...'). "
        "6. Do not correct mistakes during the test. "
        "7. Once you have asked at least 10 questions and are confident in the user's level, end the test by generating a detailed report including: Estimated CEFR level (A1-C2), Strengths, and Areas for Improvement."
    ),
}

st.sidebar.markdown('<div class="side-heading">🧹 الجلسة</div>', unsafe_allow_html=True)
if st.sidebar.button("🔄 Restart Session", width="stretch"):
    old_dir = st.session_state.get("session_audio_dir")
    if old_dir and os.path.isdir(old_dir):
        shutil.rmtree(old_dir, ignore_errors=True)
    for k in [
        "messages", "chat_session", "current_scenario", "current_model",
        "last_audio_id", "last_played_audio", "test_question_count",
        "anki_cards", "session_audio_dir", "audio_input_key",
    ]:
        st.session_state.pop(k, None)
    st.rerun()

st.sidebar.markdown('<div class="side-heading">📄 تصدير المحادثة</div>', unsafe_allow_html=True)
if st.session_state.get("messages"):
    st.sidebar.download_button(
        label="⬇️ حفظ المحادثة كملف نصي",
        data=build_transcript(st.session_state.messages, scenario),
        file_name=f"conversation_{int(time.time())}.txt",
        mime="text/plain",
        width="stretch",
    )
else:
    st.sidebar.caption("ابدأ المحادثة الأول عشان تقدر تصدّرها.")

st.sidebar.markdown("---")
st.sidebar.caption(f"🧠 Model: {model_name}")
st.sidebar.caption(f"💬 {len(st.session_state.get('messages', []))} رسالة في هذه الجلسة")

# ==========================================
# 3. تحويل النص لصوت بشري (Edge TTS)
# ==========================================
async def _synthesize(text: str, voice: str, out_path: str):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(out_path)


def speak(text: str, voice: str) -> str:
    out_path = os.path.join(AUDIO_DIR, f"tts_{int(time.time() * 1000)}.mp3")
    asyncio.run(_synthesize(text, voice, out_path))
    return out_path


# ------------------------------------------
# 3.b مشغّل صوت مخصص بشكل "رسالة صوتية" (Waveform) — شكل فقط.
# يقرأ نفس ملف الـ mp3 الذي تنتجه speak() أعلاه بالضبط ويعرضه بواجهة تفاعلية:
# زر تشغيل/إيقاف + موجة صوت تتلوّن مع التقدّم الفعلي + إمكانية القفز بالضغط على الموجة.
# ------------------------------------------
_VOICE_PLAYER_TEMPLATE = Template("""
<!DOCTYPE html>
<html>
<head>
<style>
  html, body { margin:0; padding:4px 0 0 0; background: transparent; font-family: -apple-system, "Segoe UI", Roboto, Arial, sans-serif; }
  .vp-wrap {
    display: inline-flex; align-items: center; gap: 12px;
    background: linear-gradient(135deg, rgba(56,189,248,0.14), rgba(167,139,250,0.10));
    border: 1px solid rgba(56,189,248,0.28);
    border-radius: 999px;
    padding: 8px 16px 8px 8px;
    box-sizing: border-box;
  }
  .vp-btn {
    flex: 0 0 auto;
    width: 34px; height: 34px;
    border-radius: 50%;
    border: none;
    cursor: pointer;
    background: linear-gradient(135deg, #38bdf8, #6366f1);
    color: #ffffff;
    font-size: 13px;
    padding-left: 2px;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 2px 10px rgba(56,189,248,0.35);
    transition: transform 0.12s ease, box-shadow 0.2s ease;
  }
  .vp-btn:active { transform: scale(0.90); }
  .vp-wrap.playing .vp-btn {
    box-shadow: 0 0 0 4px rgba(56,189,248,0.18), 0 2px 10px rgba(56,189,248,0.35);
  }
  .vp-wave {
    position: relative;
    width: ${wave_width}px;
    height: 28px;
    cursor: pointer;
    flex: 0 0 auto;
  }
  .vp-bars-bg, .vp-bars-fixed {
    position: absolute; top: 0; left: 0;
    width: ${wave_width}px; height: 100%;
    display: flex; align-items: center; gap: 2px;
  }
  .vp-bars-bg span {
    display: block; width: 3px; border-radius: 2px;
    background: rgba(148,163,184,0.35);
  }
  .vp-bars-fixed span {
    display: block; width: 3px; border-radius: 2px;
    background: linear-gradient(180deg, #38bdf8, #a78bfa);
  }
  .vp-clip {
    position: absolute; top: 0; left: 0; height: 100%;
    width: 0px; overflow: hidden;
  }
  .vp-time {
    flex: 0 0 auto;
    font-size: 11px; font-weight: 700;
    color: #94a3b8; min-width: 34px; text-align: right;
    font-variant-numeric: tabular-nums;
  }
</style>
</head>
<body>
  <div class="vp-wrap" id="wrap">
    <button class="vp-btn" id="btn" aria-label="play">&#9658;</button>
    <div class="vp-wave" id="wave">
      <div class="vp-bars-bg">${bars}</div>
      <div class="vp-clip" id="clip">
        <div class="vp-bars-fixed">${bars}</div>
      </div>
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
  var wrap = document.getElementById('wrap');
  var WAVE_WIDTH = ${wave_width};

  function fmt(s) {
    if (!isFinite(s) || s < 0) { return '0:00'; }
    s = Math.round(s);
    var m = Math.floor(s / 60);
    var r = s % 60;
    var rs = String(r);
    if (rs.length < 2) { rs = '0' + rs; }
    return m + ':' + rs;
  }

  audio.addEventListener('loadedmetadata', function () {
    timeLabel.textContent = fmt(audio.duration);
  });
  audio.addEventListener('play', function () {
    btn.innerHTML = '&#10074;&#10074;';
    wrap.classList.add('playing');
  });
  audio.addEventListener('pause', function () {
    btn.innerHTML = '&#9658;';
    wrap.classList.remove('playing');
  });
  audio.addEventListener('ended', function () {
    btn.innerHTML = '&#9658;';
    wrap.classList.remove('playing');
    clip.style.width = '0px';
    timeLabel.textContent = fmt(audio.duration);
  });
  audio.addEventListener('timeupdate', function () {
    if (audio.duration) {
      var frac = audio.currentTime / audio.duration;
      clip.style.width = (frac * WAVE_WIDTH) + 'px';
      timeLabel.textContent = fmt(audio.currentTime);
    }
  });
  btn.addEventListener('click', function () {
    if (audio.paused) { audio.play().catch(function(){}); } else { audio.pause(); }
  });
  wave.addEventListener('click', function (e) {
    var rect = wave.getBoundingClientRect();
    var x = e.clientX - rect.left;
    var frac = Math.min(Math.max(x / rect.width, 0), 1);
    if (isFinite(audio.duration)) {
      audio.currentTime = frac * audio.duration;
    }
  });
  if (audio.autoplay) {
    audio.play().catch(function(){});
  }
</script>
</body>
</html>
""")


def _wave_bar_heights(seed_key: str, bars: int = 30, low: int = 6, high: int = 24):
    rng = random.Random(seed_key)
    return [rng.randint(low, high) for _ in range(bars)]


def render_voice_player(audio_path: str, autoplay: bool):
    """يبني ويعرض مشغّل الصوت المخصص (Waveform) لملف mp3 معيّن. الملف نفسه غير متأثر إطلاقاً."""
    with open(audio_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")

    heights = _wave_bar_heights(os.path.basename(audio_path))
    bars_html = "".join(f'<span style="height:{h}px"></span>' for h in heights)

    html = _VOICE_PLAYER_TEMPLATE.substitute(
        wave_width=150,
        bars=bars_html,
        autoplay_attr="autoplay" if autoplay else "",
        b64=b64,
    )
    components.html(html, height=60, scrolling=False)


# ------------------------------------------
# 3.c أدوات مساعدة: مؤشر الكتابة + شارة نتيجة CEFR
# ------------------------------------------
CEFR_INFO = {
    "A1": ("#38bdf8", "مبتدئ"),
    "A2": ("#38bdf8", "مبتدئ متقدم"),
    "B1": ("#a78bfa", "متوسط"),
    "B2": ("#a78bfa", "متوسط متقدم"),
    "C1": ("#34d399", "متقدم"),
    "C2": ("#34d399", "إتقان تام"),
}
CEFR_PATTERN = re.compile(r"\b(A1|A2|B1|B2|C1|C2)\b")


def extract_cefr_level(text: str, questions_asked: int = 0):
    """يحاول يلقط مستوى CEFR من التقرير النهائي فقط (بعد 10 أسئلة على الأقل، ولو
    الرسالة فعلاً بتذكر CEFR أو Level) — عشان ما تطلع الشارة غلط أثناء الأسئلة العادية."""
    if questions_asked < 10:
        return None
    lowered = text.lower()
    if "cefr" not in lowered and "level" not in lowered:
        return None
    match = CEFR_PATTERN.search(text)
    return match.group(1) if match else None


def render_cefr_badge(level: str):
    color, label_ar = CEFR_INFO.get(level, ("#38bdf8", ""))
    st.markdown(
        f"""
        <div class="cefr-badge" style="border-color:{color}66;">
            <div class="cefr-badge-level" style="color:{color};">{level}</div>
            <div class="cefr-badge-text"><b>🎓 نتيجة اختبار تحديد المستوى</b><br/>
            <span style="color:#94a3b8;">{label_ar}</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_typing_indicator(slot):
    slot.markdown(
        """
        <div class="typing-card">
            <span>🤖 AI يكتب</span>
            <span class="typing-dots"><span></span><span></span><span></span></span>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ==========================================
# 4. رأس الصفحة (Hero) + الاتصال بـ Gemini وإدارة الجلسة
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "audio_input_key" not in st.session_state:
    st.session_state.audio_input_key = 0

st.markdown(
    f"""
    <div class="hero-card">
        <div class="hero-title">🎙️ AI English Conversation Partner</div>
        <div class="hero-sub">مارس الإنجليزي، اختبر مستواك بدقة، واستخرج مفرداتك لـ Anki بنقرة زر.</div>
        <div class="badge-row">
            <span class="badge">{SCENARIO_ICONS.get(scenario, '💬')} {scenario}</span>
            <span class="badge alt">🔊 {voice_label}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if not api_key:
    st.warning("👈 يرجى إدخال مفتاح Gemini API Key في الشريط الجانبي للبدء.")
    st.stop()

try:
    client = genai.Client(api_key=api_key)
    if (
        "chat_session" not in st.session_state
        or st.session_state.get("current_scenario") != scenario
        or st.session_state.get("current_model") != model_name
    ):
        st.session_state.chat_session = client.chats.create(
            model=model_name,
            config=types.GenerateContentConfig(
                system_instruction=PROMPTS[scenario],
                temperature=0.7,
            ),
        )
        st.session_state.current_scenario = scenario
        st.session_state.current_model = model_name
        st.session_state.messages = []
        st.session_state.test_question_count = 0

        # الترحيب الخاص باختبار المستوى
        if scenario == "Speaking Placement Test (10+ Questions)":
            welcome_msg = "Welcome to the English Speaking Placement Test. I will ask you at least 10 questions to determine your level. Let's begin! Question 1: Could you introduce yourself and tell me a bit about your daily routine?"
            st.session_state.messages.append(
                {"role": "assistant", "content": welcome_msg, "audio": speak(welcome_msg, voice_id)}
            )
except Exception as e:
    st.error(
        f"⚠️ تعذر الاتصال بالخادم. تأكد من صحة المفتاح، أو أن الموديل `{model_name}` "
        f"لا يزال مدعوماً من Google (يمكنك تغييره من ⚙️ إعدادات متقدمة).\n\n`{e}`"
    )
    st.stop()

# مؤشر تقدم اختبار تحديد المستوى
if scenario == "Speaking Placement Test (10+ Questions)":
    answered = st.session_state.get("test_question_count", 0)
    pct = min(answered / 10, 1.0)
    st.progress(pct, text=f"📝 تم الإجابة على {answered} سؤال من أصل 10-15 ({int(pct*100)}%)")

# ==========================================
# 5. عرض المحادثة السابقة
# ==========================================
messages = st.session_state.messages

if not messages:
    st.markdown(
        """
        <div class="empty-state-card">
            <div style="font-size:2rem; margin-bottom:8px;">🎙️</div>
            <b>ابدأ محادثتك الأولى!</b><br/>
            اكتب رسالة بالأسفل أو سجّل صوتك للتمرّن على الإنجليزي.
        </div>
        """,
        unsafe_allow_html=True,
    )

last_index = len(messages) - 1
for i, msg in enumerate(messages):
    avatar = "🤖" if msg["role"] == "assistant" else "🧑"
    with st.chat_message(msg["role"], avatar=avatar):
        if msg.get("cefr_level"):
            render_cefr_badge(msg["cefr_level"])
        st.write(msg["content"])
        audio_path = msg.get("audio")
        if audio_path and os.path.exists(audio_path):
            is_fresh = (i == last_index) and (audio_path != st.session_state.get("last_played_audio"))
            render_voice_player(audio_path, autoplay_audio and is_fresh)
            if is_fresh:
                st.session_state.last_played_audio = audio_path

# ==========================================
# 6. معالجة الرسائل
# ==========================================
def handle_user_message(text: str):
    st.session_state.messages.append({"role": "user", "content": text})
    with st.chat_message("user", avatar="🧑"):
        st.write(text)

    if scenario == "Speaking Placement Test (10+ Questions)":
        st.session_state.test_question_count = st.session_state.get("test_question_count", 0) + 1

    with st.chat_message("assistant", avatar="🤖"):
        typing_slot = st.empty()
        render_typing_indicator(typing_slot)
        try:
            response = st.session_state.chat_session.send_message(text)
            reply = response.text
        except Exception as e:
            typing_slot.empty()
            st.error(f"⚠️ تعذر الحصول على رد. حاول إرسال رسالتك مرة أخرى.\n\n`{e}`")
            return  # لا نسجّل رداً فاشلاً كأنه رد حقيقي؛ رسالتك تبقى فوق لإعادة المحاولة
        typing_slot.empty()

        cefr_level = None
        if scenario == "Speaking Placement Test (10+ Questions)":
            cefr_level = extract_cefr_level(reply, st.session_state.get("test_question_count", 0))
            if cefr_level:
                render_cefr_badge(cefr_level)

        st.write(reply)

        audio_path = None
        try:
            audio_path = speak(reply, voice_id)
            render_voice_player(audio_path, autoplay_audio)
            st.session_state.last_played_audio = audio_path
        except Exception:
            st.caption("🔇 تعذر توليد الصوت هالمرة، لكن يمكنك متابعة المحادثة نصياً.")

    st.session_state.messages.append(
        {"role": "assistant", "content": reply, "audio": audio_path, "cefr_level": cefr_level}
    )

# ==========================================
# 7. إدخال صوتي (مايك)
# ==========================================
st.markdown('<div class="side-heading">🎤 سجّل رسالتك</div>', unsafe_allow_html=True)
st.caption("💡 تقدر ترد بصوتك هنا أو بالكتابة بالأسفل — الاثنين متاحين طول الوقت بعد كل رد من الـ AI.")
audio_value = st.audio_input(
    "🎤 Record your message (Speak clearly in English)",
    key=f"audio_recorder_{st.session_state.audio_input_key}",
)

if audio_value is not None:
    audio_bytes = audio_value.getvalue()
    audio_id = hashlib.sha256(audio_bytes).hexdigest()
    if st.session_state.get("last_audio_id") != audio_id:
        st.session_state.last_audio_id = audio_id
        with st.spinner("🎧 جاري الاستماع لصوتك..."):
            try:
                transcript = client.models.generate_content(
                    model=model_name,
                    contents=[
                        types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav"),
                        "Transcribe exactly what is said in this audio. Output ONLY the transcription.",
                    ],
                )
                spoken_text = transcript.text.strip()
            except Exception as e:
                spoken_text = None
                st.error(f"⚠️ لم نتمكن من فهم الصوت: {e}")
        if spoken_text:
            handle_user_message(spoken_text)
        # نبدّل مفتاح خانة التسجيل بعد كل محاولة (نجحت أو فشلت) عشان تظهر فاضية فوراً،
        # وما "تعلق" على نفس التسجيل القديم وتمنعك من الرد مرة ثانية.
        st.session_state.audio_input_key += 1
        st.rerun()

# ==========================================
# 8. إدخال نصي
# ==========================================
typed = st.chat_input("...or type your message here")
if typed:
    handle_user_message(typed)
    st.rerun()

# ==========================================
# 9. مستخرج Anki المُحسَّن
# ==========================================
st.divider()
st.markdown("#### 📇 Anki Flashcards")
col1, col2 = st.columns([1, 2])
with col1:
    if st.button("📇 Extract Anki Flashcards", width="stretch"):
        user_turns = [m for m in st.session_state.messages if m["role"] == "user"]
        if not user_turns:
            st.warning("ابدأ المحادثة أولاً!")
        else:
            with st.spinner("✨ يتم استخراج أهم الأفعال والأسماء للمراجعة..."):
                conversation_text = "\n".join(
                    f"{m['role']}: {m['content']}" for m in st.session_state.messages
                )
                anki_prompt = f"""Analyze this English conversation. Extract 4 to 8 useful words or short phrases,
focusing particularly on general verbs, nouns, and phrases that the user struggled with, or new vocabulary the AI introduced.

Output ONLY plain tab-separated lines in exactly this format — no header row, no numbering,
no Markdown, no code fences, and no extra commentary before or after the lines:
Front (Word)[TAB]Back (short Arabic meaning + one English example sentence)

Conversation:
{conversation_text}"""
                try:
                    anki_result = client.models.generate_content(
                        model=model_name,
                        contents=anki_prompt,
                        config=types.GenerateContentConfig(temperature=0.3),
                    )
                    anki_text = anki_result.text.strip()
                    if anki_text.startswith("```"):
                        lines = anki_text.split("\n")[1:]
                        if lines and lines[-1].strip() == "```":
                            lines = lines[:-1]
                        anki_text = "\n".join(lines).strip()
                    st.session_state.anki_cards = anki_text
                except Exception as e:
                    st.error(f"⚠️ صار خطأ أثناء الاستخراج: {e}")

with col2:
    if "anki_cards" in st.session_state:
        card_lines = [ln for ln in st.session_state.anki_cards.splitlines() if ln.strip()]
        st.markdown(
            f"""
            <div class="anki-result-card">
                <b>✅ تم التجهيز بنجاح!</b><br/>
                <span style="color:#94a3b8;">تم استخراج {len(card_lines)} بطاقة جاهزة للتحميل.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")
        st.download_button(
            label="⬇️ Download .txt for Anki",
            data=st.session_state.anki_cards,
            file_name=f"anki_vocabulary_{int(time.time())}.txt",
            mime="text/plain",
            width="stretch",
        )
        with st.expander("👀 معاينة سريعة للبطاقات"):
            rows = []
            for ln in card_lines:
                parts = ln.split("\t")
                if len(parts) >= 2:
                    rows.append({"Front": parts[0], "Back": parts[1]})
                else:
                    rows.append({"Front": ln, "Back": ""})
            st.dataframe(rows, width="stretch", hide_index=True)
