# Telegram Shopping List Bot

Italian Telegram bot for shared shopping lists, item quantities, categorization and optional AI suggestions.

Repository: **CosePerLaSpesa**. Built with Python, python-telegram-bot, OpenAI and a Flask monitoring interface.

## Features

- Add, list, remove and clear shopping-list items.
- Keep quantities and group items into categories.
- Request meal ideas and shopping suggestions.
- Store lists between restarts; AI helpers include fallback paths.

## Commands

| Command | Purpose |
| --- | --- |
| `/aggiungi articolo` | Add an item |
| `/lista` | Show the list |
| `/rimuovi numero` | Remove an item |
| `/svuota` | Clear the list |
| `/categorie` | Group items by category |
| `/suggerisci` | Request suggestions |
| `/pasti` | Request meal ideas |
| `/ai domanda` | Ask the assistant |

## Setup and deployment

Use Python 3.11 or later, as declared in [pyproject.toml](pyproject.toml). The repository includes [uv.lock](uv.lock):

```sh
git clone https://github.com/gabrielerossoni/CosePerLaSpesa.git
cd CosePerLaSpesa
uv sync
```

Configure `TELEGRAM_TOKEN` and `OPENAI_API_KEY` in the hosting environment or your local environment. Never commit actual tokens.

[Procfile](Procfile) defines the service entry point. Follow [railway-deploy.md](railway-deploy.md) for Railway or [replit.md](replit.md) for the existing Replit setup. Hosting-specific instructions are separate from bot commands.

## Repository guide

- [telegram_bot.py](telegram_bot.py): Telegram interactions.
- [shopping_list.py](shopping_list.py) and [storage.py](storage.py): list management and persistence.
- [ai_assistant.py](ai_assistant.py) and [ai_fallback.py](ai_fallback.py): AI integration.
- [main.py](main.py), [bot_runner.py](bot_runner.py), [templates/](templates/): service and monitoring.
- [test_openai.py](test_openai.py): integration-oriented script; review required credentials and API costs before running.

## Data and project status

This is an existing personal project, not a hosted-service availability guarantee. Local list storage may contain user data; use fictional data for examples and screenshots. The repository currently has no project-wide license file granting reuse rights.
