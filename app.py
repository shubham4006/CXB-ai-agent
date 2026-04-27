import streamlit as st
import google.generativeai as genai
import pandas as pd
import matplotlib.pyplot as plt

# ------------------------
# PAGE CONFIG
# ------------------------
st.set_page_config(
    page_title="CXBerries AI Accelerator",
    layout="wide"
)

st.title("CXBerries AI Consulting Accelerator")
st.subheader("Reduce proposal, assessment & analysis effort by 50–70%")

# ------------------------
# GEMINI API
# ------------------------
api_key = st.secrets["AIzaSyCTk13nT5j5P3GDO5wmBYnbZk7DEJjF6tI"]

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

def ask_ai(prompt):
    response = model.generate_content(prompt)
    return response.text

# ------------------------
# SIDEBAR MENU
# ------------------------
menu = st.sidebar.selectbox(
    "Select Module",
    [
        "Proposal Generator",
        "Assessment Engine",
        "Data Insights"
    ]
)

# ==================================================
# MODULE 1
# ==================================================
if menu == "Proposal Generator":

    st.header("📄 Proposal Generator")

    client = st.text_input("Client Name")
    industry = st.text_input("Industry")
    problem = st.text_area("Problem Statement")
    scope = st.text_area("Scope Needed")

    if st.button("Generate Proposal"):

        prompt = f'''
        Create a consulting proposal.

        Client: {client}
        Industry: {industry}
        Problem: {problem}
        Scope: {scope}

        Include:
        1. Executive Summary
        2. Scope of Work
        3. Deliverables
        4. Timeline
        5. Team Structure
        6. Risks
        '''

        result = ask_ai(prompt)
        st.write(result)

# ==================================================
# MODULE 2
# ==================================================
elif menu == "Assessment Engine":

    st.header("📊 ITSM Assessment Engine")

    incident = st.slider("Incident Management",1,5,3)
    change = st.slider("Change Management",1,5,3)
    cmdb = st.slider("CMDB Accuracy",1,5,3)
    automation = st.slider("Automation",1,5,3)
    reporting = st.slider("Reporting",1,5,3)

    if st.button("Run Assessment"):

        score = (incident+change+cmdb+automation+reporting)/5

        st.metric("Overall Score", round(score,2))

        labels = ['Incident','Change','CMDB','Automation','Reporting']
        values = [incident,change,cmdb,automation,reporting]

        fig, ax = plt.subplots()
        ax.bar(labels, values)
        st.pyplot(fig)

        prompt = f'''
        Based on scores:

        Incident {incident}
        Change {change}
        CMDB {cmdb}
        Automation {automation}
        Reporting {reporting}

        Provide:
        1. Maturity Summary
        2. Key Gaps
        3. Recommendations
        4. 90-Day Roadmap
        '''

        result = ask_ai(prompt)
        st.write(result)

# ==================================================
# MODULE 3
# ==================================================
elif menu == "Data Insights":

    st.header("📈 Data Insights Copilot")

    file = st.file_uploader("Upload CSV", type=["csv"])

    if file:

        df = pd.read_csv(file)

        st.dataframe(df.head())

        if st.button("Generate Insights"):

            prompt = f'''
            Analyze this business dataset.

            Columns: {list(df.columns)}
            Rows: {len(df)}

            Give:
            1. Trends
            2. Risks
            3. Opportunities
            4. Executive Summary
            '''

            result = ask_ai(prompt)
            st.write(result)
