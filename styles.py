# ==========================================
# styles.py — تنسيق CSS الخاص بالتطبيق فقط، منفصل عن أي منطق برمجي
# هوية بصرية v2: "بطاقة تقييم/شهادة لغة" بدل لوك الـ AI SaaS العام (سماوي+بنفسجي)
# ==========================================
import streamlit as st

# ثابتة (تُحسب مرة واحدة عند استيراد الوحدة، وليس مع كل rerun)
APP_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Tajawal:wght@400;500;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

    :root {
        --ink: #0A0E17;        /* خلفية الصفحة */
        --ink-2: #0F1524;      /* سطح ثانوي / سايدبار */
        --paper: #161D2E;      /* سطح البطاقات */
        --paper-text: #F3EFE6; /* نص العناوين (كريمي دافئ بدل أبيض بارد) */
        --gold: #D9A441;       /* اللون المميز الأساسي */
        --gold-dim: rgba(217, 164, 65, 0.14);
        --sage: #8FBF9F;       /* نجاح / مستوى محقق */
        --rust: #C97B5F;       /* خطأ / يحتاج مراجعة */
        --mist: #93A0B7;       /* نص ثانوي */
    }

    html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"],
    [data-testid="stMarkdownContainer"], .stChatMessage, .stButton>button,
    .stTextInput input, .stTextArea textarea, .stSelectbox, [data-testid="stMetricLabel"] {
        font-family: 'Tajawal', sans-serif !important;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, #131A2B 0%, var(--ink-2) 45%, var(--ink) 100%);
    }

    /* ===== بطاقة الترحيب — بتصميم رأسية شهادة رسمية ===== */
    .hero-card {
        position: relative;
        background:
            repeating-linear-gradient(135deg, rgba(217,164,65,0.035) 0px, rgba(217,164,65,0.035) 1px, transparent 1px, transparent 14px),
            linear-gradient(135deg, #131A2B 0%, var(--ink-2) 55%, var(--ink) 100%);
        border: 1px solid rgba(217, 164, 65, 0.28);
        border-radius: 16px;
        padding: 22px 28px;
        margin-bottom: 18px;
        box-shadow: 0 14px 34px rgba(0,0,0,0.45);
        overflow: hidden;
    }
    /* ختم زاوية صغير — نفس روح الشهادة الرسمية */
    .hero-card::after {
        content: '';
        position: absolute; top: 16px; inset-inline-end: 18px;
        width: 34px; height: 34px; border-radius: 50%;
        border: 1.5px solid rgba(217, 164, 65, 0.4);
        box-shadow: inset 0 0 0 5px rgba(217, 164, 65, 0.07);
    }
    .hero-title {
        font-family: 'Amiri', 'Tajawal', serif;
        font-size: 1.9rem; font-weight: 700;
        color: var(--paper-text);
        margin-bottom: 4px;
        letter-spacing: 0.01em;
    }
    .hero-sub {
        color: var(--mist); font-size: 0.92rem; margin-bottom: 14px;
    }

    .badge {
        display: inline-flex; align-items: center; gap: 6px;
        padding: 5px 12px; border-radius: 999px; font-size: 0.8rem; font-weight: 700;
        background: transparent; color: var(--gold);
        border: 1px solid rgba(217, 164, 65, 0.45);
        transition: transform 0.15s ease, background 0.15s ease;
    }
    .badge:hover { transform: translateY(-1px); background: var(--gold-dim); }

    /* ===== بطاقة التقييم — بشكل "تذكرة/كوبون نتيجة" مثقوبة الحواف ===== */
    .eval-card {
        position: relative;
        background: var(--paper);
        border: 1px solid rgba(217, 164, 65, 0.22);
        border-radius: 12px;
        padding: 14px 16px 12px 16px;
        margin: 4px 0 12px 0;
        font-size: 0.82rem;
        color: var(--mist);
    }
    .eval-scores {
        display: flex; align-items: center; gap: 14px; flex-wrap: wrap;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700; color: var(--gold);
        font-size: 0.76rem; letter-spacing: 0.02em;
        padding-bottom: 10px; margin-bottom: 10px;
        border-bottom: 1px dashed rgba(217, 164, 65, 0.35);
        position: relative;
    }
    /* "ثقوب" التذكرة على طرفي الخط المتقطع */
    .eval-scores::before, .eval-scores::after {
        content: ''; position: absolute; bottom: -7px;
        width: 12px; height: 12px; border-radius: 50%;
        background: var(--ink-2);
        border: 1px solid rgba(217, 164, 65, 0.3);
    }
    .eval-scores::before { left: -6px; }
    .eval-scores::after  { right: -6px; }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--ink-2) 0%, var(--ink) 100%);
        border-right: 1px solid rgba(217, 164, 65, 0.08);
    }
    .side-heading {
        font-size: 0.74rem; letter-spacing: 0.1em; text-transform: uppercase;
        color: var(--gold); font-weight: 700;
        margin: 18px 0 8px 0; padding-bottom: 6px;
        border-bottom: 1px solid rgba(217, 164, 65, 0.18);
    }

    .stButton>button, .stDownloadButton>button {
        border-radius: 10px; font-weight: 700;
        background: rgba(217, 164, 65, 0.06) !important;
        color: var(--paper-text) !important;
        border: 1px solid rgba(217, 164, 65, 0.35) !important;
        transition: transform 0.15s ease, background 0.15s ease, border-color 0.15s ease;
    }
    .stButton>button:hover, .stDownloadButton>button:hover {
        transform: translateY(-1px);
        background: rgba(217, 164, 65, 0.16) !important;
        border-color: rgba(217, 164, 65, 0.6) !important;
    }
    .stButton>button:active, .stDownloadButton>button:active { transform: translateY(0); }
    .stButton>button:focus-visible, .stDownloadButton>button:focus-visible {
        outline: 2px solid var(--gold); outline-offset: 2px;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 4px; border-bottom: 1px solid rgba(148,163,184,0.12);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0; padding: 9px 18px; font-weight: 700;
        color: var(--mist);
        transition: color 0.15s ease, background 0.15s ease;
    }
    .stTabs [aria-selected="true"] {
        background: var(--gold-dim);
        color: var(--gold) !important;
        box-shadow: inset 0 -2px 0 0 var(--gold);
    }

    [data-testid="stChatMessage"] {
        border-radius: 16px; padding: 8px 6px;
        border: 1px solid rgba(217, 164, 65, 0.10);
        background: rgba(255,255,255,0.025);
        margin-bottom: 8px;
        transition: background 0.15s ease, border-color 0.15s ease;
    }
    [data-testid="stChatMessage"]:hover {
        background: rgba(255,255,255,0.04);
        border-color: rgba(217, 164, 65, 0.22);
    }

    [data-testid="stChatInput"] {
        border-radius: 14px; border: 1px solid rgba(217, 164, 65, 0.3) !important;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 14px !important;
        border-color: rgba(217, 164, 65, 0.14) !important;
        transition: border-color 0.15s ease;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: rgba(217, 164, 65, 0.35) !important;
    }

    /* أرقام الإحصائيات — بخط Mono زي لوحة نتائج */
    [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
        color: var(--gold) !important; font-weight: 700 !important;
    }
    [data-testid="stMetricLabel"] { color: var(--mist) !important; }

    /* شريط التقدم — بذهبي بدل اللون الافتراضي (ملاحظة: selector داخلي لستريملت وقد يتغير بين النسخ) */
    div[data-testid="stProgress"] > div > div > div {
        background: linear-gradient(90deg, #B9862E, var(--gold)) !important;
    }

    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(217, 164, 65, 0.25); border-radius: 8px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(217, 164, 65, 0.4); }

    .typing-card {
        display: inline-flex; align-items: center; gap: 10px;
        background: rgba(217, 164, 65, 0.05); border: 1px solid rgba(217, 164, 65, 0.18);
        border-radius: 14px; padding: 10px 16px; color: var(--mist); font-size: 0.88rem; font-weight: 600;
    }
    .typing-dots { display: inline-flex; gap: 4px; }
    .typing-dots span {
        width: 6px; height: 6px; border-radius: 50%;
        background: var(--gold);
        animation: typing-bounce 1.2s infinite ease-in-out;
    }
    .typing-dots span:nth-child(2) { animation-delay: 0.15s; }
    .typing-dots span:nth-child(3) { animation-delay: 0.3s; }
    @keyframes typing-bounce {
        0%, 60%, 100% { transform: translateY(0); opacity: 0.5; }
        30% { transform: translateY(-5px); opacity: 1; }
    }

    /* إتاحة الحركة المخفّفة */
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.001ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.001ms !important;
        }
    }

    /* شاشات الموبايل الصغيرة */
    @media (max-width: 480px) {
        .hero-card { padding: 16px 18px; }
        .hero-title { font-size: 1.45rem; }
        .eval-scores { gap: 9px; font-size: 0.7rem; }
    }
</style>
"""


def inject_css():
    st.markdown(APP_CSS, unsafe_allow_html=True)
