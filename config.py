# ==========================================
# config.py — الإعدادات الثابتة، البرومبتات، وقوائم السيناريوهات/الأصوات
# ==========================================

CEFR_ORDER = ["A1", "A2", "B1", "B2", "C1", "C2"]
CEFR_NUM = {lvl: i + 1 for i, lvl in enumerate(CEFR_ORDER)}

DEFAULT_MODEL = "gemini-3.6-flash"  # // تم التعديل: gemini-2.5-flash لم يعد متاحاً للمستخدمين الجدد (404)؛ هذا هو الموديل المستقر الحالي (يدعم الصوت أيضاً لخاصية تفريغ التسجيلات)

SCENARIO_ICONS = {
    "Casual Friend (Everyday Chat)": "☕",
    "Supermarket Customer (Work Practice)": "🛒",
    "Grammar & Translation Coach": "📘",
    "Speaking Placement Test (10+ Questions)": "📝",
}

PROMPTS = {
    "Casual Friend (Everyday Chat)": (
        "Act like a warm, casual friend having an everyday conversation. Talk about daily life, "
        "hobbies, opinions, and casual topics. Keep the tone relaxed and natural, ask follow-up "
        "questions, and encourage the user to speak freely."
    ),
    "Supermarket Customer (Work Practice)": (
        "Roleplay as a customer or cashier in a supermarket so the user can practice real-life "
        "shopping and customer-service English. Stay in character, use realistic scenarios "
        "(checkout, asking for products, prices, complaints), and gently guide the conversation "
        "back to the roleplay if the user goes off-topic."
    ),
    "Grammar & Translation Coach": (
        "Act as a strict but supportive grammar and translation coach. Help the user translate "
        "sentences between Arabic and English, explain grammar rules clearly and briefly, and "
        "correct mistakes with short explanations of WHY something is wrong."
    ),
    "Speaking Placement Test (10+ Questions)": (
        "Conduct a structured English speaking placement test. Ask one question at a time, "
        "starting easy and gradually increasing difficulty, covering topics like self-introduction, "
        "daily routine, opinions, hypothetical situations, and past experiences. Ask at least "
        "10-15 questions total, then give a final overall level estimate (CEFR) at the end."
    ),
}

VOICE_MAP = {
    "Aria — US Female": "en-US-AriaNeural",
    "Guy — US Male": "en-US-GuyNeural",
    "Sonia — UK Female": "en-GB-SoniaNeural",
    "Ryan — UK Male": "en-GB-RyanNeural",
}
