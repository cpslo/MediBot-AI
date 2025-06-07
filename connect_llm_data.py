
from transformers import pipeline
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
import os

DB_FAISS_PATH = "vectorstore/db_faiss"

# Load the HF model using transformers
llm_pipeline = pipeline(
    "text-generation",
    model="mistralai/Mistral-7B-Instruct-v0.3",
    torch_dtype="auto",
    device_map="auto"
)

# Prompt template
CUSTOM_PROMPT_TEMPLATE = """
Use the pieces of information provided in the context to answer user's question.
If you don’t know the answer, just say you don’t know. Don’t try to make up an answer. 
Don’t provide anything out of the given context.

Context: {context}
Question: {question}

Start the answer directly. No small talk. Keep the answer short.
"""

def set_custom_prompt(template):
    return PromptTemplate(template=template, input_variables=["context", "question"])

# Load FAISS vectorstore and embedding model
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = FAISS.load_local(DB_FAISS_PATH, embedding_model, allow_dangerous_deserialization=True)

# Main query function
def query_llm(prompt: str) -> str:
    try:
        # Search the vector store for relevant context
        relevant_docs = db.similarity_search(prompt, k=3)
        context = "\n".join([doc.page_content for doc in relevant_docs])

        # Format prompt
        formatted_prompt = CUSTOM_PROMPT_TEMPLATE.format(context=context, question=prompt)

        # Generate response
        result = llm_pipeline(formatted_prompt, max_new_tokens=256, do_sample=True)[0]["generated_text"]
        return result.replace(formatted_prompt, "").strip()
    except Exception as e:
        return f"⚠️ Error during query: {e}"
