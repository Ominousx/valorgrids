import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors # using mcolors instead of patches
import re
import os  # <-- NEW: for dynamic title

# ←— ADDED: use Matplotlib’s built-in dark style
plt.style.use('dark_background')

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
    except:
        continue

    # parse kills/deaths
    kills = int(re.match(r'(\d+)', row['Kills']).group(1))
    deaths = int(re.match(r'(\d+)', row['Deaths']).group(1))
    diff = kills - deaths
    engagements = kills + deaths

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
diff_norm = plt.Normalize(vmin=-3, vmax=+3)

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
    fig, ax = plt.subplots(
        figsize=(10, 10),
        # ←— ADDED: set the figure facecolor to match dark style
        facecolor='#121212',
    )
    # ←— ADDED: dark background for the axes
    ax.set_facecolor('#121212')

    ax.imshow(img, extent=[0, 10, 10, 0], origin='upper', zorder=0)

    # select data + colormap
    if choice == 'diff':
        title_type = 'Kill Differential Heatmap'
        grid_data = diff_grid
        cmap = diff_cmap
        norm = diff_norm
        color_label = 'Kill Differential'
        alpha = 0.8
    else:
        title_type = 'Engagement Heatmap'
        grid_data = engage_grid
        cmap = engage_cmap
        norm = engage_norm
        color_label = 'Engagements (Kills + Deaths)'
        alpha = 0.8

    # --- NEW: build a single 10×10×4 RGBA overlay ---
    heat_rgba = np.zeros((10, 10, 4), dtype=float)
    for y in range(10):
        for x in range(10):
            v = grid_data[y, x]
            if not np.isnan(v):
                r, g, b, _ = cmap(norm(v))    # get RGB from colormap
                heat_rgba[y, x, :3] = (r, g, b)
                heat_rgba[y, x,  3] = alpha   # fixed alpha

    # display the overlay
    ax.imshow(
        heat_rgba,
        extent=[0, 10, 10, 0],
        origin='upper',
        interpolation='nearest',
        zorder=1
    )

    # colorbar
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, shrink=0.75, pad=0.02)
    cbar.outline.set_visible(False)
    # ←— ADDED: make ticks & label white
    cbar.ax.yaxis.set_tick_params(color='white')
    cbar.ax.tick_params(colors='white')
    cbar.set_label(color_label, fontsize=12, color='white')

    # ✅ Dynamic title here!
    ax.set_title(
        f"{match_label} – {map_name} – {title_type}",
        fontsize=16,
        pad=20,
        color='white'
    )

    ax.set_axis_off()
    output_file = f'demo_heatmap_{choice}.png'
    plt.savefig(output_file, bbox_inches='tight', dpi=300,
                # ←— ADDED: ensure figure bg is saved
                facecolor=fig.get_facecolor()
    )
    print(f"Saved {output_file}")
    plt.show()
else:
    print("Invalid choice. Please run the script again and enter diff or engage.")
