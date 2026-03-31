import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import streamlit as st
from scipy import stats
from scipy.stats import rankdata
from io import BytesIO
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

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

# Color mode selection
color_mode = st.sidebar.selectbox(
    "Color Mode",
    ["Automatic (Colormap)", "Manual (Custom Colors)"],
    index=0
)

# Colormap selection (only shown if automatic mode)
if color_mode == "Automatic (Colormap)":
    colormap = st.sidebar.selectbox(
        "Colormap",
        COLORMAPS,
        index=0
    )
    # Get colors from colormap
    cmap = plt.get_cmap(colormap)
    bar_color = cmap(0.3)
    line_color = cmap(0.7)
else:
    # Manual color selection
    bar_color = st.sidebar.color_picker("Bar Color", "#DC143C")
    line_color = st.sidebar.color_picker("Line Color", "#228B22")
    colormap = "Custom"

# Font size control
font_size = st.sidebar.slider("Font Size", 8, 36, 10, 1)

# Figure size
fig_width = st.sidebar.slider("Figure Width", 4.0, 12.0, 8.0, 0.5)
fig_height = st.sidebar.slider("Figure Height", 4.0, 10.0, 6.0, 0.5)
