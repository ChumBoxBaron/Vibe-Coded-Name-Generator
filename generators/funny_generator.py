"""
Generator for funny names based on US Census data.
"""

import os
import random
import re
from typing import List, Tuple, Dict, Set
from .base_generator import BaseNameGenerator
from utils.data_loader import load_json_data, create_weighted_list

class FunnyNameGenerator(BaseNameGenerator):
    """Generator for funny names based on census data."""
    
    def __init__(self):
        """Initialize the funny name generator."""
        super().__init__()
        self.silly_sound_patterns = {
            "oo": r"oo",           # Matches "oo" sounds (Goofy, Poop)
            "ee": r"ee",           # Matches "ee" sounds (Pee, Wee)
            "bb": r"bb",           # Matches double b's (Bubba)
            "dd": r"dd",           # Matches double d's (Daddy)
            "pp": r"pp",           # Matches double p's (Poppy)
            "tt": r"tt",           # Matches double t's (Potty)
            "gg": r"gg",           # Matches double g's (Wiggle)
            "oy": r"oy",           # Funny sound (Boy, Toy)
            "oob": r"oob",         # Goober
            "ub": r"ub",           # Tub, club
            "ump": r"ump",         # Bump, lump
            "oot": r"oot",         # Boot, toot
            "onk": r"onk",         # Honk, bonk
            "izz": r"izz",         # Fizz, whizz
            "uzz": r"uzz",         # Buzz, fuzz
            "ick": r"ick",         # Slick, quick
            "ank": r"ank",         # Tank, spank
            "ink": r"ink",         # Stink, pink
            "unk": r"unk",         # Funk, junk
            "oot": r"oot",         # Boot, hoot
            "zz": r"zz",           # Matches zz (Fizz)
            "oodle": r"oodle",     # Noodle, doodle
            "oogle": r"oogle",     # Google, boogie
            "ump": r"ump",         # Bump, dump
            "onk": r"onk"          # Bonk, honk
        }
        
        self.crude_patterns = {
            "butt": r"but|butt",    # Butt related
            "poo": r"poo",          # Poo related
            "pee": r"pee",          # Pee related
            "doo": r"doo",          # Doo-doo related
            "wee": r"wee",          # Wee-wee related
            "toot": r"toot",        # Toot/fart related
            "peep": r"peep",        # Peep show
            "boob": r"b[o0]{2}b",   # Boob related
            "dick": r"dick",        # Richard or... 
            "cock": r"cock",        # Rooster or...
            "puff": r"puff",        # Puffy/inflated
            "long": r"long",        # Length related
            "big": r"big",          # Size related
            "horn": r"horn",        # Horn related
            "wang": r"wang",        # Slang term
            "wank": r"wank",        # British slang
            "hump": r"hump",        # Bump/lump/hump
            "dump": r"dump",        # Dump related
            "hole": r"hole",        # Hole related
            "junk": r"junk",        # Junk related
            "rear": r"rear",        # Rear/behind related
            "tush": r"tush",        # Tush related
            "bottom": r"bottom",    # Bottom related
            "squeeze": r"squeeze",  # Squeeze related
            "lick": r"lick"         # Lick related
        }
        
        # Innuendo names that kids find funny when combined
        self.innuendo_first_names = set([
            "HARRY", "SEYMOUR", "DICK", "WILLIE", "MIKE", "PETER", "RANDY", "BEN", "HUGH", "ANITA",
            "LUKE", "JUSTIN", "DREW", "WOODY", "PHIL", "CHUCK", "IMA", "ROCCO", "ROD", "CHESTER"
        ])
        
        self.innuendo_last_names = set([
            "BUTT", "BUTTS", "BOOTY", "BOTTOM", "SEAMAN", "SAMPLE", "HYMAN", "DIXON", "JOHNSON", 
            "DYCK", "BALLS", "WEINER", "LONGFELLOW", "COX", "HANCOCK", "COCKBURN", "CUMMINGS", 
            "PETERS", "KUNTZ", "BEAVER", "BUST", "HOOKER", "LOINS", "SMALL", "PITTS", "WOOD"
        ])
        
        self.load_data()
        
        # Index names by patterns for faster lookup
        self.silly_first_names = self._index_names_by_patterns(self.weighted_first_names, self.silly_sound_patterns)
        self.silly_last_names = self._index_names_by_patterns(self.weighted_last_names, self.silly_sound_patterns)
        self.crude_first_names = self._index_names_by_patterns(self.weighted_first_names, self.crude_patterns)
        self.crude_last_names = self._index_names_by_patterns(self.weighted_last_names, self.crude_patterns)
    
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
    
    def _index_names_by_patterns(self, names: List[str], patterns: Dict[str, str]) -> Dict[str, Set[str]]:
        """
        Index names by sound patterns for faster lookup.
        
        Args:
            names: List of names to index
            patterns: Dictionary of pattern name to regex pattern
            
        Returns:
            Dictionary of pattern -> set of names matching that pattern
        """
        result = {pattern: set() for pattern in patterns}
        
        for name in names:
            for pattern_name, pattern in patterns.items():
                if re.search(pattern, name, re.IGNORECASE):
                    result[pattern_name].add(name)
        
        return result
    
    def generate_silly_sound_name(self) -> str:
        """
        Generate a name with silly sounds.
        
        Returns:
            A funny name with silly sound patterns
        """
        # Try to find a matching first name with a silly pattern
        pattern_keys = list(self.silly_sound_patterns.keys())
        random.shuffle(pattern_keys)
        
        first_name = None
        last_name = None
        
        # Find a first name with a silly sound
        for pattern in pattern_keys:
            if self.silly_first_names[pattern]:
                candidates = list(self.silly_first_names[pattern])
                if candidates:
                    first_name = random.choice(candidates)
                    break
        
        # If no match found, use a random first name
        if not first_name:
            first_name = random.choice(self.weighted_first_names)
        
        # Try to find a last name with the same or similar pattern
        matching_pattern = None
        for pattern in pattern_keys:
            if re.search(self.silly_sound_patterns[pattern], first_name, re.IGNORECASE) and self.silly_last_names[pattern]:
                matching_pattern = pattern
                break
        
        # If a matching pattern is found, use it to choose a last name
        if matching_pattern and self.silly_last_names[matching_pattern]:
            last_name = random.choice(list(self.silly_last_names[matching_pattern]))
        else:
            # Otherwise, just pick a random silly last name
            for pattern in pattern_keys:
                if self.silly_last_names[pattern]:
                    last_name = random.choice(list(self.silly_last_names[pattern]))
                    break
        
        # Fallback to a random last name if needed
        if not last_name:
            last_name = random.choice(self.weighted_last_names)
        
        return self.format_full_name(first_name, last_name)
    
    def generate_crude_name(self) -> str:
        """
        Generate a crude/bathroom humor name.
        
        Returns:
            A funny name with crude/bathroom humor
        """
        # First try to find a combination of known innuendo names
        if self.innuendo_first_names & set(self.weighted_first_names) and self.innuendo_last_names & set(self.weighted_last_names):
            first_options = list(self.innuendo_first_names & set(self.weighted_first_names))
            last_options = list(self.innuendo_last_names & set(self.weighted_last_names))
            
            if first_options and last_options:
                return self.format_full_name(random.choice(first_options), random.choice(last_options))
        
        # Otherwise try to find a first name from our crude patterns
        pattern_keys = list(self.crude_patterns.keys())
        random.shuffle(pattern_keys)
        
        first_name = None
        last_name = None
        
        # Find a first name with a crude pattern
        for pattern in pattern_keys:
            if self.crude_first_names[pattern]:
                candidates = list(self.crude_first_names[pattern])
                if candidates:
                    first_name = random.choice(candidates)
                    break
        
        # If no match found, use a random first name
        if not first_name:
            first_name = random.choice(self.weighted_first_names)
        
        # Try to find a last name with a crude pattern
        for pattern in pattern_keys:
            if self.crude_last_names[pattern]:
                candidates = list(self.crude_last_names[pattern])
                if candidates:
                    last_name = random.choice(candidates)
                    break
        
        # Fallback to a random last name if needed
        if not last_name:
            last_name = random.choice(self.weighted_last_names)
        
        return self.format_full_name(first_name, last_name)
    
    def generate_name(self) -> str:
        """
        Generate a funny name, randomly choosing between silly sounds and crude humor.
        
        Returns:
            A funny name using either silly sounds or crude humor
        """
        # 50% chance for each type of humor
        if random.random() < 0.5:
            return self.generate_silly_sound_name()
        else:
            return self.generate_crude_name()
    
    def generate_multiple(self, count: int = 10) -> List[str]:
        """
        Generate multiple funny names.
        
        Args:
            count: Number of names to generate
            
        Returns:
            List of funny names
        """
        # Track used names to prevent duplicates
        used_first_names = set()
        used_last_names = set()
        results = []
        
        max_attempts = count * 10  # Prevent infinite loops if not enough variety
        attempts = 0
        
        while len(results) < count and attempts < max_attempts:
            name = self.generate_name()
            # Split the name to check first and last parts
            parts = name.split()
            
            # Handle names with nicknames (which have format "First 'Nickname' Last")
            if '"' in name:
                # Extract just the first and last name from the format
                name_parts = name.split('"')
                if len(name_parts) >= 3:
                    first_name = name_parts[0].strip()
                    last_name = name_parts[2].strip()
                else:
                    # Skip malformed names
                    attempts += 1
                    continue
            elif len(parts) >= 2:  # Regular names with at least first and last
                first_name = parts[0]
                last_name = parts[-1]  # Last part is the surname
            else:
                # Skip malformed names
                attempts += 1
                continue
                
            # Check if either first or last name has been used
            if first_name in used_first_names or last_name in used_last_names:
                attempts += 1
                continue
            
            # Add the name to results and track used names
            results.append(name)
            used_first_names.add(first_name)
            used_last_names.add(last_name)
            attempts += 1
        
        # If we couldn't generate enough unique names, fill the remaining with regular names
        if len(results) < count:
            remaining = count - len(results)
            print(f"Warning: Could only generate {len(results)} unique funny names. Adding {remaining} non-unique names.")
            results.extend([self.generate_name() for _ in range(remaining)])
            
        return results
    
    def calculate_possible_combinations(self) -> dict:
        """
        Calculate the total number of possible funny name combinations based on current rules.
        
        Returns:
            Dictionary with statistics about possible name combinations
        """
        # Count names that match our patterns
        silly_first_count = sum(len(names) for names in self.silly_first_names.values())
        silly_last_count = sum(len(names) for names in self.silly_last_names.values())
        crude_first_count = sum(len(names) for names in self.crude_first_names.values())
        crude_last_count = sum(len(names) for names in self.crude_last_names.values())
        
        # Adjust for duplicates (names appearing in multiple pattern categories)
        unique_silly_first = set()
        for names in self.silly_first_names.values():
            unique_silly_first.update(names)
            
        unique_silly_last = set()
        for names in self.silly_last_names.values():
            unique_silly_last.update(names)
            
        unique_crude_first = set()
        for names in self.crude_first_names.values():
            unique_crude_first.update(names)
            
        unique_crude_last = set()
        for names in self.crude_last_names.values():
            unique_crude_last.update(names)
        
        # Count innuendo names that actually exist in our data
        innuendo_first_available = self.innuendo_first_names & set(self.weighted_first_names)
        innuendo_last_available = self.innuendo_last_names & set(self.weighted_last_names)
        
        # Calculate total possible combinations
        silly_sound_combinations = len(unique_silly_first) * len(unique_silly_last)
        crude_combinations = len(unique_crude_first) * len(unique_crude_last)
        innuendo_combinations = len(innuendo_first_available) * len(innuendo_last_available)
        
        # Total possible combinations
        total_combinations = silly_sound_combinations + crude_combinations + innuendo_combinations
        
        return {
            "silly_sound": {
                "first_names": len(unique_silly_first),
                "last_names": len(unique_silly_last),
                "combinations": silly_sound_combinations
            },
            "crude": {
                "first_names": len(unique_crude_first),
                "last_names": len(unique_crude_last),
                "combinations": crude_combinations
            },
            "innuendo": {
                "first_names": len(innuendo_first_available),
                "last_names": len(innuendo_last_available),
                "combinations": innuendo_combinations
            },
            "total_combinations": total_combinations
        }

