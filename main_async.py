#!/usr/bin/env python3
"""
Simple async task runner using the clean task framework
"""

import asyncio
from task_framework import run_task_async, run_all_tasks_async

async def main():
    """Main function"""
    import sys
    
    # Available tasks
    available_tasks = [
        "data_cleaning",
        "python_bug_finder", 
        "email_triage",
        "resume_parser",
        "commit_generator"
    ]
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "all":
            num_runs = int(sys.argv[2]) if len(sys.argv) > 2 else 3
            await run_all_tasks_async(available_tasks, num_runs)
        else:
            task_name = sys.argv[1]
            num_runs = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            await run_task_async(task_name, num_runs)
    else:
        # Interactive mode
        print("🎯 Available tasks:")
        for i, task in enumerate(available_tasks, 1):
            print(f"  {i}. {task}")
        print("  6. Run all tasks")
        
        choice = input("Select task (1-6): ").strip()
        
        if choice == "6":
            num_runs = int(input("Number of runs per task (default 3): ") or "3")
            await run_all_tasks_async(available_tasks, num_runs)
        elif choice.isdigit() and 1 <= int(choice) <= 5:
            task_name = available_tasks[int(choice) - 1]
            num_runs = int(input(f"Number of runs for {task_name} (default 5): ") or "5")
            await run_task_async(task_name, num_runs)
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    asyncio.run(main())