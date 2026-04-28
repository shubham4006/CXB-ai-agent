import streamlit as st
from openai import OpenAI
import matplotlib.pyplot as plt
import numpy as np
from pypdf import PdfReader
import docx
import pandas as pd
import json, re

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="CXBerries AI Engine", layout="wide")

# -----------------------------
# BEAUTIFIED UI
# -----------------------------
st.markdown("""
<style>

/* Page background */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(to right, #f4f7fb, #eef3f9);
}

/* Main container */
.block-container {
    padding-top: 2rem;
}

/* Title */
.main-title {
    font-size: 36px;
    font-weight: 700;
    color: #1f4e79;
    text-align: center;
}

/* Subtitle */
.sub-title {
    text-align: center;
    color: #6c757d;
    margin-bottom: 25px;
}

/* Card */
.card {
    background: white;
    padding: 20px;
    border-radius: 14px;
    box-shadow: 0px 6px 18px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}

/* Highlight box */
.highlight {
    background: #e8f2ff;
    padding: 14px;
    border-left: 6px solid #1f77b4;
    border-radius: 8px;
    margin-bottom: 15px;
}

/* Buttons */
.stButton>button {
    background: #1f77b4;
    color: white;
    border-radius: 8px;
    padding: 6px 16px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #f1f4f9;
}

/* Section headings */
h3 {
    color: #1f4e79;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# HEADER
# -----------------------------
st.markdown('<div class="main-title">🚀 CXBerries AI Consulting Engine</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">RFP Intelligence • Opportunity • Assessment • Solution</div>', unsafe_allow_html=True)

# -----------------------------
# API
# -----------------------------
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=st.secrets["OPENROUTER_API_KEY"]
)
MODEL = "openai/gpt-3.5-turbo"

def ask_ai(prompt):
    return client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}]
    ).choices[0].message.content

# -----------------------------
# FILE READ
# -----------------------------
def read_file(file):
    if file.name.endswith(".pdf"):
        reader = PdfReader(file)
        return "".join([p.extract_text() or "" for p in reader.pages])
    elif file.name.endswith(".docx"):
        doc = docx.Document(file)
        return "\n".join([p.text for p in doc.paragraphs])
    elif file.name.endswith(".xlsx") or file.name.endswith(".csv"):
        df = pd.read_excel(file)
        return df.to_string()
    else:
        return file.read().decode("utf-8")

# -----------------------------
# CHUNKING
# -----------------------------
def chunk(text, size=2000):
    return [text[i:i+size] for i in range(0, len(text), size)]

def compress(text):
    chunks = chunk(text)
    return "\n".join([ask_ai(f"Summarize:\n{c}") for c in chunks[:5]])

# -----------------------------
# SAFE PARSE
# -----------------------------
def safe_parse(raw):
    try:
        return json.loads(raw)
    except:
        def get(label):
            m = re.search(rf"{label}.*?(\d)", raw, re.I)
            return int(m.group(1)) if m else 3
        return {
            "industry":"Unknown",
            "problem":"Not extracted",
            "risk_score":get("risk"),
            "complexity_score":get("complexity"),
            "effort_score":get("effort"),
            "value_score":get("value")
        }

# -----------------------------
# CHARTS
# -----------------------------
def radar(d):
    labels=["Risk","Complexity","Effort","Value"]
    vals=[d["risk_score"],d["complexity_score"],d["effort_score"],d["value_score"]]
    vals+=vals[:1]
    ang=np.linspace(0,2*np.pi,len(labels),endpoint=False).tolist()+[0]

    fig,ax=plt.subplots(subplot_kw=dict(polar=True))
    ax.plot(ang,vals)
    ax.fill(ang,vals,alpha=0.3)
    ax.set_xticks(ang[:-1])
    ax.set_xticklabels(labels)
    return fig

def matrix(d):
    fig,ax=plt.subplots()
    ax.scatter(d["risk_score"],d["value_score"],s=200)
    ax.set_xlim(0,5); ax.set_ylim(0,5)
    ax.set_xlabel("Risk"); ax.set_ylabel("Value")
    ax.axhline(3); ax.axvline(3)
    return fig

# -----------------------------
# NAV
# -----------------------------
menu = st.sidebar.selectbox("Navigation",
["RFP Intelligence","Opportunity","Assessment","Solution"])

# =========================================================
# RFP INTELLIGENCE
# =========================================================
if menu == "RFP Intelligence":

    st.markdown('<div class="card">', unsafe_allow_html=True)
    file = st.file_uploader("Upload RFP")

    if file:
        text = read_file(file)
        refined = compress(text)

        raw = ask_ai(f"""
        Based ONLY on:
        {refined}

        Return JSON:
        {{
        "industry":"",
        "problem":"",
        "risk_score":1-5,
        "complexity_score":1-5,
        "effort_score":1-5,
        "value_score":1-5
        }}
        """)

        data = safe_parse(raw)
        st.session_state["data"] = data
        st.session_state["text"] = refined

        summary = ask_ai(f"""
        Based ONLY on:
        {refined}

        Provide bullet summary:
        - Executive Summary
        - Key Insights
        - Key Risks
        """)

        st.markdown("### 📌 Summary")
        st.markdown(summary)
        st.success(f"Industry: {data['industry']}")

    st.markdown('</div>', unsafe_allow_html=True)

    if "data" in st.session_state:
        d = st.session_state["data"]

        st.markdown('<div class="highlight">📍 CXBerries Delivery Perspective</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.pyplot(radar(d))
        st.pyplot(matrix(d))
        st.markdown('</div>', unsafe_allow_html=True)

        explain = ask_ai(f"""
        Based on:
        {st.session_state['text']}

        Explain charts in bullet points.
        """)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🧠 Interpretation")
        st.markdown(explain)
        st.markdown('</div>', unsafe_allow_html=True)
