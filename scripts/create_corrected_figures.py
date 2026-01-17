"""Create CORRECTED publication-quality figures for DSAI 585 report.

Key fixes:
1. RAGAS comparison shows ONLY RAG-enabled configs (5, not 7)
2. Ablation impact shows MEANINGFUL comparisons (few-shot vs zero-shot, with-tools vs without)
3. NO tautological "RAG vs no-RAG" faithfulness comparison
"""
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

# Set publication style
plt.style.use('seaborn-v0_8-paper')
sns.set_palette("husl")
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 150
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9

# Color palette
COLORS = {
    'primary': '#2E86AB',      # Blue for faithfulness
    'secondary': '#F18F01',    # Orange for answer relevancy
    'success': '#06A77D',      # Green for judge scores
    'accent': '#A23B72',       # Purple for accents
    'danger': '#D62246',       # Red for negative
    'neutral': '#6C757D'
}

# Create output directory
output_dir = Path("figures")
output_dir.mkdir(exist_ok=True)

print("Creating CORRECTED publication-quality figures...")
print()

# ============================================================================
# Figure 1: RAGAS Comparison - RAG-ENABLED CONFIGS ONLY (FIXED)
# ============================================================================
print("1. Creating ragas_comparison.png (RAG-enabled only)...")

# ONLY RAG-enabled configurations
rag_configs = ['full_system', 'zero_shot', 'no_tools', 'one_shot', 'rag_only']
rag_labels = ['Full System\n(3-shot)', 'Zero-Shot', 'No Tools', 'One-Shot', 'RAG Only']

faithfulness = [0.120, 0.113, 0.111, 0.105, 0.104]
faithfulness_std = [0.003, 0.018, 0.014, 0.002, 0.003]

answer_rel = [0.724, 0.685, 0.688, 0.693, 0.702]
answer_rel_std = [0.040, 0.024, 0.021, 0.030, 0.045]

x = np.arange(len(rag_configs))
width = 0.35

fig, ax = plt.subplots(figsize=(10, 6))

bars1 = ax.bar(x - width/2, faithfulness, width, label='Faithfulness',
               color=COLORS['primary'], yerr=faithfulness_std, capsize=4, alpha=0.9)
bars2 = ax.bar(x + width/2, answer_rel, width, label='Answer Relevancy',
               color=COLORS['secondary'], yerr=answer_rel_std, capsize=4, alpha=0.9)

ax.set_xlabel('Configuration', fontweight='bold', fontsize=11)
ax.set_ylabel('Score', fontweight='bold', fontsize=11)
ax.set_title('RAGAS Metrics: RAG-Enabled Configurations', fontsize=13, fontweight='bold', pad=15)
ax.set_xticks(x)
ax.set_xticklabels(rag_labels, fontsize=9)
ax.legend(loc='lower right', framealpha=0.95)
ax.set_ylim(0, 0.85)
ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.5)

# Add note
ax.text(0.5, 0.02, 'Note: Non-RAG configurations excluded (faithfulness requires retrieved context)',
        transform=ax.transAxes, ha='center', fontsize=8, style='italic', color='gray')

plt.tight_layout()
plt.savefig(output_dir / "ragas_comparison.png", dpi=150, bbox_inches='tight')
plt.close()
print("  ✓ Saved ragas_comparison.png (5 RAG-enabled configs)")

# ============================================================================
# Figure 2: Judge Heatmap - ALL 7 CONFIGS
# ============================================================================
print("2. Creating judge_heatmap.png (all 7 configs)...")

all_configs = ['full_system', 'rag_only', 'no_tools', 'zero_shot', 'one_shot', 'no_rag', 'tools_only']
all_labels = ['Full System', 'RAG Only', 'No Tools', 'Zero-Shot', 'One-Shot', 'No RAG', 'Tools Only']

dimensions = ['Data\nAccuracy', 'Analysis\nDepth', 'Reasoning\nQuality',
              'Investor\nUsefulness', 'Presentation\nQuality']

heatmap_data = [
    [3.43, 2.85, 3.00, 2.72, 4.00],  # Full System
    [3.51, 2.89, 3.01, 2.75, 3.99],  # RAG Only
    [3.32, 2.83, 3.00, 2.71, 3.99],  # No Tools
    [3.31, 2.84, 2.97, 2.60, 4.00],  # Zero-Shot
    [3.45, 2.83, 3.04, 2.76, 4.01],  # One-Shot
    [3.43, 2.81, 3.03, 2.73, 4.00],  # No RAG
    [3.44, 2.88, 3.09, 2.76, 4.01],  # Tools Only
]

