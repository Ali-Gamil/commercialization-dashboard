import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("📝 Company Commercialization Scoring Dashboard")

CRITERIA_INFO = {
    "Business Model": "How well the company generates and sustains revenue",
    "Competitive Advantage": "Differentiation from competitors in a sustainable way",
    "Customer Validation": "Evidence of real customer demand or feedback",
    "Go-to-Market Readiness": "Preparedness for product/service launch",
    "Market Opportunity": "Size and growth potential of target market",
    "Product Feasibility": "Technical and operational feasibility of offering",
    "Revenue Potential": "Ability to generate significant, scalable income",
    "Uniqueness": "Originality and rarity of product/service in market",
}

CRITERIA_WEIGHTS = {
    "Business Model": 0.10,
    "Competitive Advantage": 0.10,
    "Customer Validation": 0.10,
    "Go-to-Market Readiness": 0.10,
    "Market Opportunity": 0.20,
    "Product Feasibility": 0.15,
    "Revenue Potential": 0.20,
    "Uniqueness": 0.05,
}

def init_session_state():
    if "companies" not in st.session_state:
        st.session_state["companies"] = []
    if "editing_company" not in st.session_state:
        st.session_state["editing_company"] = None
    if "delete_candidate" not in st.session_state:
        st.session_state["delete_candidate"] = None

def compute_score(company):
    score = 0.0
    for crit, weight in CRITERIA_WEIGHTS.items():
        val = company.get(crit, 0)
        score += val * weight
    max_score = 5 * sum(CRITERIA_WEIGHTS.values())
    return round((score / max_score) * 100, 2)

def handle_file_upload():
    st.sidebar.header("🔄 Upload / Download Dataset")
    uploaded_file = st.sidebar.file_uploader("Upload CSV to load companies", type=["csv"])
    if uploaded_file:
        try:
            df_uploaded = pd.read_csv(uploaded_file)
            expected_cols = ["Company Name"] + list(CRITERIA_INFO.keys())
            if not all(col in df_uploaded.columns for col in expected_cols):
                st.sidebar.error(f"CSV missing required columns: {expected_cols}")
            else:
                for crit in CRITERIA_INFO.keys():
                    df_uploaded[crit] = pd.to_numeric(df_uploaded[crit], errors='coerce').fillna(3).astype(int).clip(1,5)
                st.session_state["companies"] = df_uploaded[expected_cols].to_dict(orient="records")
                st.success(f"Loaded {len(st.session_state['companies'])} companies from file.")
                st.experimental_rerun()
        except Exception as e:
            st.sidebar.error(f"Failed to load CSV: {e}")

def provide_csv_download():
    if st.session_state["companies"]:
        df = pd.DataFrame(st.session_state["companies"])
        df["Score (%)"] = df.apply(compute_score, axis=1)
        csv_data = df.to_csv(index=False).encode("utf-8")
        st.sidebar.download_button(
            "📥 Download Companies CSV",
            data=csv_data,
            file_name="companies.csv",
            mime="text/csv",
        )

def add_company_form():
    st.header("➕ Add New Company")
    with st.form("add_form", clear_on_submit=True):
        new_name = st.text_input("Company Name")
        new_scores = {}
        for crit, desc in sorted(CRITERIA_INFO.items()):
            weight_pct = int(CRITERIA_WEIGHTS[crit] * 100)
            label = f"{crit} ({weight_pct}%) — {desc}"
            new_scores[crit] = st.slider(label, 1, 5, 3, key=f"add_{crit}")
        submitted = st.form_submit_button("Add Company")
        if submitted:
            if not new_name.strip():
                st.error("Company Name cannot be empty.")
                return
            if any(c["Company Name"].lower() == new_name.strip().lower() for c in st.session_state["companies"]):
                st.error("Company with this name already exists.")
                return
            entry = {"Company Name": new_name.strip()}
            entry.update(new_scores)
            st.session_state["companies"].append(entry)
            st.success(f"Company '{new_name.strip()}' added!")
            st.experimental_rerun()  # <--- immediate rerun after add

