# ==========================================
# AI English Conversation Partner — v2
# التحديثات عن النسخة القديمة:
#  1) الموديل القديم gemini-1.5-flash متوقف بالكامل (404) -> استبدلناه بموديل حالي
#  2) مكتبة google-generativeai صارت deprecated -> استبدلناها بـ google-genai الموحدة
#  3) إضافة إدخال صوتي (مايك): تحكي، وجوجل جيميناي يحول صوتك لنص ويكمل المحادثة عادي
#  4) اختيار الصوت (ذكر/أنثى، أمريكي/بريطاني)
#  5) تحميل بطاقات Anki كملف .txt مباشرة بدل النسخ اليدوي
#  6) رسائل خطأ واضحة بدل ما التطبيق ينهار بصمت
# ==========================================

import os
import time
import tempfile
import asyncio

import streamlit as st
import edge_tts
from google import genai
from google.genai import types

# ==========================================
# 1. إعدادات الصفحة
# ==========================================
st.set_page_config(page_title="AI English Partner", page_icon="🎙️", layout="centered")

# ملاحظة صيانة: جوجل بتوقف الموديلات القديمة بشكل دوري (متل ما صار مع gemini-1.5).
# إذا ظهر خطأ "model not found" بالمستقبل، بس بدّل الاسم هون على أي موديل حالي
# (شوف القائمة المحدثة على ai.google.dev/gemini-api/docs/models):
MODEL_NAME = "gemini-3.5-flash"

st.title("🎙️ AI English Conversation Partner")
st.caption("مارس الإنجليزي كتابة أو بصوتك، بأصوات واقعية، واستخرج مفرداتك لـ Anki بنقرة زر.")

# ==========================================
# 2. الشريط الجانبي: الإعدادات
# ==========================================
st.sidebar.header("⚙️ Configuration")

saved_key = os.environ.get("GEMINI_API_KEY", "")
api_key = st.sidebar.text_input(
    "Gemini API Key:",
    type="password",
    value=saved_key,
    help="مفتاح مجاني من aistudio.google.com/apikey",
)

