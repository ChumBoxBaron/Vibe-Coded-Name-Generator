import json
import re

# Load the player data
with open('baseball_data/all_baseball_players.json', 'r') as f:
    players = json.load(f)

# Pattern to match special characters except spaces and standard punctuation
special_char_pattern = r'[^a-zA-Z0-9\s\.\,\'\-]'

# Find players with special characters in their names
special_char_examples = []
juan_soto_entries = []

for idx, player in enumerate(players):
    first = player.get('first_name', '')
    last = player.get('last_name', '')
    nick = player.get('nickname', '')
    
    # Check for special characters
    if re.search(special_char_pattern, first):
        special_char_examples.append(f"First name: {first}")
    if re.search(special_char_pattern, last):
        special_char_examples.append(f"Last name: {last}")
    if re.search(special_char_pattern, nick):
        special_char_examples.append(f"Nickname: {nick}")
    
    # Find the exact JuanSoto entry
    if '@JuanSoto25_)' in [first, last, nick]:
        juan_soto_entries.append({
            'index': idx,
            'player': player
        })

# Print the examples
print(f"Found {len(special_char_examples)} names with special characters:")
for example in special_char_examples[:20]:  # Limit output to first 20
    print(example)

print("\nDetails of @JuanSoto25_) entries:")
for entry in juan_soto_entries:
    print(f"Index in data: {entry['index']}")
    print(json.dumps(entry['player'], indent=2)) 