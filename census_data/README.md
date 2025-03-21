# Census Data Processing

This part of the project focuses on extracting, processing, and organizing US Census data on names.

## Data Sources

The data is sourced from the US Census Bureau's 1990 Surnames and First Names datasets:

- **Surnames**: [US Census 1990 Surnames](https://www2.census.gov/topics/genealogy/1990surnames/dist.all.last)
- **Male First Names**: [US Census 1990 Male First Names](https://www2.census.gov/topics/genealogy/1990surnames/dist.male.first)
- **Female First Names**: [US Census 1990 Female First Names](https://www2.census.gov/topics/genealogy/1990surnames/dist.female.first)

## Directory Structure

The census data is organized in the following structure:

- `census_data/` - Base directory for all census data
  - `output/` - General output directory
  - `archive/` - Stores archived versions of previous data pulls
  - `tests/` - Contains test output files (limited dataset)
  - `final/` - Contains final processed data files
  - Raw data files are stored in the base directory but not tracked in git

## Data Files

The processed data is available in both JSON and CSV formats:

- **Surnames**:
  - `census_data/final/census_surnames.json`
  - `census_data/final/census_surnames.csv`
  
- **Male First Names**:
  - `census_data/final/census_firstnames_male.json`
  - `census_data/final/census_firstnames_male.csv`
  
- **Female First Names**:
  - `census_data/final/census_firstnames_female.json`
  - `census_data/final/census_firstnames_female.csv`
  
- **Combined First Names**:
  - `census_data/final/census_firstnames_combined.json`
  - `census_data/final/census_firstnames_combined.csv`

## Data Structure

Each record in the processed data includes:

- **Surnames**:
  - `surname`: The surname
  - `frequency`: Frequency percentage
  - `cumulative_frequency`: Cumulative frequency percentage
  - `rank`: Rank by frequency
  - `source`: Data source attribution

- **First Names**:
  - `firstname`: The first name
  - `gender`: "male" or "female"
  - `frequency`: Frequency percentage
  - `cumulative_frequency`: Cumulative frequency percentage
  - `rank`: Rank by frequency
  - `source`: Data source attribution

## Usage

To process the census data, use the `census_data_processor.py` script:

```
# Process all data (surnames and first names)
python census_data_processor.py --all

# Process only surnames
python census_data_processor.py --surnames

# Process only first names (both male and female)
python census_data_processor.py --firstnames

# Process only male first names
python census_data_processor.py --male-names

# Process only female first names
python census_data_processor.py --female-names

# Run in test mode (limited dataset)
python census_data_processor.py --all --test
```

## Statistics

- **Surnames**: 88,799 unique surnames
- **Male First Names**: 1,219 unique first names
- **Female First Names**: 4,275 unique first names
- **Combined First Names**: 5,494 unique first names 