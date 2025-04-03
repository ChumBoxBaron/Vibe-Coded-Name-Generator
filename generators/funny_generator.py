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
        return [self.generate_name() for _ in range(count)]

def main():
    """Main function to demonstrate the funny name generator."""
    generator = FunnyNameGenerator()
    
    print("\n=== Funny Name Generator ===\n")
    
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
    names = generator.generate_multiple(5)
    for i, name in enumerate(names, 1):
        print(f"{i}. {name}")

if __name__ == "__main__":
    main() 