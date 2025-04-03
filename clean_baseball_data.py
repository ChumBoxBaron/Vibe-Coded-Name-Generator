import json
import re
import os

# Data directory and file paths
DATA_DIR = "baseball_data"
INPUT_FILE = os.path.join(DATA_DIR, "all_baseball_players.json")
OUTPUT_FILE = os.path.join(DATA_DIR, "cleaned_baseball_players.json")

def is_valid_name(name):
    """
    Check if a name is valid (doesn't contain unwanted characters).
    
    Args:
        name (str): The name to check
        
    Returns:
        bool: True if the name is valid, False otherwise
    """
    if not name or len(name) < 2:
        return False
        
    # Reject names with @ symbol or unmatched parentheses
    if '@' in name or name.endswith(')'):
        return False
        
    # Pattern to match unwanted special characters
    # Allow letters, numbers, spaces, dots, commas, apostrophes, and hyphens
    pattern = r'[^a-zA-Z0-9\s\.\,\'\-]'
    
    # Allow matched parentheses for nicknames like "(Old Reliable)"
    if name.count('(') == name.count(')') and '(' in name:
        return True
        
    # Reject other special characters
    if re.search(pattern, name):
        return False
        
    return True

def clean_player_data(player):
    """
    Clean a player's data by removing invalid names.
    
    Args:
        player (dict): Player data dictionary
        
    Returns:
        dict: Cleaned player data
    """
    cleaned_player = player.copy()
    
    # Check first name
    first = player.get("first_name", "")
    if first and not is_valid_name(first):
        cleaned_player["first_name"] = ""
    
    # Check last name
    last = player.get("last_name", "")
    if last and not is_valid_name(last):
        cleaned_player["last_name"] = ""
    
    # Check nickname
    nick = player.get("nickname", "")
    if nick and not is_valid_name(nick):
        cleaned_player["nickname"] = ""
    
    return cleaned_player

def clean_baseball_data():
    """
    Clean the baseball data file by removing invalid names.
    """
    if not os.path.exists(INPUT_FILE):
        print(f"Input file not found: {INPUT_FILE}")
        return
    
    try:
        with open(INPUT_FILE, 'r') as f:
            players = json.load(f)
        
        print(f"Loaded {len(players)} players from {INPUT_FILE}")
        
        # Clean player data
        cleaned_players = []
        problem_count = 0
        
        for player in players:
            cleaned_player = clean_player_data(player)
            
            # Skip players with no valid names left
            if not cleaned_player["first_name"] and not cleaned_player["last_name"]:
                problem_count += 1
                continue
            
            cleaned_players.append(cleaned_player)
        
        # Save cleaned data
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(cleaned_players, f, indent=2)
        
        print(f"Cleaned data saved to {OUTPUT_FILE}")
        print(f"Removed {problem_count} problematic players")
        print(f"Kept {len(cleaned_players)} valid players")
        
    except Exception as e:
        print(f"Error cleaning data: {e}")

if __name__ == "__main__":
    clean_baseball_data() 