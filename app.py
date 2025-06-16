import streamlit as st
import json

st.set_page_config(page_title="ESGine - ESG Compliance Dashboard", layout="centered")

st.title("📊 ESGine: ESG Compliance Dashboard")
st.markdown("""
Welcome to **ESGine** — a RegTech dashboard to check ESG compliance against global regulations.

This MVP demo lets you:
- Upload an ESG report (in plain text or JSON)
- Choose a regulation to check against
- Run a mock compliance scan

---
""")

# File upload
uploaded_file = st.file_uploader("📤 Upload your ESG Report", type=["txt", "json"])

# Choose regulation
regulation = st.selectbox(
    "🌍 Select a Regulation to Check Against",
    ("UK - FCA", "EU - SFDR", "US - SEC", "Global - ISSB")
)

# Required fields per regulation (mock)
required_fields_map = {
    "UK - FCA": ["climate_risk", "esg_metrics"],
    "EU - SFDR": ["principal_adverse_impacts", "sustainability_risks"],
    "US - SEC": ["scope_1_2_emissions"],
    "Global - ISSB": ["ifrs_s1_compliance", "ifrs_s2_climate"]
}

# Run button
if st.button("▶️ Run Compliance Check"):
    if uploaded_file is None:
        st.warning("Please upload a file first.")
    else:
        file_contents = uploaded_file.read().decode("utf-8")

        # Try to parse JSON, fall back to plain text
        try:
            report_data = json.loads(file_contents)
        except json.JSONDecodeError:
            report_data = {"text": file_contents}

        # Perform mock check
        required_fields = required_fields_map.get(regulation, [])
        missing = [field for field in required_fields if field not in json.dumps(report_data)]

        st.markdown("### ✅ Compliance Check Result")
        if missing:
            st.error(f"❌ Missing Required Fields: {', '.join(missing)}")
        else:
            st.success("🎉 Your report meets all required fields!")

        st.markdown("---")
        st.json(report_data)

st.markdown("""
---
🔗 **ESG-as-Code™** powers this compliance engine.
Questions? Email [io@esgascode.com](mailto:io@esgascode.com)
""")
