import time
import math
import random
import os
import json

import config.utils as utils
from config.utils import prRed, prYellow, prGreen
import config.constants as constants
import config.config as config

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.remote.webelement import WebElement

from typing import List, Union
from selenium_stealth import stealth

# TODORequest Patterns
# The pattern you make the requests can also be a easy give away that you are a scraper and not a real user.
# For example, if I want to scrape all the products in a category from a e-commerce store, and I started with
# page 1 and product 1, and scraped the entire category in sequential order and at a constant rate then it is
# highly likely the requests are automated.Instead, of scraping every page and product in order, you should
# randomly scrape different pages/products and vary the interval between your requests (from seconds to minutes).
class Linkedin:
    def __init__(self):
        """Initializes a new instance of the Linkedin class, sets up the webdriver, and logs into LinkedIn.

        This is the constructor method for the Linkedin class. It sets up the webdriver, logs into LinkedIn 
        using the provided email and password, and handles any exceptions that occur during this process.

        Raises:
            Exception: An error occurred with the Chrome Driver.
        """
        try:
            # Deploy with code below
            # Set up the webdriver using ChromeDriverManager
            # webdriver_service = Service(ChromeDriverManager().install())
            # self.driver = webdriver.Chrome(service=webdriver_service)

            # add headers to make it seem like its coming from a real web browser
            capabilities = DesiredCapabilities.CHROME.copy()
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.5",
            }
            capabilities['goog:chromeOptions'] = {
                'headers': headers
            }

            options = self.browserOptions()
            self.driver = webdriver.Chrome(
                r'C:\Users\chris\Documents\GitHub\EasyApplyJobsBot\chromedriver-win64\chromedriver.exe', options=options, desired_capabilities=capabilities)
            self.driver.implicitly_wait(15)

            stealth(self.driver,
                    languages=["en-US", "en"],
                    vendor="Google Inc.",
                    platform="Win64",
                    webgl_vendor="Google Inc. (NVIDIA)",
                    renderer="ANGLE (NVIDIA, NVIDIA GeForce GTX 970 Direct3D11 vs_5_0 ps_5_0, D3D11)",
                    fix_hairline=True
                    )
        except Exception as e:
            # If an exception occurs while setting up the webdriver, print an error message and quit the driver
            prRed("Chrome Version should be <= 114.0.5735.90: " + str(e))
            # can also use context manager to manage exit process via a with block - which allows us to remove self.driver.quit()
            if hasattr(self, 'driver'):
                self.driver.quit()

        self.__countApplied = 0
        self.__countJobs = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.quit()

    def browserOptions(self):
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-extensions")
        options.add_argument('--disable-gpu')
        options.add_argument("user-data-dir=C:\environments\selenium")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("-profile")
        options.add_experimental_option(
            "excludeSwitches", ["enable-logging", "enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        return options

    # TODO - try catch block needs to be organized since the code below will need to run only if there are no errors

    def login(self, username=config.email, password=config.password):
        """Logs into LinkedIn using the provided username and password.

        This method navigates to the LinkedIn login page, enters the provided username and password, 
        and clicks the login button. It handles any exceptions that occur during this process, 
        including navigation errors, missing elements, and other general exceptions.

        Args:
            username (str): The username to use for logging in.
            password (str): The password to use for logging in.

        Raises:
            Exception: An error occurred while navigating to the LinkedIn login page.
            NoSuchElementException: The username field, password field, or login button was not found.
            Exception: An error occurred while entering the username, entering the password, or clicking the login button.
        """
        try:
            # Navigate to the LinkedIn login page
            self.navTo(constants.LINKEDIN_BASE_URL)

            if self.isLoggedIn():
                return
            else:
                self.navTo(constants.LINKEDIN_LOGIN_URL)
        except Exception as e:
            # If an exception occurs while navigating, print an error message, quit the driver, and return
            self.handle_error("Error navigating to LinkedIn: ", e)
            return

        # Do we need to check if these elements exist? What should we do in the event they dont?
        if self.element_exists("username"):
            self.enter_data("username", username)
        if self.element_exists("password"):
            self.enter_data("password", password)
        if self.element_exists(constants.LI_LOGIN_BTN_CSS_SELECTOR, By=By.CSS_SELECTOR):
            self.clickElement(
                constants.LI_LOGIN_BTN_CSS_SELECTOR, By=By.CSS_SELECTOR)

    #TODO add me button to constants
    def isLoggedIn(self):
        try:
            if self.element_exists(
                    constants.LI_PROFILE_LOCATOR, By=By.XPATH):
                return True
        except NoSuchElementException:
            return False

    def handle_error(self, message, exception):
        prRed(f"{message}: {str(exception)}")

    def element_exists(self, element_id, By=By.ID):
        return len(self.driver.find_elements(By, element_id)) > 0

    def enter_data(self, element_id, data):
        try:
            self.driver.find_element(By.ID, element_id).send_keys(data)
        except NoSuchElementException:
            self.handle_error(f"{element_id} field not found", e)
        except Exception as e:
            self.handle_error(f"Error entering {element_id}", e)

    def clickElement(self, element_id, By=By.ID):
        try:
            self.driver.find_element(By, element_id).click()
        except NoSuchElementException:
            # If the login button is not found, print an error message, quit the driver, and return
            self.handle_error(f"{element_id} field not found", e)
            return
        except Exception as e:
            # If an exception occurs while clicking the login button, print an error message, quit the driver, and return
            self.handle_error(f"Error clicking {element_id}: ", e)
            return

    #TODO add logout from constants
    def logout(self):
        """Logs out of LinkedIn"""
        try:
            self.driver.get("https://www.linkedin.com/logout/")
            print("Logged out successfully.")
        except Exception as e:
            prRed("Could not log out of LinkedIn " + str(e))

    def generateUrls(self):
        if not os.path.exists('data'):
            os.makedirs('data')
        try:
            with open('data/urlData.txt', 'w', encoding="utf-8") as file:
                linkedinJobLinks = utils.LinkedinUrlGenerate().generateUrlLinks()
                for url in linkedinJobLinks:
                    file.write(url + "\n")
            prGreen(
                "Urls are created successfully, now the bot will visit those urls.")
        except:
            prRed("Couldnt generate url, make sure you have /data folder and modified config.py file for your preferances.")

    def linkJobApply(self):
        self.generateUrls()
        urlData = utils.getUrlDataFile()

        for url in urlData:
            self.driver.get(url)
            totalJobs = self.getTotalJobs()
            totalPages = utils.jobsToPages(totalJobs)

            urlWords = utils.urlToKeywords(url)
            self.writeLine(urlWords, totalJobs)

            self.applyToJobsOnPage(url, totalPages)

        # After applications are completed what should happen?
        # self.displaySummary(urlWords)

    def writeLine(self, urlWords, totalJobs):
        lineToWrite = "\n Category: " + \
            urlWords[0] + ", Location: " + urlWords[1] + \
            ", Applying " + str(totalJobs) + " jobs."
        self.writeResults(lineToWrite)

    def writeResults(self, lineToWrite: str):
        try:
            utils.writeResults(lineToWrite)
        except Exception as e:
            prRed("Error in DisplayWriteResults: " + str(e))

    def applyToJobsOnPage(self, url, totalPages):
        for page in range(totalPages):
            currentPageJobs = constants.jobsPerPage * page
            url = url + "&start=" + str(currentPageJobs)
            self.driver.get(url)
            time.sleep(random.uniform(1, constants.botSpeed))

            offerIds = self.getOfferIds()

            for jobID in offerIds:
                self.applyToJob(jobID)
                if self.getCountApplied() >= 200:
                    self.driver.close()

    def applyToJob(self, jobID):
        offerPage = self.getOfferPage(jobID)
        jobProperties = self.getJobProperties()

        if "blacklisted" in jobProperties:
            lineToWrite = f"{jobProperties} | * 🤬 Blacklisted Job, skipped!: {offerPage}"
            self.writeLine(lineToWrite)
        else:
            button = self.findEasyApplyButton()

            if button is False:
                lineToWrite = f"{jobProperties} | * 🥳 Already applied! Job: {offerPage}"
                self.writeLine(lineToWrite)
            else:
                self.randomScrolling()
                linkedin_app = LinkedinApplication()
                self.__exit__()
                # button.click()
                # self.startApplication(jobProperties, offerPage)

                # self.incCountApplied()

        self.incCountJobs()

    def randomScrolling(self):
        scroll_page = 0
        sleep_speed = random.randint(constants.fast, constants.slow)
        while scroll_page < 4000:
            self.driver.execute_script(
                "window.scrollTo(0," + str(scroll_page) + " );")
            scroll_page += 200
            time.sleep(sleep_speed)

        if sleep_speed != 1:
            self.browser.execute_script("window.scrollTo(0,0);")
            time.sleep(sleep_speed)

    def getOfferPage(self, jobID):
        offerPage = constants.LINKEDIN_JOB_BASE_URL + str(jobID)
        self.driver.get(offerPage)

        # Wait until the page is loaded
        # wait = WebDriverWait(self.driver, 10)
        # element = wait.until(self.findEasyApplyButton,
        #                      "Could not find easy apply button")

        time.sleep(random.uniform(1, constants.botSpeed))
        return offerPage

    #TODO add easyapply button from constants
    def findEasyApplyButton(self, _) -> Union[WebElement, bool]:
        """Finds and returns the 'Easy Apply' button element on a LinkedIn job posting page. 

        This method attempts to find the 'Easy Apply' button on a LinkedIn job posting page using 
        the button's XPath. If the button is found, it is returned. If the button is not found, 
        the method returns False.

        Returns:
            WebElement: The 'Easy Apply' button element if found, False otherwise.
        """
        try:
            easyApplyButton = self.driver.find_element(
                By.XPATH, constants.LI_EASY_APPLY_LOCATOR)
            return easyApplyButton and easyApplyButton.is_displayed()
        except:
            return False

    def clickThroughApplication(self):
        pass

    def startApplication(self):

        pass

    def searchJobs(self, keywords, location):
        """Searches for jobs that match the provided keywords and location."""
        pass  # Implementation goes here

    def navigateToJobPage(self, job_id):
        """Navigates to the page of the job with the provided ID."""
        pass  # Implementation goes here

    def saveJob(self, job_id):
        """Save the job for the provided ID for later"""
        pass

    def follow_company(self, company_id):
        """Follows the company with the provided ID on LinkedIn."""
        pass  # Implementation goes here

    # To Do: implement chat gpt messages based on the job description, resume, etc.
    def sendMessage(self, recipient_id, message):
        """Send a message to LinkedIn user with provided ID"""
        pass

    # GETTER & SETTER METHODS #
    def getApplicationResults(self):
        pass

    def getElementData(self, element_id, attribute):
        """
            Finds and returns the element according to the attribute
            
            This method trys to find the element. If there is no element use handle_error
            to display an error message.
            
            Returns:
                String: The element value. Otherwise, print an error.
        """
        try:
            self.driver.find_element(
                By.ID, element_id).get_attribute(attribute).strip()
        except NoSuchElementException:
            self.handle_error(f"{element_id} field not found", e)
        except Exception as e:
            self.handle_error(f"Error retreiving {element_id}", e)

    def check_blacklist(self, text, blacklist):
        blacklisted_items = [
            blItem for blItem in blacklist if blItem.lower() in text.lower()]
        if blacklisted_items:
            return f"(blacklisted: {' '.join(blacklisted_items)})"
        return ""

    def handle_element(self, xpath_locator, By=By.XPATH, attribute="innerHTML"):
        """
            Finds the element xpath attribute and returns the elements attribute
            
            This method checks if the element exists by using the element_exists method.
            If the element exists, then return the data of that element is returned. If
            the element is not found then return an empty string.
            
            Returns:
                String: The attribute value of the element if found, an empty string otherwise.
        """
        if self.element_exists(xpath_locator, By):
            return self.getElementData(xpath_locator, By, attribute)
        return ""


    def getJobProperties(self):
        """
            Gets all the job details and returns a formatted text string.
            
            This method attempts to get all of the relevant job details and
            joins them together to display to the user the information of the
            jobs either applied to or attempted to apply to.
            
            Return:
                String: Job Description details seperated by a pipe.
        """
        jobCount = self.getCountJobs()
        jobTitle = self.getJobTitle()
        jobCompany = self.getJobCompany()
        jobLocation = self.getJobLocation()
        jobWorkPlace = self.getJobWorkPlace()
        jobPostedDate = self.getJobPostedDate()
        jobApplications = self.jobApplications()

        job_details = [jobCount, jobTitle, jobCompany,
                       jobLocation, jobWorkPlace, jobPostedDate, jobApplications]
        text_to_write = self.format_job_details(*job_details)
        return text_to_write

    def format_job_details(self, *args):
        text_to_write = " | ".join(str(arg) for arg in args)
        return text_to_write

    #TODO job description xpath to constants file
    def getJobDescription(self):
        return self.handle_element(constants.LI_JOB_DETAILS_LOCATOR, attribute="innerText")

    def getJobWorkPlace(self):
        return self.handle_element(constants.LI_JOB_WORKPLACE_XPATH)
        
    def getJobPostedDate(self):
        return self.handle_element(constants.LI_JOB_POSTEDDATE_XPATH)
        
    def getJobApplications(self):
        return self.handle_element(constants.LI_JOB_APPLICATIONS_XPATH)
    
    def getJobTitle(self):
        jobTitle = self.handle_element(constants.LI_JOB_TITLE_LOCATOR_XPATH)
        jobTitle += self.check_blacklist(jobTitle, config.blackListTitles)
        return jobTitle
    
    def getJobCompany(self):
        jobCompany = self.handle_element(constants.LI_JOB_COMPANY_LOCATOR_XPATH)
        jobCompany += self.check_blacklist(jobCompany,config.blacklistCompanies)
        return jobCompany
        
    def getJobLocation(self):
        return self.handle_element(constants.LI_JOB_LOCATION_XPATH)

    def getTotalJobs(self):
        try:
            wait = WebDriverWait(self.driver, 10)
            element = wait.until(
                EC.presence_of_element_located((By.XPATH, '//small')))
            # Once the element is present, you can access its text:
            totalJobs = element.text
        except:
            # If the element is not present after waiting, you can catch the exception and handle it as appropriate:
            print("Element not found")
        return totalJobs

    def getOfferIds(self) -> List[int]:
        """
        Extracts the unique identifiers of job offers listed on a LinkedIn page.

        This method finds all job offer elements on the current page of the 
        web driver instance, extracts their job ID, and returns these IDs 
        as a list of integers.

        The job ID is extracted from the 'data-occludable-job-id'
        attribute of each job offer element, which is assumed to be in a 
        format where the actual job ID is the string after the last colon (:).

        Returns:
            list: A list of integers, where each integer is a unique identifier 
            for a job offer listed on the current page.
        """
        offersPerPage = self.driver.find_elements(
            By.XPATH, '//li[@data-occludable-job-id]')

        offerIds = []
        for offer in offersPerPage:
            offerId = offer.get_attribute("data-occludable-job-id")
            offerIds.append(int(offerId.split(":")[-1]))

        return offerIds

    def getJobDetails(self, job_id):
        """Retrieves the details of the job with the provided ID."""
        pass  # Implementation goes here

    def getCountApplied(self):
        return self.__countApplied

    def setCountApplied(self, value):
        self.__countApplied = value

    def getCountJobs(self):
        return self.__countJobs

    def setCountJobs(self, value):
        self.__countJobs = value

    def incCountJobs(self):
        self.__countJobs += 1

    def incCountApplied(self):
        self.__countApplied += 1

    def getCookies(self, fileName='data/cookies.json'):
        return os.path.isfile(fileName)

    def storeCookies(self):
        cookies = self.getCookies()
        with open('data/cookies.json', 'w') as file:
            json.dump(cookies, file)

    def cookiesExist(self):
        return len(self.driver.get_cookies()) > 0

    def addCookies(self):
        if self.cookiesExist():
            with open("data/cookies.json", "r") as file:
                cookies = json.load(file)
                self.driver.add_cookie(cookies)
        else:
            return None

    def navTo(self, link):
        return self.driver.get(link)

    def clearCookies(self):
        self.driver.delete_all_cookies()
        self.driver.remove_all_credentials()
# Before logging in check if there are cookies.
# If there are cookies -> navigate to Linkedin.Com
#   -> verify the site loaded if it didn't load then check if there is a login element
# Else
#   nav to login page then get cookies and create a cookie.json file


class LinkedinApplication(Linkedin):
    def __init__(self):
        super().__init__()
        print(hasattr(self, 'driver'))
        
    def startApplication(self):
        pass
        
    def clickThroughApplication(self):
        pass
    
    def uploadResume(self):
        pass
    
    #TODO add chat GPT funct ionality to write a cover letter
    def writeCoverLetter(self):
        pass
    
    def uploadCoverLetter(self):
        pass
        
    def screeningQuestions(self):
        pass
        
    def submitApplication(self):
        pass

    def findRecruiter(self):
        pass
                
class MessageRecruiter:
    def __init__(self):
        pass

    def messageRecruiter(self):
        pass
        
    def writeRecruiterMessage(self):
        pass
