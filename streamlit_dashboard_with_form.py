import streamlit as st
import pandas as pd

st.title("📝 Company Commercialization Scoring Form & Dashboard")

# Initialize session state
if "companies" not in st.session_state:
    st.session_state["companies"] = []

st.header("📋 Company Evaluation Form")

with st.form("company_form"):
    name = st.text_input("Company Name")

    # Criteria in alphabetical order
    bm = st.slider("Business Model", 1, 5, 3)
    ca = st.slider("Competitive Advantage", 1, 5, 3)
    cv = st.slider("Customer Validation", 1, 5, 3)
    gtm = st.slider("Go-to-Market Readiness", 1, 5, 3)
    mo = st.slider("Market Opportunity", 1, 5, 3)
    pf = st.slider("Product Feasibility", 1, 5, 3)
    rp = st.slider("Revenue Potential", 1, 5, 3)
    uq = st.slider("Uniqueness", 1, 5, 3)

    submitted = st.form_submit_button("Add Company")

    if submitted and name:
        st.session_state["companies"].append({
            "Company Name": name,
            "Business Model": bm,
            "Competitive Advantage": ca,
            "Customer Validation": cv,
            "Go-to-Market Readiness": gtm,
            "Market Opportunity": mo,
            "Product Feasibility": pf,
            "Revenue Potential": rp,
            "Uniqueness": uq
        })
        st.success(f"{name} added!")

# If companies exist, show dashboard
if st.session_state["companies"]:
    st.header("📊 Scoring & Ranking")

    df = pd.DataFrame(st.session_state["companies"])

    # Weights stay the same, but keys match new order
    weights = {
        "Business Model": 0.15,
        "Competitive Advantage": 0.10,
        "Customer Validation": 0.10,
        "Go-to-Market Readiness": 0.10,
        "Market Opportunity": 0.20,
        "Product Feasibility": 0.15,
        "Revenue Potential": 0.20,
        "Uniqueness": 0.10
    }

    def compute_score(row):
        return round(sum(row[col] * weights[col] for col in weights) * 20, 2)

    df["Score (%)"] = df.apply(compute_score, axis=1)
    df["Rank"] = df["Score (%)"].rank(ascending=False, method="min").astype(int)

    # Sorting toggle
    sort_option = st.radio(
        "Sort companies by:",
        ("Rank (highest score first)", "Alphabetical (Company Name)")
    )

    if sort_option == "Rank (highest score first)":
        df = df.sort_values(["Score (%)", "Company Name"], ascending=[False, True])
    else:
        df = df.sort_values("Company Name")

    st.subheader("🏆 Company Scores")
    st.dataframe(df.reset_index(drop=True))

    st.download_button(
        label="📥 Download Scored CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="scored_companies.csv",
        mime="text/csv"
    )
