from typing import Any, Dict, List, Callable
import pandas as pd
import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report
from anthropic.types import ToolUnionParam
import json
from task_framework import python_expression_tool, submit_answer_tool

def get_data(name: str) -> Dict[str, Any]:
    """Return task-specific data."""
    
    # Load baseball Hall of Fame data
    df = pd.read_csv('data/500hits.csv', encoding='latin-1')
    
    # Use larger dataset for better accuracy (72 train, 18 test)
    df_small = df.sample(n=90, random_state=42).reset_index(drop=True)
    
    # Features: all columns except PLAYER (name) and HOF (target)
    X = df_small.drop(['PLAYER', 'HOF'], axis=1).values
    y = df_small['HOF'].values
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Baseline model (intentionally poor)
    baseline = LogisticRegression(random_state=42, max_iter=1000, solver='liblinear')
    baseline.fit(X_train, y_train)
    baseline_acc = baseline.score(X_test, y_test)
    
    return {
        "X_train": X_train.tolist(),
        "X_test": X_test.tolist(),
        "y_train": y_train.tolist(),
        "y_test": y_test.tolist(),
        "baseline_accuracy": baseline_acc,
        "target_accuracy": 0.75,  # Lower for harder HOF prediction
        "n_features": X.shape[1],
        "n_samples": X.shape[0],
        "task_type": "binary_classification"
    }

def get_prompt() -> str:
    return """Predict baseball Hall of Fame induction. You have MAX 12 steps.

CRITICAL: Do EVERYTHING in ONE python_expression call! Each call loses state.

TASK: Train sklearn models to predict HOF status, compare accuracy, submit best model.

PROCESS:
1. Call get_classification_data(name="classification")
2. In ONE python_expression call, do ALL OF THIS:
   - Import models and preprocessing
   - SCALE features (StandardScaler for SVC and KNN)
   - Train 3+ models with hyperparameters:
     * RandomForestClassifier(n_estimators=100, random_state=42)
     * SVC(C=1.0, kernel='rbf', random_state=42)  
     * KNeighborsClassifier(n_neighbors=5)
   - Compare test accuracy
   - Pick best model (>0.75 accuracy)
   - Get predictions on ALL test samples
   - Print model name and accuracy
3. Call submit_answer: {"model_name": str, "test_accuracy": float, "predictions": list}

TIPS: Scale features with StandardScaler(). Scale both train AND test before training.

TOOLS: python_expression, get_classification_data, submit_answer

CONSTRAINTS: random_state=42. One python_expression call only!"""
    
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
            "name": "get_classification_data",
            "description": "Get classification data for training and testing",
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
        
        
        
def get_classification_data_tool(name: str) -> Dict[str, Any]:
    """Tool handler to get classification data"""
    return get_data(name)

def get_tool_handlers() -> Dict[str, Any]: 
    return {
        "python_expression": python_expression_tool,
        "get_classification_data": get_classification_data_tool,
        "submit_answer": submit_answer_tool,
    }

def get_grader() -> callable:
    def grade_choose_alg_task(answer: Any, steps_used: int = None) -> bool:
        """Grade the algorithm selection task result"""
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
            required_fields = ["model_name", "test_accuracy", "predictions"]
            for field in required_fields:
                if field not in result:
                    print(f"❌ Missing required field: {field}")
                    return False
            
            # Validate accuracy is above threshold (75%)
            test_accuracy = result.get("test_accuracy")
            if not isinstance(test_accuracy, (int, float)):
                print(f"❌ test_accuracy must be numeric, got {type(test_accuracy)}")
                return False
            
            if test_accuracy < 0.75:
                print(f"❌ Accuracy {test_accuracy:.4f} is below threshold of 0.75")
                return False
            
            # Validate model name is provided
            model_name = result.get("model_name")
            if not isinstance(model_name, str) or not model_name:
                print(f"❌ model_name must be a non-empty string")
                return False
            
            # Validate predictions exist
            predictions = result.get("predictions")
            if not isinstance(predictions, list) or len(predictions) == 0:
                print(f"❌ predictions must be a non-empty list")
                return False
            
            # Get the test data to validate predictions length
            test_data = get_data("classification")
            X_test_len = len(test_data["X_test"])
            
            if len(predictions) != X_test_len:
                print(f"❌ predictions length {len(predictions)} doesn't match test data length {X_test_len}")
                return False
            
            # All validations passed
            print(f"✅ Task completed successfully!")
            print(f"   Model: {model_name}")
            print(f"   Accuracy: {test_accuracy:.4f}")
            print(f"   Predictions: {len(predictions)}")
            return True
            
        except Exception as e:
            print(f"❌ Error during grading: {e}")
            return False
    
    return grade_choose_alg_task