"""
ui.py — DocuMind design system.
Accent: Indigo #6366F1  |  Surface: #111111  |  BG: #0A0A0A
"""
import streamlit as st

# ── Tokens ──────────────────────────────────────────────────────────────────
BG      = "#0A0A0A"
SURFACE = "#111111"
BORDER  = "#1E1E1E"
ACCENT  = "#6366F1"
TEXT    = "#F5F5F5"
MUTED   = "#6B7280"
DANGER  = "#EF4444"


def inject_css() -> None:
    st.markdown(f"""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
/* ── RESET ── */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

/* ── BASE ── */
.stApp, html, body {{
    background: {BG} !important;
    color: {TEXT} !important;
    font-family: 'Inter', -apple-system, sans-serif !important;
}}

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
.stDeployButton {{ display: none !important; }}

/* ── MAIN CONTAINER ── */
[data-testid="stAppViewContainer"] {{ background: {BG} !important; }}
[data-testid="stMainBlockContainer"] {{
    background: {BG} !important;
    padding: 2rem 2.5rem !important;
    max-width: 860px !important;
}}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {{
    background: {SURFACE} !important;
    border-right: 1px solid {BORDER} !important;
}}
[data-testid="stSidebar"] > div {{ padding-top: 0 !important; }}
[data-testid="stSidebarContent"] {{ background: {SURFACE} !important; padding: 1.5rem 1rem !important; }}

/* ── ALL TEXT ── */
p, span, label, div, li, h1, h2, h3, h4, h5, h6 {{
    color: {TEXT} !important;
    font-family: 'Inter', sans-serif !important;
}}
h1 {{ font-size: 1.5rem !important; font-weight: 600 !important; letter-spacing: -0.02em; }}
h2, h3 {{ font-weight: 500 !important; }}

/* ── BUTTONS ── */
[data-testid="stButton"] > button {{
    background: transparent !important;
    border: 1px solid {BORDER} !important;
    color: {MUTED} !important;
    border-radius: 6px !important;
    font-size: 0.8rem !important;
    font-family: 'Inter', sans-serif !important;
    padding: 0.35rem 0.75rem !important;
    transition: border-color 0.15s, color 0.15s !important;
    box-shadow: none !important;
}}
[data-testid="stButton"] > button:hover {{
    border-color: {ACCENT} !important;
    color: {TEXT} !important;
    background: rgba(99,102,241,0.06) !important;
}}
[data-testid="baseButton-primary"] {{
    background: {ACCENT} !important;
    border-color: {ACCENT} !important;
    color: #fff !important;
}}
[data-testid="baseButton-primary"]:hover {{
    background: #5254cc !important;
    border-color: #5254cc !important;
    color: #fff !important;
}}

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] {{
    background: {SURFACE} !important;
    border: 1px dashed {BORDER} !important;
    border-radius: 8px !important;
    padding: 0.5rem !important;
}}
[data-testid="stFileUploaderDropzone"] {{
    background: transparent !important;
    border: none !important;
}}
[data-testid="stFileUploader"] * {{ color: {MUTED} !important; }}
[data-testid="stFileUploader"] small {{ color: {MUTED} !important; font-size: 0.75rem !important; }}
[data-testid="stFileUploader"] button {{
    background: transparent !important;
    border: 1px solid {BORDER} !important;
    color: {MUTED} !important;
    border-radius: 5px !important;
}}
[data-testid="stFileUploader"] svg {{ fill: {MUTED} !important; }}

/* ── TEXT INPUT ── */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {{
    background: {SURFACE} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 6px !important;
    color: {TEXT} !important;
    font-family: 'Inter', sans-serif !important;
}}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {{
    border-color: {ACCENT} !important;
    box-shadow: 0 0 0 1px {ACCENT}22 !important;
}}

/* ── CHAT INPUT ── */
[data-testid="stChatInput"] {{
    background: {SURFACE} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 24px !important;
    box-shadow: none !important;
}}
[data-testid="stChatInputTextArea"] {{
    background: transparent !important;
    color: {TEXT} !important;
    font-family: 'Inter', sans-serif !important;
}}
[data-testid="stChatInput"] button {{ background: transparent !important; border: none !important; }}
[data-testid="stChatInput"] button svg {{ fill: {ACCENT} !important; }}

/* ── EXPANDER ── */
[data-testid="stExpander"] {{
    background: {SURFACE} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 8px !important;
}}
[data-testid="stExpander"] summary {{
    color: {MUTED} !important;
    font-size: 0.82rem !important;
    background: transparent !important;
}}
[data-testid="stExpander"] summary:hover {{ color: {TEXT} !important; }}
[data-testid="stExpander"] svg {{ fill: {MUTED} !important; }}

/* ── ALERTS / NOTIFICATIONS ── */
[data-testid="stAlert"],
.stSuccess, .stError, .stWarning, .stInfo,
[class*="stAlert"] {{
    background: {SURFACE} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 8px !important;
    color: {TEXT} !important;
}}
[data-testid="stAlert"] * {{ color: {TEXT} !important; }}
[data-testid="stAlert"] svg {{ display: none !important; }}

/* ── SPINNER ── */
.stSpinner > div {{ border-top-color: {ACCENT} !important; }}
[data-testid="stSpinner"] {{ color: {MUTED} !important; font-size: 0.82rem !important; }}

/* ── COLUMNS ── */
[data-testid="column"] {{ background: transparent !important; }}

/* ── MARKDOWN CONTAINERS ── */
.stMarkdown {{ background: transparent !important; }}
.element-container {{ background: transparent !important; }}

/* ── SCROLLBAR ── */
::-webkit-scrollbar {{ width: 4px; height: 4px; }}
::-webkit-scrollbar-track {{ background: {BG}; }}
::-webkit-scrollbar-thumb {{ background: {BORDER}; border-radius: 4px; }}
::-webkit-scrollbar-thumb:hover {{ background: {MUTED}; }}

/* ── DIVIDER ── */
hr {{ border: none !important; border-top: 1px solid {BORDER} !important; margin: 1rem 0 !important; }}

/* ── PLAIN LABEL ── */
.plain-label {{
    font-size: 0.7rem !important;
    color: {MUTED} !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    margin: 0.75rem 0 0.3rem !important;
    font-weight: 500 !important;
    display: block !important;
}}

/* ── DELETE BUTTON ── */
.btn-danger button,
.btn-danger > div > button {{
    color: {DANGER} !important;
    border-color: transparent !important;
    padding: 0.2rem 0.4rem !important;
    font-size: 0.75rem !important;
    width: auto !important;
}}
.btn-danger button:hover,
.btn-danger > div > button:hover {{
    border-color: {DANGER}44 !important;
    background: {DANGER}11 !important;
    color: {DANGER} !important;
}}
</style>
""", unsafe_allow_html=True)


