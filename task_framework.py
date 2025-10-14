import asyncio
import json
import time
from contextlib import redirect_stdout
from io import StringIO
from typing import Any, Callable, TypedDict

from anthropic import AsyncAnthropic
from anthropic.types import MessageParam, ToolUnionParam


class PythonExpressionToolResult(TypedDict):
    result: Any
    error: str | None


class SubmitAnswerToolResult(TypedDict):
    answer: Any
    submitted: bool


def python_expression_tool(expression: str) -> PythonExpressionToolResult:
    """
    Tool that evaluates Python expressions using exec.
    Use print(...) to emit output; stdout will be captured and returned.
    """
    try:
        namespace = {}
        stdout = StringIO()
        with redirect_stdout(stdout):
            exec(expression, namespace, namespace)
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


async def run_agent_loop(
    prompt: str,
    tools: list[ToolUnionParam],
    tool_handlers: dict[str, Callable[..., Any]],
    max_steps: int = 20,
    model: str = "claude-3-5-haiku-latest",
    verbose: bool = True,
) -> Any | None:
    """
    Runs an agent loop with the given prompt and tools.

    Args:
        prompt: The initial prompt for the agent
        tools: List of tool definitions for Anthropic API
        tool_handlers: Dictionary mapping tool names to their handler functions
        max_steps: Maximum number of steps before stopping (default 20)
        model: The Anthropic model to use
        verbose: Whether to print detailed output (default True)

    Returns:
        The submitted answer if submit_answer was called, otherwise None
    """
    client = AsyncAnthropic()
    messages: list[MessageParam] = [{"role": "user", "content": prompt}]

    for step in range(max_steps):
        if verbose:
            print(f"\n=== Step {step + 1}/{max_steps} ===")

        response = await client.messages.create(
            model=model, max_tokens=1000, tools=tools, messages=messages
        )

        # Track if we need to continue
        has_tool_use = False
        tool_results = []
        submitted_answer = None

        # Process the response
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

                    # Extract arguments based on tool
                    handler = tool_handlers[tool_name]
                    tool_input = content.input

                    # Call the appropriate tool handler
                    if tool_name == "python_expression":
                        if isinstance(tool_input, dict) and "expression" in tool_input:
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
                        else:
                            result = {"result": None, "error": "Invalid tool input"}
                    elif tool_name == "submit_answer":
                        if isinstance(tool_input, dict) and "answer" in tool_input:
                            result = handler(tool_input["answer"])
                            submitted_answer = result["answer"]
                        else:
                            result = {"answer": None, "submitted": False}
                    else:
                        # Generic handler call
                        result = (
                            handler(**tool_input)
                            if isinstance(tool_input, dict)
                            else handler(tool_input)
                        )

                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": content.id,
                            "content": json.dumps(result),
                        }
                    )

        # If we have tool uses, add them to the conversation
        if has_tool_use:
            messages.append({"role": "assistant", "content": response.content})

            messages.append({"role": "user", "content": tool_results})

            # If an answer was submitted, return it
            if submitted_answer is not None:
                if verbose:
                    print(f"\nAgent submitted answer: {submitted_answer}")
                return submitted_answer
        else:
            # No tool use, conversation might be complete
            if verbose:
                print("\nNo tool use in response, ending loop.")
            break

    if verbose:
        print(f"\nReached maximum steps ({max_steps}) without submitting answer.")
    return None


async def run_single_test(
    run_id: int,
    num_runs: int,
    prompt: str,
    tools: list[ToolUnionParam],
    tool_handlers: dict[str, Callable[..., Any]],
    grader: Callable[[Any], bool],
    verbose: bool = False,
) -> tuple[int, bool, Any]:
    if verbose:
        print(f"\n\n{'=' * 20} RUN {run_id}/{num_runs} {'=' * 20}")

    result = await run_agent_loop(
        prompt=prompt,
        tools=tools,
        tool_handlers=tool_handlers,
        max_steps=20,
        verbose=verbose,
    )

    # Debug: Show what the LLM actually returned
    print(f"🔍 Run {run_id} LLM result: {result}")
    
    grader_result = grader(result)
    
    # Handle different grader return types
    if isinstance(grader_result, dict):
        # Email triage returns dict with "passed" key
        success = grader_result.get("passed", False)
        score = grader_result.get("score", 0)
        print(f"🔍 Run {run_id} grader result: {success} (score: {score})")
    else:
        # Other tasks return boolean
        success = grader_result
        print(f"🔍 Run {run_id} grader result: {success}")

    if success:
        print(f"✓ Run {run_id}: SUCCESS - Got {result}")
    else:
        print(f"✗ Run {run_id}: FAILURE - Got {result}")

    return run_id, success, result


