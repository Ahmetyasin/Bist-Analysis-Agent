"""Main evaluation script."""
import sys
import os

# Add parent directory to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config

from .ablation_runner import AblationRunner


def run_full_evaluation():
    """Run complete evaluation suite."""
    print("="*60)
    print("BIST Analysis Agent - Full Evaluation Suite")
    print("="*60)

    # Get test queries
    test_queries = config.TEST_QUERIES
    print(f"\nLoaded {len(test_queries)} test queries")

    # Initialize runner
    runner = AblationRunner(use_wandb=True)

    # Run ablation study
    print("\nStarting ablation study...")
    print(f"Configurations: {list(runner.CONFIGURATIONS.keys())}")
    print(f"Runs per config: {config.NUM_ABLATION_RUNS}")

    results = runner.run_ablation(
        test_queries=test_queries,
        num_runs=config.NUM_ABLATION_RUNS
    )

    # Print summary
    print("\n" + "="*60)
    print("EVALUATION SUMMARY")
    print("="*60)

    for config_name, metrics in results.items():
        print(f"\n{config_name}:")
        for metric, value in sorted(metrics.items()):
            if isinstance(value, float):
                print(f"  {metric}: {value:.3f}")

    return results


if __name__ == "__main__":
    run_full_evaluation()
