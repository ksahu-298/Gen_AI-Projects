import re
import time

import streamlit as st

from hr_assistant.pipeline import build_hr_assistant, ask

# ----------------------------------------------------------------------------
# Page setup
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="HR Policy Assistant",
    page_icon="🗂️",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Edit these so they match what is actually in your hr_policy.txt
SUGGESTED_QUESTIONS = [
    "How many days of annual leave do I get?",
    "What is the notice period if I resign?",
    "What is the work-from-home policy?",
    "How do I claim a medical reimbursement?",
    "What is the maternity and paternity leave policy?",
    "What is the dress code?",
]

# ----------------------------------------------------------------------------
# Styling
# Palette: mist #F2F5F8, ink #14263A, teal #1F6F78, teal tint #DCEEF0, line #DDE4EA
# ----------------------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');

.stMarkdown, .stMarkdown p, .stMarkdown li, .stButton button p,
.stChatInput textarea, .hero h1, .hero p, .side-title, .welcome-title {
    font-family: 'Manrope', system-ui, -apple-system, 'Segoe UI', sans-serif;
}

/* Layout */
.block-container { max-width: 820px; padding-top: 2.2rem; padding-bottom: 6rem; }
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }

/* Header */
.hero { display: flex; gap: 1rem; align-items: center; }
.hero-icon {
    flex: 0 0 auto; width: 52px; height: 52px; border-radius: 14px;
    background: #1F6F78; display: grid; place-items: center;
}
.hero h1 {
    margin: 0; padding: 0; font-size: 1.85rem; font-weight: 800;
    letter-spacing: -0.02em; color: #14263A; line-height: 1.15;
}
.hero p { margin: .25rem 0 0; color: #4B6072; font-size: .98rem; }
.pills { display: flex; flex-wrap: wrap; gap: .5rem; margin: 1rem 0 1.4rem; }
.pill {
    background: #DCEEF0; color: #14555C; font-size: .8rem; font-weight: 600;
    padding: .28rem .7rem; border-radius: 999px;
}

/* Empty state */
.welcome { margin: 2.2rem 0 1rem; }
.welcome-title { font-size: 1.25rem; font-weight: 700; color: #14263A; margin: 0; }
.welcome-sub { color: #4B6072; margin: .25rem 0 0; font-size: .95rem; }

/* Suggestion chips + all buttons */
.stButton > button {
    border-radius: 12px; border: 1px solid #DDE4EA; background: #FFFFFF;
    color: #14263A; text-align: left; justify-content: flex-start;
    padding: .7rem .9rem; font-weight: 600; transition: border-color .15s, background .15s;
}
.stButton > button:hover { border-color: #1F6F78; background: #F5FAFA; color: #14555C; }
.stButton > button:focus-visible { outline: 2px solid #1F6F78; outline-offset: 2px; }
.stButton > button:disabled { opacity: .5; }

/* Chat messages */
[data-testid="stChatMessage"] {
    border-radius: 16px; padding: 1rem 1.15rem; margin-bottom: .7rem;
    background: #FFFFFF; border: 1px solid #DDE4EA;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: #1F6F78; border-color: #1F6F78;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) p,
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) li {
    color: #FFFFFF;
}

/* Chat input */
[data-testid="stChatInput"] { border-radius: 14px; border: 1px solid #C9D5DE; }
[data-testid="stChatInput"]:focus-within { border-color: #1F6F78; }

/* Sidebar */
.side-title { font-weight: 800; font-size: 1.05rem; color: #14263A; margin: 0 0 .2rem; }
.side-text { color: #3F556A; font-size: .9rem; line-height: 1.5; margin: 0 0 1rem; }
.side-note {
    background: #FFFFFF; border: 1px solid #DDE4EA; border-radius: 12px;
    padding: .8rem .9rem; color: #3F556A; font-size: .85rem; line-height: 1.5;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

HERO = """
<div class="hero">
  <div class="hero-icon">
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#fff"
         stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
      <path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/>
      <path d="M14 3v5h5"/>
      <path d="m9 14 2 2 4-4"/>
    </svg>
  </div>
  <div>
    <h1>HR Policy Assistant</h1>
    <p>Ask about leave, benefits, conduct and more. Answers come straight from your company's HR policy.</p>
  </div>
</div>
<div class="pills">
  <span class="pill">Answers from the policy document</span>
  <span class="pill">Safety checks on every reply</span>
</div>
"""

# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
AVATARS = {"user": "🙂", "assistant": "💼"}


@st.cache_resource(show_spinner="Getting the assistant ready. This only happens once.")
def get_hr_assistant():
    return build_hr_assistant()


def stream_text(text: str, delay: float = 0.012):
    """Yield the answer piece by piece so it appears as if typed, keeping formatting intact."""
    for piece in re.split(r"(\s+)", text):
        if piece:
            yield piece
            time.sleep(delay)


def queue_question(question: str):
    st.session_state.pending_question = question


def reset_chat():
    st.session_state.messages = []
    st.session_state.pop("pending_question", None)


def render_history():
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=AVATARS[message["role"]]):
            st.markdown(message["content"])


def handle_question(agent, question: str):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user", avatar=AVATARS["user"]):
        st.markdown(question)

    with st.chat_message("assistant", avatar=AVATARS["assistant"]):
        with st.spinner("Checking the HR policy..."):
            try:
                response = str(ask(agent, question))
            except Exception:
                response = (
                    "I couldn't get an answer just now. Please try again in a moment. "
                    "If it keeps happening, contact HR directly."
                )
        st.write_stream(stream_text(response))

    st.session_state.messages.append({"role": "assistant", "content": response})


# ----------------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown('<p class="side-title">How it works</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="side-text">Your question is matched against the company HR policy, '
        "the most relevant sections are pulled up, and the answer is written from them. "
        "Questions and replies are also checked for unsafe requests.</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="side-note"><strong>Good to know</strong><br>'
        "For personal cases, exceptions or anything that affects your pay, confirm with HR. "
        "Your conversation isn't saved after you close the page.</div>",
        unsafe_allow_html=True,
    )
    st.write("")
    st.button(
        "New conversation",
        on_click=reset_chat,
        use_container_width=True,
        disabled=not st.session_state.get("messages"),
    )
    st.caption("Built with LangChain, Groq, Jina embeddings and FAISS.")

# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
st.markdown(HERO, unsafe_allow_html=True)

try:
    agent = get_hr_assistant()
except Exception:
    st.error(
        "The assistant couldn't start. Check that GROQ_API_KEY and JINA_API_KEY are set "
        "in your environment or Streamlit secrets, then reload the page."
    )
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

render_history()

typed = st.chat_input("Ask about leave, benefits, notice period...", max_chars=500)
question = typed or st.session_state.pop("pending_question", None)

# Empty state: invite the first question
if not st.session_state.messages and not question:
    st.markdown(
        '<div class="welcome"><p class="welcome-title">What would you like to know?</p>'
        '<p class="welcome-sub">Pick a question to start, or type your own below.</p></div>',
        unsafe_allow_html=True,
    )
    cols = st.columns(2)
    for i, q in enumerate(SUGGESTED_QUESTIONS):
        cols[i % 2].button(
            q, key=f"suggestion_{i}", on_click=queue_question, args=(q,), use_container_width=True
        )

if question:
    handle_question(agent, question)
    st.rerun()