# Monster Job Posting Scraper
## Description
- The user can search for basic key words / location on Monster.com, then use that
URL as the argument for monster_job_scraper.
  - **IMPORTANT**: Pass url surrounded by quotes
- The overall project goals were:
  - Allow filtering results further than Monster allows
  - Allow more specific keyword searching
  - Be a random project for me 

A CSV file (scraped_job_results.csv) is created with the Position, Company, Description, Link, Location, Time Posted.
- The file will be overwritten each time the script is run... so rename any csv's that need saved for later

## Setup
- Need a selenium geckodriver for your internet browser:
    - I've only verified functionality with Firefox's: https://github.com/mozilla/geckodriver

## Notes
- Press Ctrl+C to stop... interrupts can be unrelaible, so double check Task Manager
  for leftover browser instances and geckodrivers!
- There is a wait time between Job Description loads, so the script take some
  time... but better than clicking through everything :D