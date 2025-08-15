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

# --- Input method selection ---
input_method = st.sidebar.radio("How do you want to enter companies?", ["Upload CSV", "Enter Manually"])

# --- Data containers ---
company_list = []

# CSV Upload
if input_method == "Upload CSV":
    uploaded_file = st.sidebar.file_uploader("Upload a CSV with a 'Company' column", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        if "Company" not in df.columns:
            st.error("CSV must contain a 'Company' column.")
        else:
            company_list = df["Company"].tolist()

# Manual Entry
elif input_method == "Enter Manually":
    st.sidebar.subheader("Enter Company Names")
    num_companies = st.sidebar.number_input("Number of Companies", min_value=1, max_value=100, value=3, step=1)
    for i in range(num_companies):
        name = st.sidebar.text_input(f"Company {i+1} Name", key=f"manual_company_{i}")
        if name.strip():
            company_list.append(name.strip())

# --- Screening Section ---
if company_list:
    search_query = st.text_input("Search companies by name").strip().lower()

    scores = []
    answers = []

    for company_name in company_list:
        if search_query and search_query not in company_name.lower():
            continue

        st.subheader(company_name)
        company_answers = []
        score = 0
        cols = st.columns(2)
        for i, q in enumerate(questions):
            answer = cols[i % 2].radio(q, ["Yes", "No"], key=f"{company_name}_{i}")
            company_answers.append(answer)
            if answer == "Yes":
                score += 1

        scores.append({"Company": company_name, "Score": score})
        answers.append({"Company": company_name, **{q: company_answers[i] for i, q in enumerate(questions)}})

    # --- Results Table ---
    st.subheader("Company Scores")
    scores_df = pd.DataFrame(scores)
    sort_option = st.selectbox("Sort by", ["Score (High to Low)", "Score (Low to High)", "Company Name (A-Z)", "Company Name (Z-A)"])
    
    if sort_option == "Score (High to Low)":
        scores_df = scores_df.sort_values(by="Score", ascending=False)
    elif sort_option == "Score (Low to High)":
        scores_df = scores_df.sort_values(by="Score", ascending=True)
    elif sort_option == "Company Name (A-Z)":
        scores_df = scores_df.sort_values(by="Company", ascending=True)
    elif sort_option == "Company Name (Z-A)":
        scores_df = scores_df.sort_values(by="Company", ascending=False)

    st.dataframe(scores_df, use_container_width=True)

    # --- Download Results ---
    csv_buffer = io.StringIO()
    pd.DataFrame(answers).to_csv(csv_buffer, index=False)
    st.download_button("Download Results CSV", csv_buffer.getvalue(), "company_scores.csv", "text/csv")
else:
    st.info("Please upload a CSV or enter company names to begin.")
