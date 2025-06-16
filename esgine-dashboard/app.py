import streamlit as st
import json
from utils import run_esg_checks

st.set_page_config(page_title="ESGine Dashboard", layout="centered")

st.title("📊 ESGine: ESG Compliance Dashboard")

st.markdown("Upload an ESG report and check compliance with selected regulatory standards.")

uploaded_file = st.file_uploader("📤 Upload ESG Report (JSON)", type=["json"])

rule_choice = st.selectbox("📚 Select ESG Rule Set", ["UK – FCA", "EU – SFDR", "US – SEC", "Global – ISSB"])

if st.button("🚀 Run ESG-as-Code™ Check") and uploaded_file:
    data = json.load(uploaded_file)
    results = run_esg_checks(data, rule_choice)
    st.subheader("✅ Compliance Results")
    for res in results:
        st.write(res)