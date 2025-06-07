
import streamlit as st
import os
import requests
import json
from dotenv import load_dotenv

# Load .env
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")
print(os.getenv("OPENROUTER_API_KEY"))

# Instructions to model
sample_prompt = """You are a medical expert. A patient will describe visual symptoms they see in an image (e.g., redness, wounds, fibers, swelling, or other irregularities). Based on the description, identify potential health issues, suggest next steps, and offer any warnings. Always add: 'Consult with a doctor before making any decisions.'

If the description is unclear or too vague, say: 'Unable to determine based on the description provided.'"""

# Title
st.title("AI Medical Symptom Analysis (Gemma 3n 4B via OpenRouter)")
st.write("This version uses a free text-only AI model. Describe the image instead of uploading it.")

# User input
user_description = st.text_area("Describe the visual symptoms in detail (e.g., 'fibers coming out of red sores')", height=150)

# Function: model analysis
def analyze_description(description):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    full_prompt = f"{sample_prompt}\n\nPatient description: {description}"

    payload = {
        "model": "google/gemma-3n-e4b-it:free",
        "messages": [
            {"role": "user", "content": full_prompt}
        ],
        "max_tokens": 1200
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(payload))

    if response.status_code != 200:
        return f"❌ Error {response.status_code}: {response.text}"

    return response.json()["choices"][0]["message"]["content"]

# Function: simplify the explanation
def explain_eli5(result):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "google/gemma-3n-e4b-it:free",
        "messages": [
            {"role": "user", "content": "Explain this like I'm 5 years old:\n\n" + result}
        ],
        "max_tokens": 600
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(payload))

    if response.status_code != 200:
        return f"❌ Error {response.status_code}: {response.text}"

    return response.json()["choices"][0]["message"]["content"]

# Main logic
if st.button("Analyze Description"):
    if user_description.strip():
        result = analyze_description(user_description)
        st.markdown("### 🧠 Medical AI Result")
        st.markdown(result, unsafe_allow_html=True)

        if st.radio("Want it explained like you're 5?", ["No", "Yes"]) == "Yes":
            simplified = explain_eli5(result)
            st.markdown("### 👶 ELI5 Explanation")
            st.markdown(simplified, unsafe_allow_html=True)
    else:
        st.warning("Please describe the image before clicking Analyze.")
