import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="⏱️ Hour & Percentile Calculator", page_icon="📊", layout="wide")

st.title("📊 Hour Difference + Percentile Calculator")

# --- Initialize session ---
if "df" not in st.session_state:
    st.session_state.df = None

# --- File Upload ---
uploaded_file = st.file_uploader("📤 Upload CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        xls = pd.ExcelFile(uploaded_file)
        sheet_name = st.selectbox("📑 Select a sheet to process:", xls.sheet_names)
        df = pd.read_excel(xls, sheet_name=sheet_name)
    st.session_state.df = df

if st.session_state.df is not None:
    df = st.session_state.df

    st.subheader("📋 Uploaded / Processed Data Preview")
    st.dataframe(df.head())

    # =========================================================
    # 🕒 STEP 1: MULTIPLE HOUR DIFFERENCE CALCULATION
    # =========================================================
    st.markdown("## ⏳ Step 1: Calculate Hour Differences")

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

    if st.button("➕ Calculate Hour Differences"):
        for (start_col, end_col) in pairs:
            try:
                start_time = pd.to_datetime(df[start_col], errors="coerce")
                end_time = pd.to_datetime(df[end_col], errors="coerce")
                diff_hours = (end_time - start_time).dt.total_seconds() / 3600

                # Convert hour format to hr.min format
                def convert_to_60min_format(x):
                    if pd.isna(x):
                        return None
                    hrs = int(x)
                    mins = round((x - hrs) * 60)
                    return round(hrs + mins / 100, 2)

                hr_col_name = f"{start_col}_to_{end_col}_Hr"
                df[hr_col_name] = diff_hours.apply(convert_to_60min_format)

            except Exception as e:
                st.error(f"⚠️ Error calculating {start_col} → {end_col}: {e}")

        st.session_state.df = df
        st.success("✅ Hour differences added successfully to main data!")
        st.dataframe(df.head(20))

    # =========================================================
    # 🎯 STEP 2: PERCENTILE CALCULATION (ONLY FOR HR COLUMNS)
    # =========================================================
    st.markdown("---")
    st.markdown("## 🎯 Step 2: Calculate Percentiles (Only for Hour Columns)")

    hr_cols = [col for col in df.columns if col.endswith("_Hr")]
    if not hr_cols:
        st.warning("⚠️ No hour difference columns found. Please calculate them first.")
    else:
        selected_hr_cols = st.multiselect("Select Hour Columns to Calculate Percentile:", hr_cols, default=hr_cols)
        percentile_options = [90, 95]
        selected_percentiles = st.multiselect("Select Percentile(s):", percentile_options, default=[95])
        group_col = st.selectbox("Select Grouping Column (Optional):", [None] + list(df.columns))

        if st.button("📈 Calculate Percentiles"):
            if selected_hr_cols:
                if group_col:
                    # Group-wise percentile
                    for p in selected_percentiles:
                        grouped = df.groupby(group_col)[selected_hr_cols].quantile(p / 100).reset_index()
                        df = pd.merge(df, grouped, on=group_col, how="left", suffixes=("", f"_P{p}"))
                else:
                    # Global percentile
                    for p in selected_percentiles:
                        for col in selected_hr_cols:
                            percentile_val = df[col].quantile(p / 100)
                            df[f"{col}_P{p}"] = percentile_val

                st.session_state.df = df
                st.success(f"✅ Percentiles ({', '.join(map(str, selected_percentiles))}) calculated successfully!")
                st.dataframe(df.head(20))
            else:
                st.warning("⚠️ Please select at least one hour column.")

    # =========================================================
    # 💾 STEP 3: DOWNLOAD FINAL DATA
    # =========================================================
    st.markdown("---")
    st.markdown("## 💾 Step 3: Download Final Updated Dataset")

    csv_data = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Full Data (CSV)",
        data=csv_data,
        file_name="final_data.csv",
        mime="text/csv"
    )

    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Processed_Data")
    st.download_button(
        label="⬇️ Download Full Data (Excel)",
        data=output.getvalue(),
        file_name="final_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.info("👆 Please upload a CSV or Excel file to begin.")
