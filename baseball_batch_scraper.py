import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import re
import time
import os
import sys
from datetime import datetime

# Configure the years to scrape
START_YEAR = 1845
END_YEAR = 1920
BATCH_SIZE = 5  # Process this many years at a time
DELAY_BETWEEN_YEARS = 10  # Seconds between years
DELAY_BETWEEN_BATCHES = 60  # Seconds between batches
DELAY_BETWEEN_PLAYERS = 2  # Seconds between player detail pages

# File to track progress
PROGRESS_FILE = "baseball_scraper_progress.json"
OUTPUT_DIR = "baseball_data"
COMBINED_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "all_baseball_players.json")

def ensure_output_dir():
    """Make sure the output directory exists."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created output directory: {OUTPUT_DIR}")

def load_progress():
    """Load the progress from the progress file."""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {"completed_years": [], "current_batch": [], "all_players": []}

def save_progress(progress):
    """Save the progress to the progress file."""
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2)
    print(f"Progress saved to {PROGRESS_FILE}")

def scrape_year(year):
    """
    Scrape baseball player names for a specific birth year.
    
    Args:
        year (int): The birth year to scrape
        
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
        
        # Save the HTML for reference (optional)
        html_file = os.path.join(OUTPUT_DIR, f"baseball_page_{year}.html")
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(response.text)
        
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
        
        if len(player_links) == 0:
            print(f"No players found for year {year}")
            return []
        
        # Process each player link
        for i, link in enumerate(player_links):
            try:
                full_name = link.text.strip()
                href = link.get('href')
                
                if not full_name or full_name.lower() == 'player':
                    continue
                    
                print(f"Processing player {i+1}/{len(player_links)} for year {year}: {full_name}")
                
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

