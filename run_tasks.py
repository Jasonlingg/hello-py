#!/usr/bin/env python3
"""
Run RL tasks for LLM training evaluation
"""

import sys
import argparse
from task_framework import run_task, analyze_all_tasks


def main():
    parser = argparse.ArgumentParser(description="Run RL tasks for LLM training")
    parser.add_argument("--task", help="Specific task to run (data_cleaning, python_bug_finder, fraud_detector)")
    parser.add_argument("--runs", type=int, default=10, help="Number of runs per task (default: 10)")
    parser.add_argument("--steps", type=int, default=8, help="Maximum steps per run (default: 8)")
    parser.add_argument("--verbose", action="store_true", help="Verbose output for each run")
    parser.add_argument("--all", action="store_true", help="Run all tasks")
    parser.add_argument("--analyze", action="store_true", help="Analyze task difficulty")
    
    args = parser.parse_args()
    
    if args.all:
        # Run all tasks
        tasks = [
            "data_cleaning",
            "python_bug_finder",
            "fraud_detector"
        ]
        
        results = []
        for task in tasks:
            print(f"\n{'='*80}")
            print(f"Running task: {task}")
            print(f"{'='*80}")
            try:
                pass_rate = run_task(task, args.runs, args.steps, args.verbose)
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
        
        # Check if all tasks are in target range
        in_range = all(10 <= rate <= 40 for _, rate in results)
        print(f"\nAll tasks in 10-40% range: {'✓' if in_range else '✗'}")
        
    elif args.task:
        # Run specific task
        try:
            pass_rate = run_task(args.task, args.runs, args.steps, args.verbose)
            print(f"\nTask {args.task} pass rate: {pass_rate:.1f}%")
            if 10 <= pass_rate <= 40:
                print("✓ Pass rate is in target range (10-40%)")
            else:
                print("✗ Pass rate is outside target range (10-40%)")
        except Exception as e:
            print(f"Error running task {args.task}: {e}")
            sys.exit(1)
    elif args.analyze:
        # Analyze task difficulty
        analyze_all_tasks()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
