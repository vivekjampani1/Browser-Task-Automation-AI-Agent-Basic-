"""
Main Agent Orchestrator - Coordinates all components to execute browser tasks.
"""
from typing import Dict, Any, List, Optional
import time

from browser_controller import BrowserController
from perception import PerceptionModule
from llm_agent import LLMAgent
from action_executor import ActionExecutor
from config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)


class BrowserAgent:
    """Main orchestrator for AI browser automation."""
    
    def __init__(self):
        self.browser: Optional[BrowserController] = None
        self.perception: Optional[PerceptionModule] = None
        self.llm: Optional[LLMAgent] = None
        self.executor: Optional[ActionExecutor] = None
        self.actions_history: List[Dict[str, Any]] = []
        
    def initialize(self) -> None:
        """Initialize all components."""
        logger.info("Initializing Browser Agent")
        
        self.browser = BrowserController()
        self.browser.start()
        
        self.perception = PerceptionModule(self.browser)
        self.llm = LLMAgent()
        self.executor = ActionExecutor(self.browser, self.perception)
        
        logger.info("Browser Agent initialized successfully")
    
    def execute_task(self, task: str, use_vision: bool = False) -> Dict[str, Any]:
        """
        Execute a browser automation task.
        
        Args:
            task: Natural language task description
            use_vision: Whether to use vision model for analysis
            
        Returns:
            Task execution result
        """
        logger.info(f"Starting task execution: {task}")
        
        # Initialize if not already done
        if not self.browser:
            self.initialize()
        
        # Understand the task
        task_info = self.llm.understand_task(task)
        logger.info(f"Task breakdown: {task_info}")
        
        # Execute task loop
        step_count = 0
        max_steps = Config.MAX_STEPS
        task_complete = False
        
        while step_count < max_steps and not task_complete:
            step_count += 1
            logger.info(f"Step {step_count}/{max_steps}")
            
            try:
                # Get current page state
                page_state = self.perception.get_page_state()
                
                # Optionally use vision
                if use_vision and step_count % 3 == 0:  # Every 3rd step
                    screenshot = self.browser.screenshot_base64()
                    vision_analysis = self.llm.analyze_page_with_vision(screenshot, task)
                    logger.info(f"Vision analysis: {vision_analysis.get('analysis', '')[:200]}")
                
                # Plan next action
                next_action = self.llm.plan_next_action(task, page_state, self.actions_history)
                
                # Validate action
                if not self.executor.validate_action(next_action):
                    logger.warning(f"Invalid action: {next_action}")
                    continue
                
                # Execute action
                result = self.executor.execute(next_action)
                
                # Record action
                action_record = {
                    "step": step_count,
                    "action": next_action,
                    "result": result,
                    "timestamp": time.time()
                }
                self.actions_history.append(action_record)
                
                # Check if task is complete
                if result.get("complete"):
                    task_complete = True
                    logger.info("Task marked as complete by action")
                    break
                
                # Verify completion periodically
                if step_count % 5 == 0:
                    verification = self.llm.verify_task_completion(
                        task, 
                        page_state, 
                        self.actions_history
                    )
                    
                    if verification.get("completed") and verification.get("confidence", 0) > 0.8:
                        task_complete = True
                        logger.info("Task verified as complete")
                        break
                
                # Small delay between actions
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in step {step_count}: {e}")
                
                if Config.SCREENSHOT_ON_ERROR:
                    self.browser.screenshot(f"error_step_{step_count}")
                
                # Continue to next step unless critical error
                continue
        
        # Final verification
        final_state = self.perception.get_page_state()
        final_verification = self.llm.verify_task_completion(
            task,
            final_state,
            self.actions_history
        )
        
        result = {
            "task": task,
            "completed": task_complete or final_verification.get("completed", False),
            "steps_taken": step_count,
            "actions": self.actions_history,
            "final_url": self.browser.get_url(),
            "verification": final_verification
        }
        
        logger.info(f"Task execution finished: {result['completed']} in {step_count} steps")
        
        return result
    
    def cleanup(self) -> None:
        """Clean up resources."""
        logger.info("Cleaning up Browser Agent")
        
        if self.browser:
            self.browser.close()
        
        self.actions_history = []
        
        logger.info("Cleanup complete")
    
    def __enter__(self):
        """Context manager entry."""
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()


def main():
    """Main entry point for CLI usage."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python agent.py '<task description>'")
        print("Example: python agent.py 'Go to google.com and search for Python tutorials'")
        sys.exit(1)
    
    task = " ".join(sys.argv[1:])
    
    # Run the agent
    with BrowserAgent() as agent:
        result = agent.execute_task(task)
        
        print("\n" + "="*50)
        print("TASK EXECUTION RESULT")
        print("="*50)
        print(f"Task: {result['task']}")
        print(f"Completed: {result['completed']}")
        print(f"Steps: {result['steps_taken']}")
        print(f"Final URL: {result['final_url']}")
        print(f"Confidence: {result['verification'].get('confidence', 'N/A')}")
        print("="*50)


if __name__ == "__main__":
    main()
