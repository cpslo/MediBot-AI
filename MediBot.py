
import os
import json
import base64
import pandas as pd
import streamlit as st
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_core.language_models.llms import LLM
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import boto3

# --------------------------
# Claude LLM via Bedrock
# --------------------------
class ClaudeLLM(LLM):
    model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    region_name: str = "us-west-2"
    temperature: float = 0.5
    max_tokens: int = 1000

    def _call(self, prompt: str, **kwargs) -> str:
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }
        client = boto3.client("bedrock-runtime", region_name=self.region_name)
        response = client.invoke_model(
            modelId=self.model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(body)
        )
        result = json.loads(response["body"].read().decode())
        return result["content"][0]["text"].strip()

    def _llm_type(self) -> str:
        return "bedrock-claude"

# --------------------------
# Prompt Template
# --------------------------
CUSTOM_PROMPT_TEMPLATE = """
Use the pieces of information provided in the context to answer the user's question.
If you don't know the answer, just say that you don't know — don't make it up.
Only use information from the provided context.

Context: {context}
Question: {question}

Start the answer directly. Be concise.
"""
def set_custom_prompt(template):
    return PromptTemplate(template=template, input_variables=["context", "question"])

# --------------------------
# Load FAISS vectorstore
# --------------------------
DB_FAISS_PATH = "vectorstore/db_faiss"

@st.cache_resource
def get_vectorstore():
    embedding_model = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
    return FAISS.load_local(DB_FAISS_PATH, embedding_model, allow_dangerous_deserialization=True)

# --------------------------
# Initialize session state
# --------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# --------------------------
# Export Chat as CSV
# --------------------------
def get_chat_as_csv():
    df = pd.DataFrame(st.session_state.messages)
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="medibot_chat_history.csv" title="Download chat as CSV">💬</a>'
    return href

# --------------------------
# Streamlit UI Styling
# --------------------------
st.set_page_config(page_title="MediBot", layout="centered")
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
        .floating-export {
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
            z-index: 100;
        }
        .floating-export a {
            color: white;
            text-decoration: none;
            display: block;
        }
    </style>
""", unsafe_allow_html=True)

# Floating CSV export button
export_link = get_chat_as_csv()
st.markdown(f'<div class="floating-export">{export_link}</div>', unsafe_allow_html=True)

# --------------------------
# Page Header
# --------------------------
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown('<div class="image-box">', unsafe_allow_html=True)
    st.image("MediBot.png", width=300)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="assistant-msg">Ask me anything! I’m here to help you understand symptoms, medications, wellness tips, and more.</div>',
        unsafe_allow_html=True
    )

# --------------------------
# Tailored Quick Topics
# --------------------------
def get_tailored_prompt(topic):
    if topic == "Cold & Flu":
        return "What are the common symptoms of a cold?"

    elif topic == "Medications":
        if st.session_state.messages:
            latest_input = " ".join([m['content'] for m in st.session_state.messages if m['role'] == 'user']).lower()
            keyword_map = {
                "allergy": "What OTC medications help with allergies?",
                "rash": "What OTC treatments are available for skin rashes like poison ivy?",
                "fever": "What OTC medications can help reduce fever?",
                "pain": "What are some common pain relievers available over the counter?",
                "headache": "What are the best OTC medications for headaches?",
                "cold": "What are good OTC remedies for cold and flu symptoms?",
                "cough": "What over-the-counter medications relieve coughing?",
                "itch": "What can relieve itchy skin or insect bites?"
            }
            for keyword, response in keyword_map.items():
                if keyword in latest_input:
                    return response
            return f"Based on the user's prior message: '{latest_input}', suggest appropriate over-the-counter medications."
        else:
            return "What are some commonly used over-the-counter medications?"

    elif topic == "Wellness Tips":
        return "Share some daily wellness and self-care habits."

    return ""

st.markdown("### 🔍 Quick Topics")
c1, c2, c3 = st.columns(3)
if c1.button("🤒 Cold & Flu"):
    st.session_state.quick_prompt = get_tailored_prompt("Cold & Flu")
if c2.button("💊 Medications"):
    st.session_state.quick_prompt = get_tailored_prompt("Medications")
if c3.button("🧘 Wellness Tips"):
    st.session_state.quick_prompt = get_tailored_prompt("Wellness Tips")

# --------------------------
# Show Chat History
# --------------------------
for message in st.session_state.messages:
    st.chat_message(message['role']).markdown(message['content'])

# --------------------------
# Handle Input + Quick Prompt
# --------------------------
user_input = st.chat_input("Ask me anything about your symptoms or medications...")
if 'quick_prompt' in st.session_state:
    prompt = st.session_state.quick_prompt
    del st.session_state.quick_prompt
elif user_input:
    prompt = user_input
else:
    prompt = None

# --------------------------
# Respond to Prompt
# --------------------------
if prompt:
    st.chat_message('user').markdown(prompt)
    st.session_state.messages.append({'role': 'user', 'content': prompt})

    polite_phrases = ["thanks", "thank you", "thank you!", "ok", "okay", "cool", "got it"]
    if prompt.strip().lower() in polite_phrases:
        response_text = "You're welcome! Let me know if you have any other questions. 😊"
        st.chat_message('assistant').markdown(response_text)
        st.session_state.messages.append({'role': 'assistant', 'content': response_text})
        st.stop()
    
    greeting_phrases = ["hello", "hi", "hey", "hello medibot", "hi medibot"]
    if prompt.strip().lower() in greeting_phrases:
        response_text = "Hi there! 👋 I'm MediBot — here to help you with symptoms, medications, and wellness tips. Ask me anything!"
        st.chat_message('assistant').markdown(response_text)
        st.session_state.messages.append({'role': 'assistant', 'content': response_text})
        st.stop()

    try:
        vectorstore = get_vectorstore()
        llm = ClaudeLLM()
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vectorstore.as_retriever(search_kwargs={'k': 3}),
            return_source_documents=False,
            chain_type_kwargs={'prompt': set_custom_prompt(CUSTOM_PROMPT_TEMPLATE)}
        )
        response = qa_chain.invoke({'query': prompt})
        result = response["result"]

        st.chat_message('assistant').markdown(result)
        st.session_state.messages.append({'role': 'assistant', 'content': result})

    except Exception as e:
        st.error(f"⚠️ Error: {str(e)}")
