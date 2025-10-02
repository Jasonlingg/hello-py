import json
import math
import re
import csv
import time
import random
from contextlib import redirect_stdout
from io import StringIO
from typing import Any, Callable, TypedDict, Dict, List
from collections import Counter, defaultdict

from anthropic import Anthropic
from anthropic.types import MessageParam, ToolUnionParam


class PythonExpressionToolResult(TypedDict):
    result: Any
    error: str | None


class SubmitAnswerToolResult(TypedDict):
    answer: Any
    submitted: bool


def python_expression_tool(expression: str) -> PythonExpressionToolResult:
    """
    Tool that evaluates Python expressions using exec with a restricted global scope.
    Use print(...) to produce output; captured stdout is returned as result.
    """
    try:
        safe_globals = {
            "__builtins__": {},
            "math": math,
            "abs": abs,
            "min": min,
            "max": max,
            "sum": sum,
            "len": len,
            "range": range,
            "round": round,
            "int": int,
            "float": float,
            "str": str,
            "list": list,
            "dict": dict,
            "tuple": tuple,
            "set": set,
            "print": print,
            "re": re,
            "csv": csv,
            "time": time,
            "random": random,
            "Counter": Counter,
            "defaultdict": defaultdict,
        }
        stdout = StringIO()
        with redirect_stdout(stdout):
            exec(expression, safe_globals, {})
        return {"result": stdout.getvalue(), "error": None}
    except KeyboardInterrupt:
        raise
    except Exception as e:
        return {"result": None, "error": str(e)}


def submit_answer_tool(answer: Any) -> SubmitAnswerToolResult:
    """
    Tool for submitting the final answer.
    """
    return {"answer": answer, "submitted": True}


def run_agent_loop(
    prompt: str,
    tools: list[ToolUnionParam],
    tool_handlers: dict[str, Callable],
    max_steps: int = 5,
    model: str = "claude-3-5-haiku-latest",
    verbose: bool = True,
) -> Any | None:
    """
    Runs an agent loop with the given prompt and tools.

    Args:
        prompt: The initial prompt for the agent
        tools: List of tool definitions for Anthropic API
        tool_handlers: Dictionary mapping tool names to their handler functions
        max_steps: Maximum number of steps before stopping (default 5)
        model: The Anthropic model to use
        verbose: Whether to print detailed output (default True)

    Returns:
        The submitted answer if submit_answer was called, otherwise None
    """
    client = Anthropic()
    messages: list[MessageParam] = [{"role": "user", "content": prompt}]

    for step in range(max_steps):
        if verbose:
            print(f"\n=== Step {step + 1}/{max_steps} ===")

        response = client.messages.create(
            model=model, max_tokens=1000, tools=tools, messages=messages
        )

        has_tool_use = False
        tool_results = []
        submitted_answer = None

        for content in response.content:
            if content.type == "text":
                if verbose:
                    print(f"Assistant: {content.text}")
            elif content.type == "tool_use":
                has_tool_use = True
                tool_name = content.name

                if tool_name in tool_handlers:
                    if verbose:
                        print(f"Using tool: {tool_name}")

                    handler = tool_handlers[tool_name]
                    tool_input = content.input

                    if tool_name == "python_expression":
                        if not isinstance(tool_input, dict) or "expression" not in tool_input:
                            if verbose:
                                print(f"Invalid python_expression input: {tool_input}")
                            result = {"result": None, "error": "Invalid input format for python_expression"}
                        else:
                            if verbose:
                                print("\nInput:")
                                print("```")
                                for line in tool_input["expression"].split("\n"):
                                    print(f"{line}")
                                print("```")
                            result = handler(tool_input["expression"])
                            if verbose:
                                print("\nOutput:")
                                print("```")
                                print(result)
                                print("```")
                    elif tool_name == "submit_answer":
                        if not isinstance(tool_input, dict) or "answer" not in tool_input:
                            if verbose:
                                print(f"Invalid submit_answer input: {tool_input}")
                            result = {"answer": None, "submitted": False}
                        else:
                            result = handler(tool_input["answer"])
                            submitted_answer = result["answer"]
                    else:
                        # Generic handler call for other tools
                        if verbose:
                            print(f"\nTool input: {tool_input}")
                        result = (
                            handler(**tool_input)
                            if isinstance(tool_input, dict)
                            else handler(tool_input)
                        )
                        if verbose:
                            print(f"\nTool output: {result}")

                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": content.id,
                            "content": json.dumps(result),
                        }
                    )

        if has_tool_use:
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

            if submitted_answer is not None:
                if verbose:
                    print(f"\nAgent submitted answer: {submitted_answer}")
                return submitted_answer
        else:
            if verbose:
                print("\nNo tool use in response, ending loop.")
            break

    if verbose:
        print(f"\nReached maximum steps ({max_steps}) without submitting answer.")
    return None


def run_task(task_name: str, num_runs: int = 10, max_steps: int = 8, verbose_each: bool = False):
    """Run a specific task multiple times and report pass rate"""
    # Import the task module
    import importlib
    task_module = importlib.import_module(f"tasks.{task_name}")
    
    # Get task components
    prompt = task_module.get_prompt()
    tools = task_module.get_tools()
    tool_handlers = task_module.get_tool_handlers()
    grader = task_module.get_grader()
    
    successes = 0
    print(f"Running {task_name} {num_runs} times...")
    print("=" * 60)

    for i in range(num_runs):
        print(f"\n{'=' * 20} RUN {i + 1}/{num_runs} {'=' * 20}")

        result = run_agent_loop(
            prompt=prompt,
            tools=tools,
            tool_handlers=tool_handlers,
            max_steps=max_steps,
            verbose=verbose_each,
        )

        is_correct = grader(result)
        
        if is_correct:
            print(f"✓ Run {i + 1}: SUCCESS - Got {result}")
            successes += 1
        else:
            print(f"✗ Run {i + 1}: FAILURE - Got {result}")

    pass_rate = (successes / num_runs) * 100
    print(f"\n{'=' * 60}")
    print("Test Results:")
    print(f"  Passed: {successes}/{num_runs}")
    print(f"  Failed: {num_runs - successes}/{num_runs}")
    print(f"  Pass Rate: {pass_rate:.1f}%")
    print(f"{'=' * 60}")
    
    return pass_rate