scenario = st.sidebar.selectbox(
    "Choose Conversation Scenario:",
    [
        "Casual Friend (Everyday Chat)",
        "Supermarket Customer (Work Practice)",
        "Grammar & Speaking Coach",
    ],
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

PROMPTS = {
    "Casual Friend (Everyday Chat)": (
        "Act like a close friend having an easygoing conversation. Ask open-ended "
        "questions about daily life. Speak ONLY in English. Keep answers short and natural."
    ),
    "Supermarket Customer (Work Practice)": (
        "Act like an English-speaking customer in a supermarket asking for items, "
        "prices, or recommendations. Be polite, natural, and stick strictly to English."
    ),
    "Grammar & Speaking Coach": (
        "Act like a supportive tutor. Respond to the user's message, but if they make a "
        "grammar or word-choice mistake, gently correct it first in 1 short sentence "
        "before continuing the conversation naturally in English."
    ),
}

if st.sidebar.button("🔄 New Conversation"):
    for k in ["messages", "chat_session", "current_scenario", "last_audio_id"]:
        st.session_state.pop(k, None)
    st.rerun()

# ==========================================
# 3. تحويل النص لصوت بشري (Edge TTS)
# ==========================================
async def _synthesize(text: str, voice: str, out_path: str):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(out_path)


def speak(text: str, voice: str) -> str:
    out_path = os.path.join(tempfile.gettempdir(), f"tts_{int(time.time() * 1000)}.mp3")
    asyncio.run(_synthesize(text, voice, out_path))
    return out_path


# ==========================================
# 4. الاتصال بـ Gemini + إدارة الجلسة
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if not api_key:
    st.info("👈 ادخل الـ Gemini API Key من الشريط الجانبي عشان تبدأ.")
    st.stop()

try:
    client = genai.Client(api_key=api_key)
    if (
        "chat_session" not in st.session_state
        or st.session_state.get("current_scenario") != scenario
    ):
        st.session_state.chat_session = client.chats.create(
            model=MODEL_NAME,
            config=types.GenerateContentConfig(
                system_instruction=PROMPTS[scenario],
                temperature=0.8,
            ),
        )
        st.session_state.current_scenario = scenario
        st.session_state.messages = []
except Exception as e:
    st.error(f"⚠️ ما قدرنا نتصل بـ Gemini. تأكد إنو الـ API Key صحيح.\n\n`{e}`")
    st.stop()

# ==========================================
# 5. عرض المحادثة السابقة
# ==========================================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("audio") and os.path.exists(msg["audio"]):
            st.audio(msg["audio"], format="audio/mp3")

# ==========================================
# 6. معالجة أي رسالة جديدة (من الكتابة أو الصوت)
# ==========================================
def handle_user_message(text: str):
    st.session_state.messages.append({"role": "user", "content": text})
    with st.chat_message("user"):
        st.write(text)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = st.session_state.chat_session.send_message(text)
                reply = response.text
            except Exception as e:
                reply = f"⚠️ صار خطأ بالرد: {e}"
        st.write(reply)

        audio_path = None
        try:
            audio_path = speak(reply, voice_id)
            st.audio(audio_path, format="audio/mp3", autoplay=True)
        except Exception:
            st.caption("🔇 تعذر توليد الصوت هالمرة (النص موجود فوق).")

    st.session_state.messages.append(
        {"role": "assistant", "content": reply, "audio": audio_path}
    )


# ==========================================
# 7. إدخال صوتي (مايك) — سجل، ورح نحول صوتك لنص تلقائياً
# ==========================================
audio_value = st.audio_input("🎤 Record your message (English)")

if audio_value is not None:
    audio_bytes = audio_value.getvalue()
    audio_id = hash(audio_bytes)
    # حراسة ضد إعادة معالجة نفس التسجيل بكل rerun من Streamlit
    if st.session_state.get("last_audio_id") != audio_id:
        st.session_state.last_audio_id = audio_id
        with st.spinner("جاري تحويل صوتك لنص..."):
            try:
                transcript = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=[
                        types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav"),
                        "Transcribe exactly what is said in this audio. Output ONLY "
                        "the transcription, with no extra words or explanation.",
                    ],
                )
                spoken_text = transcript.text.strip()
            except Exception as e:
                spoken_text = None
                st.error(f"⚠️ ما قدرنا نفهم الصوت: {e}")
        if spoken_text:
            handle_user_message(spoken_text)

# ==========================================
# 8. إدخال نصي
# ==========================================
typed = st.chat_input("...or type your message")
if typed:
    handle_user_message(typed)

# ==========================================
# 9. مستخرج بطاقات Anki التلقائي
# ==========================================
st.divider()
if st.button("📇 Extract Anki Flashcards from Session"):
    if not st.session_state.messages:
        st.warning("Start a conversation first!")
    else:
        with st.spinner("Analyzing conversation for key vocabulary..."):
            conversation_text = "\n".join(
                f"{m['role']}: {m['content']}" for m in st.session_state.messages
            )
            anki_prompt = f"""Analyze this English-practice conversation and extract 3-7 useful
English words, phrasal verbs, or expressions the learner encountered (skip very
basic words they clearly already know).
Format the output strictly as a tab-separated list ready for Anki import, one card per line:
Front (Word/Phrase) [TAB] Back (short Arabic meaning + one English example sentence)

Conversation:
{conversation_text}"""
            try:
                anki_result = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=anki_prompt,
                    config=types.GenerateContentConfig(temperature=0.3),
                )
                st.subheader("Your Anki Cards:")
                st.code(anki_result.text, language="text")
                st.download_button(
                    "⬇️ Download .txt (استوردها مباشرة لـ Anki)",
                    data=anki_result.text,
                    file_name=f"anki_cards_{int(time.time())}.txt",
                    mime="text/plain",
                )
            except Exception as e:
                st.error(f"⚠️ صار خطأ: {e}")
