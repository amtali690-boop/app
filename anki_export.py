"""
Anki deck export — generates .apkg or fallback .txt files.
"""
import hashlib
import tempfile
from datetime import datetime
from typing import Tuple, Optional

from models import ChatMessage


def create_anki_deck(chat_history: list, language: str) -> Tuple[Optional[bytes], str]:
    """
    Create Anki deck from chat history.

    Returns:
        (bytes, filename) or (None, "") on failure
    """
    try:
        import genanki

        deck_name = f"Polyglot_{language.upper()}_{datetime.now().strftime('%Y%m%d')}"
        model_id = abs(hash(deck_name)) % 100000000
        deck_id = model_id + 1

        model = genanki.Model(
            model_id,
            'Polyglot Model',
            fields=[
                {'name': 'Front'},
                {'name': 'Back'},
                {'name': 'Tags'},
            ],
            templates=[{
                'name': 'Card 1',
                'qfmt': '{{Front}}',
                'afmt': '{{FrontSide}}<hr id="answer">{{Back}}',
            }],
            css="""
            .card { font-family: Arial; font-size: 20px; text-align: center; }
            """
        )

        deck = genanki.Deck(deck_id, deck_name)

        for i in range(0, len(chat_history) - 1, 2):
            if i + 1 < len(chat_history):
                user_msg = str(chat_history[i])[:200]
                bot_msg = str(chat_history[i + 1])[:500]

                note = genanki.Note(
                    model=model,
                    fields=[user_msg, bot_msg, f"polyglot_{language}"],
                )
                deck.add_note(note)

        with tempfile.NamedTemporaryFile(suffix=".apkg", delete=False) as f:
            genanki.Package(deck).write_to_file(f.name)
            f.seek(0)
            with open(f.name, 'rb') as rf:
                return rf.read(), f"{deck_name}.apkg"

    except ImportError:
        # Fallback to text export
        text = f"# Polyglot Flashcards ({language.upper()})\n\n"
        for i in range(0, len(chat_history) - 1, 2):
            if i + 1 < len(chat_history):
                text += f"Q: {chat_history[i]}\n"
                text += f"A: {chat_history[i+1]}\n\n---\n\n"
        return text.encode('utf-8'), f"polyglot_{language}_flashcards.txt"

    except Exception as e:
        return None, f"error_{e}.txt"
