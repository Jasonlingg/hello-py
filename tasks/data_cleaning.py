"""
1) Data Cleaning and Analysis Task

Task: Clean messy customer data and perform statistical analysis
Domain: Data Processing & Analytics
"""

import json
from typing import Any, Dict, List
from anthropic.types import ToolUnionParam
from task_framework import python_expression_tool, submit_answer_tool

# This method returns dirty data that needs cleaning
# Added more data to make it more challenging
#
def get_dirty_data(name: str) -> dict:
    """Returns messy customer data that needs comprehensive ML preprocessing"""
    if name == "customers_v1":
        return {
            "data": [
                "ID,Name,Email,Phone,Age,City,Income,Education",
                "1,John Doe,john@email.com,555-1234,25,New York,50000,Bachelor",
                "2,Jane Smith,jane.smith@company.org,(555) 987-6543,30,Los Angeles,75000,Master", 
                "3,Bob Johnson,bob@,555.123.4567,35,Chicago,0,PhD",
                "4,Alice Brown,alice@test.com,555-9999,28,San Francisco,60000,Bachelor",
                "5,Charlie Wilson,charlie@email.com,555-0000,42,Boston,90000,Master",
                "6,Diana Lee,diana@,555-1111,29,Seattle,55000,",
                "7,Frank Miller,frank@company.com,555-2222,33,Miami,80000,Bachelor",
                "8,Grace Taylor,grace@test.org,555-3333,26,Denver,45000,High School",
                "9,Henry Davis,henry@,555-4444,31,Austin,70000,Master",
                "10,Iris White,iris@email.net,555-5555,27,Portland,65000,Bachelor",
                "11,Tom Wilson,tom@email.com,555-6666,25,Boston,48000,Bachelor",
                "12,Sarah Connor,sarah@,555-7777,29,Chicago,72000,Master",
                "13,Alex Kim,alex@invalid,555-8888,22,New York,35000,High School",
                "14,Maria Garcia,maria@company.com,555-9999,38,Los Angeles,85000,PhD",
                "15,David Chen,david@test.org,555-0000,45,San Francisco,95000,Master",
                "16,Lisa Wang,lisa@email.com,555-1111,31,Seattle,68000,Bachelor",
                "17,Michael Brown,michael@company.org,555-2222,29,Miami,52000,Bachelor",
                "18,Emily Davis,emily@test.com,555-3333,26,Denver,47000,High School",
                "19,James Wilson,james@email.net,555-4444,33,Austin,78000,Master",
                "20,Sophia Lee,sophia@company.com,555-5555,28,Portland,62000,Bachelor"
            ],
        }
    return {"data": []}

# define a prompt for the task

# improvements: 
# its kinda basic, I am just asking it to do some basica cleaning
# Its failign because of a calcualtion error, it should be able to do it while the 
# cleaning of the data is pretty easy for it
# it shoudl include ml preprocessing steps, as this is super import in ML workflows the AI probably didnt do this because it didnt know to do it
def get_prompt() -> str:
    return """You are given a messy customer dataset that requires comprehensive ML data preprocessing and analysis.

IMPORTANT: You have exactly 12 steps maximum to complete this task. Plan your approach carefully and work efficiently.

STEP-BY-STEP APPROACH:
1. Use get_dirty_data(name='customers_v1') to fetch the dataset and metadata
2. Analyze the data structure and identify quality issues
3. Clean the data systematically
4. Calculate statistics on cleaned data
5. Submit your final answer

DETAILED REQUIREMENTS:

DATA CLEANING STEPS:
Step 1: Get the data using get_dirty_data(name='customers_v1')
Step 2: Parse the CSV data and identify issues:
   - Invalid emails: Look for emails without proper domain (e.g., "bob@", "diana@")
   - Missing values: Empty cells in income or education columns
   - Data types: Ensure ages and incomes are numeric

Step 3: Remove invalid records:
   - Filter out rows where email is invalid (missing domain part)
   - Count how many records you removed

Step 4: Handle missing values:
   - For missing income: Use median of valid incomes
   - For missing education: Use mode of valid educations
   - Count how many missing values you handled

Step 5: Detect outliers:
   - Use IQR method: Q1 - 1.5*IQR and Q3 + 1.5*IQR
   - Count how many outliers you detected

Step 6: Calculate statistics on cleaned data:
   - Count valid records (after removing invalid emails)
   - Calculate average age (sum of ages / count, rounded to 1 decimal)
   - Calculate average income (sum of incomes / count, rounded to nearest integer)
   - Find most common city (count occurrences, if tie use alphabetical order)

Step 7: Validate your results:
   - Check that all emails have proper format
   - Verify no missing values remain
   - Confirm ages are reasonable (18-100)
   - Ensure incomes are positive

Step 8: Submit your answer using submit_answer()

EXPECTED OUTPUT FORMAT:
{
  "valid_records": <int>,
  "avg_age": <float>,
  "most_common_city": "<string>",
  "avg_income": <int>,
  "data_quality": {
    "missing_values_handled": <int>,
    "outliers_detected": <int>,
    "invalid_records_removed": <int>
  }
}

VALIDATION CRITERIA:
- valid_records: Count of records after removing invalid emails
- avg_age: Average age of valid records (rounded to 1 decimal)
- most_common_city: City with highest count (alphabetical tie-breaker)
- avg_income: Average income of valid records (rounded to nearest integer)
- missing_values_handled: Count of missing values you imputed
- outliers_detected: Count of outliers you identified
- invalid_records_removed: Count of records you removed

WORK EFFICIENTLY:
- Use python_expression tool for calculations
- Validate each step before proceeding
- Don't repeat the same operations
- Focus on accuracy over speed

Then call submit_answer with your complete JSON result."""

