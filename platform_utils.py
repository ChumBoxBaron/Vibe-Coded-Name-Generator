import os
import platform
import subprocess
from typing import Tuple

def get_platform_specific_counters() -> Tuple[int, int]:
    """
    Get the number of open tabs and terminals based on the current platform.
    Returns a tuple of (tabs_count, terminals_count)
    """
    system = platform.system().lower()
    
    if system == 'windows':
        return _count_windows_tabs_and_terminals()
    elif system == 'darwin':  # macOS
        return _count_macos_tabs_and_terminals()
    elif system == 'linux':
        return _count_linux_tabs_and_terminals()
    else:
        return 0, 0  # Default to 0 for unknown platforms

def _count_windows_tabs_and_terminals() -> Tuple[int, int]:
    """Count open tabs and terminals on Windows."""
    try:
        # Count PowerShell and Command Prompt windows
        terminals = subprocess.check_output(
            'tasklist /FI "IMAGENAME eq cmd.exe" /FI "IMAGENAME eq powershell.exe" /NH',
            shell=True
        ).decode().count('\n')
        
        # Count VS Code windows (as a proxy for tabs)
        # Note: This is an approximation as Windows doesn't have a direct way to count tabs
        vscode_windows = subprocess.check_output(
            'tasklist /FI "IMAGENAME eq Code.exe" /NH',
            shell=True
        ).decode().count('\n')
        
        # Estimate tabs based on VS Code windows (assuming 5 tabs per window)
        tabs = vscode_windows * 5
        
        return tabs, terminals
    except Exception:
        return 0, 0

def _count_macos_tabs_and_terminals() -> Tuple[int, int]:
    """Count open tabs and terminals on macOS."""
    try:
        # Count terminal windows using AppleScript
        terminals = int(subprocess.check_output(
            'osascript -e "tell application \"Terminal\" to count windows"',
            shell=True
        ).decode().strip())
        
        # Count VS Code windows and estimate tabs
        vscode_windows = int(subprocess.check_output(
            'osascript -e "tell application \"Code\" to count windows"',
            shell=True
        ).decode().strip())
        
        # Estimate tabs based on VS Code windows
        tabs = vscode_windows * 5
        
        return tabs, terminals
    except Exception:
        return 0, 0

def _count_linux_tabs_and_terminals() -> Tuple[int, int]:
    """Count open tabs and terminals on Linux."""
    try:
        # Count terminal windows using wmctrl
        terminals = int(subprocess.check_output(
            'wmctrl -l | grep -E "Terminal|Konsole|Gnome-terminal" | wc -l',
            shell=True
        ).decode().strip())
        
        # Count VS Code windows and estimate tabs
        vscode_windows = int(subprocess.check_output(
            'wmctrl -l | grep "Code" | wc -l',
            shell=True
        ).decode().strip())
        
        # Estimate tabs based on VS Code windows
        tabs = vscode_windows * 5
        
        return tabs, terminals
    except Exception:
        return 0, 0 