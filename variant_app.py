import streamlit as st
import re

st.set_page_config(page_title="EV Variant HTML Converter", layout="wide")
st.title("🚗 EV Variant to HTML Code Converter")

raw_data = st.text_area("Paste Variant Data Here", height=300, 
                        placeholder="Example:\nMahindra XEV 9e Pack One (Electric)Rs.21.90 Lakh*, 59 kWh, 542 km, 228 bhp")

def extract_data(line):
    # --- FULL NAME (Everything before the price) ---
    # Split by "Rs." to separate name from details
    if "Rs." in line:
        parts = line.split("Rs.")
        name = parts[0].strip()
        details = "Rs." + parts[1]
    else:
        name = line.strip()
        details = line
    
    # Fix kw to kW in name
    name = re.sub(r'(\d+\.?\d*)\s*kw\s+', r'\1kW ', name, flags=re.IGNORECASE)
    
    # --- Extract Price ---
    # Match patterns like "21.90 Lakh*" or "21.90 Lakh"
    price_match = re.search(r'Rs\.?\s*([\d\.]+)\s*Lakh', details, re.IGNORECASE)
    price = price_match.group(1) if price_match else ""
    
    # --- Extract Battery ---
    # Match patterns like "59 kWh"
    battery_match = re.search(r'(\d+\.?\d*)\s*kWh', details, re.IGNORECASE)
    battery = battery_match.group(1) + " kWh" if battery_match else ""
    
    # --- Extract Range ---
    # Match patterns like "542 km"
    range_match = re.search(r'(\d+)\s*km', details, re.IGNORECASE)
    range_km = range_match.group(1) + " km" if range_match else ""
    
    return name, price, battery, range_km

if st.button("🔄 Generate HTML Code"):
    if not raw_data.strip():
        st.warning("⚠️ Please paste some data.")
    else:
        lines = [line.strip() for line in raw_data.strip().split("\n") if line.strip()]
        
        variant_count = len(lines)
        
        html_output = f"""<div class="variant-toggle">
  <span class="variant-count-text">{variant_count} Variants Available</span>
  <span class="arrow">▼</span>
</div>

<div class="variant-content">
"""
        
        for line in lines:
            name, price, battery, range_km = extract_data(line)
            html_output += f"""  <div class="variant-item">
    <span>{name}</span>
    <span>₹{price} Lakh | {battery} | {range_km}</span>
  </div>

"""
        
        html_output += "</div>"
        
        st.success(f"✅ Generated HTML for {variant_count} variants")
        
        # Show preview of extracted data
        st.subheader("Preview:")
        for i, line in enumerate(lines, 1):
            name, price, battery, range_km = extract_data(line)
            st.write(f"{i}. **{name}** - ₹{price} Lakh | {battery} | {range_km}")
        
        st.subheader("HTML Code:")
        st.code(html_output, language="html")
        
        st.download_button(
            "📥 Download HTML",
            html_output,
            "variants.html",
            "text/html"
        )