def scrape_player_detail(url):
    """
    Scrape additional player details from their individual page.
    
    Args:
        url (str): URL of the player's detail page
        
    Returns:
        dict: Additional player data including nickname if available
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    
    for attempt in range(3):  # Try up to 3 times
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            player_data = {}
            nickname_found = False
            
            # Find the table with player details
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        label = cells[0].text.strip().lower()
                        value = cells[1].text.strip()
                        
                        # Skip "Birth Name:" label, which is coming up as a nickname
                        if 'birth name' in label:
                            continue
                        
                        # Look for specific fields
                        if 'nickname' in label and not nickname_found:
                            if value and value.lower() != 'none':
                                player_data['nickname'] = value
                                nickname_found = True
                        elif 'full name' in label or 'given name' in label:
                            player_data['full_legal_name'] = value
                        elif 'position' in label:
                            player_data['position'] = value
            
            return player_data
            
        except Exception as e:
            if attempt < 2:  # Don't sleep after the last attempt
                sleep_time = 5 * (attempt + 1)  # Exponential backoff
                print(f"  Error on attempt {attempt+1}, retrying in {sleep_time} seconds: {e}")
                time.sleep(sleep_time)
            else:
                print(f"  Failed to fetch {url} after 3 attempts: {e}")
    
    return {}  # Return empty dict if all attempts fail

def simple_name_split(full_name):
    """
    Split a full name into first and last parts.
    
    Args:
        full_name (str): Full player name
        
    Returns:
        dict: Dictionary with first_name, last_name, and nickname fields
    """
    # Remove non-breaking spaces and other whitespace
    full_name = re.sub(r'\s+', ' ', full_name).strip()
    
    # Split into parts
    name_parts = full_name.split()
    
    if len(name_parts) < 2:
        return {
            "first_name": full_name,
            "last_name": "",
            "nickname": ""
        }
    
    if len(name_parts) == 2:
        return {
            "first_name": name_parts[0],
            "last_name": name_parts[1],
            "nickname": ""
        }
    
    return {
        "first_name": name_parts[0],
        "last_name": " ".join(name_parts[-1:]),
        "nickname": " ".join(name_parts[1:-1]) if len(name_parts) > 2 else ""
    }

def process_batch(years_to_process, progress):
    """Process a batch of years."""
    for year in years_to_process:
        if year in progress['completed_years']:
            print(f"Year {year} already processed, skipping...")
            continue
            
        print(f"\n{'='*40}")
        print(f"Processing year {year}...")
        print(f"{'='*40}\n")
        
        players = scrape_year(year)
        
        if players:
            # Save year data individually
            year_file = os.path.join(OUTPUT_DIR, f"baseball_players_{year}.json")
            with open(year_file, "w") as f:
                json.dump(players, f, indent=2)
            print(f"Saved {len(players)} players from {year} to {year_file}")
            
            # Add to overall collection
            progress['all_players'].extend(players)
            progress['completed_years'].append(year)
            save_progress(progress)
            
            # Save combined file periodically
            with open(COMBINED_OUTPUT_FILE, "w") as f:
                json.dump(progress['all_players'], f, indent=2)
            print(f"Updated combined file with total of {len(progress['all_players'])} players")
        
        if year != years_to_process[-1]:
            print(f"Waiting {DELAY_BETWEEN_YEARS} seconds before processing next year...")
            time.sleep(DELAY_BETWEEN_YEARS)

def generate_name_lists(players):
    """
    Generate separate lists of first names, last names, and nicknames with frequencies.
    
    Args:
        players (list): List of player dictionaries
        
    Returns:
        dict: Dictionary with first_names, last_names, and nicknames lists
    """
    first_names = {}
    last_names = {}
    nicknames = {}
    
    for player in players:
        # First names
        first = player.get("first_name", "")
        if first and first != "Player":
            if first in first_names:
                first_names[first] += 1
            else:
                first_names[first] = 1
        
        # Last names
        last = player.get("last_name", "")
        if last:
            if last in last_names:
                last_names[last] += 1
            else:
                last_names[last] = 1
        
        # Nicknames
        nick = player.get("nickname", "")
        if nick and nick != "None" and nick.lower() != "none":
            if nick in nicknames:
                nicknames[nick] += 1
            else:
                nicknames[nick] = 1
    
    # Convert to lists
    first_names_list = [{"name": name, "frequency": count, "type": "first_name"} 
                        for name, count in first_names.items()]
    
    last_names_list = [{"name": name, "frequency": count, "type": "last_name"} 
                       for name, count in last_names.items()]
    
    nicknames_list = [{"name": name, "frequency": count, "type": "nickname"} 
                      for name, count in nicknames.items()]
    
    return {
        "first_names": first_names_list,
        "last_names": last_names_list,
        "nicknames": nicknames_list
    }

def save_final_output(players):
    """Save final organized output files."""
    # Load progress to get completed years
    progress = load_progress()
    
    # Generate name lists
    name_lists = generate_name_lists(players)
    
    # Meta information for the dataset
    meta = {
        "source": "Baseball Almanac",
        "collection_date": datetime.now().strftime("%Y-%m-%d"),
        "years_covered": f"{min(progress['completed_years'])}-{max(progress['completed_years'])}" if progress['completed_years'] else "",
        "total_players": len(players),
        "unique_first_names": len(name_lists['first_names']),
        "unique_last_names": len(name_lists['last_names']),
        "unique_nicknames": len(name_lists['nicknames'])
    }
    
    # Save combined dataset with meta information
    combined_data = {
        "meta": meta,
        "name_lists": name_lists,
        "players": players
    }
    
    combined_file = os.path.join(OUTPUT_DIR, "baseball_dataset_complete.json")
    with open(combined_file, "w") as f:
        json.dump(combined_data, f, indent=2)
    print(f"Saved complete dataset to {combined_file}")
    
    # Save individual CSV files for easy access
    for name_type in name_lists:
        csv_file = os.path.join(OUTPUT_DIR, f"baseball_{name_type}.csv")
        pd.DataFrame(name_lists[name_type]).to_csv(csv_file, index=False)
        print(f"Saved {name_type} to {csv_file}")
    
    # Save players as CSV
    players_csv = os.path.join(OUTPUT_DIR, "baseball_all_players.csv")
    pd.DataFrame(players).to_csv(players_csv, index=False)
    print(f"Saved all players to {players_csv}")
    
    # Print statistics
    print("\nFinal Statistics:")
    for key, value in meta.items():
        print(f"{key}: {value}")

def get_years_to_process():
    """Get all years that need to be processed."""
    all_years = list(range(START_YEAR, END_YEAR + 1))
    return all_years

def main():
    # Ensure output directory exists
    ensure_output_dir()
    
    # Load progress
    progress = load_progress()
    
    # Get years that need processing
    all_years = get_years_to_process()
    remaining_years = [year for year in all_years if year not in progress['completed_years']]
    
    if not remaining_years:
        print("All years have been processed!")
        save_final_output(progress['all_players'])
        return
    
    print(f"Starting baseball data collection")
    print(f"Years to process: {len(remaining_years)} out of {len(all_years)}")
    print(f"Already completed: {len(progress['completed_years'])} years")
    
    # Process in batches
    for i in range(0, len(remaining_years), BATCH_SIZE):
        batch = remaining_years[i:i+BATCH_SIZE]
        print(f"\nProcessing batch {i//BATCH_SIZE + 1} of {(len(remaining_years) + BATCH_SIZE - 1) // BATCH_SIZE}")
        print(f"Years in this batch: {batch}")
        
        process_batch(batch, progress)
        
        if i + BATCH_SIZE < len(remaining_years):
            print(f"\nBatch complete. Waiting {DELAY_BETWEEN_BATCHES} seconds before next batch...")
            time.sleep(DELAY_BETWEEN_BATCHES)
    
    # Final processing
    print("\nAll batches complete!")
    save_final_output(progress['all_players'])
    print("Baseball data collection complete!")

if __name__ == "__main__":
    main() 