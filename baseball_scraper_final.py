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
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Check for empty or error responses
        if len(response.text) < 1000:  # Very small response likely indicates an error
            print(f"Received a very small response for year {year}. This year might not have data.")
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check for "no players found" message
        if "no players found" in response.text.lower():
            print(f"No players found for year {year}")
            return []
        
        # From our inspection, Table 1 is the player table
        tables = soup.find_all('table')
        if not tables or len(tables) < 1:
            print(f"Could not find any tables on the page for year {year}")
            return []
        
        player_table = tables[0]  # First table on the page
        
        players = []
        count = 0
        
        # Process each row in the table
        rows = player_table.find_all('tr')
        if len(rows) < 2:
            print(f"Player table does not have enough rows for year {year}")
            return []
        
        # Skip the first row which might be a header or empty row
        for row in rows[1:]:  # Start from second row
            cells = row.find_all('td')
            
            # Based on our inspection, the player table has 5 columns
            if len(cells) >= 5:
                # First cell contains player name link
                player_link = cells[0].find('a')
                
                if player_link:
                    full_name = player_link.text.strip()
                    # Skip header rows which might have text like "Player"
                    if full_name.lower() == "player":
                        continue
                        
                    link_href = player_link.get('href')
                    
                    # Skip invalid links
                    if not link_href or '?' in link_href:
                        continue
                    
                    # Second cell contains birth date
                    birth_date = cells[1].text.strip() if len(cells) > 1 else ""
                    
                    # Third cell contains death date (if available)
                    death_date = cells[2].text.strip() if len(cells) > 2 else ""
                    
                    # Fourth cell contains debut year
                    debut_year = cells[3].text.strip() if len(cells) > 3 else ""
                    
                    # Fifth cell contains final year
                    final_year = cells[4].text.strip() if len(cells) > 4 else ""
                    
                    # Ensure we have a complete URL
                    link_url = 'https://www.baseball-almanac.com' + link_href if link_href.startswith('/') else link_href
                    
                    player_data = {
                        "full_name": full_name,
                        "birth_date": birth_date,
                        "death_date": death_date,
                        "debut_year": debut_year,
                        "final_year": final_year,
                        "source": "Baseball Almanac",
                        "birth_year": year,
                        "player_url": link_url
                    }
                    
                    # Preliminary name parsing
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
                    
                    # Progress update
                    if count % 10 == 0:
                        print(f"Processed {count} players for year {year}...")
                    
                    # For testing purposes, limit the number of players
                    if max_players and count >= max_players:
                        break
    except Exception as e:
        print(f"Error processing year {year}: {e}")
        return []
    
    print(f"Found {len(players)} players born in {year}")
    return players

def scrape_player_detail(url, max_retries=3):
    """
    Scrape additional player details from their individual page.
    
    Args:
        url (str): URL of the player's detail page
        max_retries (int): Maximum number of retry attempts
        
    Returns:
        dict: Additional player data including nickname if available
    """
    # Add headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    
    for attempt in range(max_retries):
        try:
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
            
            return player_data
            
        except Exception as e:
            if attempt < max_retries - 1:
                sleep_time = 2 * (attempt + 1)  # Exponential backoff
                print(f"Error on attempt {attempt+1}, retrying in {sleep_time} seconds: {e}")
                time.sleep(sleep_time)
            else:
                print(f"Failed to fetch {url} after {max_retries} attempts: {e}")
                return {}

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
    # Years to scrape - comprehensive range from 1845 to 1920
    years = list(range(1845, 1921))  # This creates a list from 1845 to 1920 inclusive
    
    # Get all players per year (not just a test sample)
    max_players_per_year = None
    
    # Delay between years to be respectful to the server
    delay_between_years = 5
    
    # Use different filenames for the comprehensive dataset
    output_prefix = "comprehensive_baseball_"
    
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
        if first and first != "Player":  # Skip header rows
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
        if nick and nick != "None":  # Skip empty or "None" nicknames
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
        "nicknames": nicknames_list,
        "years_collected": years,
        "total_players": len(all_players)
    }
    
    # Save the data with new filenames
    save_as_json(all_players, f"{output_prefix}players.json")
    save_as_csv(all_players, f"{output_prefix}players.csv")
    
    save_as_json(names_by_type, f"{output_prefix}names_by_type.json")
    
    # Also save each name type separately for easier access
    save_as_csv(first_names_list, f"{output_prefix}first_names.csv")
    save_as_csv(last_names_list, f"{output_prefix}last_names.csv")
    save_as_csv(nicknames_list, f"{output_prefix}nicknames.csv")
    
    print("\nData processing complete!")
    
    # Print some statistics
    print(f"\nStatistics:")
    print(f"Total players: {len(all_players)}")
    print(f"Unique first names: {len(first_names)}")
    print(f"Unique last names: {len(last_names)}")
    print(f"Unique nicknames: {len(nicknames)}")
    print(f"Years collected: {min(years)}-{max(years)}")
    
    if all_players:
        print("\nSample entries:")
        for i, player in enumerate(all_players[:3]):
            print(f"Player {i+1}: {player}")
            
if __name__ == "__main__":
    main() 