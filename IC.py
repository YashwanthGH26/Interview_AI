import streamlit as st
import anthropic
import io
import speech_recognition as sr
from datetime import datetime

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Interview Cracker AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Initialize Session States ─────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "current_response" not in st.session_state:
    st.session_state.current_response = ""

# Anthropic client initialization safely pulls from secrets or system environment
# Make sure ANTHROPIC_API_KEY is configured in your local environment or Streamlit Cloud Secrets
try:
    client = anthropic.Anthropic()
except Exception:
    client = None

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&family=Inter:wght@300;400;500&display=swap');

/* ── Root variables ── */
:root {
    --bg:        #050A0E;
    --surface:   #0C1418;
    --card:      #111C22;
    --border:    #1E3040;
    --accent:    #00FFB2;
    --accent2:   #00C9FF;
    --warn:      #FF6B35;
    --text:      #E8F4F0;
    --muted:     #5A7A8A;
    --glow:      0 0 30px rgba(0,255,178,0.15);
}

/* ── Global reset ── */
html, body, [class*="css"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif !important;
}

.stApp { background: var(--bg) !important; }

/* ── Hide streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2rem 1rem !important; max-width: 1200px !important; }

/* ── Hero header ── */
.hero {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
    position: relative;
}
.hero::before {
    content: '';
    position: absolute;
    top: 0; left: 50%; transform: translateX(-50%);
    width: 600px; height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2rem, 5vw, 3.5rem);
    font-weight: 800;
    letter-spacing: -1px;
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent2) 60%, #fff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 0.4rem;
    line-height: 1.1;
}
.hero-sub {
    font-size: 1rem;
    color: var(--muted);
    letter-spacing: 0.15em;
    text-transform: uppercase;
    font-weight: 300;
}
.live-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(0,255,178,0.08);
    border: 1px solid rgba(0,255,178,0.3);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.72rem;
    color: var(--accent);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-top: 1rem;
}
.live-dot {
    width: 7px; height: 7px;
    background: var(--accent);
    border-radius: 50%;
    animation: pulse 1.4s ease-in-out infinite;
}
@keyframes pulse {
    0%,100% { opacity: 1; transform: scale(1); }
    50%      { opacity: 0.4; transform: scale(0.7); }
}

/* ── Section labels ── */
.section-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.5rem;
}

/* ── Input card ── */
.input-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.5rem;
    margin-bottom: 1.2rem;
    position: relative;
    overflow: hidden;
}
.input-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, var(--accent2), transparent);
    opacity: 0.5;
}

/* ── Streamlit textarea override ── */
.stTextArea textarea {
    background: #0A1520 !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 1rem !important;
    padding: 1rem !important;
    resize: none !important;
    transition: border-color 0.2s;
}
.stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(0,255,178,0.1) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent2) 100%) !important;
    color: #050A0E !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.05em !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.65rem 1.8rem !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    width: 100%;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 25px rgba(0,255,178,0.3) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* Secondary button */
.secondary-btn .stButton > button {
    background: transparent !important;
    color: var(--muted) !important;
    border: 1px solid var(--border) !important;
    font-weight: 500 !important;
}
.secondary-btn .stButton > button:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
    box-shadow: none !important;
}

/* ── Answer display ── */
.answer-wrapper {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 14px;
    overflow: hidden;
    margin-bottom: 1.2rem;
}
.answer-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.9rem 1.4rem;
    background: rgba(0,255,178,0.04);
    border-bottom: 1px solid var(--border);
}
.answer-header-left {
    display: flex;
    align-items: center;
    gap: 10px;
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.15em;
    color: var(--accent);
    text-transform: uppercase;
}
.answer-body {
    padding: 1.6rem;
    font-size: 1.05rem;
    line-height: 1.8;
    color: var(--text);
    min-height: 120px;
    white-space: pre-wrap;
}
.answer-body.streaming {
    border-left: 3px solid var(--accent);
}
.answer-placeholder {
    color: var(--muted);
    font-style: italic;
    font-size: 0.9rem;
}

/* ── History item ── */
.history-item {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.7rem;
    transition: border-color 0.2s;
}
.history-item:hover { border-color: rgba(0,255,178,0.3); }
.history-q {
    font-size: 0.85rem;
    color: var(--accent2);
    font-weight: 500;
    margin-bottom: 0.4rem;
    display: flex;
    align-items: flex-start;
    gap: 8px;
}
.history-a {
    font-size: 0.88rem;
    color: #8AACB8;
    line-height: 1.6;
}
.history-time {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    color: var(--muted);
    margin-top: 0.5rem;
}

/* ── Stat pills ── */
.stats-row {
    display: flex;
    gap: 0.8rem;
    flex-wrap: wrap;
    margin-bottom: 1.5rem;
}
.stat-pill {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 30px;
    padding: 5px 14px;
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    color: var(--muted);
}
.stat-pill span { color: var(--accent); font-weight: 700; }

/* ── Divider ── */
.custom-divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 1.5rem 0;
}

/* ── Select box ── */
.stSelectbox > div > div {
    background: #0A1520 !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
    border-radius: 10px !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }

/* ── Recording animation ── */
.recording-indicator {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    color: var(--warn);
    font-family: 'Space Mono', monospace;
    font-size: 0.8rem;
    padding: 6px 14px;
    background: rgba(255,107,53,0.1);
    border: 1px solid rgba(255,107,53,0.3);
    border-radius: 20px;
}
</style>
""", unsafe_allow_html=True)

# ── Hero Layout ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1 class="hero-title">INTERVIEW CRACKER AI</h1>
    <div class="hero-sub">Real-Time Copilot & Technical Response Engine</div>
    <div class="live-badge">
        <div class="live-dot"></div> Copilot Pipeline Active
    </div>
</div>
""", unsafe_allow_html=True)

# Layout Setup: Left panel for configurations & input, Right panel for output
col_left, col_right = st.columns([1, 1.2], gap="large")

with col_left:
    st.markdown('<div class="section-label">System Configurations</div>', unsafe_allow_html=True)
    
    # Context Type Selector
    session_mode = st.selectbox(
        "Interview Target Profile",
        ["System Design & Architecture", "LeetCode & Algorithms", "Behavioral (STAR Method)", "General Technical / Core CS"]
    )
    
    # Active Stat Indicators
    st.markdown(f"""
    <div class="stats-row">
        <div class="stat-pill">Profile: <span>{session_mode}</span></div>
        <div class="stat-pill">Logged Queries: <span>{len(st.session_state.history)}</span></div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="section-label">Audio Capture Device</div>', unsafe_allow_html=True)
    
    # ── New Cross-Platform Browser Audio Recorder ──
    # This renders an interactive microphone directly inside the user's web browser
