import streamlit as st
import re

st.set_page_config(page_title="EV Variant HTML Converter", layout="wide")
st.title("🚗 EV Variant to HTML Code Converter")

raw_data = st.text_area("Paste Variant Data Here", height=300, 
                        placeholder="Example:\nMahindra XEV 9e Pack One (Electric)Rs.21.90 Lakh*, 59 kWh, 542 km, 228 bhp")

def extract_data(line):
    # --- FULL NAME (Everything before Rs.) ---
    name = ""
    if "Rs." in line:
        name = line.split("Rs.")[0].strip()
    else:
        name = line.strip()
    
    # Keep (Electric) in the name
    # Fix kw formatting to kW
    name = re.sub(r'(\d+\.?\d*)\s*kw\s+', r'\1kW ', name, flags=re.IGNORECASE)
    
    # --- Extract Price (handle Rs.21.90 Lakh* format) ---
    price_match = re.search(r'Rs\.?\s*([\d\.]+)\s*Lakh', line, re.IGNORECASE)
    price = price_match.group(1) if price_match else ""
    
    # --- Extract Battery (handle "59 kWh" format) ---
    battery_match = re.search(r'(\d+\.?\d*)\s*kWh', line, re.IGNORECASE)
    battery = battery_match.group(1) + " kWh" if battery_match else ""
    
    # --- Extract Range (handle "542 km" format) ---
    range_match = re.search(r'(\d+)\s*km', line, re.IGNORECASE)
    range_km = range_match.group(1) + " km" if range_match else ""
    
    return name, price, battery, range_km

if st.button("Generate HTML Code"):
    if not raw_data.strip():
        st.warning("Please paste some data.")
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
        st.code(html_output, language="html")
        
        st.download_button(
            "📥 Download HTML",
            html_output,
            "variants.html",
            "text/html"
        )
```

**Key Fixes:**

1. **Price extraction** - Fixed regex to handle `Rs.21.90 Lakh*` format (with or without space)
2. **Battery extraction** - Changed to case-insensitive search for `kWh`
3. **Name extraction** - Now keeps `(Electric)` in the full name as requested
4. **kW formatting** - Fixed the regex to properly convert `7.2kw` to `7.2kW`
5. **Variant count** - Now automatically counts and displays the number of variants
6. **Better formatting** - Added proper spacing in the HTML output

**Test it with your data:**
```
Mahindra XEV 9e Pack One (Electric)Rs.21.90 Lakh*, 59 kWh, 542 km, 228 bhp
Mahindra XEV 9e Pack One 7.2kw Charger (Electric)Rs.22.40 Lakh*, 59 kWh, 542 km, 228 bhp
Mahindra XEV 9e Pack One 11.2kw Charger (Electric)Rs.22.65 Lakh*, 59 kWh, 542 km, 228 bhp
Mahindra XEV 9e Pack Three Select (Electric)Rs.24.90 Lakh*, 59 kWh, 542 km
