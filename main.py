"""Main entry point for BIST Analysis Agent."""
import argparse
import sys
import os

# Ensure the project root is in the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    parser = argparse.ArgumentParser(description='BIST Stock Analysis Agent')
    parser.add_argument('--setup', action='store_true', help='Setup data and indexes')
    parser.add_argument('--query', type=str, help='Run single query')
    parser.add_argument('--interactive', action='store_true', help='Interactive mode')
    parser.add_argument('--evaluate', action='store_true', help='Run evaluation suite')

    args = parser.parse_args()

    if args.setup:
        from scripts.setup_data import main as setup_main
        setup_main()

    elif args.query:
        from src.agent.graph import run_agent
        result = run_agent(args.query, verbose=True)
        print("\n" + "="*50)
        print(result.get("final_report", "No report generated"))
        print("="*50)

    elif args.interactive:
        from scripts.run_agent import main as agent_main
        agent_main()

    elif args.evaluate:
        from src.evaluation.run_evaluation import run_full_evaluation
        run_full_evaluation()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
