import html
import re
import time
from datetime import datetime

import streamlit as st

from hr_assistant.pipeline import build_hr_assistant, ask

st.set_page_config(page_title="HR Policy Assistant", page_icon="🗂️", layout="centered",
                   initial_sidebar_state="expanded")

# Edit topics and questions so they match what is actually in data/hr_policy.txt
TOPICS = {
    "Leave": ("🏖️", ["How many days of annual leave do I get?",
                       "What is the maternity and paternity leave policy?",
                       "How do I apply for sick leave?"]),
    "Work hours": ("🏠", ["What is the work-from-home policy?",
                           "What are the standard working hours?",
                           "How does overtime work?"]),
    "Pay": ("💳", ["When is salary credited each month?",
                    "How do I claim a medical reimbursement?",
                    "What benefits am I eligible for?"]),
    "Conduct": ("🤝", ["What is the dress code?",
                        "How do I report harassment or a grievance?",
                        "What is the code of conduct?"]),
    "Exit": ("🚪", ["What is the notice period if I resign?",
                     "What happens to my leave balance when I leave?",
                     "How does the full and final settlement work?"]),
    "Growth": ("📈", ["How do performance reviews work?",
                       "Is there a training or learning budget?",
                       "How are promotions decided?"]),
}

FOLLOW_UPS = [
    ("Explain simply", "Please explain this in simple words: {q}"),
    ("Any exceptions?", "Are there any exceptions or special cases for this: {q}"),
    ("Who do I contact?", "Who should I contact in HR about this: {q}"),
]

AVATARS = {"user": "🙂", "assistant": "💼"}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');
.stMarkdown, .stMarkdown p, .stMarkdown li, .stButton button p, .stChatInput textarea,
.hero, .hero * , .section-title { font-family: 'Manrope', system-ui, -apple-system, 'Segoe UI', sans-serif; }

.block-container { max-width: 840px; padding-top: 1.6rem; padding-bottom: 6rem; }
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }

