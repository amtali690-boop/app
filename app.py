"""
🌍 Polyglot AI v8.1 — Modular Streamlit Language Learning App
Supports: English 🇬🇧 | Русский 🇷🇺
Architecture: config → models → prompts → question_banks → gemini_client → tts → test_engine → anki_export → app
"""

import streamlit as st
import time
from datetime import datetime

# Local imports
from config import CONFIG, LANGUAGES
from models import TestSession, TestState, ChatMessage, VoiceFile, QuestionType
from prompts import get_system_prompt, get_scenario_prompt
from question_banks import get_question_bank
from gemini_client import get_client
from tts import text_to_speech
from test_engine import TestEngine
from anki_export import create_anki_deck


# ======================
# SESSION STATE
# ======================
def init_session_state():
    """Initialize all session state variables safely."""
    defaults = {
        "target_language": "en",
        "chat_history": [],
        "test_history": [],
        "voice_files": {},
        "test_session": TestSession(),
        "current_scenario": "restaurant",
        "search_query": "",
        "chat_mode": "free",  # "free" or "scenario"
        "gemini_ready": False,
    }

    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

    # Initialize Gemini client (with error handling)
    if not st.session_state.gemini_ready:
        try:
            get_client()
            st.session_state.gemini_ready = True
        except ValueError as e:
            st.session_state.gemini_error = str(e)


init_session_state()


# ======================
# UI HELPERS
# ======================
def ui(key: str) -> str:
    """Get UI label for current language."""
    lang = st.session_state.target_language
    return LANGUAGES[lang].ui_labels.get(key, key)


def render_sidebar() -> str:
    """Render sidebar and return selected tab."""
    with st.sidebar:
        st.title(f"🌍 {ui('app_title')}")
        st.caption(ui('tagline'))
        st.divider()

        # Language selector
        lang_opts = {"en": "🇬🇧 English", "ru": "🇷🇺 Русский"}
        current = st.session_state.target_language
        new_lang = st.selectbox(
            ui('select_lang'),
            options=list(lang_opts.keys()),
            format_func=lambda x: lang_opts[x],
            index=list(lang_opts.keys()).index(current)
        )

        if new_lang != current:
            st.session_state.target_language = new_lang
            st.session_state.chat_history = []
            st.session_state.test_session = TestSession()
            st.rerun()

        st.divider()

        # Navigation
        tab = st.radio(
            "Navigation",
            [ui('chat_tab'), ui('test_tab'), ui('voice_tab'), ui('settings_tab')],
            label_visibility="collapsed"
        )

        st.divider()

        # Stats
        st.subheader("📊 Stats")
        st.metric("Messages", len(st.session_state.chat_history))
        st.metric("Tests Taken", len(st.session_state.test_history))
        st.metric("Voice Files", len(st.session_state.voice_files))

        # API status
        if st.session_state.gemini_ready:
            st.success("✅ Gemini API Ready")
        else:
            st.error(ui('error_no_key'))

        return tab


