from baseball_name_generator import BaseballNameGenerator

# Initialize the generator
generator = BaseballNameGenerator()

# Test specific problematic names
test_names = [
    "@JuanSoto25_)",
    "Juan Soto",
    "Williams)",
    "Smith",
    "Rodriguez",
    "The Bruggy Boys (with Moe Berg)"
]

print("Testing name cleaning function:")
for name in test_names:
    cleaned = generator.clean_name(name)
    valid = generator.is_valid_name(name)
    print(f"'{name}' -> '{cleaned}' | Valid: {'YES' if valid else 'NO'}")

# Verify that problematic names are properly handled in the processed data
print("\nVerifying processed data...")

# Check for any names with @ symbol in any category
found_at_symbol = False
for names_list in [generator.first_names, generator.last_names, generator.nicknames]:
    for name, _ in names_list:
        if "@" in name:
            found_at_symbol = True
            print(f"WARNING: Found name with @ symbol: '{name}'")

if not found_at_symbol:
    print("SUCCESS: No names with @ symbol found in processed data")
    
# Check for names ending with parenthesis
found_trailing_paren = False
for names_list in [generator.first_names, generator.last_names, generator.nicknames]:
    for name, _ in names_list:
        if name.endswith(')'):
            found_trailing_paren = True
            print(f"WARNING: Found name with trailing parenthesis: '{name}'")

if not found_trailing_paren:
    print("SUCCESS: No names with trailing parentheses found in processed data")

# Check if cleaned names are in the dataset
print("\nVerifying presence of cleaned names:")
test_cases = ["Williams", "Rippay", "Glenalvin", "Mik", "Hogan"]
for test_name in test_cases:
    found = False
    for name, count in generator.last_names:
        if name == test_name:
            found = True
            print(f"SUCCESS: Found cleaned name '{test_name}' in dataset (count: {count})")
            break
    if not found:
        print(f"WARNING: Cleaned name '{test_name}' not found in dataset") 