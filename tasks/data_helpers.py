"""
Helper functions for data cleaning tasks
"""
import csv
from io import StringIO
from typing import List, Dict, Any


def parse_csv_data(csv_rows: List[str]) -> List[Dict[str, str]]:
    """
    Parse CSV data from a list of strings into a list of dictionaries
    
    Args:
        csv_rows: List of CSV rows as strings (first row should be header)
        
    Returns:
        List of dictionaries with column names as keys
    """
    reader = csv.DictReader(StringIO('\n'.join(csv_rows)))
    return list(reader)


def detect_outliers_iqr(data: List[float]) -> int:
    """
    Detect outliers using the Interquartile Range (IQR) method
    
    Args:
        data: List of numeric values
        
    Returns:
        Number of outliers detected
    """
    if len(data) < 4:
        return 0
    
    sorted_data = sorted(data)
    q1 = sorted_data[len(data)//4]
    q3 = sorted_data[3*len(data)//4]
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    
    outliers = [x for x in data if x < lower_bound or x > upper_bound]
    return len(outliers)


def is_valid_email(email: str) -> bool:
    """
    Check if an email address has a valid format
    
    Args:
        email: Email address string
        
    Returns:
        True if email has valid format, False otherwise
    """
    return '@' in email and '.' in email.split('@')[1]


def is_missing_value(value: str) -> bool:
    """
    Check if a value represents missing data
    
    Args:
        value: String value to check
        
    Returns:
        True if value represents missing data, False otherwise
    """
    return value in ['', '0', 'missing', 'null', 'NULL', 'None']


def calculate_most_common_city(cities: List[str]) -> str:
    """
    Find the most common city, using alphabetical order as tie-breaker
    
    Args:
        cities: List of city names
        
    Returns:
        Most common city name
    """
    city_counts = {}
    for city in cities:
        city_counts[city] = city_counts.get(city, 0) + 1
    
    # Sort by count (descending) then by name (ascending) for tie-breaker
    return max(city_counts, key=lambda x: (city_counts[x], x))


def analyze_dataset_quality(rows: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Analyze dataset quality and compute expected values for grading
    
    Args:
        rows: List of parsed CSV rows
        
    Returns:
        Dictionary with analysis results
    """
    valid_records = []
    total_age = 0
    total_income = 0
    missing_values_handled = 0
    invalid_records_removed = 0
    
    for row in rows:
        # Check for missing values FIrst (before filtering invalid emails)
        if is_missing_value(row['Income']):
            missing_values_handled += 1
        if is_missing_value(row['Education']):
            missing_values_handled += 1
        
        # Check for invalid emails
        if not is_valid_email(row['Email']):
            invalid_records_removed += 1
            continue
        
        valid_records.append(row)
        total_age += int(row['Age'])
        
        # Handle income calculation (skip missing values)
        if not is_missing_value(row['Income']):
            total_income += int(row['Income'])
    
    # Calculate expected values
    expected_records = len(valid_records)
    expected_avg_age = round(total_age / len(valid_records), 1)
    expected_avg_income = round(total_income / len(valid_records))
    
    # Find most common city
    cities = [row['City'] for row in valid_records]
    expected_most_common_city = calculate_most_common_city(cities)
    
    # Detect outliers
    ages = [int(row['Age']) for row in valid_records]
    incomes = [int(row['Income']) for row in valid_records if not is_missing_value(row['Income'])]
    expected_outliers_detected = detect_outliers_iqr(ages) + detect_outliers_iqr(incomes)
    
    return {
        'expected_records': expected_records,
        'expected_avg_age': expected_avg_age,
        'expected_avg_income': expected_avg_income,
        'expected_most_common_city': expected_most_common_city,
        'expected_outliers_detected': expected_outliers_detected,
        'missing_values_handled': missing_values_handled,
        'invalid_records_removed': invalid_records_removed
    }
