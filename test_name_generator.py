import os
import json
import sys
from baseball_name_generator import BaseballNameGenerator

# Test with the small dataset we've already collected
TEST_DATA_FILE = "baseball_data/test_all_players.json"

class TestBaseballNameGenerator(BaseballNameGenerator):
    """Test version of the name generator that uses our test data file."""
    
    def load_data(self):
        """Override to load from the test data file."""
        if not os.path.exists(TEST_DATA_FILE):
            print(f"Test data file not found: {TEST_DATA_FILE}")
            print("Please run the baseball_simple_test.py script first.")
            return
        
        try:
            with open(TEST_DATA_FILE, 'r') as f:
                players = json.load(f)
            
            print(f"Loaded {len(players)} players from {TEST_DATA_FILE}")
            
            # Extract names and count frequencies
            from collections import Counter
            first_counter = Counter()
            last_counter = Counter()
            nickname_counter = Counter()
            
            for player in players:
                # First names
                first = player.get("first_name", "")
                if first and len(first) > 1:
                    first_counter[first] += 1
                
                # Last names
                last = player.get("last_name", "")
                if last and len(last) > 1:
                    last_counter[last] += 1
                
                # Nicknames
                nick = player.get("nickname", "")
                if nick and nick != "None" and len(nick) > 1 and nick.lower() != "none":
                    # Some nicknames have "or" in them, split those
                    if " or " in nick.lower():
                        parts = nick.split(" or ")
                        for part in parts:
                            if part and len(part.strip()) > 1:
                                nickname_counter[part.strip()] += 1
                    else:
                        nickname_counter[nick] += 1
            
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

def main():
    """Main function to test the name generator with test data."""
    generator = TestBaseballNameGenerator()
    
    if not generator.weighted_first_names:
        print("No data available. Exiting.")
        sys.exit(1)
    
    print("\n=== TEST Baseball Name Generator ===\n")
    
    # Generate some random names
    print("Random Generated Names:")
    names = generator.generate_multiple(5)
    for i, name in enumerate(names, 1):
        print(f"{i}. {name}")
    
    # Show all the data we have for testing
    print("\nAll First Names:")
    for name, count in generator.first_names:
        print(f"{name}: {count}")
    
    print("\nAll Last Names:")
    for name, count in generator.last_names:
        print(f"{name}: {count}")
    
    print("\nAll Nicknames:")
    for name, count in generator.nicknames:
        print(f"{name}: {count}")

if __name__ == "__main__":
    main() 