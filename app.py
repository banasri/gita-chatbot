# app.py
import streamlit as st
from query_data import query_rag

st.set_page_config(page_title="Gita Chatbot", page_icon="📘")
st.title("🕉️ Chat with Bhagavad Gita")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "user_input" not in st.session_state:
    st.session_state.user_input = ""

# Handle user input
def submit():
    response = query_rag(st.session_state.user_input)
    st.session_state.chat_history.append((st.session_state.user_input, response))
    st.session_state.user_input = ""  # Clear input field

# Text input with key bound to session state
st.text_input(
    "Ask a question about the Gita:",
    key="user_input",
    on_change=submit,
)

# Show chat history
for q, a in reversed(st.session_state.chat_history):
    st.markdown(f"**You:** {q}")
    st.markdown(f"**Bot:** {a}")
