import os
import json
import random
import math
from collections import Counter

class CensusNameGenerator:
    """
    Generator for names based on US Census data.
    """
    
    def __init__(self):
        """Initialize the name generator."""
        self.first_names = []
        self.last_names = []
        self.weighted_first_names = []
        self.weighted_last_names = []
        
        # Make sure we have data
        self.load_data()
    
    def load_data(self):
        """Load name data from the census data files."""
        census_dir = "census_data/final"
        
        # Load first names
        first_names_file = os.path.join(census_dir, "census_firstnames_combined.json")
        if os.path.exists(first_names_file):
            with open(first_names_file, 'r') as f:
                first_names_data = json.load(f)
                self.first_names = [(item["firstname"], item["frequency"]) 
                                  for item in first_names_data]
                # Create weighted list for random selection
                self.weighted_first_names = []
                for name, freq in self.first_names:
                    # Convert frequency to integer weight (multiply by 1000 to preserve decimals)
                    weight = int(float(freq) * 1000)
                    self.weighted_first_names.extend([name] * weight)
        
        # Load last names
        last_names_file = os.path.join(census_dir, "census_surnames.json")
        if os.path.exists(last_names_file):
            with open(last_names_file, 'r') as f:
                last_names_data = json.load(f)
                self.last_names = [(item["surname"], item["frequency"]) 
                                 for item in last_names_data]
                # Create weighted list for random selection
                self.weighted_last_names = []
                for name, freq in self.last_names:
                    # Convert frequency to integer weight (multiply by 1000 to preserve decimals)
                    weight = int(float(freq) * 1000)
                    self.weighted_last_names.extend([name] * weight)
        
        print(f"Loaded {len(self.first_names)} first names")
        print(f"Loaded {len(self.last_names)} last names")
    
    def generate_name(self):
        """Generate a random name from census data."""
        if not self.weighted_first_names or not self.weighted_last_names:
            return "No data available"
        
        first = random.choice(self.weighted_first_names)
        last = random.choice(self.weighted_last_names)
        
        # Properly capitalize the names
        first = first.capitalize()
        last = last.capitalize()
        
        return f"{first} {last}"
    
    def generate_unique_name(self):
        """
        Generate a more unique name by avoiding combinations of the most common names.
        Strategy: Never combine a top 100 first name with a top 100 last name.
        """
        if not self.first_names or not self.last_names:
            return "No data available"
        
        # Get top 100 first and last names by sorting based on frequency
        top_first_names = {name for name, _ in sorted(self.first_names, key=lambda x: x[1], reverse=True)[:100]}
        top_last_names = {name for name, _ in sorted(self.last_names, key=lambda x: x[1], reverse=True)[:100]}
        
        # Select a first name
        first_name_candidate = random.choice(self.weighted_first_names)
        
        # If first name is in top 100, ensure last name is NOT in top 100
        if first_name_candidate in top_first_names:
            # Filter out top 100 last names
            available_last_names = [(name, freq) for name, freq in self.last_names if name not in top_last_names]
            # Select a random last name weighted by frequency
            last_name_weights = [freq for _, freq in available_last_names]
            last_name_candidate = random.choices(
                [name for name, _ in available_last_names], 
                weights=last_name_weights, 
                k=1
            )[0]
        else:
            # If first name is not common, we can use any last name
            last_name_candidate = random.choice(self.weighted_last_names)
        
        # Properly capitalize the names
        first_name_candidate = first_name_candidate.capitalize()
        last_name_candidate = last_name_candidate.capitalize()
        
        return f"{first_name_candidate} {last_name_candidate}"
    
    def generate_weighted_unique_name(self):
        """
        Generate a highly unique name using a weighted probability system.
        Strategy:
        1. Invert frequency weights - making less common names more likely to be selected
        2. Apply logarithmic scaling to further favor uncommon names
        3. Create tiers of uniqueness with different selection probabilities
        4. Ensure realistic combinations while still prioritizing uniqueness
        """
        if not self.first_names or not self.last_names:
            return "No data available"
        
        # Define name tiers based on frequency percentiles
        # Tier 1: Very common (top 10%)
        # Tier 2: Common (10-30%)
        # Tier 3: Moderately common (30-60%)
        # Tier 4: Uncommon (60-90%)
        # Tier 5: Rare (bottom 10%)
        
        # Sort names by frequency
        sorted_first_names = sorted(self.first_names, key=lambda x: x[1], reverse=True)
        sorted_last_names = sorted(self.last_names, key=lambda x: x[1], reverse=True)
        
        # Calculate tier boundaries
        first_name_count = len(sorted_first_names)
        last_name_count = len(sorted_last_names)
        
        first_name_tiers = {
            1: sorted_first_names[:int(first_name_count * 0.1)],
            2: sorted_first_names[int(first_name_count * 0.1):int(first_name_count * 0.3)],
            3: sorted_first_names[int(first_name_count * 0.3):int(first_name_count * 0.6)],
            4: sorted_first_names[int(first_name_count * 0.6):int(first_name_count * 0.9)],
            5: sorted_first_names[int(first_name_count * 0.9):]
        }
        
        last_name_tiers = {
            1: sorted_last_names[:int(last_name_count * 0.1)],
            2: sorted_last_names[int(last_name_count * 0.1):int(last_name_count * 0.3)],
            3: sorted_last_names[int(last_name_count * 0.3):int(last_name_count * 0.6)],
            4: sorted_last_names[int(last_name_count * 0.6):int(last_name_count * 0.9)],
            5: sorted_last_names[int(last_name_count * 0.9):]
        }
        
        # Define tier selection probabilities (favoring uncommon/rare names)
        # The more unique tiers (4, 5) get higher probabilities
        tier_probabilities = {
            1: 0.05,  # Very common (5% chance)
            2: 0.10,  # Common (10% chance)
            3: 0.20,  # Moderately common (20% chance)
            4: 0.30,  # Uncommon (30% chance)
            5: 0.35   # Rare (35% chance)
        }
        
        # Select a tier for first name and last name
        first_name_tier = random.choices(
            list(tier_probabilities.keys()),
            weights=list(tier_probabilities.values()),
            k=1
        )[0]
        
        last_name_tier = random.choices(
            list(tier_probabilities.keys()),
            weights=list(tier_probabilities.values()),
            k=1
        )[0]
        
        # Apply an additional rule: if first name is very common (tier 1), 
        # ensure last name is at least uncommon (tier 4 or 5)
        if first_name_tier == 1:
            last_name_tier = random.choice([4, 5])
        
        # Select names from the chosen tiers with inversely weighted probabilities
        first_name_options = first_name_tiers[first_name_tier]
        last_name_options = last_name_tiers[last_name_tier]
        
        # Invert and normalize weights for selected tier
        if first_name_options:
            # Invert frequencies to favor less common names within the tier
            first_name_inverted_weights = [1/(freq + 0.001) for _, freq in first_name_options]  # Add small constant to avoid division by zero
            # Apply logarithmic scaling to make the distribution more balanced
            first_name_scaled_weights = [math.log(w + 1) for w in first_name_inverted_weights]
            # Select a name using these weights
            first_name_candidate = random.choices(
                [name for name, _ in first_name_options],
                weights=first_name_scaled_weights,
                k=1
            )[0]
        else:
            # Fallback if tier is empty
            first_name_candidate = random.choice([name for name, _ in sorted_first_names[int(first_name_count * 0.6):]])
        
        if last_name_options:
            # Same weighting approach for last names
            last_name_inverted_weights = [1/(freq + 0.001) for _, freq in last_name_options]
            last_name_scaled_weights = [math.log(w + 1) for w in last_name_inverted_weights]
            last_name_candidate = random.choices(
                [name for name, _ in last_name_options],
                weights=last_name_scaled_weights,
                k=1
            )[0]
        else:
            # Fallback if tier is empty
            last_name_candidate = random.choice([name for name, _ in sorted_last_names[int(last_name_count * 0.6):]])
        
        # Properly capitalize the names
        first_name_candidate = first_name_candidate.capitalize()
        last_name_candidate = last_name_candidate.capitalize()
        
        return f"{first_name_candidate} {last_name_candidate}"
    
    def generate_multiple_weighted_unique(self, count=10):
        """Generate multiple weighted unique names."""
        return [self.generate_weighted_unique_name() for _ in range(count)]
        
    def generate_multiple_unique(self, count=10):
        """Generate multiple unique names."""
        return [self.generate_unique_name() for _ in range(count)]
        
    def generate_multiple(self, count=10):
        """Generate multiple random names."""
        return [self.generate_name() for _ in range(count)]
    
    def get_most_common(self, name_type="first", limit=20):
        """Get the most common names of a specific type."""
        if name_type == "first":
            return sorted(self.first_names, key=lambda x: x[1], reverse=True)[:limit]
        elif name_type == "last":
            return sorted(self.last_names, key=lambda x: x[1], reverse=True)[:limit]
        else:
            return []

def main():
    """Main function to demonstrate the name generator."""
    generator = CensusNameGenerator()
    
    print("\n=== Census Name Generator ===\n")
    
    # Generate some random names
    print("Random Generated Names:")
    names = generator.generate_multiple(5)
    for i, name in enumerate(names, 1):
        print(f"{i}. {name}")
    
    # Generate unique names
    print("\nUnique Generated Names:")
    unique_names = generator.generate_multiple_unique(5)
    for i, name in enumerate(unique_names, 1):
        print(f"{i}. {name}")
    
    # Generate weighted unique names
    print("\nClaude's Fancier/Quanty-er Unique Names:")
    weighted_unique_names = generator.generate_multiple_weighted_unique(5)
    for i, name in enumerate(weighted_unique_names, 1):
        print(f"{i}. {name}")
    
    # Show some statistics
    print("\nMost Common First Names:")
    for name, freq in generator.get_most_common("first", 5):
        print(f"{name}: {freq}")
    
    print("\nMost Common Last Names:")
    for name, freq in generator.get_most_common("last", 5):
        print(f"{name}: {freq}")

if __name__ == "__main__":
    main() 