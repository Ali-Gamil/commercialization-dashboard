import streamlit as st
import pandas as pd

st.title("📝 Company Commercialization Scoring Form & Dashboard")

if "companies" not in st.session_state:
    st.session_state["companies"] = []

st.header("📋 Company Evaluation Form")

with st.form("company_form"):
    name = st.text_input("Company Name")
    mo = st.slider("Market Opportunity", 1, 5, 3)
    pf = st.slider("Product Feasibility", 1, 5, 3)
    bm = st.slider("Business Model", 1, 5, 3)
    cv = st.slider("Customer Validation", 1, 5, 3)
    ca = st.slider("Competitive Advantage", 1, 5, 3)
    ts = st.slider("Team Strength", 1, 5, 3)
    tr = st.slider("Traction", 1, 5, 3)
    fr = st.slider("Financial Readiness", 1, 5, 3)
    submitted = st.form_submit_button("Add Company")

    if submitted and name:
        st.session_state["companies"].append({
            "Company Name": name,
            "Market Opportunity": mo,
            "Product Feasibility": pf,
            "Business Model": bm,
            "Customer Validation": cv,
            "Competitive Advantage": ca,
            "Team Strength": ts,
            "Traction": tr,
            "Financial Readiness": fr
        })
        st.success(f"{name} added!")

if st.session_state["companies"]:
    st.header("📊 Scoring & Ranking")

    df = pd.DataFrame(st.session_state["companies"])

    weights = {
        "Market Opportunity": 0.20,
        "Product Feasibility": 0.15,
        "Business Model": 0.15,
        "Customer Validation": 0.15,
        "Competitive Advantage": 0.10,
        "Team Strength": 0.10,
        "Traction": 0.10,
        "Financial Readiness": 0.05
    }

    def compute_score(row):
        return round(sum(row[col] * weights[col] for col in weights) * 20, 2)

    df["Score (%)"] = df.apply(compute_score, axis=1)
    df["Rank"] = df["Score (%)"].rank(ascending=False, method="min").astype(int)
    df = df.sort_values("Score (%)", ascending=False)

    st.subheader("🏆 Ranked Companies")
    st.dataframe(df.reset_index(drop=True))

    st.download_button(
        label="📥 Download Scored CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="scored_companies.csv",
        mime="text/csv"
    )
