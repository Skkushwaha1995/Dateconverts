import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

st.set_page_config(page_title="Time Difference + Percentile Calculator", page_icon="⏱️", layout="wide")
st.title("⏱️ Time Difference + Percentile Calculator")

# --- Upload File ---
uploaded_file = st.file_uploader("📂 Upload Excel or CSV file", type=["xlsx", "csv"])

if uploaded_file:
    # Read file
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.success("✅ File uploaded successfully!")

    # --- Step 1: Select Columns to Calculate Hour Difference ---
    st.subheader("⚙️ Hour Difference Calculation")

    time_columns = df.columns.tolist()
    col_pairs = st.multiselect(
        "Select column pairs for hour difference (Start ➜ End)",
        time_columns,
        placeholder="Example: collection_time, sync_time_to_report_approval_time"
    )

    if len(col_pairs) >= 2 and len(col_pairs) % 2 == 0:
        for i in range(0, len(col_pairs), 2):
            start_col = col_pairs[i]
            end_col = col_pairs[i + 1]
            new_col = f"{start_col}_to_{end_col}_Hr"

            # Convert to datetime
            df[start_col] = pd.to_datetime(df[start_col], errors='coerce')
            df[end_col] = pd.to_datetime(df[end_col], errors='coerce')

            # Calculate hour difference
            df[new_col] = (df[end_col] - df[start_col]).dt.total_seconds() / 3600
            df[new_col] = df[new_col].round(2)  # round to 2 decimals

        st.success("✅ Hour difference columns calculated successfully!")

    # --- Step 2: Percentile Calculation ---
    st.subheader("📈 Percentile Calculation")

    hr_cols = [c for c in df.columns if c.endswith("_Hr")]

    if hr_cols:
        percentile_cols = st.multiselect(
            "Select hour columns for percentile calculation",
            hr_cols
        )

        percentile_value = st.selectbox(
            "Select percentile value",
            [90, 95, 99],
            index=1
        )

        if st.button("Calculate Percentile"):
            for col in percentile_cols:
                if col in df.columns:
                    val = np.percentile(df[col].dropna(), percentile_value)
                    new_col = f"{col}_P{percentile_value}"
                    df[new_col] = round(val, 2)  # ✅ Rounded percentile (like 8.20)

            st.success(f"✅ {percentile_value}th percentile calculated and added to main data!")

    # --- Step 3: Display Final Data ---
    st.subheader("🧾 Final Data Preview")
    st.dataframe(df)

    # --- Step 4: Download Option ---
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    st.download_button(
        label="📥 Download Processed File",
        data=buffer.getvalue(),
        file_name="processed_time_percentile.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("📤 Please upload a file to start processing.")
