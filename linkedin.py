import time
import math
import random
import os
import config.utils as utils
import config.constants as constants
import config.config as config

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config.utils import prRed, prYellow, prGreen

from webdriver_manager.chrome import ChromeDriverManager


class Linkedin:
    def __init__(self):
        try:
            self.driver = webdriver.Chrome(ChromeDriverManager().install())
            self.driver.get(
                "https://www.linkedin.com/login?trk=guest_homepage-basic_nav-header-signin")
            prYellow("Trying to log in linkedin.")
        except Exception as e:
            prRed("Warning ChromeDriver" + str(e))
        try:
            self.driver.find_element("id", "username").send_keys(config.email)
            self.driver.find_element(
                "id", "password").send_keys(config.password)
            # time.sleep(5)
            self.driver.find_element(
                "xpath", '//*[@id="organic-div"]/form/div[3]/button').click()
        except:
            prRed("Couldnt log in Linkedin.")

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
            prRed("❌ Couldn't generate url, make sure you have /data folder and modified config.py file for your preferances.")

    def linkJobApply(self):
        self.generateUrls()
        countApplied = 0
        countJobs = 0

        urlData = utils.getUrlDataFile()

        wait = WebDriverWait(self.driver, 10)

        for url in urlData:
            self.driver.get(url)
            totalJobs = self.getTotalJobs(wait)
            totalPages = utils.jobsToPages(totalJobs)

            urlWords = utils.urlToKeywords(url)
            lineToWrite = "\n Category: " + \
                urlWords[0] + ", Location: " + urlWords[1] + \
                ", Applying " + str(totalJobs) + " jobs."

            self.displayWriteResults(lineToWrite)

            for page in range(totalPages):
                currentPageJobs = constants.jobsPerPage * page
                url = url + "&start=" + str(currentPageJobs)
                self.driver.get(url)
                time.sleep(random.uniform(1, constants.botSpeed))

                offerIds = self.getOfferIds()
                # Loop through all job IDs in the offerIds list
                for jobID in offerIds:
                    # Build the URL for the job offer page
                    offerPage = f'https://www.linkedin.com/jobs/view/{jobID}'
                    # Load the job offer page
                    self.driver.get(offerPage)
                    # Wait for a random amount of time, as specified in constants.botSpeed
                    time.sleep(random.uniform(1, constants.botSpeed))

                    # Increment the count of jobs
                    countJobs += 1

                    if countJobs >= 200:
                        self.driver.close()
                    # Get the properties of the current job
                    jobProperties = self.getJobProperties(countJobs)

                    # Check if the job is blacklisted
                    if "blacklisted" in jobProperties:
                        # Write a message indicating that the job is blacklisted and was skipped
                        lineToWrite = f"{jobProperties} | * 🤬 Blacklisted Job, skipped!: {offerPage}"
                        self.displayWriteResults(lineToWrite)
                        # Skip to the next job
                        continue

                    # Try to find the easy apply button
                    button = self.easyApplyButton()
                    # If the easy apply button was not found
                    if button is False:
                        # Write a message indicating that the job has already been applied to
                        lineToWrite = f"{jobProperties} | * 🥳 Already applied! Job: {offerPage}"
                        self.displayWriteResults(lineToWrite)
                        # Skip to the next job
                        continue

                    # If the easy apply button was found, click it
                    button.click()
                    # Wait for a random amount of time, as specified in constants.botSpeed
                    time.sleep(random.uniform(1, constants.botSpeed))
                    # Increment the count of jobs applied
                    countApplied += 1

                    # Try to find the submit application button
                    try:
                        submit_button = self.driver.find_element(
                            By.CSS_SELECTOR, "button[aria-label='Submit application']")
                        # If the submit application button was found, click it
                        submit_button.click()
                        # Wait for a random amount of time, as specified in constants.botSpeed
                        time.sleep(random.uniform(1, constants.botSpeed))
                        # Write a message indicating that the application was submitted
                        lineToWrite = f"{jobProperties} | * 🥳 Just Applied to this job: {offerPage}"
                        self.displayWriteResults(lineToWrite)
                    # If the submit application button was not found
                    except:
                        # Try to find the continue to next step button
                        try:
                            continue_button = self.driver.find_element(
                                By.CSS_SELECTOR, "button[aria-label='Continue to next step']")
                            # If the continue to next step button was found, click it
                            continue_button.click()
                            # Wait for a random amount of time, as specified in constants.botSpeed
                            time.sleep(random.uniform(1, constants.botSpeed))
                            # Get the completion percentage of the application
                            comPercentage = self.driver.find_element(
                                By.XPATH, 'html/body/div[3]/div/div/div[2]/div/div/span').text
                            percenNumber = int(
                                comPercentage[0:comPercentage.index("%")])

                            result = self.applyProcess(percenNumber, offerPage)
                            lineToWrite = f"{jobProperties} | {result}"
                            self.displayWriteResults(lineToWrite)
                        except Exception as e:
                            lineToWrite = f"{jobProperties} | * 🥵 Cannot apply to this Job! {offerPage}"
                            self.displayWriteResults(lineToWrite)

            prYellow("Category: " + urlWords[0] + "," + urlWords[1] + " applied: " + str(countApplied) +
                     " jobs out of " + str(countJobs) + ".")

    def getOfferIds(self):
        offersPerPage = self.driver.find_elements(
            By.XPATH, '//li[@data-occludable-job-id]')

        offerIds = []
        for offer in offersPerPage:
            offerId = offer.get_attribute("data-occludable-job-id")
            offerIds.append(int(offerId.split(":")[-1]))

        return offerIds

    def getTotalJobs(self, wait):
        try:
            element = wait.until(
                EC.presence_of_element_located((By.XPATH, '//small')))
            # Once the element is present, you can access its text:
            totalJobs = element.text
        except:
            # If the element is not present after waiting, you can catch the exception and handle it as appropriate:
            print("Element not found")
        return totalJobs

    def getJobProperties(self, count):
        textToWrite = ""
        jobTitle = ""
        jobCompany = ""
        jobLocation = ""
        jobWOrkPlace = ""
        jobPostedDate = ""
        jobApplications = ""

        try:
            jobTitle = self.driver.find_element(
                By.XPATH, "//h1[contains(@class, 'job-title')]").get_attribute("innerHTML").strip()
            res = [blItem for blItem in config.blackListTitles if (
                blItem.lower() in jobTitle.lower())]
            if (len(res) > 0):
                jobTitle += "(blaclisted title: " + ' '.join(res) + ")"
        except Exception as e:
            prYellow("Warning in getting jobTitle: " + str(e)[0:50])
            jobTitle = ""

        try:
            jobCompany = self.driver.find_element(
                By.XPATH, "//a[contains(@class, 'ember-view t-black t-normal')]").get_attribute("innerHTML").strip()
            res = [blItem for blItem in config.blacklistCompanies if (
                blItem.lower() in jobTitle.lower())]
            if (len(res) > 0):
                jobCompany += "(blaclisted company: " + ' '.join(res) + ")"
        except Exception as e:
            prYellow("Warning in getting jobCompany: " + str(e)[0:50])
            jobCompany = ""
            
        try:
            jobLocation = self.driver.find_element(
                By.XPATH, "//span[contains(@class, 'bullet')]").get_attribute("innerHTML").strip()
        except Exception as e:
            prYellow("Warning in getting jobLocation: " + str(e)[0:50])
            jobLocation = ""

        try:
            jobWOrkPlace = self.driver.find_element(
                By.XPATH, "//span[contains(@class, 'workplace-type')]").get_attribute("innerHTML").strip()
        except Exception as e:
            prYellow("Warning in getting jobWorkPlace: " + str(e)[0:50])
            jobWOrkPlace = ""

        try:
            jobPostedDate = self.driver.find_element(
                By.XPATH, "//span[contains(@class, 'posted-date')]").get_attribute("innerHTML").strip()
        except Exception as e:
            prYellow("Warning in getting jobPostedDate: " + str(e)[0:50])
            jobPostedDate = ""

        try:
            jobApplications = self.driver.find_element(
                By.XPATH, "//span[contains(@class, 'applicant-count')]").get_attribute("innerHTML").strip()
        except Exception as e:
            prYellow("Warning in getting jobApplications: " + str(e)[0:50])
            jobApplications = ""

        textToWrite = str(count) + " | " + jobTitle + " | " + jobCompany + " | " + \
            jobLocation + " | " + jobWOrkPlace + " | " + \
            jobPostedDate + " | " + jobApplications
        return textToWrite

    """
    The easyApplyButton method finds the "Easy Apply" button on a job posting page and returns the button element. 
    If the button is not found, it returns False.
    
    Parameters:
    self: the instance of the class.
    
    Returns:
    The "Easy Apply" button element or False if the button is not found.
    """

    def easyApplyButton(self):
        try:
            time.sleep(2)
            button = self.driver.find_element(By.XPATH,
                                              '//button[contains(@class, "jobs-apply-button")]')
            EasyApplyButton = button
        except:
            EasyApplyButton = False

        return EasyApplyButton

    # def is_present(button_locator) -> bool:
    #     return len(self.browser.find_elements(button_locator[0],
    #                                           button_locator[1])) > 0

    def applyProcess(self, percentage, offerPage):
        applyPages = math.floor(100 / percentage)
        result = ""
        success = False

        wait = WebDriverWait(self.driver, 3)
        chooseResume = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "button[aria-label='Choose Resume']")))
        chooseResume.click()

        # text_inputs = driver.find_elements(By.CSS_SELECTOR, '.artdeco-text-input--label')
        # go through all the text inputs and answer the questions according to file

        try:
            for pages in range(applyPages-2):
                try:
                    nextStep = wait.until(EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, "button[aria-label='Continue to next step']")))
                    nextStep.click()
                    time.sleep(random.uniform(1, constants.botSpeed))

                except NoSuchElementException:
                    pass

            reviewApplication = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button[aria-label='Review your application']")))

            # questions = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input.artdeco-text-input--input"))).
            reviewApplication.click()
            time.sleep(random.uniform(1, constants.botSpeed))

            if config.followCompanies is False:
                self.driver.find_element(
                    By.CSS_SELECTOR, "label[for='follow-company-checkbox']").click()
                time.sleep(random.uniform(1, constants.botSpeed))

            self.driver.find_element(
                By.CSS_SELECTOR, "button[aria-label='Submit application']").click()
            time.sleep(random.uniform(1, constants.botSpeed))

            success = True

        except:
            try:
                reviewApplication = wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "button[aria-label='Review your application']")))
                reviewApplication.click()
                time.sleep(random.uniform(1, constants.botSpeed))

                if config.followCompanies is False:
                    self.driver.find_element(
                        By.CSS_SELECTOR, "label[for='follow-company-checkbox']").click()
                    time.sleep(random.uniform(1, constants.botSpeed))

                self.driver.find_element(
                    By.CSS_SELECTOR, "button[aria-label='Submit application']").click()
                time.sleep(random.uniform(1, constants.botSpeed))
            except:
                success = False

        if success:
            result = "* 🥳 Just Applied to this job: " + str(offerPage)
        else:
            result = "* 🥵 Couldn't apply to this job! Link: " + str(offerPage)

        return result

    def displayWriteResults(self, lineToWrite: str):
        try:
            print(lineToWrite)
            utils.writeResults(lineToWrite)
        except Exception as e:
            prRed("Error in DisplayWriteResults: " + str(e))


start = time.time()
Linkedin().linkJobApply()
end = time.time()
prYellow("---Took: " + str(round((time.time() - start)/60)) + " minute(s).")
