import streamlit as st

# --- Set Page Metadata ---
st.set_page_config(
    page_title="ESGine Dashboard",
    page_icon="v",
    layout="wide"
)

# --- Standard Library ---
import os
import re
import sys
import json
import base64
import urllib.request
import mimetypes
from datetime import datetime

# --- Convert Extracted Text to ESG JSON ---
def convert_text_to_json(text):
    text = text.lower()
    
    fields = [
        "scope_1_emissions",
        "scope_2_emissions",
        "scope_3_emissions",
        "climate_risk_description",
        "board_oversight_description",
        "scenario_analysis_used",
        "ghg_assurance_statement",
        "carbon emissions",
        "governance structure",
        "risk management"
    ]
    
    result = {}
    for field in fields:
        pattern = re.compile(rf"{re.escape(field.replace('_', ' '))}[:\-–]?\s*(.+)", re.IGNORECASE)
        match = pattern.search(text)
        if match:
            result[field] = match.group(1).strip()
        elif "description" in field or "structure" in field or "management" in field:
            result[field] = text
        else:
            result[field] = "Not specified"
    
    return result

# --- Ensure DejaVu Font for Unicode support ---
def ensure_dejavu_font():
    font_dir = "fonts"
    os.makedirs(font_dir, exist_ok=True)
    font_path = os.path.join(font_dir, "DejaVuSans.ttf")
    if not os.path.exists(font_path):
        url = "https://github.com/dejavu-fonts/dejavu-fonts/raw/version_2_37/ttf/DejaVuSans.ttf"
        urllib.request.urlretrieve(url, font_path)
        print("✅ DejaVuSans.ttf downloaded.")
    return font_path

font_path = ensure_dejavu_font()

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

# --- Ensure DejaVu Font for Unicode support ---
def ensure_dejavu_font():
    font_dir = "fonts"
    os.makedirs(font_dir, exist_ok=True)
    font_path = os.path.join(font_dir, "DejaVuSans.ttf")
    if not os.path.exists(font_path):
        url = "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf"
        urllib.request.urlretrieve(url, font_path)
        print("✅ DejaVuSans.ttf downloaded.")
    return font_path

font_path = ensure_dejavu_font()

# --- PDF Template Class ---
class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font("DejaVu", "", font_path, uni=True)
        self.set_font("DejaVu", "", 12)

    def header(self):
        self.set_font("DejaVu", "", 14)
        self.cell(0, 10, 'ESGine™ Compliance Report', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu", "", 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

# --- PDF Generator (Unicode Compatible) ---
def generate_pdf_report(selected_rule, result):
    pdf = FPDF()
    pdf.add_page()

    # Set Unicode font
    pdf.add_font("DejaVu", "", "fonts/DejaVuSans.ttf", uni=True)
    pdf.add_font("DejaVu", "B", "fonts/DejaVuSans-Bold.ttf", uni=True)

    pdf.set_font("DejaVu", "B", 14)
    pdf.cell(0, 10, "ESGine Compliance Report", ln=True, align="C")
    pdf.ln()

    pdf.set_font("DejaVu", "", 12)
    pdf.multi_cell(0, 10, f"Selected Rule: {selected_rule}")
    pdf.multi_cell(0, 10, f"Score: {result.get('score', 0)}%")
    pdf.multi_cell(0, 10, f"✅ Passed: {result.get('passed', 0)} | ❌ Failed: {result.get('failed', 0)}")
    pdf.ln()

    pdf.set_font("DejaVu", "B", 12)
    pdf.cell(0, 10, "Rule Breakdown:", ln=True)
    pdf.set_font("DejaVu", "", 11)

    for rule in result.get("rules", []):
        if isinstance(rule, dict):
            field = rule.get("field", "N/A")
            status = "✅" if rule.get("status") else "❌"
            description = rule.get("description", "")
            pdf.multi_cell(0, 10, f"- {field}: {status} | {description}")

    return pdf.output(dest="S").encode("utf-8")

# --- Load ESGine Logo ---
logo_path = "assets/esgine-logo.png"

# --- Page Header ---
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
    # --- Always Show Footer ---
    show_footer()
    
# --- Upload Report Section ---
elif section == "Upload Report":
    st.subheader("📤 Upload Your ESG Report")

    uploaded_file = st.file_uploader("Choose a file (.json, .pdf, .docx, .txt)", type=["json", "pdf", "docx", "txt"])

    # Rule set selection
    st.markdown("### 🏛️ Select Compliance Framework")
    rule_options = {
        "UK - FCA": "rules/uk-fca-esg.yaml",
        "EU - SFDR": "rules/eu-sfdr.yaml",
        "US - SEC": "rules/us-sec-esg.yaml",
        "Global - ISSB (IFRS S1 & S2)": "rules/issb/ifrs-s1-s2.yaml"
    }
    selected_rule = st.selectbox("Choose regulatory framework", list(rule_options.keys()))
    rule_path = rule_options[selected_rule]

    if uploaded_file:
        try:
            file_type = uploaded_file.type
            report_data = {}

            # Parse uploaded content into ESG-compliant dict
            if file_type == "application/json":
                report_data = json.load(uploaded_file)

            elif file_type == "application/pdf":
                reader = PdfReader(uploaded_file)
                extracted_text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
                report_data = convert_text_to_json(extracted_text)

            elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                extracted_text = docx2txt.process(uploaded_file)
                report_data = convert_text_to_json(extracted_text)

            elif file_type == "text/plain":
                extracted_text = uploaded_file.read().decode("utf-8")
                report_data = convert_text_to_json(extracted_text)

            else:
                st.warning("❌ Unsupported file format.")

            if isinstance(report_data, dict) and report_data:
                with st.spinner("🔍 Running ESGine compliance check..."):
                    rules = load_yaml_rule(rule_path)
                    result_list = evaluate_rule(rules, report_data)

                    passed = sum(1 for r in result_list if isinstance(r, dict) and "✅" in str(r.get("status")))
                    failed = sum(1 for r in result_list if isinstance(r, dict) and "❌" in str(r.get("status")))
                    total = passed + failed
                    score = round((passed / total) * 100, 2) if total > 0 else 0

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

                    if total > 0:
                        st.markdown("### 📈 Summary Chart")
                        fig, ax = plt.subplots()
                        ax.pie([passed, failed], labels=["Passed", "Failed"], autopct="%1.1f%%", startangle=90)
                        ax.axis("equal")
                        st.pyplot(fig)

                    # --- Download Buttons ---
                    st.download_button("📥 Download JSON Result",
                                       data=json.dumps(result, indent=2),
                                       file_name="esgine_result.json",
                                       mime="application/json")

                    pdf_bytes = generate_pdf_report(selected_rule, result)
                    st.download_button("📄 Download ESGine PDF Report",
                                       data=pdf_bytes,
                                       file_name="esgine_compliance_report.pdf",
                                       mime="application/pdf")
            else:
                st.warning("⚠️ Could not extract ESG data from the uploaded file.")

        except Exception as e:
            st.error(f"🚨 An unexpected error occurred: {str(e)}")

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

