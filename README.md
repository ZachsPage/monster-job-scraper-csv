# Monster Job Posting Scraper
## Description
- The user can search for basic key words / location on Monster.com, then use that
URL as the argument for monster-job-scraper.
  - **IMPORTANT**: Pass url surrounded by quotes
- The goal was to allow a user to search multiple posting for more specific terms.

A CSV file (job_results.csv) is created with the Position, Company, Description, Link, Location, Time Posted.
- The file will be overwritten each time the script is run... so rename any csv's that need saved for later

## Setup
- Need a selenium geckodriver for your internet browser:
    - I've only verified functionality with Firefox's: https://github.com/mozilla/geckodriver

## Notes
- Press Ctrl+C to stop... interrupts can be unrelaible, so double check Task Manager!
- There is a wait time between Job Description loads, so the script take some
  time... but better than clicking through everything :D