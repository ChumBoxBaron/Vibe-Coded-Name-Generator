import requests
import csv
import re

def download_census_surnames():
    # URL for the census surname data
    url = "https://www2.census.gov/topics/genealogy/1990surnames/dist.all.last"
    
    print("Downloading surname data from census.gov...")
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Error downloading data: Status code {response.status_code}")
        return None
    
    return response.text

def parse_surnames(data):
    # Split the data into lines
    lines = data.strip().split('\n')
    
    # Create a list to store the parsed data
    surnames = []
    
    # Regular expression to match surname data
    # Format appears to be: NAME FREQUENCY CUMULATIVE_FREQ RANK
    pattern = r'([A-Z]+)\s+([\d.]+)\s+([\d.]+)\s+(\d+)'
    
    print("Parsing surname data...")
    for line in lines:
        matches = re.findall(pattern, line)
        for match in matches:
            surname, frequency, cumulative_freq, rank = match
            surnames.append({
                'surname': surname,
                'frequency': float(frequency),
                'cumulative_frequency': float(cumulative_freq),
                'rank': int(rank)
            })
    
    return surnames

def save_to_csv(surnames, filename='census_surnames.csv'):
    # Write the data to a CSV file
    print(f"Saving data to {filename}...")
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['surname', 'frequency', 'cumulative_frequency', 'rank']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for surname in surnames:
            writer.writerow(surname)
    
    print(f"Successfully saved {len(surnames)} surnames to {filename}")

def main():
    # Download the data
    data = download_census_surnames()
    if not data:
        return
    
    # Parse the data
    surnames = parse_surnames(data)
    
    # Save to CSV
    save_to_csv(surnames)
    
    # Display some statistics
    if surnames:
        print(f"\nTotal surnames extracted: {len(surnames)}")
        print(f"Top 5 surnames: {', '.join([s['surname'] for s in surnames[:5]])}")
        print(f"Most common surname: {surnames[0]['surname']} ({surnames[0]['frequency']}%)")

if __name__ == "__main__":
    main()

#run this code in terminal
#python census_surnames.py
#this will download the data from the census.gov website and save it to a csv file
#the data is in the format of a list of dictionaries
#the dictionaries contain the surname, frequency, cumulative frequency, and rank
#the frequency is the percentage of the population that has that surname
#the cumulative frequency is the percentage of the population that has a surname less common than or equal to that surname
#the rank is the rank of the surname in the population
#this code is a simple example of how to download data from a website and save it to a csv file