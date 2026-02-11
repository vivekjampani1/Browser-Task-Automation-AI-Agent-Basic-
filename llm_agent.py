"""
LLM Agent - Interfaces with Google Gemini to plan and execute browser tasks.
"""
from typing import Dict, Any, List, Optional
import json
from google import genai
from google.genai import types

from config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)


class LLMAgent:
    """AI agent that uses Gemini to plan and execute browser tasks."""
    
    def __init__(self):
        Config.validate()
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        
    def understand_task(self, user_input: str) -> Dict[str, Any]:
        """
        Understand and parse the user's task.
        
        Args:
            user_input: Natural language task description
            
        Returns:
            Structured task information
        """
        logger.info(f"Understanding task: {user_input}")
        
        prompt = f"""You are an AI assistant that helps break down browser automation tasks.
Given a user's request, extract:
1. The main goal
2. The target website (if mentioned)
3. Key steps needed
4. Any specific data to extract or actions to perform

User request: {user_input}

Respond in JSON format with keys: goal, website, steps (array), data_to_extract (array)."""

        response = self.client.models.generate_content(
            model=Config.GEMINI_MODEL,
            contents=prompt
        )
        
        # Extract JSON from response
        text = response.text
        # Try to find JSON in the response
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        
        try:
            task_info = json.loads(text)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            task_info = {
                "goal": user_input,
                "website": "",
                "steps": [user_input],
                "data_to_extract": []
            }
        
        logger.info(f"Task understood: {task_info.get('goal', 'Unknown goal')}")
        
        return task_info
    
    def plan_next_action(self, task: str, page_state: Dict[str, Any], 
                        previous_actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Plan the next action to take based on current state.
        
        Args:
            task: The overall task description
            page_state: Current page state from perception module
            previous_actions: List of actions taken so far
            
        Returns:
            Next action to execute
        """
        logger.debug("Planning next action")
        
        # Build context
        context = self._build_context(task, page_state, previous_actions)
        
        prompt = f"""You are a browser automation agent. Based on the current page state and task, 
decide the next action to take.

Available actions:
- navigate: Go to a URL (params: url)
- click: Click an element (params: selector or text)
- type: Type text into a field (params: selector, text)
- scroll: Scroll the page (params: direction)
- wait: Wait for an element (params: selector)
- extract: Extract data from page (params: data_type)
- complete: Task is complete (params: result)

{context}

Respond in JSON format with keys: action, params, reasoning"""

        response = self.client.models.generate_content(
            model=Config.GEMINI_MODEL,
            contents=prompt
        )
        
        # Extract JSON from response
        text = response.text
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        
        try:
            action = json.loads(text)
        except json.JSONDecodeError:
            # Fallback action
            action = {
                "action": "complete",
                "params": {"result": "Unable to parse action"},
                "reasoning": "JSON parsing failed"
            }
        
        logger.info(f"Next action: {action.get('action')} - {action.get('reasoning', '')}")
        
        return action
    
    def _build_context(self, task: str, page_state: Dict[str, Any], 
                      previous_actions: List[Dict[str, Any]]) -> str:
        """Build context string for the LLM."""
        context_parts = [
            f"Task: {task}",
            f"\nCurrent URL: {page_state.get('url', 'Unknown')}",
            f"Page Title: {page_state.get('title', 'Unknown')}",
            f"Page Type: {page_state.get('page_type', 'Unknown')}",
        ]
        
        # Add visible text summary
        if page_state.get('visible_text'):
            context_parts.append(f"\nVisible Text (summary): {page_state['visible_text'][:500]}")
        
        # Add interactive elements
        if page_state.get('interactive_elements'):
            elements_str = "\n\nInteractive Elements:\n"
            for elem in page_state['interactive_elements'][:20]:  # Limit to 20
                elements_str += f"- [{elem['index']}] {elem['descriptor']}\n"
            context_parts.append(elements_str)
        
        # Add previous actions
        if previous_actions:
            actions_str = "\n\nPrevious Actions:\n"
            for i, action in enumerate(previous_actions[-5:]):  # Last 5 actions
                actions_str += f"{i+1}. {action.get('action')} - {action.get('params', {})}\n"
            context_parts.append(actions_str)
        
        return "".join(context_parts)
    
    def analyze_page_with_vision(self, screenshot_base64: str, task: str) -> Dict[str, Any]:
        """
        Analyze a page screenshot using vision model.
        
        Args:
            screenshot_base64: Base64 encoded screenshot
            task: The task being performed
            
        Returns:
            Analysis results
        """
        logger.debug("Analyzing page with vision model")
        
        prompt = f"I'm trying to: {task}\n\nWhat do you see on this page? What elements are visible? What should I interact with next?"
        
        # Decode base64 image
        import base64
        image_bytes = base64.b64decode(screenshot_base64)
        
        response = self.client.models.generate_content(
            model=Config.GEMINI_VISION_MODEL,
            contents=[
                types.Part.from_text(prompt),
                types.Part.from_bytes(data=image_bytes, mime_type="image/png")
            ]
        )
        
        analysis = response.text
        logger.info(f"Vision analysis: {analysis[:200]}...")
        
        return {
            "analysis": analysis,
            "suggestions": self._extract_suggestions(analysis)
        }
    
    def _extract_suggestions(self, analysis: str) -> List[str]:
        """Extract actionable suggestions from vision analysis."""
        suggestions = []
        
        if "click" in analysis.lower():
            suggestions.append("click")
        if "type" in analysis.lower() or "enter" in analysis.lower():
            suggestions.append("type")
        if "scroll" in analysis.lower():
            suggestions.append("scroll")
        
        return suggestions
    
    def verify_task_completion(self, task: str, page_state: Dict[str, Any], 
                               actions_taken: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Verify if the task has been completed successfully.
        
        Args:
            task: Original task description
            page_state: Current page state
            actions_taken: All actions taken
            
        Returns:
            Verification result with completion status
        """
        logger.debug("Verifying task completion")
        
        prompt = f"""Task: {task}

Current Page:
- URL: {page_state.get('url')}
- Title: {page_state.get('title')}
- Visible Text: {page_state.get('visible_text', '')[:300]}

Actions Taken: {len(actions_taken)} actions

Has the task been completed successfully? Respond in JSON with keys: completed (boolean), confidence (0-1), reasoning"""

        response = self.client.models.generate_content(
            model=Config.GEMINI_MODEL,
            contents=prompt
        )
        
        # Extract JSON from response
        text = response.text
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        
        try:
            result = json.loads(text)
        except json.JSONDecodeError:
            result = {
                "completed": False,
                "confidence": 0.5,
                "reasoning": "Unable to verify completion"
            }
        
        logger.info(f"Task completion: {result.get('completed')} (confidence: {result.get('confidence')})")
        
        return result
