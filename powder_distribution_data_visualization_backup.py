import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import streamlit as st
from scipy import stats
from scipy.stats import rankdata
from io import BytesIO
import pandas as pd

# Page configuration
st.set_page_config(page_title="SLM Powder PSD Analyzer", layout="wide")

# Colormap options (50 total)
COLORMAPS = [
    'viridis', 'plasma', 'inferno', 'magma', 'cividis',
    'turbo', 'jet', 'rainbow', 'nipy_spectral', 'gist_rainbow',
    'gist_earth', 'gist_stern', 'gist_ncar', 'ocean', 'terrain',
    'hsv', 'tab10', 'tab20', 'tab20b', 'tab20c',
    'Accent', 'Dark2', 'Paired', 'Pastel1', 'Pastel2',
    'Set1', 'Set2', 'Set3', 'flag', 'prism',
    'bone', 'copper', 'pink', 'spring', 'summer',
    'autumn', 'winter', 'cool', 'Wistia', 'hot',
    'afmhot', 'gist_heat', 'binary', 'Greys', 'Purples',
    'Blues', 'Greens', 'Oranges', 'Reds', 'YlOrBr', 'YlOrRd'
]

# Sidebar for user inputs
st.sidebar.title("⚙️ Settings")

# Distribution type selection
distribution_type = st.sidebar.selectbox(
    "Distribution Type",
    ["Log-Normal", "Normal (Gaussian)", "Rosin-Rammler", "Weibull", "Bimodal"],
    index=0
)

# Material selection
material = st.sidebar.selectbox(
    "Material",
    ["Mediloy S-Co", "Ti-6Al-4V", "Inconel 718", "AlSi10Mg", "316L Stainless Steel", "Custom"],
    index=0
)

# ===== VISUALIZATION SETTINGS =====
st.sidebar.subheader("🎨 Visualization")

# Colormap selection
colormap = st.sidebar.selectbox(
    "Colormap",
    COLORMAPS,
    index=0
)

# Font size control
font_size = st.sidebar.slider("Font Size", 8, 36, 10, 1)

# Figure size - ✅ FIXED: All floats
fig_width = st.sidebar.slider("Figure Width", 4.0, 12.0, 8.0, 0.5)
fig_height = st.sidebar.slider("Figure Height", 4.0, 10.0, 6.0, 0.5)

# Legend position
legend_position = st.sidebar.selectbox(
    "Legend Position",
    ["best", "upper right", "upper left", "lower left", "lower right",
     "right", "center left", "center right", "lower center", "upper center", "center"],
    index=0
)

# Show grid
show_grid = st.sidebar.checkbox("Show Grid", value=False)

# Line width
line_width = st.sidebar.slider("Line Width", 0.5, 3.0, 2.0, 0.25)

# ===== DISTRIBUTION PARAMETERS =====
st.sidebar.subheader("📐 Distribution Parameters")

if distribution_type == "Log-Normal":
    mu = st.sidebar.slider("μ (log median)", 2.5, 4.0, 3.2, 0.1)
    sigma = st.sidebar.slider("σ (width)", 0.2, 0.8, 0.4, 0.05)
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
    std1 = st.sidebar.slider("Std Dev 1 (μm)", 2.0, 10.0, 4.0, 0.5)
    mean2 = st.sidebar.slider("Mean 2 (μm)", 30.0, 60.0, 45.0, 1.0)
    std2 = st.sidebar.slider("Std Dev 2 (μm)", 2.0, 10.0, 6.0, 0.5)
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

# Get colors from colormap
cmap = plt.get_cmap(colormap)
colors = [cmap(0.3), cmap(0.7)]

# Main display
st.title("🔬 SLM Powder Particle Size Distribution Analyzer")
st.markdown(f"**Material:** `{material}` | **Typical Range:** `{material_ranges[material]}`")
st.markdown(f"**Distribution:** `{distribution_type}` | **Colormap:** `{colormap}`")

# Create figure
fig = plt.figure(figsize=(fig_width, fig_height), dpi=150)
gs = gridspec.GridSpec(1, 1)
ax = fig.add_subplot(gs[0, 0])

# Set professional style
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = font_size
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
       align='edge', color=colors[0], edgecolor='none', alpha=0.8)

# Create secondary y-axis for cumulative distribution
ax2 = ax.twinx()

# Plot cumulative distribution curve
ax2.plot(bin_centers, cumulative, color=colors[1], linewidth=line_width)

# Set axis limits
ax.set_xlim(1, 100)
ax.set_ylim(0, max(freq_dist) * 1.2 if len(freq_dist) > 0 else 10)
ax2.set_ylim(0, 105)

# Set logarithmic x-axis
ax.set_xscale('log')

