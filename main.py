"""
Main entry point for the name generator application.
"""

from generators.baseball_generator import BaseballNameGenerator
from generators.census_generator import CensusNameGenerator

def demonstrate_baseball_generator():
    """Demonstrate the baseball name generator."""
    print("\n=== Baseball Name Generator ===\n")
    
    generator = BaseballNameGenerator()
    
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
    for name, count in generator.get_notable_nicknames(limit=5):
        print(f"{name}: {count}")

def demonstrate_census_generator():
    """Demonstrate the census name generator."""
    print("\n=== Census Name Generator ===\n")
    
    generator = CensusNameGenerator()
    
    # Generate some random names
    print("Random Generated Names:")
    names = generator.generate_multiple(10)
    for i, name in enumerate(names, 1):
        print(f"{i}. {name}")
    
    # Show some statistics
    print("\nMost Common First Names:")
    for name, freq in generator.get_most_common("first", 5):
        print(f"{name}: {freq}")
    
    print("\nMost Common Last Names:")
    for name, freq in generator.get_most_common("last", 5):
        print(f"{name}: {freq}")

def main():
    """Main function to demonstrate both generators."""
    print("Welcome to the Name Generator!")
    print("This program demonstrates different styles of name generation.\n")
    
    demonstrate_baseball_generator()
    demonstrate_census_generator()

if __name__ == "__main__":
    main() 