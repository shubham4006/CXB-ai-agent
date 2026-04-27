import streamlit as st
from openai import OpenAI
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------
# PAGE
# -----------------------
st.set_page_config(page_title="CXBerries AI Accelerator", layout="wide")

st.title("🚀 CXBerries AI Consulting Accelerator")
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
            model="openai/gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# -----------------------
# MENU
# -----------------------
menu = st.sidebar.selectbox(
    "Select Module",
    ["Proposal Generator", "Assessment Engine", "Data Insights"]
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

        st.write(result)

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

        score = (incident+change+cmdb+automation+reporting)/5
        st.metric("Overall Score", round(score,2))

        labels = ['Incident','Change','CMDB','Automation','Reporting']
        vals = [incident,change,cmdb,automation,reporting]

        fig, ax = plt.subplots()
        ax.bar(labels, vals)
        st.pyplot(fig)

# ==========================================
# DATA INSIGHTS
# ==========================================
elif menu == "Data Insights":

    st.header("📈 Data Insights")

    file = st.file_uploader("Upload CSV", type=["csv"])

    if file:
        df = pd.read_csv(file)
        st.dataframe(df.head())
