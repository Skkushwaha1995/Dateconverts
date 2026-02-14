import streamlit as st
import re

st.set_page_config(page_title="EV Variant HTML Converter", layout="wide")

st.title("🚗 EV Variant to HTML Code Converter")
st.markdown("Paste raw EV variant data below and generate ready-to-use HTML code.")

# -------------------------
# TEXT INPUT
# -------------------------
raw_data = st.text_area("Paste Variant Data Here", height=300)

# -------------------------
# DATA EXTRACTION FUNCTION
# -------------------------
def extract_data(line):
    # Extract price
    price_match = re.search(r'Rs\.([\d\.]+)', line)
    price = price_match.group(1) if price_match else ""

    # Extract battery
    battery_match = re.search(r'(\d+\.?\d*)\s?kWh', line)
    battery = battery_match.group(1) + " kWh" if battery_match else ""

    # Extract range
    range_match = re.search(r'(\d+)\s?km', line)
    range_km = range_match.group(1) + " km" if range_match else ""

    # Extract full variant name (before "(Electric)")
    name = line.split("(Electric)")[0].strip()

    return name, price, battery, range_km

# -------------------------
# BUTTON ACTION
# -------------------------
if st.button("Generate HTML Code"):

    if raw_data.strip() == "":
        st.warning("Please paste variant data first.")
    else:
        lines = raw_data.strip().split("\n")
        variant_count = 0

        html_output = """
<div class="variant-toggle">
  <span class="variant-count-text"></span>
  <span class="arrow">▼</span>
</div>

<div class="variant-content">
"""

        for line in lines:
            if line.strip():
                name, price, battery, range_km = extract_data(line)

                html_output += f"""
  <div class="variant-item">
    <span>{name}</span>
    <span>₹{price} Lakh | {battery} | {range_km}</span>
  </div>
"""
                variant_count += 1

        html_output += "\n</div>"

        # Show Variant Count
        st.success(f"✅ {variant_count} Variants Generated Successfully")

        # Show HTML
        st.subheader("Generated HTML Code:")
        st.code(html_output, language="html")

        # Download Button
        st.download_button(
            label="📥 Download HTML File",
            data=html_output,
            file_name="variants.html",
            mime="text/html"
        )
