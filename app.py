import streamlit as st
from datetime import datetime
import base64
import json
import yaml
import matplotlib.pyplot as plt
import os
import sys
import mimetypes
from PIL import Image
from fpdf import FPDF

# Add the esgine-backend directory to the path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'esgine-backend'))
sys.path.insert(0, backend_path)

# Now you can import the parser
from parser.rule_engine import run_rule_engine

# Set page config
st.set_page_config(
    page_title="ESGine Dashboard",
    page_icon="🌿",
    layout="wide"
)

# Load logo image
logo_path = "assets/esgine-logo.png"  # Update if different logo name
logo = Image.open(logo_path)

# Display logo and tagline
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

# --- Footer function ---
def show_footer():
    st.markdown("---")
    st.caption(f"\u00a9 {datetime.now().year} ESGine – Built with ❤️ and ESG-as-Code™")

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
                    ESGine™ | ESG-as-Code™ | © {current_year} ESGasCode Ltd.<br>
                    <a href="mailto:legal@esgascode.com">legal@esgascode.com</a> | 
                    <a href="mailto:info@esgine.io">info@esgine.io</a>
                </div>
                """,
                unsafe_allow_html=True
            )
        # This ensures footer is always displayed
    show_footer()


# Upload Section
elif section == "Upload Report":
    st.subheader("📤 Upload Your ESG Report")

    uploaded_file = st.file_uploader(
        "Choose a file (JSON, PDF, DOCX, or TXT)",
        type=["json", "pdf", "docx", "txt"]
    )

    st.markdown("### 🏛️ Select Rule Set")
    rule_options = {
        "UK – FCA": "rules/uk-fca-esg.yaml",
        "EU – SFDR": "rules/eu-sfdr.yaml",
        "US – SEC": "rules/us-sec-esg.yaml",
        "Global – ISSB (IFRS S1 & S2)": "rules/issb/ifrs-s1-s2.yaml"
    }
    selected_rule = st.selectbox("Choose regulatory framework", list(rule_options.keys()))
    rule_path = rule_options[selected_rule]

    if uploaded_file:
        import mimetypes
        file_type, _ = mimetypes.guess_type(uploaded_file.name)
        st.success("File uploaded successfully!")

        text = ""
        content = {}

        if file_type == "application/json":
            import json
            try:
                raw = uploaded_file.read().decode("utf-8")
                content = json.loads(raw)
                st.json(content)
            except json.JSONDecodeError:
                st.warning("⚠️ Could not parse JSON file.")

        elif file_type == "application/pdf":
            from PyPDF2 import PdfReader
            try:
                reader = PdfReader(uploaded_file)
                text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
                st.text_area("📄 Extracted PDF Text", text, height=300)
            except Exception:
                st.warning("⚠️ Could not read PDF content.")

        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            import docx
            try:
                doc = docx.Document(uploaded_file)
                text = "\n".join([p.text for p in doc.paragraphs])
                st.text_area("📄 Extracted DOCX Text", text, height=300)
            except Exception:
                st.warning("⚠️ Could not read DOCX content.")

        elif file_type == "text/plain":
            try:
                text = uploaded_file.read().decode("utf-8")
                st.text_area("📄 Text File Content", text, height=300)
            except Exception:
                st.warning("⚠️ Could not read TXT content.")

        st.markdown("### 📊 Compliance Results")

        try:
            import yaml
            with open(rule_path, "r") as f:
                rules = yaml.safe_load(f)

            from parser.rule_engine import run_rule_engine
            if file_type == "application/json":
                report_data = content
            else:
                report_data = {"report_text": text}

            result = run_rule_engine(report_data, rules)
            st.success("✅ Compliance analysis completed.")
            st.json(result)

            # Phase 4 – Rule-by-Rule Breakdown Table
            import pandas as pd
            df_rules = pd.DataFrame(result["rules"])
            st.markdown("### 📋 Rule-by-Rule Breakdown")
            st.dataframe(df_rules)

            # Phase 5 – Compliance Alerts Based on Score
            if result["score"] < 50:
                st.error("🚨 Your ESG compliance score is below 50%. Urgent action is needed.")
            elif result["score"] < 75:
                st.warning("⚠️ Your ESG compliance score is moderate. Consider improving disclosures.")
            else:
                st.success("✅ Good job! Your ESG compliance score is strong.")


            # 📈 Visual Summary - Phase 1
            st.markdown("### 📈 Compliance Summary")

            # Score progress bar
            st.write(f"**Compliance Score: {result['score']}%**")
            st.progress(result["score"] / 100)

            # Breakdown of checks
            st.write(f"✅ Passed: `{result['passed']}`")
            st.write(f"❌ Failed: `{result['failed']}`")


            st.markdown("### 📈 Visual Summary")
            st.write("**Compliance Score**")
            st.progress(result["score"] / 100)

            import matplotlib.pyplot as plt
            labels = ['Passed', 'Failed']
            sizes = [result["passed"], result["failed"]]
            colors = ['#2ecc71', '#e74c3c']
            fig, ax = plt.subplots()
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
            ax.axis('equal')
            st.pyplot(fig)

            st.markdown("### 📥 Download Your Results")
            import base64
            import io
            json_result = json.dumps(result, indent=2)
            st.download_button(
                label="📦 Download JSON Result",
                data=json_result,
                file_name="esgine_compliance_result.json",
                mime="application/json"
            )

            from fpdf import FPDF
            class PDF(FPDF):
                def header(self):
                    self.set_font('Arial', 'B', 14)
                    self.cell(0, 10, 'ESGine Compliance Report', 0, 1, 'C')

                def footer(self):
                    self.set_y(-15)
                    self.set_font('Arial', 'I', 8)
                    self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

            pdf = PDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, f"Selected Rule: {selected_rule}")
            pdf.multi_cell(0, 10, f"Compliance Score: {result['score']}%")
            pdf.multi_cell(0, 10, f"✅ Passed Checks: {result['passed']}")
            pdf.multi_cell(0, 10, f"❌ Failed Checks: {result['failed']}")
            pdf.ln()
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "Rule Breakdown:", ln=True)
            pdf.set_font("Arial", "", 11)

            for rule in result["rules"]:
                status = "✅ PASSED" if rule["status"] else "❌ FAILED"
                pdf.multi_cell(0, 10, f"- {rule['description']} → {status}")

            pdf_bytes = pdf.output(dest='S').encode('latin-1')
            st.download_button(
                label="📄 Download PDF Report",
                data=pdf_bytes,
                file_name="esgine_compliance_report.pdf",
                mime="application/pdf"
            )

        except Exception as e:
            st.error(f"🚨 Error during compliance check: {str(e)}")
        
    st.markdown("---")
    
    def show_footer():
        current_year = datetime.now().year
        st.markdown("---")
        st.markdown(
            f"""
            <div style="text-align: center; font-size: 14px; color: #555;">
                ESGine™ | ESG-as-Code™ | © {current_year} ESGasCode Ltd.<br>
                <a href="mailto:legal@esgascode.com">legal@esgascode.com</a> | 
                <a href="mailto:info@esgine.io">info@esgine.io</a>
            </div>
            """,
            unsafe_allow_html=True
        )
    # This ensures footer is always displayed
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
    
    st.markdown("---")
    def show_footer():
        current_year = datetime.now().year
        st.markdown("---")
        st.markdown(
            f"""
            <div style="text-align: center; font-size: 14px; color: #555;">
                ESGine™ | ESG-as-Code™ | © {current_year} ESGasCode Ltd.<br>
                <a href="mailto:legal@esgascode.com">legal@esgascode.com</a> | 
                <a href="mailto:info@esgine.io">info@esgine.io</a>
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
   
    st.markdown("---")
     def show_footer():
        current_year = datetime.now().year
        st.markdown("---")
        st.markdown(
            f"""
            <div style="text-align: center; font-size: 14px; color: #555;">
                ESGine™ | ESG-as-Code™ | © {current_year} ESGine Inc. All rights reserved.<br>
                <a href="mailto:info@esgine.io">info@esgine.io</a> | <a href="www.esgine.io">info@esgine.io</a>
            </div>
            """,
            unsafe_allow_html=True
        )
    # This ensures footer is always displayed
    show_footer()
