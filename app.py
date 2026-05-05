import streamlit as st
from openai import OpenAI
import matplotlib.pyplot as plt
import numpy as np
from pypdf import PdfReader
import docx
import pandas as pd
import json, re
import requests
from bs4 import BeautifulSoup

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="CXBerries AI Engine", layout="wide")

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

st.markdown('<div class="main-title">CXBERRIES AI Consulting Engine</div>', unsafe_allow_html=True)
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
# CXB WEBSITE FETCH
# -----------------------------
@st.cache_data
def fetch_cxb_website():
    try:
        url = "https://www.cxberries.com/"
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        text = soup.get_text(separator=" ")
        text = " ".join(text.split())

        return text[:5000]

    except:
        return "CXB website data not available"

def structure_cxb_capabilities(raw_text):
    return ask_ai(f"""
    Extract CXBerries consulting capabilities.

    Format:

    ### Service Areas
    - ...

    ### Key Offerings
    - ...

    ### Strength Areas
    - ...

    Content:
    {raw_text}

    Rules:
    - Only CXB services
    - Bullet points only
    """)

def get_relevant_capabilities(rfp_text, cxb_capabilities):
    return ask_ai(f"""
    Identify ONLY relevant CXB services for this RFP.

    RFP:
    {rfp_text}

    CXB CAPABILITIES:
    {cxb_capabilities}

    Output:

    ### Relevant CXB Services
    - ...

    ### Why These Fit
    - ...

    Rules:
    - Remove irrelevant services
    - Be precise
    - Bullet points only
    """)

# Load CXB data once
if "cxb_capabilities" not in st.session_state:
    raw_cxb = fetch_cxb_website()
    st.session_state["cxb_capabilities"] = structure_cxb_capabilities(raw_cxb)

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
    file = st.file_uploader("Upload RFP/RFQ")

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

        # 🔥 RELEVANT CAPABILITIES
        relevant_cxb = get_relevant_capabilities(refined, st.session_state["cxb_capabilities"])
        st.session_state["relevant_cxb"] = relevant_cxb

        summary = ask_ai(f"""
        Based ONLY on:
        {refined}

        Provide:

        ### Executive Summary
        - ...

        ### Key Insights
        - ...

        ### Key Risks
        - ...

        Rules:
        - Bullet points only
        """)

        st.markdown(summary)
        st.success(f"Industry: {data['industry']}")

        # Show relevant capabilities
        st.markdown("### 🎯 Relevant CXB Capabilities")
        st.markdown(relevant_cxb)

    st.markdown('</div>', unsafe_allow_html=True)

    if "data" in st.session_state:
        d = st.session_state["data"]

        st.markdown('<div class="highlight">CXBerries Delivery Perspective</div>', unsafe_allow_html=True)

        st.pyplot(radar(d))
        st.pyplot(matrix(d))

# =========================================================
# OPPORTUNITY (SMART)
# =========================================================
elif menu == "Opportunity":

    if "data" not in st.session_state:
        st.warning("Upload RFP first")
    else:
        t = st.session_state["text"]
        cxb = st.session_state["relevant_cxb"]

        result = ask_ai(f"""
        You are a CXBerries consulting strategist.

        RFP:
        {t}

        RELEVANT CXB SERVICES:
        {cxb}

        Provide:

        ### Core Opportunity
        - ...

        ### Cross-Sell Opportunities
        - Only from relevant services

        ### Service Bundling
        - Combine relevant services

        ### CXB Advantage
        - Why CXB wins

        ### Expansion Potential
        - Future opportunities

        Rules:
        - ONLY use listed services
        - Bullet points only
        """)

        st.markdown(result)

# =========================================================
# ASSESSMENT
# =========================================================
elif menu == "Assessment":

    if "data" not in st.session_state:
        st.warning("Upload RFP first")
    else:
        t = st.session_state["text"]

        st.markdown(ask_ai(f"""
        Based on:
        {t}

        Provide:

        ### Current Maturity
        - ...

        ### Key Gaps
        - ...

        ### Roadmap
        - 0–30 days:
        - 30–60 days:
        - 60–90 days:

        Rules:
        - Bullet points only
        """))

# =========================================================
# SOLUTION
# =========================================================
elif menu == "Solution":

    if "data" not in st.session_state:
        st.warning("Upload RFP first")
    else:
        t = st.session_state["text"]

        st.markdown(ask_ai(f"""
        Based on:
        {t}

        Provide:

        ### Approach
        - ...

        ### Delivery Model
        - ...

        ### Value
        - ...

        Rules:
        - Bullet points only
        """))
