import streamlit as st
from PIL import Image
from datetime import datetime

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

# Sidebar
st.sidebar.header("Navigation")
section = st.sidebar.radio("Go to", ["Home", "Upload Report", "About"])

# Home Section
if section == "Home":
    st.subheader("🌍 Welcome to ESGine Dashboard")
    st.write("""
        ESGine is a RegTech SaaS platform powered by ESG-as-Code™. 
        Our goal is to simplify ESG compliance using programmable rules and real-time dashboards.
        
        - Upload and analyze ESG reports
        - Track compliance with regulations (FCA, SEC, SFDR, ISSB)
        - Receive instant feedback and compliance scores
    """)

# Upload Section
elif section == "Upload Report":
    st.subheader("📤 Upload Your ESG Report")
    uploaded_file = st.file_uploader("Choose a JSON file", type=["json"])
    if uploaded_file:
        data = uploaded_file.read().decode("utf-8")
        st.json(data)
        st.success("File uploaded successfully!")
        st.info("🔧 Analysis feature coming soon.")

# About Section
elif section == "About":
    st.subheader("📘 About ESGine")
    st.markdown("""
    ESGine is built on the ESG-as-Code™ framework to empower:
    
    - **SMEs** preparing ESG disclosures
    - **Investors** assessing sustainability risks
    - **Auditors & Regulators** validating ESG claims
    
   #### 🔁 ESGine Ecosystem Overview
    """)
    st.image("assets/esg-flow-diagram.png", caption="How ESGine integrates ESG-as-Code™ into a usable platform.")

# Footer
st.markdown("---")
st.caption(f"© {datetime.now().year} ESGine – Built with ❤️ and ESG-as-Code™")
