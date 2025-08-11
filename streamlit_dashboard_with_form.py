import streamlit as st
import pandas as pd

st.title("📝 Company Commercialization Scoring Dashboard")

# Criteria descriptions
criteria_info = {
    "Business Model": "How well the company generates and sustains revenue",
    "Competitive Advantage": "Differentiation from competitors in a sustainable way",
    "Customer Validation": "Evidence of real customer demand or feedback",
    "Go-to-Market Readiness": "Preparedness for product/service launch",
    "Market Opportunity": "Size and growth potential of target market",
    "Product Feasibility": "Technical and operational feasibility of offering",
    "Revenue Potential": "Ability to generate significant, scalable income",
    "Uniqueness": "Originality and rarity of product/service in market"
}

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

# Initialize companies list in session state
if "companies" not in st.session_state:
    st.session_state["companies"] = []

# Initialize editing company key
if "edit_company" not in st.session_state:
    st.session_state["edit_company"] = None

# --- Add New Company Form ---
st.header("➕ Add New Company")
with st.form("add_form"):
    new_name = st.text_input("Company Name")

    new_scores = {}
    for crit, desc in sorted(criteria_info.items()):
        new_scores[crit] = st.slider(f"{crit} — {desc}", 1, 5, 3)

    add_submitted = st.form_submit_button("Add Company")

    if add_submitted:
        if not new_name.strip():
            st.error("Company Name cannot be empty.")
        elif any(c["Company Name"].lower() == new_name.strip().lower() for c in st.session_state["companies"]):
            st.error("Company with this name already exists.")
        else:
            entry = {"Company Name": new_name.strip()}
            entry.update(new_scores)
            st.session_state["companies"].append(entry)
            st.success(f"Company '{new_name.strip()}' added!")
            st.session_state["edit_company"] = None

# --- Edit Company Form ---
if st.session_state["companies"]:
    st.header("✏️ Edit Company")
    companies_names = [c["Company Name"] for c in st.session_state["companies"]]

    # Display clickable names to edit
    st.markdown("**Click company name below to edit:**")
    cols = st.columns(4)
    for i, cname in enumerate(companies_names):
        if cols[i % 4].button(cname):
            st.session_state["edit_company"] = cname

    if st.session_state["edit_company"]:
        company = next(c for c in st.session_state["companies"] if c["Company Name"] == st.session_state["edit_company"])
        st.subheader(f"Editing: {company['Company Name']}")
        with st.form("edit_form"):
            edited_scores = {}
            for crit, desc in sorted(criteria_info.items()):
                edited_scores[crit] = st.slider(f"{crit} — {desc}", 1, 5, company[crit])
            edit_submitted = st.form_submit_button("Save Changes")
            if edit_submitted:
                company.update(edited_scores)
                st.success(f"Updated '{company['Company Name']}'")
                st.session_state["edit_company"] = None

# --- Scoring & Ranking Table with delete buttons ---
if st.session_state["companies"]:
    st.header("📊 Scoring & Ranking")

    df = pd.DataFrame(st.session_state["companies"])

    def compute_score(row):
        return round(sum(row[col] * weights[col] for col in weights) * 20, 2)

    df["Score (%)"] = df.apply(compute_score, axis=1)
    df["Rank"] = df["Score (%)"].rank(ascending=False, method="min").astype(int)

    sort_option = st.radio(
        "Sort companies by:",
        ("Rank (highest score first)", "Alphabetical (Company Name)"),
        index=0
    )

    if sort_option == "Rank (highest score first)":
        df = df.sort_values(["Score (%)", "Company Name"], ascending=[False, True])
    else:
        df = df.sort_values("Company Name")

    # Display table with delete buttons per row
    st.markdown("### Company Scores")
    for idx, row in df.reset_index(drop=True).iterrows():
        cols = st.columns([4, 1])
        # Show company name + rank + score
        cols[0].markdown(f"**{row['Company Name']}** — Rank: {row['Rank']} — Score: {row['Score (%)']}%")
        # Delete button
        if cols[1].button("❌ Delete", key=f"del_{row['Company Name']}"):
            # Remove company from session state and rerun
            st.session_state["companies"] = [c for c in st.session_state["companies"] if c["Company Name"] != row["Company Name"]]
            st.experimental_rerun()

    st.download_button(
        label="📥 Download Scored CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="scored_companies.csv",
        mime="text/csv"
    )
