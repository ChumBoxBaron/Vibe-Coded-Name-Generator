import os
import json
import random
import re
from collections import Counter

# Data directory
DATA_DIR = "baseball_data"
NAME_DATA_FILE = os.path.join(DATA_DIR, "all_baseball_players.json")

class BaseballNameGenerator:
    """
    Generator for funny baseball player names based on historical data.
    """
    
    def __init__(self):
        """Initialize the name generator."""
        self.first_names = []
        self.last_names = []
        self.nicknames = []
        self.weighted_first_names = []
        self.weighted_last_names = []
        self.weighted_nicknames = []
        
        # Make sure we have data
        self.load_data()
    
    def clean_name(self, name):
        """
        Clean a name by removing invalid characters or fixing formatting issues.
        
        Args:
            name (str): The name to clean
            
        Returns:
            str: The cleaned name or empty string if name can't be salvaged
        """
        if not name or len(name) < 2:
            return ""
            
        # Reject names with @ symbol completely
        if '@' in name:
            return ""
            
        # Remove trailing parenthesis
        if name.endswith(')'):
            # If it's likely just a trailing parenthesis issue, remove it
            if name.count(')') > name.count('('):
                name = name.rstrip(')')
        
        # For balanced parentheses in nicknames (like descriptive text), keep as is
        
        return name
    
    def is_valid_name(self, name):
        """
        Check if a name is valid after cleaning.
        
        Args:
            name (str): The name to check
            
        Returns:
            bool: True if the name is valid, False otherwise
        """
        name = self.clean_name(name)
        return name != "" and len(name) >= 2
    
    def load_data(self):
        """Load name data from the data file."""
        if not os.path.exists(NAME_DATA_FILE):
            print(f"Data file not found: {NAME_DATA_FILE}")
            print("Please run the baseball scraper first.")
            return
        
        try:
            with open(NAME_DATA_FILE, 'r') as f:
                players = json.load(f)
            
            print(f"Loaded {len(players)} players from {NAME_DATA_FILE}")
            
            # Extract names and count frequencies
            first_counter = Counter()
            last_counter = Counter()
            nickname_counter = Counter()
            
            for player in players:
                # First names
                first = player.get("first_name", "")
                cleaned_first = self.clean_name(first)
                if cleaned_first:
                    first_counter[cleaned_first] += 1
                
                # Last names
                last = player.get("last_name", "")
                cleaned_last = self.clean_name(last)
                if cleaned_last:
                    last_counter[cleaned_last] += 1
                
                # Nicknames
                nick = player.get("nickname", "")
                if nick and nick != "None" and nick.lower() != "none":
                    cleaned_nick = self.clean_name(nick)
                    if cleaned_nick:
                        # Some nicknames have "or" in them, split those
                        if " or " in cleaned_nick.lower():
                            parts = cleaned_nick.split(" or ")
                            for part in parts:
                                cleaned_part = self.clean_name(part.strip())
                                if cleaned_part:
                                    nickname_counter[cleaned_part] += 1
                        else:
                            nickname_counter[cleaned_nick] += 1
            
            # Convert to lists and sort by frequency
            self.first_names = sorted([(name, count) for name, count in first_counter.items()], 
                                     key=lambda x: x[1], reverse=True)
            
            self.last_names = sorted([(name, count) for name, count in last_counter.items()], 
                                    key=lambda x: x[1], reverse=True)
            
            self.nicknames = sorted([(name, count) for name, count in nickname_counter.items()], 
                                   key=lambda x: x[1], reverse=True)
            
            # Create weighted lists for random selection
            self.weighted_first_names = []
            for name, count in self.first_names:
                self.weighted_first_names.extend([name] * count)
            
            self.weighted_last_names = []
            for name, count in self.last_names:
                self.weighted_last_names.extend([name] * count)
            
            self.weighted_nicknames = []
            for name, count in self.nicknames:
                self.weighted_nicknames.extend([name] * count)
            
            print(f"Processed {len(self.first_names)} unique first names")
            print(f"Processed {len(self.last_names)} unique last names")
            print(f"Processed {len(self.nicknames)} unique nicknames")
            
        except Exception as e:
            print(f"Error loading data: {e}")
    
    def generate_name(self, use_nickname=True):
        """
        Generate a random baseball name.
        
        Args:
            use_nickname (bool): Whether to include a nickname
            
        Returns:
            str: A generated name
        """
        if not self.weighted_first_names or not self.weighted_last_names:
            return "No data available"
        
        first = random.choice(self.weighted_first_names)
        last = random.choice(self.weighted_last_names)
        
        if use_nickname and self.weighted_nicknames and random.random() < 0.7:  # 70% chance to use nickname
            nickname = random.choice(self.weighted_nicknames)
            return f"{first} \"{nickname}\" {last}"
        else:
            return f"{first} {last}"
    
    def generate_multiple(self, count=10, use_nickname=True):
        """
        Generate multiple random baseball names.
        
        Args:
            count (int): Number of names to generate
            use_nickname (bool): Whether to include nicknames
            
        Returns:
            list: List of generated names
        """
        return [self.generate_name(use_nickname) for _ in range(count)]
    
    def search_nicknames(self, query):
        """
        Search for nicknames containing the query.
        
        Args:
            query (str): Search term
            
        Returns:
            list: Matching nicknames with counts
        """
        query = query.lower()
        return [(name, count) for name, count in self.nicknames 
                if query in name.lower()]
    
    def get_most_common(self, name_type="first", limit=20):
        """
        Get the most common names of a specific type.
        
        Args:
            name_type (str): Type of name ("first", "last", or "nickname")
            limit (int): Number of results to return
            
        Returns:
            list: Most common names with counts
        """
        if name_type == "first":
            return self.first_names[:limit]
        elif name_type == "last":
            return self.last_names[:limit]
        elif name_type == "nickname":
            return self.nicknames[:limit]
        else:
            return []
    
    def get_notable_nicknames(self, min_length=5, limit=20):
        """
        Get notable (longer) nicknames.
        
        Args:
            min_length (int): Minimum length of nickname
            limit (int): Number of results to return
            
        Returns:
            list: Notable nicknames
        """
        long_nicknames = [(name, count) for name, count in self.nicknames 
                         if len(name) >= min_length]
        return sorted(long_nicknames, key=lambda x: x[1], reverse=True)[:limit]

def main():
    """Main function to demonstrate the name generator."""
    generator = BaseballNameGenerator()
    
    print("\n=== Baseball Name Generator ===\n")
    
    # Generate some random names
    print("Random Generated Names:")
    names = generator.generate_multiple(10)
    for i, name in enumerate(names, 1):
        print(f"{i}. {name}")
    
    # Show some statistics
    print("\nMost Common First Names:")
    for name, count in generator.get_most_common("first", 5):
        print(f"{name}: {count}")
    
    print("\nMost Common Last Names:")
    for name, count in generator.get_most_common("last", 5):
        print(f"{name}: {count}")
    
    print("\nMost Common Nicknames:")
    for name, count in generator.get_most_common("nickname", 5):
        print(f"{name}: {count}")
    
    print("\nNotable Nicknames:")
    for name, count in generator.get_notable_nicknames():
        print(f"{name}: {count}")

if __name__ == "__main__":
    main() 