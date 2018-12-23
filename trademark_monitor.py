# Trademark monitor fills out search form at www.tmnd.org with provided data,
# and sends the results as html text within an email to receiver's email address.
# Script is then run once a month via Cron.
#
# There has to be module :email_data with the variable named 'receiver'.
# The variable contains email address of the monitoring receiver.
# There has to be module recaptcha_solved.py. For the detailed data on the code
# see: http://scraping.pro/recaptcha-solve-selenium-python/#whole_code
# TODO: Chrome should not be seen working if send_results function will be fixed.
# If it won't be fixed, opening in new window is needed to be planned.

import platform
import time

from selenium import webdriver

#import recaptcha_solved
import email_data


class OSNotRecognized(Exception):
    """Raise if OS is not recognized."""


def check_os():
    """Check operation system to install correct driver for Chrome.

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
        raise OSNotRecognized('Couldn\'t find out your operation system. Program will stop.')
    return driver


def access_search_form(driver):
    """Open advanced search form.

    Opens website and advanced search form. The URL of the form will later be used
    to return to the main page (and not the form particularly, because the URL on the
    website doesn't change with actions performed).

    :param driver: Chrome webdriver needed for Selenium module to work properly.
    :return: URL of the main page.
    """
    driver.get('https://www.tmdn.org/tmview/welcome')
    while True:
        try:
            driver.find_element_by_id('buttonBox').click()    # Accept cookies
        except selenium.common.exceptions.NoSuchElementException:
            time.sleep(30)
            continue
        break
    driver.find_element_by_id('lnkAdvancedSearch').click()    # Access advanced search form
    main_page_url = driver.current_url
    return main_page_url


def search_process(driver, trademark_name, nice_class, vienna_class=None):
    """Fill out the search form.

    :param driver: Chrome webdriver needed for Selenium module to work properly.
    :param trademark_name: Search query for similar trademark names.
    :param nice_class: Search query for registered Nice classes of company trademark.
    :param vienna_class: Search query for registered Vienna classes of company logo.
    :return: None.
    """
    driver.find_element_by_class_name('DesignatedTerritoriesControl').click()
    driver.find_element_by_xpath(".//*[contains(text(), 'Select all EU member states')]").click()
    driver.find_element_by_xpath(".//*[contains(text(), 'Select all Non-EU member states')]").click()
    driver.find_element_by_xpath(".//*[contains(text(), 'Trade mark offices')]").click()    # Click away

    driver.find_element_by_class_name('SelectedOfficesControl').click()
    driver.find_element_by_xpath(".//*[contains(text(), 'Select All')]").click()
    driver.find_element_by_xpath(".//*[contains(text(), 'Trade mark offices')]").click()    # Click away

    driver.find_element_by_id('TrademarkName').send_keys(trademark_name)

    driver.find_element_by_class_name('TrademarkStatusControl').click()
    driver.find_element_by_xpath(".//*[contains(text(), 'Filed')]").click()
    driver.find_element_by_xpath(".//*[contains(text(), 'Trade mark offices')]").click()    # Click away

    driver.find_element_by_id('NiceClass').send_keys(nice_class)

    if vienna_class is not None:
        driver.find_element_by_id('ViennaClass').send_keys(vienna_class)
    else:
        pass

    driver.find_element_by_class_name('SortControl').click()
    driver.find_element_by_xpath("//select[@name='cmbSortField']/option[text()='Application date']").click()
    driver.find_element_by_xpath(".//*[contains(text(), 'Trade mark offices')]").click()    # Click away

    driver.find_element_by_class_name('cmbOrderControl').click()
    driver.find_element_by_xpath(".//*[contains(text(), 'Descending')]").click()

    driver.find_element_by_id('SearchCopy').click()    # Start searching

    time.sleep(5)   # Wait till the database content loads
    print('Searched through successfully for TM {}'.format(trademark_name))
    driver.find_element_by_id('btnClear').click()
    driver.find_element_by_id('lnkAdvancedSearch').click()  # Get back to advanced search form

'''
def send_results(driver, email_data, trademark_name):
    """Fill out the send form.

    Fills out the send form, solves recaptcha and send email with link to search results.

    :param driver: Chrome webdriver needed for Selenium module to work properly.
    :param email_data: Contains email address of receiver or the email with search results.
    :return: None.
    """
    #driver.find_element_by_id('inviteFriendMainPage').click()
    #driver.find_element_by_xpath(".//*[contains(text(), 'Share with a friend')]").click()
    driver.find_element_by_id('inviteFriendPopup').click()
    driver.find_element_by_xpath('.//input[@id="name"]').send_keys('Trademark Monitor for {}'.format(trademark_name))
    driver.find_element_by_xpath('.//input[@id="email"]').send_keys(email_data.receiver)
    driver.find_element_by_xpath('.//input[@id="subject"]').send_keys('Overview of current trademark applications')
    #recaptcha_solved()
    driver.find_element_by_id('btnSubmitUserForm').click()
    driver.find_element_by_id('lnkAdvancedSearch').click()    # Get back to advanced search form
    print('Sent successfully for {}'.format(trademark_name))
'''

def finish_search(driver):
    driver.close()
    driver.quit()
    # kdyz stranka nebude dlouho odpovidat, tak zavrit a zkusit znovu


if __name__ == '__main__':
    driver = check_os()
    access_search_form = access_search_form(driver=driver)
    trezor_tm = search_process(driver=driver, trademark_name='*trez*r*', nice_class='9,36,38,42')
    #send_results(driver=driver, email_data=email_data, trademark_name='*trez*r*')
    trezor_tm = search_process(driver=driver, trademark_name='*tres*r*', nice_class='9,36,38,42')
    #send_results(driver=driver, email_data=email_data, trademark_name='*tres*r*')
    satoshilabs_tm = search_process(driver=driver, trademark_name='*satoshi*', nice_class='9,35,36,38,42')
    #send_results(driver=driver, email_data=email_data)
    logo_trezor_tm = search_process(driver=driver, trademark_name='*trez*r*', nice_class='9,35,36,38,42',
                             vienna_class='14.05.21,14.05.23')
    # send_results(driver=driver, email_data=email_data)
    logo_tresor_tm = search_process(driver=driver, trademark_name='*tres*r*', nice_class='9,35,36,38,42',
                                    vienna_class='14.05.21,14.05.23')
    # send_results(driver=driver, email_data=email_data)
    logo_satoshi_tm = search_process(driver=driver, trademark_name='*satoshi*', nice_class='9,35,36,38,42', vienna_class='14.05.21,14.05.23')
    #send_results(driver=driver, email_data=email_data, trademark_name='*satoshi*')
    finish_search(driver=driver)
