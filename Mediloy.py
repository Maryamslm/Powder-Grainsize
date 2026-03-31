import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import streamlit as st
from scipy import stats
from io import BytesIO
import pandas as pd

# Page configuration
st.set_page_config(page_title="SLM Powder PSD Analyzer", layout="wide")

# Sidebar for user inputs
st.sidebar.title("⚙️ Distribution Settings")

# Distribution type selection
distribution_type = st.sidebar.selectbox(
    "Select Distribution Type",
    ["Log-Normal", "Normal (Gaussian)", "Rosin-Rammler", "Weibull", "Bimodal"],
    index=0
)

# Common SLM powder materials
material = st.sidebar.selectbox(
    "Material",
    ["Mediloy S-Co", "Ti-6Al-4V", "Inconel 718", "AlSi10Mg", "316L Stainless Steel", "Custom"],
    index=0
)

# Distribution parameters based on type
st.sidebar.subheader("Distribution Parameters")

if distribution_type == "Log-Normal":
    mu = st.sidebar.slider("μ (log median)", 2.5, 4.0, 3.2, 0.1)
    sigma = st.sidebar.slider("σ (distribution width)", 0.2, 0.8, 0.4, 0.05)
    particle_sizes = np.random.lognormal(mu, sigma, 10000)
    
elif distribution_type == "Normal (Gaussian)":
    mean = st.sidebar.slider("Mean (μm)", 15.0, 50.0, 25.0, 1.0)
    std = st.sidebar.slider("Std Dev (μm)", 2.0, 15.0, 8.0, 0.5)
    particle_sizes = np.random.normal(mean, std, 10000)
    
elif distribution_type == "Rosin-Rammler":
    d_mean = st.sidebar.slider("Mean Diameter (μm)", 15.0, 50.0, 25.0, 1.0)
    n_shape = st.sidebar.slider("Shape Parameter (n)", 1.0, 5.0, 2.5, 0.1)
    u = np.random.uniform(0, 1, 10000)
    particle_sizes = d_mean * (-np.log(1 - u))**(1/n_shape)
    
elif distribution_type == "Weibull":
    scale = st.sidebar.slider("Scale Parameter (μm)", 15.0, 50.0, 25.0, 1.0)
    shape = st.sidebar.slider("Shape Parameter", 1.0, 5.0, 2.5, 0.1)
    particle_sizes = np.random.weibull(shape, 10000) * scale
    
elif distribution_type == "Bimodal":
    mean1 = st.sidebar.slider("Mean 1 (μm)", 10.0, 30.0, 15.0, 1.0)
    std1 = st.sidebar.slider("Std Dev 1 (μm)", 2.0, 10.0, 4.0, 0.5)  # ✅ Fixed
    mean2 = st.sidebar.slider("Mean 2 (μm)", 30.0, 60.0, 45.0, 1.0)
    std2 = st.sidebar.slider("Std Dev 2 (μm)", 2.0, 10.0, 6.0, 0.5)  # ✅ Fixed
    ratio = st.sidebar.slider("Ratio (Fine:Coarse)", 0.3, 0.7, 0.5, 0.05)
    
    n1 = int(10000 * ratio)
    n2 = 10000 - n1
    particle_sizes1 = np.random.normal(mean1, std1, n1)
    particle_sizes2 = np.random.normal(mean2, std2, n2)
    particle_sizes = np.concatenate([particle_sizes1, particle_sizes2])

# Filter to realistic SLM powder range (1-100 μm)
particle_sizes = particle_sizes[(particle_sizes >= 1) & (particle_sizes <= 100)]

# Calculate statistics
D10 = np.percentile(particle_sizes, 10)
D50 = np.percentile(particle_sizes, 50)
D90 = np.percentile(particle_sizes, 90)
mean_size = np.mean(particle_sizes)
std_size = np.std(particle_sizes)
span = (D90 - D10) / D50 if D50 > 0 else 0

# Material-specific typical ranges
material_ranges = {
    "Mediloy S-Co": "10-45 μm",
    "Ti-6Al-4V": "15-45 μm",
    "Inconel 718": "15-53 μm",
    "AlSi10Mg": "20-63 μm",
    "316L Stainless Steel": "15-45 μm",
    "Custom": "1-100 μm"
}

# Main display
st.title("🔬 SLM Powder Particle Size Distribution Analyzer")
st.markdown(f"**Material:** {material} | **Typical Range:** {material_ranges[material]}")
st.markdown(f"**Distribution:** {distribution_type}")

# Create figure
fig = plt.figure(figsize=(8, 6), dpi=150)
gs = gridspec.GridSpec(1, 1)
ax = fig.add_subplot(gs[0, 0])

# Set professional style
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.linewidth'] = 1.5
plt.rcParams['xtick.direction'] = 'in'
plt.rcParams['ytick.direction'] = 'in'

# Create histogram bins (logarithmic scale)
bins = np.logspace(np.log10(1), np.log10(100), 50)

# Calculate histogram
counts, bin_edges = np.histogram(particle_sizes, bins=bins, density=True)

# Calculate cumulative distribution
cumulative = np.cumsum(counts)
cumulative = (cumulative / cumulative[-1]) * 100

# Frequency distribution percentage
freq_dist = counts * 100

# Calculate bin centers for plotting
bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

# Plot frequency distribution as bars
bar_width = bin_edges[1:] - bin_edges[:-1]
ax.bar(bin_edges[:-1], freq_dist, width=bar_width, bottom=0, 
       align='edge', color='#DC143C', edgecolor='none', alpha=0.8, label='Frequency Distribution')

# Create secondary y-axis for cumulative distribution
ax2 = ax.twinx()

