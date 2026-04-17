import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

np.random.seed(42)

n_groups   = 4
n_per      = 20
colors     = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3']

# ── Data generation ────────────────────────────────────────────────────────
# Groups occupy distinct x-ranges; their intercepts are negatively correlated
# with x.  This creates a Simpson's Paradox: within each group the slope is
# positive, but pooled OLS recovers a near-zero or negative slope because it
# conflates the between-group trend with the within-group effect.
true_slope       = 0.8
x_offsets        = [0.0, 2.5, 5.0, 7.5]     # each group spans offset … offset+2.5
group_intercepts = [9.0, 6.5, 4.0, 1.5]     # decreasing → confounded with x

xs, ys = [], []
for g in range(n_groups):
    x = np.linspace(x_offsets[g], x_offsets[g] + 2.5, n_per)
    y = group_intercepts[g] + true_slope * x + np.random.normal(0, 0.4, n_per)
    xs.append(x)
    ys.append(y)

all_x = np.concatenate(xs)
all_y = np.concatenate(ys)

# ── Model estimates ────────────────────────────────────────────────────────
# Pooled OLS
ols_coef = np.polyfit(all_x, all_y, 1)

# Fixed Effects: within-group slope estimated by demeaning (Frisch-Waugh)
x_dm      = np.concatenate([xs[g] - xs[g].mean() for g in range(n_groups)])
y_dm      = np.concatenate([ys[g] - ys[g].mean() for g in range(n_groups)])
fe_slope  = np.polyfit(x_dm, y_dm, 1)[0]
fe_ints   = [ys[g].mean() - fe_slope * xs[g].mean() for g in range(n_groups)]

# Random Effects: partial pooling — intercepts shrunk toward the grand mean.
# RE uses both within (FE) and between variation, so its slope is a blend.
# When Cov(x, α_i) ≠ 0 this pulls the RE slope away from the true within slope → bias.
# λ=0 → identical to FE;  λ=1 → fully pooled (OLS)
lam           = 0.5
x_bar         = np.array([xs[g].mean() for g in range(n_groups)])
y_bar         = np.array([ys[g].mean() for g in range(n_groups)])
between_slope = np.polyfit(x_bar, y_bar, 1)[0]
re_slope      = (1 - lam) * fe_slope + lam * between_slope
# Intercepts computed consistently with re_slope, then shrunk toward grand mean
base_ints     = [ys[g].mean() - re_slope * xs[g].mean() for g in range(n_groups)]
grand_mean_re = np.mean(base_ints)
re_ints       = [grand_mean_re + (1 - lam) * (a - grand_mean_re) for a in base_ints]

# Mixed Effects (LMM): shared population slope (fixed effect) + group-level
# random deviations for both intercept and slope.
me_fits       = [np.polyfit(xs[g], ys[g], 1) for g in range(n_groups)]
me_slope_mean = np.mean([b for b, _ in me_fits])

# ── Plot ───────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 4, figsize=(20, 5.5), sharey=True)

titles = [
    "Pooled OLS\n(single line, ignores group structure)",
    "Fixed Effects (within estimator)\n(each group: own intercept, common slope)",
    f"Random Effects\n(shrunk intercepts, common slope)",
    "Mixed Effects (LMM)\n(each group: own intercept & own slope)",
]
notes = [
    f"slope \u2248 {ols_coef[0]:.2f}  \u2190 biased by confound",
    f"within-group slope \u2248 {fe_slope:.2f}",
    f"RE slope \u2248 {re_slope:.2f}  (within+between blend)",
    f"avg slope \u2248 {me_slope_mean:.2f}",
]

# Scatter points on every panel
for ax in axes:
    for g in range(n_groups):
        ax.scatter(xs[g], ys[g], color=colors[g], alpha=0.55, s=22, zorder=2)

# Panel 0 — Pooled OLS
x_full = np.array([all_x.min(), all_x.max()])
axes[0].plot(x_full, np.polyval(ols_coef, x_full), 'k-', lw=2.5, label='OLS')

# Panel 1 — Fixed Effects
for g in range(n_groups):
    xg = [xs[g].min(), xs[g].max()]
    axes[1].plot(xg, [fe_ints[g] + fe_slope * xi for xi in xg],
                 color=colors[g], lw=2.5)

