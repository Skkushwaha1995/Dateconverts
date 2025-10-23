import streamlit as st
import pandas as pd

st.set_page_config(page_title="Date-Time Splitter", page_icon="⏰", layout="centered")
st.title("⏰ Convert Date-Time Columns")
st.write("Upload a CSV/XLSX and choose columns to split into Date, Time, and Hour Slot.")

uploaded_file = st.file_uploader("📤 Upload CSV or Excel file", type=["csv", "xlsx"])
if not uploaded_file:
    st.info("👆 Upload a CSV or Excel file to begin.")
    st.stop()

# Read file
if uploaded_file.name.endswith(".csv"):
    df = pd.read_csv(uploaded_file)
else:
    df = pd.read_excel(uploaded_file)

st.subheader("Preview (first 10 rows)")
st.dataframe(df.head(10))

# Choose columns to convert (multi-select)
selected_cols = st.multiselect(
    "🧩 Select one or more columns to convert to Date/Time/Hour slot:",
    options=list(df.columns)
)

# Option: remove original columns after conversion
remove_original = st.checkbox("Delete original columns after conversion", value=False)

if selected_cols:
    for col in selected_cols:
        # parse to datetime (coerce errors to NaT)
        new_dt_col = col + "_datetime_parsed"
        df[new_dt_col] = pd.to_datetime(df[col], errors='coerce')

        # create Date, Time, Hour slot
        df[col + "_Date"] = df[new_dt_col].dt.date
        df[col + "_Time"] = df[new_dt_col].dt.strftime("%H:%M")
        df[col + "_Hour_Slot"] = (
            df[new_dt_col].dt.hour.astype("Int64").astype(str).str.zfill(2)
            + ":00 - "
            + (df[new_dt_col].dt.hour + 1).astype("Int64").astype(str).str.zfill(2)
            + ":00"
        )

        # optional: drop the helper parsed column
        df.drop(columns=[new_dt_col], inplace=True)

        if remove_original:
            df.drop(columns=[col], inplace=True)

    st.success("✅ Conversion completed")
    st.subheader("Converted Data (first 20 rows)")
    st.dataframe(df.head(20))

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download converted CSV", csv, file_name="converted_datetime_columns.csv", mime="text/csv")
else:
    st.info("👉 Please select at least one column to convert.")
