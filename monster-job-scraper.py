import sys
import signal
import time
import csv
from bs4 import BeautifulSoup
from bs4 import UnicodeDammit
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains

# Constants
DESCRIPTION_LOAD_TIME=2

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

#--- Function to: Check if HTML element existed, converts unicode, prints status, returns text ---
def check_element_text(string, string_name):
    if string:
        print("Found New " + string_name)
        return UnicodeDammit(string.text).unicode_markup.strip()
    else:
        string = "Failed Getting " + string_name
        print(string)
        return string

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
        job_writer.writerow(["Position", "Company", "Description", "Posting Link"])

        for result in job_results:
            # Avoid Ad objects... will cause an exception
            if "featured-ad" not in result.get("class"):
                result_summary = result.find("div", {"class": "summary"})
                company = result_summary.find("div", {"class": "company"})

                position_name = result_summary.find("h2")
                position_name = check_element_text(position_name, "Position Name")

                company_name = company.find("span", {"class": "name"})
                company_name = check_element_text(company_name, "Company Name")

                result_header = result_summary.find("header", {"class": "card-header"})
                result_desc_link = result_header.find("a").get('href')
                result_desc_link_element = driver.find_element_by_xpath('//a[@href="' + result_desc_link + '"]')

                # Actions are not being cleared with action_clear(), so must remake object everytime
                action = ActionChains(driver)
                action.double_click(result_desc_link_element).perform()
                driver.execute_script("arguments[0].scrollIntoView();", result_desc_link_element)
                time.sleep(DESCRIPTION_LOAD_TIME)
                del action
                
                # Must create refreshable soup since new JobDescription is not visible result's job description is clicked
                refresh_soup = BeautifulSoup(driver.page_source, "html.parser")
                job_description = refresh_soup.find("div", {"id": "JobDescription"})
                job_description = check_element_text(job_description, "Job Description")
                if job_description is "Failed Getting Job Description" :
                    print(job_description + "... try increasing DESCRIPTION_LOAD_TIME")
                del refresh_soup

                try:
                    job_writer.writerow([position_name, company_name, job_description, result_desc_link])
                except UnicodeEncodeError:
                    error = "An Error occured during csv write... Company's Job Description probably has weird character"
                    print(error)
                    job_writer.writerow([position_name, company_name, error, result_desc_link])
                except:
                    error = "An Error occured during csv write..."
                    print(error)
                    job_writer.writerow([error])

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