async def run_task_async(
    task_name: str,
    num_runs: int = 3,
    concurrent: bool = True,
    verbose: bool = False,
) -> float:
    """
    Run a task asynchronously and return pass rate.
    
    Args:
        task_name: Name of the task module
        num_runs: Number of runs to execute
        concurrent: Whether to run concurrently or sequentially
        verbose: Whether to show detailed output
        
    Returns:
        Pass rate as a percentage (0-100)
    """
    import importlib
    
    # Import the task module
    task_module = importlib.import_module(f"tasks.{task_name}")
    
    # Get task components
    prompt = task_module.get_prompt()
    tools = task_module.get_tools()
    tool_handlers = task_module.get_tool_handlers()
    grader = task_module.get_grader()
    
    print(f"🚀 Running {task_name} {num_runs} times {'concurrently' if concurrent else 'sequentially'}...")
    print("=" * 60)

    # Create all test coroutines
    tasks = [
        run_single_test(
            run_id=i + 1,
            num_runs=num_runs,
            prompt=prompt,
            tools=tools,
            tool_handlers=tool_handlers,
            grader=grader,
            verbose=verbose,
        )
        for i in range(num_runs)
    ]

    # Run with rate limiting to avoid 429 errors
    if concurrent:
        # Process results with limited concurrency (max 2 at a time)
        semaphore = asyncio.Semaphore(2)
        
        async def limited_task(task_coro):
            async with semaphore:
                # Add small delay to avoid rate limits
                await asyncio.sleep(0.5)
                return await task_coro
        
        # Run with limited concurrency
        limited_tasks = [limited_task(task) for task in tasks]
        results = []
        for coro in asyncio.as_completed(limited_tasks):
            result = await coro
            results.append(result)
    else:
        # Run sequentially by awaiting each task in order
        results = []
        for task in tasks:
            result = await task
            results.append(result)
            # Add delay between sequential runs
            await asyncio.sleep(1)

    # Count successes
    successes = sum(1 for _, success, _ in results if success)
    
    # Calculate and display pass rate
    pass_rate = (successes / num_runs) * 100
    print(f"\n{'=' * 60}")
    print("Test Results:")
    print(f"  Passed: {successes}/{num_runs}")
    print(f"  Failed: {num_runs - successes}/{num_runs}")
    print(f"  Pass Rate: {pass_rate:.1f}%")
    print(f"{'=' * 60}")
    
    return pass_rate


async def run_all_tasks_async(
    task_names: list[str],
    num_runs: int = 2,
    concurrent: bool = True,
    verbose: bool = False,
) -> list[float]:
    """
    Run multiple tasks asynchronously.
    
    Args:
        task_names: List of task names to run
        num_runs: Number of runs per task
        concurrent: Whether to run tasks concurrently
        verbose: Whether to show detailed output
        
    Returns:
        List of pass rates for each task
    """
    print(f"🚀 Running {len(task_names)} tasks with {num_runs} runs each...")
    print("=" * 60)
    
    # Create tasks for each task type
    task_coroutines = [
        run_task_async(task_name, num_runs, concurrent, verbose)
        for task_name in task_names
    ]
    
    # Run all tasks concurrently
    results = await asyncio.gather(*task_coroutines, return_exceptions=True)
    
    # Display results
    print(f"\n{'=' * 60}")
    print("FINAL RESULTS")
    print(f"{'=' * 60}")
    
    for task_name, result in zip(task_names, results):
        if isinstance(result, Exception):
            print(f"❌ {task_name}: ERROR - {result}")
        else:
            print(f"✅ {task_name}: {result:.1f}% pass rate")
    
    return results