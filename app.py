import streamlit as st
from datetime import datetime
import base64
import json
import yaml
import docx2txt
import PyPDF2
import matplotlib.pyplot as plt
import os
import sys
import mimetypes
from PIL import Image
from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'ESGine™ Compliance Report', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')


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
                ESGine™ | ESG-as-Code™ | © {current_year} - ESGine Inc. All rights reserved.<br>
                <a href="mailto:info@esgine.io">info@esgine.io</a> | <a>www.esgine.io</a>
            </div>
            """,
            unsafe_allow_html=True
        )
    # This ensures footer is always displayed
    show_footer()


# Upload Section
elif section == "Upload Report":
    st.subheader("\ud83d\udcc4 Upload Your ESG Report")

    uploaded_file = st.file_uploader("Choose a file (JSON, PDF, DOCX, or TXT)", type=["json", "pdf", "docx", "txt"])

    st.markdown("### \ud83c\udfe7 Select Rule Set")
    rule_options = {
        "UK \u2013 FCA": "rules/uk-fca-esg.yaml",
        "EU \u2013 SFDR": "rules/eu-sfdr.yaml",
        "US \u2013 SEC": "rules/us-sec-esg.yaml",
        "Global \u2013 ISSB (IFRS S1 & S2)": "rules/issb/ifrs-s1-s2.yaml"
    }
    selected_rule = st.selectbox("Choose regulatory framework", list(rule_options.keys()))
    rule_path = rule_options[selected_rule]

    if uploaded_file:
        try:
            file_type, _ = mimetypes.guess_type(uploaded_file.name)
            st.success(f"\u2705 File uploaded: `{uploaded_file.name}`")

            report_data = {}
            extracted_text = ""

            if file_type == "application/json":
                raw = uploaded_file.read().decode("utf-8")
                report_data = json.loads(raw)
                st.json(report_data)
            elif file_type == "application/pdf":
                reader = PdfReader(uploaded_file)
                extracted_text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
                st.text_area("\ud83d\udcc4 Extracted PDF Text", extracted_text, height=300)
            elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                doc = docx.Document(uploaded_file)
                extracted_text = "\n".join([p.text for p in doc.paragraphs])
                st.text_area("\ud83d\udcc4 Extracted DOCX Text", extracted_text, height=300)
            elif file_type == "text/plain":
                extracted_text = uploaded_file.read().decode("utf-8")
                st.text_area("\ud83d\udcc4 Text File Content", extracted_text, height=300)

            with open(rule_path, "r") as f:
                rules = yaml.safe_load(f)

            input_payload = report_data if file_type == "application/json" else {"report_text": extracted_text}
            result = run_rule_engine(input_payload, rules)

            st.success("\u2705 ESG compliance analysis completed.")
            st.markdown("### \ud83d\udcca Compliance Results")
            st.json(result)

            st.markdown("### \ud83d\udccb Rule-by-Rule Breakdown")
            df_rules = pd.DataFrame(result["rules"])
            st.dataframe(df_rules)

            if result["score"] < 50:
                st.error("\ud83d\udea8 Score below 50% \u2014 urgent compliance gaps.")
            elif result["score"] < 75:
                st.warning("\u26a0\ufe0f Score between 50\u201375% \u2014 room for improvement.")
            else:
                st.success("\u2705 Strong compliance! Keep it up.")

            st.markdown("### \ud83d\udcc8 Visual Summary")
            labels = ['Passed', 'Failed']
            sizes = [result["passed"], result["failed"]]
            fig, ax = plt.subplots()
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=['#2ecc71', '#e74c3c'])
            ax.axis('equal')
            st.pyplot(fig)

            st.markdown("### \ud83d\udcc5 Download Your Results")
            st.download_button("\ud83d\udce6 Download JSON Result", data=json.dumps(result, indent=2),
                               file_name="esgine_compliance_result.json", mime="application/json")

            def generate_pdf_report(selected_rule, result):
                pdf = PDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.multi_cell(0, 10, f"Selected Rule: {selected_rule}")
                pdf.multi_cell(0, 10, f"Score: {result['score']}%")
                pdf.multi_cell(0, 10, f"\u2705 Passed: {result['passed']} | \u274c Failed: {result['failed']}")
                pdf.ln()
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 10, "Rule Breakdown:", ln=True)
                pdf.set_font("Arial", "", 11)
                for rule in result["rules"]:
                    status = "\u2705 PASSED" if rule["status"] else "\u274c FAILED"
                    description = rule.get("description", "No description")
                    pdf.multi_cell(0, 10, f"- {description} \u2192 {status}")
                return pdf.output(dest='S').encode('latin-1', 'replace')

            pdf_bytes = generate_pdf_report(selected_rule, result)
            st.download_button("\ud83d\udcc4 Download ESGine\u2122 PDF Report", data=pdf_bytes,
                               file_name="esgine_compliance_report.pdf", mime="application/pdf")

        except Exception as e:
            st.error(f"\ud83d\udea8 Error during compliance check: {str(e)}")

            
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
