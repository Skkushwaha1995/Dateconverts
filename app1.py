import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Date-Time & Hour Difference Tool", page_icon="⏱️", layout="wide")

st.title("⏱️ Date-Time Difference Calculator (in 60-minute Format)")

# --- File Upload ---
uploaded_file = st.file_uploader("📤 Upload CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file:
    # Detect file type
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        xls = pd.ExcelFile(uploaded_file)
        sheet_name = st.selectbox("📑 Select a sheet to process:", xls.sheet_names)
        df = pd.read_excel(xls, sheet_name=sheet_name)

    st.subheader("📋 Uploaded Data Preview")
    st.dataframe(df.head())

    # --- Convert datetime columns ---
    datetime_cols = []
    for col in df.columns:
        try:
            df[col] = pd.to_datetime(df[col], errors='raise')
            datetime_cols.append(col)
        except:
            pass

    if not datetime_cols:
        st.error("⚠️ No valid datetime columns found!")
        st.stop()

    st.markdown("### ⏳ Step 1: Calculate Hour Differences")

    # Dynamic start and end column selection
    col1, col2 = st.columns(2)
    with col1:
        start_col = st.selectbox("Select Start Time Column", datetime_cols, key="start")
    with col2:
        end_col = st.selectbox("Select End Time Column", datetime_cols, key="end")

    if st.button("➕ Calculate Hour Difference"):
    if start_col == end_col:
        st.warning("⚠️ Start and End columns cannot be the same!")
    else:
        # Calculate time difference
        time_diff = df[end_col] - df[start_col]
        hours = time_diff.dt.total_seconds() / 3600

        # Convert to 60-minute style safely
        def convert_to_60min_format(x):
            if pd.isna(x):
                return None
            hrs = int(x)
            mins = round((x - hrs) * 60)
            return round(hrs + mins / 100, 2)

        hours_60min = hours.apply(convert_to_60min_format)

        # Add new column
        new_col_name = f"{start_col}_to_{end_col}_Hr"
        df[new_col_name] = hours_60min

        st.success(f"✅ Added new column: {new_col_name}")


    # --- View Section ---
    st.markdown("### 👀 Step 2: View Data")

    view_option = st.radio(
        "Select what you want to view:",
        ["Full Data", "Only Hour Difference Columns"],
        horizontal=True
    )

    hr_columns = [col for col in df.columns if col.endswith("_Hr")]

    if view_option == "Only Hour Difference Columns" and hr_columns:
        st.dataframe(df[hr_columns].head(30))
    else:
        st.dataframe(df.head(30))

    # --- Download Section ---
    st.markdown("---")
    st.markdown("### 📥 Step 3: Download Updated Data")

    csv_data = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download CSV",
        data=csv_data,
        file_name="time_difference_result.csv",
        mime="text/csv"
    )

    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Processed_Data")
    st.download_button(
        label="⬇️ Download Excel",
        data=output.getvalue(),
        file_name="time_difference_result.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.info("👆 Please upload a CSV or Excel file to begin.")
