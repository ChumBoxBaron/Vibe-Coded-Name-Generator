"""
Test script for the Unique Census Name generator
"""
from census_name_generator import CensusNameGenerator
from collections import Counter

def test_name_uniqueness():
    """
    Test to compare standard Census Name generator with the Unique Census Name generator
    """
    generator = CensusNameGenerator()
    
    # Generate sample names from both generators
    sample_size = 50
    standard_names = generator.generate_multiple(sample_size)
    unique_names = generator.generate_multiple_unique(sample_size)
    
    # Extract first and last names
    standard_first = [name.split()[0] for name in standard_names]
    standard_last = [name.split()[1] for name in standard_names]
    
    unique_first = [name.split()[0] for name in unique_names]
    unique_last = [name.split()[1] for name in unique_names]
    
    # Get top 100 most common names
    top_first_names = {name for name, _ in sorted(generator.first_names, key=lambda x: x[1], reverse=True)[:100]}
    top_last_names = {name for name, _ in sorted(generator.last_names, key=lambda x: x[1], reverse=True)[:100]}
    
    # Count how many names are from the top 100 lists
    standard_top_first_count = sum(1 for name in standard_first if name in top_first_names)
    standard_top_last_count = sum(1 for name in standard_last if name in top_last_names)
    
    unique_top_first_count = sum(1 for name in unique_first if name in top_first_names)
    unique_top_last_count = sum(1 for name in unique_last if name in top_last_names)
    
    # Count combinations of top 100 names
    standard_both_top_count = sum(1 for i in range(sample_size) 
                                if standard_first[i] in top_first_names and standard_last[i] in top_last_names)
    
    unique_both_top_count = sum(1 for i in range(sample_size) 
                              if unique_first[i] in top_first_names and unique_last[i] in top_last_names)
    
    # Print results
    print(f"\n=== Name Generation Comparison ({sample_size} samples) ===\n")
    
    print("Standard Census Names:")
    for i in range(min(10, sample_size)):
        print(f"{i+1}. {standard_names[i]}")
    
    print("\nUnique Census Names:")
    for i in range(min(10, sample_size)):
        print(f"{i+1}. {unique_names[i]}")
    
    print("\n=== Statistics ===")
    print(f"Standard Census Names - Top 100 first names: {standard_top_first_count}/{sample_size} ({standard_top_first_count/sample_size*100:.1f}%)")
    print(f"Standard Census Names - Top 100 last names: {standard_top_last_count}/{sample_size} ({standard_top_last_count/sample_size*100:.1f}%)")
    print(f"Standard Census Names - Both top 100: {standard_both_top_count}/{sample_size} ({standard_both_top_count/sample_size*100:.1f}%)")
    
    print(f"\nUnique Census Names - Top 100 first names: {unique_top_first_count}/{sample_size} ({unique_top_first_count/sample_size*100:.1f}%)")
    print(f"Unique Census Names - Top 100 last names: {unique_top_last_count}/{sample_size} ({unique_top_last_count/sample_size*100:.1f}%)")
    print(f"Unique Census Names - Both top 100: {unique_both_top_count}/{sample_size} ({unique_both_top_count/sample_size*100:.1f}%)")
    
    # Verify our algorithm is working correctly
    assert unique_both_top_count == 0, "Unique Census Names should never combine top 100 first and last names"
    
    # Print most frequent names in each set
    print("\nMost common first names in standard set:")
    print(Counter(standard_first).most_common(5))
    
    print("\nMost common first names in unique set:")
    print(Counter(unique_first).most_common(5))
    
    print("\nMost common last names in standard set:")
    print(Counter(standard_last).most_common(5))
    
    print("\nMost common last names in unique set:")
    print(Counter(unique_last).most_common(5))

if __name__ == "__main__":
    test_name_uniqueness() 