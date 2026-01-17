"""Run full evaluation with progress monitoring."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from src.evaluation.ablation_runner import AblationRunner

print("="*80)
print("BIST ANALYSIS AGENT - FULL EVALUATION")
print("="*80)
print(f"\nConfiguration: 7 configs × 3 runs × 25 queries = 525 total executions")
print(f"Estimated time: 30-60 minutes")
print(f"Results will be saved to: results/ablation_results_[timestamp].json\n")

# Run without W&B to avoid hanging
runner = AblationRunner(use_wandb=False)

print("Starting evaluation...\n")

results = runner.run_ablation(
    test_queries=config.TEST_QUERIES,
    num_runs=config.NUM_ABLATION_RUNS
)

print("\n" + "="*80)
print("EVALUATION COMPLETE!")
print("="*80)

# Print summary
for config_name, metrics in sorted(results.items()):
    print(f"\n{config_name.upper()}:")
    for key in ['ragas_faithfulness_mean', 'judge_overall_mean', 'tool_f1_mean', 'success_rate_mean']:
        if key in metrics:
            value = metrics[key]
            print(f"  {key:30s}: {value:.3f}")

print("\n" + "="*80)
print("Results saved. Run 'python scripts/create_figures.py' to generate visualizations.")
print("="*80)
