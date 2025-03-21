import os
import json
import time
import pprint
from simplified_scraper import (
    scrape_player_detail, 
    parse_birth_name, 
    process_player_data, 
    simple_name_split,
    ensure_output_dir
)

def test_player_detail(player_url, display_name, birth_year):
    """Test scraping player details with the improved code."""
    print(f"\nTesting player: {display_name} ({player_url})")
    
    # Get basic name parts from display name
    name_parts = simple_name_split(display_name)
    
    # Create initial player data
    player_data = {
        "full_name": display_name,
        "birth_year": birth_year,
        "player_url": player_url
    }
    player_data.update(name_parts)
    
    # Scrape detailed info
    print("Scraping player details...")
    detail_data = scrape_player_detail(player_url)
    player_data.update(detail_data)
    
    # Process player data
    print("Processing player data...")
    player_data = process_player_data(player_data)
    
    # Print result
    print("\nProcessed player data:")
    pprint.pprint(player_data)
    
    return player_data

def main():
    """Test the improved scraper on specific players."""
    # Ensure output directory exists
    ensure_output_dir()
    
    # List of players to test (display name, URL, birth year)
    test_players = [
        # Artie Wilson (has birth name "Arthur Lee Wilson" and multiple nicknames)
        ("Artie Wilson", "https://www.baseball-almanac.com/players/player.php?p=wilsoar02", 1920),
        
        # Babe Ruth (known by nickname rather than birth name)
        ("Babe Ruth", "https://www.baseball-almanac.com/players/player.php?p=ruthba01", 1895),
        
        # Jackie Robinson (modern player with middle name)
        ("Jackie Robinson", "https://www.baseball-almanac.com/players/player.php?p=robinja02", 1919),
        
        # Ducky Holmes (multiple nicknames)
        ("Ducky Holmes", "https://www.baseball-almanac.com/players/player.php?p=holmedu01", 1869)
    ]
    
    # Process each test player
    results = []
    for display_name, url, birth_year in test_players:
        player_data = test_player_detail(url, display_name, birth_year)
        results.append(player_data)
        # Add a delay to avoid overwhelming the server
        if test_players.index((display_name, url, birth_year)) < len(test_players) - 1:
            print("Waiting 3 seconds before next player...")
            time.sleep(3)
    
    # Save test results
    output_file = os.path.join("baseball_data", "test_improved_scraper.json")
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved test results to {output_file}")

if __name__ == "__main__":
    main() 