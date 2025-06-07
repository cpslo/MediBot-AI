
import streamlit as st

# Page config
st.set_page_config(page_title="MediBot", layout="centered")

# --- Custom CSS ---
st.markdown("""
    <style>
        body {
            background-color: #f0f6ff;
        }

        .assistant-msg {
            font-size: 18px;
            text-align: center;
            margin-top: 20px; 
            color: #003366;
            max-width: 300px;
            margin-left: auto;
            margin-right: auto;
        }

        .image-box {
            background-color: transparent;
            padding: 0px;
            box-shadow: none;
            border-radius: 0;
        }

        .floating-chat {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #007bff;
            color: white;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            font-size: 30px;
            text-align: center;
            line-height: 60px;
            cursor: pointer;
            z-index: 100;
        }

        .quick-buttons {
            display: flex;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
            margin-top: 10px;
        }

        .quick-buttons button {
            font-size: 16px;
            padding: 8px 18px;
            border-radius: 8px;
        }
    </style>

    <div class="floating-chat">💬</div>
""", unsafe_allow_html=True)

# --- Centered Layout ---
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown('<div class="image-box">', unsafe_allow_html=True)
    st.image("MediBot.png", width=300)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="assistant-msg">Ask me anything! I’m here to help you understand symptoms, medications, wellness tips, and more.</div>',
        unsafe_allow_html=True
    )

# --- Quick Topics ---
st.markdown("### 🔍 Quick Topics")
c1, c2, c3 = st.columns(3)
with c1:
    st.button("🤒 Cold & Flu")
with c2:
    st.button("💊 Medications")
with c3:
    st.button("🧘 Wellness Tips")

# --- Info Section ---
with st.expander("🩺 What symptoms should I worry about?"):
    st.write("""
        🚨 Seek medical help if you experience:
        - Fever over 102°F (39°C)
        - Chest pain or pressure
        - Shortness of breath
        - Severe headaches
        - Confusion or disorientation
    """)

# --- Chat Input (if using Streamlit 1.23+) ---
user_input = st.chat_input("What symptom are you feeling today?")
if user_input:
    st.markdown(f"**You:** {user_input}")
    st.markdown("**MediBot:** Hmm... sounds like something I can help with. Let me check that out for you 🧠")
