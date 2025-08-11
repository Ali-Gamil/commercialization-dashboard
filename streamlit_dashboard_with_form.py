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
    "Business Model": 0.10,
    "Competitive Advantage": 0.10,
    "Customer Validation": 0.10,
    "Go-to-Market Readiness": 0.10,
    "Market Opportunity": 0.20,
    "Product Feasibility": 0.15,
    "Revenue Potential": 0.20,
    "Uniqueness": 0.05
}

assert abs(sum(weights.values()) - 1.0) < 1e-6, "Weights must sum to 1.0"

# Initialize session state keys
if "companies" not in st.session_state:
    st.session_state["companies"] = []

if "original_csv" not in st.session_state:
    st.session_state["original_csv"] = None

if "editing_company" not in st.session_state:
    st.session_state["editing_company"] = None

if "rerun_flag" not in st.session_state:
    st.session_state["rerun_flag"] = False

# Helper to force a rerun by toggling rerun_flag
def force_rerun():
    st.session_state.rerun_flag = not st.session_state.rerun_flag

# Reference rerun_flag so Streamlit sees its usage and triggers rerun on change
_ = st.session_state.rerun_flag

# --- CSV Upload in Sidebar ---
st.sidebar.header("🔄 Upload Companies CSV")
uploaded_file = st.sidebar.file_uploader("Upload CSV with companies and scores", type=["csv"])
if uploaded_file:
    try:
        df_uploaded = pd.read_csv(uploaded_file)
        required_columns = ["Company Name"] + list(criteria_info.keys())
        missing_cols = [col for col in required_columns if col not in df_uploaded.columns]
        if missing_cols:
            st.sidebar.error(f"CSV missing required columns: {missing_cols}")
        else:
            # Clean and convert criteria columns to int 1-5
            for crit in criteria_info.keys():
                df_uploaded[crit] = pd.to_numeric(df_uploaded[crit], errors='coerce').fillna(3).astype(int).clip(1, 5)
            st.session_state["companies"] = df_uploaded[required_columns].to_dict(orient="records")
            st.session_state["original_csv"] = uploaded_file.getvalue()
            st.success(f"Loaded {len(st.session_state['companies'])} companies from uploaded CSV")
            st.session_state["editing_company"] = None
            force_rerun()
    except Exception as e:
        st.sidebar.error(f"Failed to read CSV: {e}")

# Download Original Uploaded CSV
if st.session_state["original_csv"] is not None:
    st.sidebar.download_button(
        label="📥 Download Original Uploaded CSV",
        data=st.session_state["original_csv"],
        file_name="original_companies.csv",
        mime="text/csv",
    )

# Add New Company Form
st.header("➕ Add New Company")
with st.form("add_form"):
    new_name = st.text_input("Company Name")
    new_scores = {}
    for crit, desc in sorted(criteria_info.items()):
        weight_pct = int(weights[crit] * 100)
        label = f"{crit} ({weight_pct}%) — {desc}"
        new_scores[crit] = st.slider(label, 1, 5, 3)
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
            force_rerun()

# Search Bar
search_term = st.text_input("🔍 Search Companies by Name").strip().lower()

# Company Scores & Ranking
if st.session_state["companies"]:
    st.header("📊 Company Scores & Ranking")

    df = pd.DataFrame(st.session_state["companies"])

    def compute_score(row):
        return round(sum(row[col] * weights[col] for col in weights) * 20, 2)

    df["Score (%)"] = df.apply(compute_score, axis=1)
    df["Rank"] = df["Score (%)"].rank(ascending=False, method="min").astype(int)

    # Filter by search term
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

    for idx, row in df.reset_index(drop=True).iterrows():
        key_prefix = f"company_{row['Company Name']}"

        cols = st.columns([5, 2, 1, 1])
        cols[0].markdown(f"**{row['Company Name']}** — Rank: {row['Rank']} — Score: {row['Score (%)']}%")
        cols[1].progress(min(row["Score (%)"] / 100, 1.0))

        if cols[2].button("✏️ Edit", key=f"edit_{key_prefix}"):
            # Toggle edit mode for the clicked company
            if st.session_state["editing_company"] == row["Company Name"]:
                st.session_state["editing_company"] = None
            else:
                st.session_state["editing_company"] = row["Company Name"]
            force_rerun()

        if cols[3].button("❌ Delete", key=f"del_{key_prefix}"):
            st.session_state["companies"] = [c for c in st.session_state["companies"] if c["Company Name"] != row["Company Name"]]
            if st.session_state["editing_company"] == row["Company Name"]:
                st.session_state["editing_company"] = None
            force_rerun()

        if st.session_state["editing_company"] == row["Company Name"]:
            with st.form(f"edit_form_{key_prefix}"):
                edited_scores = {}
                for crit, desc in sorted(criteria_info.items()):
                    weight_pct = int(weights[crit] * 100)
                    label = f"{crit} ({weight_pct}%) — {desc}"
                    edited_scores[crit] = st.slider(label, 1, 5, row[crit], key=f"{key_prefix}_{crit}")
                submitted = st.form_submit_button("Save Changes")
                canceled = st.form_submit_button("Cancel")
                if submitted:
                    try:
                        idx_to_update = next(i for i, c in enumerate(st.session_state["companies"]) if c["Company Name"] == row["Company Name"])
                    except StopIteration:
                        st.error("Error: Company not found in session state.")
                    else:
                        companies_copy = st.session_state["companies"].copy()
                        companies_copy[idx_to_update].update(edited_scores)
                        st.session_state["companies"] = companies_copy
                        st.success(f"Updated '{row['Company Name']}'")
                        st.session_state["editing_company"] = None
                        force_rerun()
                if canceled:
                    st.session_state["editing_company"] = None
                    force_rerun()

# Download scored companies CSV
if st.session_state["companies"]:
    df = pd.DataFrame(st.session_state["companies"])
    df["Score (%)"] = df.apply(lambda row: round(sum(row[col] * weights[col] for col in weights) * 20, 2), axis=1)
    st.download_button(
        label="📥 Download Scored CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="scored_companies.csv",
        mime="text/csv"
    )
