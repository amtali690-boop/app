# ==========================================
# app.py — AI English Conversation Partner v10 (نقطة الدخول الرئيسية)
# ==========================================

import os
import sqlite3
from datetime import datetime

import streamlit as st
from google import genai
from google.genai import types

# استيراد ملف التنسيقات الخارجي (عندك مسبقاً)
from styles import inject_css

# ملفات المشروع المقسّمة
from config import CEFR_NUM, DEFAULT_MODEL, SCENARIO_ICONS, PROMPTS, VOICE_MAP
from database import (
    DB_PATH,
    init_db,
    set_profile,
    get_profile,
    update_stat,
    get_stat,
    log_mistake,
    log_eval,
    create_session,
    log_message_to_session,
    get_all_sessions,
    load_session_messages,
    group_sessions_by_date,
    get_due_reviews,
    save_vocab_quick,
)
from audio_player import speak, render_voice_player, render_typing_indicator
from ai_parser import parse_ai_tags

init_db()

if "session_audio_dir" not in st.session_state:
    import uuid
    st.session_state.session_audio_dir = os.path.join(os.path.dirname(DB_PATH), uuid.uuid4().hex)
    os.makedirs(st.session_state.session_audio_dir, exist_ok=True)

AUDIO_DIR = st.session_state.session_audio_dir

# ==========================================
# 1. إعدادات الصفحة والتصميم (UI & CSS)
# ==========================================
st.set_page_config(page_title="AI English Elite Platform", page_icon="🎙️", layout="wide")

# تفعيل ملف الـ CSS الخارجي
inject_css()

# ==========================================
# 2. الشريط الجانبي
# ==========================================
st.sidebar.markdown("### 🎙️ AI English Elite")
st.sidebar.caption("منصة تدريب لغات متطورة")

st.sidebar.markdown('<div class="side-heading">🔑 API & Setup</div>', unsafe_allow_html=True)

api_key = st.sidebar.text_input("Gemini API Key:", value=os.environ.get("GEMINI_API_KEY", ""), type="password")

if not api_key:
    st.sidebar.warning("⚠️ يرجى إدخال مفتاح API لتعمل المحادثة.")

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
voice_id = VOICE_MAP[voice_label]

autoplay_audio = st.sidebar.checkbox("🔊 Autoplay AI Voice", value=True)
voice_only_mode = st.sidebar.checkbox("🎙️ وضع المكالمة الصوتية (Voice-Only Mode)", value=False)

st.sidebar.markdown('<div class="side-heading">⚡ صرامة التصحيح</div>', unsafe_allow_html=True)
strictness = st.sidebar.selectbox(
    "Correction Level:",
    ["تصحيح جميع الأخطاء بدقة", "الأخطاء الكبيرة فقط (لتشجيع الطلاقة)", "بدون تصحيح (محادثة حرة تماماً)"],
)

with st.sidebar.expander("⚙️ إعدادات الموديل"):
    model_name = st.text_input("Gemini Model:", value=DEFAULT_MODEL)

st.sidebar.markdown('<div class="side-heading">🧹 إدارة الجلسة</div>', unsafe_allow_html=True)
if st.sidebar.button("🔄 جلسة جديدة تماماً", use_container_width=True):
    try:
        for f in os.listdir(AUDIO_DIR):
            fp = os.path.join(AUDIO_DIR, f)
            if os.path.isfile(fp):
                os.remove(fp)
    except Exception:
        pass
    for k in list(st.session_state.keys()):
        if k not in ["session_audio_dir", "audio_input_key"]:
            del st.session_state[k]
    st.rerun()

# ==========================================
# 3. بناء التبويبات (Tabs)
# ==========================================
tab_chat, tab_vocab, tab_memory, tab_progress, tab_history = st.tabs([
    "💬 غرفة المحادثة",
    "📓 دفتر المفردات",
    "🧠 ذاكرة AI والملف الشخصي",
    "📈 تحليل الأداء",
    "🕘 سجل المحادثات",
])

