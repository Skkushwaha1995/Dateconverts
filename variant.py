import streamlit as st
import re

st.set_page_config(page_title="EV Variant HTML Converter", layout="wide")
st.title("🚗 EV Variant to HTML Code Converter")

# Show example format
with st.expander("📋 See Example Format"):
    st.code("""Mahindra XEV 9e Pack One (Electric)Rs.21.90 Lakh*, 59 kWh, 542 km, 228 bhp
Mahindra XEV 9e Pack One 7.2kw Charger (Electric)Rs.22.40 Lakh*, 59 kWh, 542 km, 228 bhp
Mahindra XEV 9e Pack One 11.2kw Charger (Electric)Rs.22.65 Lakh*, 59 kWh, 542 km, 228 bhp
Mahindra XEV 9e Pack Three Select (Electric)Rs.24.90 Lakh*, 59 kWh, 542 km""")

raw_data = st.text_area("Paste Variant Data Here", height=300, 
                        placeholder="Paste your variant data here...")

def extract_data(line):
    """Extract variant name, price, battery, and range from a line of text"""
    
    # Debug: Show what we're parsing
    # st.write(f"DEBUG - Parsing line: {line[:50]}...")
    
    name = ""
    price = ""
    battery = ""
    range_km = ""
    
    # Try multiple patterns to extract the name
    
    # Pattern 1: Name before Rs. or Lakh
    if "Rs." in line or "Lakh" in line:
        # Split by Rs. first
        if "Rs." in line:
            name = line.split("Rs.")[0].strip()
        else:
            # Sometimes it's just "21.90 Lakh" without Rs.
            parts = re.split(r'\d+\.?\d*\s*Lakh', line, maxsplit=1, flags=re.IGNORECASE)
            if len(parts) > 0:
                name = parts[0].strip()
    else:
        # No price found, use the whole line as name
        name = line.strip()
    
    # Clean up the name
    # Remove trailing commas, asterisks, etc.
    name = name.rstrip(',*').strip()
    
    # Fix kw to kW formatting
    name = re.sub(r'(\d+\.?\d*)\s*kw\s+', r'\1kW ', name, flags=re.IGNORECASE)
    name = re.sub(r'(\d+\.?\d*)\s*kw\b', r'\1kW', name, flags=re.IGNORECASE)
    
    # --- Extract Price ---
    price_match = re.search(r'Rs\.?\s*([\d\.]+)\s*Lakh', line, re.IGNORECASE)
    if not price_match:
        # Try without Rs.
        price_match = re.search(r'([\d\.]+)\s*Lakh', line, re.IGNORECASE)
    price = price_match.group(1) if price_match else ""
    
    # --- Extract Battery ---
    battery_match = re.search(r'(\d+\.?\d*)\s*kWh', line, re.IGNORECASE)
    battery = battery_match.group(1) + " kWh" if battery_match else ""
    
    # --- Extract Range ---
    range_match = re.search(r'(\d+)\s*km', line, re.IGNORECASE)
    range_km = range_match.group(1) + " km" if range_match else ""
    
    return name, price, battery, range_km

# Add a debug checkbox
show_debug = st.checkbox("Show debugging information")

if st.button("🔄 Generate HTML Code"):
    if not raw_data.strip():
        st.warning("⚠️ Please paste some data.")
    else:
        lines = [line.strip() for line in raw_data.strip().split("\n") if line.strip()]
        
        if show_debug:
            st.subheader("🔍 Debug Information")
            st.write(f"Total lines found: {len(lines)}")
            st.write("---")
        
        variant_count = len(lines)
        
        # Preview extracted data
        st.subheader("📋 Preview of Extracted Data:")
        
        all_data = []
        for i, line in enumerate(lines, 1):
            name, price, battery, range_km = extract_data(line)
            all_data.append((name, price, battery, range_km))
            
            if show_debug:
                st.write(f"**Line {i}:**")
                st.code(line)
                st.write(f"- Name: `{name}`")
                st.write(f"- Price: `{price}`")
                st.write(f"- Battery: `{battery}`")
                st.write(f"- Range: `{range_km}`")
                st.write("---")
            else:
                if name:  # Only show if name was extracted
                    st.write(f"{i}. **{name}** → ₹{price} Lakh | {battery} | {range_km}")
                else:
                    st.error(f"⚠️ Line {i}: Could not extract variant name!")
                    st.code(line)
        
        # Check if any names were extracted
        if not any(item[0] for item in all_data):
            st.error("❌ No variant names were extracted! Please check your data format.")
            st.info("Make sure your data looks like: `Variant Name Rs.21.90 Lakh, 59 kWh, 542 km`")
        else:
            # Generate HTML
            html_output = f"""<div class="variant-toggle">
  <span class="variant-count-text">{variant_count} Variants Available</span>
  <span class="arrow">▼</span>
</div>

<div class="variant-content">
"""
            
            for name, price, battery, range_km in all_data:
                html_output += f"""  <div class="variant-item">
    <span>{name}</span>
    <span>₹{price} Lakh | {battery} | {range_km}</span>
  </div>

"""
            
            html_output += "</div>"
            
            st.success(f"✅ Generated HTML for {variant_count} variants")
            
            st.subheader("📄 HTML Code:")
            st.code(html_output, language="html")
            
            st.download_button(
                "📥 Download HTML",
                html_output,
                "variants.html",
                "text/html"
            )
