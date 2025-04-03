import json
import pprint

# Load the player data
with open('baseball_data/all_baseball_players.json', 'r') as f:
    players = json.load(f)

# Search terms to find interesting entries
search_terms = [
    "Bruggy Boys",
    "Gold Dust Twins",
    "Born Emmet",
    "Patón",
    "Jíbaro"
]

# Find players with these interesting nicknames
interesting_players = []

for player in players:
    first = player.get('first_name', '')
    last = player.get('last_name', '')
    nick = player.get('nickname', '')
    
    # Search in all name fields
    for term in search_terms:
        if (term in first) or (term in last) or (term in nick):
            interesting_players.append(player)
            break

# Print the complete data for interesting players
print(f"Found {len(interesting_players)} interesting players with special nicknames:\n")

for i, player in enumerate(interesting_players, 1):
    print(f"===== Player {i} =====")
    
    # Extract the nickname and other key fields for highlighting
    nickname = player.get("nickname", "")
    
    # Print specific important fields first
    print(f"First name: {player.get('first_name', '')}")
    print(f"Last name: {player.get('last_name', '')}")
    print(f"Nickname: {nickname}")
    print(f"Full name: {player.get('full_name', '')}")
    print(f"Full legal name: {player.get('full_legal_name', '')}")
    
    # Print other details
    print("\nComplete player data:")
    pprint.pprint(player)
    print("\n" + "="*50 + "\n") 