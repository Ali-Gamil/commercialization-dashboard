
import streamlit as st
import pandas as pd

st.title("🚀 Company Commercialization Scoring Dashboard")
st.markdown("Upload a CSV with company evaluation scores (1–5 scale) to get automatic ranking and scoring.")

uploaded_file = st.file_uploader("📂 Upload companies CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Define scoring weights
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

    # Calculate score for each row
    def compute_score(row):
        return round(sum(row[col] * weights[col] for col in weights) * 20, 2)

    df["Score (%)"] = df.apply(compute_score, axis=1)
    df["Rank"] = df["Score (%)"].rank(ascending=False, method="min").astype(int)
    df = df.sort_values("Score (%)", ascending=False)

    st.subheader("📊 Full Company Rankings")
    st.dataframe(df.reset_index(drop=True))

    st.subheader("🏆 Top 10 Companies")
    st.table(df.head(10)[["Company Name", "Score (%)", "Rank"]])

    st.download_button(
        label="📥 Download Scored CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="scored_companies.csv",
        mime="text/csv"
    )
else:
    st.info("Upload a CSV file to begin.")
