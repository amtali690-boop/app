# ==========================================
# styles.py — تنسيق CSS الخاص بالتطبيق فقط، منفصل عن أي منطق برمجي
# هوية بصرية v3 (عصرية): "استوديو تسجيل صوتي" — القياس بالمستوى (Level Meter)
# بدل هوية "الشهادة/التذكرة" السابقة. اللون والشكل مبنيان على عالم التطبيق
# الحقيقي: محادثة صوتية + تقييم مستوى CEFR + تصحيح أخطاء + مفردات جديدة.
# ==========================================
import streamlit as st

# ثابتة (تُحسب مرة واحدة عند استيراد الوحدة، وليس مع كل rerun)
APP_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=El+Messiri:wght@400;500;600;700&family=Tajawal:wght@300;400;500;700;800&family=IBM+Plex+Mono:wght@500;600;700&display=swap');

    :root {
        --ink: #0B0D12;         /* خلفية الصفحة — أسود استوديو بارد */
        --ink-2: #10131A;       /* سطح ثانوي / سايدبار */
        --panel: #171A22;       /* سطح البطاقات */
        --panel-raised: #1E222C;/* سطح مرتفع عند الـ hover */
        --paper: #ECEEF3;       /* نص العناوين */
        --mist: #838B9B;        /* نص ثانوي */
        --line: rgba(255,255,255,0.07);

        /* ألوان "مقياس المستوى" (VU meter) — مأخوذة من عالم معدّات الصوت نفسه */
        --meter-green: #48C78E;   /* اللون الأساسي: تقدّم / نجاح / الحالة الطبيعية */
        --meter-amber: #E8A33D;   /* تنبيه: مستوى CEFR / يحتاج مراجعة */
        --meter-red:   #E2523F;  /* نادر ومقصود: الأخطاء فقط — تماماً كمنطقة "peak" الحمراء بمقياس صوت حقيقي */

        --green-dim: rgba(72, 199, 142, 0.14);
        --amber-dim: rgba(232, 163, 61, 0.14);
        --red-dim:   rgba(226, 82, 63, 0.14);

        --font-display: 'El Messiri', 'Tajawal', sans-serif;
        --font-body: 'Tajawal', sans-serif;
        --font-mono: 'IBM Plex Mono', monospace;
    }

    html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"],
    [data-testid="stMarkdownContainer"], .stChatMessage, .stButton>button,
    .stTextInput input, .stTextArea textarea, .stSelectbox, [data-testid="stMetricLabel"] {
        font-family: var(--font-body) !important;
    }

    /* عناوين الأقسام بكل التبويبات تأخذ خط العرض المميز — يوحّد الهوية بلا حاجة لتغيير الكود */
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3 {
        font-family: var(--font-display) !important;
        letter-spacing: -0.01em;
    }

    ::selection { background: var(--green-dim); color: var(--paper); }

    .stApp {
        background-color: var(--ink);
        background-image:
            radial-gradient(circle at 12% 8%, rgba(72,199,142,0.06), transparent 42%),
            radial-gradient(circle at 88% 92%, rgba(232,163,61,0.05), transparent 46%),
            radial-gradient(rgba(255,255,255,0.025) 1px, transparent 1px);
        background-size: auto, auto, 3px 3px;
        background-repeat: no-repeat, no-repeat, repeat;
    }

    /* ===== بطاقة الترحيب — لوحة استوديو، لا شهادة ===== */
    .hero-card {
        position: relative;
        background: linear-gradient(160deg, var(--panel) 0%, var(--ink-2) 100%);
        border: 1px solid var(--line);
        border-radius: 20px;
        padding: 24px 30px;
        margin-bottom: 18px;
        box-shadow: 0 18px 40px rgba(0,0,0,0.5);
        overflow: hidden;
    }
    /* ديكور "مقياس مستوى" صغير بزاوية البطاقة — بديل ختم الشهادة القديم.
       يُبنى بالكامل من background-image (بدون أي عنصر HTML إضافي). */
    .hero-card::after {
        content: '';
        position: absolute; top: 22px; inset-inline-end: 26px;
        width: 64px; height: 30px;
        background-image:
            linear-gradient(to top, var(--meter-green) 45%, transparent 45%),
            linear-gradient(to top, var(--meter-green) 72%, transparent 72%),
            linear-gradient(to top, var(--meter-amber) 32%, transparent 32%),
            linear-gradient(to top, var(--meter-green) 88%, transparent 88%),
            linear-gradient(to top, var(--meter-green) 55%, transparent 55%),
            linear-gradient(to top, var(--meter-red) 20%, transparent 20%);
        background-repeat: no-repeat;
        background-size: 6px 100%;
        background-position: 0 100%, 12px 100%, 24px 100%, 36px 100%, 48px 100%, 60px 100%;
        opacity: 0.6;
    }
    .hero-title {
        font-family: var(--font-display);
        font-size: 1.95rem; font-weight: 700;
        color: var(--paper);
        margin-bottom: 4px;
        letter-spacing: -0.01em;
    }
    .hero-sub {
        color: var(--mist); font-size: 0.92rem; margin-bottom: 14px;
    }

    .badge {
        display: inline-flex; align-items: center; gap: 6px;
        padding: 5px 12px; border-radius: 999px; font-size: 0.8rem; font-weight: 700;
        background: var(--green-dim); color: var(--meter-green);
        border: 1px solid rgba(72, 199, 142, 0.35);
        transition: transform 0.15s ease, background 0.15s ease;
    }
    .badge:hover { transform: translateY(-1px); }

    /* ===== بطاقة التقييم — "قراءة مقياس" لا تذكرة مثقوبة ===== */
    .eval-card {
        position: relative;
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 14px 16px 12px 16px;
        margin: 4px 0 12px 0;
        font-size: 0.82rem;
        color: var(--mist);
    }
    .eval-scores {
        display: flex; align-items: center; gap: 14px; flex-wrap: wrap;
        font-family: var(--font-mono);
        font-weight: 600; color: var(--paper);
        font-size: 0.76rem; letter-spacing: 0.02em;
        padding-bottom: 10px; margin-bottom: 10px;
        /* خط تدريج المقياس بدل الخط المتقطع + ثقوب التذكرة */
        border-bottom: 1px solid var(--line);
        background-image: repeating-linear-gradient(90deg, var(--line) 0 1px, transparent 1px 9px);
        background-position: bottom;
        background-size: 100% 1px;
        background-repeat: no-repeat;
    }
    /* نقطة ملوّنة قبل كل قيمة — تتناوب أخضر/أذهبي كأضواء مقياس صوت */
    .eval-scores span::before {
        content: '●'; font-size: 0.55rem; margin-inline-end: 5px;
        color: var(--meter-green);
    }
    .eval-scores span:nth-child(even)::before { color: var(--meter-amber); }
    .eval-card b { color: var(--meter-amber); font-weight: 700; }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--ink-2) 0%, var(--ink) 100%);
        border-inline-end: 1px solid var(--line);
    }
    .side-heading {
        font-family: var(--font-mono);
        font-size: 0.7rem; letter-spacing: 0.12em; text-transform: uppercase;
        color: var(--meter-green); font-weight: 700;
        margin: 18px 0 8px 0; padding-bottom: 6px;
        border-bottom: 1px solid var(--line);
    }

    .stButton>button, .stDownloadButton>button {
        border-radius: 12px; font-weight: 700;
        background: var(--panel-raised) !important;
        color: var(--paper) !important;
        border: 1px solid var(--line) !important;
        transition: transform 0.15s ease, background 0.15s ease, border-color 0.15s ease;
    }
    .stButton>button:hover, .stDownloadButton>button:hover {
        transform: translateY(-1px);
        background: var(--green-dim) !important;
        border-color: rgba(72, 199, 142, 0.55) !important;
        color: var(--meter-green) !important;
    }
    .stButton>button:active, .stDownloadButton>button:active { transform: translateY(0); }
    .stButton>button:focus-visible, .stDownloadButton>button:focus-visible {
        outline: 2px solid var(--meter-green); outline-offset: 2px;
    }

    .stTextInput input:focus, .stTextArea textarea:focus,
    .stSelectbox [data-baseweb="select"]:focus-within {
        outline: 2px solid var(--meter-green) !important;
        outline-offset: 1px;
        border-color: var(--meter-green) !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 4px; border-bottom: 1px solid var(--line);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0; padding: 9px 18px; font-weight: 700;
        color: var(--mist);
        transition: color 0.15s ease, background 0.15s ease;
    }
    .stTabs [aria-selected="true"] {
        background: var(--green-dim);
        color: var(--meter-green) !important;
        box-shadow: inset 0 -2px 0 0 var(--meter-green);
    }

    [data-testid="stChatMessage"] {
        border-radius: 16px; padding: 8px 6px;
        border: 1px solid var(--line);
        background: rgba(255,255,255,0.02);
        margin-bottom: 8px;
        transition: background 0.15s ease, border-color 0.15s ease;
    }
    [data-testid="stChatMessage"]:hover {
        background: rgba(255,255,255,0.035);
        border-color: rgba(72, 199, 142, 0.25);
    }

    [data-testid="stChatInput"] {
        border-radius: 14px; border: 1px solid var(--line) !important;
    }
    [data-testid="stChatInput"]:focus-within {
        border-color: rgba(72, 199, 142, 0.55) !important;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 14px !important;
        border-color: var(--line) !important;
        transition: border-color 0.15s ease;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: rgba(72, 199, 142, 0.3) !important;
    }

    /* أرقام الإحصائيات — بخط Mono زي شاشة قياس رقمية */
    [data-testid="stMetricValue"] {
        font-family: var(--font-mono) !important;
        color: var(--meter-green) !important; font-weight: 700 !important;
    }
    [data-testid="stMetricLabel"] { color: var(--mist) !important; }

    /* شريط التقدم — مقسّم كشرائح LED حقيقية بدل تدرّج مصمت
       (ملاحظة: selector داخلي لستريملت وقد يتغير بين النسخ) */
    div[data-testid="stProgress"] > div > div {
        background: rgba(255,255,255,0.06) !important;
        border-radius: 6px !important;
    }
    div[data-testid="stProgress"] > div > div > div {
        background: repeating-linear-gradient(
            90deg,
            var(--meter-green) 0 6px,
            transparent 6px 9px
        ) !important;
        border-radius: 6px !important;
    }

    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: var(--green-dim); border-radius: 8px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(72, 199, 142, 0.32); }

    /* ===== مؤشر الكتابة — أعمدة مقياس صوت نابضة بدل نقاط قافزة ===== */
    .typing-card {
        display: inline-flex; align-items: center; gap: 10px;
        background: var(--green-dim); border: 1px solid rgba(72, 199, 142, 0.22);
        border-radius: 14px; padding: 10px 16px; color: var(--mist); font-size: 0.88rem; font-weight: 600;
    }
    .typing-dots { display: inline-flex; align-items: flex-end; gap: 4px; height: 14px; }
    .typing-dots span {
        width: 4px; height: 100%; border-radius: 2px;
        background: var(--meter-green);
        animation: eq-bounce 1.1s infinite ease-in-out;
        transform-origin: bottom;
    }
    .typing-dots span:nth-child(2) { animation-delay: 0.15s; background: var(--meter-amber); }
    .typing-dots span:nth-child(3) { animation-delay: 0.3s; }
    @keyframes eq-bounce {
        0%, 100% { transform: scaleY(0.35); opacity: 0.7; }
        50% { transform: scaleY(1); opacity: 1; }
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
        .hero-card { padding: 18px 20px; }
        .hero-card::after { display: none; }
        .hero-title { font-size: 1.45rem; }
        .eval-scores { gap: 9px; font-size: 0.7rem; }
    }
</style>
"""


def inject_css():
    st.markdown(APP_CSS, unsafe_allow_html=True)
