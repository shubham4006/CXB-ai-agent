import streamlit as st
from openai import OpenAI
import matplotlib.pyplot as plt
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
    slide.shapes.title.text = "Opportunity Snapshot"
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
# 1. RFP INTELLIGENCE
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

            # -----------------------------
            # STEP 1: JSON EXTRACTION
            # -----------------------------
            prompt_json = f"""
            Extract structured insights.

            IMPORTANT:
            - Industry must be business domain (Healthcare, Banking etc.)
            - NOT ITSM/ITAM

            Return JSON:

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
            """

            raw = ask_ai(prompt_json)

            try:
                data = json.loads(raw)
            except:
                st.error("Parsing error")
                st.write(raw)
                st.stop()

            st.session_state["rfp_data"] = data
            st.session_state["rfp_content"] = content

            # -----------------------------
            # STEP 2: SUMMARY
            # -----------------------------
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

            # -----------------------------
            # STEP 3: CHART
            # -----------------------------
            labels = ["Risk", "Complexity", "Effort", "Value"]
            values = [
                data["risk_score"],
                data["complexity_score"],
                data["effort_score"],
                data["value_score"]
            ]

            fig, ax = plt.subplots()
            ax.bar(labels, values)
            st.pyplot(fig)

            # -----------------------------
            # STEP 4: METRICS
            # -----------------------------
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Risk", data["risk_score"])
            c2.metric("Complexity", data["complexity_score"])
            c3.metric("Effort", data["effort_score"])
            c4.metric("Value", data["value_score"])

            # -----------------------------
            # STEP 5: JUSTIFICATION (NEW 🔥)
            # -----------------------------
            explanation = ask_ai(f"""
            Explain why these scores were assigned:

            Risk: {data['risk_score']}
            Complexity: {data['complexity_score']}
            Effort: {data['effort_score']}
            Value: {data['value_score']}

            Based on:
            {content[:3000]}

            Output format:
            - Risk: reason
            - Complexity: reason
            - Effort: reason
            - Value: reason
            """)

            st.subheader("🧠 Score Justification")
            st.markdown(explanation)

            # -----------------------------
            # PPT
            # -----------------------------
            ppt = create_ppt(summary + "\n" + explanation, fig)
            st.download_button("📥 Download PPT", ppt, "RFP_Output.pptx")

# =========================================================
# OTHER MODULES (UNCHANGED LOGIC)
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

        Provide:
        - Fit
        - Go/No-Go
        - Reason
        """))

elif menu == "Assessment Engine":

    st.header("📊 Assessment Engine")

    if "rfp_data" not in st.session_state:
        st.warning("Run RFP first")
    else:
        st.markdown(ask_ai(f"""
        Assess maturity and roadmap:

        {st.session_state['rfp_data']['problem']}
        """))

elif menu == "Solution Shaping":

    st.header("🧠 Solution Shaping")

    if "rfp_data" not in st.session_state:
        st.warning("Run RFP first")
    else:
        data = st.session_state["rfp_data"]

        st.markdown(ask_ai(f"""
        Provide precise solution:

        Industry: {data['industry']}
        Problem: {data['problem']}

        Output bullets only.
        """))
