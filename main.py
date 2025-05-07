import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import re
import os
from skimage.transform import resize
from scipy.ndimage import zoom
import argparse

# --- CLI arguments ---
parser = argparse.ArgumentParser()
parser.add_argument('--map', type=str, required=True, help="Map name (e.g., Icebox, Ascent, Bind)")
parser.add_argument('--label', type=str, default='', help="Match label (e.g., 'Aspas Attack')")
parser.add_argument('--type', type=str, choices=['diff', 'engage'], required=True, help="Heatmap type: diff or engage")
args = parser.parse_args()

map_name = args.map
match_label = args.label
choice = args.type

# Use dark background style
plt.style.use('dark_background')

# --- Load Map ---
map_path = f'maps/{map_name}.png'
try:
    img = plt.imread(map_path)
except FileNotFoundError:
    print(f"Map image not found at {map_path}")
    exit(1)

img_h, img_w = img.shape[:2]

# Extract alpha mask (transparency)
if img.shape[2] == 4:
    alpha_mask = img[..., 3]
else:
    print("Warning: Map image has no alpha channel — masking will not work properly.")
    alpha_mask = np.ones((img_h, img_w))

# --- Read CSV ---
df = pd.read_csv('demo_data.csv', dtype=str)

diff_grid = np.full((10, 10), np.nan)
engage_grid = np.full((10, 10), np.nan)

# --- Fill Grids ---
for _, row in df.iterrows():
    coord = str(row['Coordinate']).strip().replace('"', '')
    if ',' not in coord:
        print(f"Skipping invalid coord: '{coord}'")
        continue
    try:
        y, x = map(int, coord.split(','))
    except:
        continue

    kills = int(re.match(r'(\d+)', row['Kills']).group(1))
    deaths = int(re.match(r'(\d+)', row['Deaths']).group(1))
    diff = max(-3, min(3, kills - deaths))
    engagements = kills + deaths

    diff_grid[y, x] = diff
    engage_grid[y, x] = engagements

# --- Custom Colormaps ---
diff_colors = [
    (0.0, '#8B0000'),
    (0.25, '#ff9999'),
    (0.5, '#ffffff'),
    (0.75, '#66ff66'),
    (1.0, '#006400')
]
diff_cmap = mcolors.LinearSegmentedColormap.from_list('DiffRedGreen', diff_colors)
diff_norm = plt.Normalize(vmin=-3, vmax=+3)

engage_cmap = mcolors.LinearSegmentedColormap.from_list('EngagementRed', [
    (0.0, '#ffe6e6'),
    (1.0, '#8B0000')
])
max_engage = np.nanmax(engage_grid)
if np.isnan(max_engage):
    max_engage = 1
engage_norm = plt.Normalize(vmin=0, vmax=max_engage)

if choice in ['diff', 'engage']:
    fig, ax = plt.subplots(figsize=(10, 10), facecolor='#121212')
    ax.set_facecolor('#121212')
    ax.imshow(img, extent=[0, 10, 10, 0], origin='upper', zorder=0)

    grid_data = diff_grid if choice == 'diff' else engage_grid
    cmap = diff_cmap if choice == 'diff' else engage_cmap
    norm = diff_norm if choice == 'diff' else engage_norm
    color_label = 'Kill Differential' if choice == 'diff' else 'Engagements (Kills + Deaths)'
    title_type = 'Kill Differential Heatmap' if choice == 'diff' else 'Engagement Heatmap'
    alpha = 0.8

    heat_rgba = np.zeros((10, 10, 4), dtype=float)
    for y in range(10):
        for x in range(10):
            v = grid_data[y, x]
            if not np.isnan(v):
                r, g, b, _ = cmap(norm(v))
                heat_rgba[y, x, :3] = (r, g, b)
                heat_rgba[y, x, 3] = alpha

    zoom_y = img_h / 10
    zoom_x = img_w / 10
    heat_resized = zoom(heat_rgba, (zoom_y, zoom_x, 1), order=0)  # keep grid

    heat_resized[..., 3] *= alpha_mask

    ax.imshow(
        heat_resized,
        extent=[0, 10, 10, 0],
        origin='upper',
        interpolation='nearest',
        zorder=1
    )

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, shrink=0.75, pad=0.02)
    cbar.outline.set_visible(False)
    cbar.ax.yaxis.set_tick_params(color='white')
    cbar.ax.tick_params(colors='white')
    cbar.set_label(color_label, fontsize=12, color='white')

    ax.set_title(
        f"{match_label} – {map_name} – {title_type}",
        fontsize=16,
        pad=20,
        color='white'
    )
    ax.set_axis_off()

    safe_match_label = re.sub(r'[^A-Za-z0-9_\- ]', '', match_label).replace(' ', '_')
    output_file = f'demo_heatmap_{safe_match_label}_{choice}.png'
    plt.savefig(output_file, bbox_inches='tight', dpi=300, facecolor=fig.get_facecolor())
    print(f"Saved {output_file}")
    plt.show()
else:
    print("Invalid choice. Please use --type diff or --type engage.")
