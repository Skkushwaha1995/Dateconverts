import streamlit as st
import re

st.set_page_config(page_title="EV Variant HTML Converter", layout="wide")

st.title("🚗 EV Variant to HTML Converter")
st.markdown("Paste raw EV variant data and generate HTML instantly.")

raw_data = st.text_area("Paste Variant Data Below", height=300)

def extract_data(line):
    price = re.search(r'Rs\.([\d\.]+)', line)
    battery = re.search(r'(\d+\.?\d*)\s?kWh', line)
    range_km = re.search(r'(\d+)\s?km', line)

    price = price.group(1) if price else ""
    battery = battery.group(1) + " kWh" if battery else ""
    range_km = range_km.group(1) + " km" if range_km else ""

    # Clean name
    name = line.split("(Electric)")[0]
    name = re.sub(r"Mahindra\s+[A-Za-z0-9\s]+", "", name).strip()

    return name, price, battery, range_km

if st.button("Generate HTML Code"):

    lines = raw_data.strip().split("\n")

    html = """
<div class="variant-toggle">
  <span class="variant-count-text"></span>
  <span class="arrow">▼</span>
</div>

<div class="variant-content">
"""

    for line in lines:
        if line.strip():
            name, price, battery, range_km = extract_data(line)

            html += f"""
  <div class="variant-item">
    <span>{name}</span>
    <span>₹{price} Lakh | {battery} | {range_km}</span>
  </div>
"""

    html += "\n</div>"

    st.code(html, language="html")

    st.download_button(
        label="Download HTML File",
        data=html,
        file_name="variants.html",
        mime="text/html"
    )
