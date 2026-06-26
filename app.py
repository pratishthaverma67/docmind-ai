import streamlit as st
from utils.pdf_processor import extract_text_from_pdf, chunk_text
from utils.llm_client import get_answer, HF_MODELS
from utils.session import init_session_state

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DocMind AI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Claude-inspired design system ─────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

  /* ── Reset & base ── */
  *, *::before, *::after { box-sizing: border-box; }

  html, body, .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background-color: #1a1a1a !important;
    color: #ececec;
  }

  /* ── Sidebar ── */
  section[data-testid="stSidebar"] {
    background-color: #141414 !important;
    border-right: 1px solid #2a2a2a !important;
    padding: 0 !important;
  }
  section[data-testid="stSidebar"] > div {
    padding: 0 !important;
  }
  [data-testid="stSidebarContent"] {
    padding: 20px 16px 24px 16px !important;
  }

  /* ── Main content area ── */
  .main .block-container {
    padding: 0 !important;
    max-width: 100% !important;
  }

  /* ── Hide Streamlit chrome ── */
  #MainMenu, footer, header { visibility: hidden; }
  [data-testid="stToolbar"] { display: none; }
  .stDeployButton { display: none; }

  /* ── Scrollbar ── */
  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-track { background: #1a1a1a; }
  ::-webkit-scrollbar-thumb { background: #3a3a3a; border-radius: 3px; }

  /* ── Sidebar brand header ── */
  .brand-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 4px 0 20px 0;
    border-bottom: 1px solid #2a2a2a;
    margin-bottom: 20px;
  }
  .brand-icon {
    width: 32px; height: 32px;
    background: linear-gradient(135deg, #cc785c 0%, #d4956a 100%);
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; flex-shrink: 0;
  }
  .brand-name {
    font-size: 15px; font-weight: 600;
    color: #ececec; letter-spacing: -0.2px;
  }
  .brand-sub {
    font-size: 11px; color: #666; margin-top: 1px;
  }

  /* ── Sidebar section labels ── */
  .sidebar-label {
    font-size: 11px; font-weight: 600;
    color: #666; letter-spacing: 0.8px;
    text-transform: uppercase;
    margin: 18px 0 8px 0;
  }

  /* ── Token input ── */
  .stTextInput > div > div > input {
    background-color: #242424 !important;
    border: 1px solid #333 !important;
    border-radius: 8px !important;
    color: #ececec !important;
    font-size: 13px !important;
    padding: 8px 12px !important;
    transition: border-color 0.15s;
  }
  .stTextInput > div > div > input:focus {
    border-color: #cc785c !important;
    box-shadow: 0 0 0 3px rgba(204,120,92,0.12) !important;
  }
  .stTextInput > label { color: #999 !important; font-size: 12px !important; }

  /* ── Selectbox ── */
  .stSelectbox > div > div {
    background-color: #242424 !important;
    border: 1px solid #333 !important;
    border-radius: 8px !important;
    color: #ececec !important;
    font-size: 13px !important;
  }
  .stSelectbox > label { color: #999 !important; font-size: 12px !important; }

  /* ── File uploader ── */
  [data-testid="stFileUploader"] {
    background: #242424 !important;
    border: 1.5px dashed #3a3a3a !important;
    border-radius: 10px !important;
    padding: 12px !important;
    transition: border-color 0.2s;
  }
  [data-testid="stFileUploader"]:hover {
    border-color: #cc785c !important;
  }
  [data-testid="stFileUploader"] label {
    color: #999 !important; font-size: 12px !important;
  }

  /* ── Sidebar buttons ── */
  .stButton > button {
    background: #242424 !important;
    border: 1px solid #333 !important;
    color: #ccc !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 6px 14px !important;
    transition: all 0.15s !important;
    width: 100%;
  }
  .stButton > button:hover {
    background: #2e2e2e !important;
    border-color: #cc785c !important;
    color: #ececec !important;
  }

  /* ── Doc stats card ── */
  .doc-stats {
    background: #242424;
    border: 1px solid #2e2e2e;
    border-radius: 10px;
    padding: 12px 14px;
    margin-top: 10px;
  }
  .doc-stats-row {
    display: flex; gap: 12px; margin-bottom: 8px;
  }
  .stat-pill {
    flex: 1;
    background: #1a1a1a;
    border-radius: 7px;
    padding: 8px 10px;
    text-align: center;
  }
  .stat-num {
    font-size: 18px; font-weight: 700;
    color: #cc785c; line-height: 1;
  }
  .stat-lbl {
    font-size: 10px; color: #555;
    margin-top: 3px; text-transform: uppercase; letter-spacing: 0.5px;
  }
  .doc-filename {
    font-size: 11px; color: #555;
    white-space: nowrap; overflow: hidden;
    text-overflow: ellipsis;
    padding-top: 4px;
  }

  /* ── Main chat layout ── */
  .chat-page {
    display: flex; flex-direction: column;
    height: 100vh; overflow: hidden;
  }

  /* ── Top header bar ── */
  .topbar {
    background: #141414;
    border-bottom: 1px solid #2a2a2a;
    padding: 14px 28px;
    display: flex; align-items: center;
    justify-content: space-between;
    flex-shrink: 0;
  }
  .topbar-left { display: flex; align-items: center; gap: 12px; }
  .topbar-icon {
    width: 36px; height: 36px;
    background: linear-gradient(135deg, #cc785c 0%, #e09070 100%);
    border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px;
  }
  .topbar-title {
    font-size: 16px; font-weight: 600;
    color: #ececec; letter-spacing: -0.3px;
  }
  .topbar-sub { font-size: 12px; color: #666; margin-top: 1px; }
  .topbar-badge {
    background: #242424; border: 1px solid #2e2e2e;
    border-radius: 20px; padding: 5px 12px;
    font-size: 12px; color: #888;
    display: flex; align-items: center; gap: 6px;
  }
  .dot-green {
    width: 7px; height: 7px;
    background: #4caf50; border-radius: 50%;
    display: inline-block;
  }

  /* ── Welcome / empty state ── */
  .welcome-wrap {
    flex: 1; display: flex; align-items: center;
    justify-content: center; padding: 40px 20px;
    overflow-y: auto;
  }
  .welcome-card {
    max-width: 520px; width: 100%; text-align: center;
  }
  .welcome-icon {
    width: 64px; height: 64px;
    background: linear-gradient(135deg, #cc785c22, #cc785c44);
    border: 1px solid #cc785c44;
    border-radius: 18px;
    display: flex; align-items: center; justify-content: center;
    font-size: 28px; margin: 0 auto 20px auto;
  }
  .welcome-title {
    font-size: 22px; font-weight: 700;
    color: #ececec; letter-spacing: -0.5px; margin-bottom: 10px;
  }
  .welcome-desc {
    font-size: 14px; color: #888; line-height: 1.6;
    margin-bottom: 28px;
  }
  .step-list {
    text-align: left; background: #242424;
    border: 1px solid #2e2e2e; border-radius: 12px;
    padding: 16px 20px;
  }
  .step-item {
    display: flex; align-items: flex-start;
    gap: 12px; padding: 8px 0;
    border-bottom: 1px solid #2a2a2a;
  }
  .step-item:last-child { border-bottom: none; }
  .step-num {
    width: 24px; height: 24px; flex-shrink: 0;
    background: #cc785c22; border: 1px solid #cc785c44;
    border-radius: 6px; display: flex;
    align-items: center; justify-content: center;
    font-size: 12px; font-weight: 700; color: #cc785c;
  }
  .step-text { font-size: 13px; color: #bbb; line-height: 1.5; padding-top: 2px; }

  /* ── Suggestion chips ── */
  .chips-wrap {
    display: flex; flex-wrap: wrap; gap: 8px;
    justify-content: center; margin-top: 24px;
  }
  .chip {
    background: #242424; border: 1px solid #333;
    border-radius: 20px; padding: 7px 14px;
    font-size: 12px; color: #aaa; cursor: pointer;
    transition: all 0.15s;
    display: inline-block;
  }
  .chip:hover {
    border-color: #cc785c; color: #cc785c;
    background: #cc785c11;
  }

  /* ── Chat messages container ── */
  .messages-area {
    flex: 1; overflow-y: auto;
    padding: 24px 0; scroll-behavior: smooth;
  }
  .msg-row {
    display: flex; padding: 6px 28px;
    gap: 14px; align-items: flex-start;
    max-width: 900px; margin: 0 auto;
  }
  .msg-row.user { flex-direction: row-reverse; }

  /* Avatars */
  .avatar {
    width: 32px; height: 32px; border-radius: 50%;
    flex-shrink: 0; display: flex;
    align-items: center; justify-content: center;
    font-size: 14px; font-weight: 600;
  }
  .avatar-ai {
    background: linear-gradient(135deg, #cc785c, #e09070);
    color: white; font-size: 13px;
  }
  .avatar-user {
    background: #2e2e2e; border: 1px solid #3a3a3a;
    color: #aaa;
  }

  /* Bubbles */
  .bubble {
    max-width: 78%;
    padding: 12px 16px;
    border-radius: 16px;
    font-size: 14px; line-height: 1.65;
    word-break: break-word;
  }
  .bubble-user {
    background: #cc785c;
    color: #fff;
    border-radius: 16px 16px 4px 16px;
  }
  .bubble-ai {
    background: #242424;
    border: 1px solid #2e2e2e;
    color: #ddd;
    border-radius: 16px 16px 16px 4px;
  }
  .bubble-ai p { margin: 0 0 8px 0; }
  .bubble-ai p:last-child { margin-bottom: 0; }
  .bubble-ai ul, .bubble-ai ol {
    margin: 6px 0 6px 18px; padding: 0;
  }
  .bubble-ai li { margin-bottom: 4px; }

  /* Source tag under AI bubble */
  .src-tag {
    display: inline-flex; align-items: center; gap: 5px;
    margin-top: 8px; padding: 3px 10px;
    border-radius: 20px; font-size: 11px; font-weight: 500;
  }
  .src-doc   { background: #1a3a2a; color: #5dbc80; }
  .src-none  { background: #3a1a1a; color: #e07070; }
  .src-error { background: #2a2a1a; color: #e0c070; }

  /* Typing indicator */
  .typing-wrap {
    display: flex; padding: 8px 28px;
    max-width: 900px; margin: 0 auto;
    align-items: center; gap: 14px;
  }
  .typing-dots {
    display: flex; gap: 5px; align-items: center;
    padding: 12px 16px;
    background: #242424; border: 1px solid #2e2e2e;
    border-radius: 16px;
  }
  .typing-dots span {
    width: 7px; height: 7px;
    background: #cc785c; border-radius: 50%;
    animation: bounce 1.2s infinite;
  }
  .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
  .typing-dots span:nth-child(3) { animation-delay: 0.4s; }
  @keyframes bounce {
    0%,80%,100% { transform: translateY(0); opacity: 0.4; }
    40% { transform: translateY(-6px); opacity: 1; }
  }

  /* ── Input bar ── */
  .input-bar-outer {
    border-top: 1px solid #2a2a2a;
    background: #141414;
    padding: 16px 28px 20px 28px;
    flex-shrink: 0;
  }
  .input-bar-inner {
    max-width: 900px; margin: 0 auto;
    display: flex; gap: 10px; align-items: flex-end;
  }
  .stTextInput > div > div > input.chat-input {
    background: #242424 !important;
    border: 1px solid #333 !important;
    border-radius: 12px !important;
    color: #ececec !important;
    font-size: 14px !important;
    padding: 12px 16px !important;
    min-height: 48px;
  }
  .stTextInput > div > div > input.chat-input:focus {
    border-color: #cc785c !important;
    box-shadow: 0 0 0 3px rgba(204,120,92,0.1) !important;
  }
  .send-btn > button {
    background: #cc785c !important;
    border: none !important;
    color: white !important;
    border-radius: 10px !important;
    font-size: 18px !important;
    min-height: 48px !important;
    min-width: 52px !important;
    padding: 0 16px !important;
    font-weight: 600 !important;
    transition: background 0.15s !important;
  }
  .send-btn > button:hover {
    background: #b86848 !important;
  }
  .input-hint {
    font-size: 11px; color: #444;
    text-align: center; margin-top: 8px;
  }

  /* ── Info / warning banners ── */
  .banner {
    max-width: 560px; margin: 40px auto;
    background: #242424; border: 1px solid #333;
    border-radius: 12px; padding: 20px 24px;
    text-align: center;
  }
  .banner-icon { font-size: 28px; margin-bottom: 10px; }
  .banner-title {
    font-size: 15px; font-weight: 600;
    color: #ececec; margin-bottom: 6px;
  }
  .banner-desc { font-size: 13px; color: #888; line-height: 1.5; }
  .banner-link {
    display: inline-block; margin-top: 14px;
    background: #cc785c; color: white;
    border-radius: 8px; padding: 8px 20px;
    font-size: 13px; font-weight: 600;
    text-decoration: none;
  }

  /* Streamlit form cleanup */
  .stForm { background: transparent !important; border: none !important; }
  [data-testid="stFormSubmitButton"] > button {
    background: #cc785c !important;
    border: none !important; color: white !important;
    border-radius: 10px !important;
    font-size: 20px !important;
    min-height: 48px !important; padding: 0 18px !important;
    font-weight: 700 !important;
  }
  [data-testid="stFormSubmitButton"] > button:hover {
    background: #b86848 !important;
  }

  /* Alert / success boxes */
  .stAlert { border-radius: 10px !important; }
  .stSuccess { background: #1a3a2a !important; color: #5dbc80 !important; }
  .stInfo    { background: #1a2a3a !important; color: #70aae0 !important; }
  .stError   { background: #3a1a1a !important; color: #e07070 !important; }

  /* Spinner */
  .stSpinner > div { border-top-color: #cc785c !important; }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
init_session_state()

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    # Brand
    st.markdown("""
    <div class="brand-header">
      <div class="brand-icon">✦</div>
      <div>
        <div class="brand-name">DocMind AI</div>
        <div class="brand-sub">Powered by Hugging Face</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── HF Token ──
    st.markdown('<div class="sidebar-label">API Token</div>', unsafe_allow_html=True)
    api_key_input = st.text_input(
        "HF Token",
        value=st.session_state.get("hf_token", ""),
        type="password",
        placeholder="hf_xxxxxxxxxxxxxxxx",
        label_visibility="collapsed",
        help="Get your free token at huggingface.co/settings/tokens",
    )
    if api_key_input:
        st.session_state["hf_token"] = api_key_input
    st.markdown(
        '<a href="https://huggingface.co/settings/tokens" target="_blank" '
        'style="font-size:12px;color:#cc785c;text-decoration:none;">'
        '↗ Get a free HF token</a>',
        unsafe_allow_html=True,
    )

    # ── Model ──
    st.markdown('<div class="sidebar-label">Model</div>', unsafe_allow_html=True)
    model_label = st.selectbox(
        "Model",
        options=list(HF_MODELS.keys()),
        index=0,
        label_visibility="collapsed",
    )
    st.session_state["model"] = HF_MODELS[model_label]

    # ── Upload ──
    st.markdown('<div class="sidebar-label">Document</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
        label_visibility="collapsed",
    )

    if uploaded_file is not None:
        if uploaded_file.name != st.session_state.get("current_file"):
            with st.spinner("Reading document…"):
                text, page_count = extract_text_from_pdf(uploaded_file)
                if text:
                    chunks = chunk_text(text)
                    st.session_state["doc_text"]     = text
                    st.session_state["doc_chunks"]   = chunks
                    st.session_state["current_file"] = uploaded_file.name
                    st.session_state["page_count"]   = page_count
                    st.session_state["chat_history"] = []
                    st.success(f"✅ {uploaded_file.name}")
                else:
                    st.error("Could not extract text. Is it a scanned/image PDF?")

    # ── Doc stats ──
    if st.session_state.get("doc_text"):
        wc    = len(st.session_state["doc_text"].split())
        pages = st.session_state["page_count"]
        fname = st.session_state["current_file"]
        chunks = len(st.session_state["doc_chunks"])
        st.markdown(f"""
        <div class="doc-stats">
          <div class="doc-stats-row">
            <div class="stat-pill">
              <div class="stat-num">{pages}</div>
              <div class="stat-lbl">Pages</div>
            </div>
            <div class="stat-pill">
              <div class="stat-num">{wc:,}</div>
              <div class="stat-lbl">Words</div>
            </div>
            <div class="stat-pill">
              <div class="stat-num">{chunks}</div>
              <div class="stat-lbl">Chunks</div>
            </div>
          </div>
          <div class="doc-filename">📄 {fname}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Clear chat ──
    if st.session_state.get("chat_history"):
        st.markdown('<div style="margin-top:16px;"></div>', unsafe_allow_html=True)
        if st.button("🗑  Clear conversation", use_container_width=True):
            st.session_state["chat_history"] = []
            st.rerun()

# ── MAIN AREA ─────────────────────────────────────────────────────────────────
has_token = bool(st.session_state.get("hf_token"))
has_doc   = bool(st.session_state.get("doc_text"))

# ── Top bar ──
doc_name = st.session_state.get("current_file", "No document loaded")
if has_doc:
    status_html = f'<span class="dot-green"></span> {doc_name}'
else:
    status_html = "No document loaded"

st.markdown(f"""
<div class="topbar">
  <div class="topbar-left">
    <div class="topbar-icon">✦</div>
    <div>
      <div class="topbar-title">DocMind AI Assistant</div>
      <div class="topbar-sub">Ask anything about your document</div>
    </div>
  </div>
  <div class="topbar-badge">{status_html}</div>
</div>
""", unsafe_allow_html=True)

# ── Guards ────────────────────────────────────────────────────────────────────
if not has_token:
    st.markdown("""
    <div class="banner">
      <div class="banner-icon">🔑</div>
      <div class="banner-title">Connect your Hugging Face account</div>
      <div class="banner-desc">
        Enter your free Hugging Face token in the sidebar to unlock AI-powered
        document analysis. It takes under a minute to create one.
      </div>
      <a class="banner-link" href="https://huggingface.co/settings/tokens" target="_blank">
        Get free token →
      </a>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

if not has_doc:
    suggestions = [
        "Summarize this document",
        "What are the key points?",
        "What is the main topic?",
        "List conclusions or recommendations",
        "What data or statistics are mentioned?",
        "Who are the key people or entities?",
    ]
    chips_html = "".join(f'<span class="chip">{s}</span>' for s in suggestions)
    st.markdown(f"""
    <div class="welcome-wrap">
      <div class="welcome-card">
        <div class="welcome-icon">📄</div>
        <div class="welcome-title">Upload a document to begin</div>
        <div class="welcome-desc">
          DocMind reads your PDF and lets you have a full conversation about it.
          Ask summaries, extract data, compare sections — anything.
        </div>
        <div class="step-list">
          <div class="step-item">
            <div class="step-num">1</div>
            <div class="step-text">Upload a PDF using the sidebar on the left</div>
          </div>
          <div class="step-item">
            <div class="step-num">2</div>
            <div class="step-text">Wait a moment while we extract and index the text</div>
          </div>
          <div class="step-item">
            <div class="step-num">3</div>
            <div class="step-text">Type any question in the chat box below</div>
          </div>
        </div>
        <div class="chips-wrap">{chips_html}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Chat history ──────────────────────────────────────────────────────────────
history = st.session_state["chat_history"]

if not history:
    suggestions = [
        "Summarize this document",
        "What are the key findings?",
        "List the main topics covered",
        "What conclusions are drawn?",
        "Are there any statistics or numbers?",
        "Who or what is this document about?",
    ]
    chips = "".join(f'<span class="chip">{s}</span>' for s in suggestions)
    st.markdown(f"""
    <div style="text-align:center; padding: 40px 28px 20px;">
      <div style="font-size:13px;color:#555;margin-bottom:14px;">
        Document loaded — try a suggestion or type your own question
      </div>
      <div class="chips-wrap" style="justify-content:center;">{chips}</div>
    </div>
    """, unsafe_allow_html=True)
else:
    chat_html = ""
    for msg in history:
        role = msg["role"]
        content = msg["content"].replace("\n", "<br>")
        source = msg.get("source", "document")

        if source == "document":
            tag = '<span class="src-tag src-doc">✓ From document</span>'
        elif source == "not found":
            tag = '<span class="src-tag src-none">⚠ Not in document</span>'
        elif source == "error":
            tag = '<span class="src-tag src-error">⚡ Error</span>'
        else:
            tag = ""

        if role == "user":
            chat_html += f"""
            <div class="msg-row user">
              <div class="avatar avatar-user">U</div>
              <div class="bubble bubble-user">{content}</div>
            </div>"""
        else:
            chat_html += f"""
            <div class="msg-row">
              <div class="avatar avatar-ai">✦</div>
              <div>
                <div class="bubble bubble-ai">{content}</div>
                {tag}
              </div>
            </div>"""

    st.markdown(chat_html, unsafe_allow_html=True)

# ── Input form ────────────────────────────────────────────────────────────────
st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)

with st.form("chat_form", clear_on_submit=True):
    col_q, col_btn = st.columns([11, 1])
    with col_q:
        user_question = st.text_input(
            "question",
            placeholder="Ask anything about your document…",
            label_visibility="collapsed",
        )
    with col_btn:
        submitted = st.form_submit_button("➤")

st.markdown(
    '<div class="input-hint">Enter to send · DocMind answers only from your document</div>',
    unsafe_allow_html=True,
)

# ── Handle suggestion chip clicks (stateful via query params workaround) ──────
if not history:
    suggestions = [
        "Summarize this document",
        "What are the key findings?",
        "List the main topics covered",
        "What conclusions are drawn?",
        "Are there any statistics or numbers?",
        "Who or what is this document about?",
    ]
    cols = st.columns(len(suggestions))
    for i, sug in enumerate(suggestions):
        if cols[i].button(sug, key=f"chip_{i}", use_container_width=True):
            user_question = sug
            submitted = True

# ── Process ───────────────────────────────────────────────────────────────────
if submitted and user_question and user_question.strip():
    q = user_question.strip()
    st.session_state["chat_history"].append({"role": "user", "content": q})

    with st.spinner(""):
        answer, source = get_answer(
            question=q,
            doc_chunks=st.session_state["doc_chunks"],
            chat_history=st.session_state["chat_history"][:-1],
            api_key=st.session_state["hf_token"],
            model=st.session_state["model"],
        )

    st.session_state["chat_history"].append(
        {"role": "assistant", "content": answer, "source": source}
    )
    st.rerun()