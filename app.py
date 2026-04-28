import streamlit as st
from openai import OpenAI
import matplotlib.pyplot as plt
from pptx import Presentation
from pptx.util import Inches
from io import BytesIO

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="CXBERRIES AI Consulting Engine", layout="wide")

# -----------------------------
# CUSTOM UI
# -----------------------------
st.markdown("""
<style>
.main-title {
    font-size: 36px;
    font-weight: 700;
    color: #1f4e79;
    text-align: center;
}
.sub-title {
    font-size: 18px;
    text-align: center;
    color: #555;
    margin-bottom: 20px;
}
.card {
    background-color: white;
    padding: 18px;
    border-radius: 12px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
    margin-bottom: 15px;
}
.stButton>button {
    background-color: #1f77b4;
    color: white;
    border-radius: 8px;
    padding: 8px 16px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# HEADER
# -----------------------------
st.markdown('<div class="main-title">🚀 CXBERRIES AI Consulting Decision Engine</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">AI-powered consulting accelerator for RFP evaluation, diagnostics & solution design</div>', unsafe_allow_html=True)

# -----------------------------
# METRICS
# -----------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Modules", "4")
col2.metric("Use Cases", "RFP / ITSM / ITAM")
col3.metric("Efficiency Gain", "60%")
col4.metric("AI Powered", "Yes")

st.markdown("### 🧩 Capabilities")

col1, col2 = st.columns(2)
with col1:
    st.markdown('<div class="card"><b>📑 RFP Intelligence</b><br>Analyze RFPs and extract insights.</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="card"><b>🎯 Qualification</b><br>Evaluate bid feasibility.</div>', unsafe_allow_html=True)

col3, col4 = st.columns(2)
with col3:
    st.markdown('<div class="card"><b>📊 Assessment</b><br>Maturity & gap analysis.</div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="card"><b>🧠 Solution Design</b><br>Build consulting solution.</div>', unsafe_allow_html=True)

st.markdown("---")

# -----------------------------
# OPENAI
# -----------------------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def ask_ai(prompt):
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# -----------------------------
# PPT FUNCTION
# -----------------------------
def create_ppt(result, fig):
    prs = Presentation()

    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = "RFP Evaluation"
    slide.placeholders[1].text = "CXBerries AI Accelerator"

    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Insights"
    slide.placeholders[1].text = result[:1000]

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
st.sidebar.markdown("## 🧭 Navigation")
menu = st.sidebar.selectbox(
    "Select Module",
    ["RFP Intelligence", "Opportunity Qualification", "Assessment Engine", "Solution Shaping"]
)

# =========================================================
# RFP INTELLIGENCE
# =========================================================
if menu == "RFP/RFQ Intelligence":

    st.header("📑 RFP Intelligence Engine")

    file = st.file_uploader("Upload RFP (.txt)", type=["txt"])

    if file:
        content = file.read().decode("utf-8")

        st.text_area("Preview", content[:1500], height=200)

        if st.button("Evaluate RFP/RFQ"):

            prompt = f"""
            Analyze this RFP:

            {content[:4000]}

            Provide:
            - Summary
            - Risks
            - Solution direction
            - Win strategy
            """

            with st.spinner("Analyzing..."):
                result = ask_ai(prompt)

            st.markdown(result)

            st.markdown("---")

            labels = ["Risk", "Complexity", "Effort", "Impact"]
            values = [3,4,4,5]

            fig, ax = plt.subplots()
            ax.bar(labels, values)
            st.pyplot(fig)

            ppt = create_ppt(result, fig)

            st.download_button("📥 Download PPT", ppt, "RFP_Output.pptx")

# =========================================================
# QUALIFICATION
# =========================================================
elif menu == "Opportunity Qualification":

    st.header("🎯 Qualification Engine")

    s = st.slider("Strategic Fit",1,5,3)
    c = st.slider("Capability",1,5,3)
    v = st.slider("Value",1,5,3)
    r = st.slider("Risk",1,5,3)

    if st.button("Evaluate"):

        score = (s+c+v)-r
        st.metric("Score", score)

        prompt = f"Evaluate opportunity: {s},{c},{v},{r}"
        st.markdown(ask_ai(prompt))

# =========================================================
# ASSESSMENT
# =========================================================
elif menu == "Assessment Engine":

    st.header("📊 Assessment")

    p = st.slider("Process",1,5,3)
    t = st.slider("Technology",1,5,3)
    g = st.slider("Governance",1,5,3)
    pe = st.slider("People",1,5,3)
    d = st.slider("Data",1,5,3)

    if st.button("Run Assessment"):

        score = (p+t+g+pe+d)/5
        st.metric("Maturity", round(score,2))

        labels = ["P","T","G","Pe","D"]
        values = [p,t,g,pe,d]

        fig, ax = plt.subplots()
        ax.bar(labels, values)
        st.pyplot(fig)

        st.markdown(ask_ai(f"Assess maturity {values}"))

# =========================================================
# SOLUTION
# =========================================================
elif menu == "Solution Shaping":

    st.header("🧠 Solution Design")

    problem = st.text_area("Problem")
    industry = st.text_input("Industry")

    if st.button("Generate Solution"):

        prompt = f"Design solution for {industry}: {problem}"
        st.markdown(ask_ai(prompt))
