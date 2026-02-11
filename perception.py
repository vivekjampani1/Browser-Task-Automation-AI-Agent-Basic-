"""
Perception Module - Extracts and analyzes page state.
Provides structured information about the current page for the LLM.
"""
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
import re

from browser_controller import BrowserController
from utils.logger import setup_logger

logger = setup_logger(__name__)


class PerceptionModule:
    """Analyzes and extracts information from web pages."""
    
    def __init__(self, browser: BrowserController):
        self.browser = browser
    
    def get_page_state(self) -> Dict[str, Any]:
        """
        Get comprehensive page state information.
        
        Returns:
            Dictionary containing page state information
        """
        logger.debug("Extracting page state")
        
        state = {
            "url": self.browser.get_url(),
            "title": self.browser.get_title(),
            "interactive_elements": self.get_simplified_elements(),
            "visible_text": self.get_visible_text_summary(),
            "page_type": self.detect_page_type(),
        }
        
        return state
    
    def get_simplified_elements(self) -> List[Dict[str, Any]]:
        """
        Get simplified list of interactive elements.
        
        Returns:
            List of element dictionaries with essential information
        """
        elements = self.browser.get_interactive_elements()
        
        simplified = []
        for idx, elem in enumerate(elements):
            # Only include visible elements
            if not elem.get("visible", False):
                continue
            
            # Create a simple descriptor
            descriptor = self._create_element_descriptor(elem)
            
            simplified.append({
                "index": idx,
                "type": elem["tag"],
                "descriptor": descriptor,
                "text": elem.get("text", "")[:100],
                "id": elem.get("id", ""),
                "class": elem.get("class", ""),
            })
        
        # Limit to top 50 elements to avoid overwhelming the LLM
        return simplified[:50]
    
    def _create_element_descriptor(self, elem: Dict[str, Any]) -> str:
        """
        Create a human-readable descriptor for an element.
        
        Args:
            elem: Element dictionary
            
        Returns:
            Descriptor string
        """
        parts = [elem["tag"]]
        
        if elem.get("id"):
            parts.append(f"#{elem['id']}")
        
        if elem.get("text"):
            text = elem["text"][:30].strip()
            if text:
                parts.append(f'"{text}"')
        
        if elem.get("placeholder"):
            parts.append(f'placeholder="{elem["placeholder"][:30]}"')
        
        return " ".join(parts)
    
    def get_visible_text_summary(self, max_length: int = 2000) -> str:
        """
        Get a summary of visible text on the page.
        
        Args:
            max_length: Maximum length of text to return
            
        Returns:
            Truncated visible text
        """
        text = self.browser.get_page_text()
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        return text
    
    def detect_page_type(self) -> str:
        """
        Detect the type of page (login, search, form, etc.).
        
        Returns:
            Page type string
        """
        content = self.browser.get_page_content().lower()
        title = self.browser.get_title().lower()
        
        # Simple heuristics
        if "login" in content or "sign in" in content or "password" in content:
            return "login"
        elif "search" in title or "search" in content[:500]:
            return "search"
        elif "checkout" in content or "cart" in content:
            return "checkout"
        elif "form" in content or "submit" in content:
            return "form"
        else:
            return "general"
    
    def extract_dom_tree(self) -> Dict[str, Any]:
        """
        Extract a simplified DOM tree structure.
        
        Returns:
            Simplified DOM tree
        """
        html = self.browser.get_page_content()
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Build simplified tree
        tree = self._build_tree_node(soup.body if soup.body else soup)
        
        return tree
    
    def _build_tree_node(self, element, max_depth: int = 3, current_depth: int = 0) -> Dict[str, Any]:
        """
        Recursively build a simplified tree node.
        
        Args:
            element: BeautifulSoup element
            max_depth: Maximum depth to traverse
            current_depth: Current depth in tree
            
        Returns:
            Tree node dictionary
        """
        if current_depth >= max_depth:
            return None
        
        node = {
            "tag": element.name if hasattr(element, 'name') else "text",
            "text": element.get_text()[:100] if hasattr(element, 'get_text') else str(element)[:100],
            "children": []
        }
        
        if hasattr(element, 'children'):
            for child in element.children:
                if hasattr(child, 'name'):
                    child_node = self._build_tree_node(child, max_depth, current_depth + 1)
                    if child_node:
                        node["children"].append(child_node)
        
        return node
    
    def find_element_by_text(self, text: str) -> Optional[str]:
        """
        Find an element selector by its text content.
        
        Args:
            text: Text to search for
            
        Returns:
            CSS selector if found, None otherwise
        """
        elements = self.browser.get_interactive_elements()
        
        for elem in elements:
            if text.lower() in elem.get("text", "").lower():
                # Try to build a selector
                if elem.get("id"):
                    return f"#{elem['id']}"
                elif elem.get("text"):
                    return f'text="{elem["text"][:50]}"'
        
        return None
    
    def get_form_fields(self) -> List[Dict[str, Any]]:
        """
        Extract all form fields from the page.
        
        Returns:
            List of form field information
        """
        script = """
        () => {
            const fields = [];
            const inputs = document.querySelectorAll('input, textarea, select');
            
            inputs.forEach(input => {
                fields.push({
                    tag: input.tagName.toLowerCase(),
                    type: input.type || '',
                    name: input.name || '',
                    id: input.id || '',
                    placeholder: input.placeholder || '',
                    required: input.required || false,
                    value: input.value || ''
                });
            });
            
            return fields;
        }
        """
        
        return self.browser.execute_javascript(script) or []