fig, ax = plt.subplots(figsize=(10, 7))
im = ax.imshow(heatmap_data, cmap='RdYlGn', aspect='auto', vmin=2.5, vmax=4.2)

# Set ticks and labels
ax.set_xticks(np.arange(len(dimensions)))
ax.set_yticks(np.arange(len(all_configs)))
ax.set_xticklabels(dimensions, fontsize=9)
ax.set_yticklabels(all_labels, fontsize=10)

# Add colorbar
cbar = plt.colorbar(im, ax=ax)
cbar.set_label('Score (1-5)', rotation=270, labelpad=20, fontweight='bold', fontsize=10)

# Add text annotations
for i in range(len(all_configs)):
    for j in range(len(dimensions)):
        text = ax.text(j, i, f'{heatmap_data[i][j]:.2f}',
                      ha="center", va="center", color="black", fontsize=9, fontweight='bold')

ax.set_title('LLM-as-Judge Scores by Configuration and Dimension',
             fontsize=13, fontweight='bold', pad=15)

plt.tight_layout()
plt.savefig(output_dir / "judge_heatmap.png", dpi=150, bbox_inches='tight')
plt.close()
print("  ✓ Saved judge_heatmap.png (all 7 configs)")

# ============================================================================
# Figure 3: Ablation Impact - MEANINGFUL COMPARISONS (FIXED)
# ============================================================================
print("3. Creating ablation_impact.png (meaningful comparisons)...")

# Full system baseline: faithfulness=0.120, judge=3.20
# Comparisons within RAG-enabled configs:
# vs Zero-Shot: faith 0.113 → 0.120 = +6.2%, judge 3.14 → 3.20 = +1.9%
# vs RAG-Only: faith 0.104 → 0.120 = +15.4%, judge 3.23 → 3.20 = -0.9%
# vs No-Tools: faith 0.111 → 0.120 = +8.1%, judge 3.17 → 3.20 = +0.9%

comparisons = ['Few-Shot\nvs Zero-Shot', 'With Tools\nvs RAG-Only', 'With Tools\nvs No-Tools']
comparison_labels_short = ['Prompting\nImpact', 'Tool\nImpact', 'Tool\nImpact\n(alt)']

faith_changes = [6.2, 15.4, 8.1]
judge_changes = [1.9, -0.9, 0.9]

x = np.arange(len(comparisons))
width = 0.35

fig, ax = plt.subplots(figsize=(10, 6))

bars1 = ax.bar(x - width/2, faith_changes, width, label='Faithfulness Change (%)',
               color=COLORS['primary'], alpha=0.9)
bars2 = ax.bar(x + width/2, judge_changes, width, label='Judge Score Change (%)',
               color=COLORS['success'], alpha=0.9)

# Add zero line
ax.axhline(y=0, color='black', linestyle='-', linewidth=1)

# Add value labels on bars
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:+.1f}%',
                   xy=(bar.get_x() + bar.get_width() / 2, height),
                   xytext=(0, 3 if height > 0 else -15),
                   textcoords="offset points",
                   ha='center', va='bottom' if height > 0 else 'top',
                   fontsize=9, fontweight='bold')

ax.set_xlabel('Component Comparison', fontweight='bold', fontsize=11)
ax.set_ylabel('% Change (Full System as Baseline)', fontweight='bold', fontsize=11)
ax.set_title('Component Impact: Improvement Over Ablated Versions',
             fontsize=13, fontweight='bold', pad=15)
ax.set_xticks(x)
ax.set_xticklabels(comparisons, fontsize=9)
ax.legend(loc='upper left', framealpha=0.95)
ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.5)
ax.set_ylim(-5, 18)

# Add note
ax.text(0.5, 0.02, 'Positive values indicate full_system (3-shot + tools + RAG) outperforms ablated version',
        transform=ax.transAxes, ha='center', fontsize=8, style='italic', color='gray')

plt.tight_layout()
plt.savefig(output_dir / "ablation_impact.png", dpi=150, bbox_inches='tight')
plt.close()
print("  ✓ Saved ablation_impact.png (meaningful comparisons)")

# ============================================================================
# Figure 4: Category Performance
# ============================================================================
print("4. Creating category_performance.png...")

categories = ['Fundamental', 'Technical', 'Comprehensive', 'Macro', 'Other']
faithfulness_cat = [0.13, 0.11, 0.14, 0.12, 0.12]
judge_cat = [3.30, 3.10, 3.00, 3.15, 3.20]

x = np.arange(len(categories))
width = 0.35

fig, ax = plt.subplots(figsize=(10, 6))

