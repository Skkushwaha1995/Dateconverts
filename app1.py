import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Date-Time + Hour & Percentile Calculator", page_icon="⏱️", layout="wide")

st.title("📊 Multi Hour Difference + Percentile Calculator")

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

    # =========================================================
    # 🕒 STEP 1: MULTIPLE HOUR DIFFERENCE CALCULATION
    # =========================================================
    st.markdown("## ⏳ Step 1: Add Hour Difference Pairs")

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

    if st.button("➕ Calculate All Hour Differences"):
        for (start_col, end_col) in pairs:
            try:
                start_time = pd.to_datetime(df[start_col], errors="coerce")
                end_time = pd.to_datetime(df[end_col], errors="coerce")

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

        st.success("✅ All selected hour differences calculated and added to main file!")
        st.dataframe(df.head(20))

    # =========================================================
    # 🎯 STEP 2: PERCENTILE CALCULATION
    # =========================================================
    st.markdown("---")
    st.markdown("## 🎯 Step 2: Percentile Calculation")

    numeric_cols = df.select_dtypes(include=['number', 'float', 'int']).columns.tolist()
    selected_cols = st.multiselect("Select numeric columns to calculate percentile:", numeric_cols)

    percentile_value = st.number_input("Enter percentile value (e.g. 90, 95):", min_value=1, max_value=100, value=95)

    group_col = st.selectbox("Select grouping column (optional):", [None] + list(df.columns))

    if st.button("📈 Calculate Percentile"):
        if selected_cols:
            result = []

            if group_col:
                grouped = df.groupby(group_col)
                for col in selected_cols:
                    temp = grouped[col].quantile(percentile_value / 100).reset_index()
                    temp.columns = [group_col, f"{col}_P{percentile_value}"]
                    result.append(temp)
                final_percentile_df = result[0]
                for r in result[1:]:
                    final_percentile_df = pd.merge(final_percentile_df, r, on=group_col, how="outer")
            else:
                data = {f"{col}_P{percentile_value}": [df[col].quantile(percentile_value / 100)] for col in selected_cols}
                final_percentile_df = pd.DataFrame(data)

            st.success(f"✅ Percentile ({percentile_value}th) calculated successfully!")
            st.dataframe(final_percentile_df)

            # --- Download Results ---
            csv_data = final_percentile_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Download Percentile Data (CSV)",
                data=csv_data,
                file_name=f"percentile_P{percentile_value}.csv",
                mime="text/csv"
            )
        else:
            st.warning("⚠️ Please select at least one numeric column for percentile calculation.")

    # =========================================================
    # 💾 STEP 3: DOWNLOAD FULL UPDATED DATA
    # =========================================================
    st.markdown("---")
    st.markdown("## 💾 Step 3: Download Updated Dataset")

    csv_data = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Full Data (CSV)",
        data=csv_data,
        file_name="updated_data.csv",
        mime="text/csv"
    )

    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Processed_Data")
    st.download_button(
        label="⬇️ Download Full Data (Excel)",
        data=output.getvalue(),
        file_name="updated_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.info("👆 Please upload a CSV or Excel file to start.")
