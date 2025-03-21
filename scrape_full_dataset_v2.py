import requests
from bs4 import BeautifulSoup
import json
import time
import os
import re
import csv
import random
import datetime
import sys
import traceback
import shutil
from simplified_scraper import (
    scrape_player_detail, 
    parse_birth_name, 
    process_player_data, 
    simple_name_split,
    generate_name_lists
)

# ========== CONFIGURATION ==========
# Years to scrape
START_YEAR = 1845
END_YEAR = 1920

# Delays and rate limiting
MIN_DELAY_BETWEEN_PLAYERS = 3  # Minimum seconds between player requests
MAX_DELAY_BETWEEN_PLAYERS = 8  # Maximum seconds between player requests
MIN_DELAY_BETWEEN_YEARS = 30   # Minimum seconds between years
MAX_DELAY_BETWEEN_YEARS = 60   # Maximum seconds between years
MAX_RETRIES_PER_REQUEST = 5    # Maximum retries for a single request
MAX_ERRORS_PER_YEAR = 10       # Maximum errors before skipping a year
MAX_CONSECUTIVE_ERRORS = 20    # Maximum consecutive errors before cooling down

# File organization
VERSION = "v2"  # Version identifier for files
OUTPUT_DIR = "baseball_data"
FINAL_DIR = os.path.join(OUTPUT_DIR, "final")
ARCHIVE_DIR = os.path.join(OUTPUT_DIR, "archive")
TESTS_DIR = os.path.join(OUTPUT_DIR, "tests")
YEARLY_DIR = os.path.join(OUTPUT_DIR, "yearly")

# Progress and output files
PROGRESS_FILE = os.path.join(OUTPUT_DIR, f"baseball_progress_{VERSION}.json")
FINAL_DATASET_FILE = os.path.join(FINAL_DIR, f"baseball_dataset_{VERSION}_complete.json")
COMBINED_FILE = os.path.join(OUTPUT_DIR, f"all_players_{VERSION}_current.json")
LOG_FILE = os.path.join(OUTPUT_DIR, f"scraper_log_{VERSION}.txt")

