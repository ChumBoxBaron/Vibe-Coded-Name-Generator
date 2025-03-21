import requests
from bs4 import BeautifulSoup
import json
import time
import os
import re
import random
import datetime
import logging

# Configuration
TARGET_YEAR = 1845
BASE_URL = "https://www.baseball-almanac.com/players/baseball_births.php?y={}"  # Updated to correct URL
OUTPUT_DIR = "baseball_data"
TEST_DIR = os.path.join(OUTPUT_DIR, "tests")
PROGRESS_FILE = os.path.join(TEST_DIR, "test_1845_progress.json")
OUTPUT_FILE = os.path.join(TEST_DIR, "test_1845_result.json")
LOG_FILE = os.path.join(TEST_DIR, "test_1845_log.txt")

# Request headers to mimic a browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://www.baseball-almanac.com/',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0',
}

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Add console handler
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

# Delay settings - increased to be more respectful of the server
YEAR_DELAY = (5, 10)  # Seconds to wait between years
PLAYER_DELAY = (2, 5)  # Seconds to wait between player detail pages
MAX_RETRIES = 3  # Maximum number of retry attempts for network errors

def ensure_dir_exists(dir_path):
    """Ensure the directory exists."""
    os.makedirs(dir_path, exist_ok=True)
    
def load_progress():
    """Load progress from a file."""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"completed_players": [], "current_year": TARGET_YEAR}

def save_progress(progress):
    """Save progress to a file."""
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, indent=2)
    logging.info(f"Progress saved to {PROGRESS_FILE}")

def random_delay(delay_range):
    """Sleep for a random amount of time within the range."""
    delay = random.uniform(delay_range[0], delay_range[1])
    logging.info(f"Waiting for {delay:.2f} seconds...")
    time.sleep(delay)

def get_with_retry(url, max_retries=MAX_RETRIES):
    """Make a GET request with retry logic."""
    for attempt in range(max_retries):
        try:
            # Add a longer delay between retries
            if attempt > 0:
                backoff = 5 + (2 ** attempt) + random.random() * 5
                logging.info(f"Retrying in {backoff:.2f} seconds... (Attempt {attempt+1}/{max_retries})")
                time.sleep(backoff)
            
            # Make the request with headers
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()  # Raise exception for HTTP errors
            
            # Log successful request
            logging.info(f"Successfully retrieved {url}")
            
            return response
        except requests.exceptions.RequestException as e:
            logging.error(f"Request error: {e}")
            if attempt < max_retries - 1:
                continue
            else:
                logging.error(f"Failed to retrieve {url} after {max_retries} attempts")
                raise

def parse_birth_name(text):
    """Parse birth name from player detail page."""
    if not text:
        return None, None, None
    
    # Remove any "Born as" or similar prefix
    if "Born as " in text:
        text = text.split("Born as ")[1].strip()
    
    # Split the name into parts
    parts = text.split()
    
    if len(parts) == 0:
        return None, None, None
    elif len(parts) == 1:
        return parts[0], None, None
    elif len(parts) == 2:
        return parts[0], None, parts[1]
    else:
        # Assume first part is first name, last part is last name, and middle is everything in between
        first = parts[0]
        last = parts[-1]
        middle = ' '.join(parts[1:-1])
        return first, middle, last

def simple_name_split(full_name):
    """Split a name into first and last name components."""
    parts = full_name.split()
    if len(parts) == 1:
        return parts[0], ""  # Just a single name
    else:
        # Take the first part as first name, everything else as last name
        return parts[0], ' '.join(parts[1:])

