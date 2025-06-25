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

# --- Add Backend to Path ---
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'esgine-backend'))
sys.path.insert(0, backend_path)

# --- Local Modules ---
from parser.rule_engine import run_rule_engine

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

# --- Sidebar Navigation ---
st.sidebar.header("Navigation")
section = st.sidebar.radio("Go to", ["Home", "Upload Report", "About", "Contact"])

# --- Upload Report Section ---
if section == "Upload Report":
    st.header("📄 Upload ESG Report")
    uploaded_file = st.file_uploader("Upload your ESG report (.docx or .pdf)", type=["docx", "pdf"])

    if uploaded_file:
        file_type = uploaded_file.type
        extracted_text = ""

        try:
            if file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                doc = docx.Document(uploaded_file)
                extracted_text = "\n".join([para.text for para in doc.paragraphs])
                st.success("✅ DOCX file parsed successfully.")

            elif file_type == "application/pdf":
                reader = PdfReader(uploaded_file)
                for page in reader.pages:
                    extracted_text += page.extract_text() or ""
                st.success("✅ PDF file parsed successfully.")

            st.text_area("📋 Extracted Text", extracted_text, height=300)

            # --- ESGine Compliance Check ---
            with st.spinner("🔍 Running ESGine™ compliance check..."):
                result = run_rule_engine(extracted_text)
                st.success("✅ Compliance check complete.")
                st.json(result)

        except Exception as e:
            st.error(f"🚨 Error: {str(e)}")

# --- Footer ---
def show_footer():
    st.markdown("---")
    st.caption(f"\u00a9 {datetime.now().year} ESGine – Built with ❤️ and ESG-as-Code™")

show_footer()


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
       
    def show_footer():
        current_year = datetime.now().year
        st.markdown("---")
        st.markdown(
            f"""
            <div style="text-align: center; font-size: 14px; color: #555;">
                ESGine™ | ESG-as-Code™ | © {current_year} - ESGine Inc. All rights reserved.<br>
                <a href="mailto:info@esgine.io">info@esgine.io</a> | <a>www.esgine.io</a>
            </div>
            """,
            unsafe_allow_html=True
        )
        # This ensures footer is always displayed
        show_footer()

    
# --- Upload Section ---
elif section == "Upload Report":
    st.subheader("📤 Upload Your ESG Report")

    uploaded_file = st.file_uploader("Choose a file (JSON, PDF, DOCX, or TXT)", type=["json", "pdf", "docx", "txt"])

    st.markdown("### 🏛️ Select Rule Set")
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

            report_data = {}
            extracted_text = ""

            # --- Handle file parsing ---
            if file_type == "application/json":
                raw = uploaded_file.read().decode("utf-8")
                report_data = json.loads(raw)
                st.json(report_data)

            elif file_type == "application/pdf":
                reader = PdfReader(uploaded_file)
                extracted_text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
                st.text_area("📄 Extracted PDF Text", extracted_text, height=300)

            elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                doc = docx.Document(uploaded_file)
                extracted_text = "\n".join([p.text for p in doc.paragraphs])
                st.text_area("📄 Extracted DOCX Text", extracted_text, height=300)

            elif file_type == "text/plain":
                extracted_text = uploaded_file.read().decode("utf-8")
                st.text_area("📄 Text File Content", extracted_text, height=300)

            # --- Run compliance check ---
            from parser.utils import load_rule  # Make sure this exists
            rules = load_rule(rule_path)
            input_payload = report_data if file_type == "application/json" else extracted_text
            result = run_rule_engine(input_payload, rules)

            st.success("✅ ESG compliance analysis completed.")
            st.markdown("### 📊 Compliance Results")
            st.metric(label="Compliance Score", value=f"{result['score']}%")
            st.json(result)

            st.markdown("### 📋 Rule-by-Rule Breakdown")
            df_rules = pd.DataFrame(result["rules"])
            st.dataframe(df_rules)

            if result["score"] < 50:
                st.error("🚨 Score below 50% — urgent compliance gaps.")
            elif result["score"] < 75:
                st.warning("⚠️ Score between 50–75% — room for improvement.")
            else:
                st.success("✅ Strong compliance! Keep it up.")

            # --- Visual Summary ---
            st.markdown("### 📈 Visual Summary")
            labels = ['Passed', 'Failed']
            sizes = [result["passed"], result["failed"]]
            fig, ax = plt.subplots()
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=['#2ecc71', '#e74c3c'])
            ax.axis('equal')
            st.pyplot(fig)

            # --- Download Section ---
            st.markdown("### 📥 Download Your Results")
            st.download_button("📦 Download JSON Result", data=json.dumps(result, indent=2),
                               file_name="esgine_compliance_result.json", mime="application/json")

            # PDF Report Generation
            def generate_pdf_report(selected_rule, result):
                pdf = PDF()
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
                    status = "✅ PASSED" if rule["status"] else "❌ FAILED"
                    description = rule.get("description", "No description")
                    pdf.multi_cell(0, 10, f"- {description} → {status}")
                return pdf.output(dest='S').encode('latin-1', 'replace')

            pdf_bytes = generate_pdf_report(selected_rule, result)
            st.download_button("📄 Download ESGine™ PDF Report",
                               data=pdf_bytes,
                               file_name="esgine_compliance_report.pdf",
                               mime="application/pdf")

        except Exception as e:
            st.error(f"🚨 General error during file processing or compliance check: {str(e)}")


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
    
    def show_footer():
        current_year = datetime.now().year
        st.markdown("---")
        st.markdown(
            f"""
            <div style="text-align: center; font-size: 14px; color: #555;">
                ESGine™ | ESG-as-Code™ | © {current_year} - ESGine Inc. All rights reserved.<br>
                <a href="mailto:info@esgine.io">info@esgine.io</a> | <a>www.esgine.io</a>
            </div>
            """,
            unsafe_allow_html=True
        )
    # This ensures footer is always displayed
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
   
    
    def show_footer():
        current_year = datetime.now().year
        st.markdown("---")
        st.markdown(
            f"""
            <div style="text-align: center; font-size: 14px; color: #555;">
                ESGine™ | ESG-as-Code™ | © {current_year} - ESGine Inc. All rights reserved.<br>
                <a href="mailto:info@esgine.io">info@esgine.io</a> | <a>www.esgine.io</a>
            </div>
            """,
            unsafe_allow_html=True
        )
    # This ensures footer is always displayed
    show_footer()
