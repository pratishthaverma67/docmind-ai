import streamlit as st

def init_session_state() -> None:
    defaults = {
        "chat_history": [],
        "doc_text":     "",
        "doc_chunks":   [],
        "current_file": None,
        "page_count":   0,
        "hf_token":     "",
        "model":        "mistralai/Mistral-7B-Instruct-v0.3",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value