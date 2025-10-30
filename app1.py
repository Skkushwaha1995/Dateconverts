import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Date-Time & Multi Hour Difference Tool", page_icon="⏱️", layout="wide")

st.title("⏱️ Multiple Hour Difference Calculator (in 60-minute Format)")

# --- File Upload ---
uploaded_file = st.file_uploader("📤 Upload CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file:
    # Read file
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        xls = pd.ExcelFile(uploaded_file)
        sheet_name = st.selectbox("📑 Select a sheet to process:", xls.sheet_names)
        df = pd.read_excel(xls, sheet_name=sheet_name)

    st.subheader("📋 Uploaded Data Preview")
    st.dataframe(df.head())

    # --- Multiple Pair Selection ---
    st.markdown("### ⏳ Step 1: Add Hour Difference Pairs")

    num_pairs = st.number_input("How many column pairs do you want to calculate?", min_value=1, max_value=10, value=1)
    pairs = []

    for i in range(num_pairs):
        st.markdown(f"**🕒 Pair {i+1}**")
        c1, c2 = st.columns(2)
        with c1:
            start_col = st.selectbox(f"Select Start Time Column (Pair {i+1})", df.columns, key=f"start_{i}")
        with c2:
            end_col = st.selectbox(f"Select End Time Column (Pair {i+1})", df.columns, key=f"end_{i}")
        pairs.append((start_col, end_col))

    # --- Button to Calculate All ---
    if st.button("➕ Calculate All Hour Differences"):
        for (start_col, end_col) in pairs:
            try:
                start_time = pd.to_datetime(df[start_col], errors="coerce")
                end_time = pd.to_datetime(df[end_col], errors="coerce")

                # Time difference in hours (decimal)
                time_diff = end_time - start_time
                hours = time_diff.dt.total_seconds() / 3600

                def convert_to_60min_format(x):
                    if pd.isna(x):
                        return None
                    hrs = int(x)
                    mins = round((x - hrs) * 60)
                    return round(hrs + mins / 100, 2)

                df[f"{start_col}_to_{end_col}_Hr"] = hours.apply(convert_to_60min_format)
            except Exception as e:
                st.error(f"Error in {start_col} → {end_col}: {e}")

        st.success("✅ All selected hour differences calculated!")
        st.dataframe(df.head(20))

    # --- Download Section ---
    st.markdown("---")
    st.markdown("### 📥 Step 2: Download Updated Data")

    csv_data = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download CSV",
        data=csv_data,
        file_name="multi_hour_difference.csv",
        mime="text/csv"
    )

    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Processed_Data")
    st.download_button(
        label="⬇️ Download Excel",
        data=output.getvalue(),
        file_name="multi_hour_difference.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.info("👆 Please upload a CSV or Excel file to start.")
