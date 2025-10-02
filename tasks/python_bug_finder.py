"""
2) Python Bug Detection and Code Analysis Task

Task: Identify and fix bugs in Python code while maintaining functionality
Domain: Software Engineering & Code Quality
"""

import json
from typing import Any, Dict, List
from anthropic.types import ToolUnionParam
from task_framework import python_expression_tool, submit_answer_tool


def get_buggy_code(name: str) -> dict:
    """Returns Python code with various bugs"""
    if name == "code_v1":
        return {
            "code": '''
# LeetCode Problem 1: Two Sum
def two_sum(nums, target):
    for i in range(len(nums)):
        for j in range(len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []

# LeetCode Problem 2: Valid Parentheses
def is_valid(s):
    stack = []
    for char in s:
        if char in '([{':
            stack.append(char)
        elif char in ')]}':
            if not stack:
                return False
            if char == ')' and stack[-1] != '(':
                return False
            if char == ']' and stack[-1] != '[':
                return False
            if char == '}' and stack[-1] != '{':
                return False
            stack.pop()
    return len(stack) == 0

# LeetCode Problem 3: Maximum Subarray
def max_subarray(nums):
    max_sum = nums[0]
    current_sum = 0
    for num in nums:
        current_sum += num
        if current_sum > max_sum:
            max_sum = current_sum
        if current_sum < 0:
            current_sum = 0
    return max_sum

# LeetCode Problem 4: Climbing Stairs
def climb_stairs(n):
    if n <= 2:
        return n
    return climb_stairs(n - 1) + climb_stairs(n - 2)

# LeetCode Problem 5: Best Time to Buy and Sell Stock
def max_profit(prices):
    if not prices:
        return 0
    min_price = prices[0]
    max_profit = 0
    for price in prices:
        if price < min_price:
            min_price = price
        if price - min_price > max_profit:
            max_profit = price - min_price
    return max_profit

# LeetCode Problem 6: Contains Duplicate
def contains_duplicate(nums):
    seen = set()
    for num in nums:
        if num in seen:
            return True
        seen.add(num)
    return False

# LeetCode Problem 7: Missing Number
def missing_number(nums):
    n = len(nums)
    expected_sum = n * (n + 1) // 2
    actual_sum = sum(nums)
    return expected_sum - actual_sum

# LeetCode Problem 8: Single Number
def single_number(nums):
    result = 0
    for num in nums:
        result ^= num
    return result

# LeetCode Problem 9: Reverse String
def reverse_string(s):
    left, right = 0, len(s) - 1
    while left < right:
        s[left], s[right] = s[right], s[left]
        left += 1
        right -= 1
    return s

# LeetCode Problem 10: Valid Anagram
def is_anagram(s, t):
    if len(s) != len(t):
        return False
    return sorted(s) == sorted(t)
'''
        }
    return {"code": ""}


def get_prompt() -> str:
    return """You are given Python code containing LeetCode-style problems with bugs. Analyze the code to identify algorithmic and logic errors.

1. Use get_buggy_code(name='code_v1') to fetch the code
2. Analyze each function for potential issues including:
   - Algorithm logic errors
   - Edge cases that may cause failures
   - Off-by-one errors and index issues
   - Performance and efficiency problems
   - Incorrect data structure usage
   - Missing boundary conditions
   - Incorrect loop conditions
   - Wrong return values
3. For each bug found, provide:
   - Function name where the bug occurs
   - Description of the specific issue
   - Severity level (low, medium, high)
4. Return JSON in this exact format:
   {"bugs": [{"function": "<function_name>", "description": "<bug_description>", "severity": "<severity>"}, ...]}

Then call submit_answer with that JSON."""


def get_tools() -> List[ToolUnionParam]:
    return [
        {
            "name": "python_expression",
            "description": "Evaluates a Python expression. Use print() to output results.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Python code to execute. Use print() for output.",
                    }
                },
                "required": ["expression"],
            },
        },
        {
            "name": "get_buggy_code",
            "description": "Get Python code with bugs to analyze",
            "input_schema": {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
            },
        },
        {
            "name": "submit_answer",
            "description": "Submit the final answer",
            "input_schema": {
                "type": "object",
                "properties": {"answer": {"description": "The final answer to submit"}},
                "required": ["answer"],
            },
        },
    ]


def get_tool_handlers() -> Dict[str, Any]:
    return {
        "python_expression": python_expression_tool,
        "get_buggy_code": get_buggy_code,
        "submit_answer": submit_answer_tool,
    }


def get_grader() -> callable:
    def grade_python_bug_finder_task(answer: Any) -> bool:
        """Grade the Python bug finder task result"""
        try:
            # Parse the answer
            if isinstance(answer, str):
                result = json.loads(answer)
            else:
                result = answer
            
            if not isinstance(result, dict) or "bugs" not in result:
                return False
            
            bugs = result["bugs"]
            if not isinstance(bugs, list):
                return False
            
            # Expected bugs based on what LLM can realistically find (must find at least 6 out of 7)
            expected_bugs = [
                {"function": "two_sum", "description": "Logic error - uses same index twice", "severity": "high"},
                {"function": "climb_stairs", "description": "Performance issue - exponential time complexity", "severity": "high"},
                {"function": "reverse_string", "description": "Logic error - wrong string reversal", "severity": "medium"},
                {"function": "is_anagram", "description": "Performance issue - inefficient sorting", "severity": "medium"},
                {"function": "max_subarray", "description": "Edge case - all negative numbers", "severity": "medium"},
                {"function": "max_profit", "description": "Edge case - continuously decreasing prices", "severity": "low"},
                {"function": "is_valid", "description": "Edge case - extra brackets after valid sequence", "severity": "low"}
            ]
            
            # Check if at least 6 out of 7 expected bugs are found
            found_bugs = []
            for bug in bugs:
                if isinstance(bug, dict) and "function" in bug and "description" in bug:
                    found_bugs.append({
                        "function": bug["function"],
                        "description": bug["description"].lower(),
                        "severity": bug.get("severity", "unknown")
                    })
            
            # Must find at least 6 bugs with correct function names and descriptions
            correct_bugs = 0
            for expected in expected_bugs:
                for found in found_bugs:
                    if (found["function"] == expected["function"] and 
                        any(keyword in found["description"] for keyword in expected["description"].lower().split())):
                        correct_bugs += 1
                        break
            
            # Must find at least 6 out of 7 bugs correctly (86% threshold for ~20% success rate)
            return correct_bugs >= 6
            
        except Exception:
            return False
    
    return grade_python_bug_finder_task