# Panel 2 — Random Effects
for g in range(n_groups):
    xg = [xs[g].min(), xs[g].max()]
    axes[2].plot(xg, [re_ints[g] + re_slope * xi for xi in xg],
                 color=colors[g], lw=2.5)

# Panel 3 — Mixed Effects
for g in range(n_groups):
    xg = np.array([xs[g].min(), xs[g].max()])
    axes[3].plot(xg, np.polyval(me_fits[g], xg), color=colors[g], lw=2.5)

# Formatting
for ax, title, note in zip(axes, titles, notes):
    ax.set_title(title, fontsize=10, pad=6)
    ax.set_xlabel("X", fontsize=9)
    ax.annotate(note, xy=(0.04, 0.05), xycoords='axes fraction',
                fontsize=7.5, color='#333333',
                bbox=dict(boxstyle='round,pad=0.3', fc='white', alpha=0.7))
    ax.grid(True, alpha=0.2)
    ax.spines[['top', 'right']].set_visible(False)

axes[0].set_ylabel("Y", fontsize=9)

# Group legend on last panel
handles = [Line2D([0], [0], marker='o', color='w', markerfacecolor=colors[g],
                  markersize=7, label=f'Group {g+1}') for g in range(n_groups)]
axes[3].legend(handles=handles, fontsize=8, loc='upper left', framealpha=0.7)

fig.suptitle("Comparing Panel Data Models", fontsize=13)
fig.text(0.01, 0.01, "Note: generated data, illustration for 'Introduction to Longitudinal Data Analysis with R' workshop, Jarnach, 2026.",
         ha='left', fontsize=7.5, color='#555555', style='italic')
plt.tight_layout()
plt.subplots_adjust(top=0.84, bottom=0.14)
plt.savefig("fig/panel_models.png", dpi=150, bbox_inches='tight')
plt.show()

# ── Three-panel version (OLS, FE, RE — no Mixed Effects) ───────────────────
fig3, axes3 = plt.subplots(1, 3, figsize=(15, 5.5), sharey=True)

titles3 = titles[:3]
notes3  = notes[:3]

for ax in axes3:
    for g in range(n_groups):
        ax.scatter(xs[g], ys[g], color=colors[g], alpha=0.55, s=22, zorder=2)

# Panel 0 — Pooled OLS
axes3[0].plot(x_full, np.polyval(ols_coef, x_full), 'k-', lw=2.5, label='OLS')

# Panel 1 — Fixed Effects
for g in range(n_groups):
    xg = [xs[g].min(), xs[g].max()]
    axes3[1].plot(xg, [fe_ints[g] + fe_slope * xi for xi in xg],
                  color=colors[g], lw=2.5)

# Panel 2 — Random Effects
for g in range(n_groups):
    xg = [xs[g].min(), xs[g].max()]
    axes3[2].plot(xg, [re_ints[g] + re_slope * xi for xi in xg],
                  color=colors[g], lw=2.5)

for ax, title, note in zip(axes3, titles3, notes3):
    ax.set_title(title, fontsize=10, pad=6)
    ax.set_xlabel("X", fontsize=9)
    ax.annotate(note, xy=(0.04, 0.05), xycoords='axes fraction',
                fontsize=7.5, color='#333333',
                bbox=dict(boxstyle='round,pad=0.3', fc='white', alpha=0.7))
    ax.grid(True, alpha=0.2)
    ax.spines[['top', 'right']].set_visible(False)

axes3[0].set_ylabel("Y", fontsize=9)

handles3 = [Line2D([0], [0], marker='o', color='w', markerfacecolor=colors[g],
                   markersize=7, label=f'Group {g+1}') for g in range(n_groups)]
axes3[2].legend(handles=handles3, fontsize=8, loc='upper left', framealpha=0.7)

fig3.suptitle("Comparing Panel Data Models", fontsize=13)
fig3.text(0.01, 0.01, "Note: generated data, illustration for 'Introduction to Longitudinal Data Analysis with R' workshop, Jarnach, 2026.",
          ha='left', fontsize=7.5, color='#555555', style='italic')
plt.tight_layout()
plt.subplots_adjust(top=0.84, bottom=0.14)
plt.savefig("fig/panel_models_3.png", dpi=150, bbox_inches='tight')
plt.show()

