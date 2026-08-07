"""
Unit tests for the CEFR test engine.
"""
import pytest
from models import CEFRQuestion, TestSession, QuestionType
from test_engine import TestEngine
from question_banks import get_question_bank


class TestEngineBasic:
    def setup_method(self):
        self.engine = TestEngine("en")
        self.session = TestSession()

    def test_find_next_question_basic(self):
        q = self.engine.find_next_question(self.session)
        assert q is not None
        assert q.difficulty == 3  # Start difficulty

    def test_find_next_question_exhaustion(self):
        # Ask all questions
        bank = get_question_bank("en")
        asked = set()
        for _ in range(len(bank) + 5):
            q = self.engine.find_next_question(self.session)
            if q is None:
                break
            asked.add(q.id)
            self.session.selected_questions.append(q)

        assert len(asked) <= len(bank)

    def test_evaluate_answer_strong(self):
        q = CEFRQuestion(1, "B1", "Intermediate", QuestionType.CONVERSATION,
                        "Test", "Feedback", 5)
        answer = "I would definitely agree because technology is very important."
        quality = self.engine.evaluate_answer(answer, q)
        assert quality == 1

    def test_evaluate_answer_weak(self):
        q = CEFRQuestion(1, "A1", "Beginner", QuestionType.CONVERSATION,
                        "Test", "Feedback", 1)
        answer = "hi"
        quality = self.engine.evaluate_answer(answer, q)
        assert quality == -1

    def test_evaluate_answer_medium(self):
        q = CEFRQuestion(1, "A2", "Elementary", QuestionType.CONVERSATION,
                        "Test", "Feedback", 3)
        answer = "I usually go to school."
        quality = self.engine.evaluate_answer(answer, q)
        assert quality == 0

    def test_adjust_difficulty_up(self):
        self.session.current_difficulty = 3
        self.engine.adjust_difficulty(self.session, 1)
        assert self.session.current_difficulty == 4

    def test_adjust_difficulty_down(self):
        self.session.current_difficulty = 3
        self.engine.adjust_difficulty(self.session, -1)
        assert self.session.current_difficulty == 2

    def test_adjust_difficulty_bounds(self):
        self.session.current_difficulty = 8
        self.engine.adjust_difficulty(self.session, 1)
        assert self.session.current_difficulty == 8  # Max cap

        self.session.current_difficulty = 1
        self.engine.adjust_difficulty(self.session, -1)
        assert self.session.current_difficulty == 1  # Min cap


class TestEngineRussian:
    def setup_method(self):
        self.engine = TestEngine("ru")
        self.session = TestSession()

    def test_russian_evaluate_strong(self):
        q = CEFRQuestion(1, "B1", "Средний", QuestionType.CONVERSATION,
                        "Test", "Feedback", 5)
        answer = "Я думаю, что это очень важно, потому что технологии изменили нашу жизнь."
        quality = self.engine.evaluate_answer(answer, q)
        assert quality == 1

    def test_russian_bank_loaded(self):
        bank = get_question_bank("ru")
        assert len(bank) == 20
        assert bank[0].level == "A1"
