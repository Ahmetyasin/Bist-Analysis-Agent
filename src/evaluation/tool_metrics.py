"""Tool usage evaluation metrics."""
from typing import List, Dict


class ToolMetrics:
    """Evaluate tool usage quality."""

    def evaluate(
        self,
        tools_called: List[str],
        expected_tools: List[str],
        tool_outputs: Dict[str, any] = None
    ) -> Dict[str, float]:
        """
        Evaluate tool selection and usage.

        Args:
            tools_called: Tools that were called
            expected_tools: Tools that should have been called
            tool_outputs: Optional outputs from tools

        Returns:
            Dictionary of metrics
        """
        results = {}

        # Tool Selection Precision: % of called tools that were necessary
        if tools_called:
            correct_calls = len(set(tools_called) & set(expected_tools))
            results["tool_precision"] = correct_calls / len(tools_called)
        else:
            results["tool_precision"] = 0.0 if expected_tools else 1.0

        # Tool Selection Recall: % of necessary tools that were called
        if expected_tools:
            correct_calls = len(set(tools_called) & set(expected_tools))
            results["tool_recall"] = correct_calls / len(expected_tools)
        else:
            results["tool_recall"] = 1.0 if not tools_called else 0.0

        # Tool F1 Score
        if results["tool_precision"] + results["tool_recall"] > 0:
            results["tool_f1"] = (
                2 * results["tool_precision"] * results["tool_recall"] /
                (results["tool_precision"] + results["tool_recall"])
            )
        else:
            results["tool_f1"] = 0.0

        # Tool Output Validity
        if tool_outputs:
            valid_count = 0
            for tool_name, output in tool_outputs.items():
                if self._is_valid_output(tool_name, output):
                    valid_count += 1
            results["tool_output_validity"] = valid_count / len(tool_outputs)
        else:
            results["tool_output_validity"] = 1.0

        return results

    def _is_valid_output(self, tool_name: str, output: any) -> bool:
        """Check if tool output is valid."""
        if output is None:
            return False

        if isinstance(output, dict):
            if output.get("error"):
                return False
            return True

        if isinstance(output, str):
            return len(output) > 10

        return True