# ========== UTILITY FUNCTIONS ==========
def ensure_directories():
    """Ensure all required directories exist."""
    for directory in [OUTPUT_DIR, FINAL_DIR, ARCHIVE_DIR, TESTS_DIR, YEARLY_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

def load_progress():
    """Load the progress from the progress file with enhanced error handling."""
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Error reading progress file. Creating backup and starting fresh.")
            # Create a backup of the corrupted file
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"{PROGRESS_FILE}.{timestamp}.bak"
            shutil.copy2(PROGRESS_FILE, backup_file)
            print(f"Created backup of corrupted progress file: {backup_file}")
    
    # Initialize new progress if file doesn't exist or is corrupted
    return {
        "completed_years": [],
        "partially_completed_years": {},
        "all_players": [],
        "last_run": "",
        "total_players": 0,
        "version": VERSION
    }

def save_progress(progress, force_save=False):
    """
    Save the progress to the progress file with backup protection.
    
    Args:
        progress (dict): Progress data
        force_save (bool): Whether to force save even if not at a save point
    """
    # Update timestamp
    progress["last_run"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    progress["total_players"] = len(progress["all_players"])
    
    # Create a temporary file first to avoid corrupting the main file
    temp_file = f"{PROGRESS_FILE}.tmp"
    try:
        with open(temp_file, "w") as f:
            json.dump(progress, f, indent=2)
        
        # If the temp file was written successfully, rename it to the main file
        if os.path.exists(PROGRESS_FILE):
            # Create a backup first
            if force_save:  # Only create backups when explicitly forcing a save
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = f"{PROGRESS_FILE}.{timestamp}.bak"
                shutil.copy2(PROGRESS_FILE, backup_file)
        
        # Replace the main file
        os.replace(temp_file, PROGRESS_FILE)
        
        # Only log when forcing a save to avoid excessive output
        if force_save:
            print(f"Progress saved to {PROGRESS_FILE}")
    
    except Exception as e:
        print(f"Error saving progress: {e}")
        if os.path.exists(temp_file):
            os.remove(temp_file)

def log_message(message, print_to_console=True):
    """Log a message to the log file and optionally to the console."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    
    with open(LOG_FILE, "a") as f:
        f.write(log_entry + "\n")
    
    if print_to_console:
        print(message)

def archive_old_files():
    """Archive old test and version files to keep the main directory clean."""
    # Files to archive (based on patterns)
    patterns_to_archive = [
        "test_*.json",
        "*_v1*.json",
        "baseball_players_*.json"  # Old yearly files
    ]
    
    log_message("Archiving old files...", print_to_console=True)
    
    # Process each pattern
    for pattern in patterns_to_archive:
        import glob
        files = glob.glob(os.path.join(OUTPUT_DIR, pattern))
        
        for file in files:
            # Skip files in subdirectories
            if os.path.dirname(file) != OUTPUT_DIR:
                continue
            
            # Determine target directory
            if "test_" in os.path.basename(file):
                target_dir = TESTS_DIR
            else:
                target_dir = ARCHIVE_DIR
                
            # Create target file path
            target_file = os.path.join(target_dir, os.path.basename(file))
            
            # Move file if it doesn't already exist in target
            if not os.path.exists(target_file):
                try:
                    shutil.move(file, target_file)
                    log_message(f"Archived: {file} -> {target_file}", print_to_console=False)
                except Exception as e:
                    log_message(f"Error archiving {file}: {e}", print_to_console=False)

def random_delay(min_seconds, max_seconds):
    """Sleep for a random amount of time within the specified range."""
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)
    return delay

# ========== SCRAPING FUNCTIONS ==========
def scrape_year(year, progress):
    """
    Scrape baseball player names for a specific birth year with enhanced error handling.
    
    Args:
        year (int): The birth year to scrape
        progress (dict): Progress tracking dictionary
        
    Returns:
        list: A list of dictionaries containing player name data
    """
    url = f"https://www.baseball-almanac.com/players/baseball_births.php?y={year}"
    log_message(f"Downloading baseball player data from {url}...")
    
    # Add headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    # Track consecutive errors for cooling down
    consecutive_errors = 0
    
    try:
        # Try to fetch the year page with retries
        response = None
        for attempt in range(MAX_RETRIES_PER_REQUEST):
            try:
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                break
            except Exception as e:
                if attempt < MAX_RETRIES_PER_REQUEST - 1:
                    retry_delay = (2 ** attempt) * 5  # Exponential backoff
                    log_message(f"  Error on attempt {attempt+1} for year {year}, retrying in {retry_delay} seconds: {e}")
                    time.sleep(retry_delay)
                else:
                    log_message(f"  Failed to fetch year {year} after {MAX_RETRIES_PER_REQUEST} attempts: {e}")
                    return []
        
        if not response:
            return []
        
        # Save the HTML for reference (optional)
        html_file = os.path.join(YEARLY_DIR, f"baseball_page_{year}.html")
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(response.text)
        
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
        
        log_message(f"Found {len(player_links)} potential player links for year {year}")
        
        if len(player_links) == 0:
            log_message(f"No players found for year {year}")
            return []
        
        # Check if we've partially processed this year
        processed_players = set()
        if year in progress.get('partially_completed_years', {}):
            processed_players = set(progress['partially_completed_years'][year])
            log_message(f"Already processed {len(processed_players)} players for year {year}")
        
        # Process each player link
        for i, link in enumerate(player_links):
            try:
                full_name = link.text.strip()
                href = link.get('href')
                
                if not full_name or full_name.lower() == 'player':
                    continue
                
                player_url = 'https://www.baseball-almanac.com' + href if href.startswith('/') else href
                player_id = player_url.split('=')[-1] if '=' in player_url else ''
                
                # Skip if we've already processed this player for this year
                if player_id in processed_players:
                    log_message(f"  Skipping already processed player {i+1}/{len(player_links)}: {full_name} ({player_id})")
                    continue
                    
                log_message(f"Processing player {i+1}/{len(player_links)} for year {year}: {full_name} ({player_id})")
                
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
                
                player_data = {
                    "full_name": full_name,
                    "birth_date": birth_date,
                    "death_date": death_date,
                    "debut_year": debut_year,
                    "final_year": final_year,
                    "source": "Baseball Almanac",
                    "birth_year": year,
                    "player_url": player_url,
                    "player_id": player_id
                }
                
                # Parse the name
                name_parts = simple_name_split(full_name)
                player_data.update(name_parts)
                
                # Try to get details from player page
                if player_url:
                    try:
                        log_message(f"  Scraping details from {player_url}")
                        detail_data = scrape_player_detail(player_url)
                        player_data.update(detail_data)
                        
                        # Process the player data to reconcile names and nicknames
                        player_data = process_player_data(player_data)
                        
                        # Reset consecutive errors counter upon success
                        consecutive_errors = 0
                        
                        # Add the player to the processed list
                        if year not in progress.get('partially_completed_years', {}):
                            progress['partially_completed_years'][year] = []
                        
                        progress['partially_completed_years'][year].append(player_id)
                        
                        # Add random delay to avoid overwhelming the server
                        delay = random_delay(MIN_DELAY_BETWEEN_PLAYERS, MAX_DELAY_BETWEEN_PLAYERS)
                        log_message(f"  Added delay of {delay:.2f} seconds")
                        
                        # Save progress periodically to enable resuming
                        if (i + 1) % 10 == 0:
                            save_progress(progress)
                    
                    except Exception as e:
                        error_count += 1
                        consecutive_errors += 1
                        log_message(f"  Error scraping details: {e}")
                        traceback.print_exc()
                        
                        if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                            log_message(f"Too many consecutive errors ({consecutive_errors}). Cooling down for 5 minutes.")
                            time.sleep(300)  # 5-minute cooldown
                            consecutive_errors = 0  # Reset after cooldown
                        
                        if error_count >= MAX_ERRORS_PER_YEAR:
                            log_message(f"Too many errors ({error_count}). Skipping remaining players for year {year}")
                            break
                
                players.append(player_data)
                
            except Exception as e:
                error_count += 1
                consecutive_errors += 1
                log_message(f"Error processing player link: {e}")
                
                if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                    log_message(f"Too many consecutive errors ({consecutive_errors}). Cooling down for 5 minutes.")
                    time.sleep(300)  # 5-minute cooldown
                    consecutive_errors = 0  # Reset after cooldown
                
                if error_count >= MAX_ERRORS_PER_YEAR:
                    log_message(f"Too many errors ({error_count}). Skipping remaining players for year {year}")
                    break
        
        log_message(f"Successfully processed {len(players)} players for year {year}")
        
        # Save individual year data
        if players:
            year_file = os.path.join(YEARLY_DIR, f"players_{VERSION}_{year}.json")
            with open(year_file, "w") as f:
                json.dump(players, f, indent=2)
            log_message(f"Saved {len(players)} players from {year} to {year_file}")
        
        return players
        
    except Exception as e:
        log_message(f"Error processing year {year}: {e}")
        traceback.print_exc()
        return []

def process_years(start_year, end_year, progress):
    """
    Process a range of years with enhanced error handling and recovery.
    
    Args:
        start_year (int): First year to process
        end_year (int): Last year to process
        progress (dict): Progress tracking dictionary
    """
    # Generate list of years to process
    all_years = list(range(start_year, end_year + 1))
    
    # Filter out completely processed years
    remaining_years = [year for year in all_years if year not in progress['completed_years']]
    
    log_message(f"\nStarting baseball data collection for years {start_year}-{end_year}")
    log_message(f"Years to process: {len(remaining_years)} out of {len(all_years)}")
    log_message(f"Already completed: {len(progress['completed_years'])} years")
    log_message(f"Total players collected so far: {len(progress['all_players'])}")
    
    start_time = datetime.datetime.now()
    log_message(f"Collection started at: {start_time}")
    
    # Process each year
    for i, year in enumerate(remaining_years):
        year_start_time = datetime.datetime.now()
        log_message(f"\n{'='*60}")
        log_message(f"Processing year {year}... ({i+1}/{len(remaining_years)})")
        log_message(f"{'='*60}\n")
        
        # Scrape the year's data
        players = scrape_year(year, progress)
        
        if players:
            # Add to overall collection
            progress['all_players'].extend(players)
            progress['completed_years'].append(year)
            
            # Remove from partially completed years if it was there
            if year in progress.get('partially_completed_years', {}):
                del progress['partially_completed_years'][year]
            
            # Force save progress after each year
            save_progress(progress, force_save=True)
            
            # Save combined file
            with open(COMBINED_FILE, "w") as f:
                json.dump(progress['all_players'], f, indent=2)
            log_message(f"Updated combined file with total of {len(progress['all_players'])} players")
        
            # Display time statistics
            year_end_time = datetime.datetime.now()
            year_duration = year_end_time - year_start_time
            elapsed_total = year_end_time - start_time
            remaining_count = len(remaining_years) - (i + 1)
            
            log_message(f"\nTime statistics:")
            log_message(f"  Time for year {year}: {year_duration}")
            log_message(f"  Total elapsed time: {elapsed_total}")
            
            if remaining_count > 0 and i > 0:
                avg_time_per_year = elapsed_total / (i + 1)
                est_remaining_time = avg_time_per_year * remaining_count
                est_completion_time = year_end_time + est_remaining_time
                
                log_message(f"  Estimated time remaining: {est_remaining_time}")
                log_message(f"  Estimated completion at: {est_completion_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if i < len(remaining_years) - 1:
            delay = random_delay(MIN_DELAY_BETWEEN_YEARS, MAX_DELAY_BETWEEN_YEARS)
            log_message(f"Waiting {delay:.2f} seconds before processing next year...")

def save_final_dataset(progress):
    """Generate and save the final dataset with all collected players."""
    log_message("\nGenerating final dataset...")
    
    # Generate name lists
    name_lists = generate_name_lists(progress['all_players'])
    
    # Save individual name lists
    for name_type, name_list in name_lists.items():
        name_file = os.path.join(FINAL_DIR, f"baseball_{name_type}_{VERSION}.json")
        with open(name_file, "w") as f:
            json.dump(name_list, f, indent=2)
        log_message(f"Saved {name_type} list to {name_file}")
        
        # Also save as CSV
        csv_file = os.path.join(FINAL_DIR, f"baseball_{name_type}_{VERSION}.csv")
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            if name_list:
                writer = csv.DictWriter(f, fieldnames=name_list[0].keys())
                writer.writeheader()
                writer.writerows(name_list)
        log_message(f"Saved {name_type} CSV to {csv_file}")
    
    # Meta information
    completed_years = sorted(progress['completed_years'])
    meta = {
        "source": "Baseball Almanac",
        "collection_date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "scraper_version": VERSION,
        "years_covered": f"{min(completed_years)}-{max(completed_years)}" if completed_years else "",
        "total_players": len(progress['all_players']),
        "unique_first_names": len(name_lists['first_names']),
        "unique_last_names": len(name_lists['last_names']),
        "unique_nicknames": len(name_lists['nicknames']),
        "years_included": completed_years
    }
    
    # Create final dataset
    final_data = {
        "meta": meta,
        "name_lists": name_lists,
        "players": progress['all_players']
    }
    
    # Save final dataset
    with open(FINAL_DATASET_FILE, "w") as f:
        json.dump(final_data, f, indent=2)
    log_message(f"Saved complete dataset to {FINAL_DATASET_FILE}")
    
    # Also save a players-only version for easier processing
    players_file = os.path.join(FINAL_DIR, f"baseball_players_{VERSION}.json")
    with open(players_file, "w") as f:
        json.dump(progress['all_players'], f, indent=2)
    log_message(f"Saved players-only dataset to {players_file}")
    
    # Print statistics
    log_message("\nFinal Dataset Statistics:")
    for key, value in meta.items():
        log_message(f"  {key}: {value}")

def main():
    """Main function to run the full data collection process."""
    print("\n" + "="*80)
    print(f"BASEBALL ALMANAC DATA COLLECTION (VERSION {VERSION})")
    print("="*80 + "\n")
    
    # Set up the environment
    ensure_directories()
    log_message(f"Starting Baseball Almanac data collection script (Version {VERSION})")
    
    # Archive old files to clean up the directory
    archive_old_files()
    
    # Load progress
    progress = load_progress()
    
    # Process all years from START_YEAR to END_YEAR
    try:
        process_years(START_YEAR, END_YEAR, progress)
        log_message("\nAll years processed successfully!")
    except KeyboardInterrupt:
        log_message("\nProcess interrupted by user. Progress saved.")
    except Exception as e:
        log_message(f"\nError in main process: {e}")
        traceback.print_exc()
        log_message("Process stopped due to error. Progress saved.")
    
    # Generate final dataset if all years are complete
    all_years = list(range(START_YEAR, END_YEAR + 1))
    missing_years = [year for year in all_years if year not in progress['completed_years']]
    
    if not missing_years:
        log_message("\nAll years complete! Generating final dataset...")
        save_final_dataset(progress)
    else:
        log_message(f"\nSome years are still incomplete. Missing years: {missing_years}")
        log_message(f"Run this script again to continue from where you left off.")
    
    log_message("\nData collection process finished.")

if __name__ == "__main__":
    main() 