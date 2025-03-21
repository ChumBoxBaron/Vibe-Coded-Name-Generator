# Vibe-Coded Funny Name Generator

A Python-based tool to generate amusing names by combining elements from curated historic and fictional sources, including real census data and vintage baseball player information.

## Overview

This project creates a name generator that produces funny, unique names by drawing from carefully curated historical sources and linguistic APIs. The generator combines different name elements in unexpected ways to create humorous, yet authentic-sounding results.

## Features

- Generate names drawing from real historical data sources
- Mix and match name elements from different categories
- Combine vintage baseball player names and nicknames with census data
- Create themed name collections
- Save favorite generated names
- Expand name collections through external APIs

## Data Sources

We've collected and processed data from several high-quality sources:

- **US Census Bureau**: 152,624 unique surnames and 91,320 unique first names
- **Baseball Almanac**: Vintage player information from 1845-1920, including:
  - Full names and nicknames of baseball players
  - Birth names and playing names
  - Historical naming patterns and conventions

## Project Structure

```
Vibe-Coded-Name-Generator/
├── baseball_data/         # Baseball player data collection
├── census_data/           # US Census name data processing
├── name_generator.py      # Core name generation functionality
└── [future modules]       # Additional data sources and features
```

## Tech Stack

- Python 3.x
- Web scraping tools (requests, BeautifulSoup)
- Data processing libraries (pandas, json)
- Natural Language Processing components

## Getting Started

1. Clone this repository
2. Install requirements: `pip install -r requirements.txt`
3. Run the name generator: `python name_generator.py`

## Project Status

This project is actively under development. We've completed:
- [x] US Census data collection and processing
- [x] Vintage baseball player data acquisition
- [x] Basic name generation functionality
- [ ] Advanced linguistic patterns
- [ ] Web interface
- [ ] Additional data sources

## Milestones

1. **Data Collection** - Gather and process high-quality name datasets
2. **Core Generator** - Develop the name generation engine with multiple techniques
3. **Interface Development** - Create intuitive ways to interact with the generator
4. **Expansion** - Add more sources, features, and customization options

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
