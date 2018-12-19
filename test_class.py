# File for testing Class creation principle.

from selenium import webdriver
from trademark_monitor import check_os


class AdvancedSearch:
    def __init__(self, trademark_name):
        self.driver = check_os
        self.trademark_name = self.trademark_name.driver.find_element_by_id('TrademarkName')\
            .send_keys('*tre**r*')
        self.trademark_satoshi = self.trademark_name.driver.find_element_by_id('TrademarkName') \
            .send_keys('*satoshi*')
        self.nice_class_no_services = self.nice_class.driver.find_element_by_id('NiceClass')\
            .send_keys('9,36,38,42')
        self.nice_class_incl_services = self.nice_class.driver.find_element_by_id('NiceClass')\
            .send_keys('9,35,36,38,42')
        self.vienna_code = self.vienna_code.driver.find_element_by_id('ViennaClass')\
            .send_keys('14.05.21,14.05.23')

        # TODO: nebere fuzzy search u Trademark Name
        #  fuzzy_search = driver.find_element_by_class_name('fleft').click() - specific, but for both
        #  fuzzy_search = driver.find_element_by_id('tmLinguisticCombo').click() - general, but only for one Fuzzy field
        #  and after that dropdown menu 50%
        # TODO: Designated territories, Trade mark offices, Trade mark status=filed, Sort results by
        #  Application date, Order results=Descending

