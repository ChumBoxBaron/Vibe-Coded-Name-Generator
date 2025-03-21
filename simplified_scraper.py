import requests
from bs4 import BeautifulSoup
import json
import time
import os
import re
import csv
from datetime import datetime

# Configure the years to scrape
START_YEAR = 1845
END_YEAR = 1920
DELAY_BETWEEN_YEARS = 10  # Seconds between years
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
    return {"completed_years": [], "all_players": []}

def save_progress(progress):
    """Save the progress to the progress file."""
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2)
    print(f"Progress saved to {PROGRESS_FILE}")

def scrape_player_detail(url):
    """
    Scrape additional player details from their individual page.
    
    Args:
        url (str): URL of the player's detail page
        
    Returns:
        dict: Additional player data including birth name and nickname if available
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
            birth_name_found = False
            nickname_found = False
            
            # Find elements with class 'biocolpad'
            bio_cells = soup.find_all('td', class_='biocolpad')
            for i in range(len(bio_cells) - 1):
                cell = bio_cells[i]
                cell_text = cell.text.strip()
                
                # Check if this is a label cell
                if cell_text == 'Birth Name:':
                    # Get the next cell which should contain the value
                    value_cell = bio_cells[i + 1]
                    birth_name_value = value_cell.text.strip()
                    # Remove non-breaking spaces and clean up
                    birth_name_value = birth_name_value.replace('\xa0', ' ').strip()
                    if birth_name_value:
                        player_data["birth_name"] = birth_name_value
                        birth_name_found = True
                        print(f"  Found birth name: {birth_name_value}")
                        
                        # Parse birth name into components
                        birth_first, birth_middle, birth_last = parse_birth_name(birth_name_value)
                        if birth_first:
                            player_data["birth_first_name"] = birth_first
                        if birth_middle:
                            player_data["birth_middle_name"] = birth_middle
                        if birth_last:
                            player_data["birth_last_name"] = birth_last
                
                # Check if this is a nickname label cell
                elif cell_text == 'Nickname:':
                    # Get the next cell which should contain the value
                    value_cell = bio_cells[i + 1]
                    nickname_value = value_cell.text.strip()
                    # Remove non-breaking spaces and clean up
                    nickname_value = nickname_value.replace('\xa0', ' ').strip()
                    if nickname_value and nickname_value.lower() != 'none':
                        player_data['nickname'] = nickname_value
                        nickname_found = True
                        print(f"  Found nickname: {nickname_value}")
                        # Process nickname to split by "or" if needed
                        if " or " in nickname_value:
                            player_data['nicknames'] = [nick.strip() for nick in nickname_value.split(" or ")]
            
            # If we didn't find bio_cells, fall back to traditional table search
            if not bio_cells or (not birth_name_found and not nickname_found):
                # Find the table with player details
                tables = soup.find_all('table')
                for table in tables:
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 2:
                            label = cells[0].text.strip().lower()
                            value = cells[1].text.strip()
                            
                            # Capture birth name
                            if 'birth name' in label and not birth_name_found:
                                birth_name_value = value
                                player_data['birth_name'] = birth_name_value
                                # Parse birth name into components
                                birth_first, birth_middle, birth_last = parse_birth_name(birth_name_value)
                                if birth_first:
                                    player_data["birth_first_name"] = birth_first
                                if birth_middle:
                                    player_data["birth_middle_name"] = birth_middle
                                if birth_last:
                                    player_data["birth_last_name"] = birth_last
                                birth_name_found = True
                                print(f"  Found birth name (table): {birth_name_value}")
                            
                            # Look for specific fields
                            elif 'nickname' in label and not nickname_found:
                                nickname_value = value
                                if nickname_value and nickname_value.lower() != 'none':
                                    player_data['nickname'] = nickname_value
                                    nickname_found = True
                                    print(f"  Found nickname (table): {nickname_value}")
                                    # Process nickname to split by "or" if needed
                                    if " or " in nickname_value:
                                        player_data['nicknames'] = [nick.strip() for nick in nickname_value.split(" or ")]
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

def parse_birth_name(birth_name):
    """
    Parse a birth name into components (first, middle, last).
    
    Args:
        birth_name (str): Full birth name
        
    Returns:
        tuple: (first_name, middle_name, last_name)
    """
    # Clean up the name
    birth_name = re.sub(r'\s+', ' ', birth_name).strip()
    
    # Split into parts
    parts = birth_name.split()
    
    if not parts:
        return None, None, None
    
    # Handle different cases based on number of parts
    if len(parts) == 1:
        return parts[0], None, None
    elif len(parts) == 2:
        return parts[0], None, parts[1]
    else:
        return parts[0], ' '.join(parts[1:-1]), parts[-1]

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
    
    # For names with more than 2 parts, assume first and last name with potential middle names
    return {
        "first_name": name_parts[0],
        "last_name": name_parts[-1],
        "nickname": ""  # We'll populate this from the player detail page or set later
    }

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
        
        # Check if the page indicates no players were born this year
        no_players_texts = ["no players in our database", "no records found", "no players found"]
        page_text = soup.text.lower()
        for text in no_players_texts:
            if text in page_text:
                print(f"No players found for year {year} (confirmed by page text)")
                return []
        
        players = []
        
        # ==== APPROACH 1: Find player table using specific selectors ====
        # Try to find the table - specifically looking for player data tables
        main_tables = []
        
        # First, look for the main content div
        main_content = soup.find('div', {'id': 'content'}) or soup.find('div', {'class': 'content'})
        if main_content:
            # Find all tables within main content
            main_tables = main_content.find_all('table')
            
        # If no main content div found, get all tables
        if not main_tables:
            main_tables = soup.find_all('table')
        
        # Filter tables for those that likely contain player data
        player_tables = []
        for table in main_tables:
            # Check if table has appropriate structure
            if table.find('a', href=lambda h: h and '/players/player.php' in h):
                player_tables.append(table)
        
        print(f"Found {len(player_tables)} potential player tables")
        
        # ==== PROCESS PLAYER DATA ====
        for table_idx, table in enumerate(player_tables):
            print(f"Examining table {table_idx+1}/{len(player_tables)}")
            
            rows = table.find_all('tr')
            
            # Skip header rows and find rows with player data
            player_rows = []
            for row in rows:
                cells = row.find_all('td')
                if cells and len(cells) >= 1:
                    # Look for player link in any cell
                    player_link = None
                    for cell in cells:
                        link = cell.find('a', href=lambda h: h and '/players/player.php' in h)
                        if link:
                            player_link = link
                            break
                    
                    if player_link:
                        player_rows.append((row, player_link))
            
            print(f"Found {len(player_rows)} player rows in table {table_idx+1}")
            
            # Process each player row
            for i, (row, player_link) in enumerate(player_rows):
                try:
                    cells = row.find_all('td')
                    
                    full_name = player_link.text.strip()
                    href = player_link.get('href')
                    
                    if not full_name or not href or full_name.lower() == 'player':
                        continue
                    
                    print(f"Processing player {i+1}/{len(player_rows)} for year {year}: {full_name}")
                    
                    # Try to extract additional data from cells
                    # These will vary by table structure so we'll try different patterns
                    birth_date = ""
                    death_date = ""
                    debut_year = ""
                    final_year = ""
                    
                    # Look for cells with date-like content (##/##/####)
                    for cell in cells:
                        cell_text = cell.text.strip()
                        # Birth date pattern: MM/DD/YYYY or Month D(D), YYYY
                        if (re.search(r'\d{1,2}/\d{1,2}/\d{4}', cell_text) or 
                            re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}', cell_text)):
                            if str(year) in cell_text:  # Confirm this is birth date by checking it contains the year
                                birth_date = cell_text
                    
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
                            
                            # Process the player data to reconcile names and nicknames
                            player_data = process_player_data(player_data)
                            
                            # Add delay to avoid overwhelming the server
                            time.sleep(DELAY_BETWEEN_PLAYERS)
                        except Exception as e:
                            print(f"  Error scraping details: {e}")
                    
                    players.append(player_data)
                    
                except Exception as e:
                    print(f"Error processing player row: {e}")
        
        print(f"Successfully processed {len(players)} players for year {year}")
        return players
        
    except Exception as e:
        print(f"Error processing year {year}: {e}")
        return []

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
        
        # Mark the year as processed regardless of finding players
        progress['completed_years'].append(year)
        
        if players:
            # Save year data individually
            year_file = os.path.join(OUTPUT_DIR, f"baseball_players_{year}.json")
            with open(year_file, "w") as f:
                json.dump(players, f, indent=2)
            print(f"Saved {len(players)} players from {year} to {year_file}")
            
            # Add to overall collection
            progress['all_players'].extend(players)
        else:
            print(f"No players found for year {year}, marking as processed")
            
        # Save progress after each year
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
    # Count frequencies using a dictionary
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
            # Some nicknames have "or" in them, split those
            if " or " in nick.lower():
                parts = nick.split(" or ")
                for part in parts:
                    if part and len(part.strip()) > 1:
                        if part.strip() in nicknames:
                            nicknames[part.strip()] += 1
                        else:
                            nicknames[part.strip()] = 1
            else:
                if nick in nicknames:
                    nicknames[nick] += 1
                else:
                    nicknames[nick] = 1
        
        # Also check the 'nicknames' array if it exists
        if player.get("nicknames"):
            for nickname in player["nicknames"]:
                if nickname and nickname.strip() and len(nickname.strip()) > 1:
                    if nickname.strip() in nicknames:
                        nicknames[nickname.strip()] += 1
                    else:
                        nicknames[nickname.strip()] = 1
    
    # Convert to lists
    first_names_list = [{"name": name, "frequency": count, "type": "first_name"} 
                        for name, count in sorted(first_names.items(), key=lambda x: x[1], reverse=True)]
    
    last_names_list = [{"name": name, "frequency": count, "type": "last_name"} 
                       for name, count in sorted(last_names.items(), key=lambda x: x[1], reverse=True)]
    
    nicknames_list = [{"name": name, "frequency": count, "type": "nickname"} 
                      for name, count in sorted(nicknames.items(), key=lambda x: x[1], reverse=True)]
    
    return {
        "first_names": first_names_list,
        "last_names": last_names_list,
        "nicknames": nicknames_list
    }

def save_as_csv(data, filename):
    """Save data list to a CSV file."""
    if not data:
        return
    
    # Get all possible keys from all dictionaries in data
    keys = set()
    for item in data:
        keys.update(item.keys())
    keys = sorted(list(keys))
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for item in data:
            writer.writerow(item)

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
    for name_type, name_list in name_lists.items():
        csv_file = os.path.join(OUTPUT_DIR, f"baseball_{name_type}.csv")
        save_as_csv(name_list, csv_file)
        print(f"Saved {name_type} to {csv_file}")
    
    # Save players as CSV
    players_csv = os.path.join(OUTPUT_DIR, "baseball_all_players.csv")
    save_as_csv(players, players_csv)
    print(f"Saved all players to {players_csv}")
    
    # Print statistics
    print("\nFinal Statistics:")
    for key, value in meta.items():
        print(f"{key}: {value}")

def get_years_to_process():
    """Get all years that need to be processed."""
    all_years = list(range(START_YEAR, END_YEAR + 1))
    return all_years

def process_player_data(player_data):
    """
    Process player data after fetching details to reconcile names and nicknames.
    
    Args:
        player_data (dict): Player data dictionary
        
    Returns:
        dict: Updated player data with reconciled names
    """
    # Use birth name if available for first name
    if 'birth_first_name' in player_data and player_data['birth_first_name']:
        # Check if the displayed first name is different from birth first name
        display_first = player_data.get('first_name', '')
        birth_first = player_data['birth_first_name']
        
        if display_first and display_first.lower() != birth_first.lower():
            # The displayed first name might be a nickname
            if not player_data.get('nickname'):
                player_data['nickname'] = display_first
            elif display_first not in player_data['nickname']:
                # Append to nickname if not already there
                if " or " in player_data['nickname']:
                    if not any(nick.strip().lower() == display_first.lower() for nick in player_data['nickname'].split(" or ")):
                        player_data['nickname'] += f" or {display_first}"
                else:
                    player_data['nickname'] = f"{player_data['nickname']} or {display_first}"
        
        # Update first name to birth first name
        player_data['first_name'] = birth_first
    
    # Use birth last name if available
    if 'birth_last_name' in player_data and player_data['birth_last_name']:
        player_data['last_name'] = player_data['birth_last_name']
    
    # Process nicknames - split by "or" if not already done
    if 'nickname' in player_data and player_data['nickname'] and " or " in player_data['nickname'] and 'nicknames' not in player_data:
        player_data['nicknames'] = [nick.strip() for nick in player_data['nickname'].split(" or ")]
    
    return player_data

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
    
    # Process all remaining years
    process_batch(remaining_years, progress)
    
    # Final processing
    print("\nAll years complete!")
    save_final_output(progress['all_players'])
    print("Baseball data collection complete!")

if __name__ == "__main__":
    main() 