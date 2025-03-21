import requests
from bs4 import BeautifulSoup

def inspect_site():
    url = "https://www.baseball-almanac.com/players/baseball_births.php?y=1899"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    print(f"Requesting URL: {url}")
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        print(f"Response status code: {response.status_code}")
        print(f"Content length: {len(response.text)} characters")
        
        # Check if we got HTML
        if "<!DOCTYPE html>" in response.text.lower() or "<html" in response.text.lower():
            print("Response appears to be HTML")
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check for tables
            tables = soup.find_all('table')
            print(f"Found {len(tables)} tables in the HTML")
            
            # Check if any tables have 'Player' in their headers
            player_tables = 0
            for i, table in enumerate(tables):
                headers = table.find_all('th')
                header_text = [h.text.strip() for h in headers]
                print(f"Table {i+1} headers: {header_text}")
                
                if any('Player' in h for h in header_text):
                    player_tables += 1
                    print(f"Found 'Player' in table {i+1}")
            
            print(f"Found {player_tables} tables with 'Player' in headers")
            
            # Print page title for context
            if soup.title:
                print(f"Page title: {soup.title.text}")
            
            # Check for specific section of the page with player data
            player_section = soup.find('h2', string='MLB Players That Were Born in 1899')
            if player_section:
                print("Found the section title 'MLB Players That Were Born in 1899'")
            else:
                print("Could not find the section title")
            
        else:
            print("Response is not HTML. First 500 characters:")
            print(response.text[:500])
            
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    inspect_site() 