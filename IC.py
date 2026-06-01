import streamlit as st
import anthropic
import time
import speech_recognition as sr
import threading
from datetime import datetime

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Interview Cracker AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

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
.rec-dot {
    width: 8px; height: 8px;
    background: var(--warn);
    border-radius: 50%;
    animation: pulse 0.8s ease-in-out infinite;
}

/* ── Tip box ── */
.tip-box {
    background: rgba(0,201,255,0.05);
    border: 1px solid rgba(0,201,255,0.2);
    border-radius: 10px;
    padding: 0.8rem 1.1rem;
    font-size: 0.82rem;
    color: #7DC8E8;
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "current_answer" not in st.session_state:
    st.session_state.current_answer = ""
if "is_generating" not in st.session_state:
    st.session_state.is_generating = False
if "question_count" not in st.session_state:
    st.session_state.question_count = 0
if "role" not in st.session_state:
    st.session_state.role = "Software Engineer"
if "listening" not in st.session_state:
    st.session_state.listening = False
if "mic_question" not in st.session_state:
    st.session_state.mic_question = ""

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-title">Interview Cracker AI</div>
    <div class="hero-sub">Real-time answers · Silent mode · Any interview</div>
    <div style="display:flex;justify-content:center">
        <div class="live-badge"><div class="live-dot"></div>AI Ready</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Stats row ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="stats-row">
    <div class="stat-pill">Questions answered: <span>{st.session_state.question_count}</span></div>
    <div class="stat-pill">Role: <span>{st.session_state.role}</span></div>
    <div class="stat-pill">Mode: <span>Silent Display</span></div>
</div>
""", unsafe_allow_html=True)

# ── Layout: two columns ───────────────────────────────────────────────────────
left, right = st.columns([1, 1.4], gap="large")

# ═══════════════════════════════════════════════════════════════════════════════
# LEFT PANEL — Input
# ═══════════════════════════════════════════════════════════════════════════════
with left:
    st.markdown('<div class="section-label">⚙ Session Setup</div>', unsafe_allow_html=True)

    role_options = [
        "Software Engineer", "Data Scientist", "Product Manager",
        "Frontend Developer", "Backend Developer", "DevOps / SRE",
        "Machine Learning Engineer", "Business Analyst", "UX Designer",
        "Marketing Manager", "Sales Executive", "Finance Analyst", "Other"
    ]
    selected_role = st.selectbox("Job Role / Position", role_options,
                                  index=role_options.index(st.session_state.role)
                                  if st.session_state.role in role_options else 0,
                                  label_visibility="visible")
    st.session_state.role = selected_role

    experience = st.selectbox("Experience Level", [
        "Fresher (0–1 yrs)", "Junior (1–3 yrs)",
        "Mid-level (3–6 yrs)", "Senior (6–10 yrs)", "Lead / Principal (10+ yrs)"
    ], label_visibility="visible")

    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">🎙 Interview Question</div>', unsafe_allow_html=True)

    # ── Mic input ──────────────────────────────────────────────────────────
    col_mic, col_clear = st.columns([1, 1])
    with col_mic:
        mic_clicked = st.button("🎙 Record Question", key="mic_btn")
    with col_clear:
        st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
        clear_clicked = st.button("✕ Clear All", key="clear_btn")
        st.markdown('</div>', unsafe_allow_html=True)

    if mic_clicked:
        with st.spinner("🎙 Listening for 5 seconds…"):
            recognizer = sr.Recognizer()
            try:
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=15)
                text = recognizer.recognize_google(audio)
                st.session_state.mic_question = text
                st.success(f"Heard: **{text}**")
            except sr.WaitTimeoutError:
                st.warning("No speech detected. Try again or type the question.")
            except sr.UnknownValueError:
                st.warning("Could not understand audio. Try speaking clearly.")
            except Exception as e:
                st.warning(f"Mic not available: {e}. Please type the question instead.")

    # ── Text input ─────────────────────────────────────────────────────────
    default_q = st.session_state.mic_question if st.session_state.mic_question else ""
    question = st.text_area(
        "Type or paste the interview question here",
        value=default_q,
        height=130,
        placeholder="e.g. Can you explain the difference between a process and a thread?",
        label_visibility="visible",
        key="question_input"
    )

    # ── Generate button ────────────────────────────────────────────────────
    generate_clicked = st.button("⚡ Get Answer Instantly", key="generate_btn")

    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
    st.markdown("""
    <div class="tip-box">
        💡 <strong>Pro tip:</strong> Keep your phone/laptop slightly angled so only you can see the answer.
        Glance naturally — take a breath, then reply confidently.
    </div>
    """, unsafe_allow_html=True)

    if clear_clicked:
        st.session_state.history = []
        st.session_state.current_answer = ""
        st.session_state.question_count = 0
        st.session_state.mic_question = ""
        st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# RIGHT PANEL — Answer display
# ═══════════════════════════════════════════════════════════════════════════════
with right:
    st.markdown('<div class="section-label">💡 AI Answer — Read & Respond</div>', unsafe_allow_html=True)

    answer_placeholder = st.empty()
    history_placeholder = st.empty()

    # ── Render current answer ──────────────────────────────────────────────
    def render_answer(text="", streaming=False):
        if not text:
            answer_placeholder.markdown("""
            <div class="answer-wrapper">
                <div class="answer-header">
                    <div class="answer-header-left">
                        <span>▶</span><span>Answer Display</span>
                    </div>
                    <span style="color:var(--muted);font-size:0.7rem;font-family:'Space Mono',monospace">WAITING</span>
                </div>
                <div class="answer-body">
                    <span class="answer-placeholder">Your answer will appear here instantly once you submit a question. Keep this screen visible during your interview.</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            cls = "answer-body streaming" if streaming else "answer-body"
            status = "● STREAMING" if streaming else "✓ READY"
            sc = "var(--accent)" if not streaming else "var(--warn)"
            answer_placeholder.markdown(f"""
            <div class="answer-wrapper">
                <div class="answer-header">
                    <div class="answer-header-left">
                        <span>▶</span><span>Answer Display</span>
                    </div>
                    <span style="color:{sc};font-size:0.7rem;font-family:'Space Mono',monospace">{status}</span>
                </div>
                <div class="{cls}">{text}</div>
            </div>
            """, unsafe_allow_html=True)

    render_answer(st.session_state.current_answer)

    # ── Generate answer ────────────────────────────────────────────────────
    if generate_clicked and question.strip():
        exp_map = {
            "Fresher (0–1 yrs)": "a fresh graduate with basic knowledge",
            "Junior (1–3 yrs)": "a junior professional with 1-3 years of experience",
            "Mid-level (3–6 yrs)": "a mid-level professional with 3-6 years of experience",
            "Senior (6–10 yrs)": "a senior professional with 6-10 years of experience",
            "Lead / Principal (10+ yrs)": "a lead/principal-level expert with 10+ years of experience",
        }
        exp_desc = exp_map.get(experience, "a professional")

        system_prompt = f"""You are an expert interview coach helping a {exp_desc} applying for a {selected_role} position.

When given an interview question, provide a clear, confident, and impressive answer that:
1. Directly addresses the question
2. Uses the STAR method (Situation, Task, Action, Result) for behavioral questions
3. Includes specific technical details for technical questions
4. Is concise enough to be spoken in 60-90 seconds
5. Sounds natural and conversational, not robotic

Format your answer in clean paragraphs. Use bullet points sparingly. Do NOT use markdown headers.
Start directly with the answer — no preamble like "Great question" or "Certainly"."""

        client = anthropic.Anthropic()
        full_answer = ""
        ts = datetime.now().strftime("%H:%M:%S")

        with client.messages.stream(
            model="claude-sonnet-4-20250514",
            max_tokens=600,
            system=system_prompt,
            messages=[{"role": "user", "content": question.strip()}]
        ) as stream:
            for text_chunk in stream.text_stream:
                full_answer += text_chunk
                render_answer(full_answer, streaming=True)

        st.session_state.current_answer = full_answer
        st.session_state.question_count += 1
        st.session_state.mic_question = ""

        # save to history
        st.session_state.history.insert(0, {
            "q": question.strip(),
            "a": full_answer,
            "time": ts,
            "role": selected_role,
        })

        render_answer(full_answer, streaming=False)

    elif generate_clicked and not question.strip():
        st.warning("Please enter or record a question first.")

    # ── History ────────────────────────────────────────────────────────────
    if st.session_state.history:
        st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
        st.markdown(f'<div class="section-label">📋 Session History ({len(st.session_state.history)} questions)</div>', unsafe_allow_html=True)

        for i, item in enumerate(st.session_state.history[:8]):
            short_a = item["a"][:200] + "…" if len(item["a"]) > 200 else item["a"]
            st.markdown(f"""
            <div class="history-item">
                <div class="history-q">
                    <span style="color:var(--muted);font-family:'Space Mono',monospace;font-size:0.7rem;min-width:20px">Q{len(st.session_state.history)-i}</span>
                    {item["q"]}
                </div>
                <div class="history-a">{short_a}</div>
                <div class="history-time">🕐 {item["time"]} · {item["role"]}</div>
            </div>
            """, unsafe_allow_html=True)
