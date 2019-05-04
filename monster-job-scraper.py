import sys
import signal
import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from job_result import JobResult

# Opens Web Browser for script
driver = None

#--- Function to: Kill web driver task ---
def close_browser():
    print("Closing Browser, Please Wait...")
    driver.quit()
    sys.exit(0)

#--- Function to: Register Ctrl+C signal handler ---
def signal_handler(sig, frame):
        global driver
        print('You pressed Ctrl+C!')
        close_browser()

#--- Function to: Create/Get Selenium FireFox Web Driver ---
def get_driver():
    global driver
    if driver is not None:
        return driver
    else:
        # Run invisible browser
        ff_options = Options()
        ff_options.headless = True
        driver = webdriver.Firefox( firefox_options=ff_options )

        # Timeouts in seconds
        driver.implicitly_wait(5)
        driver.set_page_load_timeout(120)
        return driver

#--- Function to: Scrap Monster search results ---
def scrape_jobs(url, records_scraped):
    global driver
    print('Waiting on page ' + str(url))

    driver = get_driver()
    driver.get(url)

    print('Loaded page, getting results...')

    soup = BeautifulSoup(driver.page_source, "html.parser")
    search_results = soup.find("div", {"id": "SearchResults"})
    job_results = search_results.find_all("section", {"class": "card-content"})

    with open('job_results.csv', 'w', newline='') as csvfile:
        
        job_writer = csv.writer(csvfile, delimiter=',')
        job_writer.writerow(["Position", "Company", "Description", "Posting Link", "Location", "Posted"])

        for result in job_results:
            # Avoid Ad objects... will cause an exception
            if "featured-ad" not in result.get("class"):

                posting = JobResult(result, driver, job_writer)
                posting.get_info()
                posting.write_csv_info()

                records_scraped = records_scraped + 1
                print('Currently on search result: ' + str(records_scraped) + ', Finding Next Result...\n')

    return records_scraped

#--- Function to: Run main program ---
def main():
    if(len(sys.argv) != 2):
        print('Invalid arguement. Please go to monster.com, do desired search.')
        print(' scroll the whole way down the results, and click "Load more jobs"')
        print(' until all available jobs are loaded. Then, use url as argument.')
        print('Press Ctrl+C to stop search and close browser... double check Task Manager!')
        sys.exit(-1)

    url = sys.argv[1]
    records_scraped = 0

    signal.signal(signal.SIGINT, signal_handler)

    records_scraped = scrape_jobs(url, records_scraped)
    print(str(records_scraped) + " Records Scraped!")

    close_browser()

#--- Function to: Allow outside calls to main ---
if __name__ == "__main__":
    main()