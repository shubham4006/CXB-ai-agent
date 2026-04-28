import streamlit as st
from openai import OpenAI
import matplotlib.pyplot as plt
from pptx import Presentation
from pptx.util import Inches
from io import BytesIO
from pypdf import PdfReader
import docx
import pandas as pd

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="CXBerries AI Consulting Engine", layout="wide")

st.title("🚀 CXBerries AI Consulting Decision Engine")
st.caption("RFP → Qualification → Assessment → Solution")

# -----------------------------
# CXBERRIES CAPABILITIES
# -----------------------------
CXB_CAPABILITIES = """
CXBerries provides:
- ITSM Consulting
- ITAM Governance & Optimization
- Service Desk Transformation
- Automation & AI Ops
- Experience Management
- Process Consulting & Optimization
"""

# -----------------------------
# API SETUP
# -----------------------------
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=st.secrets["OPENROUTER_API_KEY"]
)

MODEL = "meta-llama/llama-3-8b-instruct:free"

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

            prompt = f"""
            Analyze this RFP and extract:

            1. Industry
            2. Client Problem Statement
            3. Key Requirements
            4. Risks
            5. Opportunity Summary

            RFP:
            {content[:4000]}
            """

            result = ask_ai(prompt)

            st.session_state["rfp_content"] = content
            st.session_state["rfp_analysis"] = result

            st.markdown(result)

# =========================================================
# QUALIFICATION
# =========================================================
elif menu == "Opportunity Qualification":

    st.header("🎯 Opportunity Qualification")

    if "rfp_content" not in st.session_state:
        st.warning("⚠️ Upload and evaluate RFP first")
    else:

        prompt = f"""
        Based on this RFP and CXBerries capabilities:

        Capabilities:
        {CXB_CAPABILITIES}

        RFP:
        {st.session_state["rfp_content"][:3000]}

        Evaluate:
        - Strategic Fit
        - Capability Match
        - Risk Level
        - Go / No-Go decision
        """

        result = ask_ai(prompt)
        st.markdown(result)

# =========================================================
# ASSESSMENT ENGINE (DYNAMIC)
# =========================================================
elif menu == "Assessment Engine":

    st.header("📊 Assessment Engine")

    if "rfp_content" not in st.session_state:
        st.warning("⚠️ Upload RFP first")
    else:

        prompt = f"""
        Based on this RFP:

        {st.session_state["rfp_content"][:3000]}

        Provide:
        1. Maturity level (1-5 scale for Process, Tech, Governance, Data)
        2. Gap analysis
        3. Risk areas
        4. Transformation roadmap
        """

        result = ask_ai(prompt)
        st.markdown(result)

# =========================================================
# SOLUTION SHAPING (AUTO)
# =========================================================
elif menu == "Solution Shaping":

    st.header("🧠 Solution Shaping")

    if "rfp_content" not in st.session_state:
        st.warning("⚠️ Upload RFP first")
    else:

        prompt = f"""
        Based on RFP:

        {st.session_state["rfp_content"][:3000]}

        And CXBerries capabilities:

        {CXB_CAPABILITIES}

        Generate a SHORT consulting solution:

        - Industry
        - Problem
        - Solution (bullet points)
        - Delivery Model
        - Key Value

        Keep it crisp and executive-ready.
        """

        result = ask_ai(prompt)
        st.markdown(result)
