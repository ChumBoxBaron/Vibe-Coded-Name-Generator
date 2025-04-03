import os
import time
import glob
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict
import tiktoken
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.live import Live
from rich.table import Table
import config

console = Console()

class ContextMonitor:
    def __init__(self):
        self.encoding = tiktoken.get_encoding("cl100k_base")
        self.total_tokens = 0
        self.file_tokens: Dict[str, int] = {}
        self.chat_history_tokens = 0
        self.last_update = datetime.now()
        self.console = Console()
        self.session_start_time = datetime.now()
        self.session_duration = 0

    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in a text string."""
        return len(self.encoding.encode(text))

    def count_file_tokens(self, file_path: str) -> int:
        """Count tokens in a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return self.count_tokens(content)
        except Exception as e:
            self.console.print(f"[red]Error reading {file_path}: {str(e)}[/red]")
            return 0

    def update_token_counts(self):
        """Update token counts for all monitored files."""
        self.total_tokens = 0
        self.file_tokens.clear()
        self.session_duration = (datetime.now() - self.session_start_time).total_seconds() / 3600  # hours

        # Count file tokens
        for pattern in config.FILE_PATTERNS:
            for dir_path in config.MONITORED_DIRS:
                for file_path in glob.glob(os.path.join(dir_path, pattern)):
                    if any(ignored in file_path for ignored in config.IGNORED_DIRS):
                        continue
                    
                    tokens = self.count_file_tokens(file_path)
                    self.file_tokens[file_path] = tokens
                    self.total_tokens += tokens

        # Estimate chat history tokens (this is a rough estimate)
        # You might want to implement actual chat history tracking based on your needs
        self.chat_history_tokens = self.total_tokens * 0.5  # Assuming chat history is roughly half of code tokens

    def get_usage_percentage(self) -> float:
        """Calculate the percentage of context window used."""
        total_with_chat = self.total_tokens + self.chat_history_tokens
        return (total_with_chat / config.CONTEXT_WINDOW_SIZE) * 100

    def get_status_color(self, percentage: float) -> str:
        """Get the color for the status based on usage percentage."""
        if percentage >= config.CRITICAL_THRESHOLD:
            return "red"
        elif percentage >= config.WARNING_THRESHOLD:
            return "yellow"
        return "green"

    def get_session_recommendations(self) -> List[str]:
        """Generate recommendations based on current session state."""
        recommendations = []
        percentage = self.get_usage_percentage()
        
        if percentage >= config.CRITICAL_THRESHOLD:
            recommendations.append("⚠️ CRITICAL: Start a new session immediately!")
        elif percentage >= config.WARNING_THRESHOLD:
            recommendations.append("⚠️ WARNING: Consider starting a new session soon")
        
        if self.session_duration > 2:  # If session is longer than 2 hours
            recommendations.append("⏰ Consider starting a new session after 2+ hours of work")
        
        if self.total_tokens > 4000:  # If codebase is getting large
            recommendations.append("📁 Consider splitting your code into smaller modules")
        
        return recommendations

    def generate_status_table(self) -> Table:
        """Generate a rich table with status information."""
        table = Table(title="Context Window Status")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")

        percentage = self.get_usage_percentage()
        color = self.get_status_color(percentage)

        table.add_row("Total Code Tokens", str(self.total_tokens))
        table.add_row("Estimated Chat Tokens", str(self.chat_history_tokens))
        table.add_row("Total Context Usage", f"[{color}]{percentage:.1f}%[/{color}]")
        table.add_row("Session Duration", f"{self.session_duration:.1f} hours")
        
        recommendations = self.get_session_recommendations()
        if recommendations:
            table.add_row("Recommendations", "\n".join(recommendations))

        return table

    def monitor(self):
        """Main monitoring loop."""
        with Live(self.generate_status_table(), refresh_per_second=1) as live:
            while True:
                self.update_token_counts()
                live.update(self.generate_status_table())
                time.sleep(config.UPDATE_INTERVAL)

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, monitor: ContextMonitor):
        self.monitor = monitor

    def on_modified(self, event):
        if not event.is_directory:
            self.monitor.update_token_counts()

def main():
    console.print(Panel.fit(
        "[bold blue]Context Window Monitor[/bold blue]\n"
        "Monitoring your project for context window usage...\n"
        "Press Ctrl+C to stop monitoring",
        title="Welcome"
    ))

    monitor = ContextMonitor()
    event_handler = FileChangeHandler(monitor)
    observer = Observer()

    for dir_path in config.MONITORED_DIRS:
        observer.schedule(event_handler, dir_path, recursive=True)

    observer.start()
    console.print("[green]Started monitoring file changes...[/green]")
    
    try:
        monitor.monitor()
    except KeyboardInterrupt:
        observer.stop()
        console.print("\n[yellow]Stopping monitor...[/yellow]")
    
    observer.join()

if __name__ == "__main__":
    main() 