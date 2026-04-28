import streamlit as st
from openai import OpenAI
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from pypdf import PdfReader
import docx
import pandas as pd
import json
import re

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="CXBerries AI Consulting Engine", layout="wide")

# -----------------------------
# UI STYLING
# -----------------------------
st.markdown("""
<style>
.main-title {font-size:34px;font-weight:700;color:#1f4e79;text-align:center;}
.sub-title {text-align:center;color:#6c757d;margin-bottom:20px;}
.card {background:white;padding:18px;border-radius:12px;
box-shadow:0px 4px 10px rgba(0,0,0,0.08);margin-bottom:15px;}
.highlight {background:#f1f7ff;padding:12px;border-left:5px solid #1f77b4;border-radius:6px;}
.stButton>button {background:#1f77b4;color:white;border-radius:8px;}
section[data-testid="stSidebar"] {background:#f8f9fa;}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# HEADER
# -----------------------------
st.markdown('<div class="main-title">🚀 CXBerries AI Consulting Engine</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">AI-powered RFP Intelligence & Decision Support</div>', unsafe_allow_html=True)

# -----------------------------
# METRICS
# -----------------------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Modules", "4")
c2.metric("AI Powered", "Yes")
c3.metric("Speed", "60% Faster")
c4.metric("Focus", "RFP Intelligence")

# -----------------------------
# API SETUP
# -----------------------------
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=st.secrets["OPENROUTER_API_KEY"]
)

MODEL = "openai/gpt-3.5-turbo"

def ask_ai(prompt):
    try:
        res = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# -----------------------------
# SAFE PARSER
# -----------------------------
def safe_parse_json(raw):
    try:
        return json.loads(raw)
    except:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                pass

        def extract_score(label):
            match = re.search(rf"{label}.*?(\d)", raw, re.IGNORECASE)
            return int(match.group(1)) if match else 3

        return {
            "industry": "Unknown",
            "problem": "Not extracted",
            "risk_score": extract_score("risk"),
            "complexity_score": extract_score("complexity"),
            "effort_score": extract_score("effort"),
            "value_score": extract_score("value")
        }

# -----------------------------
# FILE READERS
# -----------------------------
def read_pdf(file):
    reader = PdfReader(file)
    return "".join([p.extract_text() or "" for p in reader.pages])

def read_docx(file):
    doc = docx.Document(file)
    return "\n".join([p.text for p in doc.paragraphs])

def read_excel(file):
    df = pd.read_excel(file)
    return df.head(50).to_string()

# -----------------------------
# CHUNKING
# -----------------------------
def chunk_text(text, size=2000):
    return [text[i:i+size] for i in range(0, len(text), size)]

def summarize_chunks(chunks):
    return "\n".join([ask_ai(f"Summarize:\n{c}") for c in chunks[:5]])

# -----------------------------
# CHARTS
# -----------------------------
def plot_radar(data):
    labels = ["Risk","Complexity","Effort","Value"]
    values = [data["risk_score"],data["complexity_score"],data["effort_score"],data["value_score"]]
    values += values[:1]
    angles = np.linspace(0,2*np.pi,len(labels),endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(subplot_kw=dict(polar=True))
    ax.plot(angles, values)
    ax.fill(angles, values, alpha=0.3)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    return fig

def plot_matrix(data):
    fig, ax = plt.subplots()
    ax.scatter(data["risk_score"], data["value_score"], s=200)
    ax.set_xlim(0,5)
    ax.set_ylim(0,5)
    ax.set_xlabel("Risk")
    ax.set_ylabel("Value")
    ax.axhline(3)
    ax.axvline(3)
    return fig

# -----------------------------
# SIDEBAR
# -----------------------------
menu = st.sidebar.selectbox("Navigation",
["RFP Intelligence","Opportunity Qualification","Assessment","Solution"])

# =========================================================
# RFP INTELLIGENCE
# =========================================================
if menu == "RFP Intelligence":

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("📑 Upload RFP")

    file = st.file_uploader("Upload file", type=["txt","pdf","docx","xlsx","csv"])

    if file:

        if file.name.endswith(".pdf"):
            content = read_pdf(file)
        elif file.name.endswith(".docx"):
            content = read_docx(file)
        elif file.name.endswith(".xlsx") or file.name.endswith(".csv"):
            content = read_excel(file)
        else:
            content = file.read().decode("utf-8")

        st.success("📄 RFP processed successfully")

        chunks = chunk_text(content)
        refined = summarize_chunks(chunks)

        # JSON extraction
        raw = ask_ai(f"""
        Based on this RFP:
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

        data = safe_parse_json(raw)
        st.session_state["rfp_data"] = data
        st.session_state["rfp_text"] = refined

        # SUMMARY
        summary = ask_ai(f"""
        Based ONLY on:
        {refined}

        Provide:
        - Executive Summary (3 bullets)
        - Key Insights (5 bullets)
        - Key Risks (3 bullets)
        """)

        st.markdown('</div>', unsafe_allow_html=True)

        # OUTPUT CARD
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📌 RFP Summary")
        st.markdown(summary)
        st.success(f"Industry: {data['industry']}")
        st.markdown('</div>', unsafe_allow_html=True)

        # CONTEXT BOX
        st.markdown('<div class="highlight">📍 Scores reflect CXBerries delivery perspective</div>', unsafe_allow_html=True)

        # CHARTS
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📊 Multi-Dimensional View")
        st.pyplot(plot_radar(data))

        st.markdown("### 📍 Opportunity Positioning")
        st.pyplot(plot_matrix(data))
        st.markdown('</div>', unsafe_allow_html=True)

        # EXPLANATION
        explanation = ask_ai(f"""
        Explain scores clearly:

        Risk {data['risk_score']}
        Complexity {data['complexity_score']}
        Effort {data['effort_score']}
        Value {data['value_score']}
        """)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🧠 Score Explanation")
        st.markdown(explanation)
        st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# OTHER MODULES
# =========================================================
elif menu == "Opportunity Qualification":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("🎯 Qualification")

    if "rfp_data" in st.session_state:
        data = st.session_state["rfp_data"]
        st.markdown(ask_ai(f"Evaluate opportunity for {data['industry']}"))
    else:
        st.warning("Upload RFP first")
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "Assessment":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("📊 Assessment")
    st.markdown("AI-driven maturity and roadmap (placeholder)")
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "Solution":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("🧠 Solution")

    if "rfp_data" in st.session_state:
        data = st.session_state["rfp_data"]
        st.markdown(ask_ai(f"Provide short solution for {data['problem']}"))
    else:
        st.warning("Upload RFP first")

    st.markdown('</div>', unsafe_allow_html=True)
