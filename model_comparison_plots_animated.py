"""
Animated GIF: four panel-data models on the same scatter plot.
The regression lines physically move (interpolate intercept + slope) from one
model to the next, cycling:
  Pooled OLS → Fixed Effects → Random Effects → Mixed Effects → Pooled OLS …

Each model is held for HOLD_FRAMES frames, then the lines slide to the next
position over TRANSITION_FRAMES frames using cubic ease-in-out.
Saved to fig/panel_models_animated.gif.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.lines import Line2D

# ── Reproducibility ────────────────────────────────────────────────────────
np.random.seed(42)

# ── Constants ──────────────────────────────────────────────────────────────
n_groups  = 4
n_per     = 20
colors    = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3']

HOLD_FRAMES       = 40   # frames a model is shown without change
TRANSITION_FRAMES = 35   # frames used to slide lines to next model position
FPS               = 18   # frames per second in the GIF

# ── Data generation ────────────────────────────────────────────────────────
true_slope       = 0.8
x_offsets        = [0.0, 2.5, 5.0, 7.5]
group_intercepts = [9.0, 6.5, 4.0, 1.5]

xs, ys = [], []
for g in range(n_groups):
    x = np.linspace(x_offsets[g], x_offsets[g] + 2.5, n_per)
    y = group_intercepts[g] + true_slope * x + np.random.normal(0, 0.4, n_per)
    xs.append(x)
    ys.append(y)

all_x = np.concatenate(xs)
all_y = np.concatenate(ys)

# ── Model estimates ────────────────────────────────────────────────────────

# Pooled OLS — single line across all data
ols_coef   = np.polyfit(all_x, all_y, 1)
ols_params = [(ols_coef[1], ols_coef[0])] * n_groups  # same (intercept, slope) for all groups

# Fixed Effects — demeaning (Frisch-Waugh)
x_dm     = np.concatenate([xs[g] - xs[g].mean() for g in range(n_groups)])
y_dm     = np.concatenate([ys[g] - ys[g].mean() for g in range(n_groups)])
fe_slope = np.polyfit(x_dm, y_dm, 1)[0]
fe_ints  = [ys[g].mean() - fe_slope * xs[g].mean() for g in range(n_groups)]
fe_params = [(fe_ints[g], fe_slope) for g in range(n_groups)]

# Random Effects — partial pooling (λ=0.5)
lam           = 0.5
x_bar         = np.array([xs[g].mean() for g in range(n_groups)])
y_bar         = np.array([ys[g].mean() for g in range(n_groups)])
between_slope = np.polyfit(x_bar, y_bar, 1)[0]
re_slope      = (1 - lam) * fe_slope + lam * between_slope
base_ints     = [ys[g].mean() - re_slope * xs[g].mean() for g in range(n_groups)]
grand_mean_re = np.mean(base_ints)
re_ints       = [grand_mean_re + (1 - lam) * (a - grand_mean_re) for a in base_ints]
re_params     = [(re_ints[g], re_slope) for g in range(n_groups)]

# Mixed Effects — group-specific slopes
me_fits       = [np.polyfit(xs[g], ys[g], 1) for g in range(n_groups)]
me_params     = [(b, m) for m, b in me_fits]   # polyfit returns [slope, intercept]
me_slope_mean = np.mean([m for m, _ in me_fits])

# ── Model sequence ─────────────────────────────────────────────────────────
models = [
    {
        "params": ols_params,
        "title": "Pooled OLS",
        "subtitle": f"slope \u2248 {ols_coef[0]:.2f}  \u2190 biased by confound",
        "line_colors": ["black"] * n_groups,
    },
    {
        "params": fe_params,
        "title": "Fixed Effects (within estimator)",
        "subtitle": f"within-group slope \u2248 {fe_slope:.2f}",
        "line_colors": colors,
    },
    {
        "params": re_params,
        "title": "Random Effects",
        "subtitle": f"RE slope \u2248 {re_slope:.2f}  (within+between blend)",
        "line_colors": colors,
    },
    {
        "params": me_params,
        "title": "Mixed Effects (LMM)",
        "subtitle": f"avg slope \u2248 {me_slope_mean:.2f}",
        "line_colors": colors,
    },
]
n_models = len(models)

# ── Build frame list ───────────────────────────────────────────────────────
# Each frame stores the current interpolated (intercept, slope) per group,
# plus the line colour and label text.
frames_data = []

def ease_in_out(t):
    """Smooth cubic ease-in-out for t in [0, 1]."""
    return t * t * (3 - 2 * t)

def lerp_color(c1, c2, t):
    """Linearly interpolate between two hex colours."""
    import matplotlib.colors as mcolors
    r1, g1, b1, _ = mcolors.to_rgba(c1)
    r2, g2, b2, _ = mcolors.to_rgba(c2)
    return (r1 + (r2 - r1) * t,
            g1 + (g2 - g1) * t,
            b1 + (b2 - b1) * t)

for m_idx in range(n_models):
    m_next  = (m_idx + 1) % n_models
    model_A = models[m_idx]
    model_B = models[m_next]

    # Hold frames — lines stay put at model A
    for _ in range(HOLD_FRAMES):
        frames_data.append({
            "params":  model_A["params"],
            "colors":  model_A["line_colors"],
            "title":   model_A["title"],
            "subtitle": model_A["subtitle"],
        })

    # Transition frames — lines slide to model B positions
    for i in range(TRANSITION_FRAMES):
        t = ease_in_out((i + 1) / TRANSITION_FRAMES)
        interp_params = [
            (
                model_A["params"][g][0] * (1 - t) + model_B["params"][g][0] * t,  # intercept
                model_A["params"][g][1] * (1 - t) + model_B["params"][g][1] * t,  # slope
            )
            for g in range(n_groups)
        ]
        interp_colors = [
            lerp_color(model_A["line_colors"][g], model_B["line_colors"][g], t)
            for g in range(n_groups)
        ]
        title    = model_A["title"]    if t < 0.5 else model_B["title"]
        subtitle = model_A["subtitle"] if t < 0.5 else model_B["subtitle"]
        frames_data.append({
            "params":  interp_params,
            "colors":  interp_colors,
            "title":   title,
            "subtitle": subtitle,
        })

total_frames = len(frames_data)

# ── Set up figure ──────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 5.5))
fig.patch.set_facecolor('white')

# Static scatter
for g in range(n_groups):
    ax.scatter(xs[g], ys[g], color=colors[g], alpha=0.55, s=22, zorder=2)

ax.set_xlabel("X", fontsize=10)
ax.set_ylabel("Y", fontsize=10)
ax.grid(True, alpha=0.2)
ax.spines[['top', 'right']].set_visible(False)

# One set of lines — positions updated each frame
line_objects = []
for g in range(n_groups):
    (ln,) = ax.plot([], [], lw=2.5, zorder=3)
    line_objects.append(ln)

# Dynamic title and annotation
title_text   = ax.set_title("", fontsize=12, pad=10, fontweight='bold')
subtitle_ann = ax.annotate("", xy=(0.04, 0.05), xycoords='axes fraction',
                            fontsize=8.5, color='#333333',
                            bbox=dict(boxstyle='round,pad=0.35', fc='white', alpha=0.8))

# Group legend (static)
legend_handles = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor=colors[g],
           markersize=7, label=f'Group {g+1}')
    for g in range(n_groups)
]
ax.legend(handles=legend_handles, fontsize=8.5, loc='upper right', framealpha=0.8)

fig.suptitle("Comparing Panel Data Models", fontsize=13, y=0.98)
fig.text(0.01, 0.01,
         "Note: generated data \u2014 'Intro to Longitudinal Data Analysis with R' workshop, Jarnach, 2026.",
         ha='left', fontsize=7, color='#666666', style='italic')

plt.tight_layout()
plt.subplots_adjust(top=0.88, bottom=0.12)

# ── Animation update function ──────────────────────────────────────────────
def update(frame_idx):
    fd = frames_data[frame_idx]

    for g, ln in enumerate(line_objects):
        intercept, slope = fd["params"][g]
        xg = np.array([xs[g].min(), xs[g].max()])
        ln.set_data(xg, intercept + slope * xg)
        ln.set_color(fd["colors"][g])

    title_text.set_text(fd["title"])
    subtitle_ann.set_text(fd["subtitle"])

    return line_objects + [title_text, subtitle_ann]

# ── Build and save animation ───────────────────────────────────────────────
ani = animation.FuncAnimation(
    fig,
    update,
    frames=total_frames,
    interval=1000 / FPS,
    blit=True,
)

output_path = "fig/panel_models_animated.gif"
ani.save(output_path, writer="pillow", fps=FPS, dpi=130)
print(f"Saved \u2192 {output_path}")
plt.close(fig)
