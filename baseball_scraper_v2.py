import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import re
import time

def scrape_baseball_names(year, follow_links=True, max_players=None):
    """
    Scrape baseball player names from Baseball Almanac for a specific birth year.
    
    Args:
        year (int): The birth year to scrape
        follow_links (bool): Whether to follow links to player detail pages
        max_players (int, optional): Maximum number of players to scrape (for testing)
        
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
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the section heading for players born in this year
    section_heading = soup.find('h2', string=f'MLB Players That Were Born in {year}')
    
    if not section_heading:
        print(f"Could not find players born in {year}")
        return []
    
    # Find the table after this heading - typically it's the next table
    player_table = None
    current = section_heading.next_sibling
    
    while current and not player_table:
        if current.name == 'table':
            player_table = current
        elif hasattr(current, 'next_sibling'):
            current = current.next_sibling
        else:
            break
    
    if not player_table:
        print("Could not find player data table")
        return []
    
    players = []
    count = 0
    
    # Process each row in the table
    for row in player_table.find_all('tr'):
        # Skip header row
        if row.find('th'):
            continue
            
        cells = row.find_all('td')
        if len(cells) >= 2:  # Player name and date of birth at minimum
            player_link = cells[0].find('a')
            if player_link:
                full_name = player_link.text.strip()
                link_href = player_link.get('href')
                
                # Ensure we have a complete URL
                if link_href:
                    link_url = 'https://www.baseball-almanac.com' + link_href if link_href.startswith('/') else link_href
                    
                    # Try to get birth date from the second column
                    birth_date = cells[1].text.strip() if len(cells) > 1 else ""
                    
                    player_data = {
                        "full_name": full_name,
                        "birth_date": birth_date,
                        "source": "Baseball Almanac",
                        "birth_year": year,
                        "player_url": link_url
                    }
                    
                    # Preliminary name parsing (will be refined with data from detail page)
                    name_parts = simple_name_split(full_name)
                    player_data.update(name_parts)
                    
                    # Follow link to get more details if requested
                    if follow_links:
                        try:
                            print(f"Scraping details for {full_name}...")
                            detail_data = scrape_player_detail(link_url)
                            player_data.update(detail_data)
                            # Increase delay between requests to avoid being blocked
                            time.sleep(1)
                        except Exception as e:
                            print(f"Error scraping details for {full_name}: {e}")
                    
                    players.append(player_data)
                    count += 1
                    
                    # For testing purposes, limit the number of players
                    if max_players and count >= max_players:
                        break
    
    print(f"Found {len(players)} players born in {year}")
    return players

def scrape_player_detail(url):
    """
    Scrape additional player details from their individual page.
    
    Args:
        url (str): URL of the player's detail page
        
    Returns:
        dict: Additional player data including nickname if available
    """
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
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    player_data = {}
    
    # Find the table with player details - look for tables with two column format
    tables = soup.find_all('table')
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 2:
                label = cells[0].text.strip().lower()
                value = cells[1].text.strip()
                
                # Look for specific fields we're interested in
                if 'nickname' in label:
                    player_data['nickname'] = value
                elif 'full name' in label or 'given name' in label:
                    player_data['full_legal_name'] = value
                elif 'position' in label:
                    player_data['position'] = value
                elif 'born' in label or 'birth' in label:
                    player_data['birth_info'] = value
    
    return player_data

def simple_name_split(full_name):
    """
    Do a simple split of a full name into first and last parts.
    This is a fallback if we can't get detailed info from player page.
    
    Args:
        full_name (str): Full player name
        
    Returns:
        dict: Dictionary with first_name and last_name fields
    """
    # Split into parts
    name_parts = full_name.split()
    
    if len(name_parts) < 2:
        return {
            "first_name": full_name,
            "last_name": "",
            "nickname": ""
        }
    
    # Often a nickname may be a first name like "Dutch" Ulrich
    # This is a guess, not perfect
    if len(name_parts) == 2:
        return {
            "first_name": name_parts[0],
            "last_name": name_parts[1],
            "nickname": ""
        }
    
    # If there are 3+ parts, the middle one might be a nickname or middle name
    # This is just a heuristic
    return {
        "first_name": name_parts[0],
        "last_name": " ".join(name_parts[-1:]),  # Just take the last part
        "nickname": " ".join(name_parts[1:-1]) if len(name_parts) > 2 else ""  # Middle parts could be nicknames
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
    # Years to scrape - testing with just one year
    years = [1899]  # Using 1899 which we know has data
    
    # Set to a small number for initial testing
    max_players_per_year = 3  # Start with just 3 players to test
    
    # Increase delay between years
    delay_between_years = 5
    
    all_players = []
    
    for i, year in enumerate(years):
        print(f"\nProcessing year {year} ({i+1} of {len(years)})...")
        players = scrape_baseball_names(year, follow_links=True, max_players=max_players_per_year)
        all_players.extend(players)
        
        # Add a delay between years to be respectful to the server
        # Skip delay after the last year
        if i < len(years) - 1:
            print(f"Waiting {delay_between_years} seconds before processing the next year...")
            time.sleep(delay_between_years)
    
    # Extract first names (with frequencies)
    first_names = {}
    for player in all_players:
        first = player.get("first_name", "")
        if first:
            if first in first_names:
                first_names[first] += 1
            else:
                first_names[first] = 1
    
    first_names_list = [{"name": name, "frequency": count, "type": "first_name"} 
                        for name, count in first_names.items()]
    
    # Extract last names (with frequencies)
    last_names = {}
    for player in all_players:
        last = player.get("last_name", "")
        if last:
            if last in last_names:
                last_names[last] += 1
            else:
                last_names[last] = 1
    
    last_names_list = [{"name": name, "frequency": count, "type": "last_name"} 
                       for name, count in last_names.items()]
    
    # Extract nicknames (with frequencies)
    nicknames = {}
    for player in all_players:
        nick = player.get("nickname", "")
        if nick:
            if nick in nicknames:
                nicknames[nick] += 1
            else:
                nicknames[nick] = 1
    
    nicknames_list = [{"name": name, "frequency": count, "type": "nickname"} 
                      for name, count in nicknames.items()]
    
    # Create structured data sets
    names_by_type = {
        "first_names": first_names_list,
        "last_names": last_names_list,
        "nicknames": nicknames_list
    }
    
    # Save the data
    save_as_json(all_players, "baseball_players.json")
    save_as_csv(all_players, "baseball_players.csv")
    
    save_as_json(names_by_type, "baseball_names_by_type.json")
    
    # Also save each name type separately for easier access
    save_as_csv(first_names_list, "baseball_first_names.csv")
    save_as_csv(last_names_list, "baseball_last_names.csv")
    save_as_csv(nicknames_list, "baseball_nicknames.csv")
    
    print("\nData processing complete!")
    
    # Print some statistics
    print(f"\nStatistics:")
    print(f"Total players: {len(all_players)}")
    print(f"Unique first names: {len(first_names)}")
    print(f"Unique last names: {len(last_names)}")
    print(f"Unique nicknames: {len(nicknames)}")
    
    if all_players:
        print("\nSample entries:")
        for i, player in enumerate(all_players[:3]):
            print(f"Player {i+1}: {player}")
            
if __name__ == "__main__":
    main() 