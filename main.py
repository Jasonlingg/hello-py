#!/usr/bin/env python3
"""
Simple async task runner using the clean task framework
"""

import asyncio
import argparse
from task_framework import run_task_async, run_all_tasks_async

async def main():
    """Main function"""
    # Available tasks
    available_tasks = [
        "data_cleaning",
        "python_bug_finder", 
        "email_triage",
        "resume_parser",
        "commit_generator",
        "pytorch_training_fix",
        "choose_alg",
        "paper_technique"
    ]
    
    parser = argparse.ArgumentParser(description="Run tasks using the clean task framework")
    parser.add_argument("--task", "-t", help="Task name to run", choices=available_tasks + ["all"])
    parser.add_argument("--runs", "-r", type=int, default=3, help="Number of runs (default: 3)")
    
    args = parser.parse_args()
    
    if args.task:
        if args.task == "all":
            await run_all_tasks_async(available_tasks, args.runs)
        else:
            await run_task_async(args.task, args.runs)
    else:
        # Interactive mode
        print("🎯 Available tasks:")
        for i, task in enumerate(available_tasks, 1):
            print(f"  {i}. {task}")
        print("  6. Run all tasks")
        
        choice = input("Select task (1-6): ").strip()
        
        if choice == "6":
            num_runs = int(input("Number of runs per task (default 2): ") or "2")
            await run_all_tasks_async(available_tasks, num_runs)
        elif choice.isdigit() and 1 <= int(choice) <= 5:
            task_name = available_tasks[int(choice) - 1]
            num_runs = int(input(f"Number of runs for {task_name} (default 3): ") or "3")
            await run_task_async(task_name, num_runs)
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    asyncio.run(main())