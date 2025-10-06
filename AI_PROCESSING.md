# AI Processing Feature

Enhance your transcriptions with AI before typing them out. AnyWhisper uses **LiteLLM** to support 100+ LLM providers.

## Overview

The AI Processing feature allows you to:
- Enhance prompts with AI
- Generate bash commands from natural language
- Create custom AI transformations
- Chain AI processing with key actions

## How It Works

**Example:** Say "generate a html5 website, generate this as prompt, hit enter"

**Processing Order:**
1. **Transcription**: "generate a html5 website, generate this as prompt, hit enter."
2. **POST_TRANSCRIPTION_ACTIONS**: Removes "hit enter" → Action: ENTER
3. **POST_AI_TRIGGERS**: Detects "generate this as prompt", removes it
4. **AI Processing**: Enhances "generate a html5 website" with AI
5. **Text Injection**: Types the AI-enhanced output
6. **Key Action**: Presses ENTER

## Configuration

Edit `/path/to/AnyWhisper/config.py`:

### Enable AI Processing

```python
ENABLE_AI_PROCESSING = False  # Set to True to enable
```

### API Configuration

LiteLLM API settings (supports 100+ providers):

```python
# Your API key
AI_API_KEY = "your-api-key-here"

# Provider name
AI_PROVIDER = 'gemini'  # Options: gemini, openai, anthropic, groq, etc.

# Model name (without provider prefix)
# Gemini: 'gemini-2.5-flash-lite', 'gemini-2.0-flash-exp'
# OpenAI: 'gpt-4o', 'gpt-4o-mini'
# Anthropic: 'claude-sonnet-4-20250514', 'claude-3-5-sonnet-20241022'
AI_MODEL_NAME = 'gemini-2.5-flash-lite'
```

### Fast Text Injection (Recommended for AI)

AI responses are often long (100+ words). Use clipboard paste instead of typing:

```python
# Fast clipboard paste method (instant regardless of length)
USE_COPY_PASTE_METHOD = True  # Copies to clipboard + Shift+Insert

# Traditional typing method (slower for long text)
USE_COPY_PASTE_METHOD = False  # Types character-by-character
```

**Why enable this for AI?**
- AI-enhanced prompts can be 200+ words
- Clipboard paste is instant (< 0.1 seconds)
- Character-by-character typing takes 5-10 seconds for long text
- No visible typing animation (looks cleaner)
- Preserves your existing clipboard content (backs up and restores automatically)

**Requirements:**
- Wayland: `wl-copy` and `wl-paste` (usually pre-installed)
- X11: `xclip` (install: `sudo apt install xclip`)

**Clipboard Protection:** Your original clipboard content is automatically backed up before pasting and restored immediately after. This includes both the CLIPBOARD selection (Ctrl+C/V) and PRIMARY selection (mouse selection/middle-click), ensuring compatibility with terminals and text editors.

**Fallback:** Automatically falls back to typing if clipboard fails.

### AI Prompt Templates

Define your AI transformation templates:

```python
AI_PROMPT_TEMPLATES = {
    'ENHANCE_PROMPT_TEMPLATE': [
        {"role": "system", "content": "You are an AI enhancer assistant..."},
        {"role": "user", "content": "__USER_INPUT__"}
    ],
    'COMMAND_GENERATION_TEMPLATE': [
        {"role": "system", "content": "You are a bash command generator..."},
        {"role": "user", "content": "Generate a bash command for: __USER_INPUT__"}
    ],
}
```

**Placeholder:** Use `__USER_INPUT__` where you want the transcribed text inserted.

### AI Triggers

Map spoken phrases to AI templates:

```python
POST_AI_TRIGGERS = {
    r'whisper with ai':
    'GEN_AI_TEMPLATE',
    r'generate this as prompt': 'ENHANCE_PROMPT_TEMPLATE',
    r'generate as command': 'COMMAND_GENERATION_TEMPLATE',
}
```

## Usage Examples

### Example 1: Generate AI Response

**Say:** "Write a four line poem about the moon, whisper with AI."

**Processing:**
1. Transcription: "Write a four line poem about the moon, whisper with AI."
2. Detect "whisper with AI" (POST_AI_TRIGGERS)
4. AI generates the poem
5. AI output:
```
"A silver disc in velvet night,
She watches stars in silent flight.
A gentle glow, a mystic gleam,
Reflecting back a waking dream."
```

The poem is inserted into the currently selected text field.

### Example: Generate Bash Command

**Say:** "list all pdf files in current directory, generate as command, hit enter"