# the python exrpetion tool is a bit basic, I maybe coudl of asked it to use more libraires or soemthign
# I shoudl give the LLM more tools to work with, I could splti it up into multiple tools so it has more focus
# for example one tool to get validate emails and one tool to do the calculations 
# for now its ok I think
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
    
# GRADER
# pros:
# has some error hadnling we need to make sure it is in a correct format
# there are mutliple valid soltions
# cons:
# just too simple, jsut checkinf for 3 things that are valid
# we jsut have hardecoded values that we are checking adn it depends on the dat set
# NO PARTIAL CREDIT, passes or fails, but I think this was for the take home so makes sense
# Next to treat grading liek rubric engineering ,wher ewe need to design a rubric that algins with learning goals with
# weighted scoring. But it is a bit hard to do becasue you need to design a really good rubric 



def get_grader() -> callable:
    def grade_data_cleaning_task(answer: Any, steps_used: int = None) -> bool:
        """Grade the comprehensive data cleaning task result"""
        try:
            # Parse the answer
            if isinstance(answer, str):
                result = json.loads(answer)
            else:
                result = answer
            
            # Validate answer is a dictionary
            if not isinstance(result, dict):
                print(f"❌ Answer is not a dictionary: {type(result)}")
                return False
            
            # Validate required fields exist
            required_fields = ["valid_records", "avg_age", "most_common_city", "avg_income", "data_quality"]
            for field in required_fields:
                if field not in result:
                    return False
            
            # Validate data_quality is a dictionary with required subfields
            if not isinstance(result["data_quality"], dict):
                return False
            
            required_quality_fields = ["missing_values_handled", "outliers_detected", "invalid_records_removed"]
            for field in required_quality_fields:
                if field not in result["data_quality"]:
                    return False
            
            # Get the actual dataset and compute expected answers dynamically
            from .data_helpers import parse_csv_data, analyze_dataset_quality
            
            dataset = get_dirty_data('customers_v1')['data']
            rows = parse_csv_data(dataset)
            analysis = analyze_dataset_quality(rows)
            
            # Print expected answers for debugging
            print("=== EXPECTED ANSWERS ===")
            print(f"valid_records: {analysis['expected_records']}")
            print(f"avg_age: {analysis['expected_avg_age']}")
            print(f"avg_income: {analysis['expected_avg_income']}")
            print(f"most_common_city: {analysis['expected_most_common_city']}")
            print(f"missing_values_handled: {analysis['missing_values_handled']}")
            print(f"invalid_records_removed: {analysis['invalid_records_removed']}")
            print(f"outliers_detected: {analysis['expected_outliers_detected']}")
            print("========================")
            
            expected_records = analysis['expected_records']
            expected_avg_age = analysis['expected_avg_age']
            expected_avg_income = analysis['expected_avg_income']
            expected_most_common_city = analysis['expected_most_common_city']
            expected_outliers_detected = analysis['expected_outliers_detected']
            missing_values_handled = analysis['missing_values_handled']
            invalid_records_removed = analysis['invalid_records_removed']
            
            # Validate valid_records
            if result.get("valid_records") != expected_records:
                return False
            
            # Validate avg_age with tolerance
            if abs(result.get("avg_age", 0) - expected_avg_age) > 0.1:
                return False
            
            # Validate most_common_city
            if result.get("most_common_city") != expected_most_common_city:
                return False
            
            # Validate avg_income with tolerance
            if abs(result.get("avg_income", 0) - expected_avg_income) > 100:
                return False
            
            # Validate data quality metrics
            quality = result["data_quality"]
            
            if quality.get("missing_values_handled", 0) != missing_values_handled:
                return False
            
            if quality.get("invalid_records_removed", 0) != invalid_records_removed:
                return False
            
            # Outlier detection is more flexible (within reasonable range)
            agent_outliers = quality.get("outliers_detected", 0)
            if agent_outliers < 0 or agent_outliers > expected_outliers_detected + 2:
                return False
            
            # Validate data types
            if not isinstance(result.get("valid_records"), int):
                return False
            if not isinstance(result.get("avg_age"), (int, float)):
                return False
            if not isinstance(result.get("most_common_city"), str):
                return False
            if not isinstance(result.get("avg_income"), int):
                return False
            
            # Validate data quality metrics are integers
            for field in required_quality_fields:
                if not isinstance(quality.get(field), int):
                    return False
            
            return True
        
        except Exception:
            return False
    
    return grade_data_cleaning_task
