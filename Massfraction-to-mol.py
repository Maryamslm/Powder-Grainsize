# app.py - Co-Cr Alloy Weight Fraction to Mole Fraction Converter
import streamlit as st
import pandas as pd
import numpy as np

# Page configuration
st.set_page_config(page_title="Co-Cr Alloy Converter", page_icon="⚗️", layout="wide")

# Constants: Atomic weights (g/mol)
ATOMIC_WEIGHTS = {
    'Co': 58.933,  # Cobalt [[1]]
    'Cr': 51.996   # Chromium [[49]]
}

def weight_to_mole_fraction(w_co, w_cr, atomic_weights):
    """
    Convert weight fractions to mole fractions for binary Co-Cr alloy.
    
    Parameters:
    -----------
    w_co : float
        Weight fraction of Cobalt (0-1 or 0-100)
    w_cr : float
        Weight fraction of Chromium (0-1 or 0-100)
    atomic_weights : dict
        Dictionary with atomic weights {'Co': ..., 'Cr': ...}
    
    Returns:
    --------
    dict : {'x_Co': mole_fraction_Co, 'x_Cr': mole_fraction_Cr}
    """
    # Normalize to 0-1 if input is in percent
    if w_co > 1 or w_cr > 1:
        w_co = w_co / 100
        w_cr = w_cr / 100
    
    # Calculate moles of each component
    n_co = w_co / atomic_weights['Co']
    n_cr = w_cr / atomic_weights['Cr']
    
    # Total moles
    n_total = n_co + n_cr
    
    # Mole fractions
    x_co = n_co / n_total
    x_cr = n_cr / n_total
    
    return {'x_Co': x_co, 'x_Cr': x_cr}

def mole_to_weight_fraction(x_co, x_cr, atomic_weights):
    """
    Convert mole fractions to weight fractions (reverse conversion).
    """
    # Calculate mass contribution of each component
    m_co = x_co * atomic_weights['Co']
    m_cr = x_cr * atomic_weights['Cr']
    
    # Total mass
    m_total = m_co + m_cr
    
    # Weight fractions
    w_co = m_co / m_total
    w_cr = m_cr / m_total
    
    return {'w_Co': w_co, 'w_Cr': w_cr}

# Streamlit UI
st.title("⚗️ Co-Cr Binary Alloy Composition Converter")
st.markdown("""
Convert between **weight fraction (wt%)** and **mole fraction (at%)** 
for Cobalt-Chromium alloys. Commonly used in metallurgy and biomaterials science [[20]].
""")

# Sidebar: Input mode selection
st.sidebar.header("⚙️ Settings")
conversion_mode = st.sidebar.radio(
    "Conversion Direction",
    ["Weight Fraction → Mole Fraction", "Mole Fraction → Weight Fraction"]
)

st.sidebar.info(f"""
**Atomic Weights Used:**
- Co: {ATOMIC_WEIGHTS['Co']} g/mol [[1]]
- Cr: {ATOMIC_WEIGHTS['Cr']} g/mol [[49]]
""")

# Main content
col1, col2 = st.columns(2)

with col1:
    st.subheader("📥 Input Composition")
    
    if conversion_mode == "Weight Fraction → Mole Fraction":
        # Weight fraction input
        w_co_input = st.slider("Cobalt (Co) weight fraction (%)", 0.0, 100.0, 60.0, 0.1)
        w_cr_input = 100.0 - w_co_input  # Ensure binary sum = 100%
        st.metric("Chromium (Cr) weight fraction (%)", f"{w_cr_input:.2f}")
        
        # Perform conversion
        result = weight_to_mole_fraction(w_co_input, w_cr_input, ATOMIC_WEIGHTS)
        
        st.subheader("📤 Output: Mole Fraction")
        st.metric("Cobalt (Co) mole fraction (at%)", f"{result['x_Co']*100:.3f} %")
        st.metric("Chromium (Cr) mole fraction (at%)", f"{result['x_Cr']*100:.3f} %")
        
    else:
        # Mole fraction input
        x_co_input = st.slider("Cobalt (Co) mole fraction (%)", 0.0, 100.0, 55.0, 0.1)
        x_cr_input = 100.0 - x_co_input
        st.metric("Chromium (Cr) mole fraction (%)", f"{x_cr_input:.2f}")
        
        # Perform reverse conversion
        result = mole_to_weight_fraction(x_co_input/100, x_cr_input/100, ATOMIC_WEIGHTS)
        
        st.subheader("📤 Output: Weight Fraction")
        st.metric("Cobalt (Co) weight fraction (wt%)", f"{result['w_Co']*100:.3f} %")
        st.metric("Chromium (Cr) weight fraction (wt%)", f"{result['w_Cr']*100:.3f} %")

with col2:
    st.subheader("📊 Composition Summary")
    
    if conversion_mode == "Weight Fraction → Mole Fraction":
        data = pd.DataFrame({
            'Element': ['Co', 'Cr'],
            'Atomic Weight (g/mol)': [ATOMIC_WEIGHTS['Co'], ATOMIC_WEIGHTS['Cr']],
            'Weight Fraction (%)': [w_co_input, w_cr_input],
            'Mole Fraction (%)': [result['x_Co']*100, result['x_Cr']*100]
        })
    else:
        data = pd.DataFrame({
            'Element': ['Co', 'Cr'],
            'Atomic Weight (g/mol)': [ATOMIC_WEIGHTS['Co'], ATOMIC_WEIGHTS['Cr']],
            'Mole Fraction (%)': [x_co_input, x_cr_input],
            'Weight Fraction (%)': [result['w_Co']*100, result['w_Cr']*100]
        })
    
    st.dataframe(data.style.format("{:.3f}", subset=['Weight Fraction (%)', 'Mole Fraction (%)']), use_container_width=True)
    
    # Visualization
    st.subheader("🥧 Visual Comparison")
    chart_data = pd.DataFrame({
        'Element': ['Co', 'Cr'],
        'Weight %': [data['Weight Fraction (%)'].iloc[0], data['Weight Fraction (%)'].iloc[1]],
        'Mole %': [data['Mole Fraction (%)'].iloc[0], data['Mole Fraction (%)'].iloc[1]]
    })
    st.bar_chart(chart_data.set_index('Element'))

# Additional info section
with st.expander("📚 Formula Reference & Notes"):
    st.markdown("""
    ### Conversion Formula [[30]][[18]]
    For binary alloy with components A and B:
    
    **Weight → Mole:**
    ```
    x_A = (w_A/M_A) / [(w_A/M_A) + (w_B/M_B)]
    x_B = 1 - x_A
    ```
    
    **Mole → Weight:**
    ```
    w_A = (x_A·M_A) / [(x_A·M_A) + (x_B·M_B)]
    w_B = 1 - w_A
    ```
    
    ### Notes:
    - Weight fractions must sum to 1 (or 100%)
    - Mole fractions are equivalent to atomic percent (at%) in alloys
    - Co-Cr alloys are widely used in biomedical implants and high-temperature applications [[25]]
    - Phase behavior depends on composition; see Co-Cr phase diagrams for context [[20]]
    """)

# Footer
st.markdown("---")
st.caption("""
*Co-Cr Alloy Converter | Based on IUPAC conventions for mole fraction [[18]] | 
Atomic weights from NIST/CODATA values [[1]][[49]]*
""")
