import streamlit as st
import json
from PIL import Image

# --- Load Logo ---
logo = Image.open("assets/esgine_logo.png")  # You must place the logo file here manually

# --- Page Config ---
st.set_page_config(page_title="ESGine – ESG Compliance Dashboard", page_icon=logo, layout="centered")

# --- Header ---
col1, col2 = st.columns([1, 5])
with col1:
    st.image(logo, width=70)
with col2:
    st.title("ESGine")
    st.caption("Automating ESG Compliance. Securely.")

# --- Navigation Tabs ---
tabs = st.tabs(["📂 Upload Report", "✅ Check Compliance", "ℹ️ About ESGine"])

# --- Tab 1: Upload Report ---
with tabs[0]:
    st.header("📤 Upload ESG Report")
    uploaded_file = st.file_uploader("Choose a report to analyze (JSON or TXT)", type=["json", "txt"])
    st.selectbox("🌍 Choose a Regulation", ["UK – FCA", "EU – SFDR", "US – SEC", "Global – ISSB"])
    st.info("After uploading your file, proceed to the 'Check Compliance' tab.")

# --- Tab 2: Check Compliance (Mock Logic) ---
with tabs[1]:
    st.header("✅ ESG Compliance Checker")
    st.markdown("Run a mock compliance scan on the uploaded ESG report.")

    required_fields_map = {
        "UK – FCA": ["climate_risk", "esg_metrics"],
        "EU – SFDR": ["principal_adverse_impacts", "sustainability_risks"],
        "US – SEC": ["scope_1_2_emissions"],
        "Global – ISSB": ["ifrs_s1_compliance", "ifrs_s2_climate"]
    }

    if uploaded_file:
        file_contents = uploaded_file.read().decode("utf-8")
        try:
            report_data = json.loads(file_contents)
        except json.JSONDecodeError:
            report_data = {"text": file_contents}

        st.success("✅ File uploaded and parsed successfully!")
        regulation = st.selectbox("Select rule set to run", list(required_fields_map.keys()))

        if st.button("🚀 Run Check"):
            missing = [field for field in required_fields_map[regulation] if field not in json.dumps(report_data)]
            st.subheader("🔍 Compliance Results")
            if missing:
                st.error(f"❌ Missing Required Fields: {', '.join(missing)}")
            else:
                st.success("🎉 All required ESG fields are present!")
            st.markdown("---")
            st.json(report_data)
    else:
        st.warning("Please upload a file in the Upload tab before running checks.")

# --- Tab 3: About ESGine ---
with tabs[2]:
    st.header("ℹ️ About ESGine")
    st.markdown("""
    **ESGine** is a modern RegTech platform designed to automate ESG compliance based on transparent, programmable logic.

    This dashboard is powered by **ESG-as-Code™**, an open-source rule engine transforming complex ESG regulations into structured validation logic.

    **Key Goals:**
    - Improve ESG disclosure quality
    - Support SMEs and investors in real-time ESG validation
    - Promote trust and transparency in ESG audits

    💬 For inquiries or partnership: [io@esgascode.com](mailto:io@esgascode.com)
    """)
