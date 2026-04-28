import streamlit as st
from openai import OpenAI
import matplotlib.pyplot as plt
from pptx import Presentation
from pptx.util import Inches
from io import BytesIO

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="CXBerries AI Consulting Engine", layout="wide")

# -----------------------------
# STYLING
# -----------------------------
st.markdown("""
<style>
.main-title {font-size:34px;font-weight:700;color:#1f4e79;text-align:center;}
.sub-title {text-align:center;color:#666;margin-bottom:20px;}
.card {background:white;padding:15px;border-radius:10px;box-shadow:0px 3px 10px rgba(0,0,0,0.1);}
.stButton>button {background:#1f77b4;color:white;border-radius:8px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🚀 CXBerries AI Consulting Decision Engine</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">RFP → Qualification → Assessment → Solution</div>', unsafe_allow_html=True)

# -----------------------------
# API SETUP (AUTO DETECT)
# -----------------------------
openrouter_key = st.secrets.get("OPENROUTER_API_KEY")
openai_key = st.secrets.get("OPENAI_API_KEY")

if openrouter_key:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=openrouter_key
    )
    MODEL = "meta-llama/llama-3-8b-instruct:free"

elif openai_key:
    client = OpenAI(api_key=openai_key)
    MODEL = "gpt-4o-mini"

else:
    st.error("❌ No API key found in secrets")
    st.stop()

# -----------------------------
# AI FUNCTION
# -----------------------------
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
# PPT FUNCTION
# -----------------------------
def create_ppt(text, fig):
    prs = Presentation()

    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = "RFP Insights"
    slide.placeholders[1].text = "CXBerries AI"

    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Insights"
    slide.placeholders[1].text = text[:1000]

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

    file = st.file_uploader("Upload RFP (.txt)", type=["txt"])

    if file:
        content = file.read().decode("utf-8")

        st.text_area("Preview", content[:1500], height=200)

        if st.button("Evaluate RFP"):

            prompt = f"""
            Analyze this RFP:

            {content[:4000]}

            Provide:
            - Summary
            - Key Risks
            - Solution Direction
            - Win Strategy
            """

            with st.spinner("Analyzing RFP..."):
                result = ask_ai(prompt)

            st.markdown(result)

            st.markdown("---")

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

    s = st.slider("Strategic Fit",1,5,3)
    c = st.slider("Capability Fit",1,5,3)
    v = st.slider("Deal Value",1,5,3)
    r = st.slider("Risk Level",1,5,3)

    if st.button("Evaluate Opportunity"):

        score = (s+c+v)-r
        st.metric("Score", score)

        if score >= 8:
            st.success("Strong Opportunity")
        elif score >= 5:
            st.warning("Moderate Opportunity")
        else:
            st.error("Low Priority")

        st.markdown(ask_ai(f"Evaluate opportunity {s},{c},{v},{r}"))

# =========================================================
# 3. ASSESSMENT
# =========================================================
elif menu == "Assessment Engine":

    st.header("📊 Assessment Engine")

    p = st.slider("Process",1,5,3)
    t = st.slider("Technology",1,5,3)
    g = st.slider("Governance",1,5,3)
    pe = st.slider("People",1,5,3)
    d = st.slider("Data",1,5,3)

    if st.button("Run Assessment"):

        score = (p+t+g+pe+d)/5
        st.metric("Maturity Score", round(score,2))

        labels = ["Process","Tech","Gov","People","Data"]
        values = [p,t,g,pe,d]

        fig, ax = plt.subplots()
        ax.bar(labels, values)
        st.pyplot(fig)

        st.markdown(ask_ai(f"Assess maturity {values}"))

# =========================================================
# 4. SOLUTION
# =========================================================
elif menu == "Solution Shaping":

    st.header("🧠 Solution Shaping")

    problem = st.text_area("Client Problem")
    industry = st.text_input("Industry")

    if st.button("Generate Solution"):

        prompt = f"""
        Design consulting solution:

        Industry: {industry}
        Problem: {problem}

        Provide:
        - Architecture
        - Roadmap
        - Team
        - Value
        """

        st.markdown(ask_ai(prompt))
