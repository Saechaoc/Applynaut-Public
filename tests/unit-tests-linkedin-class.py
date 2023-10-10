import unittest
import logging
from selenium import webdriver
from linkedin.linkedin2 import Linkedin


class TestLinkedinClass(unittest.TestCase):

    def setUp(self):
        self.linkedin_instance = Linkedin()

    # def tearDown(self):
    #     self.linkedin_instance.driver.quit()

    def testInit(self):
        self.assertIsInstance(self.linkedin_instance.driver, webdriver.Chrome)
        self.assertIsNotNone(self.linkedin_instance.driver.current_url)

    # def testLogout(self):
    #     self.linkedin_instance.logout()

    #     expectedUrl = "https://www.linkedin.com/logout/"
    #     self.assertEqual(
    #         self.linkedin_instance.driver.current_url, expectedUrl)

    def testLinkJobApply(self):
        self.linkedin_instance.linkJobApply()


if __name__ == '__main__':
    unittest.main()
