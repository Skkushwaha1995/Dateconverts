import streamlit as st
import pandas as pd
from io import BytesIO
import numpy as np

st.set_page_config(page_title="⏱️ Hour & Percentile Calculator", page_icon="📊", layout="wide")

st.title("📊 Hour Difference + Auto Percentile + 30-Min Bucket Calculator")

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
    st.markdown("## ⏳ Step 1: Calculate Hour Differences & Percentiles")

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

    percentile_options = [90, 95]
    selected_percentiles = st.multiselect("Select Percentiles to Calculate:", percentile_options, default=[90, 95])
    group_col = st.selectbox("Select Grouping Column (Optional):", [None] + list(df.columns))

    # ✅ NEW: Ask if user wants automatic 30-min bucket creation
    auto_bucket = st.checkbox("🧮 Automatically convert calculated columns into 30-min interval buckets")

    # =========================================================
    # ⚙️ BUTTON TO CALCULATE HOURS
    # =========================================================
    if st.button("⚙️ Calculate Hours + Percentiles"):
        hr_columns = []

        for (start_col, end_col) in pairs:
            try:
                start_time = pd.to_datetime(df[start_col], errors="coerce")
                end_time = pd.to_datetime(df[end_col], errors="coerce")
                diff_hours = (end_time - start_time).dt.total_seconds() / 3600

                # Convert to hr.min (like 4.30 = 4h 30m)
                def convert_to_60min_format(x):
                    if pd.isna(x):
                        return None
                    hrs = int(x)
                    mins = round((x - hrs) * 60)
                    return round(hrs + mins / 100, 2)

                hr_col = f"{start_col}_to_{end_col}_Hr"
                df[hr_col] = diff_hours.apply(convert_to_60min_format)
                df[hr_col] = df[hr_col].round(2)
                hr_columns.append(hr_col)

            except Exception as e:
                st.error(f"⚠️ Error calculating {start_col} → {end_col}: {e}")

        # =========================================================
        # 🎯 STEP 2: PERCENTILE CALCULATION
        # =========================================================
        if hr_columns:
            for p in selected_percentiles:
                if group_col:
                    grouped = df.groupby(group_col)[hr_columns].quantile(p / 100).reset_index()
                    grouped[hr_columns] = grouped[hr_columns].round(2)
                    df = pd.merge(df, grouped, on=group_col, how="left", suffixes=("", f"_P{p}"))
                else:
                    for col in hr_columns:
                        percentile_val = round(df[col].quantile(p / 100), 2)
                        df[f"{col}_P{p}"] = percentile_val

            st.success(f"✅ Hour & {', '.join(map(str, selected_percentiles))}th Percentile calculated successfully!")

            # =========================================================
            # 🧮 AUTO BUCKET CREATION IF CHECKED
            # =========================================================
            if auto_bucket:
                for col in hr_columns:
                    try:
                        numeric_val = pd.to_numeric(df[col], errors="coerce")
                        numeric_val = numeric_val.dropna()

                        if len(numeric_val) == 0:
                            st.warning(f"⚠️ Column {col} has no numeric values.")
                            continue

                        min_val = np.floor(numeric_val.min())
                        max_val = np.ceil(numeric_val.max())
                        bins = np.arange(min_val, max_val + 0.5, 0.5)

                        labels = [f"{bins[i]:.1f}-{bins[i+1]:.1f} Hr" for i in range(len(bins) - 1)]
                        bucket_col = col.replace("_Hr", "_Bucket")
                        df[bucket_col] = pd.cut(pd.to_numeric(df[col], errors="coerce"),
                                                bins=bins, labels=labels, include_lowest=True)
                    except Exception as e:
                        st.error(f"⚠️ Error bucketing column {col}: {e}")

                st.success("✅ 30-Minute Interval Buckets created successfully!")

            # Update session + preview
            st.session_state.df = df
            st.dataframe(df.head(20))
        else:
            st.warning("⚠️ No valid hour columns found to calculate percentiles.")

    # =========================================================
    # 💾 STEP 3: DOWNLOAD FINAL DATA
    # =========================================================
    st.markdown("---")
    st.markdown("## 💾 Step 2: Download Final Updated Dataset")

    df = st.session_state.df
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
