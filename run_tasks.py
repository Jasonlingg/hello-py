#!/usr/bin/env python3
"""
Run RL tasks for LLM training evaluation
"""

import sys
import argparse
from task_framework import run_task


def main():
    parser = argparse.ArgumentParser(description="Run RL tasks for LLM training")
    parser.add_argument("--task", help="Specific task to run (data_cleaning, python_bug_finder, resume_parser, email_triage, commit_generator)")
    parser.add_argument("--runs", type=int, default=10, help="Number of runs per task (default: 10)")
    parser.add_argument("--all", action="store_true", help="Run all tasks")
    
    args = parser.parse_args()
    
    if args.all:
        # Run all tasks
        tasks = [
            "data_cleaning",
            "python_bug_finder",
            "resume_parser",
            "email_triage",
            "commit_generator"
        ]
        
        results = []
        for task in tasks:
            print(f"\n{'='*80}")
            print(f"Running task: {task}")
            print(f"{'='*80}")
            try:
                pass_rate = run_task(task, args.runs)
                results.append((task, pass_rate))
            except Exception as e:
                print(f"Error running {task}: {e}")
                results.append((task, 0.0))
        
        # Summary
        print(f"\n{'='*80}")
        print("SUMMARY")
        print(f"{'='*80}")
        for task, rate in results:
            print(f"{task:25}: {rate:6.1f}%")
        
    elif args.task:
        # Run specific task
        try:
            pass_rate = run_task(args.task, args.runs)
            print(f"\nTask {args.task} pass rate: {pass_rate:.1f}%")
        except Exception as e:
            print(f"Error running task {args.task}: {e}")
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
