"""
Test script to compare all three name generator methods
"""
from census_name_generator import CensusNameGenerator
from collections import Counter
import statistics

def test_all_generators():
    """
    Test and compare all three Census name generator methods:
    1. Standard Census Name Generator
    2. Unique Census Name Generator 
    3. Claude's Fancier/Quanty-er Unique Names
    """
    generator = CensusNameGenerator()
    
    # Generate sample names from all generators
    sample_size = 50
    standard_names = generator.generate_multiple(sample_size)
    unique_names = generator.generate_multiple_unique(sample_size)
    weighted_unique_names = generator.generate_multiple_weighted_unique(sample_size)
    
    # Extract first and last names
    standard_first = [name.split()[0] for name in standard_names]
    standard_last = [name.split()[1] for name in standard_names]
    
    unique_first = [name.split()[0] for name in unique_names]
    unique_last = [name.split()[1] for name in unique_names]
    
    weighted_first = [name.split()[0] for name in weighted_unique_names]
    weighted_last = [name.split()[1] for name in weighted_unique_names]
    
    # Get different tiers of common names
    sorted_first_names = sorted(generator.first_names, key=lambda x: x[1], reverse=True)
    sorted_last_names = sorted(generator.last_names, key=lambda x: x[1], reverse=True)
    
    first_name_count = len(sorted_first_names)
    last_name_count = len(sorted_last_names)
    
    top_100_first = {name for name, _ in sorted_first_names[:100]}
    top_100_last = {name for name, _ in sorted_last_names[:100]}
    
    top_10_percent_first = {name for name, _ in sorted_first_names[:int(first_name_count * 0.1)]}
    top_10_percent_last = {name for name, _ in sorted_last_names[:int(last_name_count * 0.1)]}
    
    bottom_50_percent_first = {name for name, _ in sorted_first_names[int(first_name_count * 0.5):]}
    bottom_50_percent_last = {name for name, _ in sorted_last_names[int(last_name_count * 0.5):]}
    
    # Count metrics for all generators
    metrics = {
        "Standard Census Names": {
            "top_100_first": sum(1 for name in standard_first if name in top_100_first),
            "top_100_last": sum(1 for name in standard_last if name in top_100_last),
            "top_100_both": sum(1 for i in range(sample_size) 
                              if standard_first[i] in top_100_first and standard_last[i] in top_100_last),
            "top_10p_first": sum(1 for name in standard_first if name in top_10_percent_first),
            "top_10p_last": sum(1 for name in standard_last if name in top_10_percent_last),
            "bottom_50p_first": sum(1 for name in standard_first if name in bottom_50_percent_first),
            "bottom_50p_last": sum(1 for name in standard_last if name in bottom_50_percent_last),
            "unique_names": len(set(standard_names))
        },
        "Unique Census Names": {
            "top_100_first": sum(1 for name in unique_first if name in top_100_first),
            "top_100_last": sum(1 for name in unique_last if name in top_100_last),
            "top_100_both": sum(1 for i in range(sample_size) 
                              if unique_first[i] in top_100_first and unique_last[i] in top_100_last),
            "top_10p_first": sum(1 for name in unique_first if name in top_10_percent_first),
            "top_10p_last": sum(1 for name in unique_last if name in top_10_percent_last),
            "bottom_50p_first": sum(1 for name in unique_first if name in bottom_50_percent_first),
            "bottom_50p_last": sum(1 for name in unique_last if name in bottom_50_percent_last),
            "unique_names": len(set(unique_names))
        },
        "Claude's Fancier/Quanty-er Unique Names": {
            "top_100_first": sum(1 for name in weighted_first if name in top_100_first),
            "top_100_last": sum(1 for name in weighted_last if name in top_100_last),
            "top_100_both": sum(1 for i in range(sample_size) 
                              if weighted_first[i] in top_100_first and weighted_last[i] in top_100_last),
            "top_10p_first": sum(1 for name in weighted_first if name in top_10_percent_first),
            "top_10p_last": sum(1 for name in weighted_last if name in top_10_percent_last),
            "bottom_50p_first": sum(1 for name in weighted_first if name in bottom_50_percent_first),
            "bottom_50p_last": sum(1 for name in weighted_last if name in bottom_50_percent_last),
            "unique_names": len(set(weighted_unique_names))
        }
    }
    
    # Print results
    print(f"\n=== Name Generation Comparison ({sample_size} samples) ===\n")
    
    # Print sample names for each generator
    print("Standard Census Names:")
    for i in range(min(10, sample_size)):
        print(f"{i+1}. {standard_names[i]}")
    
    print("\nUnique Census Names:")
    for i in range(min(10, sample_size)):
        print(f"{i+1}. {unique_names[i]}")
        
    print("\nClaude's Fancier/Quanty-er Unique Names:")
    for i in range(min(10, sample_size)):
        print(f"{i+1}. {weighted_unique_names[i]}")
    
    # Print comparative statistics
    print("\n=== Comparative Statistics ===")
    
    metrics_labels = {
        "top_100_first": "Top 100 first names",
        "top_100_last": "Top 100 last names",
        "top_100_both": "Both names in top 100",
        "top_10p_first": "First names in top 10%",
        "top_10p_last": "Last names in top 10%",
        "bottom_50p_first": "First names in bottom 50%",
        "bottom_50p_last": "Last names in bottom 50%",
        "unique_names": "Unique names in sample"
    }
    
    for metric, label in metrics_labels.items():
        print(f"\n{label}:")
        for generator_name, stats in metrics.items():
            value = stats[metric]
            percentage = (value / sample_size) * 100 if metric != "unique_names" else (value / sample_size) * 100
            print(f"  {generator_name}: {value}/{sample_size if metric != 'unique_names' else sample_size} ({percentage:.1f}%)")
    
    # Print duplicate analysis
    print("\n=== Duplicate Analysis ===")
    for generator_name in metrics.keys():
        if generator_name == "Standard Census Names":
            names_list = standard_names
        elif generator_name == "Unique Census Names":
            names_list = unique_names
        else:
            names_list = weighted_unique_names
            
        duplicates = [item for item, count in Counter(names_list).items() if count > 1]
        if duplicates:
            print(f"{generator_name} - Duplicates found:")
            for duplicate in duplicates:
                print(f"  {duplicate} ({Counter(names_list)[duplicate]} times)")
        else:
            print(f"{generator_name} - No duplicates found")

if __name__ == "__main__":
    test_all_generators() 