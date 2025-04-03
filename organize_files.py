import os
import json
import shutil
import datetime
import csv
from pathlib import Path

def print_section(title):
    """Print a formatted section title."""
    print("\n" + "=" * 50)
    print(f" {title} ".center(50, "="))
    print("=" * 50)

def create_directory_structure():
    """Create the necessary directory structure if it doesn't exist."""
    base_dir = "baseball_data"
    subdirs = ["final", "yearly", "archive", "tests"]
    
    for subdir in subdirs:
        path = os.path.join(base_dir, subdir)
        os.makedirs(path, exist_ok=True)
    
    print("Directory structure ensured.")

def archive_old_files():
    """Move older versions of files to the archive directory."""
    print_section("ARCHIVING OLD FILES")
    
    base_dir = "baseball_data"
    archive_dir = os.path.join(base_dir, "archive")
    
    # Files to check for archiving (excluding v2 files which are the latest)
    patterns = [
        "baseball_dataset_*.json",
        "baseball_first_names_*.json",
        "baseball_last_names_*.json",
        "baseball_nicknames_*.json",
        "baseball_players_*.json",
        "all_players_*.json",
    ]
    
    # Files we should not archive
    exclusions = [
        "baseball_dataset_v2_complete.json",
        "baseball_first_names_v2.json",
        "baseball_last_names_v2.json",
        "baseball_nicknames_v2.json",
        "baseball_players_v2.json",
        "all_players_v2_current.json",
    ]
    
    files_moved = 0
    
    # Search in base_dir and final dir
    for search_dir in [base_dir, os.path.join(base_dir, "final")]:
        if not os.path.exists(search_dir):
            continue
            
        for pattern in patterns:
            import glob
            pattern_path = os.path.join(search_dir, pattern)
            for file_path in glob.glob(pattern_path):
                filename = os.path.basename(file_path)
                
                # Skip the latest v2 files
                if filename in exclusions:
                    continue
                
                # Archive the file
                dest_path = os.path.join(archive_dir, filename)
                try:
                    shutil.move(file_path, dest_path)
                    print(f"Archived: {filename}")
                    files_moved += 1
                except Exception as e:
                    print(f"Error archiving {filename}: {e}")
    
    # Also move test files to the test directory
    test_dir = os.path.join(base_dir, "tests")
    test_patterns = [
        "test_*.json",
        "test_*.py",
        "simplified_small_test.py",
    ]
    
    for pattern in test_patterns:
        pattern_path = os.path.join(base_dir, pattern)
        for file_path in glob.glob(pattern_path):
            filename = os.path.basename(file_path)
            dest_path = os.path.join(test_dir, filename)
            
            if os.path.exists(file_path) and file_path != dest_path:
                try:
                    shutil.move(file_path, dest_path)
                    print(f"Moved to tests: {filename}")
                    files_moved += 1
                except Exception as e:
                    print(f"Error moving {filename}: {e}")
    
    if files_moved == 0:
        print("No files needed archiving.")
    else:
        print(f"Archived {files_moved} files.")