**Processing:**
1. Transcription: "list all pdf files in current directory, generate as command."
2. Remove "hit enter" (POST_TRANSCRIPTION_ACTIONS)
3. Detect "generate as command" (POST_AI_TRIGGERS)
4. AI generates command from: "list all pdf files in current directory"
5. AI output: `ls *.pdf`
6. Types: `ls *.pdf`
7. Presses ENTER → Command executes

### Example 3: VibeCoding - Extend Brief Instructions

**Say:** "add error handling, extend the vibe, hit enter"

**Processing:**
1. Transcription: "add error handling, extend the vibe."
2. Remove "hit enter" (POST_TRANSCRIPTION_ACTIONS)
3. Detect "extend the vibe" (POST_AI_TRIGGERS)
4. AI extends: "add error handling"
5. AI output: "Implement comprehensive error handling throughout the codebase. Add try-catch blocks for async operations, validate user inputs, handle edge cases gracefully, log errors appropriately, provide user-friendly error messages, and ensure the application fails gracefully without crashing. Follow best practices for the specific framework/language being used."
6. Types the extended prompt (instant if USE_COPY_PASTE_METHOD=True)
7. Presses ENTER

## Setup Guide

### 1. Get API Key

**For Gemini (Recommended - Free tier available):**
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click "Create API Key"
3. Copy your key

**For OpenAI:**
1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy your key

**For Anthropic:**
1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Create an API key
3. Copy your key

**For other providers:** Check LiteLLM's [provider documentation](https://docs.litellm.ai/docs/providers)

### 2. Configure in `config.py`

Open `config.py` and update:

```python
# Enable AI Processing
ENABLE_AI_PROCESSING = True

# Your API key
AI_API_KEY = "your-api-key-here"

# Provider name
AI_PROVIDER = 'gemini'  # Options: gemini, openai, anthropic, groq, etc.

# Model name (without provider prefix)
# Gemini: 'gemini-2.5-flash-lite', 'gemini-2.0-flash-exp'
# OpenAI: 'gpt-4o', 'gpt-4o-mini'
# Anthropic: 'claude-sonnet-4-20250514', 'claude-3-5-sonnet-20241022'
AI_MODEL_NAME = 'gemini-2.5-flash-lite'

# Enable fast clipboard paste for long AI responses
USE_COPY_PASTE_METHOD = True
```

**Example (Gemini):**
```python
ENABLE_AI_PROCESSING = True
AI_API_KEY = "AIzaSy..."  # Your Gemini API key
AI_PROVIDER = 'gemini'
AI_MODEL_NAME = 'gemini-2.5-flash-lite'
USE_COPY_PASTE_METHOD = True  # Recommended for AI
```

**Example (OpenAI):**
```python
ENABLE_AI_PROCESSING = True
AI_API_KEY = "sk-..."  # Your OpenAI API key
AI_PROVIDER = 'openai'
AI_MODEL_NAME = 'gpt-4o-mini'
USE_COPY_PASTE_METHOD = True
```

**Example (Anthropic):**
```python
ENABLE_AI_PROCESSING = True
AI_API_KEY = "sk-ant-..."  # Your Anthropic API key
AI_PROVIDER = 'anthropic'
AI_MODEL_NAME = 'claude-3-5-sonnet-20241022'
USE_COPY_PASTE_METHOD = True
```

### 3. Install LiteLLM Library

```bash
cd /path/to/AnyWhisper
source venv/bin/activate
pip install litellm
```

### 4. Install Clipboard Tool (for USE_COPY_PASTE_METHOD)

**For Wayland (usually pre-installed):**
```bash
# Check if wl-copy is available
which wl-copy
```

**For X11:**
```bash
sudo apt install xclip
```

### 5. Restart Daemon

```bash
systemctl --user restart any-whisper
# or
./start_daemon.sh
```

### 6. Test It

Say: "hello world, generate this as prompt"

Check the console output for AI processing logs.

## Processing Order

Understanding the order of operations is crucial:

```
1. Transcription
   ↓
2. POST_TRANSCRIPTION_ACTIONS (removes key trigger phrases like "hit enter")
   ↓
3. POST_AI_TRIGGERS (removes AI trigger phrases like "generate this as prompt")
   ↓
4. AI Processing (if triggered)
   ↓
5. Text Injection (types or pastes the final result)
   ↓
6. Key Action (if specified, like pressing ENTER)
```

**Example Flow:**

