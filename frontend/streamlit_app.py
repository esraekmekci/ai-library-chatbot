import sys
import os
import base64
import streamlit as st
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.app import ask

# Logo yükle
current_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(current_dir, "../assets/iyte_logo-eng.png")
logo_base64 = base64.b64encode(open(logo_path, "rb").read()).decode()

leblebi_path = os.path.join(current_dir, "../assets/leblebi-nobg.png")
leblebi_base64 = base64.b64encode(open(leblebi_path, "rb").read()).decode()


# Başlık ve logo
st.markdown(f"""
<div style='display: flex; align-items: center; gap: 20px; margin-top: 10px; font-family: "Segoe UI", sans-serif;'>
    <img src='data:image/png;base64,{leblebi_base64}' width='90'/>
    <div style='display: flex; flex-direction: column;'>
        <div style='font-size: 26px; font-weight: bold;'>Leblebi</div>
        <div style='font-size: 20px; font-weight: 600;'>Chatbot for IZTECH Library</div>
    </div>
</div>
""", unsafe_allow_html=True)


# Stil
st.markdown("""
<style>
.chat-container {
    display: flex;
    flex-direction: column;
    margin-top: 25px;
    font-family: 'Segoe UI', sans-serif;
}

.msg-wrapper {
    margin-bottom: 18px;  /* Sabit boşluk */
}

.msg-row {
    display: flex;
    align-items: flex-end;
}

.user-msg {
    background-color: #d1e7ff;
    color: #003366;
    align-self: flex-end;
    border-radius: 16px 16px 4px 16px;
    padding: 12px 16px;
    max-width: 70%;
    margin-left: auto;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    word-break: break-word;
    overflow-wrap: break-word;
    white-space: pre-wrap;
}

.bot-msg {
    background-color: #f0f0f0;
    color: #333;
    align-self: flex-start;
    border-radius: 16px 16px 16px 4px;
    padding: 12px 16px;
    max-width: 70%;
    margin-right: auto;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    word-break: break-word;
    overflow-wrap: break-word;
    white-space: pre-wrap;
    line-height: 1.4;
}


.icon {
    font-size: 22px;
    margin: 0 8px;
}
</style>
""", unsafe_allow_html=True)


# Mesaj geçmişi başlat
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Hi! I am Leblebi, I can understand the leblebi before you even say leb. How can I assist you with the IZTECH Library today?"
    }]

# Chat mesajlarını göster
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

for message in st.session_state.messages:
    if message["role"] == "user":
        content = message.get("original_query", message["content"])
        st.markdown(f"""
        <div class='msg-wrapper'>
            <div class='msg-row'>
                <div class='user-msg'>{content}</div>
                <div class='icon'>👤</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class='msg-wrapper'>
            <div class='msg-row'>
                <div class='icon'>🤖</div>
                <div class='bot-msg'>{message['content']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)


# Kullanıcı girişi
user_input = st.chat_input("Ask your question about the IZTECH Library...")

if user_input:
    # Göster kullanıcı mesajı
    st.markdown(f"""
    <div class='chat-container'>
        <div class='msg-wrapper'>
            <div class='msg-row' style='justify-content: flex-end;'>
                <div class='user-msg'>{user_input}</div>
                <div class='icon'>👤</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("Thinking..."):
        response, preprocessed_query = ask(user_input, st.session_state.messages)

        # Geçmişe kaydet
        st.session_state.messages.append({
            "role": "user",
            "content": preprocessed_query,
            "original_query": user_input
        })

    # Göster bot cevabı
    st.markdown(f"""
    <div class='chat-container'>
    <div class='msg-row' style='justify-content: flex-start;'>
        <div class='icon'>🤖</div>
        <div class='bot-msg'>{response}</div>
    </div>
    </div>
    """, unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": response})