/* Hero banner */
.hero { position: relative; overflow: hidden; border-radius: 22px; padding: 1.7rem 1.8rem 1.5rem;
        background: linear-gradient(135deg, #0F2A43 0%, #1B5560 60%, #1F6F78 100%); color: #fff;
        margin-bottom: 1.4rem; }
.hero-art { position: absolute; right: -20px; top: -30px; width: 62%; opacity: .9; pointer-events: none; }
.hero-body { position: relative; z-index: 1; }
.hero-top { display: flex; gap: 1rem; align-items: center; }
.hero-icon { flex: 0 0 auto; width: 54px; height: 54px; border-radius: 15px; display: grid; place-items: center;
             background: rgba(255,255,255,.16); border: 1px solid rgba(255,255,255,.25); }
.hero h1 { margin: 0; padding: 0; font-size: 1.9rem; font-weight: 800; letter-spacing: -0.02em;
           color: #fff; line-height: 1.15; }
.hero p { margin: .3rem 0 0; color: rgba(255,255,255,.82); font-size: .97rem; max-width: 34rem; }
.stats { display: flex; flex-wrap: wrap; gap: .6rem; margin-top: 1.3rem; }
.stat { background: rgba(255,255,255,.12); border: 1px solid rgba(255,255,255,.18);
        border-radius: 12px; padding: .5rem .85rem; min-width: 118px; }
.stat b { display: block; font-size: 1.15rem; font-weight: 800; color: #fff; }
.stat span { font-size: .76rem; color: rgba(255,255,255,.78); }

.section-title { font-size: 1.05rem; font-weight: 800; color: #14263A; margin: .4rem 0 .6rem; }

/* Buttons */
.stButton > button { border-radius: 12px; border: 1px solid #DDE4EA; background: #fff; color: #14263A;
    text-align: left; justify-content: flex-start; padding: .65rem .9rem; font-weight: 600;
    transition: border-color .15s, background .15s, transform .15s; }
.stButton > button:hover { border-color: #1F6F78; background: #F5FAFA; color: #14555C; transform: translateY(-1px); }
.stButton > button:focus-visible { outline: 2px solid #1F6F78; outline-offset: 2px; }
.stButton > button[kind="primary"] { background: #1F6F78; border-color: #1F6F78; color: #fff; }
.stButton > button[kind="primary"] p { color: #fff; }
.stButton > button:disabled { opacity: .5; transform: none; }

/* Topic cards */
[class*="st-key-topic_"] button { min-height: 96px; flex-direction: column; justify-content: center;
    align-items: center; text-align: center; }
[class*="st-key-topic_"] button p { text-align: center; font-size: .95rem; }

/* Chat */
[data-testid="stChatMessage"] { border-radius: 16px; padding: 1rem 1.15rem; margin-bottom: .7rem;
    background: #fff; border: 1px solid #DDE4EA; }
[data-testid="stChatMessage"],
[data-testid="stChatMessage"] :is(p, li, span, strong, em, label, summary, h1, h2, h3, td, th) { color: #14263A; }
[data-testid="stChatMessage"] .user-bubble { display: inline-block; background: #1F6F78; color: #fff;
    border-radius: 14px; padding: .55rem .9rem; white-space: pre-wrap; line-height: 1.5; }
[data-testid="stChatMessage"] .meta { color: #6B7F90; }
[data-testid="stChatInput"] { border-radius: 14px; border: 1px solid #C9D5DE; background: #fff; }
[data-testid="stChatInput"] textarea { color: #14263A; background: #fff; }
[data-testid="stChatInput"] textarea::placeholder { color: #6B7F90; }
[data-testid="stChatInput"]:focus-within { border-color: #1F6F78; }
.meta { font-size: .78rem; margin-top: .3rem; }

/* Keep the app light even when the browser or Streamlit is in dark mode */
.stApp { background: #F2F5F8; color: #14263A; }
[data-testid="stBottom"] > div, [data-testid="stBottomBlockContainer"] { background: #F2F5F8; }
[data-testid="stSidebar"] { background: #E7EDF2; }
[data-testid="stCaptionContainer"], .stCaption, .stApp .stMarkdown p { color: #3F556A; }
.stButton > button p, .stDownloadButton > button p { color: #14263A; }
.stButton > button[kind="primary"] p { color: #fff; }
.stDownloadButton > button { border-radius: 12px; border: 1px solid #DDE4EA; background: #fff; }
.stApp .hero p { color: rgba(255,255,255,.82); }
.stApp .stMarkdown p.section-title, .stApp .stMarkdown p.side-title { color: #14263A; }

/* Sidebar */
.side-title { font-weight: 800; font-size: 1.02rem; color: #14263A; margin: 0 0 .5rem; }
.step { display: flex; gap: .65rem; margin-bottom: .7rem; color: #3F556A; font-size: .88rem; line-height: 1.45; }
.step i { flex: 0 0 auto; width: 24px; height: 24px; border-radius: 50%; background: #1F6F78; color: #fff;
          font-style: normal; font-weight: 700; font-size: .78rem; display: grid; place-items: center; }
.side-note { background: #fff; border: 1px solid #DDE4EA; border-radius: 12px; padding: .8rem .9rem;
             color: #3F556A; font-size: .85rem; line-height: 1.5; }
</style>
"""


def hero_html(asked: int, last_time) -> str:
    last = f"{last_time:.1f}s" if last_time else "-"
    return f"""
<div class="hero">
  <svg class="hero-art" viewBox="0 0 420 220" fill="none" aria-hidden="true">
    <circle cx="330" cy="70" r="120" stroke="#fff" stroke-opacity=".10" stroke-width="2"/>
    <circle cx="330" cy="70" r="80" stroke="#fff" stroke-opacity=".14" stroke-width="2"/>
    <circle cx="330" cy="70" r="40" fill="#fff" fill-opacity=".06"/>
    <rect x="250" y="120" width="150" height="86" rx="14" fill="#fff" fill-opacity=".07"/>
    <path d="M268 145h84M268 163h116M268 181h62" stroke="#fff" stroke-opacity=".25" stroke-width="6" stroke-linecap="round"/>
  </svg>
  <div class="hero-body">
    <div class="hero-top">
      <div class="hero-icon">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.8"
             stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5"/><path d="m9 14 2 2 4-4"/>
        </svg>
      </div>
      <div>
        <h1>HR Policy Assistant</h1>
        <p>Ask about leave, pay, conduct and more. Answers come straight from your company's HR policy.</p>
      </div>
    </div>
    <div class="stats">
      <div class="stat"><b>{asked}</b><span>Questions asked</span></div>
      <div class="stat"><b>{last}</b><span>Last answer time</span></div>
      <div class="stat"><b>On</b><span>Safety checks</span></div>
    </div>
  </div>
</div>"""


@st.cache_resource(show_spinner="Getting the assistant ready. This only happens once.")
def get_hr_assistant():
    return build_hr_assistant()


def stream_text(text: str, delay: float = 0.010):
    for piece in re.split(r"(\s+)", text):
        if piece:
            yield piece
            time.sleep(delay)


def queue_question(q: str):
    st.session_state.pending_question = q


def toggle_topic(name: str):
    st.session_state.topic = None if st.session_state.get("topic") == name else name


def reset_chat():
    st.session_state.messages = []
    st.session_state.topic = None
    st.session_state.last_time = None
    st.session_state.pop("pending_question", None)


def chat_as_text() -> str:
    lines = []
    for m in st.session_state.get("messages", []):
        who = "You" if m["role"] == "user" else "HR Assistant"
        lines.append(f"{who}: {m['content']}\n")
    return "\n".join(lines)


def show_user(text: str):
    st.markdown(f'<div class="user-bubble">{html.escape(text)}</div>', unsafe_allow_html=True)


def render_history():
    for i, m in enumerate(st.session_state.messages):
        with st.chat_message(m["role"], avatar=AVATARS[m["role"]]):
            if m["role"] == "user":
                show_user(m["content"])
                continue
            st.markdown(m["content"])
            st.markdown(f'<div class="meta">Answered in {m["secs"]:.1f}s at {m["ts"]}</div>',
                        unsafe_allow_html=True)
            if hasattr(st, "feedback"):
                st.feedback("thumbs", key=f"feedback_{i}")


def handle_question(agent, question: str):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user", avatar=AVATARS["user"]):
        show_user(question)

    with st.chat_message("assistant", avatar=AVATARS["assistant"]):
        start = time.perf_counter()
        with st.status("Checking the HR policy...", expanded=False) as status:
            try:
                response = str(ask(agent, question))
                secs = time.perf_counter() - start
                status.update(label=f"Answered in {secs:.1f}s", state="complete")
            except Exception:
                secs = time.perf_counter() - start
                response = ("I couldn't get an answer just now. Please try again in a moment. "
                            "If it keeps happening, contact HR directly.")
                status.update(label="Something went wrong", state="error")
        st.write_stream(stream_text(response))

    st.session_state.last_time = secs
    st.session_state.messages.append({"role": "assistant", "content": response, "secs": secs,
                                      "ts": datetime.now().strftime("%H:%M")})


# ---------------------------------------------------------------- state + layout
st.markdown(CSS, unsafe_allow_html=True)
st.session_state.setdefault("messages", [])
st.session_state.setdefault("topic", None)
st.session_state.setdefault("last_time", None)

with st.sidebar:
    st.markdown('<p class="side-title">How it works</p>', unsafe_allow_html=True)
    st.markdown(
        '<div class="step"><i>1</i><div>Your question is checked for unsafe requests.</div></div>'
        '<div class="step"><i>2</i><div>The most relevant parts of the HR policy are found.</div></div>'
        '<div class="step"><i>3</i><div>The answer is written from those parts and checked again before you see it.</div></div>',
        unsafe_allow_html=True)
    st.markdown('<div class="side-note"><strong>Good to know</strong><br>For personal cases, exceptions or '
                "anything that affects your pay, confirm with HR. Your chat isn't saved once you close the page.</div>",
                unsafe_allow_html=True)
    st.write("")
    has_chat = bool(st.session_state.messages)
    st.button("New conversation", on_click=reset_chat, use_container_width=True, disabled=not has_chat)
    st.download_button("Download this chat", data=chat_as_text(), file_name="hr_chat.txt",
                       mime="text/plain", use_container_width=True, disabled=not has_chat)
    st.caption("Built with LangChain, Groq, Jina embeddings and FAISS.")

asked = sum(1 for m in st.session_state.messages if m["role"] == "user")
st.markdown(hero_html(asked, st.session_state.last_time), unsafe_allow_html=True)

try:
    agent = get_hr_assistant()
except Exception:
    st.error("The assistant couldn't start. Check that GROQ_API_KEY and JINA_API_KEY are set in your "
             "environment or Streamlit secrets, then reload the page.")
    st.stop()

render_history()

typed = st.chat_input("Ask about leave, pay, notice period...", max_chars=500)
question = typed or st.session_state.pop("pending_question", None)

if not question:
    if not st.session_state.messages:
        st.markdown('<p class="section-title">Pick a topic to start</p>', unsafe_allow_html=True)
        cols = st.columns(3)
        for i, (name, (icon, _)) in enumerate(TOPICS.items()):
            cols[i % 3].button(f"{icon}\n\n**{name}**", key=f"topic_{i}", on_click=toggle_topic, args=(name,),
                               type="primary" if st.session_state.topic == name else "secondary",
                               use_container_width=True)
        topic = st.session_state.topic
        if topic:
            st.markdown(f'<p class="section-title">Popular in {topic}</p>', unsafe_allow_html=True)
            for j, q in enumerate(TOPICS[topic][1]):
                st.button(q, key=f"q_{topic}_{j}", on_click=queue_question, args=(q,), use_container_width=True)
        else:
            st.caption("Or type your own question below.")
    else:
        last_q = st.session_state.messages[-2]["content"] if len(st.session_state.messages) >= 2 else ""
        st.caption("Want more detail?")
        cols = st.columns(len(FOLLOW_UPS))
        for k, (label, template) in enumerate(FOLLOW_UPS):
            cols[k].button(label, key=f"follow_{len(st.session_state.messages)}_{k}", on_click=queue_question,
                           args=(template.format(q=last_q),), use_container_width=True)

if question:
    handle_question(agent, question)
    st.rerun()