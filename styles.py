# ==========================================
# styles.py — تنسيق CSS الخاص بالتطبيق فقط، منفصل عن أي منطق برمجي
# ==========================================
import streamlit as st

# ثابتة (تُحسب مرة واحدة عند استيراد الوحدة، وليس مع كل rerun)
APP_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap');

    html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"],
    [data-testid="stMarkdownContainer"], .stChatMessage, .stButton>button,
    .stTextInput input, .stTextArea textarea, .stSelectbox, [data-testid="stMetricValue"] {
        font-family: 'Tajawal', sans-serif !important;
    }

    .stApp {
        background: radial-gradient(circle at top left, #0f172a 0%, #090d16 55%, #030712 100%);
    }

    /* بطاقة الترحيب */
    .hero-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 60%, #090d16 100%);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 18px; padding: 20px 26px; margin-bottom: 16px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.4);
    }
    .hero-title { font-size: 1.7rem; font-weight: 800; color: #f8fafc; margin-bottom: 4px; }
    .hero-sub { color: #94a3b8; font-size: 0.92rem; margin-bottom: 12px; }
    .badge {
        display: inline-flex; align-items: center; gap: 6px;
        padding: 5px 12px; border-radius: 999px; font-size: 0.8rem; font-weight: 600;
        background: rgba(56, 189, 248, 0.12); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3);
        transition: transform 0.15s ease;
    }
    .badge:hover { transform: translateY(-1px); }

    .eval-card {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(167, 139, 250, 0.25);
        border-radius: 12px; padding: 10px 14px; margin-bottom: 8px;
        font-size: 0.82rem; color: #cbd5e1;
    }
    .eval-scores { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 4px; font-weight: 700; color: #38bdf8; }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #090d16 0%, #030712 100%);
        border-right: 1px solid rgba(148,163,184,0.1);
    }
    .side-heading {
        font-size: 0.78rem; letter-spacing: 0.08em; text-transform: uppercase;
        color: #64748b; font-weight: 700; margin: 16px 0 6px 0;
    }

    .stButton>button, .stDownloadButton>button {
        border-radius: 10px; font-weight: 700;
        transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
    }
    .stButton>button:hover, .stDownloadButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(56, 189, 248, 0.18);
        border-color: rgba(56, 189, 248, 0.5);
    }
    .stButton>button:active, .stDownloadButton>button:active { transform: translateY(0); }

    .stTabs [data-baseweb="tab-list"] {
        gap: 6px; border-bottom: 1px solid rgba(148,163,184,0.12);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px 10px 0 0; padding: 8px 16px; font-weight: 700;
        transition: background 0.15s ease;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(56, 189, 248, 0.1); color: #38bdf8 !important;
    }

    [data-testid="stChatMessage"] {
        border-radius: 16px; padding: 6px 4px;
        border: 1px solid rgba(148,163,184,0.08);
        background: rgba(255,255,255,0.02);
        margin-bottom: 6px;
        transition: background 0.15s ease;
    }
    [data-testid="stChatMessage"]:hover { background: rgba(255,255,255,0.035); }

    [data-testid="stChatInput"] {
        border-radius: 14px; border: 1px solid rgba(56, 189, 248, 0.25) !important;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 14px !important;
        transition: border-color 0.15s ease;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: rgba(56, 189, 248, 0.35) !important;
    }

    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(148,163,184,0.25); border-radius: 8px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(148,163,184,0.4); }

    .typing-card {
        display: inline-flex; align-items: center; gap: 10px;
        background: rgba(255,255,255,0.04); border: 1px solid rgba(148,163,184,0.12);
        border-radius: 14px; padding: 10px 16px; color: #94a3b8; font-size: 0.88rem; font-weight: 600;
    }
    .typing-dots { display: inline-flex; gap: 4px; }
    .typing-dots span {
        width: 6px; height: 6px; border-radius: 50%;
        background: linear-gradient(135deg, #38bdf8, #a78bfa);
        animation: typing-bounce 1.2s infinite ease-in-out;
    }
    .typing-dots span:nth-child(2) { animation-delay: 0.15s; }
    .typing-dots span:nth-child(3) { animation-delay: 0.3s; }
    @keyframes typing-bounce {
        0%, 60%, 100% { transform: translateY(0); opacity: 0.5; }
        30% { transform: translateY(-5px); opacity: 1; }
    }
</style>
"""


def inject_css():
    st.markdown(APP_CSS, unsafe_allow_html=True)
