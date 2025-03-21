import requests
from bs4 import BeautifulSoup

def inspect_detailed():
    url = "https://www.baseball-almanac.com/players/baseball_births.php?y=1899"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    
    print(f"Requesting URL: {url}")
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the section heading
        section_heading = soup.find('h2', string='MLB Players That Were Born in 1899')
        
        if section_heading:
            print("Found section heading!")
            
            # Examine siblings and structure
            print("\nLooking at the next 10 elements after the heading...")
            current = section_heading
            count = 0
            
            while current and count < 10:
                current = current.next_sibling
                count += 1
                
                if current:
                    # Print type and some info about the element
                    element_type = type(current).__name__
                    
                    if element_type == 'Tag':
                        print(f"{count}. Element type: {element_type}, Tag name: {current.name}")
                        
                        # If it's a table, print more details
                        if current.name == 'table':
                            print(f"   Table found! It has {len(current.find_all('tr'))} rows")
                            
                            # Print first row structure
                            first_row = current.find('tr')
                            if first_row:
                                print(f"   First row has {len(first_row.find_all('th'))} header cells and {len(first_row.find_all('td'))} data cells")
                                
                                # Print sample of cell content
                                cells = first_row.find_all(['th', 'td'])
                                if cells:
                                    print(f"   First row cells content: {[cell.text.strip() for cell in cells[:3]]}")
                    else:
                        # For non-tag elements like strings, show a preview
                        content = str(current).strip()
                        preview = content[:50] + "..." if len(content) > 50 else content
                        print(f"{count}. Element type: {element_type}, Content preview: {preview}")
            
            # Look specifically for the player table
            print("\nLooking for player table with specific structure...")
            tables = soup.find_all('table')
            for i, table in enumerate(tables):
                rows = table.find_all('tr')
                print(f"Table {i+1} has {len(rows)} rows")
                
                # Print structure of a few rows to help identify the player table
                for j, row in enumerate(rows[:2]):  # Just check first 2 rows
                    cells = row.find_all(['th', 'td'])
                    print(f"  Row {j+1} has {len(cells)} cells: {[cell.name for cell in cells]}")
                    
                    # If this might be our player table, print cell contents
                    if j == 0 and len(cells) >= 2:
                        print(f"  Row {j+1} cell contents: {[cell.text.strip() for cell in cells]}")
                        
                    # Check for player links in non-header rows
                    if j > 0:
                        player_links = row.find_all('a')
                        if player_links:
                            print(f"  Row {j+1} has {len(player_links)} links, first link text: {player_links[0].text.strip()}")
                            # This is likely our player table!
                            print(f"  === This appears to be our player table (Table {i+1}) ===")
        else:
            print("Could not find section heading")
            
            # As a fallback, try to find any table with player data
            tables = soup.find_all('table')
            print(f"\nFound {len(tables)} tables on the page")
            
            # Look for tables that might contain player data (have links)
            for i, table in enumerate(tables):
                links = table.find_all('a')
                print(f"Table {i+1} has {len(links)} links")
                
                # If this table has links, check some of them
                if links:
                    print(f"Sample link texts from Table {i+1}:")
                    for j, link in enumerate(links[:5]):  # Show up to 5 sample links
                        print(f"  Link {j+1}: {link.text.strip()}")
                    
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    inspect_detailed() 