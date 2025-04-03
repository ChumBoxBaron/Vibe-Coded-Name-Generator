"""
Generator for names based on US Census data.
"""

import os
from typing import List, Tuple
from .base_generator import BaseNameGenerator
from utils.data_loader import load_json_data, create_weighted_list

class CensusNameGenerator(BaseNameGenerator):
    """Generator for census-based names."""
    
    def __init__(self):
        """Initialize the census name generator."""
        super().__init__()
        self.load_data()
    
    def load_data(self):
        """Load name data from census files."""
        census_dir = "census_data/final"
        
        # Load first names
        first_names_file = os.path.join(census_dir, "census_firstnames_combined.json")
        first_names_data = load_json_data(first_names_file)
        if first_names_data:
            self.first_names = [(item["firstname"], item["frequency"]) 
                               for item in first_names_data]
            self.weighted_first_names = create_weighted_list(self.first_names)
        
        # Load last names
        last_names_file = os.path.join(census_dir, "census_surnames.json")
        last_names_data = load_json_data(last_names_file)
        if last_names_data:
            self.last_names = [(item["surname"], item["frequency"]) 
                              for item in last_names_data]
            self.weighted_last_names = create_weighted_list(self.last_names)
        
        print(f"Loaded {len(self.first_names)} first names")
        print(f"Loaded {len(self.last_names)} last names") 