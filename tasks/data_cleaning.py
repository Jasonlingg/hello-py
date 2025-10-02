"""
1) Data Cleaning and Analysis Task

Task: Clean messy customer data and perform statistical analysis
Domain: Data Processing & Analytics
"""

import json
from typing import Any, Dict, List
from anthropic.types import ToolUnionParam
from task_framework import python_expression_tool, submit_answer_tool


def get_dirty_data(name: str) -> dict:
    """Returns messy customer data that needs cleaning"""
    if name == "customers_v1":
        return {
            "data": [
                "ID,Name,Email,Phone,Age,City",
                "1,John Doe,john@email.com,555-1234,25,New York",
                "2,Jane Smith,jane.smith@company.org,(555) 987-6543,30,Los Angeles", 
                "3,Bob Johnson,bob@,555.123.4567,35,Chicago",
                "4,Alice Brown,alice@test.com,555-9999,28,San Francisco",
                "5,Charlie Wilson,charlie@email.com,555-0000,42,Boston",
                "6,Diana Lee,diana@,555-1111,29,Seattle",
                "7,Frank Miller,frank@company.com,555-2222,33,Miami",
                "8,Grace Taylor,grace@test.org,555-3333,26,Denver",
                "9,Henry Davis,henry@,555-4444,31,Austin",
                "10,Iris White,iris@email.net,555-5555,27,Portland",
                "11,Tom Wilson,tom@email.com,555-6666,25,Boston",
                "12,Sarah Connor,sarah@,555-7777,29,Chicago"
            ]
        }
    return {"data": []}


def get_prompt() -> str:
    return """You are given a messy customer dataset that needs cleaning and analysis.

1. Use get_dirty_data(name='customers_v1') to fetch the data
2. Clean the data by:
   - Removing rows where email appears invalid or incomplete
   - Standardizing phone numbers to a consistent format
   - Converting age to proper numeric values (handle edge cases)
3. Calculate statistics on the cleaned data:
   - Count of valid records
   - Average age (rounded to 1 decimal)
   - Most common city (by count, handle ties appropriately)
4. Return JSON in this exact format:
   {"valid_records": <int>, "avg_age": <float>, "most_common_city": "<string>"}

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
            "name": "get_dirty_data",
            "description": "Get messy customer dataset that needs cleaning",
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
        "get_dirty_data": get_dirty_data,
        "submit_answer": submit_answer_tool,
    }


def get_grader() -> callable:
    def grade_data_cleaning_task(answer: Any) -> bool:
        """Grade the data cleaning task result"""
        try:
            # Parse the answer
            if isinstance(answer, str):
                result = json.loads(answer)
            else:
                result = answer
            
            if not isinstance(result, dict):
                return False
                
            # Expected correct answer based on the data
            # Valid records (emails with @domain): 1,2,4,5,7,8,10,11 = 8 records
            # Ages: 25,30,28,42,33,26,27,25 = 236/8 = 29.5
            # Cities: Boston(2), Chicago(2), others(1 each) - so Boston and Chicago are tied for most common
            
            expected_records = 8
            expected_avg_age = 29.5
            valid_cities = ["Austin", "Boston", "Chicago", "Denver", "Los Angeles", "Miami", "New York", "Portland", "San Francisco", "Seattle"]
            
            # Check each field with tolerance for float
            if result.get("valid_records") != expected_records:
                return False
                
            if abs(result.get("avg_age", 0) - expected_avg_age) > 0.1:
                return False
                
            # For most common city, accept only Boston or Chicago (both appear twice)
            most_common_cities = ["Boston", "Chicago"]
            if result.get("most_common_city") not in most_common_cities:
                return False
                
            return True
            
        except Exception:
            return False
    
    return grade_data_cleaning_task
