"""
Unit tests for configuration and models.
"""
import pytest
import os
from config import CONFIG, LANGUAGES, AppConfig
from models import CEFRQuestion, TestSession, QuestionType, TestState


class TestConfig:
    def test_languages_loaded(self):
        assert "en" in LANGUAGES
        assert "ru" in LANGUAGES

    def test_english_config(self):
        en = LANGUAGES["en"]
        assert en.code == "en"
        assert en.name == "English"
        assert en.voice == "en-US-AriaNeural"
        assert "A1" in en.cefr_labels

    def test_russian_config(self):
        ru = LANGUAGES["ru"]
        assert ru.code == "ru"
        assert ru.name == "Русский"
        assert ru.voice == "ru-RU-SvetlanaNeural"
        assert "A1" in ru.cefr_labels

    def test_app_config_defaults(self):
        assert CONFIG.gemini_model_primary == "gemini-3.5-flash"
        assert CONFIG.gemini_model_fallback == "gemini-2.5-flash"
        assert CONFIG.test_total_questions == 12
        assert CONFIG.test_start_difficulty == 3

    def test_api_key_from_env(self, monkeypatch):
        monkeypatch.setenv("GEMINI_API_KEY", "test-key-123")
        config = AppConfig()
        assert config.gemini_api_key == "test-key-123"

    def test_api_key_missing_raises(self, monkeypatch):
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        config = AppConfig()
        with pytest.raises(ValueError):
            _ = config.gemini_api_key


class TestModels:
    def test_question_creation(self):
        q = CEFRQuestion(
            id=1, level="A1", level_label="Beginner",
            type=QuestionType.CONVERSATION,
            question="Hello?", feedback="Good!", difficulty=1
        )
        assert q.id == 1
        assert q.difficulty == 1

    def test_question_to_dict(self):
        q = CEFRQuestion(1, "A1", "Beginner", QuestionType.CONVERSATION, "Q", "F", 1)
        d = q.to_dict()
        assert d["id"] == 1
        assert d["type"] == "conversation"

    def test_test_session_reset(self):
        ts = TestSession()
        ts.current_question = 5
        ts.user_answers = ["a", "b"]
        ts.reset()
        assert ts.current_question == 0
        assert ts.user_answers == []
        assert ts.state == TestState.IDLE

    def test_test_session_state_transitions(self):
        ts = TestSession()
        assert ts.state == TestState.IDLE
        ts.state = TestState.RUNNING
        assert ts.state == TestState.RUNNING
        ts.state = TestState.FINISHED
        assert ts.state == TestState.FINISHED
