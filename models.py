"""
Data models — dataclasses for type safety and clean architecture.
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict
from enum import Enum


class QuestionType(Enum):
    CONVERSATION = "conversation"
    SCENARIO = "scenario"
    IMAGE = "image"


class TestState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    FINISHED = "finished"


@dataclass
class CEFRQuestion:
    id: int
    level: str
    level_label: str
    type: QuestionType
    question: str
    feedback: str
    difficulty: int
    scenario_icon: Optional[str] = None
    scenario_title: Optional[str] = None
    scenario_desc: Optional[str] = None
    image_emoji: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "level": self.level,
            "levelLabel": self.level_label,
            "type": self.type.value,
            "question": self.question,
            "feedback": self.feedback,
            "difficulty": self.difficulty,
            "scenarioIcon": self.scenario_icon,
            "scenarioTitle": self.scenario_title,
            "scenarioDesc": self.scenario_desc,
            "imageEmoji": self.image_emoji,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CEFRQuestion":
        return cls(
            id=data["id"],
            level=data["level"],
            level_label=data["levelLabel"],
            type=QuestionType(data.get("type", "conversation")),
            question=data["question"],
            feedback=data["feedback"],
            difficulty=data["difficulty"],
            scenario_icon=data.get("scenarioIcon"),
            scenario_title=data.get("scenarioTitle"),
            scenario_desc=data.get("scenarioDesc"),
            image_emoji=data.get("imageEmoji"),
        )


@dataclass
class TestResult:
    level_code: str
    level_desc: str
    color: str
    bg_color: str
    emoji: str
    recommendation: str
    total_words: int
    grammar_score: int
    complexity: str
    test_duration_seconds: int
    max_difficulty_reached: int
    timestamp: str = field(default_factory=lambda: __import__('datetime').datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "level_code": self.level_code,
            "level_desc": self.level_desc,
            "total_words": self.total_words,
            "grammar_score": self.grammar_score,
            "complexity": self.complexity,
            "duration": self.test_duration_seconds,
            "max_difficulty": self.max_difficulty_reached,
            "timestamp": self.timestamp,
        }


@dataclass
class ChatMessage:
    role: str  # "user" | "assistant"
    content: str
    timestamp: str = field(default_factory=lambda: __import__('datetime').datetime.now().isoformat())
    edited: bool = False
    original_content: Optional[str] = None


@dataclass
class VoiceFile:
    key: str
    bytes: bytes
    text_preview: str
    language: str
    timestamp: str


@dataclass
class TestSession:
    current_question: int = 0
    user_answers: List[str] = field(default_factory=list)
    selected_questions: List[CEFRQuestion] = field(default_factory=list)
    current_difficulty: int = 3
    start_time: Optional[float] = None
    state: TestState = TestState.IDLE

    def reset(self):
        self.current_question = 0
        self.user_answers = []
        self.selected_questions = []
        self.current_difficulty = 3
        self.start_time = None
        self.state = TestState.IDLE

    def to_dict(self) -> dict:
        return {
            "current_question": self.current_question,
            "user_answers": self.user_answers,
            "selected_questions": [q.to_dict() for q in self.selected_questions],
            "current_difficulty": self.current_difficulty,
            "start_time": self.start_time,
            "state": self.state.value,
  }
