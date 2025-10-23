import streamlit as st
import pandas as pd

st.set_page_config(page_title="Date-Time Splitter + Pivot", page_icon="⏰", layout="wide")

st.title("⏰ Date-Time Splitter & Pivot Table")
st.write("Upload a file, choose an Excel sheet if applicable, convert datetime columns, and create pivot tables dynamically.")

# --- File Upload ---
uploaded_file = st.file_uploader("📤 Upload CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file:
    # Detect file type
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        # Read Excel sheet names first
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

            # Create new columns
            df[col + "_Date"] = df[col + "_datetime"].dt.date
            df[col + "_Time"] = df[col + "_datetime"].dt.strftime("%H:%M")
            df[col + "_Hour_Slot"] = (
                df[col + "_datetime"].dt.hour.astype("Int64").astype(str).str.zfill(2)
                + ":00 - "
                + (df[col + "_datetime"].dt.hour + 1).astype("Int64").astype(str).str.zfill(2)
                + ":00"
            )

            # Cleanup
            df.drop(columns=[col + "_datetime"], inplace=True)
            if remove_original:
                df.drop(columns=[col], inplace=True)

        st.success("✅ Date-Time conversion complete!")
        st.dataframe(df.head(20))

        # Download converted data
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download Converted CSV",
            csv,
            file_name="converted_datetime_columns.csv",
            mime="text/csv",
        )

    # --- Pivot Table Section ---
    st.markdown("---")
    st.markdown("### 📊 Step 2: Create Pivot Table")

    with st.expander("🔧 Pivot Table Options", expanded=True):
        rows = st.multiselect("Rows:", df.columns)
        cols = st.multiselect("Columns:", df.columns)
        values = st.multiselect("Values:", df.select_dtypes(include=['number', 'float', 'int']).columns)
        aggfunc = st.selectbox("Aggregation Function:", ["sum", "count", "mean", "max", "min"])

    # --- Generate Pivot Table ---
    if rows and values:
        try:
            pivot = pd.pivot_table(
                df,
                index=rows,
                columns=cols if cols else None,
                values=values,
                aggfunc=aggfunc,
                fill_value=0,
            )

            st.success("✅ Pivot table generated successfully!")
            st.subheader("📈 Pivot Table Result")
            st.dataframe(pivot)

            # Download pivot result
            csv_pivot = pivot.to_csv().encode("utf-8")
            st.download_button(
                "📥 Download Pivot Table CSV",
                csv_pivot,
                file_name="pivot_table.csv",
                mime="text/csv",
            )

        except Exception as e:
            st.error(f"⚠️ Error creating pivot table: {e}")

    else:
        st.info("👉 Select at least **Rows** and **Values** to generate the Pivot Table.")
else:
    st.info("👆 Please upload a CSV or Excel file to begin.")