# Scale faithfulness to similar range for visualization
faith_scaled = [f * 25 for f in faithfulness_cat]

bars1 = ax.bar(x - width/2, faith_scaled, width, label='Faithfulness (×25)',
               color=COLORS['primary'], alpha=0.8)
bars2 = ax.bar(x + width/2, judge_cat, width, label='Judge Overall',
               color=COLORS['secondary'], alpha=0.8)

# Add value labels showing ACTUAL faithfulness values
for bar, val in zip(bars1, faithfulness_cat):
    height = bar.get_height()
    ax.annotate(f'{val:.2f}',
               xy=(bar.get_x() + bar.get_width() / 2, height),
               xytext=(0, 3),
               textcoords="offset points",
               ha='center', va='bottom',
               fontsize=9, fontweight='bold')

# Add judge values
for bar, val in zip(bars2, judge_cat):
    height = bar.get_height()
    ax.annotate(f'{val:.2f}',
               xy=(bar.get_x() + bar.get_width() / 2, height),
               xytext=(0, 3),
               textcoords="offset points",
               ha='center', va='bottom',
               fontsize=9, fontweight='bold')

ax.set_xlabel('Query Category', fontweight='bold', fontsize=11)
ax.set_ylabel('Score', fontweight='bold', fontsize=11)
ax.set_title('Performance by Query Category (Full System)',
             fontsize=13, fontweight='bold', pad=15)
ax.set_xticks(x)
ax.set_xticklabels(categories, fontsize=9)
ax.legend(loc='upper right', framealpha=0.95)
ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.5)

# Add note highlighting comprehensive > technical
ax.text(0.5, 0.02, 'Comprehensive queries show 27% higher faithfulness than Technical (0.14 vs 0.11)',
        transform=ax.transAxes, ha='center', fontsize=8, style='italic', color=COLORS['success'],
        fontweight='bold')

plt.tight_layout()
plt.savefig(output_dir / "category_performance.png", dpi=150, bbox_inches='tight')
plt.close()
print("  ✓ Saved category_performance.png")

# ============================================================================
# Figure 5: Query Distribution
# ============================================================================
print("5. Creating query_distribution.png...")

categories_dist = {
    'Fundamental': 5,
    'Technical': 5,
    'Comprehensive': 5,
    'Macroeconomic': 3,
    'Comparison': 2,
    'Sector': 2,
    'Portfolio': 2,
    'Risk': 1
}

fig, ax = plt.subplots(figsize=(8, 6))
colors_pie = sns.color_palette("husl", len(categories_dist))

wedges, texts, autotexts = ax.pie(
    categories_dist.values(),
    labels=categories_dist.keys(),
    autopct='%1.1f%%',
    startangle=90,
    colors=colors_pie,
    textprops={'fontsize': 10}
)

# Make percentage text bold and white
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
    autotext.set_fontsize(9)

# Make labels bold
for text in texts:
    text.set_fontweight('bold')

ax.set_title('Test Query Distribution (n=25)', fontsize=13, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig(output_dir / "query_distribution.png", dpi=150, bbox_inches='tight')
plt.close()
print("  ✓ Saved query_distribution.png")

# ============================================================================
# Summary
# ============================================================================
print()
print("="*80)
print("CORRECTED Figures Created Successfully!")
print("="*80)
print()
print("Output location: figures/")
print()
print("Key corrections applied:")
print("  1. ✓ ragas_comparison.png - Shows ONLY 5 RAG-enabled configs")
print("  2. ✓ judge_heatmap.png - Shows all 7 configs (judge applicable to all)")
print("  3. ✓ ablation_impact.png - Shows MEANINGFUL comparisons:")
print("      • Few-shot vs Zero-shot (+6.2% faithfulness)")
print("      • With-tools vs RAG-only (+15.4% faithfulness)")
print("      • With-tools vs No-tools (+8.1% faithfulness)")
print("  4. ✓ category_performance.png - Highlights Comprehensive > Technical by 27%")
print("  5. ✓ query_distribution.png - Standard pie chart")
print()
print("Files created:")
for f in ['ragas_comparison.png', 'judge_heatmap.png', 'ablation_impact.png',
          'category_performance.png', 'query_distribution.png']:
    filepath = output_dir / f
    size = filepath.stat().st_size / 1024 if filepath.exists() else 0
    print(f"  • {f:<30} {size:>6.0f} KB")
print()
print("All figures:")
print("  - 150 DPI (publication quality)")
print("  - Clean, professional style")
print("  - Consistent color palette")
print("  - NO tautological RAG vs no-RAG comparisons")
print("  - Ready for LaTeX inclusion at 0.85\\textwidth")
print()
