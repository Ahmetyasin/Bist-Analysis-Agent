"""Ablation study runner."""
from typing import List, Dict
import json
from datetime import datetime
from pathlib import Path
import sys
import os

# Add parent directory to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config

import wandb
from .ragas_metrics import RAGASEvaluator
from .llm_judge import LLMJudge
from .tool_metrics import ToolMetrics


class AblationRunner:
    """Run ablation studies across configurations."""

    CONFIGURATIONS = {
        "full_system": {
            "use_rag": True,
            "use_tools": True,
            "prompting": "3-shot",
            "description": "Full system with all components"
        },
        "no_rag": {
            "use_rag": False,
            "use_tools": True,
            "prompting": "3-shot",
            "description": "Without RAG retrieval"
        },
        "no_tools": {
            "use_rag": True,
            "use_tools": False,
            "prompting": "3-shot",
            "description": "Without financial data tools"
        },
        "rag_only": {
            "use_rag": True,
            "use_tools": False,
            "prompting": "0-shot",
            "description": "RAG only, no tools"
        },
        "tools_only": {
            "use_rag": False,
            "use_tools": True,
            "prompting": "0-shot",
            "description": "Tools only, no RAG"
        },
        "zero_shot": {
            "use_rag": True,
            "use_tools": True,
            "prompting": "0-shot",
            "description": "Full system with zero-shot prompting"
        },
        "one_shot": {
            "use_rag": True,
            "use_tools": True,
            "prompting": "1-shot",
            "description": "Full system with one-shot prompting"
        }
    }

    def __init__(self, use_wandb: bool = True):
        self.ragas_eval = RAGASEvaluator()
        self.judge = LLMJudge()
        self.tool_metrics = ToolMetrics()
        self.use_wandb = use_wandb

        if use_wandb:
            try:
                wandb.login(key=config.WANDB_API_KEY)
            except Exception as e:
                print(f"Warning: Could not login to wandb: {e}")
                self.use_wandb = False

    def run_ablation(
        self,
        test_queries: List[Dict],
        num_runs: int = 3
    ) -> Dict[str, Dict]:
        """
        Run full ablation study.

        Args:
            test_queries: List of test query dictionaries
            num_runs: Number of runs per configuration

        Returns:
            Results for all configurations
        """
        all_results = {}

        for config_name, config_params in self.CONFIGURATIONS.items():
            print(f"\n{'='*50}")
            print(f"Running configuration: {config_name}")
            print(f"Description: {config_params['description']}")
            print(f"{'='*50}")

            config_results = []

            for run_idx in range(num_runs):
                print(f"\nRun {run_idx + 1}/{num_runs}")

                if self.use_wandb:
                    try:
                        wandb.init(
                            project=config.WANDB_PROJECT,
                            name=f"{config_name}_run{run_idx + 1}",
                            config=config_params,
                            reinit=True
                        )
                    except Exception as e:
                        print(f"Warning: Could not init wandb: {e}")

                run_results = self._run_single_config(
                    config_name,
                    config_params,
                    test_queries
                )

                config_results.append(run_results)

                if self.use_wandb:
                    try:
                        wandb.log(run_results["aggregate"])
                        wandb.finish()
                    except:
                        pass

            # Aggregate across runs
            all_results[config_name] = self._aggregate_runs(config_results)

        # Save results
        self._save_results(all_results)

        return all_results

    def _run_single_config(
        self,
        config_name: str,
        config_params: Dict,
        test_queries: List[Dict]
    ) -> Dict:
        """Run a single configuration on all test queries."""
        from src.agent.graph import run_agent

        query_results = []

        for query_data in test_queries:
            query = query_data["query"]
            expected_tools = query_data.get("expected_tools", [])

            print(f"  Query: {query[:50]}...")

            try:
                # Run agent (with modified config if needed)
                result = run_agent(query, verbose=False)

                # If config disables RAG or tools, simulate that
                if not config_params["use_rag"]:
                    result["rag_context"] = None
                    result["rag_sources"] = []

                if not config_params["use_tools"]:
                    result["stock_data"] = None
                    result["macro_data"] = None
                    result["technical_data"] = None
                    result["portfolio_data"] = None

                # Evaluate
                eval_result = self._evaluate_result(
                    query=query,
                    result=result,
                    expected_tools=expected_tools
                )

                query_results.append({
                    "query_id": query_data["id"],
                    "query": query,
                    "query_type": query_data.get("type"),
                    **eval_result
                })

            except Exception as e:
                print(f"    Error: {e}")
                query_results.append({
                    "query_id": query_data["id"],
                    "query": query,
                    "error": str(e)
                })

        # Aggregate query results
        aggregate = self._aggregate_query_results(query_results)

        return {
            "config": config_name,
            "query_results": query_results,
            "aggregate": aggregate
        }

    def _evaluate_result(
        self,
        query: str,
        result: Dict,
        expected_tools: List[str]
    ) -> Dict:
        """Evaluate a single result."""
        response = result.get("final_report", "")
        contexts = [result.get("rag_context", "")] if result.get("rag_context") else []
        tools_called = result.get("tools_called", [])

        # RAGAS metrics
        ragas_scores = self.ragas_eval.evaluate(
            query=query,
            response=response,
            contexts=contexts
        )

        # LLM Judge scores
        rag_sources = result.get("rag_sources") or []
        sources_str = "\n".join([f"- {s}" for s in rag_sources if isinstance(s, str)])
        if not sources_str and rag_sources:
            sources_str = "\n".join([f"- {s.get('source', str(s))}" for s in rag_sources])
        judge_scores = self.judge.evaluate(
            query=query,
            response=response,
            sources=sources_str
        )

        # Tool metrics
        tool_scores = self.tool_metrics.evaluate(
            tools_called=tools_called,
            expected_tools=expected_tools,
            tool_outputs={
                "stock": result.get("stock_data"),
                "macro": result.get("macro_data"),
                "technical": result.get("technical_data"),
                "portfolio": result.get("portfolio_data")
            }
        )

        return {
            "ragas": ragas_scores,
            "judge": judge_scores,
            "tools": tool_scores,
            "step_count": result.get("step_count", 0)
        }

    def _aggregate_query_results(self, query_results: List[Dict]) -> Dict:
        """Aggregate results across queries."""
        valid_results = [r for r in query_results if "error" not in r]

        if not valid_results:
            return {"error": "All queries failed"}

        # RAGAS aggregation
        ragas_metrics = ["faithfulness", "answer_relevancy", "context_precision"]
        ragas_agg = {}
        for metric in ragas_metrics:
            values = [r["ragas"].get(metric, 0) for r in valid_results if "ragas" in r]
            if values:
                ragas_agg[f"ragas_{metric}"] = sum(values) / len(values)

        # Judge aggregation
        judge_dims = ["data_accuracy", "analysis_depth", "reasoning_quality",
                      "investor_usefulness", "presentation_quality"]
        judge_agg = {}
        for dim in judge_dims:
            values = [r["judge"][dim]["score"] for r in valid_results
                     if "judge" in r and dim in r["judge"]]
            if values:
                judge_agg[f"judge_{dim}"] = sum(values) / len(values)

        if [r["judge"].get("overall_score", 0) for r in valid_results if "judge" in r]:
            judge_agg["judge_overall"] = sum(
                r["judge"].get("overall_score", 0) for r in valid_results if "judge" in r
            ) / len(valid_results)

        # Tool aggregation
        tool_metrics = ["tool_precision", "tool_recall", "tool_f1", "tool_output_validity"]
        tool_agg = {}
        for metric in tool_metrics:
            values = [r["tools"].get(metric, 0) for r in valid_results if "tools" in r]
            if values:
                tool_agg[metric] = sum(values) / len(values)

        return {
            **ragas_agg,
            **judge_agg,
            **tool_agg,
            "success_rate": len(valid_results) / len(query_results),
            "avg_steps": sum(r.get("step_count", 0) for r in valid_results) / len(valid_results)
        }

    def _aggregate_runs(self, run_results: List[Dict]) -> Dict:
        """Aggregate results across runs (mean +/- std)."""
        import numpy as np

        all_metrics = {}

        for result in run_results:
            agg = result.get("aggregate", {})
            for metric, value in agg.items():
                if isinstance(value, (int, float)):
                    if metric not in all_metrics:
                        all_metrics[metric] = []
                    all_metrics[metric].append(value)

        final = {}
        for metric, values in all_metrics.items():
            final[f"{metric}_mean"] = np.mean(values)
            final[f"{metric}_std"] = np.std(values)

        return final

    def _save_results(self, results: Dict):
        """Save results to file."""
        output_path = config.RESULTS_DIR / f"ablation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"\nResults saved to: {output_path}")
