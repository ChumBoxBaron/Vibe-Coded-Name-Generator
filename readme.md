# Baseball Player Data Collection

This project collects baseball player data from [Baseball Almanac](https://www.baseball-almanac.com/) for the years 1845-1920. The collected data includes player names, nicknames, birth/death dates, and career information.

## Scripts Overview

The project includes several scripts for data collection:

- `simplified_scraper.py`: Core scraping functions
- `simplified_small_test.py`: Collects a small sample (10 players per year) for testing
- `collect_full_dataset.py`: Main script for collecting the full dataset with flexible options

## Data Collection Process

The `collect_full_dataset.py` script offers several options for collecting data:

```
python collect_full_dataset.py [--start YEAR] [--end YEAR] [--delay SECONDS] [--batch N]
```

### Command Line Options

- `--start` - Starting year (default: 1845)
- `--end` - Ending year (default: 1920)
- `--delay` - Delay between processing years in seconds (default: 10)
- `--batch` - Process years in batches of N years (optional)

### Examples

**Collect a small range for testing:**
```
python collect_full_dataset.py --start 1845 --end 1847 --delay 5
```

**Collect data in batches of 10 years:**
```
python collect_full_dataset.py --batch 10 --delay 8
```

**Collect a specific decade:**
```
python collect_full_dataset.py --start 1890 --end 1899
```

## Features

- **Progress Tracking**: The script automatically saves progress after each year, allowing you to resume collection if interrupted.
- **Individual Files**: Each year's data is saved separately in addition to the combined dataset.
- **Statistics**: The script provides statistics on unique names, nicknames, and total players collected.
- **Time Estimation**: During collection, estimated completion times are displayed.

## Output Files

- `baseball_data/full_players_YYYY.json` - Individual year data files
- `baseball_data/full_all_players_current.json` - Combined dataset (updated during collection)
- `baseball_data/baseball_dataset_START_END.json` - Range-specific datasets
- `baseball_data/baseball_dataset_complete.json` - Final complete dataset (when all years are processed)

## Data Structure

Each player record contains:
- Full name
- First name
- Last name
- Nickname (if available)
- Birth and death dates
- Career span (debut and final years)
- Birth year
- Additional details from player pages

## Notes

- The collection process includes appropriate delays to avoid overwhelming the server.
- For testing purposes, use shorter ranges and smaller datasets before starting the full collection.
- The full dataset collection (1845-1920) may take several hours to complete.

## Name Generator

Once data is collected, you can use the baseball player names to generate funny or historically-inspired baseball names using the `baseball_name_generator.py` script.
