import os
import sys
from simplified_scraper import (ensure_output_dir, load_progress, save_progress, 
                             scrape_player_detail, simple_name_split, save_final_output, 
                             generate_name_lists, PROGRESS_FILE, OUTPUT_DIR, COMBINED_OUTPUT_FILE)
import requests
from bs4 import BeautifulSoup
import json
import time

# Configuration for the small test
TEST_START_YEAR = 1895
TEST_END_YEAR = 1897
PLAYERS_PER_YEAR = 10  # Just get 10 players per year for testing
DELAY_BETWEEN_YEARS = 5
DELAY_BETWEEN_PLAYERS = 1

def scrape_year_limited(year, max_players=10):
    """
    Scrape a limited number of baseball player names for a specific birth year.
    
    Args:
        year (int): The birth year to scrape
        max_players (int): Maximum number of players to scrape
        
    Returns:
        list: A list of dictionaries containing player name data
    """
    url = f"https://www.baseball-almanac.com/players/baseball_births.php?y={year}"
    print(f"Downloading baseball player data from {url}...")
    
    # Add headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        players = []
        
        # Look for links that might be player links
        all_links = soup.find_all('a')
        player_links = []
        
        for link in all_links:
            href = link.get('href')
            if href and '/players/player.php?p=' in href:
                player_links.append(link)
        
        print(f"Found {len(player_links)} potential player links for year {year}")
        print(f"Will process only {max_players} players for testing")
        
        if len(player_links) == 0:
            print(f"No players found for year {year}")
            return []
        
        # Process limited number of player links
        for i, link in enumerate(player_links[:max_players]):
            try:
                full_name = link.text.strip()
                href = link.get('href')
                
                if not full_name or full_name.lower() == 'player':
                    continue
                    
                print(f"Processing player {i+1}/{max_players} for year {year}: {full_name}")
                
                # Try to find parent row to get additional data
                parent_row = link.find_parent('tr')
                birth_date = ""
                death_date = ""
                debut_year = ""
                final_year = ""
                
                if parent_row:
                    cells = parent_row.find_all('td')
                    if len(cells) >= 5:
                        birth_date = cells[1].text.strip() if len(cells) > 1 else ""
                        death_date = cells[2].text.strip() if len(cells) > 2 else ""
                        debut_year = cells[3].text.strip() if len(cells) > 3 else ""
                        final_year = cells[4].text.strip() if len(cells) > 4 else ""
                
                player_url = 'https://www.baseball-almanac.com' + href if href.startswith('/') else href
                
                player_data = {
                    "full_name": full_name,
                    "birth_date": birth_date,
                    "death_date": death_date,
                    "debut_year": debut_year,
                    "final_year": final_year,
                    "source": "Baseball Almanac",
                    "birth_year": year,
                    "player_url": player_url
                }
                
                # Parse the name
                name_parts = simple_name_split(full_name)
                player_data.update(name_parts)
                
                # Try to get details from player page
                if player_url:
                    try:
                        print(f"  Scraping details from {player_url}")
                        detail_data = scrape_player_detail(player_url)
                        player_data.update(detail_data)
                        # Add delay to avoid overwhelming the server
                        time.sleep(DELAY_BETWEEN_PLAYERS)
                    except Exception as e:
                        print(f"  Error scraping details: {e}")
                
                players.append(player_data)
                
            except Exception as e:
                print(f"Error processing player link: {e}")
        
        print(f"Successfully processed {len(players)} players for year {year}")
        return players
        
    except Exception as e:
        print(f"Error processing year {year}: {e}")
        return []

def process_test_batch():
    """Process a small test batch of years with limited players per year."""
    # Ensure output directory exists
    ensure_output_dir()
    
    # Use a different progress file for the test
    test_progress_file = "test_baseball_progress.json"
    if os.path.exists(test_progress_file):
        with open(test_progress_file, "r") as f:
            progress = json.load(f)
    else:
        progress = {"completed_years": [], "all_players": []}
    
    # Define the years to process
    years_to_process = list(range(TEST_START_YEAR, TEST_END_YEAR + 1))
    remaining_years = [year for year in years_to_process if year not in progress['completed_years']]
    
    print(f"Starting TEST baseball data collection")
    print(f"Years to process: {len(remaining_years)} out of {len(years_to_process)}")
    print(f"Already completed: {len(progress['completed_years'])} years")
    
    for year in remaining_years:
        print(f"\n{'='*40}")
        print(f"Processing year {year}...")
        print(f"{'='*40}\n")
        
        players = scrape_year_limited(year, PLAYERS_PER_YEAR)
        
        if players:
            # Save year data individually
            year_file = os.path.join(OUTPUT_DIR, f"test_players_{year}.json")
            with open(year_file, "w") as f:
                json.dump(players, f, indent=2)
            print(f"Saved {len(players)} players from {year} to {year_file}")
            
            # Add to overall collection
            progress['all_players'].extend(players)
            progress['completed_years'].append(year)
            
            # Save progress
            with open(test_progress_file, "w") as f:
                json.dump(progress, f, indent=2)
            
            # Save combined file
            combined_file = os.path.join(OUTPUT_DIR, "test_all_players.json")
            with open(combined_file, "w") as f:
                json.dump(progress['all_players'], f, indent=2)
            print(f"Updated combined file with total of {len(progress['all_players'])} players")
        
        if year != remaining_years[-1]:
            print(f"Waiting {DELAY_BETWEEN_YEARS} seconds before processing next year...")
            time.sleep(DELAY_BETWEEN_YEARS)
    
    # Generate final output
    if progress['all_players']:
        # Generate name lists for the test data
        name_lists = generate_name_lists(progress['all_players'])
        
        # Save as JSON with name lists
        final_file = os.path.join(OUTPUT_DIR, "test_dataset_complete.json")
        
        # Meta information
        meta = {
            "source": "Baseball Almanac (TEST)",
            "collection_date": time.strftime("%Y-%m-%d"),
            "years_covered": f"{TEST_START_YEAR}-{TEST_END_YEAR}",
            "total_players": len(progress['all_players']),
            "unique_first_names": len(name_lists['first_names']),
            "unique_last_names": len(name_lists['last_names']),
            "unique_nicknames": len(name_lists['nicknames'])
        }
        
        final_data = {
            "meta": meta,
            "name_lists": name_lists,
            "players": progress['all_players']
        }
        
        with open(final_file, "w") as f:
            json.dump(final_data, f, indent=2)
        print(f"Saved complete test dataset to {final_file}")
        
        # Print statistics
        print("\nTest Statistics:")
        for key, value in meta.items():
            print(f"{key}: {value}")

if __name__ == "__main__":
    process_test_batch() 