```
Input: "create login page, generate this as prompt, hit enter"

Step 1 - Transcription:
  "create login page, generate this as prompt, hit enter."

Step 2 - POST_TRANSCRIPTION_ACTIONS:
  Pattern: r'hit enter$'
  Result: "create login page, generate this as prompt"
  Action: ENTER (saved for later)

Step 3 - POST_AI_TRIGGERS:
  Pattern: r'generate this as prompt'
  Result: "create login page"
  Template: ENHANCE_PROMPT_TEMPLATE

Step 4 - AI Processing:
  Input: "create login page"
  Output: "Design and implement a secure login page with..."

Step 5 - Text Injection:
  If USE_COPY_PASTE_METHOD=True:
    - Copies to clipboard
    - Presses Shift+Insert (instant)
  Else:
    - Types character-by-character (5-10 seconds)

Step 6 - Key Action:
  Presses: ENTER
```

## Text Injection Performance

### Character-by-Character Typing (USE_COPY_PASTE_METHOD=False)

**Speed:** ~10-20 chars/second

| Text Length | Typing Time |
|-------------|-------------|
| 50 chars    | 2-5 seconds |
| 200 chars   | 10-20 seconds |
| 500 chars   | 25-50 seconds |

**Pros:**
- More compatible
- Visible typing animation

**Cons:**
- Slow for long text
- User sees each character appear

### Clipboard Paste (USE_COPY_PASTE_METHOD=True)

**Speed:** < 0.1 seconds regardless of length

| Text Length | Paste Time |
|-------------|------------|
| 50 chars    | < 0.1 sec  |
| 200 chars   | < 0.1 sec  |
| 500 chars   | < 0.1 sec  |
| 5000 chars  | < 0.1 sec  |

**Pros:**
- ⚡ Instant injection
- 🚀 Perfect for AI outputs (often 100-500 words)
- Clean (no typing animation)

**Cons:**
- Overwrites clipboard temporarily
- Requires wl-copy (Wayland) or xclip (X11)

**Recommendation:** Enable `USE_COPY_PASTE_METHOD=True` when using AI features, as AI responses are typically long.

## Custom Templates

Create your own AI transformations:

```python
AI_PROMPT_TEMPLATES = {
    # ... existing templates ...
    
    'CODE_REVIEW_TEMPLATE': [
        {"role": "system", "content": "You are an expert code reviewer. Analyze the code focusing on bugs, security issues, performance, best practices, and maintainability. Provide specific, actionable feedback."},
        {"role": "user", "content": "Review this code: __USER_INPUT__"}
    ],
    
    'TRANSLATE_TEMPLATE': [
        {"role": "system", "content": "Translate the following text to Spanish, maintaining the original tone and meaning."},
        {"role": "user", "content": "__USER_INPUT__"}
    ],
    
    'SUMMARIZE_TEMPLATE': [
        {"role": "system", "content": "Provide a concise summary in 2-3 sentences, capturing the key points and main ideas."},
        {"role": "user", "content": "__USER_INPUT__"}
    ],
}

POST_AI_TRIGGERS = {
    # ... existing triggers ...
    r'review code': 'CODE_REVIEW_TEMPLATE',
    r'translate to spanish': 'TRANSLATE_TEMPLATE',
    r'summarize it': 'SUMMARIZE_TEMPLATE',
}
```

## Advanced Usage

### Combining Multiple Features

**Chain everything together:**

Say: "generate docker compose file for postgres, generate this as prompt, hit enter"

1. Removes "hit enter"
2. Removes "generate this as prompt"
3. AI enhances "generate docker compose file for postgres"
4. Pastes enhanced output (if USE_COPY_PASTE_METHOD=True)
5. Presses ENTER

### VibeCoding Integration

Perfect for expanding brief coding instructions:

```python
'VIBE_EXTEND_TEMPLATE': [
    {"role": "system", "content": "You are assisting with VibeCoding - a conversational AI-assisted coding workflow. The user is giving brief instructions to their AI coding assistant. Transform their concise input into a detailed, actionable prompt that provides context, specifies requirements, mentions best practices, and clearly defines the expected outcome. Make it developer-friendly and ready for an AI coding assistant to act upon. Return only the expanded prompt."},
    {"role": "user", "content": "__USER_INPUT__"}
],
```

Trigger: `r'extend the vibe': 'VIBE_EXTEND_TEMPLATE'`

**Usage Examples:**

**Brief:** "add auth, extend the vibe, hit enter"  
**Extended:** "Implement a complete authentication system with user registration, login, logout, password hashing (bcrypt), JWT token management, session handling, protected routes, and password reset functionality. Follow security best practices including input validation, rate limiting, and secure cookie handling. Ensure compatibility with the existing tech stack."

