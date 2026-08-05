# ==========================================
# styles.py — تنسيق CSS الخاص بالتطبيق فقط، منفصل عن أي منطق برمجي
# هوية بصرية v4 (نضيفة وفاتحة): مستوحاة من واجهة شات جي بي تي
# — خلفية بيضاء، أسطح رمادي فاتح، تباعد سخي، وحدة لون واحدة هادئة
# بدل هوية "استوديو التسجيل" الغامقة السابقة (VU meter / أخضر على أسود).
# نفس أسماء الـ CSS variables والـ classes اتحفظت عشان أي كود
# تاني بيستخدمها (hero-card, badge, eval-card...) يفضل شغال من غير تعديل.
# ==========================================
import streamlit as st

# ثابتة (تُحسب مرة واحدة عند استيراد الوحدة، وليس مع كل rerun)
APP_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=El+Messiri:wght@400;500;600;700&family=Tajawal:wght@300;400;500;700;800&family=IBM+Plex+Mono:wght@500;600;700&display=swap');

    :root {
        --ink: #FFFFFF;          /* خلفية الصفحة — أبيض نضيف */
        --ink-2: #F7F7F8;        /* سطح ثانوي / سايدبار — رمادي فاتح جدًا */
        --panel: #FFFFFF;        /* سطح البطاقات */
        --panel-raised: #F0F0F1; /* سطح الأزرار / hover */
        --paper: #0D0D0D;        /* نص العناوين — أسود شبه نقي */
        --mist: #6E6E80;         /* نص ثانوي رمادي */
        --line: rgba(0,0,0,0.09);/* خطوط وحدود فاتحة */

        /* لون تمييز واحد هادئ — نفس روح لون شات جي بي تي الأخضر،
           مستخدم بانضباط في الأزرار والحالات والـ focus فقط */
        --meter-green: #10A37F;   /* أساسي: تقدّم / نجاح / تمييز */
        --meter-amber: #B45309;   /* تنبيه: مستوى CEFR / يحتاج مراجعة */
        --meter-red:   #DC2626;   /* الأخطاء فقط */

        --green-dim: rgba(16, 163, 127, 0.09);
        --amber-dim: rgba(180, 83, 9, 0.10);
        --red-dim:   rgba(220, 38, 38, 0.09);

        --font-display: 'El Messiri', 'Tajawal', sans-serif;
        --font-body: 'Tajawal', sans-serif;
        --font-mono: 'IBM Plex Mono', monospace;
    }

    html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"],
    [data-testid="stMarkdownContainer"], .stChatMessage, .stButton>button,
    .stTextInput input, .stTextArea textarea, .stSelectbox, [data-testid="stMetricLabel"] {
        font-family: var(--font-body) !important;
        color: var(--paper) !important;
    }

    /* عناوين الأقسام بكل التبويبات تأخذ خط العرض المميز — يوحّد الهوية بلا حاجة لتغيير الكود */
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3 {
        font-family: var(--font-display) !important;
        letter-spacing: -0.01em;
        color: var(--paper);
    }

    ::selection { background: var(--green-dim); color: var(--paper); }

    /* خلفية مسطحة نضيفة — من غير أي نويز أو زخرفة استوديو */
    .stApp {
        background-color: var(--ink);
    }

    /* ✅ التعديل: القوائم المنسدلة (selectbox) بحالتها العادية —
       كانت سوداء لأنها ما كانت متغطاة إلا عند الـ focus فقط.
       هلق صارت فاتحة زي حقول شات جي بي تي: خلفية رمادي فاتح، حدود ناعمة، نص غامق */
    .stSelectbox [data-baseweb="select"] > div {
        background-color: var(--panel-raised) !important;
        border: 1px solid var(--line) !important;
        border-radius: 12px !important;
        color: var(--paper) !important;
    }
    .stSelectbox [data-baseweb="select"] input,
    .stSelectbox [data-baseweb="select"] div[role="button"] {
        color: var(--paper) !important;
    }
    .stSelectbox svg { fill: var(--mist) !important; }

    /* قائمة الخيارات المنسدلة نفسها (البوب أب) لما تفتحها */
    div[data-baseweb="popover"] ul[role="listbox"] {
        background-color: var(--panel) !important;
        border: 1px solid var(--line) !important;
        border-radius: 12px !important;
    }
    div[data-baseweb="popover"] li[role="option"] {
        color: var(--paper) !important;
        background-color: transparent !important;
    }
    div[data-baseweb="popover"] li[role="option"]:hover,
    div[data-baseweb="popover"] li[aria-selected="true"] {
        background-color: var(--green-dim) !important;
        color: var(--meter-green) !important;
    }

    .badge {
        display: inline-flex; align-items: center; gap: 6px;
        padding: 5px 12px; border-radius: 999px; font-size: 0.8rem; font-weight: 700;
        background: var(--green-dim); color: var(--meter-green);
        border: 1px solid rgba(16, 163, 127, 0.28);
        transition: transform 0.15s ease, background 0.15s ease;
    }
    .badge:hover { transform: translateY(-1px); }

    /* ===== بطاقة التقييم ===== */
    .eval-card {
        position: relative;
        background: var(--ink-2);
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
        border-bottom: 1px solid var(--line);
    }
    /* نقطة صغيرة قبل كل قيمة لتمييزها بسرعة */
    .eval-scores span::before {
        content: '●'; font-size: 0.55rem; margin-inline-end: 5px;
        color: var(--meter-green);
    }
    .eval-scores span:nth-child(even)::before { color: var(--meter-amber); }
    .eval-card b { color: var(--meter-amber); font-weight: 700; }

    section[data-testid="stSidebar"] {
        background: var(--ink-2);
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
        border-color: rgba(16, 163, 127, 0.4) !important;
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
        background: rgba(0,0,0,0.012);
        margin-bottom: 8px;
        transition: background 0.15s ease, border-color 0.15s ease;
    }
    [data-testid="stChatMessage"]:hover {
        background: rgba(0,0,0,0.025);
        border-color: rgba(16, 163, 127, 0.22);
    }

    [data-testid="stChatInput"] {
        border-radius: 14px; border: 1px solid var(--line) !important;
        background: var(--panel) !important;
    }
    [data-testid="stChatInput"]:focus-within {
        border-color: rgba(16, 163, 127, 0.5) !important;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 14px !important;
        border-color: var(--line) !important;
        transition: border-color 0.15s ease;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: rgba(16, 163, 127, 0.28) !important;
    }

    /* أرقام الإحصائيات — بخط Mono زي شاشة قياس رقمية */
    [data-testid="stMetricValue"] {
        font-family: var(--font-mono) !important;
        color: var(--meter-green) !important; font-weight: 700 !important;
    }
    [data-testid="stMetricLabel"] { color: var(--mist) !important; }

    /* شريط التقدم — تعبئة مسطحة وبسيطة
       (ملاحظة: selector داخلي لستريملت وقد يتغير بين النسخ) */
    div[data-testid="stProgress"] > div > div {
        background: rgba(0,0,0,0.07) !important;
        border-radius: 6px !important;
    }
    div[data-testid="stProgress"] > div > div > div {
        background: var(--meter-green) !important;
        border-radius: 6px !important;
    }

    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: var(--green-dim); border-radius: 8px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(16, 163, 127, 0.3); }

    /* ===== مؤشر الكتابة — ثلاث نقاط بسيطة نابضة، زي مؤشرات الشات المعتادة ===== */
    .typing-card {
        display: inline-flex; align-items: center; gap: 10px;
        background: var(--ink-2); border: 1px solid var(--line);
        border-radius: 14px; padding: 10px 16px; color: var(--mist); font-size: 0.88rem; font-weight: 600;
    }
    .typing-dots { display: inline-flex; align-items: center; gap: 4px; height: 14px; }
    .typing-dots span {
        width: 6px; height: 6px; border-radius: 50%;
        background: var(--meter-green);
        animation: dot-bounce 1.2s infinite ease-in-out;
    }
    .typing-dots span:nth-child(2) { animation-delay: 0.15s; }
    .typing-dots span:nth-child(3) { animation-delay: 0.3s; }
    @keyframes dot-bounce {
        0%, 80%, 100% { transform: translateY(0); opacity: 0.4; }
        40% { transform: translateY(-4px); opacity: 1; }
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
        .hero-title { font-size: 1.45rem; }
        .eval-scores { gap: 9px; font-size: 0.7rem; }
    }
</style>
"""


def inject_css():
    st.markdown(APP_CSS, unsafe_allow_html=True)
