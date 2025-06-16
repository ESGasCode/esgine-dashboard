# ESGine Dashboard 🌱📊

**Automating ESG Compliance. Securely.**

This is the official frontend dashboard for **ESGine**, a RegTech SaaS platform built on top of the ESG-as-Code™ framework. It enables users to upload ESG reports, validate them against regulatory rules (e.g. SEC, SFDR, FCA), and view compliance results.

## 🔧 Features
- Upload ESG reports (`.json`)
- Apply regulatory rules from SEC, SFDR, FCA, ISSB
- Real-time compliance results
- Streamlit-powered UI

## 📁 Folder Structure
- `app.py` — Main dashboard app
- `parser/` — Compliance rule engine and logic
- `rules/` — YAML-formatted regulatory rulepacks
- `assets/` — Brand visuals (e.g., logo.png)
- `.gitignore`, `README.md`, `requirements.txt`

## ⚙️ Setup & Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
```


## 💼 ESG-as-Code Integration
This dashboard relies on the ESG-as-Code™ backend logic for regulatory interpretation and rule matching.

---

Created by [Isaiah Owolabi](https://github.com/ESGasCode)  
Website: [https://esgascode.com](https://esgascode.com)