def extract_name_lists():
    """Extract name lists from the main dataset and save as separate files."""
    print_section("EXTRACTING NAME LISTS")
    
    base_dir = "baseball_data"
    final_dir = os.path.join(base_dir, "final")
    dataset_path = os.path.join(final_dir, "baseball_dataset_v2_complete.json")
    
    if not os.path.exists(dataset_path):
        print(f"Main dataset not found at {dataset_path}")
        return False
    
    try:
        with open(dataset_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract name lists
        name_lists = {
            "first_names": data.get("name_lists", {}).get("first_names", {}),
            "last_names": data.get("name_lists", {}).get("last_names", {}),
            "nicknames": data.get("name_lists", {}).get("nicknames", {})
        }
        
        # Check if we have data
        if not any(name_lists.values()):
            print("No name lists found in the dataset.")
            return False
        
        # Save each name list as JSON and CSV
        for name_type, names in name_lists.items():
            # Save as JSON
            json_path = os.path.join(final_dir, f"baseball_{name_type}_v2.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(names, f, indent=2)
            print(f"Saved: {json_path}")
            
            # Save as CSV
            csv_path = os.path.join(final_dir, f"baseball_{name_type}_v2.csv")
            with open(csv_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["name", "frequency"])
                for name, freq in sorted(names.items(), key=lambda x: x[1], reverse=True):
                    writer.writerow([name, freq])
            print(f"Saved: {csv_path}")
        
        # Extract player data and save separately
        players_path = os.path.join(final_dir, "baseball_players_v2.json")
        with open(players_path, 'w', encoding='utf-8') as f:
            json.dump(data.get("players", []), f, indent=2)
        print(f"Saved: {players_path}")
        
        return True
    
    except Exception as e:
        print(f"Error extracting name lists: {e}")
        return False

def verify_dataset():
    """Verify the dataset by checking key statistics."""
    print_section("VERIFYING DATASET")
    
    base_dir = "baseball_data"
    final_dir = os.path.join(base_dir, "final")
    dataset_path = os.path.join(final_dir, "baseball_dataset_v2_complete.json")
    
    if not os.path.exists(dataset_path):
        print(f"Main dataset not found at {dataset_path}")
        return False
    
    try:
        with open(dataset_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check if we have player data
        players = data.get("players", [])
        if not players:
            print("No player data found in the dataset.")
            return False
        
        total_players = len(players)
        years_covered = set()
        birth_names_count = 0
        nicknames_count = 0
        
        for player in players:
            if "birth_year" in player and player["birth_year"]:
                years_covered.add(player["birth_year"])
            
            if player.get("birth_name"):
                birth_names_count += 1
                
            if player.get("nicknames") and len(player.get("nicknames", [])) > 0:
                nicknames_count += 1
        
        # Print stats
        print(f"Total players: {total_players}")
        print(f"Birth years covered: {min(years_covered)} to {max(years_covered)}")
        print(f"Players with birth names: {birth_names_count} ({birth_names_count/total_players*100:.1f}%)")
        print(f"Players with nicknames: {nicknames_count} ({nicknames_count/total_players*100:.1f}%)")
        
        # Check first and last name lists
        first_name_count = len(data.get("name_lists", {}).get("first_names", {}))
        last_name_count = len(data.get("name_lists", {}).get("last_names", {}))
        nickname_count = len(data.get("name_lists", {}).get("nicknames", {}))
        
        print(f"Unique first names: {first_name_count}")
        print(f"Unique last names: {last_name_count}")
        print(f"Unique nicknames: {nickname_count}")
        
        # Check for any partial years (years not completed in the scraping process)
        progress_path = os.path.join(base_dir, "baseball_progress_v2.json")
        if os.path.exists(progress_path):
            with open(progress_path, 'r', encoding='utf-8') as f:
                progress = json.load(f)
            
            completed_years = progress.get("completed_years", [])
            partial_year = progress.get("current_year")
            
            if partial_year and partial_year not in completed_years:
                print(f"WARNING: Year {partial_year} may be incomplete.")
        
        return True
    
    except Exception as e:
        print(f"Error verifying dataset: {e}")
        return False

def generate_readme():
    """Generate a simple README file for the dataset."""
    print_section("GENERATING README")
    
    base_dir = "baseball_data"
    final_dir = os.path.join(base_dir, "final")
    readme_path = os.path.join(final_dir, "README.md")
    
    # Get dataset info if available
    meta_info = {}
    dataset_path = os.path.join(final_dir, "baseball_dataset_v2_complete.json")
    if os.path.exists(dataset_path):
        try:
            with open(dataset_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                meta_info = data.get("meta", {})
        except:
            pass
    
    # Generate README content
    readme_content = f"""# Baseball Player Data Collection v2

## Dataset Information

- **Collection Date**: {meta_info.get("collection_date", datetime.datetime.now().strftime("%Y-%m-%d"))}
- **Version**: 2.0
- **Source**: Baseball Almanac (https://www.baseball-almanac.com/)
- **Years Covered**: 1845-1920
- **Total Players**: {meta_info.get("total_players", "N/A")}

## Files in this Directory

- `baseball_dataset_v2_complete.json` - Complete dataset with metadata and name lists
- `baseball_players_v2.json` - Players-only dataset for easier processing
- `baseball_first_names_v2.json` - First names with frequencies (JSON)
- `baseball_first_names_v2.csv` - First names with frequencies (CSV)
- `baseball_last_names_v2.json` - Last names with frequencies (JSON)
- `baseball_last_names_v2.csv` - Last names with frequencies (CSV)
- `baseball_nicknames_v2.json` - Nicknames with frequencies (JSON)
- `baseball_nicknames_v2.csv` - Nicknames with frequencies (CSV)

## Usage Notes

- All players' birth names and nicknames have been properly processed
- First names are extracted from birth names when available
- Nicknames are split into arrays for easier random selection
- See the main project README for more detailed information on data structure

Generated on: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
"""
    
    try:
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print(f"Created README at {readme_path}")
        return True
    except Exception as e:
        print(f"Error generating README: {e}")
        return False

def main():
    print_section("BASEBALL DATA ORGANIZER")
    print("This script organizes and verifies the baseball dataset files.")
    
    # Create directory structure
    create_directory_structure()
    
    # Archive old files
    archive_old_files()
    
    # Extract name lists
    extract_name_lists()
    
    # Verify dataset
    verify_dataset()
    
    # Generate README
    generate_readme()
    
    print_section("ORGANIZATION COMPLETE")
    print("All files have been organized into the appropriate directories.")
    print("The final dataset is available in the baseball_data/final/ directory.")

if __name__ == "__main__":
    main() 