# ------------------------------------------
# تبويب 3: الذاكرة والملف الشخصي
# ------------------------------------------
with tab_memory:
    st.subheader("🧠 ذاكرة المستخدم والملف الشخصي")
    st.caption("هذه المعلومات تُرسل تلقائياً للذكاء الاصطناعي لكي يتذكرك دائماً.")

    with st.form("profile_form"):
        p_name = st.text_input("اسمك الكريم:", value=get_profile("name", ""))
        LEVEL_OPTIONS = ["A1 (مبتدئ)", "A2 (مبتدئ متقدم)", "B1 (متوسط)", "B2 (متوسط متقدم)", "C1 (متقدم)", "C2 (محترف)"]
        saved_level = get_profile("level", "B1 (متوسط)")
        default_level_index = LEVEL_OPTIONS.index(saved_level) if saved_level in LEVEL_OPTIONS else 2
        p_level = st.selectbox("مستواك في الإنجليزية:", LEVEL_OPTIONS, index=default_level_index)
        p_goals = st.text_input("هدف التعلم (مثلاً: IELTS، عمل، محادثة):", value=get_profile("goals", ""))
        p_notes = st.text_area("ملاحظات خاصة للـ AI:", value=get_profile("notes", ""))

        if st.form_submit_button("💾 حفظ الملف الشخصي"):
            set_profile("name", p_name)
            set_profile("level", p_level)
            set_profile("goals", p_goals)
            set_profile("notes", p_notes)
            st.success("✅ تم التحديث بنجاح!")

# ------------------------------------------
# تبويب 2: دفتر المفردات
# ------------------------------------------
with tab_vocab:
    st.subheader("📓 دفتر المفردات الذكي")
    st.caption("احفظ الكلمات الجديدة، صنفها، وراجعها.")

    # مراجعة ذكية (Smart Review)
    due = get_due_reviews()
    if any(due.values()):
        with st.container(border=True):
            st.markdown("#### 🔁 مراجعة اليوم")
            for label, words in due.items():
                if words:
                    st.markdown(f"**{label}:** {'، '.join(words)}")

    with st.expander("➕ إضافة كلمة جديدة"):
        with st.form("add_vocab"):
            col1, col2 = st.columns(2)
            new_word = col1.text_input("الكلمة / التعبير:")
            new_type = col2.selectbox("التصنيف:", ["Verb (فعل)", "Noun (اسم)", "Phrase (تعبير)", "Adjective (صفة)", "Idiom (مصطلح)", "Phrasal Verb", "Collocation"])
            new_meaning = st.text_input("المعنى بالعربي:")
            new_example = st.text_input("مثال إنجليزي:")
            if st.form_submit_button("حفظ الكلمة"):
                if new_word:
                    try:
                        with sqlite3.connect(DB_PATH, timeout=10) as conn:
                            c = conn.cursor()
                            c.execute(
                                """INSERT OR REPLACE INTO vocab_notebook
                                   (word, word_type, meaning_ar, example, status, created_at) VALUES (?, ?, ?, ?, ?, ?)""",
                                (new_word.strip(), new_type, new_meaning.strip(), new_example.strip(), "Needs Review", datetime.now().isoformat()),
                            )
                            conn.commit()
                        st.success(f"تم حفظ ({new_word}) بنجاح!")
                        update_stat("total_vocab_words", 1)
                    except Exception as e:
                        st.error(f"خطأ: {e}")
                else:
                    st.warning("يرجى كتابة الكلمة.")

    try:
        with sqlite3.connect(DB_PATH, timeout=10) as conn:
            c = conn.cursor()
            c.execute("SELECT id, word, word_type, meaning_ar, example, status FROM vocab_notebook ORDER BY id DESC")
            vocab_rows = c.fetchall()

        if vocab_rows:
            search_q = st.text_input("🔍 ابحث:", "")
            search_q_lower = search_q.lower()
            filtered = [r for r in vocab_rows if search_q_lower in r[1].lower() or search_q_lower in r[3].lower()]
            st.markdown(f"**إجمالي الكلمات:** {len(vocab_rows)}")
            for row in filtered:
                r_id, r_word, r_type, r_meaning, r_example, r_status = row
                with st.container(border=True):
                    cols = st.columns([3, 2, 2, 1, 1])
                    cols[0].markdown(f"**{r_word}** ({r_type})<br><span style='color:#94a3b8;font-size:0.85rem;'>{r_meaning}</span>", unsafe_allow_html=True)
                    cols[1].markdown(f"<span style='color:#cbd5e1;font-size:0.85rem;'>Ex: {r_example}</span>", unsafe_allow_html=True)
                    status_color = "#34d399" if r_status == "Learned" else "#f87171"
                    cols[2].markdown(f"<span style='color:{status_color};font-weight:700;'>{r_status}</span>", unsafe_allow_html=True)
                    if cols[3].button("🔄 تبديل", key=f"toggle_v_{r_id}"):
                        new_st = "Learned" if r_status == "Needs Review" else "Needs Review"
                        with sqlite3.connect(DB_PATH, timeout=10) as update_conn:
                            cu = update_conn.cursor()
                            cu.execute("UPDATE vocab_notebook SET status = ? WHERE id = ?", (new_st, r_id))
                            update_conn.commit()
                        st.rerun()
                    if cols[4].button("🗑️", key=f"delete_v_{r_id}"):
                        with sqlite3.connect(DB_PATH, timeout=10) as del_conn:
                            cd = del_conn.cursor()
                            cd.execute("DELETE FROM vocab_notebook WHERE id = ?", (r_id,))
                            del_conn.commit()
                        st.rerun()
        else:
            st.info("دفتر المفردات فارغ.")
    except Exception:
        pass