# ======================
# CHAT TAB
# ======================
def render_chat_tab():
    st.header(ui('chat_tab'))

    # Mode selector
    mode = st.radio(
        "Mode",
        [ui('free_chat'), ui('roleplay')],
        horizontal=True
    )

    st.session_state.chat_mode = "free" if mode == ui('free_chat') else "scenario"

    # Scenario selector
    if st.session_state.chat_mode == "scenario":
        scenarios = LANGUAGES[st.session_state.target_language].scenario_labels
        scenario = st.selectbox(
            ui('scenario_select'),
            list(scenarios.keys()),
            format_func=lambda x: scenarios[x]
        )
        st.session_state.current_scenario = scenario

    # Search
    search = st.text_input(ui('search_chat'), value=st.session_state.search_query)
    st.session_state.search_query = search

    # Clear button
    if st.button(ui('clear_chat'), use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

    # Chat display
    chat_container = st.container(height=400)
    with chat_container:
        history = st.session_state.chat_history

        # Filter by search
        if search:
            filtered = [msg for msg in history if search.lower() in msg.lower()]
        else:
            filtered = history

        for i, msg_text in enumerate(filtered):
            idx = history.index(msg_text) if msg_text in history else -1
            is_user = idx % 2 == 0 if idx >= 0 else True

            if is_user:
                with st.chat_message("user"):
                    st.markdown(msg_text)
                    c1, c2 = st.columns([1, 10])
                    with c1:
                        if st.button("🗑️", key=f"del_{idx}"):
                            # Remove user message and bot response
                            if idx < len(history):
                                history.pop(idx)
                            if idx < len(history):
                                history.pop(idx)
                            st.rerun()
            else:
                with st.chat_message("assistant"):
                    st.markdown(msg_text)
                    c1, c2 = st.columns([1, 10])
                    with c1:
                        if st.button("🔊", key=f"tts_{idx}"):
                            audio = text_to_speech(msg_text, st.session_state.target_language)
                            if audio:
                                st.audio(audio, format="audio/mp3")
                                # Store
                                key = f"tts_{hash(msg_text) % 100000}_{idx}"
                                st.session_state.voice_files[key] = audio

    # Input
    user_input = st.chat_input(ui('your_answer'))

    if user_input and st.session_state.gemini_ready:
        # Add user message
        st.session_state.chat_history.append(user_input)

        # Build system prompt
        lang = st.session_state.target_language
        if st.session_state.chat_mode == "scenario":
            sys_prompt = get_scenario_prompt(st.session_state.current_scenario, lang)
            sys_prompt += "\n\n" + get_system_prompt(lang)
        else:
            sys_prompt = get_system_prompt(lang)

        # Build conversation context
        messages = []
        for i, msg in enumerate(st.session_state.chat_history[-10:]):
            role = "user" if i % 2 == 0 else "assistant"
            messages.append({"role": role, "content": msg})

        # Generate response
        with st.spinner(ui('loading')):
            response = get_client().chat(
                messages=messages,
                system_instruction=sys_prompt,
                temperature=CONFIG.gemini_temperature
            )

        st.session_state.chat_history.append(response)
        st.rerun()

    elif user_input and not st.session_state.gemini_ready:
        st.error(ui('error_no_key'))

    # Export Anki
    if st.session_state.chat_history:
        if st.button(ui('export_anki'), use_container_width=True):
            data, filename = create_anki_deck(
                st.session_state.chat_history,
                st.session_state.target_language
            )
            if data:
                st.download_button("📥 Download", data, filename, use_container_width=True)


# ======================
# TEST TAB
# ======================
def render_test_tab():
    st.header(ui('test_tab'))

    session = st.session_state.test_session
    engine = TestEngine(st.session_state.target_language)

    # State: IDLE
    if session.state == TestState.IDLE:
        st.info(f"🎯 {ui('test_tab')}: {CONFIG.test_total_questions} adaptive questions")
        if st.button(ui('start_test'), type="primary", use_container_width=True):
            session.reset()
            session.state = TestState.RUNNING
            session.start_time = time.time()
            st.rerun()
        return

    # State: FINISHED
    if session.state == TestState.FINISHED:
        analysis = engine.analyze_results(session)
        result = engine.determine_level(analysis)

        # Fill analysis data into result
        result.total_words = analysis['total_words']
        result.grammar_score = analysis['grammar_score']
        result.complexity = analysis['complexity']
        result.max_difficulty_reached = analysis['max_difficulty']
        result.test_duration_seconds = int(time.time() - session.start_time) if session.start_time else 0

        # Save to history
        st.session_state.test_history.append(result.to_dict())

        # Display
        mins, secs = divmod(result.test_duration_seconds, 60)

        col1, col2, col3 = st.columns(3)
        col1.metric(ui('result_title'), result.level_code)
        col2.metric(ui('words_used'), result.total_words)
        col3.metric(ui('test_time'), f"{mins}:{secs:02d}")

        st.markdown(f"### {result.emoji} {result.level_desc}")
        st.markdown(f"**{ui('recommendation')}:** {result.recommendation}")

        st.progress(result.grammar_score / 100, text=f"{ui('grammar_accuracy')}: {result.grammar_score}%")

        if st.button(ui('restart'), use_container_width=True):
            session.reset()
            st.rerun()
        return

    # State: RUNNING
    progress = session.current_question / CONFIG.test_total_questions
    st.progress(progress, text=f"{ui('test_progress')}: {session.current_question} / {CONFIG.test_total_questions}")

    # Check if finished
    if session.current_question >= CONFIG.test_total_questions:
        session.state = TestState.FINISHED
        st.rerun()

    # Get next question if needed
    if session.current_question >= len(session.selected_questions):
        q = engine.find_next_question(session)
        if q is None:
            session.state = TestState.FINISHED
            st.rerun()
        session.selected_questions.append(q)

    q = session.selected_questions[session.current_question]

    # Display question
    level_class = "hard" if q.difficulty >= 6 else ("medium" if q.difficulty >= 4 else "")
    type_emoji = {QuestionType.SCENARIO: "🎭", QuestionType.IMAGE: "🖼️", QuestionType.CONVERSATION: "💬"}
    type_names = {QuestionType.SCENARIO: ui('type_scenario'), QuestionType.IMAGE: ui('type_image'), QuestionType.CONVERSATION: ui('type_conversation')}

    st.markdown(f"""
    <div style="background:#1e293b;padding:12px;border-radius:12px;margin-bottom:12px;border:1px solid #334155;">
        <span style="background:#0ea5e9;color:white;padding:2px 8px;border-radius:10px;font-size:12px;">{ui('question')} {session.current_question + 1}</span>
        <span style="background:{'rgba(245,158,11,0.2)' if level_class=='medium' else ('rgba(239,68,68,0.2)' if level_class=='hard' else '#334155')};color:{'#fbbf24' if level_class=='medium' else ('#f87171' if level_class=='hard' else '#94a3b8')};padding:2px 8px;border-radius:10px;font-size:12px;margin:0 6px;">{q.level}</span>
        <span style="background:rgba(99,102,241,0.2);color:#a78bfa;padding:2px 8px;border-radius:10px;font-size:12px;">{type_emoji.get(q.type, '💬')} {type_names.get(q.type, 'Chat')}</span>
    </div>
    """, unsafe_allow_html=True)

    # Extra content for scenario/image
    if q.type == QuestionType.SCENARIO:
        st.info(f"{q.scenario_icon or '🎭'} **{q.scenario_title or ''}**\n\n_{q.scenario_desc or ''}_")
    elif q.type == QuestionType.IMAGE:
        st.markdown(f"<div style='font-size:60px;text-align:center;padding:20px;'>{q.image_emoji or '🖼️'}</div>", unsafe_allow_html=True)

    st.markdown(q.question)

    # Answer input
    answer = st.text_area(ui('your_answer'), key=f"test_ans_{session.current_question}", height=100)

    if st.button(ui('send'), type="primary", use_container_width=True):
        if answer.strip():
            session.user_answers.append(answer.strip())

            # Evaluate and adjust
            quality = engine.evaluate_answer(answer.strip(), q)
            engine.adjust_difficulty(session, quality)

            # Show feedback
            st.success(q.feedback)
            time.sleep(1.5)

            session.current_question += 1
            st.rerun()


# ======================
# VOICE TAB
# ======================
def render_voice_tab():
    st.header(ui('voice_tab'))

    files = st.session_state.voice_files
    if not files:
        st.info(ui('no_voice_files'))
        return

    for key, audio_bytes in list(files.items())[-20:]:
        with st.container():
            col1, col2, col3 = st.columns([4, 1, 1])
            with col1:
                st.write(f"🎵 {key}")
            with col2:
                st.audio(audio_bytes, format="audio/mp3")
            with col3:
                st.download_button("⬇️", audio_bytes, f"{key}.mp3", key=f"dl_{key}")


# ======================
# SETTINGS TAB
# ======================
def render_settings_tab():
    st.header(ui('settings_tab'))

    # Voice settings
    st.subheader(ui('voice_settings'))
    lang = st.session_state.target_language
    voice_opts = [LANGUAGES[lang].voice, LANGUAGES[lang].voice_alt]
    st.selectbox(ui('tts_voice'), voice_opts, index=0)

    st.divider()

    # Test history
    st.subheader(ui('test_history'))
    for test in st.session_state.test_history[-5:]:
        with st.expander(f"📝 {test.get('level_code', '?')} — {test.get('timestamp', '')[:10]}"):
            st.json(test)

    st.divider()

    # Data management
    st.subheader(ui('data_mgmt'))
    if st.button(ui('clear_all'), type="secondary"):
        st.session_state.chat_history = []
        st.session_state.test_history = []
        st.session_state.voice_files = {}
        st.session_state.test_session = TestSession()
        st.success("Cleared!")
        st.rerun()


# ======================
# MAIN
# ======================
def main():
    tab = render_sidebar()

    if ui('chat_tab') in tab:
        render_chat_tab()
    elif ui('test_tab') in tab:
        render_test_tab()
    elif ui('voice_tab') in tab:
        render_voice_tab()
    elif ui('settings_tab') in tab:
        render_settings_tab()


if __name__ == "__main__":
    main()
