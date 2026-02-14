import streamlit as st
import re

st.set_page_config(page_title="EV Variant HTML Converter", layout="wide")

st.title("🚗 EV Variant to HTML Code Converter")

raw_data = st.text_area("Paste Variant Data Here", height=300)

def extract_data(line):

    # --- FULL NAME (Everything before Rs. OR (Electric)) ---
    name = line

    if "Rs." in line:
        name = line.split("Rs.")[0]

    if "(Electric)" in name:
        name = name.replace("(Electric)", "")

    name = name.strip()

    # Fix kw formatting
    name = re.sub(r'(\d+\.?\d*)kw', r'\1kW', name, flags=re.IGNORECASE)

    # --- Extract Price ---
    price_match = re.search(r'Rs\.([\d\.]+)', line)
    price = price_match.group(1) if price_match else ""

    # --- Extract Battery ---
    battery_match = re.search(r'(\d+\.?\d*)\s*kWh', line)
    battery = battery_match.group(1) + " kWh" if battery_match else ""

    # --- Extract Range ---
    range_match = re.search(r'(\d+)\s*km', line)
    range_km = range_match.group(1) + " km" if range_match else ""

    return name, price, battery, range_km


if st.button("Generate HTML Code"):

    if not raw_data.strip():
        st.warning("Please paste some data.")
    else:
        lines = raw_data.strip().split("\n")

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

        html_output += "\n</div>"

        st.code(html_output, language="html")

        st.download_button(
            "Download HTML",
            html_output,
            "variants.html",
            "text/html"
        )
