# Vibe-Coded Funny Name Generator

A Python-based tool to generate amusing names by combining elements from curated historic and fictional sources, including real census data and vintage baseball player information.

## Overview

This project creates a name generator that produces funny, unique names by drawing from carefully curated historical sources and linguistic APIs. The generator combines different name elements in unexpected ways to create humorous, yet authentic-sounding results.

## Features

- Generate names drawing from real historical data sources
- Mix and match name elements from different categories
- Combine vintage baseball player names and nicknames with census data
- Create funny names using child-friendly humor techniques
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
├── generators/            # Different name generation strategies
├── templates/             # Web interface templates
├── utils/                 # Utility functions
├── app.py                 # Flask web application
└── name_generator.py      # Core name generation functionality
```

## Tech Stack

- Python 3.x
- Web scraping tools (requests, BeautifulSoup)
- Data processing libraries (pandas, json)
- Natural Language Processing components
- Flask for web interface

## Getting Started

1. Clone this repository
2. Install requirements: `pip install -r requirements.txt`
3. Run the web application: `python app.py`
4. Or run the name generator directly: `python name_generator.py`

## Project Status

This project is actively under development. We've completed:
- [x] US Census data collection and processing
- [x] Vintage baseball player data acquisition
- [x] Basic name generation functionality
- [x] Child-friendly funny name generator
- [x] Web interface
- [ ] Advanced linguistic patterns
- [ ] Additional data sources

## Example Outputs

### Baseball Name Generator

The baseball name generator produces authentic-sounding vintage baseball player names from the 1845-1920 era. Names are generated with a 35% chance of including a nickname (deliberately tuned below the actual 85% historical rate to ensure better variety). The generator prevents duplicate nicknames within a single batch of results, ensuring maximum variety.

Here are some sample outputs from our current implementation:

```
1. Fred "Red" Ellam
2. James Siever
3. William Borchers
4. Carl "Barney" Hawk
5. Abner Staley
6. Anthony "Dutchman" Smith
7. Hunter "Slim" Zabala
8. Ellis Hock
9. Theodore Gumbert
10. Howard "Charlie" Cuccurullo
```

The generator draws from a rich dataset of:
- 1,125 unique first names
- 4,513 unique last names
- 1,984 unique nicknames

Most common components include:
- First names: John, William, George, James, Charles
- Last names: Smith, Miller, Jones, Brown, Williams
- Nicknames: Bill, Joe, Ed, Jim, Charlie

### Census Name Generator

The census-based name generator produces realistic contemporary names with proper capitalization, drawing from modern US Census data. Here are sample outputs:

```
1. Margaret Hall
2. Angela Almodovar
3. Gerald Thomas
4. Amy Smith
5. Milton Brewer
6. Bettie Olmstead
7. Jason Butler
8. Christopher Flynn
9. Nickolas Phillips
10. Setsuko Rodriguez
```

The generator draws from a comprehensive dataset of:
- 5,494 unique first names
- 88,799 unique last names

Most common first names from census data:
- James (3.318%)
- John (3.271%)
- Robert (3.143%)

### Unique Census Name Generator

This version provides uncommon but realistic name combinations that avoid the most frequent pairings. It uses a simple rule to avoid combining top 100 most common first names with top 100 most common last names.

### Claude's Fancier/Quanty-er Unique Names

This advanced generator creates distinctive yet plausible names derived from census data using a sophisticated weighted system favoring rarer combinations.

### Funny Names Generator

Our newest addition is the Funny Names generator that creates names with crude humor and double entendres. These names feature humorous word patterns derived from census data. Here are some sample outputs:

```
1. WOODY JOHNSON
2. RANDY BUTTS
3. RICHARD PETERS
4. PETER HANCOCK
5. BOOBOO TOOTOOT
6. POOPY DOOLEY
7. BUBBA PUFF
8. ZIGGY WIGGLES
9. DOODOO HINEY
10. PIPPY PUDDINGTON
```

The generator uses sophisticated pattern matching on census data to find names with humorous qualities.

### Name Generation Strategies

Our generator uses different strategies to produce names:

#### 1. Standard Census Name Generator
Generates names by randomly selecting from Census data based on actual frequency distributions. This produces realistic names but tends to favor common names. All names are properly capitalized.

#### 2. Unique Census Name Generator
Uses a simple rule to avoid combining top 100 most common first names with top 100 most common last names. This ensures no extremely common combinations while maintaining realism.

#### 3. Claude's Fancier/Quanty-er Unique Names
This advanced generator uses a sophisticated weighted probability system with multiple strategies:

- **Tier-based Selection**: Names are divided into 5 tiers based on frequency:
  - Tier 1: Very common (top 10%)
  - Tier 2: Common (10-30%)
  - Tier 3: Moderately common (30-60%)
  - Tier 4: Uncommon (60-90%)
  - Tier 5: Rare (bottom 10%)

- **Biased Tier Selection**: The system favors uncommon and rare name tiers:
  - Very common names: 5% chance
  - Common names: 10% chance
  - Moderately common names: 20% chance
  - Uncommon names: 30% chance
  - Rare names: 35% chance

- **Inverted Frequency Weighting**: Within each tier, frequencies are inverted, making less common names more likely to be selected.

- **Logarithmic Scaling**: Weights are logarithmically scaled to create a more balanced distribution while still favoring uniqueness.

- **Combination Rules**: Additional rules ensure interesting combinations, such as pairing very common first names with only uncommon or rare last names.

This produces names that are significantly more unique while still drawing from real census data, resulting in distinctive yet plausible names.

#### 4. Funny Names Generator
The Funny Names generator uses two distinct approaches to create humorous names:

- **Silly Sound Names**: This approach identifies and combines names with inherently funny sound patterns:
  - Names with specific letter combinations (oo, ee, zz, etc.)
  - Repeating syllables and rhyming elements 
  - Names that sound like sound effects (zoom, bang, pop, etc.)
  - Names with unusual mouth movements when spoken
  
  The algorithm uses regular expression pattern matching against the census database to identify names with these qualities, then strategically pairs them for maximum humor effect, often matching similar sound patterns between first and last names.

- **Crude Humor Names**: This approach looks for:
  - Names with crude or suggestive connotations
  - Names that sound like body parts or functions
  - Innuendo-laden combinations with double entendres
  - Names with suggestive patterns

  This algorithm maintains a curated set of "funny" first and last names and also uses pattern matching to identify names in the census database that match crude humor patterns.

Both approaches are implemented in a single generator that alternates between them, providing variety in the humorous names produced.

## Web Interface Features

The name generator web interface offers several intuitive features:

- **Generator Type Selection**: Choose from multiple name generation algorithms
- **Descriptive Information**: Each generator type includes a brief description of what it produces
- **Customizable Output Count**: Select how many names to generate at once
- **Instant Generation**: Names are generated quickly without page refresh
- **Mobile-Friendly Design**: Responsive layout works well on all devices

## Milestones

1. **Data Collection** - Gather and process high-quality name datasets
2. **Core Generator** - Develop the name generation engine with multiple techniques
3. **Interface Development** - Create intuitive ways to interact with the generator
4. **Expansion** - Add more sources, features, and customization options

## Deploying as a Website

Currently, the project runs as a local web application. To deploy it as a public website, you would need:

### Hosting Requirements

1. **Web Hosting/Server**:
   - Cloud provider (AWS, Google Cloud, Azure)
   - Virtual Private Server (Digital Ocean, Linode)
   - Platform as a Service (Heroku, Render, Fly.io, Vercel)

2. **Domain Name**:
   - Purchase from a registrar (Namecheap, GoDaddy, etc.)
   - Configure DNS records to point to your hosting

3. **Production Configuration**:
   - WSGI server (Gunicorn, uWSGI) instead of Flask's development server
   - Web server (Nginx, Apache) as a reverse proxy
   - Environment variables for configuration

4. **Security Measures**:
   - HTTPS/SSL certificate (Let's Encrypt)
   - Proper secrets management
   - Input validation and security headers

5. **Database** (if needed):
   - Set up production database (PostgreSQL, MySQL)
   - Configure connection pooling

6. **Deployment Process**:
   - CI/CD pipeline
   - Docker containerization (optional)
   - Environment configuration

7. **Monitoring & Maintenance**:
   - Logging
   - Error tracking
   - Performance monitoring
   - Regular updates and backups

### Recommended Approach

For beginners, the simplest deployment approach would be using a Platform as a Service (PaaS) like Heroku or Render. These platforms handle much of the infrastructure configuration automatically and provide straightforward deployment processes.

### Future Deployment Plans

- [ ] Create production configuration files
- [ ] Set up containerization with Docker
- [ ] Implement CI/CD pipeline
- [ ] Deploy to cloud platform
- [ ] Configure custom domain and SSL

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
