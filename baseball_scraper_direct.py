import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import re
import time

def scrape_specific_page():
    """
    Scrape baseball player names directly from the 1899 page.
    """
    url = "https://www.baseball-almanac.com/players/baseball_births.php?y=1899"
    print(f"Downloading baseball player data from {url}...")
    
    # Add headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    # Save the HTML for inspection
    with open("baseball_page_1899.html", "w", encoding="utf-8") as f:
        f.write(response.text)
    print("Saved HTML to baseball_page_1899.html for inspection")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    players = []
    
    # Look for links that might be player links
    all_links = soup.find_all('a')
    player_links = []
    
    for link in all_links:
        href = link.get('href')
        if href and '/players/player.php?p=' in href:
            player_links.append(link)
    
    print(f"Found {len(player_links)} potential player links")
    
    # Process each player link
    for i, link in enumerate(player_links):
        try:
            full_name = link.text.strip()
            href = link.get('href')
            
            if not full_name or full_name.lower() == 'player':
                continue
                
            print(f"Processing player {i+1}/{len(player_links)}: {full_name}")
            
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
                "birth_year": 1899,
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
                    time.sleep(2)
                except Exception as e:
                    print(f"  Error scraping details: {e}")
            
            players.append(player_data)
            
        except Exception as e:
            print(f"Error processing player link: {e}")
    
    print(f"Successfully processed {len(players)} players")
    return players

def scrape_player_detail(url):
    """
    Scrape additional player details from their individual page.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    player_data = {}
    
    # Find the table with player details
    tables = soup.find_all('table')
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 2:
                label = cells[0].text.strip().lower()
                value = cells[1].text.strip()
                
                # Look for specific fields
                if 'nickname' in label:
                    player_data['nickname'] = value
                elif 'full name' in label or 'given name' in label:
                    player_data['full_legal_name'] = value
                elif 'position' in label:
                    player_data['position'] = value
    
    return player_data

def simple_name_split(full_name):
    """
    Split a full name into first and last parts.
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

def save_as_json(data, output_file):
    """Save data as JSON file."""
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"JSON data saved to {output_file}")

def save_as_csv(data, output_file):
    """Save data as CSV file."""
    df = pd.DataFrame(data)
    df.to_csv(output_file, index=False)
    print(f"CSV data saved to {output_file}")

def main():
    players = scrape_specific_page()
    
    # Process for name frequencies
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
        if nick and nick != "None":
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
    
    # Create structured data
    names_by_type = {
        "first_names": first_names_list,
        "last_names": last_names_list,
        "nicknames": nicknames_list,
        "years_collected": [1899],
        "total_players": len(players)
    }
    
    # Save the data
    save_as_json(players, "direct_baseball_players.json")
    save_as_csv(players, "direct_baseball_players.csv")
    
    save_as_json(names_by_type, "direct_baseball_names_by_type.json")
    
    # Also save each name type separately
    save_as_csv(first_names_list, "direct_baseball_first_names.csv")
    save_as_csv(last_names_list, "direct_baseball_last_names.csv")
    save_as_csv(nicknames_list, "direct_baseball_nicknames.csv")
    
    print("\nData processing complete!")
    
    # Print statistics
    print(f"\nStatistics:")
    print(f"Total players: {len(players)}")
    print(f"Unique first names: {len(first_names)}")
    print(f"Unique last names: {len(last_names)}")
    print(f"Unique nicknames: {len(nicknames)}")
    
    if players:
        print("\nSample entries:")
        for i, player in enumerate(players[:3]):
            print(f"Player {i+1}: {player}")

if __name__ == "__main__":
    main() 