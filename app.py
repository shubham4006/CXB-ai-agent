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
st.set_page_config(page_title="CXBerries AI Consulting Engine", layout="wide")

# -----------------------------
# UI
# -----------------------------
st.markdown("""
<style>
.main-title {font-size:34px;font-weight:700;color:#1f4e79;text-align:center;}
.sub-title {text-align:center;color:#6c757d;margin-bottom:20px;}
.card {background:white;padding:18px;border-radius:12px;
box-shadow:0px 4px 10px rgba(0,0,0,0.08);margin-bottom:15px;}
.highlight {background:#f1f7ff;padding:12px;border-left:5px solid #1f77b4;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🚀 CXBerries AI Consulting Engine</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">RFP Intelligence • Qualification • Assessment • Solution</div>', unsafe_allow_html=True)

# -----------------------------
# CXB CAPABILITIES
# -----------------------------
CXB = """
ITSM Consulting
ITAM Governance
Service Desk Transformation
Automation & AI Ops
Experience Management
Process Optimization
"""

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
        messages=[{"role":"user","content":prompt}]
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
    return [text[i:i+size] for i in range(0,len(text),size)]

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
    ax.plot(ang,vals); ax.fill(ang,vals,alpha=0.3)
    ax.set_xticks(ang[:-1]); ax.set_xticklabels(labels)
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

        Give:
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

        st.markdown('<div class="highlight">CXBerries delivery perspective</div>', unsafe_allow_html=True)

        st.pyplot(radar(d))
        st.pyplot(matrix(d))

# =========================================================
# OPPORTUNITY
# =========================================================
elif menu == "Opportunity":

    st.markdown('<div class="card">', unsafe_allow_html=True)

    if "data" not in st.session_state:
        st.warning("Upload RFP first")
    else:
        d = st.session_state["data"]
        t = st.session_state["text"]

        output = ask_ai(f"""
        Based on RFP:
        {t}

        CXBerries capabilities:
        {CXB}

        Identify:

        1. Core opportunity
        2. Adjacent opportunities (cross-sell)
        3. How CXB enhances delivery
        4. Expansion potential

        Be specific to RFP.
        """)

        st.markdown(output)

    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# ASSESSMENT
# =========================================================
elif menu == "Assessment":

    st.markdown('<div class="card">', unsafe_allow_html=True)

    if "data" not in st.session_state:
        st.warning("Upload RFP first")
    else:
        d = st.session_state["data"]
        t = st.session_state["text"]

        output = ask_ai(f"""
        Based on RFP:
        {t}

        Provide:

        1. Current maturity (Low/Medium/High)
        2. Key gaps (bullets)
        3. Detailed roadmap:

           Phase 1 (0-30 days)
           Phase 2 (30-60 days)
           Phase 3 (60-90 days)

        Ensure roadmap aligns with CXBerries services.
        """)

        st.markdown(output)

    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# SOLUTION
# =========================================================
elif menu == "Solution":

    st.markdown('<div class="card">', unsafe_allow_html=True)

    if "data" not in st.session_state:
        st.warning("Upload RFP first")
    else:
        d = st.session_state["data"]
        t = st.session_state["text"]

        output = ask_ai(f"""
        Based on RFP:
        {t}

        Provide concise solution:

        - Approach (3 bullets)
        - Delivery model
        - Value
        """)

        st.markdown(output)

    st.markdown('</div>', unsafe_allow_html=True)