def main():
    """Main function to demonstrate the funny name generator."""
    generator = FunnyNameGenerator()
    
    print("\n=== Funny Name Generator ===\n")
    
    # Calculate and display possible combinations
    combinations = generator.calculate_possible_combinations()
    print("\nPossible Name Combinations Statistics:")
    print(f"Silly Sound Names: {combinations['silly_sound']['first_names']} first names × {combinations['silly_sound']['last_names']} last names = {combinations['silly_sound']['combinations']} combinations")
    print(f"Crude Humor Names: {combinations['crude']['first_names']} first names × {combinations['crude']['last_names']} last names = {combinations['crude']['combinations']} combinations")
    print(f"Innuendo Names: {combinations['innuendo']['first_names']} first names × {combinations['innuendo']['last_names']} last names = {combinations['innuendo']['combinations']} combinations")
    print(f"Total Possible Funny Names: {combinations['total_combinations']}\n")
    
    # Generate silly sound names
    print("Silly Sound Names:")
    for i in range(5):
        print(f"{i+1}. {generator.generate_silly_sound_name()}")
    
    # Generate crude names
    print("\nCrude/Bathroom Humor Names:")
    for i in range(5):
        print(f"{i+1}. {generator.generate_crude_name()}")
    
    # Generate mixed funny names
    print("\nMixed Funny Names:")
    names = generator.generate_multiple(10)
    for i, name in enumerate(names, 1):
        print(f"{i}. {name}")
    
    # Check for duplicates in a larger batch to show the deduplication
    print("\nChecking for duplicates in a larger batch of 20 names...")
    names = generator.generate_multiple(20)
    first_names = [name.split()[0] for name in names]
    last_names = [name.split()[-1] for name in names]
    
    print(f"Number of unique first names: {len(set(first_names))} out of {len(names)}")
    print(f"Number of unique last names: {len(set(last_names))} out of {len(names)}")
    print(f"All first names are unique: {len(set(first_names)) == len(names)}")
    print(f"All last names are unique: {len(set(last_names)) == len(names)}")

if __name__ == "__main__":
    main() 