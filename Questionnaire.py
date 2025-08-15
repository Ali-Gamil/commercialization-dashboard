import streamlit as st
import pandas as pd
import io

# --- Page settings ---
st.set_page_config(page_title="Commercialization Screening", layout="wide")
st.title("Commercialization Readiness Screening Dashboard")

# --- Questions ---
questions = [
    "Does the company have a defined product or service concept?",
    "Does the company have at least one prototype created?",
    "Does the company have a clearly identified target market?",
    "Has the company tested the product/service with potential customers?",
    "Does the company have pre-orders, letters of intent, or confirmed customer interest?",
    "Does the company have a clear revenue model?",
    "Does the company have the freedom to operate without major legal barriers in its target market?",
    "Does the company know its key competitors?",
    "Does the company have a clear explanation of how it differs from its competitors?",
    "Does the company have access to necessary equipment, facilities, or technology?"
]

# --- Sidebar for CSV upload ---
st.sidebar.header("Upload Company List")
uploaded_file = st.sidebar.file_uploader("Upload a CSV with a 'Company' column", type="csv")

# Example CSV template
if st.sidebar.button("Download CSV Template"):
    template_df = pd.DataFrame({"Company": ["Example Company 1", "Example Company 2"]})
    csv_bytes = template_df.to_csv(index=False).encode()
    st.sidebar.download_button("Download Template", csv_bytes, "template.csv", "text/csv")

# --- Data containers ---
all_answers = []

# --- Mode 1: CSV-based screening ---
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    if "Company" not in df.columns:
        st.error("CSV must contain a 'Company' column.")
    else:
        st.subheader("📂 Screening Companies from CSV")
        search_query = st.text_input("Search companies by name", key="csv_search").strip().lower()

        for idx, row in df.iterrows():
            company_name = row["Company"]
            if search_query and search_query not in company_name.lower():
                continue

            st.markdown(f"### {company_name}")
            company_answers = {}
            score = 0
            cols = st.columns(2)
            for i, q in enumerate(questions):
                answer = cols[i % 2].radio(q, ["Yes", "No"], key=f"{company_name}_{i}")
                company_answers[q] = answer
                if answer == "Yes":
                    score += 1
            company_answers["Company"] = company_name
            company_answers["Score"] = score
            all_answers.append(company_answers)

# --- Mode 2: Manual single-company screening ---
st.subheader("✏️ Quick Screening (No CSV Required)")
manual_company_name = st.text_input("Enter Company Name", placeholder="Type company name here", key="manual_name")
if manual_company_name:
    st.markdown(f"### {manual_company_name}")
    manual_answers = {}
    score = 0
    cols = st.columns(2)
    for i, q in enumerate(questions):
        answer = cols[i % 2].radio(q, ["Yes", "No"], key=f"manual_{i}")
        manual_answers[q] = answer
        if answer == "Yes":
            score += 1
    manual_answers["Company"] = manual_company_name
    manual_answers["Score"] = score
    all_answers.append(manual_answers)

# --- Show combined results if any ---
if all_answers:
    st.subheader("📊 Combined Company Scores")
    results_df = pd.DataFrame(all_answers)

    # Sorting options
    sort_option = st.selectbox("Sort by", ["Score (High to Low)", "Score (Low to High)", "Company Name (A-Z)", "Company Name (Z-A)"])
    if sort_option == "Score (High to Low)":
        results_df = results_df.sort_values(by="Score", ascending=False)
    elif sort_option == "Score (Low to High)":
        results_df = results_df.sort_values(by="Score", ascending=True)
    elif sort_option == "Company Name (A-Z)":
        results_df = results_df.sort_values(by="Company", ascending=True)
    elif sort_option == "Company Name (Z-A)":
        results_df = results_df.sort_values(by="Company", ascending=False)

    st.dataframe(results_df, use_container_width=True)

    # Download all results
    csv_buffer = io.StringIO()
    results_df.to_csv(csv_buffer, index=False)
    st.download_button("Download All Results CSV", csv_buffer.getvalue(), "all_company_scores.csv", "text/csv")
