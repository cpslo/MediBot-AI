
import streamlit as st
import base64
import os
import requests
import json
import tempfile
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

# Sample medical prompt
sample_prompt = """You are a medical expert analyzing patient images. Identify visible symptoms, health issues, or anomalies based on the image. Provide findings, recommendations, and next steps. Always include: 'Consult with a doctor before making any decisions.'

If the image is unclear, say: 'Unable to determine based on the image provided.'"""

# Function: base64 encode image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Function: send image to OpenRouter (Gemma multimodal)
def analyze_image_with_gemma(filename):
    base64_image = encode_image(filename)

    messages = [
        {
            "role": "user",
            "content": [
                { "type": "text", "text": sample_prompt },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}",
                        "detail": "high"
                    }
                }
            ]
        }
    ]

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    body = {
        "model": "google/gemma-3n-e4b-it:free",
        "messages": messages,
        "max_tokens": 1500
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(body))

    if response.status_code != 200:
        return f"❌ Error {response.status_code}: {response.text}"

    return response.json()["choices"][0]["message"]["content"]

# Function: ELI5 explanation
def explain_eli5(text):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "google/gemma-3n-e4b-it:free",
        "messages": [
            {"role": "user", "content": "Explain this like I'm 5:\n" + text}
        ],
        "max_tokens": 600
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(payload))

    if response.status_code != 200:
        return f"❌ Error {response.status_code}: {response.text}"

    return response.json()["choices"][0]["message"]["content"]

# Streamlit UI
st.title("Medical Image Analyzer (Gemma 3n 4B via OpenRouter)")

uploaded_file = st.file_uploader("Upload a medical image (jpg, png)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_filename = tmp_file.name

    st.image(uploaded_file, caption="Uploaded Image")

    if st.button("Analyze Image"):
        result = analyze_image_with_gemma(tmp_filename)
        st.markdown("### 🧠 AI Medical Analysis")
        st.markdown(result, unsafe_allow_html=True)

        if st.radio("Need a simpler explanation?", ["No", "Yes"]) == "Yes":
            simplified = explain_eli5(result)
            st.markdown("### 👶 ELI5 Explanation")
            st.markdown(simplified, unsafe_allow_html=True)

        os.unlink(tmp_filename)
