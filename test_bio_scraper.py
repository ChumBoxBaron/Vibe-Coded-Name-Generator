from simplified_scraper import scrape_player_detail

def test_player(player_url, player_name):
    print(f"\nTesting player: {player_name}")
    print(f"URL: {player_url}")
    result = scrape_player_detail(player_url)
    print("\nResult:")
    for key, value in result.items():
        print(f"{key}: {value}")
    return result

def main():
    print("Testing updated scrape_player_detail function...")
    
    # Test with Lip Pike
    test_player('https://www.baseball-almanac.com/players/player.php?p=pikeli01', "Lip Pike")
    
    # Test with Babe Ruth
    test_player('https://www.baseball-almanac.com/players/player.php?p=ruthba01', "Babe Ruth")
    
    print("\nTests completed.")

if __name__ == "__main__":
    main() 