import sys
import signal
import csv
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from job_result import JobResult
from selenium.webdriver.common.action_chains import ActionChains

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
        # Run invisible browser - can comment headless out to see scraping
        ff_options = Options()
        ff_options.headless = True
        driver = webdriver.Firefox( options=ff_options )

        # Timeouts in seconds
        driver.implicitly_wait(5)
        driver.set_page_load_timeout(120)
        return driver

#--- Function to: click next page button - already expects driver to have page loaded
def expand_next_results_page():
    driver = get_driver()
    soup = BeautifulSoup(driver.page_source, "html.parser")
    action = ActionChains(driver)
    next_page_link_elem = None
    try:
        next_page_link_elem = driver.find_element_by_xpath("//a[@id='loadMoreJobs']")
    except:
        return False
    driver.execute_script("arguments[0].scrollIntoView();", next_page_link_elem)
    action.double_click(next_page_link_elem).perform()
    time.sleep(1)
    return True

#--- Function to: Expand all pages of results ---
def expand_all_results():
    print('Loaded page, expanding results...', flush=True)
    new_page_cnt = 0
    while True:
        if not expand_next_results_page():
            break
        new_page_cnt = new_page_cnt+1
    print("Done expanding results - found ", new_page_cnt, "new pages", flush=True)

#--- Function to: Scrap Monster search results ---
def scrape_jobs(url, records_scraped):
    global driver
    print('Waiting on page ' + str(url), flush=True)

    driver = get_driver()
    driver.get(url)

    # Expand results, then get soup again with all results loaded
    expand_all_results()
    soup = BeautifulSoup(driver.page_source, "html.parser")
    search_results = soup.find("div", {"id": "SearchResults"})
    job_results = search_results.find_all("section", {"class": "card-content"})

    with open('scraped_job_results.csv', 'w', newline='') as csvfile:
        
        job_writer = csv.writer(csvfile, delimiter=',')
        job_writer.writerow(["Position", "Company", "Description", "Posting Link", "Location", "Posted"])

        for result in job_results:
            # Avoid Ad objects... will cause an exception
            if "featured-ad" in result.get("class"):
                continue

            posting = JobResult(result, driver, job_writer)
            posting.get_info()
            posting.write_csv_info()

            records_scraped = records_scraped + 1
            print('Currently on search result: ' + str(records_scraped) + ', Finding Next Result...\n',flush=True)

    return records_scraped

#--- Function to: Run main program ---
def main():
    if(len(sys.argv) != 2):
        print('Invalid arguement. Please go to monster.com, do desired search, and use url as argument.')
        print('Press Ctrl+C to stop... interrupts can be unrelaible, so double check Task Manager!')
        sys.exit(-1)

    url = sys.argv[1]
    records_scraped = 0

    signal.signal(signal.SIGINT, signal_handler)

    try:
        records_scraped = scrape_jobs(url, records_scraped)
        print(str(records_scraped) + " Records Scraped!")
    except KeyboardInterrupt:
        print("Exiting due to keyboard interrupt")

    close_browser()
    print("Shutting down")

#--- Function to: Allow outside calls to main ---
if __name__ == "__main__":
    main()