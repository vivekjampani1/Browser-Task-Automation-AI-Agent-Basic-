"""
Action Executor - Executes browser actions based on LLM decisions.
"""
from typing import Dict, Any, Optional
import time

from browser_controller import BrowserController
from perception import PerceptionModule
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ActionExecutor:
    """Executes actions in the browser based on LLM decisions."""
    
    def __init__(self, browser: BrowserController, perception: PerceptionModule):
        self.browser = browser
        self.perception = perception
        
    def execute(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an action and return the result.
        
        Args:
            action: Action dictionary with 'action' and 'params' keys
            
        Returns:
            Result dictionary with 'success', 'message', and optional 'data'
        """
        action_type = action.get("action", "").lower()
        params = action.get("params", {})
        
        logger.info(f"Executing action: {action_type}")
        
        try:
            if action_type == "navigate":
                return self._execute_navigate(params)
            elif action_type == "click":
                return self._execute_click(params)
            elif action_type == "type":
                return self._execute_type(params)
            elif action_type == "scroll":
                return self._execute_scroll(params)
            elif action_type == "wait":
                return self._execute_wait(params)
            elif action_type == "extract":
                return self._execute_extract(params)
            elif action_type == "complete":
                return self._execute_complete(params)
            else:
                return {
                    "success": False,
                    "message": f"Unknown action type: {action_type}"
                }
        except Exception as e:
            logger.error(f"Action execution failed: {e}")
            return {
                "success": False,
                "message": f"Execution error: {str(e)}"
            }
    
    def _execute_navigate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute navigation action."""
        url = params.get("url")
        if not url:
            return {"success": False, "message": "No URL provided"}
        
        # Add https:// if not present
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        
        success = self.browser.navigate(url)
        
        # Wait a bit for page to settle
        time.sleep(2)
        
        return {
            "success": success,
            "message": f"Navigated to {url}" if success else "Navigation failed",
            "data": {"url": self.browser.get_url()}
        }
    
    def _execute_click(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute click action."""
        selector = params.get("selector")
        text = params.get("text")
        
        if not selector and not text:
            return {"success": False, "message": "No selector or text provided"}
        
        # Try to find element by text if no selector
        if not selector and text:
            selector = self.perception.find_element_by_text(text)
            if not selector:
                return {"success": False, "message": f"Could not find element with text: {text}"}
        
        success = self.browser.click(selector)
        
        # Wait for potential page changes
        time.sleep(1)
        
        return {
            "success": success,
            "message": f"Clicked {selector}" if success else "Click failed"
        }
    
    def _execute_type(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute typing action."""
        selector = params.get("selector")
        text = params.get("text")
        
        if not selector or text is None:
            return {"success": False, "message": "Selector and text required"}
        
        success = self.browser.type_text(selector, text)
        
        return {
            "success": success,
            "message": f"Typed into {selector}" if success else "Typing failed"
        }
    
    def _execute_scroll(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute scroll action."""
        direction = params.get("direction", "down")
        amount = params.get("amount", 500)
        
        success = self.browser.scroll(direction, amount)
        
        # Wait for content to load
        time.sleep(1)
        
        return {
            "success": success,
            "message": f"Scrolled {direction}" if success else "Scroll failed"
        }
    
    def _execute_wait(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute wait action."""
        selector = params.get("selector")
        timeout = params.get("timeout", 5000)
        
        if not selector:
            # Just wait for a fixed time
            time.sleep(timeout / 1000)
            return {"success": True, "message": f"Waited {timeout}ms"}
        
        success = self.browser.wait_for_selector(selector, timeout)
        
        return {
            "success": success,
            "message": f"Element appeared: {selector}" if success else "Wait timeout"
        }
    
    def _execute_extract(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data extraction action."""
        data_type = params.get("data_type", "text")
        
        if data_type == "text":
            data = self.browser.get_page_text()
        elif data_type == "title":
            data = self.browser.get_title()
        elif data_type == "url":
            data = self.browser.get_url()
        elif data_type == "forms":
            data = self.perception.get_form_fields()
        else:
            data = self.perception.get_page_state()
        
        return {
            "success": True,
            "message": f"Extracted {data_type}",
            "data": data
        }
    
    def _execute_complete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mark task as complete."""
        result = params.get("result", "Task completed")
        
        return {
            "success": True,
            "message": "Task marked as complete",
            "data": {"result": result},
            "complete": True
        }
    
    def validate_action(self, action: Dict[str, Any]) -> bool:
        """
        Validate that an action has required parameters.
        
        Args:
            action: Action dictionary
            
        Returns:
            True if valid, False otherwise
        """
        action_type = action.get("action", "").lower()
        params = action.get("params", {})
        
        required_params = {
            "navigate": ["url"],
            "click": [],  # Either selector or text
            "type": ["selector", "text"],
            "scroll": [],
            "wait": [],
            "extract": [],
            "complete": []
        }
        
        if action_type not in required_params:
            return False
        
        # Check required params
        for param in required_params[action_type]:
            if param not in params:
                logger.warning(f"Missing required parameter '{param}' for action '{action_type}'")
                return False
        
        return True
