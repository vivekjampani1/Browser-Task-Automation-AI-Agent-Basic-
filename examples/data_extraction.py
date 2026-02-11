"""
Data Extraction Example

This example demonstrates how to use the AI browser agent to extract data from websites.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import BrowserAgent


def main():
    """Extract data from a website."""
    task = "Go to news.ycombinator.com and extract the top 5 story titles"
    
    print(f"\n🤖 Starting task: {task}\n")
    
    with BrowserAgent() as agent:
        result = agent.execute_task(task, use_vision=True)
        
        print(f"\n✅ Task completed: {result['completed']}")
        print(f"📊 Steps taken: {result['steps_taken']}")
        
        if result.get('extracted_data'):
            print(f"\n📝 Extracted data:")
            print(result['extracted_data'])


if __name__ == "__main__":
    main()
