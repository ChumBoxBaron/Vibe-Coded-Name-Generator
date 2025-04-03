"""
Data loading utilities for name generators.
"""

import os
import json
from typing import List, Tuple, Dict, Any

def load_json_data(filepath: str) -> List[Dict[str, Any]]:
    """
    Load data from a JSON file.
    
    Args:
        filepath (str): Path to the JSON file
        
    Returns:
        List[Dict[str, Any]]: List of data records
    """
    if not os.path.exists(filepath):
        print(f"Data file not found: {filepath}")
        return []
    
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading data from {filepath}: {e}")
        return []

def create_weighted_list(names: List[Tuple[str, float]], weight_multiplier: int = 1000) -> List[str]:
    """
    Create a weighted list of names for random selection.
    
    Args:
        names (List[Tuple[str, float]]): List of (name, frequency) tuples
        weight_multiplier (int): Multiplier to convert frequencies to integer weights
        
    Returns:
        List[str]: Weighted list where names appear multiple times based on frequency
    """
    weighted_list = []
    for name, freq in names:
        # Convert frequency to integer weight
        weight = int(float(freq) * weight_multiplier)
        weighted_list.extend([name] * weight)
    return weighted_list

def format_name(name: str, capitalize: bool = True) -> str:
    """
    Format a name string according to conventions.
    
    Args:
        name (str): Name to format
        capitalize (bool): Whether to capitalize the name
        
    Returns:
        str: Formatted name
    """
    if not name:
        return name
    
    # Remove trailing parenthesis if present
    if name.endswith(")"):
        closing_paren_index = name.rfind(")")
        opening_paren_index = name.rfind("(")
        if opening_paren_index != -1 and closing_paren_index != -1:
            name = name[:opening_paren_index].strip()
        else:
            # Just remove the trailing parenthesis if no opening one is found
            name = name[:-1].strip()
        
    if capitalize:
        # Handle hyphenated names
        if '-' in name:
            return '-'.join(part.capitalize() for part in name.split('-'))
        # Handle names with spaces
        return ' '.join(part.capitalize() for part in name.split())
    
    return name 