import requests
import pandas as pd
import json
import re
import os
import time
from datetime import datetime

# Define directory structure
BASE_DIR = "census_data"
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
ARCHIVE_DIR = os.path.join(BASE_DIR, "archive")
TEST_DIR = os.path.join(BASE_DIR, "tests")
FINAL_DIR = os.path.join(BASE_DIR, "final")

# Ensure directories exist
for directory in [BASE_DIR, OUTPUT_DIR, ARCHIVE_DIR, TEST_DIR, FINAL_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")

def download_census_data(url, output_file=None, max_retries=3, delay_between_retries=5):
    """
    Download data from the census URL with retry capability.
    
    Args:
        url (str): URL to download data from
        output_file (str, optional): File to save raw downloaded data
        max_retries (int): Maximum number of retry attempts
        delay_between_retries (int): Seconds to wait between retries
        
    Returns:
        str: Downloaded text content
    """
    print(f"Downloading data from {url}...")
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            
            # Save raw data if output file specified
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"Raw data saved to {output_file}")
                
            return response.text
            
        except requests.exceptions.RequestException as e:
            print(f"Error downloading data (attempt {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {delay_between_retries} seconds...")
                time.sleep(delay_between_retries)
            else:
                raise Exception(f"Failed to download data after {max_retries} attempts")

def parse_fixed_width_data(text, data_type="surname"):
    """
    Parse fixed-width formatted census data.
    
    Args:
        text (str): Text content to parse
        data_type (str): Type of data being parsed (surname, firstname, etc.)
        
    Returns:
        list: List of dictionaries containing parsed data
    """
    lines = text.split('\n')
    data = []
    
    # Skip any header lines - assuming data starts with a name
    data_lines = [line for line in lines if line.strip() and re.match(r'^\s*[A-Z]', line)]
    
    print(f"Found {len(data_lines)} data lines to parse")
    
    # Parse based on data type
    if data_type.lower() == "surname":
        for i, line in enumerate(data_lines):
            try:
                # Parse fixed-width format - adjust positions as needed based on actual data
                parts = line.strip().split()
                if len(parts) >= 4:  # Ensure we have all needed parts
                    surname = parts[0]
                    frequency = float(parts[1])
                    cumulative_freq = float(parts[2])
                    rank = int(parts[3])
                    
                    data.append({
                        "surname": surname,
                        "frequency": frequency,
                        "cumulative_frequency": cumulative_freq,
                        "rank": rank,
                        "source": "US Census 1990"
                    })
                    
                    # Print progress for every 10000 lines
                    if (i + 1) % 10000 == 0 or i == 0:
                        print(f"Processed {i+1}/{len(data_lines)} entries...")
                        
            except Exception as e:
                print(f"Error parsing line: {line}")
                print(f"Error details: {e}")
    
    # Add other data types as needed (firstname, etc.)
    # elif data_type.lower() == "firstname":
    #     # Parse first name data
    #     pass
    
    print(f"Successfully parsed {len(data)} records")
    return data

