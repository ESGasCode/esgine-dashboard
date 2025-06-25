import streamlit as st

# --- Set Page Metadata ---
st.set_page_config(
    page_title="ESGine Dashboard",
    page_icon="🌿",
    layout="wide"
)

# --- Hide Streamlit Branding ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- Standard Library ---
import os
import sys
import json
import base64
import mimetypes
from datetime import datetime

# --- Third-Party Libraries ---
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from PIL import Image
import yaml
import docx
import docx2txt
from PyPDF2 import PdfReader

# --- Local Modules ---
from parser.local_evaluator import load_yaml_rule, evaluate_rule

# --- PDF Template for Export (Optional Future Use) ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'ESGine™ Compliance Report', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

# --- Load Logo ---
logo_path = "assets/esgine-logo.png"
logo = Image.open(logo_path)

col1, col2 = st.columns([1, 8])
with col1:
    st.image(logo, width=90)
with col2:
    st.markdown("""
        <h1 style='margin-bottom: 0; font-size: 2.5rem;'>ESGine</h1>
        <p style='margin-top: 0; font-size: 1.2rem; color: #555;'>Automating ESG Compliance. Securely.</p>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- Global Footer Function ---
def show_footer():
    current_year = datetime.now().year
    st.markdown("---")
    st.markdown(
        f"""
        <div style="text-align: center; font-size: 14px; color: #555;">
            ESGine | ESG-as-Code™ | © {current_year} - ESGine Inc. All rights reserved.<br>
            <a href="mailto:info@esgine.io">info@esgine.io</a> | <a href="https://www.esgine.io" target="_blank">www.esgine.io</a>
        </div>
        """,
        unsafe_allow_html=True
    )

st.sidebar.success("✅ Sidebar loaded")  # Debug

# --- Sidebar Navigation ---
st.sidebar.header("Navigation")
section = st.sidebar.radio("Go to", ["Home", "Upload Report", "About", "Contact"])

# Home Section
if section == "Home":
    st.subheader("🌍 Welcome to ESGine Dashboard")

    st.markdown("""
    ESGine is a **RegTech SaaS platform** powered by **ESG-as-Code™**.

    Our mission is to simplify ESG compliance using programmable rules and real-time dashboards.

    ### 🔑 Key Features:
    - 📤 **Upload & analyze** ESG reports (JSON, PDF, DOCX, TXT)
    - 📊 **Track compliance** with global frameworks (FCA, SEC, SFDR, ISSB)
    - ⚡ **Instant scoring** & visual feedback
    - 📄 **Download reports** (JSON or PDF)
    - 🔐 Secure, no data stored

    ---
    ### 🚀 Get Started
    👉 Go to the **Upload Report** tab to begin your ESG analysis.

    ---
    ### 📚 Supported Frameworks:
    - 🇬🇧 FCA (UK)
    - 🇪🇺 SFDR (EU)
    - 🇺🇸 SEC (USA)
    - 🌐 ISSB (Global)

    """)

    
# --- Upload Report Section ---
elif section == "Upload Report":
    st.subheader("📤 Upload Your ESG Report")

    # Upload input
    uploaded_file = st.file_uploader("Choose a file (.json, .pdf, .docx, .txt)", type=["json", "pdf", "docx", "txt"])

    # Rule set selection
    st.markdown("### 🏛️ Select Compliance Framework")
    rule_options = {
        "UK - FCA": "rules/uk-fca-esg.yaml",
        "EU - SFDR": "rules/eu-sfdr.yaml",
        "US - SEC": "rules/sec/sec-esg.yaml",
        "Global - ISSB (IFRS S1 & S2)": "rules/issb/ifrs-s1-s2.yaml"
    }
    selected_rule = st.selectbox("Choose regulatory framework", list(rule_options.keys()))
    rule_path = rule_options[selected_rule]

    if uploaded_file:
        try:
            file_type, _ = mimetypes.guess_type(uploaded_file.name)
            st.success(f"✅ File uploaded: `{uploaded_file.name}`")
            extracted_text = ""
            report_data = {}

            # --- Parse uploaded file ---
            if file_type == "application/json":
                raw = uploaded_file.read().decode("utf-8")
                report_data = json.loads(raw)
                st.json(report_data)

            elif file_type == "application/pdf":
                reader = PdfReader(uploaded_file)
                extracted_text = "\n".join(page.extract_text() or "" for page in reader.pages)
                st.text_area("📄 Extracted PDF Text", extracted_text, height=300)

            elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                doc = docx.Document(uploaded_file)
                extracted_text = "\n".join([p.text for p in doc.paragraphs])
                st.text_area("📄 Extracted DOCX Text", extracted_text, height=300)

            elif file_type == "text/plain":
                extracted_text = uploaded_file.read().decode("utf-8")
                st.text_area("📄 Text File Content", extracted_text, height=300)

            else:
                st.warning("⚠️ Unsupported file type. Please upload JSON, PDF, DOCX, or TXT.")
                st.stop()

            # --- Run Compliance Check (only for JSON) ---
            from parser.local_evaluator import load_yaml_rule, evaluate_rule

            rules = load_yaml_rule(rule_path)
            input_payload = report_data if file_type == "application/json" else {}

            if input_payload:
                with st.spinner("🔍 Running ESGine™ compliance check..."):
                    result_list = evaluate_rule(rules, input_payload)
                    passed = sum(1 for r in result_list if "✅" in r["status"])
                    failed = sum(1 for r in result_list if "❌" in r["status"])
                    score = round((passed / (passed + failed)) * 100, 2) if passed + failed > 0 else 0

                    result = {
                        "score": score,
                        "passed": passed,
                        "failed": failed,
                        "rules": result_list
                    }

                    st.success("✅ ESG compliance analysis completed.")
                    st.metric("Compliance Score", f"{score}%")
                    st.markdown("### 📊 Rule Evaluation")
                    st.dataframe(pd.DataFrame(result["rules"]))

                    # --- Score Feedback ---
                    if score < 50:
                        st.error("🚨 Score below 50% — major compliance gaps.")
                    elif score < 75:
                        st.warning("⚠️ Score between 50–75% — moderate gaps, needs work.")
                    else:
                        st.success("✅ Score above 75% — strong ESG alignment.")

                    # --- Visual Summary ---
                    st.markdown("### 📈 Summary Chart")
                    labels = ['Passed', 'Failed']
                    sizes = [passed, failed]
                    fig, ax = plt.subplots()
                    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=['#2ecc71', '#e74c3c'])
                    ax.axis('equal')
                    st.pyplot(fig)

                    # --- Download JSON ---
                    st.markdown("### 📥 Download Reports")
                    st.download_button("📦 Download JSON Result", data=json.dumps(result, indent=2),
                                       file_name="esgine_compliance_result.json", mime="application/json")

                    # --- PDF Report ---
                    def generate_pdf_report(selected_rule, result):
                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_font("Arial", size=12)
                        pdf.multi_cell(0, 10, f"Selected Rule: {selected_rule}")
                        pdf.multi_cell(0, 10, f"Score: {result['score']}%")
                        pdf.multi_cell(0, 10, f"✅ Passed: {result['passed']} | ❌ Failed: {result['failed']}")
                        pdf.ln()
                        pdf.set_font("Arial", "B", 12)
                        pdf.cell(0, 10, "Rule Breakdown:", ln=True)
                        pdf.set_font("Arial", "", 11)
                        for rule in result["rules"]:
                            status = rule["status"]
                            field = rule.get("field", "N/A")
                            pdf.multi_cell(0, 10, f"- {field} → {status}")
                        return pdf.output(dest='S').encode('latin-1', 'replace')

                    pdf_bytes = generate_pdf_report(selected_rule, result)
                    st.download_button("📄 Download ESGine™ PDF Report",
                                       data=pdf_bytes,
                                       file_name="esgine_compliance_report.pdf",
                                       mime="application/pdf")

            else:
                st.warning("⚠️ Compliance check currently only supports structured JSON files. DOCX/PDF text can be extracted, but automated checks will come in a later version.")

        except Exception as e:
            st.error(f"🚨 An unexpected error occurred: {str(e)}")

    # --- Always Show Footer ---
    show_footer()

# ✅ About Section
elif section == "About":    
    st.subheader("📘 About ESGine")
    st.markdown("""
**ESGine** is built on the **ESG-as-Code™** framework to empower:

- **SMEs** preparing ESG disclosures  
- **Investors** assessing sustainability risks  
- **Auditors & Regulators** validating ESG claims  

#### 🔁 ESGine Ecosystem Overview
    """)

    # --- Always Show Footer ---
    show_footer()

# ✅ Contact Section
elif section == "Contact":
    st.subheader("📬 Contact Us")
    with st.form("contact_form"):
        name = st.text_input("Your Name")
        email = st.text_input("Your Email")
        message = st.text_area("Your Message")
        subscribe = st.checkbox("Keep me updated with ESGine insights")
        submitted = st.form_submit_button("Send Message")

    if submitted:
        st.success(f"Thanks {name}, your message has been received!")
        # Optionally save to database or send via email here
   
# --- Always Show Footer ---
show_footer()