# Set labels with editable font size
ax.set_xlabel('Particle Diameter [μm]', fontsize=font_size+1, fontweight='bold', labelpad=10)
ax.set_ylabel('Frequency [%]', fontsize=font_size+1, fontweight='bold', color=colors[0], labelpad=10)
ax2.set_ylabel('Cumulative [%]', fontsize=font_size+1, fontweight='bold', color=colors[1], labelpad=10)

# Set tick parameters
ax.tick_params(axis='both', which='major', labelsize=font_size, width=1.5, length=6)
ax2.tick_params(axis='both', which='major', labelsize=font_size, width=1.5, length=6, 
                labelcolor=colors[1])
ax.tick_params(axis='y', which='major', labelcolor=colors[0])

# Set x-axis ticks
ax.set_xticks([1, 10, 100])
ax.set_xticklabels(['1', '10', '100'])

# Add grid if enabled
if show_grid:
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)

# Add D10, D50, D90 text box
textstr = f'D₉₀ = {D90:.2f} μm\nD₅₀ = {D50:.2f} μm\nD₁₀ = {D10:.2f} μm\nSpan = {span:.2f}'
props = dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='gray', linewidth=1)
ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=font_size, 
        verticalalignment='top', fontweight='bold', bbox=props)

# Add vertical lines for D10, D50, D90
ax.axvline(x=D10, color='gray', linestyle='--', linewidth=1, alpha=0.7)
ax.axvline(x=D50, color='gray', linestyle='--', linewidth=1, alpha=0.7)
ax.axvline(x=D90, color='gray', linestyle='--', linewidth=1, alpha=0.7)

# ===== SINGLE UNIFIED LEGEND =====
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

legend_elements = [
    Patch(facecolor=colors[0], edgecolor='none', alpha=0.8, label='Frequency Distribution'),
    Line2D([0], [0], color=colors[1], linewidth=line_width, label='Cumulative PSD'),
    Line2D([0], [0], color='gray', linestyle='--', linewidth=1, alpha=0.7, label='D₁₀, D₅₀, D₉₀')
]

# Add single legend at best position
ax.legend(handles=legend_elements, loc=legend_position, fontsize=font_size-1, 
          framealpha=0.9, edgecolor='gray')

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
    st.metric("Span", f"{span:.2f}")

with col3:
    st.subheader("✅ Quality Check")
    span_ok = span < 1.5
    range_ok = D10 >= 1 and D90 <= 100
    st.metric("Span < 1.5", "✅ Pass" if span_ok else "⚠️ Review")
    st.metric("Range Valid", "✅ Pass" if range_ok else "⚠️ Review")
    st.metric("Sample Size", f"{len(particle_sizes):,}")

# Detailed statistics table
st.subheader("📋 Detailed Statistics")
st.write(f"""
| Parameter | Value |
|-----------|-------|
| **Distribution Type** | {distribution_type} |
| **Material** | {material} |
| **Colormap** | {colormap} |
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

col_dl1, col_dl2, col_dl3 = st.columns(3)

with col_dl1:
    buf_png = BytesIO()
    fig.savefig(buf_png, format='png', dpi=300, bbox_inches='tight')
    buf_png.seek(0)
    
    st.download_button(
        label="📥 Download PNG",
        data=buf_png,
        file_name=f"{material.replace(' ', '_')}_PSD.png",
        mime="image/png"
    )

with col_dl2:
    buf_pdf = BytesIO()
    fig.savefig(buf_pdf, format='pdf', bbox_inches='tight')
    buf_pdf.seek(0)
    
    st.download_button(
        label="📥 Download PDF",
        data=buf_pdf,
        file_name=f"{material.replace(' ', '_')}_PSD.pdf",
        mime="application/pdf"
    )

with col_dl3:
    df = pd.DataFrame({
        'Particle_Size_μm': particle_sizes,
        'Cumulative_Percentile': rankdata(particle_sizes) / len(particle_sizes) * 100
    })
    csv = df.to_csv(index=False)
    
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=f"{material.replace(' ', '_')}_PSD_data.csv",
        mime="text/csv"
    )

# Colormap preview
with st.expander("🎨 Colormap Preview"):
    st.write(f"**Selected:** `{colormap}`")
    
    fig_cmap, axes = plt.subplots(5, 10, figsize=(20, 2))
    axes = axes.flatten()
    
    for i, cmap_name in enumerate(COLORMAPS):
        if i < 50:
            gradient = np.linspace(0, 1, 256).reshape(1, -1)
            axes[i].imshow(gradient, aspect='auto', cmap=plt.get_cmap(cmap_name))
            axes[i].axis('off')
            if i == COLORMAPS.index(colormap):
                axes[i].set_title(f"★ {cmap_name}", fontsize=8, fontweight='bold')
            else:
                axes[i].set_title(cmap_name, fontsize=7)
    
    plt.tight_layout()
    st.pyplot(fig_cmap)

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
