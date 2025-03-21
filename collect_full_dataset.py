import os
import sys
import requests
from bs4 import BeautifulSoup
import json
import time
import datetime
import argparse
from simplified_scraper import (ensure_output_dir, load_progress, save_progress, 
                             scrape_player_detail, simple_name_split, save_final_output, 
                             generate_name_lists, OUTPUT_DIR)

# Configuration for full data collection
DEFAULT_START_YEAR = 1845
DEFAULT_END_YEAR = 1920
DELAY_BETWEEN_YEARS = 10  # Longer delay for full dataset
DELAY_BETWEEN_PLAYERS = 2  # Longer delay between player scrapes
MAX_ERRORS_PER_YEAR = 5    # Maximum number of errors before skipping a year
PROGRESS_FILE = "full_baseball_progress.json"
FINAL_OUTPUT_FILE = "baseball_dataset_complete.json"

def scrape_year_full(year):
    """
    Scrape all baseball player names for a specific birth year.
    
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
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        players = []
        error_count = 0
        
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
        
        # Process all player links
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
                        error_count += 1
                        if error_count >= MAX_ERRORS_PER_YEAR:
                            print(f"Too many errors ({error_count}). Skipping remaining players for year {year}")
                            break
                
                players.append(player_data)
                
            except Exception as e:
                print(f"Error processing player link: {e}")
                error_count += 1
                if error_count >= MAX_ERRORS_PER_YEAR:
                    print(f"Too many errors ({error_count}). Skipping remaining players for year {year}")
                    break
        
        print(f"Successfully processed {len(players)} players for year {year}")
        return players
        
    except Exception as e:
        print(f"Error processing year {year}: {e}")
        return []

def process_full_dataset(start_year=DEFAULT_START_YEAR, end_year=DEFAULT_END_YEAR, year_delay=None):
    """
    Process the full dataset of baseball players for the specified year range.
    
    Args:
        start_year (int): First year to process (default: 1845)
        end_year (int): Last year to process (default: 1920)
        year_delay (int): Optional override for delay between years
    """
    # Use custom delay if provided
    delay_between_years = year_delay if year_delay is not None else DELAY_BETWEEN_YEARS
    
    # Ensure output directory exists
    ensure_output_dir()
    
    # Load existing progress if available
    if os.path.exists(PROGRESS_FILE):
        print(f"Loading progress from {PROGRESS_FILE}")
        with open(PROGRESS_FILE, "r") as f:
            progress = json.load(f)
    else:
        progress = {"completed_years": [], "all_players": []}
    
    # Define the years to process
    years_to_process = list(range(start_year, end_year + 1))
    remaining_years = [year for year in years_to_process if year not in progress['completed_years']]
    
    print(f"\nStarting baseball data collection for years {start_year}-{end_year}")
    print(f"Years to process: {len(remaining_years)} out of {len(years_to_process)}")
    print(f"Already completed in this range: {len(years_to_process) - len(remaining_years)} years")
    print(f"Total players collected so far: {len(progress['all_players'])}")
    
    start_time = datetime.datetime.now()
    print(f"Collection started at: {start_time}")
    
    for year in remaining_years:
        year_start_time = datetime.datetime.now()
        completed_count = len([y for y in progress['completed_years'] if start_year <= y <= end_year])
        total_in_range = len(years_to_process)
        
        print(f"\n{'='*60}")
        print(f"Processing year {year}... ({completed_count + 1} of {total_in_range} in current range)")
        print(f"{'='*60}\n")
        
        players = scrape_year_full(year)
        
        if players:
            # Save year data individually
            year_file = os.path.join(OUTPUT_DIR, f"full_players_{year}.json")
            with open(year_file, "w") as f:
                json.dump(players, f, indent=2)
            print(f"Saved {len(players)} players from {year} to {year_file}")
            
            # Add to overall collection
            progress['all_players'].extend(players)
            progress['completed_years'].append(year)
            
            # Save progress
            with open(PROGRESS_FILE, "w") as f:
                json.dump(progress, f, indent=2)
            
            # Save current combined file
            combined_file = os.path.join(OUTPUT_DIR, "full_all_players_current.json")
            with open(combined_file, "w") as f:
                json.dump(progress['all_players'], f, indent=2)
            print(f"Updated combined file with total of {len(progress['all_players'])} players")
        
            # Calculate and display time statistics
            year_end_time = datetime.datetime.now()
            year_duration = year_end_time - year_start_time
            elapsed_total = year_end_time - start_time
            remaining_years_count = len(remaining_years) - remaining_years.index(year) - 1
            
            print(f"\nTime statistics:")
            print(f"  Time for year {year}: {year_duration}")
            print(f"  Total elapsed time: {elapsed_total}")
            
            if remaining_years_count > 0 and remaining_years.index(year) > 0:
                avg_time_per_year = elapsed_total / (remaining_years.index(year) + 1)
                est_remaining_time = avg_time_per_year * remaining_years_count
                est_completion_time = year_end_time + est_remaining_time
                
                print(f"  Estimated time remaining: {est_remaining_time}")
                print(f"  Estimated completion time: {est_completion_time}")
        
        if year != remaining_years[-1]:
            print(f"Waiting {delay_between_years} seconds before processing next year...")
            time.sleep(delay_between_years)
    
    # Generate final output if all years in the full range are processed
    all_years_processed = all(year in progress['completed_years'] for year in range(DEFAULT_START_YEAR, DEFAULT_END_YEAR + 1))
    current_range_completed = len(remaining_years) == 0
    
    if all_years_processed:
        print("\nAll years in full range processed! Generating final dataset...")
        generate_final_dataset(progress['all_players'])
    elif current_range_completed:
        print(f"\nAll years in specified range {start_year}-{end_year} are complete.")
        print(f"To generate the final dataset, complete all years from {DEFAULT_START_YEAR} to {DEFAULT_END_YEAR}.")
        
        # Generate a subset dataset for the completed range
        name_lists = generate_name_lists(progress['all_players'])
        range_players = [p for p in progress['all_players'] if start_year <= p.get('birth_year', 0) <= end_year]
        
        range_file = os.path.join(OUTPUT_DIR, f"baseball_dataset_{start_year}_{end_year}.json")
        range_meta = {
            "source": "Baseball Almanac",
            "collection_date": time.strftime("%Y-%m-%d"),
            "years_covered": f"{start_year}-{end_year}",
            "total_players": len(range_players),
            "unique_first_names": len(name_lists['first_names']),
            "unique_last_names": len(name_lists['last_names']),
            "unique_nicknames": len(name_lists['nicknames'])
        }
        
        range_data = {
            "meta": range_meta,
            "name_lists": name_lists,
            "players": range_players
        }
        
        with open(range_file, "w") as f:
            json.dump(range_data, f, indent=2)
        print(f"Saved partial dataset for years {start_year}-{end_year} to {range_file}")
    else:
        print(f"\nPartial collection completed for range {start_year}-{end_year}.")
        print(f"Run this script again to continue from where you left off.")

def generate_final_dataset(players):
    """Generate and save the final complete dataset with stats."""
    # Generate name lists
    name_lists = generate_name_lists(players)
    
    # Save as JSON with name lists
    final_file = os.path.join(OUTPUT_DIR, FINAL_OUTPUT_FILE)
    
    # Meta information
    meta = {
        "source": "Baseball Almanac",
        "collection_date": time.strftime("%Y-%m-%d"),
        "years_covered": f"{DEFAULT_START_YEAR}-{DEFAULT_END_YEAR}",
        "total_players": len(players),
        "unique_first_names": len(name_lists['first_names']),
        "unique_last_names": len(name_lists['last_names']),
        "unique_nicknames": len(name_lists['nicknames'])
    }
    
    final_data = {
        "meta": meta,
        "name_lists": name_lists,
        "players": players
    }
    
    with open(final_file, "w") as f:
        json.dump(final_data, f, indent=2)
    print(f"Saved complete final dataset to {final_file}")
    
    # Print statistics
    print("\nFinal Dataset Statistics:")
    for key, value in meta.items():
        print(f"{key}: {value}")

def main():
    """Process command line arguments and run the data collection."""
    parser = argparse.ArgumentParser(description="Collect baseball player data from specified years")
    parser.add_argument("--start", type=int, default=DEFAULT_START_YEAR, 
                        help=f"Starting year (default: {DEFAULT_START_YEAR})")
    parser.add_argument("--end", type=int, default=DEFAULT_END_YEAR, 
                        help=f"Ending year (default: {DEFAULT_END_YEAR})")
    parser.add_argument("--batch", type=int, default=None,
                        help="Process in batches of N years (optional)")
    parser.add_argument("--delay", type=int, default=DELAY_BETWEEN_YEARS,
                        help=f"Delay between years in seconds (default: {DELAY_BETWEEN_YEARS})")
    
    args = parser.parse_args()
    
    # Validate years
    if args.start < 1845 or args.end > 1920:
        print("Error: Years must be between 1845 and 1920")
        sys.exit(1)
    
    if args.start > args.end:
        print("Error: Start year cannot be greater than end year")
        sys.exit(1)
    
    # Process in batches if specified
    if args.batch:
        current_start = args.start
        while current_start <= args.end:
            current_end = min(current_start + args.batch - 1, args.end)
            print(f"\nProcessing batch: {current_start} to {current_end}")
            process_full_dataset(current_start, current_end, args.delay)
            current_start = current_end + 1
    else:
        # Process the specified range
        process_full_dataset(args.start, args.end, args.delay)

if __name__ == "__main__":
    main() 