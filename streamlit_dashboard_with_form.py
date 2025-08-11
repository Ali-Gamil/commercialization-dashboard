import streamlit as st
import pandas as pd

st.title("📝 Company Commercialization Scoring Dashboard")

# Initialize session state
if "companies" not in st.session_state:
    st.session_state["companies"] = []

# ===================== ADD COMPANY FORM =====================
st.header("➕ Add New Company")
with st.form("add_form"):
    name = st.text_input("Company Name")

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

# ===================== EDIT COMPANY FORM =====================
if st.session_state["companies"]:
    st.header("✏️ Edit Existing Company")
    company_names = [c["Company Name"] for c in st.session_state["companies"]]
    company_to_edit = st.selectbox("Select company to edit", [""] + company_names)

    if company_to_edit:
        company_data = next(c for c in st.session_state["companies"] if c["Company Name"] == company_to_edit)

        with st.form("edit_form"):
            bm = st.slider("Business Model", 1, 5, company_data["Business Model"])
            ca = st.slider("Competitive Advantage", 1, 5, company_data["Competitive Advantage"])
            cv = st.slider("Customer Validation", 1, 5, company_data["Customer Validation"])
            gtm = st.slider("Go-to-Market Readiness", 1, 5, company_data["Go-to-Market Readiness"])
            mo = st.slider("Market Opportunity", 1, 5, company_data["Market Opportunity"])
            pf = st.slider("Product Feasibility", 1, 5, company_data["Product Feasibility"])
            rp = st.slider("Revenue Potential", 1, 5, company_data["Revenue Potential"])
            uq = st.slider("Uniqueness", 1, 5, company_data["Uniqueness"])

            update_submitted = st.form_submit_button("Update Company")
            if update_submitted:
                company_data.update({
                    "Business Model": bm,
                    "Competitive Advantage": ca,
                    "Customer Validation": cv,
                    "Go-to-Market Readiness": gtm,
                    "Market Opportunity": mo,
                    "Product Feasibility": pf,
                    "Revenue Potential": rp,
                    "Uniqueness": uq
                })
                st.success(f"{company_to_edit} updated!")

# ===================== DELETE COMPANIES =====================
if st.session_state["companies"]:
    st.header("🗑 Delete Companies")
    delete_list = st.multiselect("Select companies to delete", [c["Company Name"] for c in st.session_state["companies"]])
    if st.button("Delete Selected"):
        st.session_state["companies"] = [c for c in st.session_state["companies"] if c["Company Name"] not in delete_list]
        st.success("Selected companies deleted!")

# ===================== SCORING & RANKING =====================
if st.session_state["companies"]:
    st.header("📊 Scoring & Ranking")

    df = pd.DataFrame(st.session_state["companies"])

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
