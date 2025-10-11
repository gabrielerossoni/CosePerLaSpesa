# Overview

This is a Telegram shopping list bot built with Python that helps users manage their grocery lists with AI-powered features. The bot supports Italian language and includes intelligent suggestions, automatic categorization, meal planning, and conversational AI assistance. It's designed for deployment on Railway with 24/7 uptime and includes both a Telegram bot interface and a Flask web monitoring dashboard.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Bot Framework & Deployment Strategy

**Problem**: Need a Telegram bot that runs continuously with monitoring capabilities and can be deployed to cloud platforms.

**Solution**: Dual-process architecture with separate bot runner and web server processes.

- **Bot Process** (`bot_runner.py`): Dedicated Python Telegram Bot API process handling all Telegram interactions
- **Web Process** (`main.py`): Flask/Gunicorn server providing health monitoring and status endpoints
- **Process Management**: Both processes run concurrently via Railway's start command using background execution (`&`)

**Rationale**: Separating concerns allows the bot to operate independently while providing HTTP endpoints for platform health checks and monitoring. The Railway deployment uses Gunicorn with 2 workers and 240-second timeout for stability.

## Data Persistence

**Problem**: Shopping lists need to persist across bot restarts and be accessible per-user and per-group.

**Solution**: JSON file-based storage with intelligent list identification.

- **Storage Layer** (`storage.py`): Abstraction for reading/writing JSON data with error handling
- **List Identification**: Uses `group_{id}` for group chats and `user_{id}` for private chats (distinguishes by negative chat_id for groups)
- **Data Format**: Structured items with name, quantity, and category fields
- **Migration Support**: Automatic conversion from old format (string lists) to new format (dictionaries)

**Rationale**: JSON storage is simple, human-readable, and sufficient for the scale. The dual identification system ensures lists are properly scoped to their context.

## AI Integration with Fallback

**Problem**: Need AI features (suggestions, categorization, meal planning) with resilience against API failures or quota limits.

**Solution**: Multi-tier fallback system with primary and secondary AI providers via OpenRouter.

- **Primary**: DeepSeek V3.1 (free) via OpenRouter for intelligent responses
- **Secondary**: Llama 3.1 8B (free) via OpenRouter as fallback
- **Tertiary**: Local rule-based AI (`ai_fallback.py`) with hardcoded suggestions and templates

**Architecture**:
```
AIAssistant
├── _get_openai_response() → Try DeepSeek V3.1
│   └── Fallback to Llama 3.1 8B
└── LocalAI → Pattern-based responses
```

**Rationale**: Using OpenRouter provides access to free, high-quality models while ensuring the bot remains functional even when external APIs are unavailable or rate-limited. The local fallback provides basic but reliable functionality.

## Shopping List Management

**Problem**: Users need to add items with flexible quantity formats and organize by categories.

**Solution**: Pattern-based parsing with automatic categorization.

- **Quantity Parsing**: Regex patterns supporting multiple formats:
  - `2 kg di patate` (quantity + unit + "di" + name)
  - `3 mele` (quantity + name)  
  - `pomodori (500g)` (name + quantity in parentheses)
- **Category System**: Predefined categories with emoji mappings for visual organization
- **Data Corruption Repair**: Built-in `_repair_corrupted_data()` method to clean malformed entries

**Rationale**: Flexible parsing accommodates natural language input while maintaining structured data. Category system improves list readability and shopping efficiency.

## User Interface

**Problem**: Provide intuitive bot interaction with both commands and visual buttons.

**Solution**: Dual interface with text commands and inline keyboards.

- **Text Commands**: Traditional `/command` format for power users
- **Inline Keyboards**: Button-based interface with callbacks for common actions
- **Conversation States**: State machine for multi-step flows (add item → set quantity)
- **Reply Keyboards**: Persistent bottom keyboard with frequently used actions

**Constants Management**: Centralized message templates and UI strings in `constants.py` for easy localization and maintenance.

**Message Formatting**: Text formatting uses emoji indicators (📍 for list type) instead of Markdown to avoid display issues with special characters like underscores and asterisks.

**Rationale**: Accommodates different user preferences and skill levels. Buttons reduce typing for mobile users while commands provide speed for experienced users. Clean text formatting ensures messages display correctly on all Telegram clients.

# External Dependencies

## Telegram Bot API
- **Library**: `python-telegram-bot` 
- **Purpose**: Core bot framework for handling updates, commands, callbacks, and conversations
- **Integration**: Async/await pattern with ApplicationBuilder and various handler types

## OpenRouter API
- **Models**: DeepSeek V3.1 (primary, free), Llama 3.1 8B (fallback, free)
- **Endpoint**: `https://openrouter.ai/api/v1/chat/completions`
- **Purpose**: AI-powered suggestions, categorization, meal planning, and conversational assistance
- **Authentication**: Bearer token via `OPENROUTER_API_KEY` environment variable

## Web Server Stack
- **Flask**: Web framework for monitoring dashboard and health endpoints
- **Gunicorn**: WSGI production server (2 workers, 240s timeout)
- **Keep-Alive Service**: Separate Flask instance on port 9292/9393 to prevent sleeping on free tiers

## Deployment Platform
- **Railway**: Primary cloud hosting platform
- **Configuration**: `.railway.json` with custom build/deploy commands
- **Health Checks**: `/status` endpoint with 240s timeout
- **Restart Policy**: ON_FAILURE with max 10 retries

## Environment Variables
- `TELEGRAM_TOKEN`: Bot authentication token from BotFather
- `OPENROUTER_API_KEY`: OpenRouter API authentication key for AI features
- `SESSION_SECRET`: Flask session encryption key
- `PORT`: Server port (auto-assigned by Railway)

## Data Storage
- **Format**: JSON files (`shopping_lists.json`)
- **Location**: Local filesystem (persisted in deployment environment)
- **Encoding**: UTF-8 with non-ASCII support for Italian characters