import os
import sys
from baseball_batch_scraper import ensure_output_dir, scrape_year, simple_name_split, process_batch, load_progress, save_progress, save_final_output

# A smaller version of the batch scraper for testing purposes
# This will just scrape a few years between 1890-1895

if __name__ == "__main__":
    # Create the output directory
    ensure_output_dir()
    
    # Load any existing progress
    progress = load_progress()
    
    # Define a small range of years to test with
    test_years = list(range(1890, 1896))  # Just 1890-1895
    remaining_years = [year for year in test_years if year not in progress['completed_years']]
    
    if not remaining_years:
        print("All test years have been processed!")
        save_final_output(progress['all_players'])
        sys.exit(0)
    
    print(f"Starting baseball data collection (TEST MODE)")
    print(f"Years to process: {len(remaining_years)} out of {len(test_years)}")
    print(f"Already completed: {len(progress['completed_years'])} years")
    
    # Process the batch
    process_batch(remaining_years, progress)
    
    # Final processing
    print("\nAll test years complete!")
    save_final_output(progress['all_players'])
    print("Baseball test data collection complete!") 