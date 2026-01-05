# import os
# from urllib import response
# import streamlit as st
# from langchain_groq import ChatGroq
# # from dotenv import load_dotenv


# # load_dotenv()

# os.environ["GROQ_API_KEY"] ="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"


# st.set_page_config(
#     page_title="ChateX",
#     page_icon="🤖",
#     layout="centered",
# )

# st.title("ChateX-chat with intelligence 🤖")

# #intiate the chat history

# # chat_history = []

# if "chat_history" not in st.session_state:
#     st.session_state.chat_history = []


# #show chat history

# for message in st.session_state.chat_history:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])


# #llm intiation

# llm = ChatGroq(
#     model='llama-3.3-70b-versatile',
#     temperature=0.0,

# )

# user_prompt = st.chat_input("Ask your chatbot anything")  #chat input box

# #disploay user prompt in chat message

# if user_prompt:
#     st.session_state.chat_history.append({"role": "user", "content": user_prompt})
#     with st.chat_message("user"):
#         st.markdown(user_prompt)

#     #get the response from llm

#     response = llm.invoke(
#         input=[{"role":"system","content":"You are a helpful assistant."},*st.session_state.chat_history,]
#     )

#     assistant_response = response.content
#     st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})

#     #display the response in chat message

#     with st.chat_message("assistant"):
#         st.markdown(assistant_response)


# #user query -> display user prompt -> get response from llm -> save respone in chat history -> display llm response in chat message


import os
import streamlit as st
from langchain_groq import ChatGroq
import streamlit.components.v1 as components
import whisper
import tempfile


# ==============================
# CONFIG
# ==============================
st.set_page_config(
    page_title="NeuraChat",
    page_icon="🧠✨",
    layout="centered",
)

# ⚠️ Use env / secrets in production
# os.environ["GROQ_API_KEY"] = "YOUR_GROQ_API_KEY"
GROQ_API_KEY= os.getenv("GROQ_API_KEY")

if "pending_voice_text" not in st.session_state:
    st.session_state.pending_voice_text = None

import ssl
ssl._create_default_https_context = ssl._create_unverified_context


@st.cache_resource
def load_whisper():
    return whisper.load_model("base")  # fast & accurate

whisper_model = load_whisper()

# ==============================
# STYLES
# ==============================
st.markdown("""
<style>

/* Floating animation */
@keyframes float {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-6px); }
  100% { transform: translateY(0px); }
}

/* Gradient shimmer */
@keyframes shimmer {
  0% { background-position: 0% 50%; }
  100% { background-position: 200% 50%; }
}

/* Glow pulse */
@keyframes glow {
  0% { text-shadow: 0 0 10px rgba(0,198,255,0.3); }
  50% { text-shadow: 0 0 25px rgba(124,255,0,0.6); }
  100% { text-shadow: 0 0 10px rgba(0,198,255,0.3); }
}

.neura-title {
  font-size: 3.2rem;
  text-align: center;
  font-weight: 800;
  letter-spacing: 1px;

  background: linear-gradient(
    90deg,
    #00c6ff,
    #7cff00,
    #00c6ff
  );
  background-size: 200% 200%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;

  animation:
    float 4s ease-in-out infinite,
    shimmer 6s linear infinite,
    glow 3s ease-in-out infinite;
}

.subtitle {
  text-align: center;
  opacity: 0.85;
  margin-top: -10px;
  font-size: 1.05rem;
  letter-spacing: 0.3px;
}

</style>

<div class="neura-title">🧠✨ Lumio</div>
<div class="subtitle">
Talk • Listen • Think • Respond — powered by Groq ⚡
</div>
""", unsafe_allow_html=True)




# ==============================
# SIDEBAR
# ==============================
with st.sidebar:
    st.markdown("## ⚙️ Controls")
    temperature = st.slider("Creativity", 0.0, 1.0, 0.2)
    stream_mode = st.toggle("Streaming Response", True)
    auto_speak = st.toggle("Auto Speak AI", True)
    st.markdown("---")
    st.markdown("🎙️ Voice Input")
    st.markdown("🎧 AI Voice Output")

# ==============================
# SESSION STATE
# ==============================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ==============================
# VOICE INPUT → TEXT (WHISPER)
# ==============================
audio = st.audio_input("🎙️ Speak")

if audio:
    with st.spinner("🧠 Transcribing speech..."):
        # Save audio to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio.read())
            tmp_path = tmp.name

        # Transcribe
        result = whisper_model.transcribe(tmp_path)
        spoken_text = result["text"].strip()

    st.success("✅ Transcription complete")
    st.write("🗣️ You said:", spoken_text)

    # Auto-fill chat input
    # if spoken_text:
    #     st.session_state.chat_history.append(
    #         {"role": "user", "content": spoken_text}
    #     )

    #     with st.chat_message("user"):
    #         st.markdown(spoken_text)

    if spoken_text:
        st.session_state.pending_voice_text = spoken_text



# ==============================
# DISPLAY CHAT HISTORY
# ==============================
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ==============================
# LLM INIT
# ==============================
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=temperature,
    streaming=True
)

# ==============================
# STREAMING HANDLER
# ==============================
def stream_response(messages):
    container = st.empty()
    full_response = ""

    for chunk in llm.stream(messages):
        if chunk.content:
            full_response += chunk.content
            container.markdown(full_response)

    return full_response

# ==============================
# TEXT TO SPEECH (Browser)
# ==============================
def speak(text):
    components.html(f"""
    <script>
    const msg = new SpeechSynthesisUtterance({text!r});
    msg.rate = 1;
    msg.pitch = 1;
    msg.lang = 'en-US';
    window.speechSynthesis.speak(msg);
    </script>
    """, height=0)

# ==============================
# CHAT INPUT
# ==============================
# user_prompt = st.chat_input("Ask Lumio anything...")

typed_prompt = st.chat_input("Ask Lumio anything...")

user_prompt = None

# Priority: voice to > text
if st.session_state.pending_voice_text:
    user_prompt = st.session_state.pending_voice_text
    st.session_state.pending_voice_text = None
elif typed_prompt:
    user_prompt = typed_prompt


# ==============================
# HANDLE CHAT
# ==============================
if user_prompt:
    st.session_state.chat_history.append(
        {"role": "user", "content": user_prompt}
    )

    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        if stream_mode:
            assistant_reply = stream_response(
                [{"role": "system", "content": "You are a helpful assistant."}]
                + st.session_state.chat_history
            )
        else:
            response = llm.invoke(
                [{"role": "system", "content": "You are a helpful assistant."}]
                + st.session_state.chat_history
            )
            assistant_reply = response.content
            st.markdown(assistant_reply)

        # 🎧 Speak AI response
        if auto_speak:
            speak(assistant_reply)

    st.session_state.chat_history.append(
        {"role": "assistant", "content": assistant_reply}
    )
# USER QUERY -> DISPLAY USER PROMPT -> GET RESPONSE FROM LLM -> SAVE RESPONSE IN CHAT HISTORY -> DISPLAY LLM RESPONSE IN CHAT MESSAGE