# ------------------------------------------
# تبويب 4: تحليل الأداء
# ------------------------------------------
with tab_progress:
    st.subheader("📈 لوحة تحليل الأداء")

    c1, c2, c3 = st.columns(3)
    c1.metric("💬 إجمالي الرسائل", get_stat("total_messages"))
    c2.metric("📓 مفردات بالدفتر", get_stat("total_vocab_words"))
    c3.metric("📚 كلمات متفاعل معها", get_stat("total_words"))

    st.markdown("---")

    try:
        with sqlite3.connect(DB_PATH, timeout=10) as conn:
            c = conn.cursor()
            c.execute("SELECT grammar, vocab, natural, fluency, cefr FROM eval_log ORDER BY id DESC LIMIT 50")
            eval_rows = c.fetchall()
    except Exception:
        eval_rows = []

    if eval_rows:
        def _avg(idx):
            vals = [r[idx] for r in eval_rows if r[idx] is not None]
            return sum(vals) / len(vals) if vals else 0.0

        st.markdown("#### 🎯 متوسط آخر 50 رسالة")
        for label, val in [
            ("Grammar (القواعد)", _avg(0)),
            ("Vocabulary (المفردات)", _avg(1)),
            ("Naturalness (الطبيعية)", _avg(2)),
            ("Fluency (الطلاقة)", _avg(3)),
        ]:
            st.markdown(f"**{label}** — {val:.1f}/10")
            st.progress(min(val / 10, 1.0))

        cefr_vals = [CEFR_NUM.get(r[4]) for r in eval_rows if r[4] in CEFR_NUM]
        if cefr_vals:
            st.markdown("#### 📊 تطور مستوى CEFR (الأحدث على اليمين)")
            st.line_chart(list(reversed(cefr_vals)))
            st.caption("المقياس: 1=A1, 2=A2, 3=B1, 4=B2, 5=C1, 6=C2")
    else:
        st.info("لسا ما في بيانات كافية — كمل احكي وبتظهر هون لوحة تحليل تلقائياً 📊")

    st.markdown("---")
    st.markdown("#### 🔁 أخطاؤك الأكثر تكراراً")
    try:
        with sqlite3.connect(DB_PATH, timeout=10) as conn:
            c = conn.cursor()
            c.execute(
                """SELECT wrong_text, correct_text, COUNT(*) as cnt
                   FROM mistakes_log GROUP BY wrong_text, correct_text
                   ORDER BY cnt DESC LIMIT 8"""
            )
            mistake_rows = c.fetchall()
    except Exception:
        mistake_rows = []

    if mistake_rows:
        for wrong, correct, cnt in mistake_rows:
            st.markdown(
                f"- ❌ *{wrong}* → ✅ **{correct}** <span style='color:#94a3b8;font-size:0.8rem;'>(تكررت {cnt} مرة)</span>",
                unsafe_allow_html=True,
            )
    else:
        st.caption("ما في أخطاء مسجلة لهلأ — ممتاز! 🎉")

