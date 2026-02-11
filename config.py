"""
Configuration management for the AI Browser Agent.
Loads settings from environment variables and provides defaults.
"""
import os
from dotenv import load_dotenv
from typing import Literal

# Load environment variables
load_dotenv()

class Config:
    """Central configuration for the browser agent."""
    
    # Gemini Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "models/gemini-1.5-flash-latest")
    GEMINI_VISION_MODEL: str = os.getenv("GEMINI_VISION_MODEL", "models/gemini-1.5-flash-latest")
    
    # Browser Configuration
    HEADLESS: bool = os.getenv("HEADLESS", "false").lower() == "true"
    BROWSER_TYPE: Literal["chromium", "firefox", "webkit"] = os.getenv("BROWSER_TYPE", "chromium")
    
    # Agent Configuration
    MAX_STEPS: int = int(os.getenv("MAX_STEPS", "50"))
    TIMEOUT_MS: int = int(os.getenv("TIMEOUT_MS", "30000"))
    SCREENSHOT_ON_ERROR: bool = os.getenv("SCREENSHOT_ON_ERROR", "true").lower() == "true"
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Directories
    SCREENSHOTS_DIR: str = "screenshots"
    LOGS_DIR: str = "logs"
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present."""
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required. Please set it in .env file.")
        return True

# Create directories if they don't exist
os.makedirs(Config.SCREENSHOTS_DIR, exist_ok=True)
os.makedirs(Config.LOGS_DIR, exist_ok=True)