def display_companies():
    if not st.session_state["companies"]:
        st.info("No companies added yet. Use the form above or upload a dataset.")
        return

    df = pd.DataFrame(st.session_state["companies"])
    df["Score (%)"] = df.apply(compute_score, axis=1)
    df["Rank"] = df["Score (%)"].rank(ascending=False, method="min").astype(int)

    search_term = st.text_input("🔍 Search Companies by Name").strip().lower()

    filtered_df = df
    if search_term:
        filtered_df = df[df["Company Name"].str.lower().str.contains(search_term)]

    sort_option = st.radio(
        "Sort companies by:",
        ("Rank (highest score first)", "Alphabetical (Company Name)"),
        index=0,
    )

    if sort_option == "Rank (highest score first)":
        filtered_df = filtered_df.sort_values(["Score (%)", "Company Name"], ascending=[False, True])
    else:
        filtered_df = filtered_df.assign(SortKey=filtered_df["Company Name"].str.lower())
        filtered_df = filtered_df.sort_values("SortKey").drop(columns=["SortKey"])

    st.header(f"📊 Company Scores & Ranking ({len(filtered_df)} shown)")

    for _, row in filtered_df.iterrows():
        key_prefix = f"company_{row['Company Name']}"
        cols = st.columns([5, 2, 1, 1])
        cols[0].markdown(f"**{row['Company Name']}** — Rank: {row['Rank']} — Score: {row['Score (%)']}%")
        cols[1].progress(min(row["Score (%)"] / 100, 1.0))

        if cols[2].button("✏️ Edit", key=f"edit_{key_prefix}"):
            if st.session_state["editing_company"] == row["Company Name"]:
                st.session_state["editing_company"] = None
            else:
                st.session_state["editing_company"] = row["Company Name"]
            st.experimental_rerun()  # <--- rerun to show/hide edit form instantly

        if cols[3].button("❌ Delete", key=f"del_{key_prefix}"):
            st.session_state["delete_candidate"] = row["Company Name"]
            st.experimental_rerun()  # <--- rerun to show delete confirmation instantly

        if st.session_state["editing_company"] == row["Company Name"]:
            with st.form(f"edit_form_{key_prefix}"):
                edited_scores = {}
                for crit, desc in sorted(CRITERIA_INFO.items()):
                    weight_pct = int(CRITERIA_WEIGHTS[crit] * 100)
                    label = f"{crit} ({weight_pct}%) — {desc}"
                    current_val = row[crit] if crit in row else 3
                    edited_scores[crit] = st.slider(label, 1, 5, current_val, key=f"edit_{key_prefix}_{crit}")
                submitted = st.form_submit_button("Save Changes")
                canceled = st.form_submit_button("Cancel")
                if submitted:
                    idx = next((i for i, c in enumerate(st.session_state["companies"]) if c["Company Name"] == row["Company Name"]), None)
                    if idx is not None:
                        for crit, val in edited_scores.items():
                            st.session_state["companies"][idx][crit] = val
                        st.success(f"Updated '{row['Company Name']}'")
                        st.session_state["editing_company"] = None
                        st.experimental_rerun()  # <--- instant update after save
                    else:
                        st.error("Company not found.")
                if canceled:
                    st.session_state["editing_company"] = None
                    st.experimental_rerun()  # <--- instant update after cancel

def handle_delete():
    if st.session_state.get("delete_candidate"):
        company_to_delete = st.session_state["delete_candidate"]
        st.warning(f"Are you sure you want to delete **{company_to_delete}**? This action cannot be undone.")
        confirm_col, cancel_col = st.columns(2)
        with confirm_col:
            if st.button("Yes, delete"):
                st.session_state["companies"] = [c for c in st.session_state["companies"] if c["Company Name"] != company_to_delete]
                st.session_state["delete_candidate"] = None
                st.success(f"Deleted company '{company_to_delete}'")
                st.experimental_rerun()  # <--- instant update after delete
        with cancel_col:
            if st.button("Cancel"):
                st.session_state["delete_candidate"] = None
                st.experimental_rerun()  # <--- instant update after cancel
# Main flow
init_session_state()
handle_file_upload()
provide_csv_download()
add_company_form()
display_companies()
handle_delete()
