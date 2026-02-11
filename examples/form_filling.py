"""
Form Filling Example

This example demonstrates how to use the AI browser agent to fill out web forms.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import BrowserAgent


def main():
    """Fill out a contact form."""
    task = """
    Go to example.com/contact and fill out the form with:
    - Name: John Doe
    - Email: john@example.com
    - Message: Testing AI browser automation
    """
    
    print(f"\n🤖 Starting task: {task}\n")
    
    with BrowserAgent() as agent:
        result = agent.execute_task(task)
        
        print(f"\n✅ Task completed: {result['completed']}")
        print(f"📊 Steps taken: {result['steps_taken']}")


if __name__ == "__main__":
    main()
