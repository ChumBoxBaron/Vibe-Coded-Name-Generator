"""
Base class for name generators.
"""

import random
from typing import List, Tuple, Optional
from utils.data_loader import create_weighted_list, format_name

class BaseNameGenerator:
    """Base class for name generators."""
    
    def __init__(self):
        """Initialize the name generator."""
        self.first_names: List[Tuple[str, float]] = []
        self.last_names: List[Tuple[str, float]] = []
        self.weighted_first_names: List[str] = []
        self.weighted_last_names: List[str] = []
    
    def load_data(self):
        """Load name data from files. To be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement load_data()")
    
    def generate_name(self) -> str:
        """
        Generate a random name.
        
        Returns:
            str: A generated name
        """
        if not self.weighted_first_names or not self.weighted_last_names:
            return "No data available"
        
        first = random.choice(self.weighted_first_names)
        last = random.choice(self.weighted_last_names)
        
        return self.format_full_name(first, last)
    
    def generate_multiple(self, count: int = 10) -> List[str]:
        """
        Generate multiple random names.
        
        Args:
            count (int): Number of names to generate
            
        Returns:
            List[str]: List of generated names
        """
        return [self.generate_name() for _ in range(count)]
    
    def get_most_common(self, name_type: str = "first", limit: int = 20) -> List[Tuple[str, float]]:
        """
        Get the most common names of a specific type.
        
        Args:
            name_type (str): Type of name ("first" or "last")
            limit (int): Number of results to return
            
        Returns:
            List[Tuple[str, float]]: Most common names with frequencies
        """
        if name_type == "first":
            names = self.first_names
        elif name_type == "last":
            names = self.last_names
        else:
            return []
            
        return sorted(names, key=lambda x: x[1], reverse=True)[:limit]
    
    def format_full_name(self, first: str, last: str, nickname: Optional[str] = None) -> str:
        """
        Format a full name with optional nickname.
        
        Args:
            first (str): First name
            last (str): Last name
            nickname (Optional[str]): Optional nickname
            
        Returns:
            str: Formatted full name
        """
        first = format_name(first)
        last = format_name(last)
        
        if nickname:
            nickname = format_name(nickname)
            return f"{first} \"{nickname}\" {last}"
        
        return f"{first} {last}" 