# ==========================================
# ai_parser.py — تحليل واستخراج الوسوم الذكية من رد الـ AI
# ==========================================
import re


def parse_ai_tags(full_reply: str):
    """
    يفصل رد الـ AI الطبيعي عن الوسوم البرمجية:
    [EVAL|...] [CEFR:X] [MISTAKE|wrong|correct|explanation] [NEWWORD|word|type|meaning|example]
    """
    display_reply = full_reply
    eval_data = {}
    cefr = None
    mistake = None
    newword = None

    eval_match = re.search(r"\[EVAL\s*\|(.*?)\]", full_reply, re.DOTALL | re.IGNORECASE)
    if eval_match:
        eval_str = eval_match.group(1).replace('\n', '')
        display_reply = display_reply.replace(eval_match.group(0), "")
        for item in eval_str.split("|"):
            if ":" in item:
                k, v = item.split(":", 1)
                eval_data[k.strip()] = v.strip()

    cefr_match = re.search(r"\[CEFR\s*:\s*([A-Ca-c][12])\]", full_reply)
    if cefr_match:
        cefr = cefr_match.group(1).upper()
        display_reply = display_reply.replace(cefr_match.group(0), "")

    mistake_match = re.search(r"\[MISTAKE\s*\|(.*?)\]", full_reply, re.DOTALL | re.IGNORECASE)
    if mistake_match:
        parts = [p.strip() for p in mistake_match.group(1).split("|")]
        display_reply = display_reply.replace(mistake_match.group(0), "")
        if len(parts) >= 3 and parts[0].lower() not in ("none", "n/a", "-", ""):
            mistake = {"wrong": parts[0], "correct": parts[1], "explanation": parts[2]}

    newword_match = re.search(r"\[NEWWORD\s*\|(.*?)\]", full_reply, re.DOTALL | re.IGNORECASE)
    if newword_match:
        parts = [p.strip() for p in newword_match.group(1).split("|")]
        display_reply = display_reply.replace(newword_match.group(0), "")
        if len(parts) >= 4 and parts[0].lower() not in ("none", "n/a", "-", ""):
            newword = {"word": parts[0], "type": parts[1], "meaning": parts[2], "example": parts[3]}

    return display_reply.strip(), eval_data, cefr, mistake, newword
