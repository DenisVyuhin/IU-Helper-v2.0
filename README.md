# Telegram Bot for School Homework Management

## Overview
This is a Russian-language Telegram bot built with aiogram that helps students manage and share homework assignments. It includes features for posting homework, searching for assignments, user statistics tracking, and AI-powered assistance.

## Project Structure
```
.
├── app/
│   ├── assets/          # Media assets
│   ├── database/        # SQLAlchemy models and database requests
│   │   ├── models.py    # User, Bot, Post models
│   │   └── requests.py  # Database query functions
│   ├── utils/           # Utility functions
│   │   ├── json_requests.py  # JSON file operations
│   │   ├── mistral.py   # AI integration (Mistral AI & DeepSeek)
│   │   └── utils.py     # Helper functions
│   ├── handlers.py      # Main bot command handlers and callbacks
│   ├── keyboards.py     # Inline keyboard builders
│   └── middlewares.py   # Bot middlewares (blocking, rate limiting)
├── run.py              # Main entry point
├── constants.py        # Configuration constants
├── db.sqlite3          # SQLite database
├── banned.json         # Banned users list
└── stats.json          # User statistics
```

## Technology Stack
- **Framework**: aiogram 3.22.0 (Telegram Bot API)
- **Database**: SQLite with SQLAlchemy 2.0.44 + aiosqlite
- **AI Integration**: Mistral AI & OpenAI (DeepSeek via OpenRouter)
- **Scheduling**: aioschedule for automated tasks
- **Environment**: Python 3.12

## Key Features
1. **Homework Management**
   - Post homework with photos/files
   - Search by grade, subject, quarter, and week
   - Tagging system for easy retrieval

2. **User System**
   - User profiles with statistics
   - Star-based reward system
   - Leaderboards (all-time and yearly)

3. **AI Features** (Optional)
   - Mistral AI integration for automated responses
   - DeepSeek fallback via OpenRouter

4. **Administrative Tools**
   - User blocking/unblocking
   - Operator chat system
   - Automated scheduled tasks

## Environment Variables
### Required
- `BOT_TOKEN` - Telegram Bot API token from @BotFather

### Optional (for AI features)
- `MISTRAL_API_KEY` - Mistral AI API key
- `DEEPSEEK_API_KEY` - DeepSeek/OpenRouter API key

## Database Schema
- **users**: User profiles (tg_id, name, posts count, stars)
- **bot**: Bot statistics (find_posts, published_posts, debit_stars)
- **posts**: Homework posts (post_id, key, tag, url)

## Scheduled Tasks
The bot runs daily tasks at 12:00:
- May 8: Announce yearly winners
- August 31: Clean old posts and reset yearly statistics

## Recent Changes (November 28, 2025)
- Imported from GitHub to Replit
- Configured Python 3.12 environment
- Installed all dependencies via uv package manager
- Set up workflow for running the bot
- Added BOT_TOKEN secret for production use
- Created requirements.txt for dependency tracking
- Updated .gitignore with Python-specific entries

## Running the Bot
The bot runs automatically via the "Telegram Bot" workflow. It executes:
```bash
python run.py
```

## Notes
- The bot is configured for Russian-language schools ("Интернет урок")
- Supports grades 7-11
- Uses inline keyboards for all user interactions
- Channel subscription requirement for homework search
- Built-in anti-spam middleware