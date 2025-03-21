import os
import sys
from baseball_batch_scraper import scrape_year, ensure_output_dir, simple_name_split, scrape_player_detail

# Quick test script to verify the scraper functionality on a single year

if __name__ == "__main__":
    # Create the output directory
    ensure_output_dir()
    
    # Test year - using a later year that should have more players
    test_year = 1900
    
    print(f"Testing baseball scraper on year {test_year}...")
    players = scrape_year(test_year)
    
    if players:
        print(f"\nSuccessfully scraped {len(players)} players from year {test_year}")
        
        # Print the first 5 players as sample
        print("\nSample players:")
        for i, player in enumerate(players[:5]):
            print(f"Player {i+1}: {player['full_name']}")
            if 'nickname' in player and player['nickname']:
                print(f"  Nickname: {player['nickname']}")
            print(f"  First name: {player['first_name']}")
            print(f"  Last name: {player['last_name']}")
            print(f"  Birth date: {player['birth_date']}")
            if 'position' in player:
                print(f"  Position: {player['position']}")
            print()
    else:
        print(f"Failed to scrape any players from year {test_year}")
        sys.exit(1)
        
    print("Test completed successfully!") 