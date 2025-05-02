import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.colors as mcolors
import re

# --- Load Map ---
img = plt.imread('maps/Icebox.png')

fig, ax = plt.subplots(figsize=(10, 10))
ax.imshow(img, extent=[0, 10, 10, 0])

# --- Read CSV ---
df = pd.read_csv(
    'demo_data.csv',
    dtype=str
)

grid = np.full((10, 10), np.nan)

# --- Fill Grid ---
for _, row in df.iterrows():
    coord = str(row['Coordinate']).strip()
    if ',' not in coord:
        print(f"Skipping invalid coord: '{coord}'")
        continue

    try:
        y, x = map(int, coord.split(','))
    except Exception as e:
        print(f"Failed to parse coordinate '{coord}': {e}")
        continue

    diff_text = str(row['Differential']).strip()
    diff_match = re.match(r'([+-]?\d+)', diff_text)
    if not diff_match:
        print(f"Invalid differential format: '{diff_text}'")
        continue
    diff = int(diff_match.group(1))

    print(f"Placing diff {diff} at grid (row={y}, col={x})")
    grid[y, x] = diff

# --- Custom Colormap ---
colors = [
    (0.0, '#8B0000'),  # Deep dark red (-3)
    (0.25, '#ff9999'), # Light red (-1)
    (0.5, '#ffffff'),  # White (0)
    (0.75, '#66ff66'), # Light green (+1)
    (1.0, '#006400')   # Dark green (+3)
]
cmap = mcolors.LinearSegmentedColormap.from_list('CustomRedGreen', colors)

norm = plt.Normalize(vmin=-3, vmax=3)

# --- Plot Filled Grids (with opacity) ---
for y in range(10):
    for x in range(10):
        value = grid[y, x]
        if not np.isnan(value):
            print(f"Filling grid ({y},{x}) with value {value}")
            color = cmap(norm(value))
            rect = patches.Rectangle(
                (x, y), 1, 1,
                linewidth=0,
                edgecolor=None,
                facecolor=color,
                alpha=0.7  # Opacity for blending
            )
            ax.add_patch(rect)

# --- Draw grid lines everywhere ---
for y in range(10):
    for x in range(10):
        gridline = patches.Rectangle(
            (x, y), 1, 1,
            linewidth=0.5,
            edgecolor='gray',
            facecolor='none'
        )
        ax.add_patch(gridline)

# ✅ Grid labels in white now
for i in range(10):
    for j in range(10):
        ax.text(
            j + 0.5, i + 0.5, f'{i},{j}',
            ha='center', va='center',
            color='white',  # <-- Changed from cyan to white
            fontsize=8,
            alpha=0.8
        )

# Colorbar
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax, shrink=0.75, pad=0.02)
cbar.outline.set_visible(False)
cbar.set_label('Kill Differential', fontsize=12)

# Title & save
ax.set_title('Aspas Atk Icebox Kill Differential Heatmap', fontsize=16, pad=20)
ax.set_axis_off()

plt.savefig('demo_heatmap_output_white_labels.png', bbox_inches='tight', dpi=300)
plt.show()
