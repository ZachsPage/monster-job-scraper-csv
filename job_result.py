import csv
import time
from bs4 import BeautifulSoup
from bs4 import UnicodeDammit
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

# Object to represent single job posting
class JobResult:

    # Constants
    DESCRIPTION_LOAD_TIME=1

    def __init__(self, result_element, web_driver, csv_writer):
        self.result_element = result_element
        self.driver = web_driver
        self.csv_writer = csv_writer
    
    # --- --- --- ---
    def get_info(self):
        self.get_scrollable_info()
        self.get_job_preview_info()

    #--- Function to: Check if HTML element existed, converts unicode, prints status, returns text ---
    def check_element_text(self, string, string_name):
        if string:
            print("Found New " + string_name)
            return UnicodeDammit(string.text).unicode_markup.strip()
        else:
            string = "Failed Getting " + string_name
            print(string)
            return string

    #--- Function to: Get info that is immediate available in the scrollable result container ---
    def get_scrollable_info(self):
        self.summary = self.result_element.find("div", {"class": "summary"})

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

    #--- Function to: Load the job postings description in Monsters side Job Preview container ---
    def click_job_link(self):
        result_header = self.summary.find("header", {"class": "card-header"})
        self.link = result_header.find("a").get('href')
        desc_link_element = self.driver.find_element_by_xpath('//a[@href="' + self.link + '"]')

        # Actions are not being cleared with action_clear(), so must remake object everytime
        action = ActionChains(self.driver)
        action.double_click(desc_link_element).perform()
        self.driver.execute_script("arguments[0].scrollIntoView();", desc_link_element)
        time.sleep(self.DESCRIPTION_LOAD_TIME)

    #--- Function to: Get the information from the job's preview 
    def get_job_preview_info(self):
        self.click_job_link()

        # Must create refreshable soup since new Job Description is not visible until result's job description is clicked
        refresh_soup = BeautifulSoup(self.driver.page_source, "html.parser")
        description = refresh_soup.find("div", {"id": "JobDescription"})
        self.description = self.check_element_text(description, "Job Description")
        if description is "Failed Getting Job Description" :
            print(description + "... try increasing DESCRIPTION_LOAD_TIME")

    # --- --- --- --- --- ---
    def write_csv_info(self):
        try:
            self.csv_writer.writerow([self.name, self.company, self.description, self.link, self.location, self.time_posted])
        except UnicodeEncodeError:
            error = "An Error occured during csv write... Company's Job Description probably has weird character"
            print(error)
            self.csv_writer.writerow([self.name, self.company, error, self.link, self.location, self.time_posted])
        except:
            error = "An Error occured during csv write..."
            print(error)
            self.csv_writer.writerow([error])