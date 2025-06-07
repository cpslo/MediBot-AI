# MediBot – AI Healthcare Assistant

MediBot is an AI-powered healthcare assistant built with Streamlit and AWS Bedrock (Claude 3). It uses a Retrieval-Augmented Generation (RAG) pipeline to help users understand symptoms, medications, and wellness tips in a conversational format.

---

## How to Run MediBot Locally

1. Clone your repository:
   git clone <your-github-repo-url>
   cd <your-project-folder>

2. (Optional) Create and activate a virtual environment:
   python3 -m venv .venv
   source .venv/bin/activate  # for macOS/Linux
   .venv\\Scripts\\activate   # for Windows

3. Install the required dependencies:
   pip install -r requirements.txt

4. Run the app using Streamlit:
   streamlit run medibot.py

---

## Optional: Rebuild the Vector Database

If you want to embed new medical PDFs or retrain the document index:

1. Place your PDFs in the `data/` folder.

2. Run:
   python database.py

This script uses sentence-transformer embeddings to create a searchable FAISS vectorstore.

---

## Features

- Chat interface for asking symptom-related questions
- Quick topic shortcuts (Cold & Flu, Medications, Wellness Tips)
- Context-aware answers retrieved from trusted medical sources
- CSV export of chat history for future reference
