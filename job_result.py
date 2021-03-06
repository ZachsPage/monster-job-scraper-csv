import csv
import time
from bs4 import BeautifulSoup
from bs4 import UnicodeDammit
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

# Object to represent single job posting
class JobResult:

    # Constants
    DESCRIPTION_LOAD_TIME = 1

    def __init__(self, result_element, web_driver, csv_writer):
        self.result_element = result_element
        self.driver = web_driver
        self.csv_writer = csv_writer
    
    # --- --- --- ---
    def get_info(self):
        if not self.get_scrollable_info():
            return False
        self.click_job_link()
        if not self.get_job_preview_info():
            return False

    #--- Function to: Check if HTML element existed, converts unicode, prints status, returns text ---
    def check_element_text(self, element, text_desc):
        if not element:
            return "Failed getting " + text_desc + " element"
        stripped_string = UnicodeDammit(element.text).unicode_markup.strip()
        if not stripped_string:
            error_string = "Failed Getting " + text_desc
            print(error_string)
            return error_string
        print("Found New", text_desc)
        return stripped_string

    #--- Function to: Check for / close an "expired job" pop-up, return True if expired ---
    def avoid_expired_job(self, curr_soup):
        expired_job_popup = curr_soup.find("div", {"id": "expired-job-alert"})
        if not expired_job_popup:
            return False
        popup = self.driver.find_element_by_id("expired-job-alert")
        close_popup_button = popup.find_element_by_xpath('.//button[@class="mux-close"]')
        if not close_popup_button:
            return False
        action = ActionChains(self.driver)
        action.click(close_popup_button).perform()
        return True

    #--- Function to: Get info that is immediately available in the scrollable result container ---
    def get_scrollable_info(self):
        self.summary = self.result_element.find("div", {"class": "summary"})
        if self.summary is None:
            print( "Failed to get main summary element" )
            return False

        name = self.summary.find("h2")
        self.name = self.check_element_text(name, "Position Name")

        company_element = self.summary.find("div", {"class": "company"})
        company_name = company_element.find("span", {"class": "name"})
        self.company = self.check_element_text(company_name, "Company Name")

        time_posted = self.result_element.find("time")
        self.time_posted = self.check_element_text(time_posted, "When Job Was Posted")

        location = self.summary.find("div", {"class": "location"})
        location = location.find("span", {"class": "name"})
        self.location = self.check_element_text(location, "Position Location")
        return True

    #--- Function to: Load the job postings description in Monsters side Job Preview container ---
    def click_job_link(self):
        result_header = self.summary.find("header", {"class": "card-header"})
        self.link = result_header.find("a").get('href')
        desc_link_element = self.driver.find_element_by_xpath('//a[@href="' + self.link + '"]')

        # Actions are not being cleared with action_clear(), so must remake object everytime
        action = ActionChains(self.driver)
        self.driver.execute_script("arguments[0].scrollIntoView();", desc_link_element)
        action.double_click(desc_link_element).perform()
        time.sleep(self.DESCRIPTION_LOAD_TIME)

    #--- Function to: Get the information from the job's preview 
    def get_job_preview_info(self):
        # Must create refreshable soup since new Job Description is not visible until result's job description is clicked
        refresh_soup = BeautifulSoup(self.driver.page_source, "html.parser")

        # Check for the "Job not available" pop-up, or it ruins us
        if self.avoid_expired_job(refresh_soup):
            self.description = "Expired Job Posting"
            print(self.description)

        # Get job description
        description = refresh_soup.find("div", {"id": "JobDescription"})
        self.description = self.check_element_text(description, "Job Description")
        if self.description.startswith("Fail"):
            self.description += " - try increasing DESCRIPTION_LOAD_TIME"
            print(self.description)

    # --- --- --- --- --- ---
    def write_csv_info(self):
        try:
            self.csv_writer.writerow([self.name, self.company, self.description, self.link, self.location, self.time_posted])
        except UnicodeEncodeError:
            error = "An Error occured with JobResult object... Company's Job Description probably has weird character"
            print(error)
            self.csv_writer.writerow([self.name, self.company, error, self.link, self.location, self.time_posted])
        except:
            error = "An Error occured with JobResult object, skipping posting..."
            print(error)
            self.csv_writer.writerow([error])