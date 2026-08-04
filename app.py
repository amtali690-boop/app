# ==========================================
# AI English Conversation Partner — v5 (Ultra Pro+) — UI Refresh
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
# تحديثات واجهة إضافية (UI Refresh) — بدون أي تغيير على المنطق/الصوت/الـ API:
# - تصميم عام أهدأ وأكثر احترافية (خلفية، بطاقات، تدرجات لونية خفيفة).
# - رأس صفحة (Hero header) مع شارة توضح السيناريو الحالي والموديل الحالي.
# - شريط جانبي مقسّم لأقسام واضحة بعناوين وأيقونات وفواصل.
# - فقاعات محادثة مخصصة بمظهر بطاقة، وشارة "AI يتكلم..." أثناء التفكير.
# - "مشغل صوت" (Voice Player) بشكل بطاقة مميزة حول عنصر st.audio بدل ما يطلع عاري.
# - مؤشر تقدّم اختبار المستوى بشكل شريط ملوّن متدرّج مع نسبة مئوية.
# - قسم Anki بشكل بطاقة نتيجة مرتبة مع عداد للكلمات المستخرجة.
# - نفس كل الدوال والمتغيرات ونفس منطق الـ API والصوت والملفات المؤقتة تماماً كما هي.
#
# التحديثات السابقة (v4):
# 1) اختبار تحديد المستوى يسأل 10 أسئلة كحد أدنى، وقد يمتد لـ 15 سؤال لضمان الدقة.
# 2) تحسين سيناريو القواعد ليركز على الأفعال والأسماء العامة وبناء جمل الترجمة.
# 3) إضافة خيار (Autoplay Toggle) للتحكم بتشغيل الصوت تلقائياً أو يدوياً.
# 4) تحسين استخراج كلمات Anki لتركز على الكلمات التي أخطأ فيها المستخدم.
# ==========================================

import os
import time
import uuid
import shutil
import hashlib
import tempfile
import asyncio

import streamlit as st
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
        .badge.green {
            background: rgba(52, 211, 153, 0.12);
            color: #34d399;
            border: 1px solid rgba(52, 211, 153, 0.3);
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
        .voice-player-card {
            margin-top: 6px;
            padding: 10px 14px;
            border-radius: 12px;
            background: rgba(56, 189, 248, 0.06);
            border: 1px solid rgba(56, 189, 248, 0.18);
        }
        .voice-player-label {
            font-size: 0.78rem;
            color: #38bdf8;
            font-weight: 700;
            margin-bottom: 4px;
            display: flex;
            align-items: center;
            gap: 6px;
        }
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
    </style>
    """,
    unsafe_allow_html=True,
)

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
        "anki_cards", "session_audio_dir",
    ]:
        st.session_state.pop(k, None)
    st.rerun()

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


def render_voice_player(audio_path: str, autoplay: bool):
    """يعرض عنصر الصوت داخل بطاقة مصغّرة بدل ما يطلع عارياً — شكل فقط."""
    st.markdown(
        '<div class="voice-player-card"><div class="voice-player-label">🎧 Voice reply</div>',
        unsafe_allow_html=True,
    )
    st.audio(audio_path, format="audio/mp3", autoplay=autoplay)
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 4. رأس الصفحة (Hero) + الاتصال بـ Gemini وإدارة الجلسة
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

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
last_index = len(messages) - 1
for i, msg in enumerate(messages):
    avatar = "🤖" if msg["role"] == "assistant" else "🧑"
    with st.chat_message(msg["role"], avatar=avatar):
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
        with st.spinner("🤖 AI يفكّر بالرد..."):
            try:
                response = st.session_state.chat_session.send_message(text)
                reply = response.text
            except Exception as e:
                st.error(f"⚠️ تعذر الحصول على رد. حاول إرسال رسالتك مرة أخرى.\n\n`{e}`")
                return  # لا نسجّل رداً فاشلاً كأنه رد حقيقي؛ رسالتك تبقى فوق لإعادة المحاولة

        st.write(reply)

        audio_path = None
        try:
            audio_path = speak(reply, voice_id)
            render_voice_player(audio_path, autoplay_audio)
            st.session_state.last_played_audio = audio_path
        except Exception:
            st.caption("🔇 تعذر توليد الصوت هالمرة، لكن يمكنك متابعة المحادثة نصياً.")

    st.session_state.messages.append(
        {"role": "assistant", "content": reply, "audio": audio_path}
    )

# ==========================================
# 7. إدخال صوتي (مايك)
# ==========================================
st.markdown('<div class="side-heading">🎤 سجّل رسالتك</div>', unsafe_allow_html=True)
audio_value = st.audio_input("🎤 Record your message (Speak clearly in English)")

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

# ==========================================
# 8. إدخال نصي
# ==========================================
typed = st.chat_input("...or type your message here")
if typed:
    handle_user_message(typed)

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
        card_count = len([ln for ln in st.session_state.anki_cards.splitlines() if ln.strip()])
        st.markdown(
            f"""
            <div class="anki-result-card">
                <b>✅ تم التجهيز بنجاح!</b><br/>
                <span style="color:#94a3b8;">تم استخراج {card_count} بطاقة جاهزة للتحميل.</span>
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
