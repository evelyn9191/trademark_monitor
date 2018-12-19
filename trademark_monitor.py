# Trademark monitor fills out search form at www.tmnd.org with provided data,
# and sends the results as html text within an email to receiver's email address.
# Script is then run once a month via Cron.
#
# There has to be module :email_data with email account access info.
# The module has to include variables:
# * openkeyword: password for gmail account
# * sender: sender email address
# * receiver: receiver email address
# TODO: fix commentaries and description

import platform
from selenium import webdriver
from selenium.webdriver.support.ui import Select
# TODO: check if possible: from input_data import AdvancedSearch


def check_os():
    """Check operation system to install correct driver.

    :return Correct driver needed for Selenium module.
    """
    operation_system = platform.system()
    if 'linux' in operation_system.lower():
        driver = webdriver.Chrome('chromedriver\chromedriver_linux64')
    elif 'darwin' in operation_system.lower():
        driver = webdriver.Chrome('chromedriver\chromedriver_mac64')
    elif 'win' in operation_system.lower():
        driver = webdriver.Chrome('chromedriver\chromedriver_win32.exe')
    else:
        print('Couldn\'t find out your operation system. Program will now stop.')
        exit()
    return driver


def access_search_form(driver):
    """Open advanced search form.

    Opens website and advanced search form. The URL of the form will later be used
    to return to the form URL in case something goes wrong.

    :param driver: Chrome webdriver needed for Selenium module to work properly.
    :return: URL of the advanced search form.
    """
    driver.get('https://www.tmdn.org/tmview/welcome')
    driver.find_element_by_id('buttonBox').click() # Accept cookies
    driver.find_element_by_id('lnkAdvancedSearch').click() # Access advanced search form
    advanced_search_form_path = driver.current_url
    return advanced_search_form_path


def search_process(driver):
    driver.find_element_by_xpath('.//input[@id="linguisticTm"]').click()
    driver.find_element_by_xpath('.//input[@id="select-EU"]').click() 
    driver.find_element_by_xpath('.//input[@id="select-non-EU"]').click() 
    driver.find_element_by_xpath('.//button[@id="btnSelectAll"]').click() 
    driver.find_element_by_id('TrademarkName').send_keys(tm_name)
    
    select = Select(driver.find_element_by_id('TradeMarkStatus'))
    select.select_by_value('Filed')
    select.select_by_value('Registered')
    
    driver.find_element_by_id('NiceClass').send_keys(nice_class)
    driver.find_element_by_id('ViennaClass').send_keys(vienna_class)
    
    select = Select(driver.find_element_by_id('cmbSortField'))
    select.select_by_value('ad')
    select.select_by_value('Registered')

    select = Select(driver.find_element_by_id('cmbOrder'))
    select.select_by_value('DESC')

    driver.find_element_by_id('SearchCopy').click()

def send_results(driver):
    driver.find_element_by_title('Share with a friend').click()
    driver.find_element_by_xpath('.//input[@id="name"]').send_keys(name)
    driver.find_element_by_xpath('.//input[@id="email"]').send_keys(email)
    driver.find_element_by_xpath('.//input[@id="subject"]').send_keys('Overview of current trademark applications')
"""
<div id="captchaBox"></div>
		<script type="text/javascript" src="https://www.google.com/recaptcha/api.js?onload=onloadCaptchaCallback&render=explicit" async defer></script>
	</div>
"""
    driver.find_element_by_id('btnSubmitUserForm').click()

    # driver.close()
    # driver.quit()

if __name__ == '__main__':
    check_os = check_os()
    access_search_form = access_search_form(driver=check_os)
    trezor_tm = search_process(tm_name='*tre**r*', nice_class='9,36,38,42')
    satoshilabs_tm = search_process(tm_name='*satoshi*', nice_class='9,35,36,38,42')
    logo_tm = search_process(tm_name='*satoshi*', nice_class='9,35,36,38,42', vienna_class='14.05.21,14.05.23')
    # search_process = search_process(driver=check_os)

