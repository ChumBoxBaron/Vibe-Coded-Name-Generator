import requests
from bs4 import BeautifulSoup
import json
import time
import os
import re

# Output directory
OUTPUT_DIR = "baseball_data"

def ensure_output_dir():
    """Make sure the output directory exists."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created output directory: {OUTPUT_DIR}")

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
    
    try:
        print(f"  Fetching details from {url}")
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
                            print(f"  Found nickname: {value}")
                    elif 'full name' in label or 'given name' in label:
                        player_data['full_legal_name'] = value
                    elif 'position' in label:
                        player_data['position'] = value
        
        return player_data
        
    except Exception as e:
        print(f"  Error fetching player details: {e}")
        return {}

def scrape_year(year):
    """Scrape baseball player names for a specific birth year."""
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
        
        # Process first 5 player links for the test
        for i, link in enumerate(player_links[:5]):
            try:
                full_name = link.text.strip()
                href = link.get('href')
                
                if not full_name or full_name.lower() == 'player':
                    continue
                    
                print(f"Processing player {i+1}/5 for year {year}: {full_name}")
                
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
                
                # Get additional details from player page
                if player_url:
                    detail_data = scrape_player_detail(player_url)
                    player_data.update(detail_data)
                    # Add a small delay between requests
                    time.sleep(2)  
                
                players.append(player_data)
                
            except Exception as e:
                print(f"Error processing player link: {e}")
        
        print(f"Successfully processed {len(players)} players for year {year}")
        return players
        
    except Exception as e:
        print(f"Error processing year {year}: {e}")
        return []

if __name__ == "__main__":
    # Create the output directory
    ensure_output_dir()
    
    # Test with just a few years
    test_years = [1890, 1895, 1900]
    all_players = []
    
    for year in test_years:
        print(f"\nTesting year {year}...")
        players = scrape_year(year)
        
        if players:
            # Save the data
            output_file = os.path.join(OUTPUT_DIR, f"test_players_{year}.json")
            with open(output_file, "w") as f:
                json.dump(players, f, indent=2)
            print(f"Saved {len(players)} players to {output_file}")
            
            # Add to overall collection
            all_players.extend(players)
    
    # Save combined results
    combined_file = os.path.join(OUTPUT_DIR, "test_all_players.json")
    with open(combined_file, "w") as f:
        json.dump(all_players, f, indent=2)
    
    print(f"\nTest complete! Collected {len(all_players)} players total.")
    print(f"Results saved to {combined_file}") 