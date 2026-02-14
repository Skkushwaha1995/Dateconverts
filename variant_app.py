import streamlit as st
import re

st.set_page_config(page_title="EV Variant HTML Converter", layout="wide")

st.title("🚗 EV Variant HTML Generator")

raw_data = st.text_area("Paste Variant Data Here", height=300)


def extract_data(line):

    # 1️⃣ Extract full name BEFORE (Electric)
    name_match = re.search(r'^(.*?)\s*\(Electric\)', line)
    name = name_match.group(1).strip() if name_match else ""

    # Fix kw formatting
    name = re.sub(r'(\d+\.?\d*)kw', r'\1kW', name, flags=re.IGNORECASE)

    # 2️⃣ Extract price
    price_match = re.search(r'Rs\.([\d\.]+)', line)
    price = price_match.group(1) if price_match else ""

    # 3️⃣ Extract battery
    battery_match = re.search(r'(\d+\.?\d*)\s*kWh', line)
    battery = battery_match.group(1) + " kWh" if battery_match else ""

    # 4️⃣ Extract range
    range_match = re.search(r'(\d+)\s*km', line)
    range_km = range_match.group(1) + " km" if range_match else ""

    return name, price, battery, range_km


if st.button("Generate HTML"):

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

    st.download_button("Download HTML", html, "variants.html", "text/html")
