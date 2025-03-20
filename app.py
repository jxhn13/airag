import streamlit as st
from backend.utils import extract_text
from backend.vec import generate_answer
from backend.vec  import generate_question



st.title("📚 AI-Powered Document Search")

uploaded_file = st.file_uploader("Upload a document (PDF or Text file)", type=["txt", "pdf"])

if uploaded_file is not None:
    with st.spinner("Processing..."):
        document_text = extract_text(uploaded_file)
        if document_text:
            st.session_state["document_text"] = document_text

    st.success("✅ Document processed successfully!")



if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

query = st.text_input("🔍 Ask a question about the document or let AI ask you!")

if st.button("Let AI Ask Me"):
    bot_question = generate_question()
    st.session_state["chat_history"].append(("AI", bot_question))
    st.write(f"🤖 AI: {bot_question}")

if query:
    answer = generate_answer(query)
    st.session_state["chat_history"].append(("User", query))
    st.write(f"🤖 AI Answer: {answer}")

st.subheader("📜 Chat History")

for i, question in enumerate(st.session_state["chat_history"]):
    st.write(question)
l

    