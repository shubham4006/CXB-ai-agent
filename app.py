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
# FILE READERS
# -----------------------------
def read_pdf(file):
    reader = PdfReader(file)
    text = ""
    for p in reader.pages:
        if p.extract_text():
            text += p.extract_text()
    return text

def read_docx(file):
    doc = docx.Document(file)
    return "\n".join([p.text for p in doc.paragraphs])

def read_excel(file):
    df = pd.read_excel(file)
    return df.head(50).to_string()

# -----------------------------
# RADAR CHART
# -----------------------------
def plot_radar(data):
    labels = ["Risk", "Complexity", "Effort", "Value"]
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

# -----------------------------
# MATRIX CHART
# -----------------------------
def plot_matrix(data):
    fig, ax = plt.subplots()

    x = data["risk_score"]
    y = data["value_score"]

    ax.scatter(x, y, s=200)

    ax.set_xlim(0,5)
    ax.set_ylim(0,5)

    ax.set_xlabel("Risk")
    ax.set_ylabel("Value")
    ax.set_title("Opportunity Positioning")

    ax.axhline(3)
    ax.axvline(3)

    return fig

# -----------------------------
# PPT
# -----------------------------
def create_ppt(text, fig):
    prs = Presentation()

    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = "RFP Insights"

    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Summary"
    slide.placeholders[1].text = text[:800]

    img = BytesIO()
    fig.savefig(img, format="png")
    img.seek(0)

    slide = prs.slides.add_slide(prs.slide_layouts[5])
    slide.shapes.title.text = "Analysis"
    slide.shapes.add_picture(img, Inches(1), Inches(2), width=Inches(6))

    ppt = BytesIO()
    prs.save(ppt)
    ppt.seek(0)
    return ppt

# -----------------------------
# SIDEBAR
# -----------------------------
menu = st.sidebar.selectbox(
    "Select Module",
    ["RFP Intelligence", "Opportunity Qualification", "Assessment Engine", "Solution Shaping"]
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

        st.text_area("Preview", content[:1500], height=200)

        if st.button("Evaluate RFP"):

            # JSON extraction
            raw = ask_ai(f"""
            Extract:
            {{
              "industry": "",
              "problem": "",
              "risk_score": 1-5,
              "complexity_score": 1-5,
              "effort_score": 1-5,
              "value_score": 1-5
            }}

            RFP:
            {content[:4000]}
            """)

            try:
                data = json.loads(raw)
            except:
                st.error("Parsing error")
                st.write(raw)
                st.stop()

            st.session_state["rfp_data"] = data

            # Summary
            summary = ask_ai(f"""
            Provide:
            - Executive Summary (3 bullets)
            - Key Insights (5 bullets)
            - Key Risks (3 bullets)

            RFP:
            {content[:4000]}
            """)

            st.subheader("📌 RFP Summary")
            st.markdown(summary)

            st.success(f"Industry: {data['industry']}")

            # Radar Chart
            st.subheader("📊 Multi-Dimensional View")
            st.pyplot(plot_radar(data))

            # Matrix Chart
            st.subheader("📍 Opportunity Positioning")
            st.pyplot(plot_matrix(data))

            # Score Explanation
            explanation = ask_ai(f"""
            Explain:
            Risk {data['risk_score']},
            Complexity {data['complexity_score']},
            Effort {data['effort_score']},
            Value {data['value_score']}

            based on RFP.
            """)

            st.subheader("🧠 Score Justification")
            st.markdown(explanation)

            # PPT
            ppt = create_ppt(summary + explanation, plot_radar(data))
            st.download_button("📥 Download PPT", ppt, "RFP_Output.pptx")

# =========================================================
# OTHER MODULES (same)
# =========================================================

elif menu == "Opportunity Qualification":

    st.header("🎯 Opportunity Qualification")

    if "rfp_data" not in st.session_state:
        st.warning("Run RFP first")
    else:
        data = st.session_state["rfp_data"]

        st.markdown(ask_ai(f"""
        Evaluate:
        Industry: {data['industry']}
        Problem: {data['problem']}

        Give Go/No-Go.
        """))

elif menu == "Assessment Engine":

    st.header("📊 Assessment Engine")

    if "rfp_data" not in st.session_state:
        st.warning("Run RFP first")
    else:
        st.markdown(ask_ai("Provide maturity + roadmap"))

elif menu == "Solution Shaping":

    st.header("🧠 Solution Shaping")

    if "rfp_data" not in st.session_state:
        st.warning("Run RFP first")
    else:
        data = st.session_state["rfp_data"]

        st.markdown(ask_ai(f"""
        Provide short solution bullets for:
        {data['problem']}
        """))