# ------------------------------------------
# تبويب 5: سجل المحادثات
# ------------------------------------------
with tab_history:
    st.subheader("🕘 سجل محادثاتك")
    st.caption("محادثاتك السابقة مجمّعة حسب التاريخ. اضغط استئناف لتحميلها في غرفة المحادثة.")

    sessions = get_all_sessions()
    if not sessions:
        st.info("ما في محادثات محفوظة بعد. ابدأ الحكي بتبويب 💬 وح تنسجل هون تلقائياً.")
    else:
        groups = group_sessions_by_date(sessions)
        for label, items in groups.items():
            if not items:
                continue
            st.markdown(f"#### {label}")
            for sid, scenario_name, title, created in items:
                with st.container(border=True):
                    cc1, cc2 = st.columns([4, 1])
                    try:
                        created_fmt = datetime.fromisoformat(created).strftime("%Y-%m-%d %H:%M")
                    except Exception:
                        created_fmt = created
                    cc1.markdown(
                        f"**{SCENARIO_ICONS.get(scenario_name, '💬')} {title or scenario_name}**  \n"
                        f"<span style='color:#94a3b8;font-size:0.8rem;'>{created_fmt}</span>",
                        unsafe_allow_html=True,
                    )
                    if cc2.button("🔁 استئناف", key=f"resume_{sid}"):
                        loaded = load_session_messages(sid)
                        st.session_state.messages = loaded
                        st.session_state.current_session_id = sid
                        st.session_state.current_scenario = scenario_name
                        st.session_state.last_played_audio = None
                        st.success("تم تحميل المحادثة — روح لتبويب 💬 غرفة المحادثة.")
                        st.rerun()

