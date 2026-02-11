"""
Google Search Example

This example demonstrates how to use the AI browser agent to perform a Google search.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import BrowserAgent


def main():
    """Run a Google search task."""
    task = "Go to google.com and search for 'AI browser automation'"
    
    print(f"\n🤖 Starting task: {task}\n")
    
    with BrowserAgent() as agent:
        result = agent.execute_task(task)
        
        print(f"\n✅ Task completed: {result['completed']}")
        print(f"📊 Steps taken: {result['steps_taken']}")
        print(f"⏱️  Time elapsed: {result['time_elapsed']:.2f}s")


if __name__ == "__main__":
    main()
