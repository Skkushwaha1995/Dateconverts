import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Date-Time Splitter + Pivot + Column Selector", page_icon="📊", layout="wide")

st.title("📊 Date-Time Splitter, Pivot & Custom Column Export")
st.write("Upload a file, select sheet (if Excel), process date-time columns, create a pivot table, and download only the columns you want.")

# --- File Upload ---
uploaded_file = st.file_uploader("📤 Upload CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file:
    # Detect file type
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        # Excel — show sheet selection
        xls = pd.ExcelFile(uploaded_file)
        sheet_name = st.selectbox("📑 Select a sheet to process:", xls.sheet_names)
        df = pd.read_excel(xls, sheet_name=sheet_name)

    st.subheader("📋 Uploaded Data Preview")
    st.dataframe(df.head())

    # --- DateTime Conversion Section ---
    st.markdown("### 🔄 Step 1: Convert Date-Time Columns")
    selected_cols = st.multiselect(
        "Select datetime columns to split into Date / Time / Hour Slot:",
        options=list(df.columns)
    )

    remove_original = st.checkbox("🗑️ Delete original datetime columns after conversion", value=False)

    if selected_cols:
        for col in selected_cols:
            df[col + "_datetime"] = pd.to_datetime(df[col], errors="coerce")

            df[col + "_Date"] = df[col + "_datetime"].dt.date
            df[col + "_Time"] = df[col + "_datetime"].dt.strftime("%H:%M")
            df[col + "_Hour_Slot"] = (
                df[col + "_datetime"].dt.hour.astype("Int64").astype(str).str.zfill(2)
                + ":00 - "
                + (df[col + "_datetime"].dt.hour + 1).astype("Int64").astype(str).str.zfill(2)
                + ":00"
            )

            df.drop(columns=[col + "_datetime"], inplace=True)
            if remove_original:
                df.drop(columns=[col], inplace=True)

        st.success("✅ Date-Time conversion complete!")
        st.dataframe(df.head(20))

    # --- Time Difference (Hour Calculation) Section ---
    st.markdown("---")
    st.markdown("### ⏱️ Step 1.5: Calculate Time Difference Between Two Columns (in Hours - 60 min format)")

    time_cols = [col for col in df.columns if 'time' in col.lower() or 'date' in col.lower()]
    col1 = st.selectbox("Select Start Time Column:", options=time_cols)
    col2 = st.selectbox("Select End Time Column:", options=time_cols)

    if col1 and col2:
        if st.button("⚡ Calculate Hour Difference"):
            try:
                df[col1] = pd.to_datetime(df[col1], errors="coerce")
                df[col2] = pd.to_datetime(df[col2], errors="coerce")

                # Calculate total seconds difference
                diff_seconds = (df[col2] - df[col1]).dt.total_seconds()

                # Convert to hours and minutes (3.09 format instead of 3.75)
                df["Hour_Diff_60min_Format"] = (
                    (diff_seconds // 3600) + ((diff_seconds % 3600) / 60) / 100
                ).round(2)

                st.success(f"✅ Hour difference calculated between '{col1}' and '{col2}' in 60-min format!")
                st.dataframe(df[[col1, col2, "Hour_Diff_60min_Format"]].head(20))

            except Exception as e:
                st.error(f"⚠️ Error calculating time difference: {e}")

    # --- Pivot Table Section ---
    st.markdown("---")
    st.markdown("### 📈 Step 2: Create Pivot Table")

    with st.expander("⚙️ Pivot Table Options", expanded=True):
        rows = st.multiselect("Rows:", df.columns)
        cols = st.multiselect("Columns:", df.columns)
        values = st.multiselect("Values:", df.select_dtypes(include=['number', 'float', 'int']).columns)
        aggfunc = st.selectbox("Aggregation Function:", ["sum", "count", "mean", "max", "min"])

    final_df = df  # Default (if pivot not used)

    if rows and values:
        try:
            pivot = pd.pivot_table(
                df,
                index=rows,
                columns=cols if cols else None,
                values=values,
                aggfunc=aggfunc,
                fill_value=0,
            ).reset_index()

            st.success("✅ Pivot table generated successfully!")
            st.subheader("📊 Pivot Table Result")
            st.dataframe(pivot)
            final_df = pivot  # Update for export

        except Exception as e:
            st.error(f"⚠️ Error creating pivot table: {e}")
    else:
        st.info("👉 Select at least **Rows** and **Values** to generate the Pivot Table (or skip this step).")

    # --- Column Selection for Download ---
    st.markdown("---")
    st.markdown("### 📥 Step 3: Select Columns for Download")

    selected_export_cols = st.multiselect(
        "Choose columns to include in final file:",
        options=list(final_df.columns),
        default=list(final_df.columns)  # All selected by default
    )

    if selected_export_cols:
        export_df = final_df[selected_export_cols]

        # --- CSV Download ---
        csv_data = export_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download Selected Columns as CSV",
            data=csv_data,
            file_name="selected_columns.csv",
            mime="text/csv",
        )

        # --- Excel Download ---
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            export_df.to_excel(writer, index=False, sheet_name="Processed_Data")
        st.download_button(
            label="⬇️ Download Selected Columns as Excel",
            data=output.getvalue(),
            file_name="selected_columns.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

else:
    st.info("👆 Please upload a CSV or Excel file to begin.")