# ------------------------------------------
# تبويب 1: غرفة المحادثة الذكية
# ------------------------------------------
with tab_chat:
    if not api_key:
        st.warning("👈 يرجى إدخال مفتاح Gemini API Key في الشريط الجانبي لبدء المحادثة.")
    else:
        mem_name = get_profile("name", "الطالب")
        mem_level = get_profile("level", "B1 (متوسط)")
        mem_goals = get_profile("goals", "محادثة عامة")
        mem_notes = get_profile("notes", "")

        # برومبت النظام: idioms/phrasal verbs/collocations/نطق + تصحيح طبيعي داخل الحوار + وسوم منظمة لاستخراج البيانات آلياً
        SYSTEM_PROMPT = f"""
        You are an elite, warm English conversation coach — never a robotic grammar checker.
        Talk the way a skilled, encouraging native-speaker tutor would: natural, contractions,
        follow-up questions, occasional humor when it fits.

        User Profile:
        - Name: {mem_name}
        - CEFR Level: {mem_level}
        - Goals: {mem_goals}
        - Notes: {mem_notes}
        - Correction Strictness: {strictness}

        Scenario Instruction: {PROMPTS.get(scenario, PROMPTS['Casual Friend (Everyday Chat)'])}

        TEACHING STYLE (follow all of these):
        1. Match vocabulary/sentence complexity to {mem_level}, but push slightly above it (i+1 level).
        2. When natural, weave in ONE idiom, phrasal verb, or collocation per response — never forced.
           The first time you use it, add a brief Arabic gloss in parentheses.
        3. Correct mistakes conversationally by recasting the sentence naturally inside your reply
           (not like a red-pen teacher), unless the strictness setting says otherwise.
        4. If a word is commonly mispronounced by Arabic speakers, add a short phonetic tip in Arabic.
        5. Never sound robotic or like a checklist.

        MANDATORY OUTPUT FORMAT — after your natural reply, ALWAYS append these bookkeeping tags,
        each on its own line (the user's app parses and hides these, so always include all four,
        exactly in this order, even if some values are "none"):

        [EVAL|Grammar:X/10|Vocab:X/10|Natural:X/10|Fluency:X/10|Correction: short tip in Arabic+English, or "ممتاز!" if none]
        [CEFR:X] — your best-guess CEFR level (A1, A2, B1, B2, C1, or C2) of the user's LAST message specifically.
        [MISTAKE|wrong phrase or none|correct phrase or none|one-line explanation in Arabic or none]
        [NEWWORD|word/phrase or none|type: Verb/Noun/Phrase/Idiom/Phrasal Verb/Collocation or none|Arabic meaning or none|example sentence or none]

        Only fill MISTAKE if the user made a real, notable error this turn.
        Only fill NEWWORD if there's a genuinely useful new item worth saving from this exchange —
        otherwise write "none" for every field in that tag.
        """

        def sync_gemini_history(client_instance, messages_list):
            try:
                history_parts = []
                last_role = None
                for m in messages_list:
                    role = "user" if m["role"] == "user" else "model"
                    if role == last_role and history_parts:
                        history_parts[-1].parts[0].text += f"\n\n{m['content']}"
                    else:
                        history_parts.append(types.Content(role=role, parts=[types.Part.from_text(text=m["content"])]))
                    last_role = role
                st.session_state.chat_session = client_instance.chats.create(
                    model=model_name,
                    config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT, temperature=0.7),
                    history=history_parts,
                )
            except Exception as e:
                st.error(f"Error Syncing: {e}")

        client = None
        try:
            client = genai.Client(api_key=api_key)
            if "chat_session" not in st.session_state or st.session_state.get("current_scenario") != scenario or st.session_state.get("current_model") != model_name:
                st.session_state.current_scenario = scenario
                st.session_state.current_model = model_name
                st.session_state.messages = []
                st.session_state.test_question_count = 0
                st.session_state.last_played_audio = None
                st.session_state.current_session_id = create_session(scenario)
                sync_gemini_history(client, [])

                if scenario == "Speaking Placement Test (10+ Questions)":
                    welcome_msg = f"Welcome {mem_name} to the English Speaking Placement Test. Let's begin! Question 1: Could you introduce yourself?"
                    audio_path = speak(welcome_msg, voice_id, AUDIO_DIR)
                    st.session_state.messages.append({"role": "assistant", "content": welcome_msg, "audio": audio_path})
                    log_message_to_session(st.session_state.current_session_id, "assistant", welcome_msg)
                    sync_gemini_history(client, st.session_state.messages)
                    update_stat("total_messages", 1)
        except Exception as e:
            st.error(f"⚠️ خطأ بالاتصال بالـ API: `{e}`")

        st.markdown(f"""
            <div class="hero-card">
                <div class="hero-title">🎙️ أهلاً بك يا {mem_name or 'صديقي'}!</div>
                <div class="hero-sub">المستوى: {mem_level} | الهدف: {mem_goals}</div>
                <div style="display:flex; gap:10px; flex-wrap:wrap;">
                    <span class="badge">{SCENARIO_ICONS.get(scenario, '💬')} {scenario}</span>
                    <span class="badge" style="background:rgba(167,139,250,0.12); color:#a78bfa;">🔊 {voice_label}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if scenario == "Speaking Placement Test (10+ Questions)":
            answered = st.session_state.get("test_question_count", 0)
            pct = min(answered / 10, 1.0)
            st.progress(pct, text=f"📝 تم الإجابة على {answered} سؤال من أصل 10-15")

        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "audio_input_key" not in st.session_state:
            st.session_state.audio_input_key = 0

        messages = st.session_state.messages
        if not messages:
            st.markdown("""
                <div style="text-align:center; padding:30px; border:1px dashed rgba(148,163,184,0.25); border-radius:16px; color:#94a3b8; margin-bottom:12px;">
                    <div style="font-size:2rem; margin-bottom:8px;">🎙️</div>
                    <b>ابدأ مكالمتك أو محادثتك الآن!</b>
                </div>
            """, unsafe_allow_html=True)

        last_index = len(messages) - 1
        for i, msg in enumerate(messages):
            avatar = "🤖" if msg["role"] == "assistant" else "🧑"
            with st.chat_message(msg["role"], avatar=avatar):
                if msg.get("eval"):
                    ev = msg["eval"]
                    cefr_badge = ""
                    if msg.get("cefr"):
                        cefr_badge = f"<span class='badge' style='background:rgba(52,211,153,0.14);color:#34d399;margin-inline-start:6px;'>CEFR: {msg['cefr']}</span>"
                    st.markdown(f"""
                        <div class="eval-card">
                            <div class="eval-scores">
                                <span>Grammar: {ev.get('Grammar','-')}</span>
                                <span>Vocab: {ev.get('Vocab','-')}</span>
                                <span>Natural: {ev.get('Natural','-')}</span>
                                <span>Fluency: {ev.get('Fluency','-')}</span>
                                {cefr_badge}
                            </div>
                            <div><b>التصحيح:</b> {ev.get('Correction','ممتاز!')}</div>
                        </div>
                    """, unsafe_allow_html=True)

                st.write(msg["content"])

                audio_path = msg.get("audio")
                if audio_path:
                    is_fresh = (i == last_index) and (audio_path != st.session_state.get("last_played_audio"))
                    render_voice_player(audio_path, autoplay_audio and is_fresh)
                    if is_fresh:
                        st.session_state.last_played_audio = audio_path

                if msg.get("explanation"):
                    st.info(f"💡 {msg['explanation']}")

                if msg.get("slow_audio"):
                    st.caption("🐢 نطق بطيء:")
                    render_voice_player(msg["slow_audio"], False)

                # صف الأزرار (شرح / نطق بطيء / حفظ كلمة / حذف)
                if msg["role"] == "assistant":
                    nw = msg.get("newword")
                    has_savable_word = bool(nw and nw.get("word") and nw["word"].strip().lower() not in ("none", ""))
                    btn_cols = st.columns(4 if has_savable_word else 3)

                    if btn_cols[0].button("🧠 اشرح", key=f"explain_{i}"):
                        if client and st.session_state.get("chat_session"):
                            with st.spinner("جاري الشرح..."):
                                try:
                                    explain_resp = st.session_state.chat_session.send_message(
                                        "Explain briefly in simple Arabic (max 4 lines, no tags) why your "
                                        "previous response/correction was right, and why the user's sentence "
                                        "needed it if it did."
                                    )
                                    st.session_state.messages[i]["explanation"] = explain_resp.text.strip()
                                except Exception as e:
                                    st.error(f"⚠️ تعذر الشرح: {e}")
                        st.rerun()

                    if btn_cols[1].button("🔁 بطيء", key=f"slow_{i}"):
                        with st.spinner("جاري توليد النطق البطيء..."):
                            slow_path = speak(msg["content"], voice_id, AUDIO_DIR, rate="-30%")
                            st.session_state.messages[i]["slow_audio"] = slow_path
                        st.rerun()

                    col_idx = 2
                    if has_savable_word:
                        label = f"💾 {nw['word'][:14]}"
                        if btn_cols[2].button(label, key=f"savew_{i}"):
                            save_vocab_quick(nw)
                            st.success(f"تم حفظ '{nw['word']}' بدفتر المفردات!")
                        col_idx = 3

                    if btn_cols[col_idx].button("🗑️", key=f"del_{i}"):
                        deleted_audio = st.session_state.messages[i].get("audio")
                        st.session_state.messages.pop(i)
                        if deleted_audio and os.path.exists(deleted_audio):
                            try:
                                os.remove(deleted_audio)
                            except Exception:
                                pass
                        if client:
                            sync_gemini_history(client, st.session_state.messages)
                        st.rerun()
                else:
                    if st.button("🗑️ حذف", key=f"del_{i}"):
                        st.session_state.messages.pop(i)
                        if client:
                            sync_gemini_history(client, st.session_state.messages)
                        st.rerun()

        st.markdown("---")
        if voice_only_mode:
            st.info("🎙️ وضع المكالمة الصوتية مفعل.")

        audio_value = st.audio_input("🎤 سجل صوتك هنا", key=f"audio_recorder_{st.session_state.audio_input_key}")

        typed_text = None
        if not voice_only_mode:
            typed_text = st.chat_input("...أو اكتب رسالتك هنا")

        user_text = None
        is_audio_input = False

        if audio_value is not None and len(audio_value.getvalue()) > 0:
            audio_bytes = audio_value.getvalue()
            import hashlib
            audio_id = hashlib.sha256(audio_bytes).hexdigest()
            if st.session_state.get("last_audio_id") != audio_id:
                st.session_state.last_audio_id = audio_id
                with st.spinner("🎧 جاري معالجة الصوت..."):
                    if not client:
                        st.error("⚠️ لا يوجد اتصال فعّال بالـ API لمعالجة الصوت.")
                    else:
                        try:
                            transcript = client.models.generate_content(
                                model=model_name,
                                contents=[types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav"), "Transcribe exactly what is said."],
                            )
                            if transcript.text:
                                user_text = transcript.text.strip()
                                is_audio_input = True
                        except Exception as e:
                            st.error(f"⚠️ خطأ: {e}")
        elif typed_text:
            user_text = typed_text

        if user_text:
            st.session_state.messages.append({"role": "user", "content": user_text})
            log_message_to_session(st.session_state.get("current_session_id"), "user", user_text)
            update_stat("total_messages", 1)
            update_stat("total_words", len(user_text.split()))

            if scenario == "Speaking Placement Test (10+ Questions)":
                st.session_state.test_question_count = st.session_state.get("test_question_count", 0) + 1

            with st.chat_message("user", avatar="🧑"):
                st.write(user_text)

            with st.chat_message("assistant", avatar="🤖"):
                typing_slot = st.empty()
                render_typing_indicator(typing_slot)
                try:
                    response = st.session_state.chat_session.send_message(user_text)
                    full_reply = response.text
                except Exception as e:
                    typing_slot.empty()
                    st.error(f"⚠️ تعذر الحصول على رد: {e}")
                    st.session_state.messages.pop()
                    st.stop()
                typing_slot.empty()

                display_reply, eval_data, cefr, mistake, newword = parse_ai_tags(full_reply)

                if eval_data:
                    log_eval(eval_data, cefr)
                    cefr_badge = f"<span class='badge' style='background:rgba(52,211,153,0.14);color:#34d399;margin-inline-start:6px;'>CEFR: {cefr}</span>" if cefr else ""
                    st.markdown(f"""
                        <div class="eval-card">
                            <div class="eval-scores">
                                <span>Grammar: {eval_data.get('Grammar','-')}</span>
                                <span>Vocab: {eval_data.get('Vocab','-')}</span>
                                <span>Natural: {eval_data.get('Natural','-')}</span>
                                <span>Fluency: {eval_data.get('Fluency','-')}</span>
                                {cefr_badge}
                            </div>
                            <div><b>التصحيح:</b> {eval_data.get('Correction','ممتاز!')}</div>
                        </div>
                    """, unsafe_allow_html=True)

                if mistake:
                    log_mistake(mistake["wrong"], mistake["correct"], mistake["explanation"])

                st.write(display_reply)

                audio_path = None
                try:
                    with st.spinner("🔊 جاري توليد الصوت..."):
                        audio_path = speak(display_reply, voice_id, AUDIO_DIR)
                    render_voice_player(audio_path, autoplay_audio)
                    st.session_state.last_played_audio = audio_path
                except Exception:
                    pass

            st.session_state.messages.append({
                "role": "assistant",
                "content": display_reply,
                "audio": audio_path,
                "eval": eval_data,
                "cefr": cefr,
                "newword": newword,
            })
            log_message_to_session(st.session_state.get("current_session_id"), "assistant", display_reply)
            update_stat("total_messages", 1)
            update_stat("total_words", len(display_reply.split()))

            if is_audio_input:
                st.session_state.audio_input_key += 1
                st.rerun()