def process_player_data(player_data):
    """Process player data to ensure consistent name fields."""
    # If we have a birth name, use it for the first/last name fields
    if player_data.get("birth_name"):
        birth_first, birth_middle, birth_last = parse_birth_name(player_data["birth_name"])
        
        if birth_first:
            player_data["birth_first_name"] = birth_first
            player_data["first_name"] = birth_first  # Use birth first name
            
        if birth_middle:
            player_data["birth_middle_name"] = birth_middle
            
        if birth_last:
            player_data["birth_last_name"] = birth_last
            player_data["last_name"] = birth_last  # Use birth last name
    
    # If we don't have birth names, use the display name
    if not player_data.get("first_name") or not player_data.get("last_name"):
        first, last = simple_name_split(player_data["full_name"])
        if not player_data.get("first_name"):
            player_data["first_name"] = first
        if not player_data.get("last_name"):
            player_data["last_name"] = last
    
    # Process nicknames
    if player_data.get("nickname"):
        # Split nicknames separated by "or"
        player_data["nicknames"] = [n.strip() for n in re.split(r'\s+or\s+', player_data["nickname"])]
    else:
        player_data["nicknames"] = []
    
    return player_data

def scrape_player_detail(player_url, player_name, birth_year, date_of_birth=None, date_of_death=None, debut_year=None, final_year=None):
    """Scrape detailed information for a player."""
    logging.info(f"Scraping player details for {player_name} from {player_url}")
    
    player_data = {
        "full_name": player_name,
        "player_url": player_url,
        "player_id": player_url.split('/')[-1].replace('.shtml', '').replace('player.php?p=', ''),
        "birth_year": birth_year,
        "source": "Baseball Almanac"
    }
    
    # Add the data we already have from the player list
    if date_of_birth:
        player_data["birth_date"] = date_of_birth
    if date_of_death:
        player_data["death_date"] = date_of_death
    if debut_year:
        player_data["debut_year"] = debut_year
    if final_year:
        player_data["final_year"] = final_year
    
    # Extract first/last name from full name
    first_name, last_name = simple_name_split(player_name)
    player_data["first_name"] = first_name
    player_data["last_name"] = last_name
    
    try:
        response = get_with_retry(player_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for biographical data
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
                    logging.info(f"Found birth name: {birth_name_value}")
                    
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
                    player_data["nickname"] = nickname_value
                    nickname_found = True
                    logging.info(f"Found nickname: {nickname_value}")
        
        if not birth_name_found:
            logging.warning(f"Birth name not found for {player_name}")
            
        if not nickname_found:
            logging.warning(f"Nickname not found for {player_name}")
        
        return process_player_data(player_data)
        
    except Exception as e:
        logging.error(f"Error scraping player detail: {e}")
        return process_player_data(player_data)

def scrape_year(year, progress):
    """Scrape player data for a specific birth year."""
    logging.info(f"Scraping players born in {year}...")
    url = BASE_URL.format(year)
    
    try:
        # Try to get the page
        response = get_with_retry(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Debug: Save the HTML for inspection
        debug_path = os.path.join(TEST_DIR, f"debug_year_{year}_page.html")
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(response.text)
        logging.info(f"Saved page HTML to {debug_path} for inspection")
        
        # Find the player table - this is the main table with player data
        # The table usually has a specific structure with player names and their details
        player_table = None
        tables = soup.find_all('table')
        
        for table in tables:
            # Check if this table has the player data headers (Player, Date of Birth, etc.)
            headers = table.find_all('th') or table.find_all('td', {'class': 'header'})
            header_text = [h.text.strip() for h in headers]
            
            if any(['Player' in h for h in header_text]) or any(['Date of Birth' in h for h in header_text]):
                player_table = table
                break
        
        # If we can't find the table directly, look for specific patterns in the page
        if not player_table:
            # Try to find the table with player links
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 2:  # Most player tables have at least 2 columns
                        links = row.find_all('a', href=lambda href: href and "/players/player.php?p=" in href)
                        if links:
                            player_table = table
                            break
                if player_table:
                    break
        
        if not player_table:
            logging.warning(f"Could not find player table for year {year}")
            return []
        
        # Process the player table
        players = []
        rows = player_table.find_all('tr')
        
        # Log the number of rows for debugging
        logging.info(f"Found {len(rows)} rows in the player table")
        
        # Skip header row if present
        start_row = 1 if len(rows) > 1 and not rows[0].find('a', href=lambda href: href and "/players/player.php?p=" in href) else 0
        
        for row in rows[start_row:]:
            cells = row.find_all('td')
            if len(cells) < 2:  # Need at least player name and one other column
                continue
            
            # Find player link - this should be in the first cell
            player_link = row.find('a', href=lambda href: href and "/players/player.php?p=" in href)
            if not player_link:
                continue
            
            player_name = player_link.text.strip()
            player_url = player_link['href']
            
            if not player_url.startswith('http'):
                player_url = 'https://www.baseball-almanac.com' + player_url
            
            # Extract other data from the row cells
            date_of_birth = cells[1].text.strip() if len(cells) > 1 else None
            date_of_death = cells[2].text.strip() if len(cells) > 2 else None
            debut_year = cells[3].text.strip() if len(cells) > 3 else None
            final_year = cells[4].text.strip() if len(cells) > 4 else None
            
            # Skip already processed players
            if player_url in progress["completed_players"]:
                logging.info(f"Skipping already processed player: {player_name}")
                continue
            
            try:
                # Scrape player details
                player_data = scrape_player_detail(
                    player_url, 
                    player_name, 
                    year, 
                    date_of_birth, 
                    date_of_death, 
                    debut_year, 
                    final_year
                )
                players.append(player_data)
                progress["completed_players"].append(player_url)
                
                # Save progress after each player
                save_progress(progress)
                
                # Random delay between player requests
                random_delay(PLAYER_DELAY)
                
            except Exception as e:
                logging.error(f"Error processing {player_name}: {e}")
        
        return players
        
    except Exception as e:
        logging.error(f"Error scraping year {year}: {e}")
        return []

def generate_name_lists(players):
    """Generate lists of first names, last names, and nicknames with frequencies."""
    first_names = {}
    last_names = {}
    nicknames = {}
    
    for player in players:
        # First name
        first = player.get("first_name")
        if first:
            first_names[first] = first_names.get(first, 0) + 1
        
        # Last name
        last = player.get("last_name")
        if last:
            last_names[last] = last_names.get(last, 0) + 1
        
        # Nicknames
        for nickname in player.get("nicknames", []):
            nicknames[nickname] = nicknames.get(nickname, 0) + 1
    
    return {
        "first_names": first_names,
        "last_names": last_names,
        "nicknames": nicknames
    }

def main():
    """Main function to scrape a single year of player data."""
    # Ensure directories exist
    ensure_dir_exists(OUTPUT_DIR)
    ensure_dir_exists(TEST_DIR)
    
    # Reset progress file for clean test
    if os.path.exists(PROGRESS_FILE):
        os.remove(PROGRESS_FILE)
    
    # Load progress
    progress = load_progress()
    
    # Scrape 1845
    all_players = []
    logging.info(f"Starting test scrape for year {TARGET_YEAR}")
    
    year_players = scrape_year(TARGET_YEAR, progress)
    if year_players:
        all_players.extend(year_players)
        logging.info(f"Added {len(year_players)} players from {TARGET_YEAR}")
    
    # Generate name lists
    name_lists = generate_name_lists(all_players)
    
    # Create final dataset
    dataset = {
        "meta": {
            "collection_date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "years_included": [TARGET_YEAR],
            "total_players": len(all_players),
            "version": "test_v2"
        },
        "name_lists": name_lists,
        "players": all_players
    }
    
    # Save the final dataset
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2)
    
    logging.info(f"Test completed! {len(all_players)} players saved to {OUTPUT_FILE}")
    logging.info(f"Found {len(name_lists['first_names'])} unique first names")
    logging.info(f"Found {len(name_lists['last_names'])} unique last names")
    logging.info(f"Found {len(name_lists['nicknames'])} unique nicknames")

if __name__ == "__main__":
    main() 