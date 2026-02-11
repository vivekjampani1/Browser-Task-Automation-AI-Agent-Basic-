# AI Browser Automation Agent 🤖

A powerful AI-powered browser automation agent that can understand natural language tasks and autonomously execute them in a web browser using **Google Gemini** and Playwright.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Playwright](https://img.shields.io/badge/Playwright-Latest-green.svg)](https://playwright.dev/)
[![Gemini](https://img.shields.io/badge/Google-Gemini-orange.svg)](https://ai.google.dev/)

## 🌟 Features

- **Natural Language Understanding**: Describe tasks in plain English
- **Autonomous Execution**: AI plans and executes multi-step workflows
- **Vision Capabilities**: Understands page layouts using Gemini Vision
- **Robust Element Detection**: Multiple strategies for finding and interacting with elements
- **Cost-Effective**: Uses Google Gemini's generous free tier (1,500 requests/day)
- **Error Handling**: Automatic retries and fallback mechanisms
- **Comprehensive Logging**: Rich console output and detailed log files
- **Flexible Configuration**: Easy customization via environment variables

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or navigate to the project directory
cd ai-browser-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### 2. Configuration

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your Google Gemini API key
# Get your free API key from: https://aistudio.google.com/apikey
# GEMINI_API_KEY=your_api_key_here
```

### 3. Run Your First Task

```bash
# Simple command-line usage
python agent.py "Go to google.com and search for Python tutorials"

# Or use the example scripts
python examples/google_search.py
```

## 📖 Usage

### Command Line

```bash
python agent.py "<your task description>"
```

### Python API

```python
from agent import BrowserAgent

# Using context manager (recommended)
with BrowserAgent() as agent:
    result = agent.execute_task("Go to example.com and click the login button")
    print(f"Task completed: {result['completed']}")

# Manual initialization
agent = BrowserAgent()
agent.initialize()
result = agent.execute_task("Your task here")
agent.cleanup()
```

### With Vision Analysis

```python
with BrowserAgent() as agent:
    result = agent.execute_task(
        "Extract product prices from amazon.com",
        use_vision=True  # Enables Gemini Vision
    )
```

## 🎯 Example Tasks

The agent can handle various automation tasks:

### Web Search
```python
"Go to google.com and search for 'machine learning courses'"
```

### Form Filling
```python
"Navigate to contact form and fill in name: John, email: john@example.com"
```

### Data Extraction
```python
"Go to news.ycombinator.com and get the top 5 story titles"
```

### Multi-Step Workflows
```python
"Go to github.com, search for 'playwright', and click the first result"
```

## 🏗️ Architecture

```
┌─────────────────┐
│  User Task      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LLM Agent      │  ← Understands task & plans actions
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Perception     │  ← Analyzes page state
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Action         │  ← Executes browser actions
│  Executor       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Browser        │  ← Playwright automation
│  Controller     │
└─────────────────┘
```

## 📁 Project Structure

```
ai-browser-agent/
├── agent.py                 # Main orchestrator
├── browser_controller.py    # Playwright wrapper
├── perception.py            # Page analysis
├── llm_agent.py            # Google Gemini integration
├── action_executor.py       # Action execution
├── config.py               # Configuration
├── requirements.txt        # Dependencies
├── .env.example           # Environment template
├── utils/
│   └── logger.py          # Logging utilities
├── examples/
│   ├── google_search.py   # Search example
│   ├── form_filling.py    # Form example
│   └── data_extraction.py # Extraction example
├── logs/                  # Log files
└── screenshots/           # Error screenshots
```

## ⚙️ Configuration

Edit `.env` file to customize behavior:

```bash
# Required
GEMINI_API_KEY=your_key_here

# Optional
GEMINI_MODEL=models/gemini-2.0-flash
GEMINI_VISION_MODEL=models/gemini-2.0-flash
HEADLESS=false                    # Run browser in headless mode
BROWSER_TYPE=chromium             # chromium, firefox, or webkit
MAX_STEPS=50                      # Maximum steps per task
TIMEOUT_MS=30000                  # Element timeout
SCREENSHOT_ON_ERROR=true          # Save screenshots on errors
LOG_LEVEL=INFO                    # DEBUG, INFO, WARNING, ERROR
```

## 🔧 Advanced Usage

### Custom Actions

```python
from agent import BrowserAgent

agent = BrowserAgent()
agent.initialize()

# Access components directly
agent.browser.navigate("https://example.com")
agent.browser.click("#login-button")
agent.browser.type_text("#username", "myuser")

# Get page state
state = agent.perception.get_page_state()
print(state)

agent.cleanup()
```

### Error Handling

```python
with BrowserAgent() as agent:
    try:
        result = agent.execute_task("Complex task")
        if not result['completed']:
            print(f"Task incomplete: {result['verification']}")
    except Exception as e:
        print(f"Error: {e}")
        # Screenshots saved automatically if SCREENSHOT_ON_ERROR=true
```

## 🧪 Testing

Run the example scripts to test functionality:

```bash
# Test basic search
python examples/google_search.py

# Test form filling
python examples/form_filling.py

# Test data extraction with vision
python examples/data_extraction.py
```

## 🛠️ Technology Stack

- **Python 3.8+**: Core language
- **Playwright**: Browser automation
- **Google Gemini**: Task understanding and planning
- **Gemini Vision**: Visual page analysis
- **BeautifulSoup**: HTML parsing
- **Rich**: Beautiful console output

## 📊 Capabilities

| Feature | Status |
|---------|--------|
| Navigation | ✅ |
| Clicking | ✅ |
| Text Input | ✅ |
| Form Filling | ✅ |
| Scrolling | ✅ |
| Data Extraction | ✅ |
| Vision Analysis | ✅ |
| Multi-step Tasks | ✅ |
| Error Recovery | ✅ |
| Screenshot Capture | ✅ |

## 🔒 Security & Ethics

- Never share your Gemini API key (keep `.env` file private)
- Respect website terms of service and robots.txt
- Implement rate limiting for production use
- Don't automate prohibited activities
- Handle user credentials securely
- Monitor your API usage at https://ai.dev/rate-limit

## 🐛 Troubleshooting

### "GEMINI_API_KEY is required"
- Make sure you've created `.env` file from `.env.example`
- Get your free API key from https://aistudio.google.com/apikey
- Add your Gemini API key to the `.env` file

### "Browser failed to launch"
- Run `playwright install chromium` to install browser
- Check if you have sufficient permissions

### "Element not found"
- The agent will try multiple strategies automatically
- Increase `TIMEOUT_MS` in `.env` for slower websites
- Enable vision mode for better element detection

### Task not completing
- Check logs in `logs/` directory for details
- Increase `MAX_STEPS` if task is complex
- Simplify task description or break into smaller tasks

## 📝 Logging

Logs are saved in two places:

1. **Console**: Rich formatted output with colors
2. **File**: `logs/agent_YYYYMMDD.log` with detailed information

Set `LOG_LEVEL=DEBUG` in `.env` for verbose logging.

## 🚧 Limitations

- Requires Google Gemini API key (free tier: 1,500 requests/day)
- May struggle with complex CAPTCHAs
- Performance depends on LLM response time
- Not suitable for real-time applications
- Limited to websites accessible without authentication (unless credentials provided)
- Free tier has daily quota limits (upgrade to paid for unlimited)

## 🔮 Future Enhancements

- [ ] Support for other LLM providers (Anthropic, local models)
- [ ] Memory/context persistence across sessions
- [ ] Parallel task execution
- [ ] Visual regression testing
- [ ] Chrome extension interface
- [ ] Task recording and replay
- [ ] Integration with workflow tools

## 📄 License

This project is provided as-is for educational and research purposes.

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- Better element detection strategies
- Support for more complex authentication flows
- Enhanced error recovery
- Performance optimizations
- Additional example scripts

## 📚 Resources

- [Playwright Documentation](https://playwright.dev)
- [Google Gemini API Reference](https://ai.google.dev/gemini-api/docs)
- [Get Gemini API Key](https://aistudio.google.com/apikey)
- [Gemini Rate Limits](https://ai.google.dev/gemini-api/docs/rate-limits)

## 💡 Tips

1. **Start Simple**: Test with simple tasks first
2. **Be Specific**: Clear task descriptions work best
3. **Monitor Quota**: Free tier has 1,500 requests/day
4. **Use Vision Sparingly**: Vision analysis uses more tokens
5. **Check Logs**: Detailed logs help debug issues
6. **Upgrade if Needed**: $5 = ~10,000 tasks with paid tier

## 🎓 Learning Path

1. Run the example scripts
2. Modify examples for your use cases
3. Create custom tasks
4. Explore the codebase
5. Extend with new capabilities

---

**Built with ❤️ using Google Gemini and Playwright**

## 🎯 Getting Started

1. **Get your free Gemini API key**: https://aistudio.google.com/apikey
2. **Clone and setup** the project (see Quick Start above)
3. **Run your first task**: `python agent.py "Go to example.com"`
4. **Explore examples**: Check the `examples/` directory

For questions or issues, check the logs or review the code comments for detailed documentation.
