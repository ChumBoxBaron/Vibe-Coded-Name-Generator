import requests
import pandas as pd
import json
import re

def download_census_data(url):
    """Download data from the census URL."""
    print(f"Downloading data from {url}...")
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.text

def parse_fixed_width_data(text):
    """Parse fixed-width formatted census data."""
    lines = text.split('\n')
    data = []
    
    # Skip any header lines - assuming data starts with a name
    data_lines = [line for line in lines if line.strip() and re.match(r'^\s*[A-Z]', line)]
    
    for line in data_lines:
        # Based on analysis of the file structure (adjust these positions as needed)
        # This is a placeholder - you'll need to adjust based on actual file format
        try:
            parts = line.split()
            if len(parts) >= 4:
                surname = parts[0]
                frequency = float(parts[1])
                cumulative_freq = float(parts[2])
                rank = int(parts[3])
                
                data.append({
                    "surname": surname,
                    "frequency": frequency,
                    "cumulative_frequency": cumulative_freq,
                    "rank": rank
                })
        except Exception as e:
            print(f"Error parsing line: {line}")
            print(f"Error details: {e}")
    
    return data

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
    # URL of the census data
    url = "https://www2.census.gov/topics/genealogy/1990surnames/dist.all.last"
    
    try:
        # Download the data
        text_data = download_census_data(url)
        
        # Print a sample to check the format
        print("\nSample of downloaded data (first 200 characters):")
        print(text_data[:200])
        
        # Parse the data
        parsed_data = parse_fixed_width_data(text_data)
        
        # Print a sample of parsed data
        print("\nSample of parsed data (first 3 records):")
        for i, record in enumerate(parsed_data[:3]):
            print(f"Record {i+1}: {record}")
        
        # Save as JSON and CSV
        save_as_json(parsed_data, "census_surnames_1990.json")
        save_as_csv(parsed_data, "census_surnames_1990.csv")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 
    