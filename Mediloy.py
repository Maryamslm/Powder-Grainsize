import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import matplotlib.gridspec as gridspec

# Set professional style
plt.style.use('default')
plt.rcParams['font.family'] 'Arial'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.linewidth'] = 1.5
plt.rcParams['xtick.direction'] = 'in'
plt.rcParams['ytick.direction'] = 'in'
plt.rcParams['xtick.top'] = False
plt.rcParams['ytick.right'] = False

# Generate representative particle size data for Mediloy S-Co (10-45 μm range)
np.random.seed(42)
n_particles = 10000

# Log-normal distribution centered in the 10-45 μm range
mu = np.log(25)  # median around 25 μm
sigma = 0.4  # distribution width
particle_sizes = np.random.lognormal(mu, sigma, n_particles)

# Filter to 10-45 μm range
particle_sizes = particle_sizes[(particle_sizes >= 10) & (particle_sizes <= 45)]

# Calculate D10, D50, D90
D10 = np.percentile(particle_sizes, 10)
D50 = np.percentile(particle_sizes, 50)
D90 = np.percentile(particle_sizes, 90)

# Create figure with specific size
fig = plt.figure(figsize=(6, 5), dpi=300)
gs = gridspec.GridSpec(1, 1)
ax = fig.add_subplot(gs[0, 0])

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

# Plot frequency distribution as bars (red)
bar_width = bin_edges[1:] - bin_edges[:-1]
ax.bar(bin_edges[:-1], freq_dist, width=bar_width, bottom=0, 
       align='edge', color='#DC143C', edgecolor='none', alpha=0.8, label='FD')

# Create secondary y-axis for cumulative distribution
ax2 = ax.twinx()

# Plot cumulative distribution curve (green)
ax2.plot(bin_centers, cumulative, color='#228B22', linewidth=2.5, label='PSD')

# Set axis limits
ax.set_xlim(1, 100)
ax.set_ylim(0, 8.5)
ax2.set_ylim(0, 105)

# Set logarithmic x-axis
ax.set_xscale('log')

# Set labels
ax.set_xlabel('Diameter [μm]', fontsize=11, fontweight='bold', labelpad=10)
ax.set_ylabel('FD [%]', fontsize=11, fontweight='bold', color='#DC143C', labelpad=10)
ax2.set_ylabel('PSD [%]', fontsize=11, fontweight='bold', color='#228B22', labelpad=10)

# Set tick parameters
ax.tick_params(axis='both', which='major', labelsize=10, width=1.5, length=6)
ax2.tick_params(axis='both', which='major', labelsize=10, width=1.5, length=6, 
                labelcolor='#228B22')
ax.tick_params(axis='y', which='major', labelcolor='#DC143C')

# Set x-axis ticks
ax.set_xticks([1, 10, 100])
ax.set_xticklabels(['1', '10', '100'])

# Add D10, D50, D90 text box
textstr = f'D₉₀={D90:.2f} μm\nD₅₀={D50:.2f} μm\nD₁₀={D10:.2f} μm'
props = dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='none')
ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=10, 
        verticalalignment='top', fontweight='bold', bbox=props)

# Add vertical lines for D10, D50, D90
ax.axvline(x=D10, color='gray', linestyle='--', linewidth=0.8, alpha=0.5)
ax.axvline(x=D50, color='gray', linestyle='--', linewidth=0.8, alpha=0.5)
ax.axvline(x=D90, color='gray', linestyle='--', linewidth=0.8, alpha=0.5)

# Add subplot label (b)
ax.text(-0.15, 1.05, '(b)', transform=ax.transAxes, 
        fontsize=14, fontweight='bold', va='top', ha='right')

# Tight layout
plt.tight_layout()

# Save figure
plt.savefig('Mediloy_SCo_PSD_histogram.png', dpi=300, bbox_inches='tight')
plt.savefig('Mediloy_SCo_PSD_histogram.pdf', bbox_inches='tight')

print(f"Particle Size Distribution Statistics for Mediloy S-Co:")
print(f"D₁₀ (10th percentile): {D10:.2f} μm")
print(f"D₅₀ (50th percentile/median): {D50:.2f} μm")
print(f"D₉₀ (90th percentile): {D90:.2f} μm")
print(f"Mean particle size: {np.mean(particle_sizes):.2f} μm")
print(f"Standard deviation: {np.std(particle_sizes):.2f} μm")
print(f"Range: {np.min(particle_sizes):.2f} - {np.max(particle_sizes):.2f} μm")

plt.show()
