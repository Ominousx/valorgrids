import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.colors as mcolors
import re
import os  # <-- NEW: for dynamic title

# --- Load Map ---
map_path = 'maps/Icebox.png'
try:
    img = plt.imread(map_path)
except FileNotFoundError:
    print(f"Map image not found at {map_path}")
    exit(1)

# --- Extract map name dynamically ---
map_name = os.path.basename(map_path).split('.')[0]

# --- Ask user for a custom label (team names, player, side, etc.) ---
match_label = input("Enter match label (e.g., 'Aspas Attack', 'DRX vs PRX'):\n").strip()

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
    except Exception as e:
        print(f"Failed to parse coordinate '{coord}': {e}")
        continue

    # Extract number from 'Kills' and 'Deaths' columns like '4 kills'
    kills_text = str(row['Kills']).strip()
    deaths_text = str(row['Deaths']).strip()

    kills_match = re.match(r'(\d+)', kills_text)
    deaths_match = re.match(r'(\d+)', deaths_text)

    if not (kills_match and deaths_match):
        print(f"Invalid kills/deaths: '{kills_text}', '{deaths_text}'")
        continue

    kills = int(kills_match.group(1))
    deaths = int(deaths_match.group(1))

    # We still recalculate diff just in case
    diff = kills - deaths
    engagements = kills + deaths

    print(f"Grid ({y},{x}): K={kills}, D={deaths}, Diff={diff}, Engage={engagements}")
    diff_grid[y, x] = diff
    engage_grid[y, x] = engagements

# --- Custom Colormaps ---
# Kill Differential: Red to Green
diff_colors = [
    (0.0, '#8B0000'),  # Deep dark red (-3)
    (0.25, '#ff9999'), # Light red (-1)
    (0.5, '#ffffff'),  # White (0)
    (0.75, '#66ff66'), # Light green (+1)
    (1.0, '#006400')   # Dark green (+3)
]
diff_cmap = mcolors.LinearSegmentedColormap.from_list('DiffRedGreen', diff_colors)
diff_norm = plt.Normalize(vmin=-3, vmax=3)

# Engagements: Light red to dark red
engage_cmap = mcolors.LinearSegmentedColormap.from_list('EngagementRed', [
    (0.0, '#ffe6e6'),
    (1.0, '#8B0000')
])
max_engage = np.nanmax(engage_grid)
if np.isnan(max_engage):
    max_engage = 1
engage_norm = plt.Normalize(vmin=0, vmax=max_engage)

# --- Ask user what to generate ---
choice = input("What heatmap do you want to generate? (diff / engage):\n").strip().lower()

if choice in ['diff', 'engage']:
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.imshow(img, extent=[0, 10, 10, 0])

    if choice == 'diff':
        title_type = 'Kill Differential Heatmap'
        grid_data = diff_grid
        cmap = diff_cmap
        norm = diff_norm
        color_label = 'Kill Differential'
    else:
        title_type = 'Engagement Heatmap'
        grid_data = engage_grid
        cmap = engage_cmap
        norm = engage_norm
        color_label = 'Engagements (Kills + Deaths)'

    for y in range(10):
        for x in range(10):
            value = grid_data[y, x]
            if not np.isnan(value):
                color = cmap(norm(value))
                rect = patches.Rectangle(
                    (x, y), 1, 1,
                    linewidth=0,
                    edgecolor=None,
                    facecolor=color,
                    alpha=0.8
                )
                ax.add_patch(rect)

    # Gridlines & labels
    for y in range(10):
        for x in range(10):
            gridline = patches.Rectangle((x, y), 1, 1, linewidth=0.5, edgecolor='gray', facecolor='none')
            ax.add_patch(gridline)
    for i in range(10):
        for j in range(10):
            ax.text(j + 0.5, i + 0.5, f'{i},{j}', ha='center', va='center', color='white', fontsize=8, alpha=0.8)

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, shrink=0.75, pad=0.02)
    cbar.outline.set_visible(False)
    cbar.set_label(color_label, fontsize=12)

    # ✅ Dynamic title here!
    ax.set_title(f"{match_label} - {map_name} - {title_type}", fontsize=16, pad=20)
    ax.set_axis_off()
    output_file = f'demo_heatmap_{choice}.png'
    plt.savefig(output_file, bbox_inches='tight', dpi=300)
    print(f"Saved {output_file}")
    plt.show()

else:
    print("Invalid choice. Please run the script again and enter diff or engage.")