def save_as_json(data, output_file, indent=2):
    """Save data as JSON file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent)
    print(f"JSON data saved to {output_file}")

def save_as_csv(data, output_file):
    """Save data as CSV file."""
    df = pd.DataFrame(data)
    df.to_csv(output_file, index=False)
    print(f"CSV data saved to {output_file}")

def archive_old_files(file_pattern, archive_dir):
    """
    Archive old files matching the pattern by moving them to the archive directory.
    
    Args:
        file_pattern (str): Pattern of files to archive (e.g., "census_surnames_*.json")
        archive_dir (str): Directory to move files to
    """
    import glob
    import shutil
    
    files = glob.glob(file_pattern)
    if files:
        # Create timestamped subdirectory in archive
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_subdir = os.path.join(archive_dir, f"archive_{timestamp}")
        os.makedirs(archive_subdir, exist_ok=True)
        
        for file in files:
            if os.path.exists(file):
                shutil.move(file, os.path.join(archive_subdir, os.path.basename(file)))
                print(f"Archived {file} to {archive_subdir}")

def process_census_surnames(url=None, test_mode=False):
    """
    Process US Census surname data.
    
    Args:
        url (str, optional): URL to download data from
        test_mode (bool): Whether to run in test mode with limited data
        
    Returns:
        list: Processed data
    """
    # Default URL for US Census 1990 surnames
    if url is None:
        url = "https://www2.census.gov/topics/genealogy/1990surnames/dist.all.last"
    
    # Determine output directories based on mode
    output_dir = TEST_DIR if test_mode else FINAL_DIR
    
    # File paths
    raw_data_file = os.path.join(BASE_DIR, "raw_surname_data.txt")
    json_output = os.path.join(output_dir, f"census_surnames{'_test' if test_mode else ''}.json")
    csv_output = os.path.join(output_dir, f"census_surnames{'_test' if test_mode else ''}.csv")
    
    # Archive old files if in production mode
    if not test_mode:
        archive_old_files(os.path.join(FINAL_DIR, "census_surnames*.json"), ARCHIVE_DIR)
        archive_old_files(os.path.join(FINAL_DIR, "census_surnames*.csv"), ARCHIVE_DIR)
    
    try:
        # Download the data
        text_data = download_census_data(url, raw_data_file)
        
        # Print a sample to check the format
        print("\nSample of downloaded data (first 200 characters):")
        print(text_data[:200])
        
        # Parse the data
        parsed_data = parse_fixed_width_data(text_data, "surname")
        
        # Limit data if in test mode
        if test_mode:
            parsed_data = parsed_data[:100]  # Just take first 100 records for testing
        
        # Print a sample of parsed data
        print("\nSample of parsed data (first 3 records):")
        for i, record in enumerate(parsed_data[:3]):
            print(f"Record {i+1}: {record}")
        
        # Save as JSON and CSV
        save_as_json(parsed_data, json_output)
        save_as_csv(parsed_data, csv_output)
        
        # Return the parsed data
        return parsed_data
        
    except Exception as e:
        print(f"Error processing census surnames: {e}")
        return None

def process_census_firstnames(gender="all", url=None, test_mode=False):
    """
    Process US Census first name data.
    
    Args:
        gender (str): 'male', 'female', or 'all'
        url (str, optional): URL to download data from
        test_mode (bool): Whether to run in test mode with limited data
        
    Returns:
        list: Processed data
    """
    # URLs for US Census first names
    urls = {
        "male": "https://www2.census.gov/topics/genealogy/1990surnames/dist.male.first",
        "female": "https://www2.census.gov/topics/genealogy/1990surnames/dist.female.first",
    }
    
    # Determine output directories based on mode
    output_dir = TEST_DIR if test_mode else FINAL_DIR
    
    if gender.lower() == "all":
        # Process both male and female names
        male_data = process_census_firstnames("male", urls["male"], test_mode)
        female_data = process_census_firstnames("female", urls["female"], test_mode)
        
        # Combine the data
        combined_data = male_data + female_data
        
        # Save the combined data
        json_output = os.path.join(output_dir, f"census_firstnames_combined{'_test' if test_mode else ''}.json")
        csv_output = os.path.join(output_dir, f"census_firstnames_combined{'_test' if test_mode else ''}.csv")
        
        save_as_json(combined_data, json_output)
        save_as_csv(combined_data, csv_output)
        
        print(f"Combined data saved with {len(combined_data)} names")
        return combined_data
    
    # If url not provided, use default from dictionary
    if url is None and gender.lower() in urls:
        url = urls[gender.lower()]
    
    # File paths
    raw_data_file = os.path.join(BASE_DIR, f"raw_firstname_{gender.lower()}_data.txt")
    json_output = os.path.join(output_dir, f"census_firstnames_{gender.lower()}{'_test' if test_mode else ''}.json")
    csv_output = os.path.join(output_dir, f"census_firstnames_{gender.lower()}{'_test' if test_mode else ''}.csv")
    
    # Archive old files if in production mode
    if not test_mode:
        archive_old_files(os.path.join(FINAL_DIR, f"census_firstnames_{gender.lower()}*.json"), ARCHIVE_DIR)
        archive_old_files(os.path.join(FINAL_DIR, f"census_firstnames_{gender.lower()}*.csv"), ARCHIVE_DIR)
    
    try:
        # Download the data
        text_data = download_census_data(url, raw_data_file)
        
        # Print a sample to check the format
        print(f"\nSample of downloaded {gender} first name data (first 200 characters):")
        print(text_data[:200])
        
        # Parse the data
        parsed_data = parse_firstname_data(text_data, gender)
        
        # Limit data if in test mode
        if test_mode:
            parsed_data = parsed_data[:100]  # Just take first 100 records for testing
        
        # Print a sample of parsed data
        print(f"\nSample of parsed {gender} first name data (first 3 records):")
        for i, record in enumerate(parsed_data[:3]):
            print(f"Record {i+1}: {record}")
        
        # Save as JSON and CSV
        save_as_json(parsed_data, json_output)
        save_as_csv(parsed_data, csv_output)
        
        # Return the parsed data
        return parsed_data
        
    except Exception as e:
        print(f"Error processing census {gender} first names: {e}")
        return []

def parse_firstname_data(text, gender="unknown"):
    """
    Parse census first name data.
    
    Args:
        text (str): Text content to parse
        gender (str): "male" or "female"
        
    Returns:
        list: List of dictionaries containing parsed data
    """
    lines = text.split('\n')
    data = []
    
    # Skip any header lines - assuming data starts with a name
    data_lines = [line for line in lines if line.strip() and not line.startswith("#")]
    
    print(f"Found {len(data_lines)} data lines to parse")
    
    for i, line in enumerate(data_lines):
        try:
            # Split by whitespace
            parts = line.strip().split()
            
            if len(parts) >= 4:  # We need at least 4 parts for name, frequency, cumulative, rank
                firstname = parts[0]
                frequency = float(parts[1])
                cumulative_freq = float(parts[2])
                rank = int(parts[3])
                
                data.append({
                    "firstname": firstname,
                    "gender": gender,
                    "frequency": frequency,
                    "cumulative_frequency": cumulative_freq,
                    "rank": rank,
                    "source": "US Census 1990"
                })
                
                # Print progress for every 1000 lines
                if (i + 1) % 1000 == 0 or i == 0:
                    print(f"Processed {i+1}/{len(data_lines)} entries...")
                    
        except Exception as e:
            print(f"Error parsing line: {line}")
            print(f"Error details: {e}")
    
    print(f"Successfully parsed {len(data)} records")
    return data

def main():
    print("Census Data Processor")
    print("=" * 40)
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Process US Census data files')
    parser.add_argument('--test', action='store_true', help='Run in test mode with limited data')
    parser.add_argument('--surnames', action='store_true', help='Process surname data')
    parser.add_argument('--firstnames', action='store_true', help='Process first name data')
    parser.add_argument('--male-names', action='store_true', help='Process male first name data')
    parser.add_argument('--female-names', action='store_true', help='Process female first name data')
    parser.add_argument('--all', action='store_true', help='Process all data types')
    parser.add_argument('--firstname-url', type=str, help='URL for first name data')
    parser.add_argument('--male-url', type=str, help='URL for male first name data')
    parser.add_argument('--female-url', type=str, help='URL for female first name data')
    parser.add_argument('--surname-url', type=str, help='URL for surname data')
    args = parser.parse_args()
    
    # Default to processing surnames if no specific args given
    if not (args.surnames or args.firstnames or args.male_names or args.female_names or args.all):
        args.surnames = True
    
    # Process data types based on arguments
    if args.surnames or args.all:
        print("\nProcessing surname data...")
        process_census_surnames(url=args.surname_url, test_mode=args.test)
    
    if args.firstnames or args.all:
        print("\nProcessing first name data (combined male and female)...")
        process_census_firstnames(gender="all", test_mode=args.test)
    
    if args.male_names:
        print("\nProcessing male first name data...")
        process_census_firstnames(gender="male", url=args.male_url, test_mode=args.test)
    
    if args.female_names:
        print("\nProcessing female first name data...")
        process_census_firstnames(gender="female", url=args.female_url, test_mode=args.test)
    
    print("\nCensus data processing complete!")

if __name__ == "__main__":
    main() 