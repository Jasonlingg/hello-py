"""
Paper Technique Implementation Task

Task: Implement a technique from a research paper (label smoothing) into a training script
Domain: Machine Learning & Research Implementation
"""

import json
from typing import Any, Dict, List
from anthropic.types import ToolUnionParam
from task_framework import python_expression_tool, submit_answer_tool


def get_paper_excerpt() -> str:
    """Returns the research paper excerpt describing label smoothing"""
    return """
Label Smoothing is a regularization technique that prevents models from becoming over-confident.

Instead of using hard labels [1, 0], we use soft labels [0.9, 0.1] which encourages the model to be less confident and more robust.

Implementation:
loss = -sum_over_classes(soft_labels * log(predictions))

Where soft_labels are created by replacing the true label's confidence (e.g., 1.0) with:
confidence = 1 - smoothing_factor + (smoothing_factor / num_classes)

For a binary classification problem with smoothing_factor=0.1 and true_label=1:
- Old hard label: [0, 1]
- New smooth label: [0.05, 0.95]  # 0.1/2 applied to wrong class, 1-0.1+0.1/2 for correct

Expected effects:
- Training loss will be slightly HIGHER (model is less confident)
- Test/validation accuracy improves by 2-5% (better generalization)
- Reduces overfitting to training data
"""


def get_baseline_training_code() -> str:
    """Returns baseline training code without label smoothing"""
    return '''
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader

class SimpleDataset(Dataset):
    def __init__(self, num_samples=1000):
        # Synthetic binary classification data
        self.X = torch.randn(num_samples, 10)
        # Labels: 0 or 1
        self.y = torch.randint(0, 2, (num_samples,)).long()
    
    def __len__(self):
        return len(self.X)
    
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

class SimpleNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(10, 32)
        self.fc2 = nn.Linear(32, 16)
        self.fc3 = nn.Linear(16, 2)  # Binary classification
    
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = self.fc3(x)
        return x

# Dataset and dataloader
dataset = SimpleDataset(num_samples=1000)
loader = DataLoader(dataset, batch_size=32, shuffle=True)

# Model and optimizer
model = SimpleNet()
optimizer = optim.Adam(model.parameters(), lr=0.001)
criterion = nn.CrossEntropyLoss()  # Uses hard labels

# Baseline training (no label smoothing)
device = torch.device('cpu')
model = model.to(device)
model.train()

epochs = 20
train_losses = []

for epoch in range(epochs):
    epoch_loss = 0
    for inputs, labels in loader:
        inputs, labels = inputs.to(device), labels.to(device)
        
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        
        epoch_loss += loss.item()
    
    avg_loss = epoch_loss / len(loader)
    train_losses.append(avg_loss)
    if epoch % 5 == 0:
        print(f"Epoch {epoch}, Loss: {avg_loss:.4f}")

print(f"Final training loss: {train_losses[-1]:.4f}")
print(f"Training loss progression: {train_losses[-5:]}")
'''


def get_prompt() -> str:
    return """Implement Label Smoothing from a research paper. You have MAX 12 steps.

TASK: Implement label smoothing in the training code based on the paper excerpt.

STEP-BY-STEP:
1. Call get_paper_excerpt() to read about label smoothing
2. Call get_baseline_training_code() to get the baseline code
3. Create label smoothing loss function with formula (1-0.1+0.1/2=0.95, 0.1/2=0.05)
4. Train baseline and get its loss
5. Train with label smoothing and get its loss
6. Call submit_answer with your results

EXPECTED RESULTS:
- Training loss should be HIGHER with label smoothing (model less confident)
- Typically baseline loss: 0.45-0.55, smoothed loss: 0.48-0.60 (slightly higher)
- Loss should still decrease over epochs

Return as JSON:
{
    "label_smoothing_implementation": "Brief description of how you did it",
    "baseline_loss": <float>,
    "smoothed_loss": <float>,
    "loss_difference": <float>,
    "explanation": "Why smoothed loss is higher"
}

Then call submit_answer with your JSON."""


def get_tools() -> List[ToolUnionParam]:
    return [
        {
            "name": "python_expression",
            "description": "Evaluates Python code. Use print() for output.",
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
            "name": "get_paper_excerpt",
            "description": "Get the research paper excerpt describing label smoothing",
            "input_schema": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
        {
            "name": "get_baseline_training_code",
            "description": "Get baseline training code without label smoothing",
            "input_schema": {
                "type": "object",
                "properties": {},
                "required": [],
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
        "get_paper_excerpt": get_paper_excerpt,
        "get_baseline_training_code": get_baseline_training_code,
        "submit_answer": submit_answer_tool,
    }


def get_grader() -> callable:
    def grade_paper_technique_task(answer: Any, steps_used: int = None) -> bool:
        """Grade the label smoothing implementation task"""
        try:
            if isinstance(answer, str):
                result = json.loads(answer)
            else:
                result = answer
            
            if not isinstance(result, dict):
                print(f"❌ Answer is not a dictionary: {type(result)}")
                return False
            
            required_fields = ["label_smoothing_implementation", "baseline_loss", "smoothed_loss", "loss_difference", "explanation"]
            for field in required_fields:
                if field not in result:
                    print(f"❌ Missing field: {field}")
                    return False
            
            # Just check the implementation has something (flexible)
            impl = result.get("label_smoothing_implementation", "") or result.get("implementation_code", "")
            if not impl or len(impl) < 10:
                print(f"❌ Implementation description is too short")
                return False
            
            # Check loss values are reasonable
            baseline_loss = result["baseline_loss"]
            smoothed_loss = result["smoothed_loss"]
            loss_diff = result["loss_difference"]
            
            # Loss should be higher with smoothing (expected behavior)
            if smoothed_loss < baseline_loss - 0.02:  # Allow small variance
                print(f"❌ Smoothed loss ({smoothed_loss}) should be slightly higher than baseline ({baseline_loss})")
                return False
            
            # Check values are reasonable for cross-entropy loss
            if not (0.1 < baseline_loss < 1.0):
                print(f"❌ Baseline loss {baseline_loss} seems unreasonable")
                return False
            
            if not (0.1 < smoothed_loss < 1.0):
                print(f"❌ Smoothed loss {smoothed_loss} seems unreasonable")
                return False
            
            # Check loss difference (should be positive, small increase)
            if loss_diff < 0:
                print(f"❌ Loss difference should be positive (higher with smoothing)")
                return False
            
            # Loss difference should be in reasonable range (0.01-0.20 for this setup)
            if not (0.01 < loss_diff < 0.20):
                print(f"❌ Loss difference {loss_diff:.4f} seems unreasonable (expected 0.01-0.20)")
                return False
            
            # Just check explanation exists
            explanation = result.get("explanation", "")
            if not explanation or len(explanation) < 20:
                print(f"❌ Explanation is too short")
                return False
            
            print(f"✅ Implementation verified:")
            print(f"   Baseline loss: {baseline_loss:.4f}")
            print(f"   Smoothed loss: {smoothed_loss:.4f}")
            print(f"   Difference: {loss_diff:.4f}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error grading: {e}")
            return False
    
    return grade_paper_technique_task

