import streamlit as st
import re

st.set_page_config(page_title="EV Variant HTML Converter", layout="wide")

st.title("🚗 EV Variant to HTML Code Converter")
st.markdown("Paste raw EV variant data and generate clean HTML.")

raw_data = st.text_area("Paste Variant Data Here", height=300)

def extract_data(line):
    # Extract full name before (Electric)
    name_match = re.search(r'^(.*?)\s*\(Electric\)', line)
    name = name_match.group(1).strip() if name_match else ""

    # Fix charger formatting (7.2kw → 7.2kW)
    name = re.sub(r'(\d+\.?\d*)kw', r'\1kW', name, flags=re.IGNORECASE)

    # Extract price
    price_match = re.search(r'Rs\.([\d\.]+)', line)
    price = price_match.group(1) if price_match else ""

    # Extract battery
    battery_match = re.search(r'(\d+\.?\d*)\s*kWh', line)
    battery = battery_match.group(1) + " kWh" if battery_match else ""

    # Extract range
    range_match = re.search(r'(\d+)\s*km', line)
    range_km = range_match.group(1) + " km" if range_match else ""

    return name, price, battery, range_km


if st.button("Generate HTML Code"):

    if not raw_data.strip():
        st.warning("Please paste data first.")
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

        st.success(f"✅ {variant_count} Variants Generated")
        st.code(html_output, language="html")

        st.download_button(
            "📥 Download HTML File",
            html_output,
            "variants.html",
            "text/html"
        )