# ── HTML components ──────────────────────────────────────────────────────────

def sidebar_logo() -> str:
    return f"""
<div style="padding: 1.25rem 0 1rem; border-bottom: 1px solid {BORDER}; margin-bottom: 1rem;">
  <div style="font-size: 1.1rem; font-weight: 600; color: {TEXT}; letter-spacing: -0.01em;">DocuMind</div>
  <div style="font-size: 0.72rem; color: {MUTED}; margin-top: 2px;">RAG Document Intelligence</div>
</div>"""


def stats_row(doc_count: int, total_chunks: int) -> str:
    return f"""
<div style="display: flex; gap: 1rem; margin-bottom: 0.75rem;">
  <div>
    <div style="font-size: 1.1rem; font-weight: 600; color: {ACCENT};">{doc_count}</div>
    <div style="font-size: 0.7rem; color: {MUTED}; text-transform: uppercase; letter-spacing: 0.05em;">Documents</div>
  </div>
  <div>
    <div style="font-size: 1.1rem; font-weight: 600; color: {ACCENT};">{total_chunks}</div>
    <div style="font-size: 0.7rem; color: {MUTED}; text-transform: uppercase; letter-spacing: 0.05em;">Chunks</div>
  </div>
</div>"""


def thinking_indicator() -> str:
    return f"""
<style>
@keyframes _blink {{ 0%,80%,100%{{opacity:0}} 40%{{opacity:1}} }}
._dot {{ display:inline-block; width:6px; height:6px; border-radius:50%; background:{ACCENT}; margin:0 2px; animation:_blink 1.2s infinite; }}
._dot:nth-child(2){{animation-delay:.2s}} ._dot:nth-child(3){{animation-delay:.4s}}
</style>
<div style="display:flex; align-items:center; gap:8px; padding: 10px 0; color:{MUTED}; font-size:0.82rem;">
  <span class="_dot"></span><span class="_dot"></span><span class="_dot"></span>
  <span>Thinking</span>
</div>"""


