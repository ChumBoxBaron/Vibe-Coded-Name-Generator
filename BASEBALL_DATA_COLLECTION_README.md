# Baseball Data Collection

This part of the project focuses on scraping, processing, and organizing historical baseball player data from Baseball Almanac.

## Data Sources

The data is sourced from the Baseball Almanac website, specifically players born in years 1845-1920:
- Example URL: [Baseball Almanac - Born in 1845](https://www.baseball-almanac.com/players/birthplace.php?y=1845)

## Directory Structure

The baseball data is organized in the following structure:

- `baseball_data/` - Base directory for all baseball data
  - `archive/` - Stores archived versions of previous data pulls
  - `tests/` - Contains test output files and progress logs
  - `final/` - Contains final processed data files
  - Raw HTML files are stored in the base directory but excluded from git

## Scripts

The project includes several scripts for scraping and processing baseball player data:

- **Main Scrapers**:
  - `scrape_full_dataset_v2.py` - Full dataset scraper for years 1845-1920
  - `simplified_scraper.py` - Core functions used by other scraper scripts
  
- **Test Scripts**:
  - `test_single_year.py` - Test script for scraping a single year
  - `test_bio_scraper.py` - Test script for bio extraction functionality
  - `test_improved_scraper.py` - Test script for improved scraper features

## Features

The baseball data collection scripts include the following features:

1. **Robust Web Scraping**:
   - Handles network errors with retries
   - Respects rate limits to avoid overloading the server
   - Saves progress to allow resuming interrupted scrapes

2. **Data Extraction**:
   - Player names (first, middle, last)
   - Birth names and nicknames
   - Birth and death dates
   - Career span (debut and final years)
   - Player URLs for detailed information

3. **Data Processing**:
   - Reconciles nicknames with birth names
   - Structures data in consistent JSON format
   - Creates separate collections for first names, last names, and nicknames

## Usage

To scrape the full dataset:

```
python scrape_full_dataset_v2.py
```

To test scraping a single year:

```
python test_single_year.py
```

To test bio extraction:

```
python test_bio_scraper.py
```

## Data Structure

Each player record includes:

- `player_name`: Full name as displayed
- `birth_name`: Full birth name (when available)
- `birth_first_name`: First name from birth name
- `birth_middle_name`: Middle name(s) from birth name
- `birth_last_name`: Last name from birth name
- `nickname`: Player's nickname(s)
- `player_url`: URL to player's detail page
- `birth_year`: Year of birth
- `birth_date`: Full birth date (when available)
- `death_date`: Full death date (when available)
- `debut_year`: First year in professional baseball
- `final_year`: Last year in professional baseball

## Key Improvements in v2

- **Enhanced Birth Name Handling**: Properly captures and processes birth names from player detail pages
- **Improved Nickname Processing**: Splits multiple nicknames (e.g., "Babe or The Bambino") into separate entries
- **Advanced Error Handling**: Automatically retries on errors and includes cooling-down periods
- **Better File Organization**: Standardized naming conventions and directory structure
- **Detailed Logging**: All actions are recorded in a log file for troubleshooting

## Output Files

### Main Dataset Files (in `final/` directory)

- `baseball_dataset_v2_complete.json` - Complete dataset with metadata and name lists
- `baseball_players_v2.json` - Players-only dataset for easier processing
- `baseball_first_names_v2.json` - List of first names with frequencies
- `baseball_last_names_v2.json` - List of last names with frequencies
- `baseball_nicknames_v2.json` - List of nicknames with frequencies
- CSV versions of all name lists

### Progress and Status Files

- `baseball_progress_v2.json` - Progress tracking file
- `all_players_v2_current.json` - Current combined dataset (updated during processing)
- `scraper_log_v2.txt` - Detailed log of all scraper actions

## Player Data Structure

Each player record contains:

```json
{
  "full_name": "Display name from index page",
  "first_name": "First name (from birth name when available)",
  "last_name": "Last name (from birth name when available)",
  "nickname": "Nickname(s) as a single string with 'or' separators",
  "nicknames": ["Array", "of", "individual", "nicknames"],
  "birth_name": "Full birth name from player page",
  "birth_first_name": "First name from birth name",
  "birth_middle_name": "Middle name(s) from birth name",
  "birth_last_name": "Last name from birth name",
  "birth_date": "Birth date",
  "death_date": "Death date",
  "debut_year": "First year in MLB",
  "final_year": "Last year in MLB",
  "player_url": "URL to player's detail page",
  "player_id": "Player ID from URL",
  "birth_year": 1920,
  "source": "Baseball Almanac"
}
```

## Handling Interruptions

If the script is interrupted (intentionally or due to errors):

1. All progress up to the last completed year is saved
2. Partially completed years are tracked by player ID
3. When restarted, the script will:
   - Skip already completed years
   - Resume partially completed years from where it left off
   - Process remaining years in order

## Using the Dataset

The final dataset in `baseball_data/final/baseball_dataset_v2_complete.json` includes:

- **Meta Information**: Collection date, version, total players, etc.
- **Name Lists**: Categorized lists of first names, last names, and nicknames with frequencies
- **Player Records**: Complete player data with birth names and properly processed nicknames

## For Name Generator Use

When using this data with a name generator:
- The `birth_first_name` field contains the player's actual first name
- The `nicknames` array contains individual nicknames for random selection
- The `first_names_v2.json` and `last_names_v2.json` files provide frequency-weighted name options 