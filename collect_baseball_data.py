import os
import sys
from baseball_batch_scraper import ensure_output_dir, process_batch, load_progress, save_progress, save_final_output

"""
Script to collect baseball name data from Baseball Almanac.
This will start with a small range and can be expanded later.
"""

def collect_data_for_years(start_year, end_year):
    """
    Collect data for a range of years.
    
    Args:
        start_year (int): Start year
        end_year (int): End year
    """
    # Create the output directory
    ensure_output_dir()
    
    # Load any existing progress
    progress = load_progress()
    
    # Define the range of years to collect
    years_to_process = list(range(start_year, end_year + 1))
    remaining_years = [year for year in years_to_process if year not in progress['completed_years']]
    
    if not remaining_years:
        print(f"All years from {start_year} to {end_year} have been processed!")
        save_final_output(progress['all_players'])
        return
    
    print(f"Starting baseball data collection")
    print(f"Years to process: {len(remaining_years)} out of {len(years_to_process)}")
    print(f"Already completed: {len(progress['completed_years'])} years")
    
    # Process the batch
    process_batch(remaining_years, progress)
    
    # Final processing
    print("\nAll requested years complete!")
    save_final_output(progress['all_players'])
    print("Baseball data collection complete!")

def main():
    """Main function to start data collection."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Collect baseball player data from Baseball Almanac')
    parser.add_argument('--start', type=int, default=1890, help='Start year (default: 1890)')
    parser.add_argument('--end', type=int, default=1900, help='End year (default: 1900)')
    
    args = parser.parse_args()
    
    # Validate the years
    if args.start < 1845 or args.start > 1920:
        print(f"Start year {args.start} is outside the valid range (1845-1920)")
        return
    
    if args.end < 1845 or args.end > 1920:
        print(f"End year {args.end} is outside the valid range (1845-1920)")
        return
    
    if args.start > args.end:
        print(f"Start year {args.start} cannot be after end year {args.end}")
        return
    
    # Collect the data
    collect_data_for_years(args.start, args.end)

if __name__ == "__main__":
    main() 