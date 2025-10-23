# Task Framework

A reinforcement learning environment for evaluating LLM agents on multi-step, tool-using tasks. The framework supports parallel execution, comprehensive logging, and efficiency bonuses.

## Features

- **Multi-step Agent Tasks**: Complex tasks requiring planning and tool use
- **Parallel Execution**: Run multiple task instances concurrently for faster evaluation
- **Efficiency Bonuses**: Reward agents that complete tasks with fewer steps
- **Comprehensive Logging**: Detailed execution logs for debugging and analysis
- **Rate Limiting Protection**: Built-in handling for API rate limits
- **Chain of Thought**: Encourages step-by-step reasoning in complex tasks

## Task Framework Architecture

The framework consists of several key components:

### Core Components
- **`task_framework.py`**: Main orchestration logic, agent loop, and parallel execution
- **`tasks/`**: Individual task implementations with prompts, tools, and graders
- **`main.py`**: Command-line interface for running tasks

### Task Structure
Each task includes:
- **Prompt**: Detailed instructions with step-by-step guidance
- **Tools**: Available functions (Python expressions, data access, answer submission)
- **Grader**: Evaluation logic with partial scoring and detailed feedback
- **Data**: Task-specific datasets and rules

### Agent Loop
1. **Initialization**: Load prompt, tools, and handlers
2. **Iteration**: Agent makes API calls and uses tools (max 12-20 steps)
3. **Evaluation**: Grader scores the final answer
4. **Logging**: Record execution details and results

## How to Run Tasks

### Run All Tasks
```bash
# Parallel execution (default, faster)
python main.py --all --runs 10

# Sequential execution (slower but easier to debug)
python main.py --all --runs 10 --sequential

# Custom number of parallel workers (be careful with rate limits)
python main.py --all --runs 10 --workers 2
```

### Run Individual Tasks

**Data Cleaning Task:**
```bash
# Parallel (default)
python main.py --task data_cleaning --runs 10

# Sequential
python main.py --task data_cleaning --runs 10 --sequential

# Custom workers (be careful with rate limits)
python main.py --task data_cleaning --runs 10 --workers 2
```
*Comprehensive ML data preprocessing with missing value imputation, outlier detection, and statistical analysis.*

**Python Bug Detection Task:**
```bash
python main.py --task python_bug_finder --runs 10
```
*Find and categorize bugs in Python code using static analysis techniques.*

**Resume Parsing Task:**
```bash
python main.py --task resume_parser --runs 10
```
*Extract structured information from resume text and calculate work experience.*

**Email Triage Task (with Efficiency Bonus):**
```bash
python main.py --task email_triage --runs 10
```
*Categorize emails using automation rules with Chain of Thought reasoning. Earn up to 10 bonus points for completing in ≤6 steps!*

**Commit Generator Task:**
```bash
python main.py --task commit_generator --runs 10
```
*Generate conventional commit messages from code changes and documentation.*

## Efficiency Bonus System

The email triage task includes an efficiency bonus system that rewards agents for completing tasks with fewer steps:

### Bonus Points
- **≤4 steps**: 10 points (Excellent efficiency)
- **≤6 steps**: 7 points (Good efficiency)  
- **≤8 steps**: 4 points (Moderate efficiency)
- **≤10 steps**: 2 points (Acceptable efficiency)
- **≥11 steps**: 0 points (Poor efficiency)

### Benefits
- Encourages strategic planning and efficient problem-solving
- Rewards production-ready behavior
- Provides competitive advantage over basic implementations
- Helps identify agents that understand optimization

## Logging

The framework automatically logs execution details to:
- **Console**: Real-time progress and results
- **File**: `task_execution.log` with detailed execution logs

### Log Levels
- **INFO**: Task start/completion, success/failure
- **WARNING**: Timeouts, max steps reached, no tool use
- **ERROR**: Exceptions, API failures
- **DEBUG**: API call timing, detailed step information

### Example Log Output
```
2024-01-15 10:30:15 - INFO - Starting task email_triage with 10 runs (parallel=True)
2024-01-15 10:30:15 - INFO - Running 10 tasks in parallel with 2 workers
2024-01-15 10:30:16 - INFO - Starting task email_triage run 1
🔍 Run 1 LLM result: {...} (used 5 steps)
2024-01-15 10:30:20 - INFO - Run 1 SUCCESS: Score 87/110 (efficiency: 7/10) in 4.2s
2024-01-15 10:30:25 - WARNING - Run 2 FAILURE: Reached max steps (12) in 9.1s
```

## Performance Tips

1. **Use Parallel Execution**: Default behavior, significantly faster
2. **Adjust Workers**: More workers = faster execution (but watch for rate limits)
3. **Monitor Logs**: Check `task_execution.log` for failure reasons
4. **Reduce Runs**: Use fewer runs for testing (`--runs 3`)
5. **Sequential Mode**: Use `--sequential` for debugging individual runs
6. **Rate Limiting**: Default 2 workers to avoid API rate limits

## Rate Limiting

The framework includes built-in rate limiting protection:
- **Default**: 2 parallel workers to avoid 429 errors
- **Automatic Retry**: Waits 2 seconds on rate limit errors
- **Request Spacing**: 500ms delay between parallel requests
- **Fallback**: Use `--sequential` if rate limits persist

### If You Get Rate Limit Errors:
```bash
# Reduce workers
python main.py --task data_cleaning --runs 10 --workers 1

# Or use sequential mode
python main.py --task data_cleaning --runs 10 --sequential
```
