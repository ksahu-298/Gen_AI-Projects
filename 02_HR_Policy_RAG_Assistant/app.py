import streamlit as st

from hr_assistant.pipeline import build_hr_assistant, ask

st.set_page_config(page_title="HR Policy RAG Assistant", page_icon=":robot_face:")
st.title("HR Policy RAG Assistant")
st.caption("Ask questions about the company's HR policies and get accurate answers based on the provided documents.")

@st.cache_resource(show_spinner="Building the HR assistant...only happens once")
def get_hr_assistant():
    return build_hr_assistant()

agent = get_hr_assistant()

if "messages" not in st.session_state:
    st.session_state.messages = []

#show past messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

#get new message from user
question = st.chat_input("Ask a question about HR policies...")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        response = ask(agent, question)
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        