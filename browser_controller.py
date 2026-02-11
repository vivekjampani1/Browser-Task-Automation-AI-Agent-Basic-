"""
Browser Controller - Manages browser automation with Playwright.
Provides high-level interface for browser interactions.
"""
from playwright.sync_api import sync_playwright, Browser, Page, BrowserContext
from typing import Optional, Dict, Any, List
from pathlib import Path
import base64
from datetime import datetime

from config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)


class BrowserController:
    """Controls browser automation using Playwright."""
    
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
    def start(self) -> None:
        """Initialize and launch the browser."""
        logger.info(f"Starting {Config.BROWSER_TYPE} browser (headless={Config.HEADLESS})")
        
        self.playwright = sync_playwright().start()
        
        # Launch browser based on config
        if Config.BROWSER_TYPE == "chromium":
            self.browser = self.playwright.chromium.launch(headless=Config.HEADLESS)
        elif Config.BROWSER_TYPE == "firefox":
            self.browser = self.playwright.firefox.launch(headless=Config.HEADLESS)
        elif Config.BROWSER_TYPE == "webkit":
            self.browser = self.playwright.webkit.launch(headless=Config.HEADLESS)
        else:
            raise ValueError(f"Unsupported browser type: {Config.BROWSER_TYPE}")
        
        # Create context and page
        self.context = self.browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )
        self.page = self.context.new_page()
        self.page.set_default_timeout(Config.TIMEOUT_MS)
        
        logger.info("Browser started successfully")
    
    def navigate(self, url: str) -> bool:
        """
        Navigate to a URL.
        
        Args:
            url: The URL to navigate to
            
        Returns:
            True if navigation successful, False otherwise
        """
        try:
            logger.info(f"Navigating to: {url}")
            self.page.goto(url, wait_until="domcontentloaded")
            self.page.wait_for_load_state("networkidle", timeout=10000)
            logger.info(f"Successfully navigated to: {url}")
            return True
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return False
    
    def click(self, selector: str, timeout: Optional[int] = None) -> bool:
        """
        Click an element.
        
        Args:
            selector: CSS selector or text to click
            timeout: Optional timeout in milliseconds
            
        Returns:
            True if click successful, False otherwise
        """
        try:
            logger.debug(f"Clicking: {selector}")
            
            # Try multiple strategies
            if timeout:
                self.page.click(selector, timeout=timeout)
            else:
                self.page.click(selector)
            
            logger.info(f"Clicked: {selector}")
            return True
        except Exception as e:
            logger.error(f"Click failed for '{selector}': {e}")
            return False
    
    def type_text(self, selector: str, text: str, clear: bool = True) -> bool:
        """
        Type text into an element.
        
        Args:
            selector: CSS selector of the input element
            text: Text to type
            clear: Whether to clear existing text first
            
        Returns:
            True if typing successful, False otherwise
        """
        try:
            logger.debug(f"Typing into {selector}: {text[:50]}...")
            
            if clear:
                self.page.fill(selector, text)
            else:
                self.page.type(selector, text)
            
            logger.info(f"Typed text into: {selector}")
            return True
        except Exception as e:
            logger.error(f"Typing failed for '{selector}': {e}")
            return False
    
    def screenshot(self, name: Optional[str] = None) -> str:
        """
        Take a screenshot of the current page.
        
        Args:
            name: Optional name for the screenshot file
            
        Returns:
            Path to the screenshot file
        """
        if not name:
            name = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        filepath = Path(Config.SCREENSHOTS_DIR) / f"{name}.png"
        self.page.screenshot(path=str(filepath), full_page=False)
        logger.debug(f"Screenshot saved: {filepath}")
        
        return str(filepath)
    
    def screenshot_base64(self) -> str:
        """
        Take a screenshot and return as base64 string.
        
        Returns:
            Base64 encoded screenshot
        """
        screenshot_bytes = self.page.screenshot()
        return base64.b64encode(screenshot_bytes).decode('utf-8')
    
    def get_page_content(self) -> str:
        """
        Get the full HTML content of the current page.
        
        Returns:
            HTML content as string
        """
        return self.page.content()
    
    def get_page_text(self) -> str:
        """
        Get all visible text from the current page.
        
        Returns:
            Visible text content
        """
        return self.page.inner_text("body")
    
    def get_url(self) -> str:
        """Get the current page URL."""
        return self.page.url
    
    def get_title(self) -> str:
        """Get the current page title."""
        return self.page.title()
    
    def wait_for_selector(self, selector: str, timeout: Optional[int] = None) -> bool:
        """
        Wait for an element to appear.
        
        Args:
            selector: CSS selector to wait for
            timeout: Optional timeout in milliseconds
            
        Returns:
            True if element appeared, False otherwise
        """
        try:
            self.page.wait_for_selector(selector, timeout=timeout or Config.TIMEOUT_MS)
            return True
        except Exception as e:
            logger.error(f"Wait failed for '{selector}': {e}")
            return False
    
    def scroll(self, direction: str = "down", amount: int = 500) -> bool:
        """
        Scroll the page.
        
        Args:
            direction: 'up' or 'down'
            amount: Number of pixels to scroll
            
        Returns:
            True if scroll successful
        """
        try:
            if direction == "down":
                self.page.evaluate(f"window.scrollBy(0, {amount})")
            else:
                self.page.evaluate(f"window.scrollBy(0, -{amount})")
            return True
        except Exception as e:
            logger.error(f"Scroll failed: {e}")
            return False
    
    def execute_javascript(self, script: str) -> Any:
        """
        Execute JavaScript in the page context.
        
        Args:
            script: JavaScript code to execute
            
        Returns:
            Result of the script execution
        """
        try:
            return self.page.evaluate(script)
        except Exception as e:
            logger.error(f"JavaScript execution failed: {e}")
            return None
    
    def get_interactive_elements(self) -> List[Dict[str, Any]]:
        """
        Get all interactive elements on the page.
        
        Returns:
            List of element information dictionaries
        """
        script = """
        () => {
            const elements = [];
            const selectors = 'a, button, input, textarea, select, [onclick], [role="button"]';
            const nodes = document.querySelectorAll(selectors);
            
            nodes.forEach((el, idx) => {
                const rect = el.getBoundingClientRect();
                if (rect.width > 0 && rect.height > 0) {
                    elements.push({
                        tag: el.tagName.toLowerCase(),
                        type: el.type || '',
                        text: el.innerText?.substring(0, 100) || '',
                        placeholder: el.placeholder || '',
                        id: el.id || '',
                        class: el.className || '',
                        visible: rect.top >= 0 && rect.top <= window.innerHeight,
                        position: {
                            x: rect.left,
                            y: rect.top,
                            width: rect.width,
                            height: rect.height
                        }
                    });
                }
            });
            
            return elements;
        }
        """
        
        try:
            return self.page.evaluate(script)
        except Exception as e:
            logger.error(f"Failed to get interactive elements: {e}")
            return []
    
    def close(self) -> None:
        """Close the browser and cleanup."""
        logger.info("Closing browser")
        
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        
        logger.info("Browser closed")
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
