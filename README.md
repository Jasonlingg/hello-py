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

**Python Bug Detection Task:**
```bash
python main.py --task python_bug_finder --runs 10
```

**Resume Parsing Task:**
```bash
python main.py --task resume_parser --runs 10
```

**Email Triage Task:**
```bash
python main.py --task email_triage --runs 10
```

**Commit Generator Task:**
```bash
python main.py --task commit_generator --runs 10
```

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
2024-01-15 10:30:15 - INFO - Starting task data_cleaning with 10 runs (parallel=True)
2024-01-15 10:30:15 - INFO - Running 10 tasks in parallel with 3 workers
2024-01-15 10:30:16 - INFO - Starting task data_cleaning run 1
2024-01-15 10:30:20 - INFO - Run 1 SUCCESS: Completed in 4.2s with answer: {...}
2024-01-15 10:30:25 - WARNING - Run 2 FAILURE: Reached max steps (8) in 9.1s
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
