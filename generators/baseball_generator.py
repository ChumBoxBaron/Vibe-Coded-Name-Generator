"""
Generator for vintage baseball player names.
"""

import os
import random
from typing import List, Tuple
from .base_generator import BaseNameGenerator
from utils.data_loader import load_json_data, create_weighted_list

class BaseballNameGenerator(BaseNameGenerator):
    """Generator for vintage baseball player names."""
    
    def __init__(self):
        """Initialize the baseball name generator."""
        super().__init__()
        self.nicknames: List[Tuple[str, float]] = []
        self.weighted_nicknames: List[str] = []
        self.load_data()
    
    def load_data(self):
        """Load baseball player name data."""
        data_dir = "baseball_data"
        player_file = os.path.join(data_dir, "all_baseball_players.json")
        
        players = load_json_data(player_file)
        if not players:
            return
            
        print(f"Loaded {len(players)} players from {player_file}")
        
        # Process first names
        first_counter = {}
        last_counter = {}
        nickname_counter = {}
        
        for player in players:
            # First names
            first = player.get("first_name", "")
            if first and len(first) > 1:
                first_counter[first] = first_counter.get(first, 0) + 1
            
            # Last names
            last = player.get("last_name", "")
            if last and len(last) > 1:
                last_counter[last] = last_counter.get(last, 0) + 1
            
            # Nicknames
            nick = player.get("nickname", "")
            if nick and nick != "None" and len(nick) > 1 and nick.lower() != "none":
                if " or " in nick.lower():
                    parts = nick.split(" or ")
                    for part in parts:
                        if part and len(part.strip()) > 1:
                            nickname_counter[part.strip()] = nickname_counter.get(part.strip(), 0) + 1
                else:
                    nickname_counter[nick] = nickname_counter.get(nick, 0) + 1
        
        # Convert counters to lists of tuples
        self.first_names = [(name, count) for name, count in first_counter.items()]
        self.last_names = [(name, count) for name, count in last_counter.items()]
        self.nicknames = [(name, count) for name, count in nickname_counter.items()]
        
        # Create weighted lists
        self.weighted_first_names = create_weighted_list(self.first_names)
        self.weighted_last_names = create_weighted_list(self.last_names)
        self.weighted_nicknames = create_weighted_list(self.nicknames)
        
        print(f"Processed {len(self.first_names)} unique first names")
        print(f"Processed {len(self.last_names)} unique last names")
        print(f"Processed {len(self.nicknames)} unique nicknames")
    
    def generate_name(self) -> str:
        """
        Generate a random baseball player name.
        
        Returns:
            str: A generated name
        """
        if not self.weighted_first_names or not self.weighted_last_names:
            return "No data available"
        
        first = random.choice(self.weighted_first_names)
        last = random.choice(self.weighted_last_names)
        
        if self.weighted_nicknames and random.random() < 0.7:  # 70% chance to use nickname
            nickname = random.choice(self.weighted_nicknames)
            return self.format_full_name(first, last, nickname)
        
        return self.format_full_name(first, last)
    
    def get_notable_nicknames(self, min_length: int = 5, limit: int = 20) -> List[Tuple[str, float]]:
        """
        Get notable (longer) nicknames.
        
        Args:
            min_length (int): Minimum length of nickname
            limit (int): Number of results to return
            
        Returns:
            List[Tuple[str, float]]: Notable nicknames with frequencies
        """
        long_nicknames = [(name, count) for name, count in self.nicknames 
                         if len(name) >= min_length]
        return sorted(long_nicknames, key=lambda x: x[1], reverse=True)[:limit] 