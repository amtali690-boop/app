# 🌍 Polyglot AI — Language Learning App

A modular, production-ready language learning application built with **Streamlit**, **Google Gemini API**, and **Edge TTS**.

## ✨ Features

- **🌐 Multi-Language Support**: English 🇬🇧 & Russian 🇷🇺 (easily extensible)
- **🤖 AI Conversation**: Roleplay scenarios powered by Gemini 3.5 Flash
- **🎯 Adaptive CEFR Test**: 20-question bank with dynamic difficulty adjustment
- **🔊 Text-to-Speech**: Edge TTS with language-specific neural voices
- **📦 Anki Export**: Generate flashcard decks from chat history
- **🔍 Search & Edit**: Full chat management (search, edit, delete)
- **🎙️ Voice Library**: Manage and download all generated audio
- **⚙️ Modular Architecture**: Clean separation of concerns

## 🏗️ Architecture

```
polyglot-ai/
├── app.py              # Streamlit UI (main entry)
├── config.py           # Settings, languages, constants
├── models.py           # Dataclasses (Question, Result, etc.)
├── prompts.py          # System prompts per language
├── question_banks.py   # CEFR question banks
├── gemini_client.py    # Gemini API with retry + fallback
├── tts.py              # Edge TTS wrapper
├── test_engine.py      # Adaptive test logic
├── anki_export.py      # Anki deck generation
├── tests/              # Unit tests
│   ├── test_config.py
│   ├── test_engine.py
│   └── test_tts.py
├── .env                # API keys (not committed)
└── requirements.txt
```

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone <repo-url>
cd polyglot-ai
pip install -r requirements.txt
```

### 2. Configure API Key

```bash
cp .env.example .env
# Edit .env and add your Gemini API key:
# GEMINI_API_KEY=your_key_here
```

Get your key at [Google AI Studio](https://aistudio.google.com/app/apikey).

### 3. Run

```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

## 🧪 Running Tests

```bash
pytest tests/ -v
```

## 🔧 Adding a New Language

1. **Add language config** in `config.py`:
   ```python
   "fr": LanguageConfig(
       code="fr", name="Français", flag="🇫🇷",
       voice="fr-FR-DeniseNeural",
       ...
   )
   ```

2. **Add question bank** in `question_banks.py`:
   ```python
   "fr": [
       CEFRQuestion(1, "A1", "Débutant", ...),
       ...
   ]
   ```

3. **Add prompts** in `prompts.py`:
   ```python
   "fr": "Vous êtes un tuteur de français..."
   ```

4. Done! The UI auto-detects the new language.

## 📋 Model Fallback Strategy

The app uses a resilient fallback chain:

1. **Primary**: `gemini-3.5-flash` (fastest, latest)
2. **Fallback**: `gemini-2.5-flash` (stable, proven)
3. **Retry logic**: 3 attempts with exponential backoff
4. **Error handling**: Graceful degradation with user-friendly messages

## 📝 License

MIT License — free for personal and commercial use.