# Plot cumulative distribution curve
ax2.plot(bin_centers, cumulative, color='#228B22', linewidth=2.5, label='Cumulative PSD')

# Set axis limits
ax.set_xlim(1, 100)
ax.set_ylim(0, max(freq_dist) * 1.2 if len(freq_dist) > 0 else 10)
ax2.set_ylim(0, 105)

# Set logarithmic x-axis
ax.set_xscale('log')

# Set labels
ax.set_xlabel('Particle Diameter [μm]', fontsize=11, fontweight='bold', labelpad=10)
ax.set_ylabel('Frequency [%]', fontsize=11, fontweight='bold', color='#DC143C', labelpad=10)
ax2.set_ylabel('Cumulative [%]', fontsize=11, fontweight='bold', color='#228B22', labelpad=10)

# Set tick parameters
ax.tick_params(axis='both', which='major', labelsize=10, width=1.5, length=6)
ax2.tick_params(axis='both', which='major', labelsize=10, width=1.5, length=6, 
                labelcolor='#228B22')
ax.tick_params(axis='y', which='major', labelcolor='#DC143C')

# Set x-axis ticks
ax.set_xticks([1, 10, 100])
ax.set_xticklabels(['1', '10', '100'])

# Add D10, D50, D90 text box
textstr = f'D₉₀ = {D90:.2f} μm\nD₅₀ = {D50:.2f} μm\nD₁₀ = {D10:.2f} μm\nSpan = {span:.2f}'
props = dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='gray', linewidth=1)
ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=10, 
        verticalalignment='top', fontweight='bold', bbox=props)

# Add vertical lines for D10, D50, D90
ax.axvline(x=D10, color='gray', linestyle='--', linewidth=1, alpha=0.7)
ax.axvline(x=D50, color='gray', linestyle='--', linewidth=1, alpha=0.7)
ax.axvline(x=D90, color='gray', linestyle='--', linewidth=1, alpha=0.7)

# Add legend
ax.legend(loc='upper right', fontsize=9)
ax2.legend(loc='lower right', fontsize=9)

# Tight layout
plt.tight_layout()

# Display plot in Streamlit
st.pyplot(fig)

# Statistics display in columns
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("📊 Key Percentiles")
    st.metric("D₁₀ (10th percentile)", f"{D10:.2f} μm")
    st.metric("D₅₀ (Median)", f"{D50:.2f} μm")
    st.metric("D₉₀ (90th percentile)", f"{D90:.2f} μm")

with col2:
    st.subheader("📈 Distribution Stats")
    st.metric("Mean Size", f"{mean_size:.2f} μm")
    st.metric("Std Deviation", f"{std_size:.2f} μm")
    st.metric("Span (D90-D10)/D50", f"{span:.2f}")

with col3:
    st.subheader("✅ Quality Check")
    span_ok = span < 1.5
    range_ok = D10 >= 1 and D90 <= 100
    st.metric("Span < 1.5", "✅ Pass" if span_ok else "⚠️ Review")
    st.metric("Range Valid", "✅ Pass" if range_ok else "⚠️ Review")
    st.metric("Sample Size", f"{len(particle_sizes):,}")

# Additional analysis
st.subheader("📋 Detailed Statistics")
st.write(f"""
| Parameter | Value |
|-----------|-------|
| **Distribution Type** | {distribution_type} |
| **Material** | {material} |
| **D₁₀** | {D10:.2f} μm |
| **D₅₀** | {D50:.2f} μm |
| **D₉₀** | {D90:.2f} μm |
| **Mean** | {mean_size:.2f} μm |
| **Standard Deviation** | {std_size:.2f} μm |
| **Span** | {span:.2f} |
| **Min Size** | {np.min(particle_sizes):.2f} μm |
| **Max Size** | {np.max(particle_sizes):.2f} μm |
| **Sample Count** | {len(particle_sizes):,} particles |
""")

# Download options
st.subheader("💾 Export Options")

col_dl1, col_dl2 = st.columns(2)

with col_dl1:
    buf_png = BytesIO()
    fig.savefig(buf_png, format='png', dpi=300, bbox_inches='tight')
    buf_png.seek(0)
    
    st.download_button(
        label="📥 Download Figure (PNG)",
        data=buf_png,
        file_name=f"{material.replace(' ', '_')}_PSD.png",
        mime="image/png"
    )

with col_dl2:
    df = pd.DataFrame({
        'Particle_Size_μm': particle_sizes,
        'Cumulative_Percentile': np.rankdata(particle_sizes) / len(particle_sizes) * 100
    })
    csv = df.to_csv(index=False)
    
    st.download_button(
        label="📥 Download Data (CSV)",
        data=csv,
        file_name=f"{material.replace(' ', '_')}_PSD_data.csv",
        mime="text/csv"
    )

# Distribution information
with st.expander("ℹ️ About Distribution Types"):
    st.markdown("""
    ### Distribution Types for SLM Powders
    
    | Distribution | Description | Best For |
    |--------------|-------------|----------|
    | **Log-Normal** | Most common for gas-atomized powders | Standard SLM powders |
    | **Normal (Gaussian)** | Symmetric distribution | Water-atomized powders |
    | **Rosin-Rammler** | Common for milled/crushed powders | Irregular particles |
    | **Weibull** | Flexible shape parameter | Various manufacturing methods |
    | **Bimodal** | Two distinct size populations | Enhanced packing density |
    
    ### Quality Metrics
    
    - **Span**: (D₉₀ - D₁₀) / D₅₀ — Lower values indicate narrower distribution
    - **Typical Span**: < 1.5 for good flowability
    - **D₅₀ Range**: 15-45 μm optimal for most SLM applications
    """)
