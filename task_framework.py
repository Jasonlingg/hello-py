import json
import math
import re
import csv
import time
import random
import statistics
import datetime
import logging
import concurrent.futures
from contextlib import redirect_stdout
from io import StringIO
from typing import Any, Callable, TypedDict, Dict, List
from collections import Counter, defaultdict

from anthropic import Anthropic
from anthropic.types import MessageParam, ToolUnionParam

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('task_execution.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


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
            "statistics": statistics,
            "datetime": datetime,
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
    run_id: int = 0,
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
        run_id: Identifier for this run (for logging)

    Returns:
        The submitted answer if submit_answer was called, otherwise None
    """
    logger.info(f"Starting agent loop {run_id} with model {model}")
    start_time = time.time()
    
    try:
        client = Anthropic()
        messages: list[MessageParam] = [{"role": "user", "content": prompt}]

        for step in range(max_steps):
            if verbose:
                print(f"\n=== Step {step + 1}/{max_steps} ===")

            logger.debug(f"Run {run_id} - Step {step + 1}: Making API call")
            api_start = time.time()
            
            # Add small delay to avoid rate limiting
            if run_id > 1:
                time.sleep(0.5)  # 500ms delay between parallel requests
            
            try:
                response = client.messages.create(
                    model=model, max_tokens=1000, tools=tools, messages=messages
                )
            except Exception as e:
                if "429" in str(e) or "rate limit" in str(e).lower():
                    logger.warning(f"Run {run_id} - Step {step + 1}: Rate limited, waiting 2s")
                    time.sleep(2)
                    response = client.messages.create(
                        model=model, max_tokens=1000, tools=tools, messages=messages
                    )
                else:
                    raise e
            
            api_time = time.time() - api_start
            logger.debug(f"Run {run_id} - Step {step + 1}: API call took {api_time:.2f}s")

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
                    total_time = time.time() - start_time
                    logger.info(f"Run {run_id} SUCCESS: Completed in {total_time:.2f}s with answer: {submitted_answer}")
                    return submitted_answer
            else:
                if verbose:
                    print("\nNo tool use in response, ending loop.")
                logger.warning(f"Run {run_id} WARNING: No tool use in response, ending loop")
                break

        if verbose:
            print(f"\nReached maximum steps ({max_steps}) without submitting answer.")
        total_time = time.time() - start_time
        logger.warning(f"Run {run_id} FAILURE: Reached max steps ({max_steps}) in {total_time:.2f}s")
        return None
    
    except Exception as e:
        total_time = time.time() - start_time
        logger.error(f"Run {run_id} ERROR: Exception after {total_time:.2f}s - {str(e)}")
        return None


def run_single_task(task_name: str, run_id: int, prompt: str, tools: list, tool_handlers: dict, grader: callable, max_steps: int, verbose_each: bool):
    """Run a single task instance"""
    logger.info(f"Starting task {task_name} run {run_id}")
    
    result = run_agent_loop(
        prompt=prompt,
        tools=tools,
        tool_handlers=tool_handlers,
        max_steps=max_steps,
        verbose=verbose_each,
        run_id=run_id,
    )
    
    is_correct = grader(result)
    
    if is_correct:
        logger.info(f"Task {task_name} run {run_id}: SUCCESS - {result}")
        return True, result
    else:
        logger.warning(f"Task {task_name} run {run_id}: FAILURE - {result}")
        return False, result


def run_task(task_name: str, num_runs: int = 10, max_steps: int = 8, verbose_each: bool = False, parallel: bool = True, max_workers: int = 2):
    """Run a specific task multiple times and report pass rate"""
    logger.info(f"Starting task {task_name} with {num_runs} runs (parallel={parallel})")
    
    # Import the task module
    import importlib
    task_module = importlib.import_module(f"tasks.{task_name}")
    
    # Get task components
    prompt = task_module.get_prompt()
    tools = task_module.get_tools()
    tool_handlers = task_module.get_tool_handlers()
    grader = task_module.get_grader()
    
    successes = 0
    results = []
    print(f"Running {task_name} {num_runs} times...")
    print("=" * 60)
    
    start_time = time.time()

    if parallel and num_runs > 1:
        # Parallel execution
        logger.info(f"Running {num_runs} tasks in parallel with {max_workers} workers")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for i in range(num_runs):
                future = executor.submit(
                    run_single_task, 
                    task_name, i + 1, prompt, tools, tool_handlers, grader, max_steps, verbose_each
                )
                futures.append(future)
            
            # Collect results
            for i, future in enumerate(futures):
                try:
                    is_correct, result = future.result(timeout=300)  # 5 minute timeout per task
                    results.append((i + 1, is_correct, result))
                    
                    if is_correct:
                        print(f"✓ Run {i + 1}: SUCCESS - Got {result}")
                        successes += 1
                    else:
                        print(f"✗ Run {i + 1}: FAILURE - Got {result}")
                        
                except concurrent.futures.TimeoutError:
                    logger.error(f"Task {task_name} run {i + 1}: TIMEOUT")
                    print(f"✗ Run {i + 1}: TIMEOUT")
                    results.append((i + 1, False, None))
                except Exception as e:
                    logger.error(f"Task {task_name} run {i + 1}: EXCEPTION - {str(e)}")
                    print(f"✗ Run {i + 1}: EXCEPTION - {str(e)}")
                    results.append((i + 1, False, None))
    else:
        # Sequential execution
        logger.info(f"Running {num_runs} tasks sequentially")
        
        for i in range(num_runs):
            print(f"\n{'=' * 20} RUN {i + 1}/{num_runs} {'=' * 20}")
            
            is_correct, result = run_single_task(
                task_name, i + 1, prompt, tools, tool_handlers, grader, max_steps, verbose_each
            )
            
            results.append((i + 1, is_correct, result))
            
            if is_correct:
                print(f"✓ Run {i + 1}: SUCCESS - Got {result}")
                successes += 1
            else:
                print(f"✗ Run {i + 1}: FAILURE - Got {result}")

    total_time = time.time() - start_time
    pass_rate = (successes / num_runs) * 100
    
    logger.info(f"Task {task_name} completed: {successes}/{num_runs} passed ({pass_rate:.1f}%) in {total_time:.2f}s")
    
    print(f"\n{'=' * 60}")
    print("Test Results:")
    print(f"  Passed: {successes}/{num_runs}")
    print(f"  Failed: {num_runs - successes}/{num_runs}")
    print(f"  Pass Rate: {pass_rate:.1f}%")
    print(f"  Total Time: {total_time:.2f}s")
    print(f"  Parallel: {parallel}")
    print(f"{'=' * 60}")
    
    return pass_rate