**Brief:** "refactor this, extend the vibe"  
**Extended:** "Refactor this code to improve readability, maintainability, and performance. Extract reusable functions, apply SOLID principles, add meaningful variable names, remove code duplication, optimize algorithms where possible, and ensure consistent code style. Include comments for complex logic and maintain existing functionality."

## Troubleshooting

### AI Processing Not Working

**Problem:** AI trigger phrase doesn't activate AI processing.

**Solutions:**
1. Check `ENABLE_AI_PROCESSING = True`
2. Verify `AI_API_KEY` is set
3. Check console for error messages
4. Ensure LiteLLM library is installed: `pip install litellm`
5. Test API key with a simple Python script

### Clipboard Paste Not Working

**Problem:** Text still types character-by-character even with `USE_COPY_PASTE_METHOD=True`.

**Solutions:**
1. **Wayland:** Check if `wl-copy` is installed: `which wl-copy`
2. **X11:** Install xclip: `sudo apt install xclip`
3. Check console for error messages like "Clipboard paste failed"
4. The system automatically falls back to typing if clipboard fails

### API Errors

**Problem:** Getting API errors in console.

**Solutions:**
1. **Invalid API key**: Check your API key is correct
2. **Quota exceeded**: Check your API usage limits
3. **Network issues**: Verify internet connection
4. **Model not found**: Check model name spelling

### Console Error Examples:

```
⚠️  AI_API_KEY not configured, skipping AI processing
→ Set AI_API_KEY in config.py

⚠️  Template 'UNKNOWN_TEMPLATE' not found
→ Check template name in POST_AI_TRIGGERS matches AI_PROMPT_TEMPLATES

⚠️  AI processing failed: 401 Unauthorized
→ Check your API key is valid

⚠️  Clipboard paste failed: [Errno 2] No such file or directory: 'wl-copy'
→ Install wl-copy or xclip, falling back to typing
```

### Slow Response

**Problem:** AI processing takes a long time.

**Solutions:**
1. Use faster models:
   - Gemini: `gemini-2.5-flash-lite` (very fast)
   - OpenAI: `gpt-4o-mini` (fast and cheap)
2. optimize the prompt template


**Note:** Even with slow AI processing, enable `USE_COPY_PASTE_METHOD=True` to make text injection instant once AI responds.

### Period Handling

AI triggers also respect `POST_TRANSCRIPTION_OPT_DOT`:

```python
POST_TRANSCRIPTION_OPT_DOT = True  # "generate this as prompt" matches "generate this as prompt."
```

## Security Notes

- API keys are stored in `config.py` (keep this file secure)
- Consider using environment variables for API keys:

```python
import os
AI_API_KEY = os.getenv('ANYWHISPER_API_KEY', '')
```

Then set: `export ANYWHISPER_API_KEY="your-key"`

## Examples for VibeCoding

### Prompt Enhancement

**Say:** "add login functionality, generate this as prompt, hit enter"

**Result:** AI expands this into a detailed, actionable prompt with specifics about JWT, security, validation, error handling, etc.

### VibeCoding Extension

**Say:** "optimize performance, extend the vibe, hit enter"

**Result:** AI transforms brief instruction into comprehensive optimization guidance including code splitting, lazy loading, memoization, caching strategies, bundle size reduction, and performance monitoring.

### Command Generation

**Say:** "install all npm packages with legacy peer deps, generate as command, hit enter"

**Result:** `npm install --legacy-peer-deps` is typed and executed.

### Basic Prompt

**Say:** "Center the div, make no mistakes hit enter"

**Result:**
```
Center the div, make no mistakes
[ENTER pressed - your AI agent starts working]
```

### Extended VibeCoding Prompt

**Say:** "make it responsive, extend the vibe, hit enter"

**Result:**
```
Implement responsive design for this component. Add CSS media queries for mobile (320px-767px), tablet (768px-1023px), and desktop (1024px+) breakpoints. Ensure proper scaling of fonts, images, and layout. Use flexible units (rem, em, %) instead of fixed pixels. Test touch interactions for mobile devices. Maintain visual hierarchy and readability across all screen sizes. Consider mobile-first approach and progressive enhancement.
[ENTER pressed - AI coding assistant receives detailed instructions]
```

## Disabling AI Processing

To disable:

```python
ENABLE_AI_PROCESSING = False  # Just flip to False
```

AI triggers will be ignored and text will be typed as-is.

## Restart After Changes

Always restart after changing config:

```bash
systemctl --user restart any-whisper
```
