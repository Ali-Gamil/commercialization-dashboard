import streamlit as st
import pandas as pd

st.title("📝 Company Commercialization Scoring Dashboard")

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

# Track which company is currently being edited inline
if "editing_company" not in st.session_state:
    st.session_state["editing_company"] = None

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
            st.session_state["editing_company"] = None

# --- Scoring & Ranking Table with inline editing and delete ---
if st.session_state["companies"]:
    st.header("📊 Company Scores & Ranking")

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

    # Display list with inline editing and delete button
    for idx, row in df.reset_index(drop=True).iterrows():
        key_prefix = f"company_{row['Company Name']}"

        if st.session_state["editing_company"] == row["Company Name"]:
            st.markdown(f"### Editing: {row['Company Name']} (Rank: {row['Rank']}, Score: {row['Score (%)']}%)")
            with st.form(f"edit_form_{key_prefix}"):
                edited_scores = {}
                for crit, desc in sorted(criteria_info.items()):
                    edited_scores[crit] = st.slider(f"{crit} — {desc}", 1, 5, row[crit], key=f"{key_prefix}_{crit}")
                submitted = st.form_submit_button("Save Changes")
                cancel = st.form_submit_button("Cancel")
                if submitted:
                    # Update the company in session_state
                    for c in st.session_state["companies"]:
                        if c["Company Name"] == row["Company Name"]:
                            c.update(edited_scores)
                            break
                    st.success(f"Updated '{row['Company Name']}'")
                    st.session_state["editing_company"] = None
                    st.experimental_rerun()
                if cancel:
                    st.session_state["editing_company"] = None
                    st.experimental_rerun()

        else:
            cols = st.columns([5, 1, 1])
            # Company name as clickable button for edit
            if cols[0].button(f"{row['Company Name']} (Rank: {row['Rank']}, Score: {row['Score (%)']}%)", key=f"btn_{key_prefix}"):
                st.session_state["editing_company"] = row["Company Name"]
                st.experimental_rerun()
            # Empty placeholder for alignment
            cols[1].write("")
            # Delete button
            if cols[2].button("❌ Delete", key=f"del_{key_prefix}"):
                st.session_state["companies"] = [c for c in st.session_state["companies"] if c["Company Name"] != row["Company Name"]]
                if st.session_state["editing_company"] == row["Company Name"]:
                    st.session_state["editing_company"] = None
                st.experimental_rerun()

    st.download_button(
        label="📥 Download Scored CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="scored_companies.csv",
        mime="text/csv"
    )
