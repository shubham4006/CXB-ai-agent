import streamlit as st
from openai import OpenAI
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from pptx import Presentation
from pptx.util import Inches
from pypdf import PdfReader
import docx
import pandas as pd
import json
import re

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="CXBerries AI Consulting Engine", layout="wide")

st.title("🚀 CXBerries AI Consulting Decision Engine")
st.caption("RFP → Qualification → Assessment → Solution")

# -----------------------------
# CXB CAPABILITIES
# -----------------------------
CXB_CAPABILITIES = """
ITSM Consulting
ITAM Governance
Service Desk Transformation
Automation & AI Ops
Experience Management
Process Optimization
"""

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
# CHUNKING (IMPORTANT FIX)
# -----------------------------
def chunk_text(text, chunk_size=2000):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def summarize_chunks(chunks):
    summaries = []
    for chunk in chunks[:5]:  # limit for performance
        summaries.append(ask_ai(f"Summarize this:\n{chunk}"))
    return "\n".join(summaries)

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
# CHARTS
# -----------------------------
def plot_radar(data):
    labels = ["Risk","Complexity","Effort","Value"]
    values = [
        data["risk_score"],
        data["complexity_score"],
        data["effort_score"],
        data["value_score"]
    ]

    values += values[:1]
    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
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

    ax.set_xlabel("Risk (CXB Delivery Risk)")
    ax.set_ylabel("Value (Business Impact)")

    ax.axhline(3)
    ax.axvline(3)

    return fig

# -----------------------------
# SIDEBAR
# -----------------------------
menu = st.sidebar.selectbox(
    "Select Module",
    ["RFP Intelligence","Opportunity Qualification","Assessment Engine","Solution Shaping"]
)

# =========================================================
# RFP INTELLIGENCE
# =========================================================
if menu == "RFP Intelligence":

    st.header("📑 RFP Intelligence Engine")

    file = st.file_uploader("Upload RFP", type=["txt","pdf","docx","xlsx","csv"])

    if file:

        name = file.name.lower()

        if name.endswith(".pdf"):
            content = read_pdf(file)
        elif name.endswith(".docx"):
            content = read_docx(file)
        elif name.endswith(".xlsx") or name.endswith(".csv"):
            content = read_excel(file)
        else:
            content = file.read().decode("utf-8")

        st.success("📄 Processing full RFP content")

        chunks = chunk_text(content)
        refined_content = summarize_chunks(chunks)

        # JSON extraction
        raw = ask_ai(f"""
        Based ONLY on this RFP summary:

        {refined_content}

        Return JSON:
        {{
          "industry": "",
          "problem": "",
          "risk_score": 1-5,
          "complexity_score": 1-5,
          "effort_score": 1-5,
          "value_score": 1-5
        }}
        """)

        data = safe_parse_json(raw)

        st.session_state["rfp_data"] = data
        st.session_state["rfp_content"] = refined_content

        # SUMMARY
        summary = ask_ai(f"""
        Based ONLY on this RFP:

        {refined_content}

        Provide:
        - Executive Summary (3 bullets)
        - Key Insights (5 bullets)
        - Key Risks (3 bullets)
        """)

        st.subheader("📌 RFP Summary")
        st.markdown(summary)

        st.success(f"Industry: {data['industry']}")
        st.info("📍 Scores from CXBerries delivery perspective")

        # CHARTS
        st.subheader("📊 Multi-Dimensional View")
        st.pyplot(plot_radar(data))

        st.markdown("Radar shows relative intensity across risk, complexity, effort, and value.")

        st.subheader("📍 Opportunity Positioning")
        st.pyplot(plot_matrix(data))

        st.markdown("Matrix shows risk vs value positioning for decision making.")

        # EXPLANATION
        explanation = ask_ai(f"""
        Explain scores based on RFP:

        {refined_content}

        Risk: {data['risk_score']}
        Complexity: {data['complexity_score']}
        Effort: {data['effort_score']}
        Value: {data['value_score']}
        """)

        st.subheader("🧠 Score Justification")
        st.markdown(explanation)

# =========================================================
# OTHER MODULES
# =========================================================
elif menu == "Opportunity Qualification":

    st.header("🎯 Opportunity Qualification")

    if "rfp_data" not in st.session_state:
        st.warning("Run RFP first")
    else:
        data = st.session_state["rfp_data"]

        st.markdown(ask_ai(f"""
        Evaluate opportunity:

        Industry: {data['industry']}
        Problem: {data['problem']}

        CXBerries:
        {CXB_CAPABILITIES}
        """))

elif menu == "Assessment Engine":

    st.header("📊 Assessment Engine")

    if "rfp_data" not in st.session_state:
        st.warning("Run RFP first")
    else:
        st.markdown(ask_ai("Provide maturity and roadmap"))

elif menu == "Solution Shaping":

    st.header("🧠 Solution Shaping")

    if "rfp_data" not in st.session_state:
        st.warning("Run RFP first")
    else:
        data = st.session_state["rfp_data"]

        st.markdown(ask_ai(f"""
        Provide precise solution bullets:

        Industry: {data['industry']}
        Problem: {data['problem']}
        """))
