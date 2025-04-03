import os
from pathlib import Path

# Context Window Monitor Configuration

# Default context window size (tokens)
CONTEXT_WINDOW_SIZE = 128000

# Warning threshold (percentage)
WARNING_THRESHOLD = 70

# Critical threshold (percentage)
CRITICAL_THRESHOLD = 85

# File patterns to monitor
FILE_PATTERNS = [
    "*.py",
    "*.md",
    "*.txt"
]

# Directories to monitor
MONITORED_DIRS = [
    "."
]

# Directories to ignore
IGNORED_DIRS = [
    "venv",
    "node_modules",
    ".git",
    "__pycache__",
    "data",
    "baseball_data",
    "census_data",
    "utils",
    "generators"
]

# Files to ignore
IGNORED_FILES = [
    "*.csv",
    "*.json",
    "*.html",
    "*.sh",
    "test_*.py",
    "*_test.py",
    "scrape_*.py",
    "collect_*.py",
    "baseball_*.json",
    "census_*.json",
    "census_*.csv",
    "baseball_*.csv",
    "baseball_*.html"
]

# Update interval in seconds
UPDATE_INTERVAL = 5

# Workspace management settings
MAX_OPEN_TABS = 5  # Recommended maximum number of open tabs
MAX_OPEN_TERMINALS = 2  # Recommended maximum number of open terminals
SESSION_DURATION_WARNING = 2  # Hours after which to warn about session duration 