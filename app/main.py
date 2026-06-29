"""
main.py — DocuMind Streamlit entry point.

Run with:
    streamlit run app/main.py
"""

import os
import streamlit as st

# ── Page config — must be the very first Streamlit call ────────────────────
st.set_page_config(
    page_title="DocuMind",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Internal modules ────────────────────────────────────────────────────────
from ui import (
    inject_css,
    sidebar_logo,
    stats_row,
    thinking_indicator,
    empty_state,
    empty_state_no_docs_chat,
    error_card,
    ollama_error_card,
    chat_bubble_user,
    chat_bubble_ai,
    source_card,
    doc_item_html,
    custom_divider,
    success_badge,
)
import llm
import rag as rag_module

# ── Inject CSS immediately ──────────────────────────────────────────────────
inject_css()

# ── Prompt template ─────────────────────────────────────────────────────────
PROMPT_TEMPLATE = (
    "You are a helpful assistant that answers questions based strictly on the "
    "provided document context.\n\n"
    "Answer the question based ONLY on the provided context. "
    "If the answer is not contained in the context, say: "
    "'I could not find an answer to that question in the uploaded documents.'\n\n"
    "Context:\n{context}\n\n"
    "Question: {question}\n\n"
    "Answer:"
)


# ── Cached resource loaders ─────────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading embedding model…")
def get_document_store() -> rag_module.DocumentStore:
    return rag_module.DocumentStore()


# ── Session-state defaults ──────────────────────────────────────────────────
def _init_session_state() -> None:
    defaults = {
        "messages": [],          # list of {role, content, sources}
        "last_upload_name": "",  # track last processed file to avoid double-indexing
        "processing": False,     # flag: currently awaiting LLM
        "upload_success": "",    # ephemeral success message
        "error_message": "",     # ephemeral error message
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


_init_session_state()
store = get_document_store()


# ── Helpers ─────────────────────────────────────────────────────────────────

def _build_context(chunks: list[dict]) -> str:
    parts = []
    for i, c in enumerate(chunks, 1):
        parts.append(
            f"[Source {i}: {c['source']}, page {c['page']}]\n{c['text']}"
        )
    return "\n\n---\n\n".join(parts)


def _answer_question(question: str) -> tuple[str, list[dict]]:
    """
    Retrieve relevant chunks, build prompt, query LLM.
    Returns (answer_text, list_of_source_chunks).
    """
    chunks = store.query(question, top_k=4)

    if not chunks:
        return (
            "No documents have been indexed yet. Please upload a document first.",
            [],
        )

    context = _build_context(chunks)
    prompt = PROMPT_TEMPLATE.format(context=context, question=question)

    messages = [{"role": "user", "content": prompt}]
    answer = llm.chat(messages, stream=False)
    return answer, chunks


# ── Sidebar ─────────────────────────────────────────────────────────────────

def render_sidebar() -> None:
    with st.sidebar:
        # Logo banner
        st.markdown(sidebar_logo(), unsafe_allow_html=True)

        # ── Stats ──────────────────────────────────────────────────────────
        doc_count = len(store.list_documents())
        total_chunks = store.total_chunks()
        st.markdown(stats_row(doc_count, total_chunks), unsafe_allow_html=True)
        st.markdown(custom_divider(), unsafe_allow_html=True)

        # ── File uploader ──────────────────────────────────────────────────
        st.markdown('<p class="plain-label">Upload Document</p>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            label="Upload Document",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=False,
            help="Supported formats: PDF, Word (.docx), plain text (.txt)",
            label_visibility="collapsed",
        )

        if uploaded_file is not None:
            uid = f"{uploaded_file.name}_{uploaded_file.size}"
            if st.session_state.last_upload_name != uid:
                with st.spinner(f"Indexing {uploaded_file.name}…"):
                    try:
                        ext = uploaded_file.name.rsplit(".", 1)[-1].lower()
                        n_chunks = store.add_document(
                            file_bytes=uploaded_file.read(),
                            filename=uploaded_file.name,
                            file_type=ext,
                        )
                        st.session_state.last_upload_name = uid
                        st.session_state.upload_success = (
                            f"Indexed {uploaded_file.name} ({n_chunks} chunks)"
                        )
                    except Exception as exc:
                        st.session_state.error_message = str(exc)

        if st.session_state.upload_success:
            st.markdown(
                success_badge(st.session_state.upload_success),
                unsafe_allow_html=True,
            )
            # Clear after showing
            st.session_state.upload_success = ""

        if st.session_state.error_message:
            st.markdown(
                error_card(st.session_state.error_message),
                unsafe_allow_html=True,
            )
            st.session_state.error_message = ""

        st.markdown(custom_divider(), unsafe_allow_html=True)

        # ── Document list ──────────────────────────────────────────────────
        docs = store.list_documents()
        if docs:
            st.markdown('<p class="plain-label">Indexed Documents</p>', unsafe_allow_html=True)
            chunk_counts = store.document_chunk_count()

            for doc_name in docs:
                col_doc, col_del = st.columns([5, 1])
                with col_doc:
                    st.markdown(
                        doc_item_html(doc_name, chunk_counts.get(doc_name, 0)),
                        unsafe_allow_html=True,
                    )
                with col_del:
                    st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
                    if st.button("✕", key=f"del_{doc_name}", help=f"Remove {doc_name}"):
                        store.delete_document(doc_name)
                        # Also clear last_upload_name so re-uploading same file works
                        st.session_state.last_upload_name = ""
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown(
                '<p style="color:#6e7681;font-size:0.82rem;text-align:center;padding:10px 0;">'
                "No documents indexed yet."
                "</p>",
                unsafe_allow_html=True,
            )

        st.markdown(custom_divider(), unsafe_allow_html=True)

        # ── Clear chat ─────────────────────────────────────────────────────
        if st.session_state.messages:
            if st.button("🗑️  Clear Chat", use_container_width=True):
                st.session_state.messages = []
                st.rerun()

        # ── Model info footer ──────────────────────────────────────────────
        model_name = os.getenv("OLLAMA_MODEL", "mistral")
        ollama_ok = llm.is_ollama_running()
        status_color = "#22c55e" if ollama_ok else "#ef4444"
        status_text = "Online" if ollama_ok else "Offline"
        st.markdown(
            f"""
            <div style="margin-top:auto;padding-top:16px;">
                <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(108,99,255,0.12);
                            border-radius:10px;padding:10px 14px;font-size:0.78rem;color:#8B949E;">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                        <span>&#127968; Model</span>
                        <span style="color:#a5b4fc;font-weight:500;">{model_name}</span>
                    </div>
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span>&#9679; Ollama</span>
                        <span style="color:{status_color};font-weight:500;">{status_text}</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ── Main content ─────────────────────────────────────────────────────────────

def render_chat_history() -> None:
    """Render all past messages in the session."""
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(chat_bubble_user(msg["content"]), unsafe_allow_html=True)
        else:
            st.markdown(chat_bubble_ai(msg["content"]), unsafe_allow_html=True)
            # Sources expander
            sources = msg.get("sources", [])
            if sources:
                with st.expander(f"📎 {len(sources)} source passage(s)", expanded=False):
                    for s in sources:
                        st.markdown(
                            source_card(
                                text=s["text"],
                                source=s["source"],
                                page=s["page"],
                                score=s.get("score", 0.0),
                            ),
                            unsafe_allow_html=True,
                        )


def render_main() -> None:
    docs = store.list_documents()
    has_docs = len(docs) > 0
    has_messages = len(st.session_state.messages) > 0

    # ── Page header ─────────────────────────────────────────────────────────
    st.markdown(
        """
        <h1 style="margin-bottom:4px;">DocuMind</h1>
        <p style="color:#8B949E;font-size:0.92rem;margin-top:0;">
            Ask questions about your documents — get answers with source citations.
        </p>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(custom_divider(), unsafe_allow_html=True)

    # ── Ollama status warning ────────────────────────────────────────────────
    if not llm.is_ollama_running():
        st.markdown(ollama_error_card(), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # ── Empty states ─────────────────────────────────────────────────────────
    if not has_docs and not has_messages:
        st.markdown(empty_state(), unsafe_allow_html=True)

    elif has_docs and not has_messages:
        st.markdown(empty_state_no_docs_chat(), unsafe_allow_html=True)

    # ── Chat history ─────────────────────────────────────────────────────────
    if has_messages:
        render_chat_history()

    # ── Chat input ───────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    user_input = st.chat_input(
        placeholder="Ask a question about your documents…",
        disabled=not has_docs,
    )

    if user_input:
        # Add user message
        st.session_state.messages.append(
            {"role": "user", "content": user_input, "sources": []}
        )

        # Show user bubble immediately
        st.markdown(chat_bubble_user(user_input), unsafe_allow_html=True)

        # Show thinking indicator while waiting
        thinking_placeholder = st.empty()
        thinking_placeholder.markdown(thinking_indicator(), unsafe_allow_html=True)

        answer = ""
        sources: list[dict] = []

        try:
            answer, sources = _answer_question(user_input)
        except Exception as exc:
            err_msg = str(exc)
            if "ConnectionError" in type(exc).__name__ or "ConnectionRefused" in err_msg:
                answer = (
                    "Could not connect to Ollama. Please make sure Ollama is running "
                    "(`ollama serve`) and the model is pulled (`ollama pull mistral`)."
                )
            else:
                answer = f"An error occurred: {err_msg}"

        # Remove thinking indicator
        thinking_placeholder.empty()

        # Persist AI message
        st.session_state.messages.append(
            {"role": "assistant", "content": answer, "sources": sources}
        )

        # Show AI bubble
        st.markdown(chat_bubble_ai(answer), unsafe_allow_html=True)

        if sources:
            with st.expander(f"📎 {len(sources)} source passage(s)", expanded=False):
                for s in sources:
                    st.markdown(
                        source_card(
                            text=s["text"],
                            source=s["source"],
                            page=s["page"],
                            score=s.get("score", 0.0),
                        ),
                        unsafe_allow_html=True,
                    )

        st.rerun()


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    render_sidebar()
    render_main()


if __name__ == "__main__":
    main()
