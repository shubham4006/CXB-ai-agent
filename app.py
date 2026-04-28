import streamlit as st
from openai import OpenAI
import pandas as pd
import matplotlib.pyplot as plt
from pypdf import PdfReader
import docx
from pptx import Presentation
from pptx.util import Inches

# -----------------------
# PAGE
# -----------------------
st.set_page_config(page_title="CXBerries AI Accelerator", layout="wide")

st.title("🚀 CXBERRIES AI Consulting Accelerator")
st.subheader("Reduce proposal, assessment & analysis effort by 50–70%")

# -----------------------
# OPENROUTER CLIENT
# -----------------------
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=st.secrets["OPENROUTER_API_KEY"]
)

def ask_ai(prompt):
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"
def create_ppt(result_text, chart_fig):
    prs = Presentation()

    # Slide 1: Title
    slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(slide_layout)
    slide.shapes.title.text = "RFP Evaluation Summary"
    slide.placeholders[1].text = "AI Consulting Accelerator Output"

    # Slide 2: AI Output (summary)
    slide_layout = prs.slide_layouts[1]
    slide = prs.slides.add_slide(slide_layout)
    slide.shapes.title.text = "Key Insights"

    content = result_text[:1000]  # avoid overflow
    slide.placeholders[1].text = content

    # Slide 3: Chart
    chart_path = "/mnt/data/chart.png"
    chart_fig.savefig(chart_path)

    slide_layout = prs.slide_layouts[5]
    slide = prs.slides.add_slide(slide_layout)
    slide.shapes.title.text = "Risk & Complexity Analysis"
    slide.shapes.add_picture(chart_path, Inches(1), Inches(2), width=Inches(6))

    ppt_path = "/mnt/data/rfp_output.pptx"
    prs.save(ppt_path)

    return ppt_path
# -----------------------
# MENU
# -----------------------
menu = st.sidebar.selectbox(
    "Select Module",
    [
        "Proposal Generator",
        "Assessment Engine",
        "RFP Insights Engine"
    ]
)
# ==========================================
# PROPOSAL GENERATOR
# ==========================================
if menu == "Proposal Generator":

    st.header("📄 Proposal Generator")

    client_name = st.text_input("Client Name")
    industry = st.text_input("Industry")
    problem = st.text_area("Problem Statement")
    scope = st.text_area("Scope Needed")

    if st.button("Generate Proposal"):

        prompt = f"""
        Create a premium consulting proposal.

        Client: {client_name}
        Industry: {industry}
        Problem: {problem}
        Scope: {scope}

        Include:
        1 Executive Summary
        2 Scope of Work
        3 Deliverables
        4 Timeline
        5 Team Structure
        6 Risks
        """

        with st.spinner("Generating Proposal..."):
            result = ask_ai(prompt)

        st.markdown(result)

# ==========================================
# ASSESSMENT
# ==========================================
elif menu == "Assessment Engine":

    st.header("📊 Assessment Engine")

    incident = st.slider("Incident Mgmt",1,5,3)
    change = st.slider("Change Mgmt",1,5,3)
    cmdb = st.slider("CMDB",1,5,3)
    automation = st.slider("Automation",1,5,3)
    reporting = st.slider("Reporting",1,5,3)

    if st.button("Run Assessment"):

        score = (incident + change + cmdb + automation + reporting) / 5

        st.metric("Overall Score", round(score,2))

        labels = ['Incident','Change','CMDB','Automation','Reporting']
        vals = [incident, change, cmdb, automation, reporting]

        fig, ax = plt.subplots()
        ax.bar(labels, vals)
        st.pyplot(fig)

        # -----------------------------
        # ADD THIS AI PART HERE
        # -----------------------------
        prompt = f"""
        Analyze these ITSM maturity scores:

        Incident Management: {incident}
        Change Management: {change}
        CMDB: {cmdb}
        Automation: {automation}
        Reporting: {reporting}

        Give:
        1. Current maturity summary
        2. Top 3 gaps
        3. Recommended actions
        4. 90-day roadmap
        """

        with st.spinner("Generating Recommendations..."):
            result = ask_ai(prompt)

        st.subheader("📌 AI Recommendations")
        st.write(result)

# ==========================================
# DATA INSIGHTS
# ==========================================
elif menu == "RFP Insights Engine":

    st.header("📑 RFP Insights Engine")

    uploaded_file = st.file_uploader(
        "Upload RFP File",
        type=["pdf", "docx", "txt"]
    )

    def read_pdf(file):
        text = ""
        reader = PdfReader(file)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text

    def read_docx(file):
        doc = docx.Document(file)
        return "\n".join([para.text for para in doc.paragraphs])

    if uploaded_file:

        file_name = uploaded_file.name.lower()

        if file_name.endswith(".pdf"):
            content = read_pdf(uploaded_file)
        elif file_name.endswith(".docx"):
            content = read_docx(uploaded_file)
        else:
            content = uploaded_file.read().decode("utf-8")

        st.success("✅ File uploaded successfully")
        st.text_area("Preview Content", content[:3000], height=250)

        # -----------------------------
        # BUTTON BLOCK (CLEAN)
        # -----------------------------
        if st.button("Evaluate RFP/RFQ"):

            prompt = f"""
            Act as a senior consulting partner.

            Analyze the RFP:

            {content[:5000]}

            Provide structured consulting insights including risks, solution, roadmap, team model, and strategy.
            """

            with st.spinner("Evaluating RFP..."):
                result = ask_ai(prompt)

            st.subheader("📌 RFP Evaluation Output")
            st.markdown(result)

            st.markdown("---")

            # 📊 Chart
            st.subheader("📊 Risk & Complexity Visualization")

            labels = ["Risk", "Complexity", "Effort", "Impact"]
            values = [3, 4, 4, 5]

            fig, ax = plt.subplots()
            ax.bar(labels, values)
            st.pyplot(fig)

            st.markdown("---")

            # 📈 Heat Indicator
            st.subheader("📈 Engagement Heat Indicator")

            score = sum(values) / len(values)

            if score >= 4:
                st.success("High Complexity Engagement")
            elif score >= 3:
                st.warning("Moderate Complexity Engagement")
            else:
                st.info("Low Complexity Engagement")

            st.markdown("---")

            # 🔄 Diagram
            st.subheader("🔄 Transformation Journey")

            st.code("""
Current State
    ↓
Assessment & Discovery
    ↓
Future State Design
    ↓
Implementation
    ↓
Steady State Optimization
""")

            st.markdown("---")

            # 📥 PPT Download
            ppt_file = create_ppt(result, fig)

            with open(ppt_file, "rb") as f:
                st.download_button(
                    label="📥 Download PPT Report",
                    data=f,
                    file_name="RFP_Evaluation.pptx",
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                )
            result = ask_ai(prompt)

            st.subheader("📌 RFP Evaluation Output")
            st.write(result)
