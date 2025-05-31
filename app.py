# app.py
import streamlit as st
from query_data import query_rag

st.set_page_config(page_title="Gita Chatbot", page_icon="📘")
st.title("🕉️ Chat with Bhagavad Gita")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.text_input("Ask a question about the Gita:")

if user_input:
    response = query_rag(user_input)
    st.session_state.chat_history.append((user_input, response))

for q, a in reversed(st.session_state.chat_history):
    st.markdown(f"**You:** {q}")
    st.markdown(f"**Bot:** {a}")
