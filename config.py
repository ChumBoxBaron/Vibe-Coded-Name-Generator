# Context Window Monitor Configuration

# Default context window size (tokens)
CONTEXT_WINDOW_SIZE = 8000

# Warning threshold (percentage)
WARNING_THRESHOLD = 80

# Critical threshold (percentage)
CRITICAL_THRESHOLD = 90

# File patterns to monitor
FILE_PATTERNS = [
    "*.py",
    "*.js",
    "*.ts",
    "*.jsx",
    "*.tsx",
    "*.html",
    "*.css",
    "*.json",
    "*.md"
]

# Directories to monitor
MONITORED_DIRS = [
    ".",
]

# Directories to ignore
IGNORED_DIRS = [
    "venv",
    "node_modules",
    ".git",
    "__pycache__",
]

# Update interval in seconds
UPDATE_INTERVAL = 5 