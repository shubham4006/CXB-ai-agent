import streamlit as st
from openai import OpenAI
import matplotlib.pyplot as plt
from io import BytesIO
from pptx import Presentation
from pptx.util import Inches
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
ITSM Consulting
ITAM Governance
Service Desk Transformation
Automation & AI Ops
Experience Management
Process Optimization
"""

# -----------------------------
# OPENROUTER SETUP (STABLE MODEL)
# -----------------------------
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=st.secrets["OPENROUTER_API_KEY"]
)

MODEL = "openai/gpt-3.5-turbo"  # Stable for demo

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
# PPT GENERATOR
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

            prompt = f"""
            Analyze this RFP and extract:

            - Industry
            - Client Problem
            - Key Requirements
            - Risks
            - Opportunity Summary

            RFP:
            {content[:4000]}
            """

            with st.spinner("Analyzing RFP..."):
                result = ask_ai(prompt)

            st.session_state["rfp_content"] = content
            st.session_state["rfp_analysis"] = result

            st.markdown(result)

            # simple chart
            labels = ["Risk","Complexity","Effort","Impact"]
            values = [3,4,4,5]

            fig, ax = plt.subplots()
            ax.bar(labels, values)
            st.pyplot(fig)

            ppt = create_ppt(result, fig)

            st.download_button("📥 Download PPT", ppt, "RFP_Output.pptx")

# =========================================================
# 2. QUALIFICATION
# =========================================================
elif menu == "Opportunity Qualification":

    st.header("🎯 Opportunity Qualification")

    if "rfp_content" not in st.session_state:
        st.warning("⚠️ Run RFP Intelligence first")
    else:

        prompt = f"""
        Based on RFP and CXBerries capabilities:

        Capabilities:
        {CXB_CAPABILITIES}

        RFP:
        {st.session_state["rfp_content"][:3000]}

        Provide:
        - Strategic Fit
        - Capability Match
        - Risk Level
        - Go / No-Go Decision
        """

        st.markdown(ask_ai(prompt))

# =========================================================
# 3. ASSESSMENT ENGINE (DYNAMIC)
# =========================================================
elif menu == "Assessment Engine":

    st.header("📊 Assessment Engine")

    if "rfp_content" not in st.session_state:
        st.warning("⚠️ Run RFP Intelligence first")
    else:

        prompt = f"""
        Based on RFP:

        {st.session_state["rfp_content"][:3000]}

        Provide:

        - Maturity scoring (Process, Tech, Governance, Data)
        - Gap analysis
        - Risks
        - 90-day roadmap
        """

        st.markdown(ask_ai(prompt))

# =========================================================
# 4. SOLUTION SHAPING
# =========================================================
elif menu == "Solution Shaping":

    st.header("🧠 Solution Shaping")

    if "rfp_content" not in st.session_state:
        st.warning("⚠️ Run RFP Intelligence first")
    else:

        prompt = f"""
        Based on RFP:

        {st.session_state["rfp_content"][:3000]}

        And CXBerries capabilities:

        {CXB_CAPABILITIES}

        Provide SHORT solution:

        - Industry
        - Problem
        - Solution (bullet points)
        - Delivery Model
        - Value

        Keep concise and executive-ready.
        """

        st.markdown(ask_ai(prompt))
