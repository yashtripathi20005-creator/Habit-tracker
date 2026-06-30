"""
Configuration file for the Habit Tracker application
"""

import os

# Database configuration
DB_NAME = "habits.db"
DB_PATH = os.path.join(os.path.dirname(__file__), DB_NAME)

# Habit frequencies
FREQUENCIES = {
    "daily": 1,
    "weekly": 7,
    "monthly": 30
}

# Color codes for terminal output
COLORS = {
    "RESET": "\033[0m",
    "RED": "\033[91m",
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "BLUE": "\033[94m",
    "MAGENTA": "\033[95m",
    "CYAN": "\033[96m",
    "WHITE": "\033[97m",
    "BOLD": "\033[1m"
}

# Habit categories
CATEGORIES = [
    "Health",
    "Fitness",
    "Learning",
    "Work",
    "Personal",
    "Social",
    "Other"
]

# Messages
WELCOME_MESSAGE = """
╔═══════════════════════════════════════════════════╗
║             🌟 HABIT TRACKER 🌟                  ║
║         Build better habits, one day at a time    ║
╚═══════════════════════════════════════════════════╝
"""

HELP_MESSAGE = """
📖 Available Commands:
  📋 list              - Show all habits
  ➕ add               - Add a new habit
  ✅ check             - Mark a habit as done
  📊 stats             - View habit statistics
  🔍 view              - View habit details
  ✏️ edit              - Edit a habit
  🗑️ delete            - Delete a habit
  📈 progress          - View progress chart
  📅 history           - View habit history
  💡 help              - Show this help message
  ❌ exit/quit         - Exit the application
"""
