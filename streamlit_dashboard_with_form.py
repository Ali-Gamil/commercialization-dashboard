import streamlit as st
import pandas as pd
import io

st.set_page_config(layout="wide")
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
    "Business Model": 0.10,
    "Competitive Advantage": 0.10,
    "Customer Validation": 0.10,
    "Go-to-Market Readiness": 0.10,
    "Market Opportunity": 0.20,
    "Product Feasibility": 0.15,
    "Revenue Potential": 0.20,
    "Uniqueness": 0.05
}

def compute_score(row):
    return round(sum(row[col] * weights[col] for col in weights) * 20, 2)

if "companies" not in st.session_state:
    st.session_state["companies"] = []

if "editing_company" not in st.session_state:
    st.session_state["editing_company"] = None

if "delete_candidate" not in st.session_state:
    st.session_state["delete_candidate"] = None

# --- Data Upload ---
st.sidebar.header("🔄 Upload / Download Dataset")
uploaded_file = st.sidebar.file_uploader("Upload CSV to load companies", type=["csv"])
if uploaded_file:
    try:
        df_uploaded = pd.read_csv(uploaded_file)
        expected_cols = ["Company Name"] + list(criteria_info.keys())
        if not all(col in df_uploaded.columns for col in expected_cols):
            st.sidebar.error(f"CSV missing required columns: {expected_cols}")
        else:
            st.session_state["companies"] = df_uploaded[expected_cols].to_dict(orient="records")
            st.success(f"Loaded {len(st.session_state['companies'])} companies from file.")
    except Exception as e:
        st.sidebar.error(f"Failed to load CSV: {e}")

# --- Data Download ---
if st.session_state["companies"]:
    df_download = pd.DataFrame(st.session_state["companies"])
    df_download["Score (%)"] = df_download.apply(compute_score, axis=1)

    csv_data = df_download.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button("📥 Download CSV", data=csv_data, file_name="companies.csv", mime="text/csv")

# --- Add Company ---
st.header("➕ Add New Company")
with st.form("add_form"):
    new_name = st.text_input("Company Name")

    new_scores = {}
    for crit, desc in sorted(criteria_info.items()):
        weight_pct = int(weights[crit]*100)
        label = f"{crit} ({weight_pct}%) — {desc}"
        new_scores[crit] = st.slider(label, 1, 5, 3, key=f"add_{crit}")

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

# --- Search Filter ---
search_term = st.text_input("🔍 Search Companies by Name").strip().lower()

# --- Main Table ---
if st.session_state["companies"]:
    df = pd.DataFrame(st.session_state["companies"])
    df["Score (%)"] = df.apply(compute_score, axis=1)
    df["Rank"] = df["Score (%)"].rank(ascending=False, method="min").astype(int)

    # Filter by search
    if search_term:
        df = df[df["Company Name"].str.lower().str.contains(search_term)]

    sort_option = st.radio(
        "Sort companies by:",
        ("Rank (highest score first)", "Alphabetical (Company Name)"),
        index=0
    )

    if sort_option == "Rank (highest score first)":
        df = df.sort_values(["Score (%)", "Company Name"], ascending=[False, True])
    else:
        df = df.assign(SortKey=df["Company Name"].str.lower())
        df = df.sort_values("SortKey")
        df = df.drop(columns=["SortKey"])

    st.header(f"📊 Company Scores & Ranking ({len(df)} shown)")

    for idx, row in df.reset_index(drop=True).iterrows():
        key_prefix = f"company_{row['Company Name']}"

        cols = st.columns([5, 2, 1, 1])
        cols[0].markdown(f"**{row['Company Name']}** — Rank: {row['Rank']} — Score: {row['Score (%)']}%")

        score = row["Score (%)"]
        cols[1].progress(min(score / 100, 1.0))

        if cols[2].button("✏️ Edit", key=f"edit_{key_prefix}"):
            if st.session_state["editing_company"] == row["Company Name"]:
                st.session_state["editing_company"] = None
            else:
                st.session_state["editing_company"] = row["Company Name"]

        if cols[3].button("❌ Delete", key=f"del_{key_prefix}"):
            st.session_state["delete_candidate"] = row["Company Name"]

        if st.session_state["editing_company"] == row["Company Name"]:
            with st.form(f"edit_form_{key_prefix}"):
                edited_scores = {}
                for crit, desc in sorted(criteria_info.items()):
                    weight_pct = int(weights[crit] * 100)
                    label = f"{crit} ({weight_pct}%) — {desc}"
                    edited_scores[crit] = st.slider(label, 1, 5, row[crit], key=f"edit_{key_prefix}_{crit}")
                submitted = st.form_submit_button("Save Changes")
                canceled = st.form_submit_button("Cancel")
                if submitted:
                    idx_to_update = None
                    for i, comp in enumerate(st.session_state["companies"]):
                        if comp["Company Name"] == row["Company Name"]:
                            idx_to_update = i
                            break
                    if idx_to_update is not None:
                        companies_copy = st.session_state["companies"].copy()
                        for crit, val in edited_scores.items():
                            companies_copy[idx_to_update][crit] = val
                        st.session_state["companies"] = companies_copy
                        st.success(f"Updated '{row['Company Name']}'")
                        st.session_state["editing_company"] = None
                        st.experimental_rerun()
                    else:
                        st.error("Company not found.")
                if canceled:
                    st.session_state["editing_company"] = None

# Delete confirmation
if st.session_state.get("delete_candidate", None):
    company_to_delete = st.session_state["delete_candidate"]
    st.warning(f"Are you sure you want to delete **{company_to_delete}**? This action cannot be undone.")
    confirm_col, cancel_col = st.columns(2)
    with confirm_col:
        if st.button("Yes, delete"):
            st.session_state["companies"] = [c for c in st.session_state["companies"] if c["Company Name"] != company_to_delete]
            st.session_state["delete_candidate"] = None
            st.success(f"Deleted company '{company_to_delete}'")
            st.experimental_rerun()
    with cancel_col:
        if st.button("Cancel"):
            st.session_state["delete_candidate"] = None

if not st.session_state["companies"]:
    st.info("No companies added yet. Use the form above or upload a dataset.")
