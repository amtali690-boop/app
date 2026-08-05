import streamlit as st

APP_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=El+Messiri:wght@400;500;600;700&family=Tajawal:wght@300;400;500;700;800&family=IBM+Plex+Mono:wght@500;600;700&display=swap');

    :root {
        /* ─── تم تصحيح أسماء المتغيرات: ink = داكن | paper = فاتح ─── */
        --ink: #0D0D0D;
        --ink-2: #F7F7F8;
        --panel: #FFFFFF;
        --panel-raised: #F0F0F1;
        --paper: #FFFFFF;
        --mist: #6E6E80;
        --line: rgba(0,0,0,0.09);

        --meter-green: #10A37F;
        --meter-amber: #B45309;
        --meter-red: #DC2626;
        --meter-blue: #2563EB;
        --meter-purple: #7C3AED;

        --green-dim: rgba(16, 163, 127, 0.09);
        --amber-dim: rgba(180, 83, 9, 0.10);
        --red-dim: rgba(220, 38, 38, 0.09);
        --blue-dim: rgba(37, 99, 235, 0.09);

        --font-display: 'El Messiri', 'Tajawal', sans-serif;
        --font-body: 'Tajawal', sans-serif;
        --font-mono: 'IBM Plex Mono', monospace;

        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 14px;
        --radius-xl: 16px;
        --radius-full: 999px;
    }

    /* ─── أساسيات الخطوط ─── */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"],
    [data-testid="stMarkdownContainer"], [data-testid="stChatMessage"], .stButton>button,
    .stTextInput input, .stTextArea textarea, .stSelectbox, [data-testid="stMetricLabel"],
    .stNumberInput input, .stDateInput input, .stTimeInput input {
        font-family: var(--font-body) !important;
        color: var(--ink) !important;
    }

    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3,
    [data-testid="stMarkdownContainer"] h4 {
        font-family: var(--font-display) !important;
        letter-spacing: -0.01em;
        color: var(--ink);
        line-height: 1.25;
    }

    ::selection { background: var(--green-dim); color: var(--ink); }

    /* ─── خلفية التطبيق ─── */
    .stApp { background-color: var(--paper); }

    /* ─── Selectbox & Multiselect ─── */
    .stSelectbox [data-baseweb="select"] > div,
    .stMultiselect [data-baseweb="select"] > div {
        background-color: var(--panel-raised) !important;
        border: 1px solid var(--line) !important;
        border-radius: var(--radius-md) !important;
        color: var(--ink) !important;
        min-height: 40px;
    }
    .stSelectbox [data-baseweb="select"] input,
    .stMultiselect [data-baseweb="select"] input,
    .stSelectbox [data-baseweb="select"] div[role="button"],
    .stMultiselect [data-baseweb="select"] div[role="button"] {
        color: var(--ink) !important;
    }
    .stSelectbox svg, .stMultiselect svg { fill: var(--mist) !important; }

    /* قائمة الخيارات المنسدلة */
    div[data-baseweb="popover"] ul[role="listbox"] {
        background-color: var(--panel) !important;
        border: 1px solid var(--line) !important;
        border-radius: var(--radius-md) !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08) !important;
    }
    div[data-baseweb="popover"] li[role="option"] {
        color: var(--ink) !important;
        background-color: transparent !important;
        font-family: var(--font-body) !important;
    }
    div[data-baseweb="popover"] li[role="option"]:hover,
    div[data-baseweb="popover"] li[aria-selected="true"] {
        background-color: var(--green-dim) !important;
        color: var(--meter-green) !important;
    }

    /* ─── TextInput & TextArea & NumberInput & Date/Time ─── */
    .stTextInput input, .stTextArea textarea,
    .stNumberInput input, .stDateInput input, .stTimeInput input {
        background-color: var(--panel-raised) !important;
        border: 1px solid var(--line) !important;
        border-radius: var(--radius-md) !important;
        color: var(--ink) !important;
        font-family: var(--font-body) !important;
    }
    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder,
    .stNumberInput input::placeholder {
        color: var(--mist) !important;
        opacity: 0.7 !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus,
    .stNumberInput input:focus, .stDateInput input:focus, .stTimeInput input:focus,
    .stSelectbox [data-baseweb="select"]:focus-within,
    .stMultiselect [data-baseweb="select"]:focus-within {
        outline: 2px solid var(--meter-green) !important;
        outline-offset: 1px;
        border-color: var(--meter-green) !important;
        box-shadow: 0 0 0 3px var(--green-dim) !important;
    }

    /* ─── Sidebar ─── */
    section[data-testid="stSidebar"] {
        background: var(--ink-2);
        border-inline-end: 1px solid var(--line);
    }
    button[data-testid="baseButton-header"] {
        background: var(--panel-raised) !important;
        border: 1px solid var(--line) !important;
        color: var(--mist) !important;
        border-radius: var(--radius-sm) !important;
    }
    button[data-testid="baseButton-header"]:hover {
        background: var(--green-dim) !important;
        color: var(--meter-green) !important;
    }

    .side-heading {
        font-family: var(--font-mono);
        font-size: 0.7rem; letter-spacing: 0.12em; text-transform: uppercase;
        color: var(--meter-green); font-weight: 700;
        margin: 18px 0 8px 0; padding-bottom: 6px;
        border-bottom: 1px solid var(--line);
    }

    /* ─── Buttons (Primary, Secondary, Download, Link) ─── */
    .stButton>button, .stDownloadButton>button,
    .stLinkButton>a {
        border-radius: var(--radius-md) !important;
        font-weight: 700 !important;
        font-family: var(--font-body) !important;
        background: var(--panel-raised) !important;
        color: var(--ink) !important;
        border: 1px solid var(--line) !important;
        transition: transform 0.15s ease, background 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease;
    }
    .stButton>button:hover, .stDownloadButton>button:hover,
    .stLinkButton>a:hover {
        transform: translateY(-1px);
        background: var(--green-dim) !important;
        border-color: rgba(16, 163, 127, 0.4) !important;
        color: var(--meter-green) !important;
        box-shadow: 0 2px 8px rgba(16, 163, 127, 0.12) !important;
    }
    .stButton>button:active, .stDownloadButton>button:active,
    .stLinkButton>a:active { transform: translateY(0); }
    .stButton>button:focus-visible, .stDownloadButton>button:focus-visible,
    .stLinkButton>a:focus-visible {
        outline: 2px solid var(--meter-green); outline-offset: 2px;
    }
    .stButton>button[kind="primary"], .stDownloadButton>button[kind="primary"] {
        background: var(--meter-green) !important;
        color: #FFFFFF !important;
        border-color: var(--meter-green) !important;
    }
    .stButton>button[kind="primary"]:hover, .stDownloadButton>button[kind="primary"]:hover {
        background: #0D8C6D !important;
        border-color: #0D8C6D !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 12px rgba(16, 163, 127, 0.25) !important;
    }

    /* ─── Tabs ─── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px; border-bottom: 1px solid var(--line);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: var(--radius-sm) var(--radius-sm) 0 0;
        padding: 9px 18px; font-weight: 700;
        color: var(--mist);
        font-family: var(--font-body) !important;
        transition: color 0.15s ease, background 0.15s ease;
    }
    .stTabs [aria-selected="true"] {
        background: var(--green-dim);
        color: var(--meter-green) !important;
        box-shadow: inset 0 -2px 0 0 var(--meter-green);
    }

    /* ─── Chat ─── */
    [data-testid="stChatMessage"] {
        border-radius: var(--radius-xl);
        padding: 12px 14px;
        border: 1px solid var(--line);
        background: rgba(0,0,0,0.012);
        margin-bottom: 8px;
        transition: background 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease;
    }
    [data-testid="stChatMessage"]:hover {
        background: rgba(0,0,0,0.025);
        border-color: rgba(16, 163, 127, 0.22);
        box-shadow: 0 2px 12px rgba(0,0,0,0.03);
    }
    [data-testid="stChatMessage"] img {
        border-radius: var(--radius-full) !important;
        border: 2px solid var(--line) !important;
    }
    [data-testid="stChatMessage"] [data-testid="stChatMessageAvatar"] + div {
        font-weight: 700;
        color: var(--ink);
    }

    [data-testid="stChatInput"] {
        border-radius: var(--radius-lg);
        border: 1px solid var(--line) !important;
        background: var(--panel) !important;
    }
    [data-testid="stChatInput"]:focus-within {
        border-color: rgba(16, 163, 127, 0.5) !important;
        box-shadow: 0 0 0 3px var(--green-dim) !important;
    }

    /* ─── Expanders ─── */
    [data-testid="stExpander"] {
        border: 1px solid var(--line) !important;
        border-radius: var(--radius-lg) !important;
        background: var(--panel) !important;
        overflow: hidden;
    }
    [data-testid="stExpanderToggle"] {
        background: transparent !important;
        color: var(--ink) !important;
        font-weight: 700 !important;
    }
    [data-testid="stExpanderToggle"]:hover {
        background: var(--green-dim) !important;
        color: var(--meter-green) !important;
    }

    /* ─── Vertical Block Borders ─── */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: var(--radius-lg) !important;
        border-color: var(--line) !important;
        transition: border-color 0.15s ease, box-shadow 0.15s ease;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: rgba(16, 163, 127, 0.28) !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    }

    /* ─── Metrics ─── */
    [data-testid="stMetricValue"] {
        font-family: var(--font-mono) !important;
        color: var(--meter-green) !important;
        font-weight: 700 !important;
        font-size: 1.6rem !important;
    }
    [data-testid="stMetricLabel"] { color: var(--mist) !important; font-weight: 500 !important; }
    [data-testid="stMetricDelta"] {
        font-family: var(--font-mono) !important;
        font-weight: 600 !important;
    }

    /* ─── Progress Bar ─── */
    div[data-testid="stProgress"] > div > div {
        background: rgba(0,0,0,0.07) !important;
        border-radius: 6px !important;
    }
    div[data-testid="stProgress"] > div > div > div {
        background: var(--meter-green) !important;
        border-radius: 6px !important;
        transition: width 0.3s ease;
    }

    /* ─── Slider ─── */
    div[data-testid="stSlider"] > div > div > div {
        background: var(--line) !important;
    }
    div[data-testid="stSlider"] > div > div > div > div {
        background: var(--meter-green) !important;
    }
    div[data-testid="stSlider"] [role="slider"] {
        border: 2px solid var(--meter-green) !important;
        background: var(--panel) !important;
    }

    /* ─── Toggle / Checkbox / Radio ─── */
    /* تم تصحيح selector الـ Toggle ليتوافق مع Streamlit الحديث */
    [data-testid="stToggle"] > div > div {
        background: var(--line) !important;
    }
    [data-testid="stToggle"] > div > div[data-checked="true"] {
        background: var(--meter-green) !important;
    }
    .stCheckbox > label > div[role="checkbox"],
    .stRadio > div > label > div[role="radio"] {
        border-color: var(--line) !important;
    }
    .stCheckbox > label > div[role="checkbox"][aria-checked="true"],
    .stRadio > div > label > div[role="radio"][aria-checked="true"] {
        background: var(--meter-green) !important;
        border-color: var(--meter-green) !important;
    }

    /* ─── File Uploader ─── */
    [data-testid="stFileUploader"] {
        border: 2px dashed var(--line) !important;
        border-radius: var(--radius-lg) !important;
        background: var(--ink-2) !important;
        transition: border-color 0.2s ease, background 0.2s ease;
    }
    [data-testid="stFileUploader"]:hover, [data-testid="stFileUploader"]:focus-within {
        border-color: var(--meter-green) !important;
        background: var(--green-dim) !important;
    }
    [data-testid="stFileUploader"] button {
        background: var(--panel-raised) !important;
        border: 1px solid var(--line) !important;
        color: var(--ink) !important;
        border-radius: var(--radius-sm) !important;
    }
    [data-testid="stFileUploader"] button:hover {
        background: var(--green-dim) !important;
        color: var(--meter-green) !important;
        border-color: rgba(16, 163, 127, 0.4) !important;
    }

    /* ─── Alerts (Success, Info, Warning, Error) ─── */
    [data-testid="stAlert"] {
        border-radius: var(--radius-lg) !important;
        border: 1px solid var(--line) !important;
        font-family: var(--font-body) !important;
    }
    [data-testid="stAlert"][kind="success"] {
        background: var(--green-dim) !important;
        border-color: rgba(16, 163, 127, 0.3) !important;
        color: #065F46 !important;
    }
    [data-testid="stAlert"][kind="info"] {
        background: var(--blue-dim) !important;
        border-color: rgba(37, 99, 235, 0.3) !important;
        color: #1E40AF !important;
    }
    [data-testid="stAlert"][kind="warning"] {
        background: var(--amber-dim) !important;
        border-color: rgba(180, 83, 9, 0.3) !important;
        color: #92400E !important;
    }
    [data-testid="stAlert"][kind="error"] {
        background: var(--red-dim) !important;
        border-color: rgba(220, 38, 38, 0.3) !important;
        color: #991B1B !important;
    }

    /* ─── Code Blocks ─── */
    /* تم تصحيح selector من .stMarkdown إلى [data-testid="stMarkdownContainer"] */
    [data-testid="stMarkdownContainer"] pre, [data-testid="stMarkdownContainer"] code {
        font-family: var(--font-mono) !important;
        border-radius: var(--radius-sm) !important;
    }
    [data-testid="stMarkdownContainer"] pre {
        background: #1E1E1E !important;
        color: #D4D4D4 !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        padding: 14px !important;
        overflow-x: auto;
    }
    [data-testid="stMarkdownContainer"] code {
        background: var(--panel-raised) !important;
        color: var(--meter-green) !important;
        padding: 2px 6px !important;
        font-size: 0.9em;
    }
    [data-testid="stMarkdownContainer"] pre code {
        background: transparent !important;
        color: #D4D4D4 !important;
        padding: 0 !important;
    }

    /* ─── DataFrame / Table ─── */
    [data-testid="stDataFrame"] {
        border: 1px solid var(--line) !important;
        border-radius: var(--radius-lg) !important;
        overflow: hidden;
    }
    [data-testid="stDataFrame"] th {
        background: var(--ink-2) !important;
        color: var(--ink) !important;
        font-weight: 700 !important;
        font-family: var(--font-body) !important;
        border-bottom: 1px solid var(--line) !important;
    }
    [data-testid="stDataFrame"] td {
        color: var(--ink) !important;
        font-family: var(--font-body) !important;
        border-bottom: 1px solid var(--line) !important;
    }
    [data-testid="stDataFrame"] tr:hover td {
        background: var(--green-dim) !important;
    }

    /* ─── Spinner & Status ─── */
    .stSpinner > div {
        border-top-color: var(--meter-green) !important;
    }
    [data-testid="stStatus"] {
        border: 1px solid var(--line) !important;
        border-radius: var(--radius-lg) !important;
        background: var(--panel) !important;
    }
    [data-testid="stStatus"] [data-testid="stStatusLabel"] {
        color: var(--ink) !important;
        font-weight: 700 !important;
    }

    /* ─── Popover ─── */
    [data-testid="stPopover"] > div:first-child > button {
        background: var(--panel-raised) !important;
        border: 1px solid var(--line) !important;
        border-radius: var(--radius-md) !important;
        color: var(--ink) !important;
        font-weight: 600 !important;
    }
    [data-testid="stPopover"] > div:first-child > button:hover {
        background: var(--green-dim) !important;
        color: var(--meter-green) !important;
        border-color: rgba(16, 163, 127, 0.4) !important;
    }

    /* ─── Toast ─── */
    [data-testid="stToast"] {
        border-radius: var(--radius-lg) !important;
        border: 1px solid var(--line) !important;
        background: var(--panel) !important;
        box-shadow: 0 8px 30px rgba(0,0,0,0.12) !important;
    }

    /* ─── Divider ─── */
    hr {
        border: none !important;
        border-top: 1px solid var(--line) !important;
        margin: 1.5rem 0 !important;
    }

    /* ─── Scrollbar ─── */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: var(--green-dim); border-radius: var(--radius-full); }
    ::-webkit-scrollbar-thumb:hover { background: rgba(16, 163, 127, 0.3); }
    /* دعم Firefox */
    * { scrollbar-width: thin; scrollbar-color: rgba(16, 163, 127, 0.2) transparent; }

    /* ─── Typing Indicator ─── */
    .typing-card {
        display: inline-flex; align-items: center; gap: 10px;
        background: var(--ink-2); border: 1px solid var(--line);
        border-radius: var(--radius-lg); padding: 10px 16px;
        color: var(--mist); font-size: 0.88rem; font-weight: 600;
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

    /* ─── Badge ─── */
    .badge {
        display: inline-flex; align-items: center; gap: 6px;
        padding: 5px 12px; border-radius: var(--radius-full);
        font-size: 0.8rem; font-weight: 700;
        background: var(--green-dim); color: var(--meter-green);
        border: 1px solid rgba(16, 163, 127, 0.28);
        transition: transform 0.15s ease, background 0.15s ease;
    }
    .badge:hover { transform: translateY(-1px); }

    /* ─── Eval Card ─── */
    .eval-card {
        position: relative;
        background: var(--ink-2);
        border: 1px solid var(--line);
        border-radius: var(--radius-lg);
        padding: 14px 16px 12px 16px;
        margin: 4px 0 12px 0;
        font-size: 0.82rem;
        color: var(--mist);
    }
    .eval-scores {
        display: flex; align-items: center; gap: 14px; flex-wrap: wrap;
        font-family: var(--font-mono);
        font-weight: 600; color: var(--ink);
        font-size: 0.76rem; letter-spacing: 0.02em;
        padding-bottom: 10px; margin-bottom: 10px;
        border-bottom: 1px solid var(--line);
    }
    .eval-scores span::before {
        content: '●'; font-size: 0.55rem; margin-inline-end: 5px;
        color: var(--meter-green);
    }
    .eval-scores span:nth-child(even)::before { color: var(--meter-amber); }
    .eval-card b { color: var(--meter-amber); font-weight: 700; }

    /* ─── Reduced Motion ─── */
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.001ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.001ms !important;
        }
    }

    /* ─── Mobile ─── */
    @media (max-width: 480px) {
        .eval-scores { gap: 9px; font-size: 0.7rem; }
        [data-testid="stMetricValue"] { font-size: 1.3rem !important; }
    }
</style>
"""


def inject_css():
    st.markdown(APP_CSS, unsafe_allow_html=True)