def empty_state() -> str:
    return f"""
<div style="text-align:center; padding: 4rem 1rem; color:{MUTED};">
  <div style="font-size:2rem; margin-bottom:1rem;">📄</div>
  <div style="font-size:0.95rem; font-weight:500; color:{TEXT}; margin-bottom:0.4rem;">Upload a document to get started</div>
  <div style="font-size:0.82rem;">Supports PDF, Word (.docx), and plain text</div>
</div>"""


def empty_state_no_docs_chat() -> str:
    return f"""
<div style="text-align:center; padding: 3rem 1rem; color:{MUTED};">
  <div style="font-size:0.88rem;">Document indexed — ask your first question below.</div>
</div>"""


def error_card(msg: str) -> str:
    return f"""
<div style="background:{SURFACE}; border:1px solid {DANGER}33; border-radius:8px; padding:10px 14px; font-size:0.8rem; color:{DANGER}; margin: 6px 0;">
  {msg}
</div>"""


def ollama_error_card() -> str:
    return f"""
<div style="background:{SURFACE}; border:1px solid {DANGER}33; border-radius:8px; padding:12px 16px; font-size:0.82rem; color:{MUTED}; margin-bottom:1rem;">
  <span style="color:{DANGER}; font-weight:500;">Ollama is offline.</span>
  Run <code style="background:#1E1E1E; padding:1px 5px; border-radius:3px; font-size:0.78rem; color:{TEXT};">ollama serve</code>
  then
  <code style="background:#1E1E1E; padding:1px 5px; border-radius:3px; font-size:0.78rem; color:{TEXT};">ollama pull mistral</code>
</div>"""


def chat_bubble_user(text: str) -> str:
    import html
    safe = html.escape(text).replace("\n", "<br>")
    return f"""
<div style="display:flex; justify-content:flex-end; margin: 8px 0;">
  <div style="background:{ACCENT}; color:#fff; border-radius:16px 16px 4px 16px;
              padding:10px 14px; max-width:72%; font-size:0.88rem; line-height:1.5;">
    {safe}
  </div>
</div>"""


def chat_bubble_ai(text: str) -> str:
    import html
    safe = html.escape(text).replace("\n", "<br>")
    return f"""
<div style="display:flex; justify-content:flex-start; margin: 8px 0;">
  <div style="background:{SURFACE}; border:1px solid {BORDER}; color:{TEXT};
              border-radius:16px 16px 16px 4px; padding:10px 14px;
              max-width:82%; font-size:0.88rem; line-height:1.5;">
    {safe}
  </div>
</div>"""


def source_card(text: str, source: str, page: int, score: float = 0.0) -> str:
    import html
    preview = html.escape(text[:240]) + ("…" if len(text) > 240 else "")
    return f"""
<div style="background:{BG}; border:1px solid {BORDER}; border-radius:6px;
            padding:10px 12px; margin-bottom:8px; font-size:0.78rem;">
  <div style="color:{MUTED}; margin-bottom:5px;">
    <span style="color:{ACCENT};">{source}</span>
    &nbsp;·&nbsp; page {page}
    &nbsp;·&nbsp; score {score:.2f}
  </div>
  <div style="color:{TEXT}; line-height:1.5; font-family:monospace; white-space:pre-wrap;">{preview}</div>
</div>"""


def doc_item_html(name: str, chunks: int) -> str:
    import html
    safe_name = html.escape(name)
    short = safe_name if len(safe_name) <= 22 else safe_name[:20] + "…"
    return f"""
<div style="padding:6px 0; font-size:0.8rem;">
  <div style="color:{TEXT}; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;"
       title="{safe_name}">{short}</div>
  <div style="color:{MUTED}; font-size:0.7rem;">{chunks} chunks</div>
</div>"""


def custom_divider() -> str:
    return f'<hr style="border:none; border-top:1px solid {BORDER}; margin:0.75rem 0;">'


def success_badge(msg: str) -> str:
    return f"""
<div style="font-size:0.78rem; color:#22c55e; padding:4px 0;">✓ {msg}</div>"""
