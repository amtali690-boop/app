"""
Configuration module — centralized settings, no hardcoded secrets.
"""
import os
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class LanguageConfig:
    code: str
    name: str
    flag: str
    voice: str
    voice_alt: str
    cefr_labels: Dict[str, str]
    ui_labels: Dict[str, str]
    scenario_labels: Dict[str, str]


@dataclass(frozen=True)
class AppConfig:
    gemini_model_primary: str = "gemini-3.5-flash"
    gemini_model_fallback: str = "gemini-2.5-flash"
    gemini_max_retries: int = 3
    gemini_retry_delay: float = 1.5
    gemini_temperature: float = 0.8
    gemini_timeout: int = 30

    tts_default_speed: str = "+0%"
    tts_volume: str = "+0%"

    test_total_questions: int = 12
    test_start_difficulty: int = 3
    test_adaptive_step: int = 1
    test_min_difficulty: int = 1
    test_max_difficulty: int = 8

    autosave_enabled: bool = True
    max_chat_history: int = 200
    max_voice_files: int = 50
    max_test_history: int = 20

    @property
    def gemini_api_key(self) -> str:
        key = os.getenv("GEMINI_API_KEY", "")
        if not key:
            raise ValueError(
                "GEMINI_API_KEY not set.\n"
                "Create a .env file with: GEMINI_API_KEY=your_key_here\n"
                "Or set it as an environment variable."
            )
        return key


# Language definitions
LANGUAGES: Dict[str, LanguageConfig] = {
    "en": LanguageConfig(
        code="en",
        name="English",
        flag="🇬🇧",
        voice="en-US-AriaNeural",
        voice_alt="en-US-GuyNeural",
        cefr_labels={
            "A1": "Beginner", "A1+": "Beginner+", "A2": "Elementary",
            "A2+": "Elementary+", "B1": "Intermediate", "B1+": "Intermediate+",
            "B2": "Upper-Intermediate", "B2+": "Upper-Intermediate+", "C1": "Advanced"
        },
        ui_labels={
            "app_title": "Polyglot AI",
            "tagline": "Learn by speaking",
            "select_lang": "🌐 Target Language",
            "chat_tab": "💬 Conversation",
            "test_tab": "🎯 Level Test",
            "settings_tab": "⚙️ Settings",
            "voice_tab": "🎙️ Voice Library",
            "start_test": "▶️ Start Test",
            "your_answer": "Type your answer...",
            "send": "➤ Send",
            "listening": "Listening...",
            "test_progress": "Test Progress",
            "question": "Question",
            "level": "Level",
            "type_conversation": "Conversation",
            "type_scenario": "Scenario",
            "type_image": "Image",
            "result_title": "Your Level is",
            "words_used": "Words Used",
            "test_time": "Test Time",
            "grammar_accuracy": "Grammar Accuracy",
            "complexity": "Complexity",
            "recommendation": "💡 Recommendation",
            "restart": "🔄 Restart Test",
            "export_anki": "📦 Export Anki Deck",
            "search_chat": "🔍 Search conversation...",
            "autosave_on": "Autosave: ON",
            "scenario_select": "Choose a scenario",
            "clear_chat": "🗑️ Clear Chat",
            "free_chat": "Free Chat",
            "roleplay": "Roleplay Scenario",
            "no_voice_files": "No voice files yet. Start a conversation to generate TTS audio!",
            "voice_settings": "🔊 Voice Settings",
            "test_history": "📚 Test History",
            "data_mgmt": "⚠️ Data Management",
            "clear_all": "🗑️ Clear All History",
            "last_save": "Last autosave",
            "tts_voice": "TTS Voice",
            "error_no_key": "🔴 Gemini API key not configured. Set GEMINI_API_KEY in your .env file.",
            "error_model": "⚠️ Model error. Retrying with fallback...",
            "loading": "Loading...",
        },
        scenario_labels={
            "restaurant": "🍽️ At the Restaurant",
            "airport": "✈️ At the Airport",
            "interview": "💼 Job Interview",
            "shopping": "🛒 Shopping",
            "doctor": "🏥 At the Doctor",
            "hotel": "🏨 Hotel Check-in",
            "meeting": "📊 Business Meeting",
            "date": "💕 First Date"
        }
    ),
    "ru": LanguageConfig(
        code="ru",
        name="Русский",
        flag="🇷🇺",
        voice="ru-RU-SvetlanaNeural",
        voice_alt="ru-RU-DmitryNeural",
        cefr_labels={
            "A1": "Начинающий", "A1+": "Начинающий+", "A2": "Элементарный",
            "A2+": "Элементарный+", "B1": "Средний", "B1+": "Средний+",
            "B2": "Выше среднего", "B2+": "Выше среднего+", "C1": "Продвинутый"
        },
        ui_labels={
            "app_title": "Polyglot AI",
            "tagline": "Учись, говоря",
            "select_lang": "🌐 Целевой язык",
            "chat_tab": "💬 Диалог",
            "test_tab": "🎯 Тест уровня",
            "settings_tab": "⚙️ Настройки",
            "voice_tab": "🎙️ Библиотека голосов",
            "start_test": "▶️ Начать тест",
            "your_answer": "Введите ответ...",
            "send": "➤ Отправить",
            "listening": "Слушаю...",
            "test_progress": "Прогресс теста",
            "question": "Вопрос",
            "level": "Уровень",
            "type_conversation": "Диалог",
            "type_scenario": "Сценарий",
            "type_image": "Картинка",
            "result_title": "Ваш уровень",
            "words_used": "Слов использовано",
            "test_time": "Время теста",
            "grammar_accuracy": "Точность грамматики",
            "complexity": "Сложность",
            "recommendation": "💡 Рекомендация",
            "restart": "🔄 Пройти снова",
            "export_anki": "📦 Экспорт Anki",
            "search_chat": "🔍 Поиск по диалогу...",
            "autosave_on": "Автосохранение: ВКЛ",
            "scenario_select": "Выберите сценарий",
            "clear_chat": "🗑️ Очистить чат",
            "free_chat": "Свободный чат",
            "roleplay": "Ролевая игра",
            "no_voice_files": "Голосовых файлов пока нет. Начните диалог для генерации аудио!",
            "voice_settings": "🔊 Настройки голоса",
            "test_history": "📚 История тестов",
            "data_mgmt": "⚠️ Управление данными",
            "clear_all": "🗑️ Очистить всю историю",
            "last_save": "Последнее сохранение",
            "tts_voice": "Голос TTS",
            "error_no_key": "🔴 Ключ API Gemini не настроен. Установите GEMINI_API_KEY в файле .env.",
            "error_model": "⚠️ Ошибка модели. Повторная попытка с резервной моделью...",
            "loading": "Загрузка...",
        },
        scenario_labels={
            "restaurant": "🍽️ В ресторане",
            "airport": "✈️ В аэропорту",
            "interview": "💼 Собеседование",
            "shopping": "🛒 Покупки",
            "doctor": "🏥 У врача",
            "hotel": "🏨 Регистрация в отеле",
            "meeting": "📊 Деловая встреча",
            "date": "💕 Первое свидание"
        }
    )
}

# Global config instance
CONFIG = AppConfig()
